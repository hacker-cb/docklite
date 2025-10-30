"""Maintenance commands for DockLite CLI."""

import subprocess
import tarfile
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from ..config import (
    PROJECT_ROOT,
    BACKUPS_DIR,
    BACKEND_DATA_DIR,
    ENV_FILE,
    DOCKER_COMPOSE_FILE,
    CONTAINER_TRAEFIK,
    CONTAINER_BACKEND,
    CONTAINER_FRONTEND,
    VERSION,
    get_hostname,
    get_access_url
)
from ..utils.console import (
    log_info,
    log_success,
    log_warning,
    log_error,
    log_step,
    print_banner,
    console,
    confirm,
    create_table,
    create_progress
)
from ..utils.docker import (
    docker_compose_cmd,
    is_container_running,
    get_container_status
)
from ..utils.validation import check_docker

app = typer.Typer(help="Maintenance commands")


@app.command(name="add-user")
def add_user(
    username: str = typer.Argument(..., help="Username"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Password (prompted if not provided)"),
    is_admin: bool = typer.Option(False, "--admin", "-a", help="Create as admin user"),
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email address"),
    system_user: str = typer.Option("docklite", "--system-user", "-s", help="Linux system user for projects"),
) -> None:
    """Add a new user to DockLite."""
    import getpass
    
    print_banner("Add New User")
    
    # Check Docker
    check_docker()
    
    # Check if backend is running
    if not is_container_running(CONTAINER_BACKEND):
        log_warning("Backend is not running. Starting it...")
        docker_compose_cmd("up", "-d", "backend", cwd=PROJECT_ROOT)
        log_step("Waiting for backend...")
        time.sleep(3)
    
    # Get password if not provided
    if not password:
        console.print()
        password = getpass.getpass(f"Enter password for {username}: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            log_error("Passwords do not match!")
            raise typer.Exit(1)
    
    if len(password) < 8:
        log_error("Password must be at least 8 characters!")
        raise typer.Exit(1)
    
    # Check if user exists
    log_step("Checking if user exists...")
    try:
        result = docker_compose_cmd(
            "exec", "-T", "backend",
            "python", "-m", "app.cli_helpers.list_users", "simple",
            cwd=PROJECT_ROOT,
            capture_output=True
        )
        existing_users = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        if username in existing_users:
            log_error(f"User '{username}' already exists!")
            raise typer.Exit(1)
            
    except subprocess.CalledProcessError:
        log_warning("Could not check existing users, continuing...")
    
    # Create user
    log_step(f"Creating user '{username}'...")
    
    # Build Python script
    admin_flag = "True" if is_admin else "False"
    email_arg = f'"{email}"' if email else "None"
    
    python_script = f"""
import asyncio
import sys
import logging

# Disable SQLAlchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

from app.core.database import AsyncSessionLocal
from app.models import user, project  # Import all models
from app.models.user import User
from app.core.security import get_password_hash

async def create_user():
    async with AsyncSessionLocal() as session:
        new_user = User(
            username="{username}",
            hashed_password=get_password_hash("{password}"),
            is_admin={admin_flag},
            email={email_arg},
            system_user="{system_user}"
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        print(f"SUCCESS:{{new_user.id}}")

if __name__ == "__main__":
    asyncio.run(create_user())
"""
    
    try:
        result = docker_compose_cmd(
            "exec", "-T", "backend",
            "python", "-c", python_script,
            cwd=PROJECT_ROOT,
            capture_output=True
        )
        
        if "SUCCESS" in result.stdout:
            user_id = result.stdout.strip().split(":")[-1]
            log_success(f"User '{username}' created successfully! (ID: {user_id})")
            
            console.print()
            console.print("[bold]User Details:[/bold]")
            console.print(f"  Username:     [cyan]{username}[/cyan]")
            console.print(f"  Role:         [cyan]{'Admin' if is_admin else 'User'}[/cyan]")
            console.print(f"  System User:  [cyan]{system_user}[/cyan]")
            if email:
                console.print(f"  Email:        [cyan]{email}[/cyan]")
            console.print()
            
            if is_admin:
                log_info("This user has full admin privileges")
            else:
                log_info("This user can only see their own projects")
                
        else:
            log_error("Failed to create user")
            console.print(result.stdout)
            raise typer.Exit(1)
            
    except subprocess.CalledProcessError as e:
        log_error("Failed to create user")
        if e.stderr:
            console.print(f"[red]{e.stderr}[/red]")
        raise typer.Exit(1)


@app.command()
def backup(
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory")
) -> None:
    """Backup database and configuration."""
    print_banner("DockLite Backup")
    
    # Determine backup directory
    backup_dir = output if output else BACKUPS_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"docklite_backup_{timestamp}"
    backup_path = backup_dir / f"{backup_name}.tar.gz"
    
    log_step(f"Creating backup: {backup_name}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Backup database
        log_info("Backing up database...")
        db_file = BACKEND_DATA_DIR / "docklite.db"
        if db_file.exists():
            import shutil
            shutil.copy(db_file, temp_path / "docklite.db")
            log_success("Database backed up")
        else:
            log_warning("Database file not found")
        
        # Backup configuration
        log_info("Backing up configuration...")
        if ENV_FILE.exists():
            import shutil
            shutil.copy(ENV_FILE, temp_path / ".env")
        if DOCKER_COMPOSE_FILE.exists():
            import shutil
            shutil.copy(DOCKER_COMPOSE_FILE, temp_path / "docker-compose.yml")
        log_success("Configuration backed up")
        
        # Backup SSH keys (if exist)
        log_info("Backing up SSH configuration...")
        ssh_dir = Path("/home/docklite/.ssh")
        if ssh_dir.exists():
            ssh_backup = temp_path / "ssh"
            ssh_backup.mkdir()
            authorized_keys = ssh_dir / "authorized_keys"
            if authorized_keys.exists():
                import shutil
                try:
                    shutil.copy(authorized_keys, ssh_backup / "authorized_keys")
                except PermissionError:
                    subprocess.run(
                        ["sudo", "cp", str(authorized_keys), str(ssh_backup / "authorized_keys")],
                        check=False
                    )
        
        # Create metadata file
        metadata = f"""DockLite Backup
================
Date: {datetime.now()}
Hostname: {get_hostname()}
Version: {VERSION}
User: {Path.home().name}

Contents:
- Database (SQLite)
- Configuration (.env, docker-compose.yml)
- SSH keys
"""
        (temp_path / "backup_info.txt").write_text(metadata)
        
        # Create tar archive
        log_step("Creating archive...")
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(temp_path, arcname=".")
    
    # Get backup size
    backup_size = backup_path.stat().st_size
    size_mb = backup_size / (1024 * 1024)
    
    log_success("Backup created successfully!")
    console.print()
    print_banner("Backup Complete")
    log_info(f"File:     [cyan]{backup_path}[/cyan]")
    log_info(f"Size:     [cyan]{size_mb:.2f} MB[/cyan]")
    log_info(f"Location: [cyan]{backup_dir}[/cyan]")
    console.print()
    log_info(f"To restore: [cyan]./docklite restore {backup_path}[/cyan]")


@app.command()
def restore(
    backup_file: Path = typer.Argument(..., help="Backup file to restore"),
    no_confirm: bool = typer.Option(False, "--no-confirm", help="Skip confirmation prompt")
) -> None:
    """Restore from backup."""
    if not backup_file.exists():
        log_error(f"Backup file not found: {backup_file}")
        raise typer.Exit(1)
    
    print_banner("DockLite Restore")
    
    log_warning("This will REPLACE current database and configuration!")
    if not no_confirm:
        if not confirm("Continue with restore?"):
            log_info("Cancelled")
            raise typer.Abort()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract backup
        log_step("Extracting backup...")
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(temp_path)
        log_success("Backup extracted")
        
        # Show backup info
        info_file = temp_path / "backup_info.txt"
        if info_file.exists():
            console.print()
            console.print(info_file.read_text())
            console.print()
        
        # Stop services
        log_step("Stopping services...")
        docker_compose_cmd("down", cwd=PROJECT_ROOT)
        
        # Backup current state
        log_step("Backing up current state...")
        safety_backup_dir = BACKUPS_DIR
        safety_backup_dir.mkdir(parents=True, exist_ok=True)
        safety_name = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        safety_backup = safety_backup_dir / safety_name
        
        import shutil
        with tarfile.open(safety_backup, "w:gz") as tar:
            if BACKEND_DATA_DIR.exists():
                tar.add(BACKEND_DATA_DIR, arcname="backend-data")
            if ENV_FILE.exists():
                tar.add(ENV_FILE, arcname=".env")
            if DOCKER_COMPOSE_FILE.exists():
                tar.add(DOCKER_COMPOSE_FILE, arcname="docker-compose.yml")
        log_success(f"Safety backup created: {safety_backup}")
        
        # Restore database
        log_step("Restoring database...")
        db_backup = temp_path / "docklite.db"
        if db_backup.exists():
            BACKEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy(db_backup, BACKEND_DATA_DIR / "docklite.db")
            log_success("Database restored")
        
        # Restore configuration
        log_step("Restoring configuration...")
        env_backup = temp_path / ".env"
        if env_backup.exists():
            shutil.copy(env_backup, ENV_FILE)
        compose_backup = temp_path / "docker-compose.yml"
        if compose_backup.exists():
            shutil.copy(compose_backup, DOCKER_COMPOSE_FILE)
        log_success("Configuration restored")
        
        # Restore SSH keys
        ssh_backup = temp_path / "ssh" / "authorized_keys"
        if ssh_backup.exists():
            log_step("Restoring SSH keys...")
            subprocess.run(
                ["sudo", "mkdir", "-p", "/home/docklite/.ssh"],
                check=False
            )
            subprocess.run(
                ["sudo", "cp", str(ssh_backup), "/home/docklite/.ssh/authorized_keys"],
                check=False
            )
            subprocess.run(
                ["sudo", "chown", "-R", "docklite:docklite", "/home/docklite/.ssh"],
                check=False
            )
            subprocess.run(
                ["sudo", "chmod", "600", "/home/docklite/.ssh/authorized_keys"],
                check=False
            )
            log_success("SSH keys restored")
    
    # Restart services
    log_step("Starting services...")
    docker_compose_cmd("up", "-d", cwd=PROJECT_ROOT)
    time.sleep(3)
    
    log_success("Restore complete!")
    console.print()
    log_info("DockLite has been restored from backup")
    log_info(f"Safety backup saved at: [cyan]{safety_backup}[/cyan]")


@app.command()
def clean(
    all_resources: bool = typer.Option(False, "--all", help="Clean everything"),
    images: bool = typer.Option(False, "--images", help="Clean unused images only"),
    volumes: bool = typer.Option(False, "--volumes", help="Clean unused volumes only"),
    logs: bool = typer.Option(False, "--logs", help="Clean log files"),
) -> None:
    """Clean up unused resources."""
    print_banner("DockLite Cleanup")
    
    # Interactive mode if no options specified
    if not any([all_resources, images, volumes, logs]):
        console.print("What would you like to clean?")
        console.print("1) Unused Docker images")
        console.print("2) Unused Docker volumes")
        console.print("3) Log files")
        console.print("4) All of the above")
        console.print("5) Cancel")
        
        choice = typer.prompt("Select option [1-5]", type=int)
        
        if choice == 1:
            images = True
        elif choice == 2:
            volumes = True
        elif choice == 3:
            logs = True
        elif choice == 4:
            all_resources = True
        elif choice == 5:
            log_info("Cancelled")
            raise typer.Abort()
        else:
            log_error("Invalid choice")
            raise typer.Exit(1)
    
    if all_resources:
        images = volumes = logs = True
    
    # Clean unused images
    if images:
        log_step("Cleaning unused Docker images...")
        subprocess.run(["docker", "image", "prune", "-f"], check=True)
        log_success("Unused images removed")
    
    # Clean unused volumes
    if volumes:
        log_warning("This will remove unused volumes!")
        if confirm("Continue?"):
            log_step("Cleaning unused Docker volumes...")
            subprocess.run(["docker", "volume", "prune", "-f"], check=True)
            log_success("Unused volumes removed")
    
    # Clean logs
    if logs:
        log_step("Cleaning log files...")
        result = subprocess.run(
            ["docker-compose", "ps", "-q"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            container_ids = result.stdout.strip().split('\n')
            for cid in container_ids:
                if cid:
                    # Get log path
                    log_result = subprocess.run(
                        ["docker", "inspect", "--format={{.LogPath}}", cid],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if log_result.returncode == 0:
                        log_path = log_result.stdout.strip()
                        subprocess.run(
                            ["sudo", "truncate", "-s", "0", log_path],
                            check=False
                        )
        
        log_success("Logs cleaned")
    
    # Show disk usage
    log_step("Disk usage after cleanup:")
    subprocess.run(["docker", "system", "df"])
    
    log_success("Cleanup complete!")


@app.command()
def status(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
) -> None:
    """Show system status."""
    print_banner("DockLite System Status")
    
    # Check containers
    console.print()
    log_step("Container Status:")
    docker_compose_cmd("ps", cwd=PROJECT_ROOT)
    
    # Check if containers are running
    console.print()
    status_dict = get_container_status()
    
    if status_dict["traefik"]:
        console.print("✅ Traefik:  [green]Running[/green]")
    else:
        console.print("❌ Traefik:  [red]Stopped[/red]")
    
    if status_dict["backend"]:
        console.print("✅ Backend:  [green]Running[/green]")
    else:
        console.print("❌ Backend:  [red]Stopped[/red]")
    
    if status_dict["frontend"]:
        console.print("✅ Frontend: [green]Running[/green]")
    else:
        console.print("❌ Frontend: [red]Stopped[/red]")
    
    # Show URLs
    if all(status_dict.values()):
        console.print()
        log_step("Access URLs (via Traefik):")
        
        log_info(f"Frontend:          [cyan]{get_access_url()}[/cyan]")
        log_info(f"Backend API:       [cyan]{get_access_url('/api')}[/cyan]")
        log_info(f"API Docs:          [cyan]{get_access_url('/docs')}[/cyan]")
        log_info(f"Traefik Dashboard: [cyan]{get_access_url('/traefik')}[/cyan] [yellow](admin only)[/yellow]")
        
        # Show localhost alternative if hostname is not localhost
        current_hostname = get_hostname()
        if current_hostname != "localhost":
            log_info("")
            log_info(f"Local access:      [cyan]http://localhost[/cyan]")
    
    # Show version
    console.print()
    log_step("Version:")
    log_info(f"DockLite: [cyan]v{VERSION}[/cyan]")
    
    # Show disk usage
    if verbose:
        console.print()
        log_step("Docker Disk Usage:")
        subprocess.run(["docker", "system", "df"])
        
        console.print()
        log_step("Database Info:")
        db_file = BACKEND_DATA_DIR / "docklite.db"
        if db_file.exists():
            db_size = db_file.stat().st_size / (1024 * 1024)
            log_info(f"Database size: [cyan]{db_size:.2f} MB[/cyan]")
            log_info(f"Location: [cyan]{db_file}[/cyan]")
        else:
            log_warning("Database not found")
        
        console.print()
        log_step("Projects Directory:")
        projects_dir = Path("/home/docklite/projects")
        if projects_dir.exists():
            try:
                result = subprocess.run(
                    ["sudo", "find", str(projects_dir), "-mindepth", "1", "-maxdepth", "1", "-type", "d"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                project_count = len([l for l in result.stdout.strip().split('\n') if l])
                log_info(f"Projects: [cyan]{project_count}[/cyan]")
            except Exception:
                log_warning("Could not count projects")
        else:
            log_warning("Projects directory not found")
    
    console.print()


@app.command(name="reset-password")
def reset_password(
    username: str = typer.Argument(..., help="Username"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="New password (interactive if not provided)")
) -> None:
    """Reset user password."""
    print_banner("Reset User Password")
    
    # Check Docker
    check_docker()
    
    # Check if backend is running
    if not is_container_running(CONTAINER_BACKEND):
        log_warning("Backend is not running. Starting it...")
        docker_compose_cmd("up", "-d", "backend", cwd=PROJECT_ROOT)
        time.sleep(3)
    
    # First, get list of existing users
    log_step("Checking existing users...")
    
    result = docker_compose_cmd(
        "exec", "-T", "backend",
        "python", "-m", "app.cli_helpers.reset_password", "list",
        cwd=PROJECT_ROOT,
        capture_output=True
    )
    
    users_list = result.stdout.strip()
    
    if users_list == "NO_USERS":
        log_warning("No users found in database!")
        log_info("Use the setup screen to create the first admin user:")
        log_info(f"[cyan]{get_access_url()}[/cyan]")
        raise typer.Exit(1)
    
    # Check if requested user exists
    if not any(line.startswith(f"{username}:") for line in users_list.split('\n')):
        log_error(f"User '{username}' not found!")
        console.print()
        log_step("Existing users:")
        for line in users_list.split('\n'):
            if ':' in line:
                user, role = line.split(':', 1)
                if role == "admin":
                    log_info(f"  [cyan]{user}[/cyan] [yellow]({role})[/yellow]")
                else:
                    log_info(f"  [cyan]{user}[/cyan] ({role})")
        console.print()
        log_info(f"Usage: [cyan]./docklite reset-password <username>[/cyan]")
        raise typer.Exit(1)
    
    console.print()
    log_info(f"Username: [cyan]{username}[/cyan]")
    console.print()
    
    # If password not provided, ask interactively
    if not password:
        log_step(f"Enter new password for user '{username}':")
        password = typer.prompt("Password", hide_input=True)
        password_confirm = typer.prompt("Confirm password", hide_input=True)
        
        if password != password_confirm:
            log_error("Passwords don't match!")
            raise typer.Exit(1)
        
        if len(password) < 6:
            log_error("Password must be at least 6 characters!")
            raise typer.Exit(1)
    
    # Execute password reset
    log_step("Resetting password...")
    
    result = docker_compose_cmd(
        "exec", "-T", "backend",
        "python", "-m", "app.cli_helpers.reset_password", "reset", username, password,
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False
    )
    
    if "SUCCESS" in result.stdout:
        console.print()
        log_success("Password reset successfully!")
        console.print()
        
        # Show user info
        for line in result.stdout.split('\n'):
            if line.startswith('User ID:') or line.startswith('Email:') or \
               line.startswith('Admin:') or line.startswith('Active:'):
                console.print(line)
        
        console.print()
        log_info("You can now login with:")
        log_info(f"  Username: [cyan]{username}[/cyan]")
        log_info(f"  Password: [cyan][your new password][/cyan]")
        console.print()
        log_info(f"Frontend: [cyan]{get_access_url()}[/cyan]")
    else:
        console.print()
        log_error("Failed to reset password")
        console.print(result.stdout)
        raise typer.Exit(1)


@app.command(name="list-users")
def list_users(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
) -> None:
    """List all users."""
    print_banner("DockLite Users")
    
    # Check Docker
    check_docker()
    
    # Check if backend is running
    if not is_container_running(CONTAINER_BACKEND):
        log_warning("Backend is not running. Starting it...")
        docker_compose_cmd("up", "-d", "backend", cwd=PROJECT_ROOT)
        time.sleep(3)
    
    # Get users list
    log_step("Loading users...")
    console.print()
    
    if verbose:
        # Detailed user info
        result = docker_compose_cmd(
            "exec", "-T", "backend",
            "python", "-m", "app.cli_helpers.list_users", "detailed",
            cwd=PROJECT_ROOT,
            capture_output=True
        )
        
        output = result.stdout.strip()
        
        if output == "NO_USERS":
            log_warning("No users found in database!")
            log_info("Use the setup screen to create the first admin user:")
            log_info(f"[cyan]{get_access_url()}[/cyan]")
            raise typer.Exit(1)
        
        # Create table
        table = create_table("Users", show_lines=True)
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Username", style="cyan")
        table.add_column("Email")
        table.add_column("Role")
        table.add_column("Status")
        table.add_column("System User")
        
        for line in output.split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 6:
                    user_id, username, email, role, status, sys_user = parts
                    
                    # Style based on role and status
                    role_style = "yellow" if role == "admin" else "white"
                    status_style = "green" if status == "active" else "red"
                    
                    table.add_row(
                        user_id,
                        username,
                        email,
                        f"[{role_style}]{role}[/{role_style}]",
                        f"[{status_style}]{status}[/{status_style}]",
                        sys_user
                    )
        
        console.print(table)
    else:
        # Simple list
        result = docker_compose_cmd(
            "exec", "-T", "backend",
            "python", "-m", "app.cli_helpers.list_users", "simple",
            cwd=PROJECT_ROOT,
            capture_output=True
        )
        
        output = result.stdout.strip()
        
        if output == "NO_USERS":
            log_warning("No users found in database!")
            log_info("Use the setup screen to create the first admin user:")
            log_info(f"[cyan]{get_access_url()}[/cyan]")
            raise typer.Exit(1)
        
        for line in output.split('\n'):
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 3:
                    username, role, status = parts
                    
                    if role == "admin":
                        if status == "✓":
                            log_success(f"[cyan]{username}[/cyan] [yellow]({role})[/yellow]")
                        else:
                            log_warning(f"[cyan]{username}[/cyan] [yellow]({role})[/yellow] [red][inactive][/red]")
                    else:
                        if status == "✓":
                            log_info(f"[cyan]{username}[/cyan] ({role})")
                        else:
                            log_warning(f"[cyan]{username}[/cyan] ({role}) [red][inactive][/red]")
    
    console.print()
    
    # Count users
    result = docker_compose_cmd(
        "exec", "-T", "backend",
        "python", "-m", "app.cli_helpers.list_users", "count",
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False
    )
    
    count = result.stdout.strip()
    log_info(f"Total users: [cyan]{count}[/cyan]")
    
    console.print()
    
    if not verbose:
        log_info("Use [cyan]--verbose[/cyan] for detailed information")
    
    console.print()

