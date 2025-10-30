#!/usr/bin/env python3
"""Script to mass fix return types in API endpoints"""

import re
from pathlib import Path

# Files and their return types
fixes = {
    "backend/app/api/containers.py": [
        ("async def list_containers(", " -> dict:"),
        ("async def get_container(", " -> dict:"),
        ("async def start_container(", " -> dict:"),
        ("async def stop_container(", " -> dict:"),
        ("async def restart_container(", " -> dict:"),
        ("async def remove_container(", " -> dict:"),
        ("async def get_container_logs(", " -> dict:"),
        ("async def get_container_stats(", " -> dict:"),
    ],
    "backend/app/api/projects.py": [
        ("async def create_project(", " -> dict:"),
        ("async def get_projects(", " -> list:"),
        ("async def get_project(", " -> dict:"),
        ("async def update_project(", " -> dict:"),
        ("async def delete_project(", " -> None:"),
        ("async def get_env_vars(", " -> dict:"),
        ("async def update_env_vars(", " -> dict:"),
    ],
    "backend/app/api/deployment.py": [
        ("async def get_deployment_info(", " -> dict:"),
        ("async def get_ssh_setup_info():", " -> dict:"),
    ],
}

for file_path, replacements in fixes.items():
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"Skipping {file_path} (not found)")
        continue
    
    content = file_path.read_text()
    
    for search_pattern, return_type in replacements:
        # Find the function definition
        pattern = re.escape(search_pattern) + r"([^:]*?):"
        
        def add_return_type(match):
            params = match.group(1)
            # Skip if already has return type
            if "->" in params:
                return match.group(0)
            return f"{search_pattern}{params}{return_type}"
        
        content = re.sub(pattern, add_return_type, content)
    
    file_path.write_text(content)
    print(f"✅ Fixed {file_path}")

print("\nDone!")

