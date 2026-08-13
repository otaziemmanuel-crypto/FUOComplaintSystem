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

## Expose the app with ngrok
1. Install dependencies if you have not already:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
2. Sign up for an ngrok account and get your auth token from:
   ```text
   https://dashboard.ngrok.com/get-started/your-authtoken
   ```
3. Set `NGROK_AUTHTOKEN` in your PowerShell session:
   ```powershell
   setx NGROK_AUTHTOKEN "your-auth-token"
   ```
   Then close and reopen your terminal for the environment variable to take effect.
4. Run the ngrok launcher script:
   ```powershell
   .\.venv\Scripts\python.exe run_ngrok.py
   ```
5. Copy the public URL shown in the terminal.
6. Open that URL in your browser while the app and ngrok tunnel are running.

> The public URL is temporary and will stop when the script exits.

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
   gunicorn app:app
   ```
7. Add an environment variable named `SECRET_KEY` with a secure value.
8. Deploy the service and open the generated public URL.

This repository also includes a `render.yaml` file so Render can auto-create the service when you connect the repository. The `render.yaml` will generate a `SECRET_KEY` automatically.

## Deployment to PythonAnywhere
1. Create a PythonAnywhere account and log in.
2. Open a Bash console.
3. Clone this repository:
   ```bash
   cd ~
   git clone https://github.com/otaziemmanuel-crypto/FUOComplaintSystem.git
   cd FUOComplaintSystem
   ```
4. Create and activate a virtual environment:
   ```bash
   python3.11 -m venv ~/virtualenvs/fuocomplaint
   source ~/virtualenvs/fuocomplaint/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. In the PythonAnywhere Web tab, add a new web app using manual configuration and the matching Python version.
6. Set the source code directory to `/home/<your-username>/FUOComplaintSystem`.
7. Set the virtualenv path to `/home/<your-username>/virtualenvs/fuocomplaint`.
8. Edit the WSGI configuration file and point it to this project by importing `app` from `app.py`.
9. Reload the web app and open the public URL.

### PythonAnywhere WSGI example
Use the bundled `wsgi.py` file in this repo as your WSGI entry point.

### Notes for deployment
- The app listens on `0.0.0.0` and uses `PORT` from the hosting environment.
- Set `SECRET_KEY` in the hosting environment for security.
- PythonAnywhere does not require `gunicorn`; it uses the WSGI entry point defined in `wsgi.py`.

## Default administrator
- Email: `admin@fuo.edu.ng`
- Password: `admin123`

## Notes
- The app uses SQLite and initializes the database on first run.
- Sentiment analysis is performed automatically when a student submits a complaint.
