"""User management commands for DockLite CLI."""

import subprocess
import time
import typer
from pathlib import Path
from typing import Optional

from ..config import (
    PROJECT_ROOT,
    CONTAINER_BACKEND,
    get_access_url
)
from ..utils.console import (
    log_info,
    log_success,
    log_warning,
    log_step,
    log_error,
    print_banner,
    console,
    create_table
)
from ..utils.docker import (
    docker_compose_cmd,
    is_container_running
)
from ..utils.validation import check_docker

app = typer.Typer(
    help="User management commands",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]}
)


@app.command(name="add")
def add(
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
from app.services.auth_service import AuthService

async def create_user():
    async with AsyncSessionLocal() as session:
        new_user = User(
            username="{username}",
            password_hash=AuthService.get_password_hash("{password}"),
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


@app.command(name="list")
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
        log_info(f"Usage: [cyan]./docklite user reset-password <username>[/cyan]")
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

