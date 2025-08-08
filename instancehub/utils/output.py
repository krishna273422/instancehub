"""
Output formatting and console utilities.
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

console = Console()

def setup_console(verbose=False):
    """Setup console with appropriate settings."""
    global console
    if verbose:
        console = Console(stderr=True, force_terminal=True)
    else:
        console = Console()

def print_success(message):
    """Print success message in green."""
    rprint(f"[green]✓[/green] {message}")

def print_error(message):
    """Print error message in red."""
    rprint(f"[red]✗[/red] {message}")

def print_warning(message):
    """Print warning message in yellow."""
    rprint(f"[yellow]⚠[/yellow] {message}")

def print_info(message):
    """Print info message in blue."""
    rprint(f"[blue]ℹ[/blue] {message}")

def create_table(title, columns):
    """Create a rich table with given title and columns."""
    table = Table(title=title)
    for column in columns:
        table.add_column(column['name'], style=column.get('style', 'white'))
    return table

def create_panel(content, title=None, style="blue"):
    """Create a rich panel with content."""
    return Panel(content, title=title, border_style=style)

def create_progress():
    """Create a progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    )

def format_bytes(bytes_value):
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def format_uptime(seconds):
    """Format uptime in seconds to human readable format."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
