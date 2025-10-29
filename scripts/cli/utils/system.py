"""System utilities for user management and file operations."""

import os
import pwd
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from .console import log_success


def check_root():
    """
    Check if running as root.
    
    Raises:
        PermissionError: If not running as root
    """
    if os.geteuid() != 0:
        raise PermissionError("This command must be run as root (use sudo)")


def check_not_root():
    """
    Check if NOT running as root.
    
    Raises:
        PermissionError: If running as root
    """
    if os.geteuid() == 0:
        raise PermissionError("This command should NOT be run as root")


def get_actual_user() -> str:
    """
    Get actual user (even when using sudo).
    
    Returns:
        str: Username
    """
    return os.environ.get('SUDO_USER', os.environ.get('USER', 'unknown'))


def get_actual_home() -> Path:
    """
    Get actual user's home directory.
    
    Returns:
        Path: Home directory
    """
    user = get_actual_user()
    try:
        return Path(pwd.getpwnam(user).pw_dir)
    except KeyError:
        return Path.home()


def user_exists(username: str) -> bool:
    """
    Check if system user exists.
    
    Args:
        username: Username to check
    
    Returns:
        bool: True if user exists
    """
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def backup_file(file_path: Path, show_message: bool = True) -> Optional[Path]:
    """
    Create timestamped backup of a file.
    
    Args:
        file_path: File to backup
        show_message: Show success message
    
    Returns:
        Path: Backup file path or None if file doesn't exist
    """
    if not file_path.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"{file_path}.backup.{timestamp}")
    
    shutil.copy2(file_path, backup_path)
    
    if show_message:
        log_success(f"Backup created: {backup_path}")
    
    return backup_path


def create_user(
    username: str,
    home_dir: Optional[Path] = None,
    shell: str = "/bin/bash"
) -> bool:
    """
    Create system user.
    
    Args:
        username: Username
        home_dir: Home directory (default: /home/{username})
        shell: Shell (default: /bin/bash)
    
    Returns:
        bool: True if created, False if already exists
    
    Raises:
        PermissionError: If not root
    """
    check_root()
    
    if user_exists(username):
        return False
    
    import subprocess
    
    cmd = ["useradd", "-m", "-s", shell]
    if home_dir:
        cmd.extend(["-d", str(home_dir)])
    cmd.append(username)
    
    subprocess.run(cmd, check=True)
    return True


def add_user_to_group(username: str, group: str):
    """
    Add user to group.
    
    Args:
        username: Username
        group: Group name
    
    Raises:
        PermissionError: If not root
    """
    check_root()
    
    import subprocess
    subprocess.run(
        ["usermod", "-aG", group, username],
        check=True
    )


def set_permissions(path: Path, mode: int, recursive: bool = False):
    """
    Set file/directory permissions.
    
    Args:
        path: Path to set permissions on
        mode: Permission mode (e.g., 0o755)
        recursive: Apply recursively
    """
    if recursive and path.is_dir():
        for item in path.rglob('*'):
            item.chmod(mode)
    path.chmod(mode)


def set_owner(path: Path, user: str, group: Optional[str] = None, recursive: bool = False):
    """
    Set file/directory owner.
    
    Args:
        path: Path to set owner on
        user: Username
        group: Group name (default: same as user)
        recursive: Apply recursively
    
    Raises:
        PermissionError: If not root
    """
    check_root()
    
    import subprocess
    
    if group is None:
        group = user
    
    owner = f"{user}:{group}"
    
    cmd = ["chown"]
    if recursive:
        cmd.append("-R")
    cmd.extend([owner, str(path)])
    
    subprocess.run(cmd, check=True)

