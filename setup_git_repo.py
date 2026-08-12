import os
from dulwich import porcelain

root = os.path.abspath(os.path.dirname(__file__))
ignore_dirs = {'.git', '.venv', 'venv', '__pycache__'}
ignore_files = {'debug_request.py', 'check_routes.py'}

if not os.path.exists(os.path.join(root, '.git')):
    porcelain.init(root)
    print('Initialized git repository.')
else:
    print('Git repository already exists.')

paths = []
for dirpath, dirnames, filenames in os.walk(root):
    # Remove ignored dirs in-place so os.walk doesn't recurse into them.
    dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
    for filename in filenames:
        if filename in ignore_files or filename.endswith('.pyc'):
            continue
        if dirpath.startswith(os.path.join(root, '.git')):
            continue
        relpath = os.path.relpath(os.path.join(dirpath, filename), root)
        if relpath.startswith('.git' + os.sep):
            continue
        paths.append(relpath)

if paths:
    porcelain.add(root, paths)
    print(f'Staged {len(paths)} files.')
else:
    print('No files to stage.')

try:
    porcelain.commit(root, message=b'Initial commit for FUO Complaint System', author=b'FUO Student <noreply@fuo.edu.ng>')
    print('Created initial commit.')
except Exception as exc:
    print('Commit failed:', exc)
