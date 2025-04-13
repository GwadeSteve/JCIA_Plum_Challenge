import os
from pathlib import Path

def print_directory_structure(startpath, exclude_dirs=None, exclude_extensions=None):
    if exclude_dirs is None:
        exclude_dirs = ['.git', '.venv', 'venv', '__pycache__', '.ipynb_checkpoints']
    
    if exclude_extensions is None:
        exclude_extensions = []

    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and 'run' not in d.lower()]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * level
        print(f'{indent}├── {os.path.basename(root)}/')
        
        sub_indent = '│   ' * (level + 1)
        for file in sorted(files):
            if any(file.endswith(ext) for ext in exclude_extensions):
                continue
            print(f'{sub_indent}├── {file}')