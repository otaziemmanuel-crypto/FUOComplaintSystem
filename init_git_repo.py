import os
from dulwich.repo import Repo
from dulwich.index import build_index_from_tree
from dulwich.objects import Blob, Tree
from dulwich.errors import NotGitRepository

path = os.path.abspath(os.path.dirname(__file__))
repo_path = os.path.join(path, '.git')

if not os.path.exists(repo_path):
    repo = Repo.init(path.encode('utf-8'))
    print('initialized git repo')
else:
    repo = Repo(path.encode('utf-8'))
    print('git repo already exists')

# Stage files, ignoring .venv, __pycache__, debug_request.py, check_routes.py
ignore_dirs = {'.git', '.venv', 'venv', '__pycache__'}
ignore_files = {'debug_request.py', 'check_routes.py'}

index = repo.open_index()
for root, dirs, files in os.walk(path):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for file_name in files:
        if file_name in ignore_files or file_name.endswith('.pyc'):
            continue
        full_path = os.path.join(root, file_name)
        rel_path = os.path.relpath(full_path, path).replace('\\', '/')
        if rel_path.startswith('.git/'):
            continue
        with open(full_path, 'rb') as f:
            data = f.read()
        blob = Blob.from_string(data)
        repo.object_store.add_object(blob)
        index[rel_path] = (0o100644, blob.id)

index.write()
print('staged files in index')
