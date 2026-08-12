# FUO Complaint System

A web-based Departmental Complaint Management System for students and administrators at Federal University Otuoke (FUO).

## Features
- Student registration and login
- Administrator login
- Complaint submission with category selection
- Sentiment analysis using VADER
- Complaint status tracking
- Administrator responses
- Dashboard summaries for students and administrators

## How to run locally
1. Create and activate a Python virtual environment.
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Run the application:
   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```
4. Open `http://127.0.0.1:5000` in your browser.

## Deployment to Render
1. Push the project to a GitHub repository.
2. Create a Render account and select "New Web Service".
3. Connect your GitHub repo and choose the branch to deploy.
4. Set the environment to `Python`.
5. Use the build command:
   ```bash
   pip install -r requirements.txt
   ```
6. Use the start command:
   ```bash
   python app.py
   ```
7. Add an environment variable named `SECRET_KEY` with a secure value.
8. Deploy the service and open the generated public URL.

Alternatively, this repo includes a `render.yaml` file so Render can auto-create the service when you connect the repository. The `render.yaml` will generate a `SECRET_KEY` for you automatically. If you prefer the Render dashboard, connect the repo and review the generated service settings.

### Notes for deployment
- The app listens on `0.0.0.0` and uses `PORT` from the hosting environment.
- Render will automatically provide the public URL once deploy is complete.

## Default administrator
- Email: `admin@fuo.edu.ng`
- Password: `admin123`

## Notes
- The app uses SQLite and initializes the database on first run.
- Sentiment analysis is performed automatically when a student submits a complaint.
