"""Development commands for DockLite CLI."""

import time
import typer
from pathlib import Path
from typing import Optional

from ..config import (
    PROJECT_ROOT,
    DEFAULT_PROJECTS_DIR,
    CONTAINER_BACKEND,
    CONTAINER_FRONTEND,
    get_access_url
)
from ..utils.console import (
    log_info,
    log_success,
    log_warning,
    log_step,
    log_error,
    print_banner,
    console
)
from ..utils.docker import (
    docker_compose_cmd,
    is_container_running,
    get_container_status
)
from ..utils.validation import check_docker, check_docker_compose

app = typer.Typer(help="Development commands")


@app.command(name="setup-dev")
def setup_dev():
    """Setup development environment (create venv, install dependencies, create .env)."""
    import subprocess
    import sys
    import platform
    
    print_banner("DockLite Development Setup")
    
    # Check Python
    log_step("Checking Python installation...")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info < (3, 8):
        log_error(f"Python 3.8+ required, found {python_version}")
        raise typer.Exit(1)
    log_success(f"Python {python_version} found")
    
    # Create virtual environment
    venv_path = PROJECT_ROOT / ".venv"
    requirements_file = PROJECT_ROOT / "scripts" / "requirements.txt"
    
    if not venv_path.exists():
        log_step("Creating virtual environment...")
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True
            )
            log_success(f"Virtual environment created at .venv/")
        except subprocess.CalledProcessError as e:
            log_error("Failed to create virtual environment")
            console.print(f"[red]Error: {e.stderr.decode()}[/red]")
            log_info("Make sure python3-venv is installed:")
            if platform.system() == "Linux":
                console.print("  sudo apt-get install python3-venv")
            raise typer.Exit(1)
    else:
        log_success("Virtual environment already exists")
    
    # Detect venv python
    if platform.system() == "Windows":
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"
    
    # Install CLI dependencies in venv
    log_step("Installing Python CLI dependencies in venv...")
    try:
        result = subprocess.run(
            [str(venv_pip), "install", "-q", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
            text=True
        )
        log_success("CLI dependencies installed in venv")
        
        # Show warnings if any (but dimmed)
        if result.stderr and "WARNING" in result.stderr:
            console.print("[dim]" + result.stderr.strip() + "[/dim]")
            
    except subprocess.CalledProcessError as e:
        log_error("Failed to install CLI dependencies")
        console.print(f"[red]Error: {e.stderr}[/red]")
        log_info(f"Try manually: .venv/bin/pip install -r {requirements_file}")
        raise typer.Exit(1)
    
    # Check .env file
    log_step("Checking .env configuration...")
    env_file = PROJECT_ROOT / ".env"
    env_example = PROJECT_ROOT / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            log_info("Creating .env from .env.example...")
            import shutil
            shutil.copy(env_example, env_file)
            log_success(".env file created")
            console.print()
            log_warning("Please edit .env and set your HOSTNAME:")
            console.print("  nano .env")
        else:
            log_warning("No .env.example found - creating basic .env...")
            with open(env_file, 'w') as f:
                f.write("# DockLite Configuration\n")
                f.write("HOSTNAME=localhost\n")
                f.write("TRAEFIK_DASHBOARD_HOST=localhost\n")
                f.write(f"PROJECTS_DIR={Path.home()}/docklite-projects\n")
                f.write("SECRET_KEY=dev-secret-key-change-in-production\n")
            log_success(".env file created with defaults")
    else:
        log_success(".env file exists")
    
    # Check Docker
    log_step("Checking Docker...")
    try:
        check_docker()
        check_docker_compose()
        log_success("Docker is running")
    except Exception:
        log_warning("Docker is not installed or not running")
        console.print("Install Docker Desktop (macOS) or Docker Engine (Linux)")
        console.print("See: https://docs.docker.com/get-docker/")
    
    # Make CLI executable
    log_step("Making CLI executable...")
    docklite_cli = PROJECT_ROOT / "docklite"
    docklite_sh = PROJECT_ROOT / "scripts" / "docklite.sh"
    docklite_cli.chmod(0o755)
    docklite_sh.chmod(0o755)
    log_success("CLI ready")
    
    console.print()
    print_banner("Setup Complete! 🎉")
    console.print()
    console.print("[bold green]Virtual environment ready![/bold green]")
    console.print(f"  Location: [cyan]{venv_path}[/cyan]")
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print("  1. Edit .env file:        [cyan]nano .env[/cyan]")
    console.print("  2. Start DockLite:        [cyan]./docklite start[/cyan]")
    console.print("  3. Create admin user:     [cyan]./docklite add-user admin -p 'YourPassword' --admin[/cyan]")
    console.print(f"  4. Open in browser:       [cyan]{get_access_url()}[/cyan]")
    console.print()
    console.print("[bold]Available commands:[/bold]")
    console.print("  [cyan]./docklite --help[/cyan]         # Show all commands")
    console.print("  [cyan]./docklite status[/cyan]         # Check system status")
    console.print("  [cyan]./docklite test[/cyan]           # Run all tests")
    console.print()
    console.print("[dim]Note: The ./docklite CLI automatically uses the .venv environment[/dim]")
    console.print()


@app.command()
def start(
    build: bool = typer.Option(False, "--build", "-b", help="Rebuild images before starting"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow logs after starting"),
):
    """Start DockLite services."""
    print_banner("Starting DockLite Development Environment")
    
    # Check prerequisites
    log_step("Checking prerequisites...")
    check_docker()
    check_docker_compose()
    log_success("Docker is ready")
    
    # Create projects directory if needed
    log_step("Creating projects directory...")
    DEFAULT_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    log_success("Projects directory ready")
    
    # Start services
    log_step("Starting services...")
    args = ["up", "-d"]
    if build:
        args.append("--build")
    
    docker_compose_cmd(*args, cwd=PROJECT_ROOT)
    
    # Wait for services
    log_step("Waiting for services to start...")
    time.sleep(3)
    
    # Check if containers are running
    if is_container_running(CONTAINER_BACKEND) and is_container_running(CONTAINER_FRONTEND):
        log_success("All services started successfully!")
    else:
        log_warning("Some services may not have started correctly")
    
    console.print()
    print_banner("DockLite is Running")
    log_info(f"Frontend:  [cyan]{get_access_url()}[/cyan]")
    log_info(f"Backend:   [cyan]{get_access_url('/api')}[/cyan]")
    log_info(f"API Docs:  [cyan]{get_access_url('/docs')}[/cyan]")
    log_info(f"Traefik: [cyan]{get_access_url('/traefik')}[/cyan] [yellow](admin only)[/yellow]")
    console.print()
    log_info(f"View logs: [cyan]./docklite logs[/cyan]")
    log_info(f"Stop:      [cyan]./docklite stop[/cyan]")
    console.print()
    
    # Follow logs if requested
    if follow:
        docker_compose_cmd("logs", "-f", cwd=PROJECT_ROOT)


@app.command()
def stop(
    volumes: bool = typer.Option(False, "--volumes", "-v", help="Remove volumes as well")
):
    """Stop DockLite services."""
    print_banner("Stopping DockLite")
    
    if volumes:
        log_warning("This will remove all volumes (including database)!")
        if not typer.confirm("Continue?"):
            log_info("Cancelled")
            raise typer.Abort()
    
    log_step("Stopping services...")
    args = ["down"]
    if volumes:
        args.append("-v")
    
    docker_compose_cmd(*args, cwd=PROJECT_ROOT)
    
    log_success("DockLite stopped")


@app.command()
def restart(
    build: bool = typer.Option(False, "--build", "-b", help="Rebuild images before restarting")
):
    """Restart DockLite services."""
    print_banner("Restarting DockLite")
    
    # Stop services
    log_step("Stopping services...")
    docker_compose_cmd("down", cwd=PROJECT_ROOT)
    log_success("DockLite stopped")
    
    console.print()
    
    # Start services (without following logs)
    start(build=build, follow=False)


@app.command()
def rebuild(
    no_cache: bool = typer.Option(False, "--no-cache", help="Build without using cache"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow logs after rebuild"),
):
    """Rebuild and restart services."""
    print_banner("Rebuilding DockLite")
    
    # Check prerequisites
    check_docker()
    check_docker_compose()
    
    # Stop services
    log_step("Stopping current services...")
    docker_compose_cmd("down", cwd=PROJECT_ROOT)
    
    # Rebuild
    log_step("Rebuilding images...")
    args = ["build"]
    if no_cache:
        args.append("--no-cache")
    
    docker_compose_cmd(*args, cwd=PROJECT_ROOT)
    
    # Start
    log_step("Starting services...")
    docker_compose_cmd("up", "-d", cwd=PROJECT_ROOT)
    
    # Wait
    log_step("Waiting for services...")
    time.sleep(3)
    
    log_success("Rebuild complete!")
    console.print()
    print_banner("DockLite is Running")
    log_info(f"Frontend:  [cyan]{get_access_url()}[/cyan]")
    log_info(f"Backend:   [cyan]{get_access_url('/api')}[/cyan]")
    log_info(f"API Docs:  [cyan]{get_access_url('/docs')}[/cyan]")
    log_info(f"Traefik: [cyan]{get_access_url('/traefik')}[/cyan] [yellow](admin only)[/yellow]")
    console.print()
    
    # Follow logs if requested
    if follow:
        docker_compose_cmd("logs", "-f", cwd=PROJECT_ROOT)


@app.command()
def logs(
    service: Optional[str] = typer.Argument(None, help="Service name (backend, frontend, traefik)")
):
    """Show container logs."""
    args = ["logs", "-f"]
    if service:
        args.append(service)
    
    docker_compose_cmd(*args, cwd=PROJECT_ROOT)


@app.command()
def test(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output"),
):
    """Run all tests (backend + frontend)."""
    print_banner("DockLite Test Suite")
    
    # Prepare pytest args
    pytest_args = []
    if verbose:
        pytest_args.append("-v")
    if quiet:
        pytest_args.append("-q")
    
    backend_passed = False
    frontend_passed = False
    
    # Backend tests
    console.print()
    log_step("Running backend tests...")
    try:
        docker_compose_cmd(
            "run", "--rm", "backend", "pytest", *pytest_args,
            cwd=PROJECT_ROOT,
            check=True
        )
        log_success("Backend tests passed")
        backend_passed = True
    except Exception:
        log_error("Backend tests failed")
    
    # Frontend tests
    console.print()
    log_step("Running frontend tests...")
    try:
        import subprocess
        frontend_dir = PROJECT_ROOT / "frontend"
        subprocess.run(
            ["npm", "test", "--", "--run"],
            cwd=frontend_dir,
            check=True
        )
        log_success("Frontend tests passed")
        frontend_passed = True
    except Exception:
        log_error("Frontend tests failed")
    
    # Summary
    console.print()
    print_banner("Test Summary")
    if backend_passed:
        log_success("Backend:  PASSED")
    else:
        log_error("Backend:  FAILED")
    
    if frontend_passed:
        log_success("Frontend: PASSED")
    else:
        log_error("Frontend: FAILED")
    
    console.print()
    
    # Exit with error if any tests failed
    if not (backend_passed and frontend_passed):
        log_error("Some tests failed")
        raise typer.Exit(1)
    
    log_success("All tests passed! 🎉")


@app.command(name="test-backend")
def test_backend(
    args: list[str] = typer.Argument(None, help="Arguments to pass to pytest")
):
    """Run backend tests only."""
    print_banner("Backend Tests (Python/Pytest)")
    
    log_step("Running backend tests...")
    
    # Pass all arguments to pytest
    pytest_args = list(args) if args else []
    docker_compose_cmd(
        "run", "--rm", "backend", "pytest", *pytest_args,
        cwd=PROJECT_ROOT
    )
    
    log_success("Backend tests complete")


@app.command(name="test-frontend")
def test_frontend(
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch mode"),
    ui: bool = typer.Option(False, "--ui", "-u", help="Open UI"),
    coverage: bool = typer.Option(False, "--coverage", help="Show coverage report"),
):
    """Run frontend tests only."""
    print_banner("Frontend Tests (Vitest)")
    
    frontend_dir = PROJECT_ROOT / "frontend"
    
    # Check node_modules
    if not (frontend_dir / "node_modules").exists():
        log_warning("node_modules not found. Installing dependencies...")
        import subprocess
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    # Run tests
    log_step("Running frontend tests...")
    
    import subprocess
    
    if watch:
        subprocess.run(["npm", "test"], cwd=frontend_dir)
    elif ui:
        subprocess.run(["npm", "test", "--", "--ui"], cwd=frontend_dir)
    else:
        args = ["npm", "test", "--", "--run"]
        if coverage:
            args.append("--coverage")
        subprocess.run(args, cwd=frontend_dir)
    
    log_success("Frontend tests complete")

