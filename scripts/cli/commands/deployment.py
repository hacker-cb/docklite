"""Deployment commands for DockLite CLI."""

import subprocess
import time
import typer
from pathlib import Path
from typing import Optional

from ..config import PROJECT_ROOT, ENV_FILE, get_access_url
from ..utils.console import (
    log_info,
    log_success,
    log_warning,
    log_step,
    log_error,
    print_banner,
    console,
    confirm
)
from ..utils.docker import docker_compose_cmd, is_container_running
from ..utils.system import (
    check_root,
    get_actual_user,
    get_actual_home,
    user_exists,
    create_user,
    add_user_to_group,
    set_permissions,
    set_owner,
    backup_file
)
from ..utils.validation import check_docker

app = typer.Typer(help="Deployment commands")


@app.command(name="setup-user")
def setup_user(
    user: str = typer.Option("docklite", "--user", "-u", help="Username"),
    directory: Optional[str] = typer.Option(None, "--dir", "-d", help="Projects directory"),
) -> None:
    """Create system user for deployment."""
    check_root()
    
    print_banner("Setting up DockLite Deployment User")
    
    # Determine directories
    projects_dir = Path(directory) if directory else Path(f"/home/{user}/projects")
    
    log_info(f"User: [cyan]{user}[/cyan]")
    log_info(f"Projects directory: [cyan]{projects_dir}[/cyan]")
    console.print()
    
    # Create user if doesn't exist
    log_step("Checking user...")
    if user_exists(user):
        log_success(f"User '{user}' already exists")
    else:
        log_step(f"Creating user '{user}'...")
        create_user(user, shell="/bin/bash")
        log_success("User created")
    
    # Unlock account if locked
    result = subprocess.run(
        ["passwd", "-S", user],
        capture_output=True,
        text=True
    )
    if " L " in result.stdout:
        log_step("Unlocking account...")
        subprocess.run(["usermod", "-p", "*", user], check=True)
        log_success("Account unlocked")
    
    # Create projects directory
    log_step("Creating projects directory...")
    projects_dir.mkdir(parents=True, exist_ok=True)
    set_owner(projects_dir, user, recursive=True)
    set_permissions(projects_dir, 0o755)
    log_success(f"Projects directory: {projects_dir}")
    
    # Create .ssh directory for SSH keys
    log_step("Setting up SSH access...")
    ssh_dir = Path(f"/home/{user}/.ssh")
    ssh_dir.mkdir(parents=True, exist_ok=True)
    (ssh_dir / "authorized_keys").touch()
    set_owner(ssh_dir, user, recursive=True)
    set_permissions(ssh_dir, 0o700)
    set_permissions(ssh_dir / "authorized_keys", 0o600)
    log_success("SSH directory configured")
    
    # Add to docker group
    log_step("Adding to docker group...")
    add_user_to_group(user, "docker")
    log_success("Docker access granted")
    
    # Add current user to deploy user group (if different)
    actual_user = get_actual_user()
    if user != actual_user:
        log_step(f"Adding '{actual_user}' to '{user}' group...")
        add_user_to_group(actual_user, user)
        log_success("Groups configured")
    
    # Update .env file
    if ENV_FILE.exists():
        log_step("Updating .env configuration...")
        
        # Backup original
        backup_file(ENV_FILE)
        
        # Read current content
        content = ENV_FILE.read_text()
        lines = content.split('\n')
        
        # Update or add PROJECTS_DIR
        projects_dir_found = False
        deploy_user_found = False
        new_lines = []
        
        for line in lines:
            if line.startswith('PROJECTS_DIR='):
                new_lines.append(f'PROJECTS_DIR={projects_dir}')
                projects_dir_found = True
            elif line.startswith('DEPLOY_USER='):
                new_lines.append(f'DEPLOY_USER={user}')
                deploy_user_found = True
            else:
                new_lines.append(line)
        
        if not projects_dir_found:
            new_lines.append(f'PROJECTS_DIR={projects_dir}')
        if not deploy_user_found:
            new_lines.append(f'DEPLOY_USER={user}')
        
        ENV_FILE.write_text('\n'.join(new_lines))
        log_success("Configuration updated")
    
    # Create info file
    info_file = Path(f"/home/{user}/README.txt")
    info_content = f"""DockLite Deployment User
========================

This user is for deploying applications to DockLite.

User: {user}
Projects Directory: {projects_dir}

Project paths: {projects_dir}/{{project-slug}}/

SSH Access:
-----------
1. Add your SSH public key to: /home/{user}/.ssh/authorized_keys
2. Use rsync/scp to upload files:
   
   rsync -avz ./my-app/ {user}@server:{projects_dir}/{{project-slug}}/
   
3. Deploy with docker-compose:
   
   ssh {user}@server "cd {projects_dir}/{{project-slug}} && docker-compose up -d"

For more information, see: {PROJECT_ROOT}/SSH_ACCESS.md
"""
    info_file.write_text(info_content)
    set_owner(info_file, user)
    log_success(f"Info file created: {info_file}")
    
    console.print()
    print_banner("Setup Complete!")
    console.print()
    log_info("Next steps:")
    log_info(f"1. Configure SSH: [cyan]sudo ./docklite setup-ssh[/cyan]")
    log_info(f"2. Start DockLite: [cyan]./docklite start[/cyan]")
    log_info(f"3. Access UI: [cyan]{get_access_url()}[/cyan]")
    console.print()
    log_info(f"Documentation: [cyan]{PROJECT_ROOT}/SSH_ACCESS.md[/cyan]")
    console.print()


