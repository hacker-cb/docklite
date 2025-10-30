#!/usr/bin/env python3
"""Fix remaining typing issues"""

from pathlib import Path
import re

# Fix: safe_json_loads to accept Optional[str]
def fix_formatters():
    file = Path("backend/app/utils/formatters.py")
    content = file.read_text()
    content = content.replace(
        "def safe_json_loads(json_str: str, default: dict = None) -> dict:",
        "def safe_json_loads(json_str: Optional[str], default: Optional[dict] = None) -> dict:"
    )
    file.write_text(content)
    print("✅ Fixed formatters.py")

# Fix: Column assignments - cast to proper type
def fix_column_assignments():
    changes = {
        "backend/app/api/users.py": [
            ("user.is_active = 1 if is_active else 0", "setattr(user, 'is_active', 1 if is_active else 0)"),
            ("user.is_admin = 1 if is_admin else 0", "setattr(user, 'is_admin', 1 if is_admin else 0)"),
            ("user.password_hash = auth_service.get_password_hash(new_password)", "setattr(user, 'password_hash', auth_service.get_password_hash(new_password))"),
        ],
        "backend/app/services/project_service.py": [
            ("new_project.slug = slug", "setattr(new_project, 'slug', slug)"),
            ("new_project.compose_content = modified_compose", "setattr(new_project, 'compose_content', modified_compose)"),
            ("project.compose_content = modified_compose", "setattr(project, 'compose_content', modified_compose)"),
            ("project.domain = project_data.domain", "setattr(project, 'domain', project_data.domain)"),
            ("project.name = project_data.name", "setattr(project, 'name', project_data.name)"),
            ("project.env_vars = json.dumps(project_data.env_vars)", "setattr(project, 'env_vars', json.dumps(project_data.env_vars))"),
            ("project.env_vars = json.dumps(env_vars)", "setattr(project, 'env_vars', json.dumps(env_vars))"),
        ],
        "backend/app/services/auth_service.py": [
            ("user.is_admin = 1", "setattr(user, 'is_admin', 1)"),
        ],
        "backend/tests/conftest.py": [
            ("user.is_admin = 1", "setattr(user, 'is_admin', 1)"),
        ],
    }
    
    for file_path, replacements in changes.items():
        file = Path(file_path)
        if not file.exists():
            continue
        content = file.read_text()
        for old, new in replacements:
            content = content.replace(old, new)
        file.write_text(content)
        print(f"✅ Fixed {file_path}")

fix_formatters()
fix_column_assignments()
print("\nDone!")

