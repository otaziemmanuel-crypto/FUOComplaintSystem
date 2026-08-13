import os
import sqlite3
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sentiment import analyze_text

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['DATABASE'] = os.path.join(app.instance_path, 'complaints.db')

os.makedirs(app.instance_path, exist_ok=True)

STATUS_LABELS = ['submitted', 'under review', 'resolved', 'rejected']


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaint_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(category_id) REFERENCES complaint_categories(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            admin_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(complaint_id) REFERENCES complaints(id),
            FOREIGN KEY(admin_id) REFERENCES users(id)
        )
    ''')
    categories = ['Academic', 'Facilities', 'Staff', 'Examination', 'Other']
    for name in categories:
        cursor.execute('INSERT OR IGNORE INTO complaint_categories (name) VALUES (?)', (name,))

    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    if cursor.fetchone() is None:
        now = datetime.utcnow().isoformat()
        cursor.execute(
            'INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)',
            ('Department Admin', 'admin@fuo.edu.ng', generate_password_hash('admin123'), 'admin', now)
        )

    # ensure a system user exists to post automated responses
    cursor.execute("SELECT id FROM users WHERE role = 'system' LIMIT 1")
    if cursor.fetchone() is None:
        now = datetime.utcnow().isoformat()
        cursor.execute(
            'INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)',
            ('Auto Responder', 'system@fuo.edu.ng', generate_password_hash('system'), 'system', now)
        )

    db.commit()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)


def require_login(role=None):
    user = get_current_user()
    if user is None:
        return redirect(url_for('home'))
    if role and user['role'] != role:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('home'))
    return user


with app.app_context():
    init_db()


@app.route('/')
def home():
    user = get_current_user()
    if user:
        if user['role'] == 'student':
            return redirect(url_for('student_dashboard'))
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not name or not email or not password:
            flash('Please fill in all registration fields.', 'error')
            return render_template('student_register.html')

        existing = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
        if existing:
            flash('Email already exists. Use a different email.', 'error')
            return render_template('student_register.html')

        db = get_db()
        db.execute(
            'INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)',
            (name, email, generate_password_hash(password), 'student', datetime.utcnow().isoformat())
        )
        db.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('student_login'))

    return render_template('student_register.html')


@app.route('/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = query_db('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'student'), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            return redirect(url_for('student_dashboard'))
        flash('Invalid student email or password.', 'error')

    return render_template('student_login.html')


@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not name or not email or not password:
            flash('Please fill in all administrator registration fields.', 'error')
            return render_template('admin_register.html')

        existing = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
        if existing:
            flash('Email already exists. Use a different email.', 'error')
            return render_template('admin_register.html')

        db = get_db()
        db.execute(
            'INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)',
            (name, email, generate_password_hash(password), 'admin', datetime.utcnow().isoformat())
        )
        db.commit()
        flash('Administrator registration successful. Please log in.', 'success')
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = query_db('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'admin'), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            return redirect(url_for('admin_dashboard'))
        flash('Invalid administrator email or password.', 'error')

    return render_template('admin_login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/student/dashboard')
def student_dashboard():
    user = require_login('student')
    if not isinstance(user, sqlite3.Row) and not user:
        return user

    total = query_db('SELECT COUNT(*) AS count FROM complaints WHERE student_id = ?', (user['id'],), one=True)['count']
    open_count = query_db('SELECT COUNT(*) AS count FROM complaints WHERE student_id = ? AND status != ?', (user['id'], 'resolved'), one=True)['count']
    negative_count = query_db('SELECT COUNT(*) AS count FROM complaints WHERE student_id = ? AND sentiment = ?', (user['id'], 'negative'), one=True)['count']
    recent = query_db(
        '''SELECT c.id, c.title, c.status, c.sentiment, c.created_at, cat.name AS category_name
           FROM complaints c
           JOIN complaint_categories cat ON c.category_id = cat.id
           WHERE c.student_id = ?
           ORDER BY c.created_at DESC
           LIMIT 5''',
        (user['id'],)
    )

    return render_template('student_dashboard.html', user=user, total=total, open_count=open_count,
                           negative_count=negative_count, recent=recent)


@app.route('/student/submit', methods=['GET', 'POST'])
def submit_complaint():
    user = require_login('student')
    if not isinstance(user, sqlite3.Row) and not user:
        return user

    categories = query_db('SELECT * FROM complaint_categories ORDER BY name')
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id')
        description = request.form.get('description', '').strip()
        if not title or not category_id or not description:
            flash('Please complete all fields before submitting your complaint.', 'error')
            return render_template('submit_complaint.html', categories=categories)
        sentiment, score = analyze_text(description)
        now = datetime.utcnow().isoformat()
        db = get_db()
        cur = db.cursor()
        cur.execute(
            '''INSERT INTO complaints (student_id, category_id, title, description, sentiment, sentiment_score, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user['id'], category_id, title, description, sentiment, score, 'submitted', now, now)
        )
        complaint_id = cur.lastrowid

        # generate automated response based on complaint content and category (not sentiment)
        system_row = query_db('SELECT id FROM users WHERE role = ?', ('system',), one=True)
        system_id = system_row['id'] if system_row else None

        # get category name for category-specific messages
        cat_row = query_db('SELECT name FROM complaint_categories WHERE id = ?', (category_id,), one=True)
        category_name = cat_row['name'] if cat_row else 'Other'

        if system_id:
            text = description.lower()
            urgent_keywords = ['urgent', 'immediately', 'asap', 'emergency', 'danger', 'harassed', 'harassment', 'assault']
            facility_keywords = ['broken', 'no water', 'power', 'electric', 'leak', 'leaking', 'broken toilet', 'broken door']

            is_urgent = any(k in text for k in urgent_keywords)
            is_facility = any(k in text for k in facility_keywords) or category_name.lower() == 'facilities'

            if is_urgent:
                auto_msg = f"We're very sorry to hear this. Your complaint (ID {complaint_id}) has been flagged as urgent and will be prioritized by the department."
            elif is_facility:
                auto_msg = f"Thanks for reporting this facilities issue (ID {complaint_id}). Facilities staff have been notified and will look into it." 
            elif category_name.lower() == 'examination':
                auto_msg = f"Your examination-related complaint (ID {complaint_id}) has been recorded. The examinations office will review it and respond as necessary." 
            else:
                auto_msg = f"Thank you. Your complaint (ID {complaint_id}) has been recorded and will be reviewed by administrators soon."

            cur.execute(
                'INSERT INTO responses (complaint_id, admin_id, message, created_at) VALUES (?, ?, ?, ?)',
                (complaint_id, system_id, auto_msg, now)
            )

        db.commit()
        flash('Complaint submitted successfully and an automatic acknowledgement was posted.', 'success')
        return redirect(url_for('student_history'))

    return render_template('submit_complaint.html', categories=categories)


