"""
Main CLI entry point for InstanceHub.
"""

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from instancehub.commands.instances import instances
from instancehub.commands.monitor import monitor
from instancehub.commands.services import services
from instancehub.commands.config import config
from instancehub.utils.output import setup_console

console = Console()

@click.group()
@click.version_option(version="1.0.0", prog_name="InstanceHub")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config-file', '-c', help='Path to configuration file')
@click.pass_context
def main(ctx, verbose, config_file):
    """
    InstanceHub - A powerful CLI tool for managing cloud instances, monitoring systems, and handling services.
    
    Examples:
        instancehub instances list
        instancehub monitor dashboard
        instancehub services redis status
        instancehub config init
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config_file'] = config_file
    
    setup_console(verbose)

# Add command groups
main.add_command(instances)
main.add_command(monitor)
main.add_command(services)
main.add_command(config)

@main.command()
def info():
    """Show InstanceHub information and status."""
    table = Table(title="InstanceHub Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Version", "1.0.0")
    table.add_row("Author", "Your Name")
    table.add_row("Description", "Cloud instance and system management tool")
    table.add_row("Commands", "instances, monitor, services, config")
    
    console.print(table)

if __name__ == '__main__':
    main()
