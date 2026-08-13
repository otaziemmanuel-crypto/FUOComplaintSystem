import os
import sys

project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault('SECRET_KEY', 'change-me-to-a-secure-secret')

from app import app as application
