"""Console utilities with Rich for beautiful output."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

# Create global console instance
console = Console()


def log_info(message: str) -> None:
    """Print info message with icon."""
    console.print(f"ℹ {message}", style="blue")


def log_success(message: str) -> None:
    """Print success message with icon."""
    console.print(f"✅ {message}", style="green")


def log_error(message: str) -> None:
    """Print error message with icon to stderr."""
    import sys
    console_err = Console(stderr=True)
    console_err.print(f"❌ {message}", style="red bold")


def log_warning(message: str) -> None:
    """Print warning message with icon."""
    console.print(f"⚠️  {message}", style="yellow")


def log_step(message: str) -> None:
    """Print step message with icon."""
    console.print(f"▶ {message}", style="cyan")


def print_banner(title: str) -> None:
    """Print a beautiful banner with title."""
    panel = Panel(
        title,
        expand=False,
        border_style="cyan",
        padding=(0, 1)
    )
    console.print(panel)


def confirm(
    prompt: str,
    default: bool = False,
    abort: bool = False
) -> bool:
    """
    Ask for user confirmation.
    
    Args:
        prompt: Question to ask
        default: Default answer
        abort: Abort if user says no
    
    Returns:
        bool: User's answer
    """
    return typer.confirm(prompt, default=default, abort=abort)


def create_table(
    title: Optional[str] = None,
    *,
    show_header: bool = True,
    show_lines: bool = False
) -> Table:
    """
    Create a Rich table for displaying data.
    
    Args:
        title: Table title
        show_header: Show column headers
        show_lines: Show lines between rows
    
    Returns:
        Table: Configured Rich table
    """
    return Table(
        title=title,
        show_header=show_header,
        show_lines=show_lines,
        border_style="cyan"
    )


def create_progress() -> Progress:
    """
    Create a Rich progress bar with spinner.
    
    Returns:
        Progress: Configured progress bar
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    )