@app.route('/student/history')
def student_history():
    user = require_login('student')
    if not isinstance(user, sqlite3.Row) and not user:
        return user

    complaints = query_db(
        '''SELECT c.id, c.title, c.status, c.sentiment, c.sentiment_score, c.created_at, cat.name AS category_name
           FROM complaints c
           JOIN complaint_categories cat ON c.category_id = cat.id
           WHERE c.student_id = ?
           ORDER BY c.created_at DESC''',
        (user['id'],)
    )
    return render_template('complaint_history.html', complaints=complaints)


@app.route('/student/complaint/<int:complaint_id>')
def student_complaint_detail(complaint_id):
    user = require_login('student')
    if not isinstance(user, sqlite3.Row) and not user:
        return user

    complaint = query_db(
        '''SELECT c.*, cat.name AS category_name
           FROM complaints c
           JOIN complaint_categories cat ON c.category_id = cat.id
           WHERE c.id = ? AND c.student_id = ?''',
        (complaint_id, user['id']), one=True
    )
    if not complaint:
        flash('Complaint not found.', 'error')
        return redirect(url_for('student_history'))

    responses = query_db(
        '''SELECT r.*, u.name AS admin_name
           FROM responses r
           JOIN users u ON r.admin_id = u.id
           WHERE r.complaint_id = ?
           ORDER BY r.created_at DESC''',
        (complaint_id,)
    )
    return render_template('complaint_detail.html', complaint=complaint, responses=responses, admin_view=False)


