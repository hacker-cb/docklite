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
    log_info(f"Dashboard: [cyan]{get_access_url('/dashboard')}[/cyan] [yellow](admin only)[/yellow]")
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
    log_info(f"Dashboard: [cyan]{get_access_url('/dashboard')}[/cyan] [yellow](admin only)[/yellow]")
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

