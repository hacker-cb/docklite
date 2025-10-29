"""DockLite CLI - Main application."""

import typer
from typing import Optional

from . import __version__
from .commands import development, deployment, maintenance

# Create main Typer app
app = typer.Typer(
    name="docklite",
    help="DockLite - Multi-tenant Docker management system",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich"
)

# Add command groups
app.add_typer(development.app, name="dev", help="Development commands (start, stop, test, etc.)")
app.add_typer(deployment.app, name="deploy", help="Deployment commands (setup-user, setup-ssh, init-db)")
app.add_typer(maintenance.app, name="maint", help="Maintenance commands (backup, restore, status, etc.)")

# Register individual commands at root level for convenience
app.command(name="start")(development.start)
app.command(name="stop")(development.stop)
app.command(name="restart")(development.restart)
app.command(name="rebuild")(development.rebuild)
app.command(name="logs")(development.logs)
app.command(name="test")(development.test)
app.command(name="test-backend")(development.test_backend)
app.command(name="test-frontend")(development.test_frontend)

app.command(name="setup-user")(deployment.setup_user)
app.command(name="setup-ssh")(deployment.setup_ssh)
app.command(name="init-db")(deployment.init_db)

app.command(name="backup")(maintenance.backup)
app.command(name="restore")(maintenance.restore)
app.command(name="clean")(maintenance.clean)
app.command(name="status")(maintenance.status)
app.command(name="reset-password")(maintenance.reset_password)
app.command(name="list-users")(maintenance.list_users)


@app.command()
def version():
    """Show DockLite version."""
    from .utils.console import console
    console.print(f"DockLite v{__version__}")


@app.callback()
def main_callback():
    """
    DockLite CLI - Multi-tenant Docker management system.
    
    Commands:
      Development: start, stop, restart, rebuild, logs, test
      Deployment:  setup-user, setup-ssh, init-db
      Maintenance: backup, restore, clean, status, reset-password, list-users
    
    Examples:
      docklite start              # Start services
      docklite status             # Show status
      docklite test               # Run all tests
      docklite backup             # Backup database
      docklite list-users         # List all users
    """
    pass


if __name__ == "__main__":
    app()