@app.route('/admin/dashboard')
def admin_dashboard():
    user = require_login('admin')
    if not isinstance(user, sqlite3.Row) and not user:
        return user

    total = query_db('SELECT COUNT(*) AS count FROM complaints', one=True)['count']
    pending = query_db('SELECT COUNT(*) AS count FROM complaints WHERE status != ?', ('resolved',), one=True)['count']
    negative = query_db('SELECT COUNT(*) AS count FROM complaints WHERE sentiment = ?', ('negative',), one=True)['count']
    sentiment_counts = query_db(
        '''SELECT sentiment, COUNT(*) AS count
           FROM complaints
           GROUP BY sentiment'''
    )
    categories = query_db(
        '''SELECT cat.name, COUNT(*) AS count
           FROM complaints c
           JOIN complaint_categories cat ON c.category_id = cat.id
           GROUP BY c.category_id
           ORDER BY count DESC'''
    )
    urgent = query_db(
        '''SELECT c.id, c.title, c.status, c.sentiment, c.created_at, u.name AS student_name, cat.name AS category_name
           FROM complaints c
           JOIN users u ON c.student_id = u.id
           JOIN complaint_categories cat ON c.category_id = cat.id
           WHERE c.sentiment = ? AND c.status != ?
           ORDER BY c.created_at DESC
           LIMIT 5''',
        ('negative', 'resolved')
    )
    recent = query_db(
        '''SELECT c.id, c.title, c.status, c.sentiment, c.created_at, u.name AS student_name, cat.name AS category_name
           FROM complaints c
           JOIN users u ON c.student_id = u.id
           JOIN complaint_categories cat ON c.category_id = cat.id
           ORDER BY c.created_at DESC
           LIMIT 6'''
    )

    sentiment_map = {row['sentiment']: row['count'] for row in sentiment_counts}
    return render_template('admin_dashboard.html', user=user, total=total, pending=pending,
                           negative=negative, sentiment_map=sentiment_map,
                           categories=categories, urgent=urgent, recent=recent)


@app.route('/admin/complaints')
def admin_complaint_list():
    user = require_login('admin')
    if not isinstance(user, sqlite3.Row) and not user:
        return user

    sentiment_filter = request.args.get('sentiment')
    status_filter = request.args.get('status')
    params = []
    where_clauses = []
    if sentiment_filter:
        where_clauses.append('c.sentiment = ?')
        params.append(sentiment_filter)
    if status_filter:
        where_clauses.append('c.status = ?')
        params.append(status_filter)
    where_sql = 'WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''

    complaints = query_db(
        f'''SELECT c.id, c.title, c.status, c.sentiment, c.created_at, u.name AS student_name, cat.name AS category_name
            FROM complaints c
            JOIN users u ON c.student_id = u.id
            JOIN complaint_categories cat ON c.category_id = cat.id
            {where_sql}
            ORDER BY c.created_at DESC''',
        tuple(params)
    )
    return render_template('admin_complaints.html', complaints=complaints,
                           selected_sentiment=sentiment_filter, selected_status=status_filter,
                           status_labels=STATUS_LABELS)


@app.route('/admin/complaint/<int:complaint_id>', methods=['GET', 'POST'])
def admin_complaint_detail(complaint_id):
    user = require_login('admin')
    if not isinstance(user, sqlite3.Row) and not user:
        return user

    complaint = query_db(
        '''SELECT c.*, u.name AS student_name, u.email AS student_email, cat.name AS category_name
           FROM complaints c
           JOIN users u ON c.student_id = u.id
           JOIN complaint_categories cat ON c.category_id = cat.id
           WHERE c.id = ?''',
        (complaint_id,), one=True
    )
    if not complaint:
        flash('Complaint not found.', 'error')
        return redirect(url_for('admin_complaint_list'))

    if request.method == 'POST':
        status = request.form.get('status', complaint['status'])
        message = request.form.get('message', '').strip()
        db = get_db()
        now = datetime.utcnow().isoformat()
        if status and status in STATUS_LABELS:
            db.execute('UPDATE complaints SET status = ?, updated_at = ? WHERE id = ?', (status, now, complaint_id))
        if message:
            db.execute(
                'INSERT INTO responses (complaint_id, admin_id, message, created_at) VALUES (?, ?, ?, ?)',
                (complaint_id, user['id'], message, now)
            )
        db.commit()
        flash('Complaint status updated and response saved.', 'success')
        return redirect(url_for('admin_complaint_detail', complaint_id=complaint_id))

    responses = query_db(
        '''SELECT r.*, u.name AS admin_name
           FROM responses r
           JOIN users u ON r.admin_id = u.id
           WHERE r.complaint_id = ?
           ORDER BY r.created_at DESC''',
        (complaint_id,)
    )
    return render_template('complaint_detail.html', complaint=complaint, responses=responses, admin_view=True,
                           status_labels=STATUS_LABELS)


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
