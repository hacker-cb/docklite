#!/usr/bin/env python3
"""Fix incorrect -> dict: syntax in function parameters"""

from pathlib import Path
import re

def fix_file(file_path):
    content = file_path.read_text()
    original = content
    
    # Fix: param -> dict: type  =>  param: type
    patterns = [
        (r'(\w+)\s*->\s*dict:\s*(\w+)', r'\1: \2'),  # container_id -> dict: str  =>  container_id: str
        (r'"(\w+)"\s*->\s*dict:', r'"\1":'),  # "deploy_user" -> dict:  =>  "deploy_user":
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        file_path.write_text(content)
        print(f"✅ Fixed {file_path}")
        return True
    return False

files = [
    Path("backend/app/api/containers.py"),
    Path("backend/app/api/projects.py"),
    Path("backend/app/api/deployment.py"),
]

fixed = 0
for file in files:
    if file.exists():
        if fix_file(file):
            fixed += 1

print(f"\n✅ Fixed {fixed} files")