@app.command(name="setup-ssh")
def setup_ssh(
    user: str = typer.Option("docklite", "--user", "-u", help="Deploy user"),
) -> None:
    """Configure SSH for localhost deployment."""
    check_root()
    
    deploy_home = Path(f"/home/{user}")
    actual_user = get_actual_user()
    actual_home = get_actual_home()
    ssh_key = actual_home / ".ssh" / "id_ed25519"
    
    print_banner("DockLite SSH Configuration for Localhost")
    
    log_info(f"Actual user: [cyan]{actual_user}[/cyan]")
    log_info(f"Deploy user: [cyan]{user}[/cyan]")
    log_info(f"SSH key: [cyan]{ssh_key}[/cyan]")
    console.print()
    
    # Step 1: Ensure deploy user exists and is unlocked
    log_step("1️⃣  Checking deploy user...")
    if not user_exists(user):
        log_error(f"User '{user}' doesn't exist. Run: ./docklite setup-user")
        raise typer.Exit(1)
    log_success(f"User '{user}' exists")
    
    # Check if account is locked
    result = subprocess.run(
        ["passwd", "-S", user],
        capture_output=True,
        text=True
    )
    if " L " in result.stdout:
        log_step("Unlocking account...")
        subprocess.run(["usermod", "-p", "*", user], check=True)
        log_success("Account unlocked")
    
    # Step 2: Fix ~/.ssh permissions for actual user
    log_step(f"2️⃣  Fixing ~/.ssh permissions for {actual_user}...")
    ssh_dir = actual_home / ".ssh"
    if ssh_dir.exists():
        set_owner(ssh_dir, actual_user, recursive=True)
        set_permissions(ssh_dir, 0o700)
        log_success("Permissions fixed")
    else:
        ssh_dir.mkdir(parents=True, exist_ok=True)
        set_owner(ssh_dir, actual_user)
        set_permissions(ssh_dir, 0o700)
        log_success("Created ~/.ssh")
    
    # Step 3: Generate SSH key if doesn't exist
    log_step("3️⃣  Checking SSH key...")
    if ssh_key.exists():
        log_warning(f"SSH key already exists: {ssh_key}")
        log_info("Using existing key")
    else:
        log_step(f"Generating new SSH key for {actual_user}...")
        subprocess.run(
            ["sudo", "-u", actual_user, "ssh-keygen", "-t", "ed25519", 
             "-C", "docklite@localhost", "-f", str(ssh_key), "-N", ""],
            check=True
        )
        log_success(f"SSH key created: {ssh_key}")
    
    # Ensure key has correct permissions
    ssh_key.chmod(0o600)
    set_owner(ssh_key, actual_user)
    
    # Step 4: Setup .ssh for deploy user
    log_step(f"4️⃣  Setting up .ssh for {user}...")
    deploy_ssh = deploy_home / ".ssh"
    deploy_ssh.mkdir(parents=True, exist_ok=True)
    (deploy_ssh / "authorized_keys").touch()
    set_permissions(deploy_ssh, 0o700)
    set_permissions(deploy_ssh / "authorized_keys", 0o600)
    set_owner(deploy_ssh, user, recursive=True)
    log_success("Directory configured")
    
    # Step 5: Add public key to authorized_keys
    log_step("5️⃣  Adding SSH key to authorized_keys...")
    pubkey = (ssh_key.parent / f"{ssh_key.name}.pub").read_text().strip()
    
    authorized_keys = deploy_ssh / "authorized_keys"
    if pubkey in authorized_keys.read_text():
        log_warning("Key already in authorized_keys")
    else:
        with authorized_keys.open('a') as f:
            f.write(f"\n{pubkey}\n")
        log_success("Key added")
    
    # Fix permissions again
    authorized_keys.chmod(0o600)
    set_owner(authorized_keys, user)
    
    # Step 6: Create projects directory
    log_step("6️⃣  Creating projects directory...")
    projects_dir = deploy_home / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    set_owner(projects_dir, user, recursive=True)
    set_permissions(projects_dir, 0o755)
    log_success("Projects directory ready")
    
    # Step 7: Test SSH connection
    log_step("7️⃣  Testing SSH connection...")
    try:
        result = subprocess.run(
            ["sudo", "-u", actual_user, "ssh", "-o", "StrictHostKeyChecking=no",
             "-o", "BatchMode=yes", "-o", "UserKnownHostsFile=/dev/null",
             f"{user}@localhost", "echo SSH_OK"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "SSH_OK" in result.stdout:
            log_success("SSH connection works!")
            ssh_ok = True
        else:
            log_error("SSH connection failed")
            log_info(f"Output: {result.stdout}")
            ssh_ok = False
    except Exception as e:
        log_error(f"SSH test failed: {e}")
        ssh_ok = False
    
    # Step 8: Test docker access
    if ssh_ok:
        log_step("8️⃣  Testing docker-compose access...")
        result = subprocess.run(
            ["sudo", "-u", actual_user, "ssh", "-o", "StrictHostKeyChecking=no",
             "-o", "UserKnownHostsFile=/dev/null",
             f"{user}@localhost", "which docker-compose || which docker"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            log_success("docker-compose is accessible")
        else:
            log_warning("docker-compose not found")
            log_info("User was added to docker group, but needs re-login")
    
    # Summary
    console.print()
    print_banner("Setup Complete!")
    console.print()
    
    if ssh_ok:
        log_success("All checks passed!")
        console.print()
        log_info("You can now:")
        log_info(f"1. Start DockLite: [cyan]./docklite start[/cyan]")
        log_info(f"2. Test deployment: [cyan]ssh {user}@localhost[/cyan]")
        log_info(f"3. Check logs: [cyan]./docklite logs[/cyan]")
    else:
        log_error("SSH setup incomplete")
        console.print()
        log_info("Try these steps:")
        log_info(f"1. Check SSH server: [cyan]sudo systemctl status sshd[/cyan]")
        log_info(f"2. Test manually: [cyan]ssh -v {user}@localhost[/cyan]")
        log_info(f"3. Re-run setup: [cyan]sudo ./docklite setup-ssh[/cyan]")
    
    console.print()
    log_info(f"Documentation: [cyan]{PROJECT_ROOT}/SSH_ACCESS.md[/cyan]")
    console.print()


@app.command(name="init-db")
def init_db(
    reset: bool = typer.Option(False, "--reset", help="Reset database (deletes all data!)")
) -> None:
    """Initialize database."""
    print_banner("Database Initialization")
    
    if reset:
        log_warning("This will DELETE all database data!")
        if not confirm("Continue with database reset?"):
            log_info("Cancelled")
            raise typer.Abort()
        
        log_step("Removing database...")
        docker_compose_cmd("down", "-v", cwd=PROJECT_ROOT)
        
        db_file = PROJECT_ROOT / "backend-data" / "docklite.db"
        if db_file.exists():
            db_file.unlink()
        log_success("Database removed")
    
    # Ensure backend is running
    log_step("Starting backend container...")
    docker_compose_cmd("up", "-d", "backend", cwd=PROJECT_ROOT)
    
    # Wait for container
    time.sleep(2)
    
    # Run migrations
    log_step("Running database migrations...")
    docker_compose_cmd("exec", "-T", "backend", "alembic", "upgrade", "head", cwd=PROJECT_ROOT)
    
    log_success("Database initialized!")
    console.print()
    log_info(f"Backend is ready at: [cyan]{get_access_url('/api')}[/cyan]")
    log_info(f"API Docs at:         [cyan]{get_access_url('/docs')}[/cyan]")
    console.print()
    
    if reset:
        log_info("Database has been reset. You'll need to create an admin user via the setup screen.")

