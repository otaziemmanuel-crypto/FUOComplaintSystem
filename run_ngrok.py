import os
import signal
import subprocess
import sys
import time

from pyngrok import ngrok

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get('PORT', '5000'))
AUTH_TOKEN = os.environ.get('NGROK_AUTHTOKEN')


def shutdown(signum, frame):
    print('\nShutting down ngrok and Flask app...')
    try:
        ngrok.disconnect(f'http://127.0.0.1:{PORT}')
        ngrok.kill()
    except Exception:
        pass
    if app_proc.poll() is None:
        app_proc.terminate()
        try:
            app_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app_proc.kill()
    sys.exit(0)


if __name__ == '__main__':
    env = os.environ.copy()
    env['PORT'] = str(PORT)
    python_executable = sys.executable

    if AUTH_TOKEN:
        ngrok.set_auth_token(AUTH_TOKEN)
    else:
        print('ERROR: NGROK_AUTHTOKEN is not set.')
        print('Set your ngrok auth token in the environment before running this script.')
        print('See https://dashboard.ngrok.com/get-started/your-authtoken')
        app_proc.terminate()
        sys.exit(1)

    print(f'Starting Flask app on port {PORT}...')
    app_proc = subprocess.Popen([python_executable, os.path.join(PROJECT_DIR, 'app.py')], cwd=PROJECT_DIR, env=env)

    print('Opening ngrok tunnel...')
    tunnel = ngrok.connect(PORT, 'http')
    public_url = tunnel.public_url
    print(f'Public URL: {public_url}')
    print('Press Ctrl+C to stop the app and close the tunnel.')

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)
