"""DockLite CLI - Main application."""

import typer
from typing import Optional

from . import __version__
from .commands import development, deployment, maintenance, user

# Create main Typer app with -h support
app = typer.Typer(
    name="docklite",
    help="DockLite - Multi-tenant Docker management system",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Add command groups
app.add_typer(development.app, name="dev", help="Development commands (5)")
app.add_typer(deployment.app, name="deploy", help="Deployment commands (3)")
app.add_typer(user.app, name="user", help="User management commands (3)")
app.add_typer(maintenance.app, name="maint", help="Maintenance commands (3)")

# Register essential commands at root level for convenience
app.command(name="start")(development.start)
app.command(name="stop")(development.stop)
app.command(name="restart")(development.restart)
app.command(name="logs")(development.logs)
app.command(name="test")(development.test)
app.command(name="status")(maintenance.status)


@app.command()
def version():
    """Show DockLite version."""
    from .utils.console import console
    console.print(f"DockLite v{__version__}")


@app.callback()
def main_callback():
    """
    DockLite CLI - Multi-tenant Docker management system.
    
    Daily Commands:
      start, stop, restart    # System lifecycle
      logs, status            # Monitoring
      test                    # Run all tests
    
    Command Groups:
      dev                     # Development (setup-dev, rebuild, test-*)
      deploy                  # Deployment (setup-user, setup-ssh, init-db)
      user                    # User management (add, list, reset-password)
      maint                   # Maintenance (backup, restore, clean)
    
    Examples:
      docklite start                    # Start services
      docklite status -v                # Check status
      docklite dev rebuild              # Rebuild images
      docklite user add admin           # Add user
      docklite deploy setup-user        # Production setup
    """
    pass


if __name__ == "__main__":
    app()

