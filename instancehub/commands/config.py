"""
Configuration management commands.
"""

import click
import os
import yaml
from pathlib import Path
from rich.table import Table
from rich import print as rprint

from instancehub.utils.output import (
    console, print_success, print_error, print_warning, print_info
)
from instancehub.config.manager import ConfigManager

@click.group()
def config():
    """Configuration management."""
    pass

@config.command()
@click.option('--force', '-f', is_flag=True, help='Overwrite existing configuration')
def init(force):
    """Initialize InstanceHub configuration."""
    config_manager = ConfigManager()
    
    if config_manager.config_exists() and not force:
        print_warning("Configuration already exists. Use --force to overwrite.")
        return
    
    try:
        # Create default configuration
        default_config = {
            'aws': {
                'default_region': 'us-east-1',
                'profile': 'default'
            },
            'monitoring': {
                'cpu_threshold': 90,
                'memory_threshold': 90,
                'disk_threshold': 90,
                'refresh_interval': 2
            },
            'redis': {
                'default_host': 'localhost',
                'default_port': 6379,
                'default_db': 0
            },
            'output': {
                'color': True,
                'verbose': False,
                'format': 'table'
            }
        }
        
        config_manager.save_config(default_config)
        print_success(f"Configuration initialized at: {config_manager.config_path}")
        
        # Show the created configuration
        show_config()
        
    except Exception as e:
        print_error(f"Error initializing configuration: {e}")

@config.command()
def show():
    """Show current configuration."""
    show_config()

def show_config():
    """Helper function to display configuration."""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists():
        print_warning("No configuration found. Run 'instancehub config init' to create one.")
        return
    
    try:
        config_data = config_manager.load_config()
        
        print_info(f"Configuration file: {config_manager.config_path}")
        
        # AWS Configuration
        aws_config = config_data.get('aws', {})
        aws_table = Table(title="AWS Configuration")
        aws_table.add_column("Setting", style="cyan")
        aws_table.add_column("Value", style="white")
        
        aws_table.add_row("Default Region", aws_config.get('default_region', 'Not set'))
        aws_table.add_row("Profile", aws_config.get('profile', 'Not set'))
        
        # Monitoring Configuration
        monitoring_config = config_data.get('monitoring', {})
        monitoring_table = Table(title="Monitoring Configuration")
        monitoring_table.add_column("Setting", style="cyan")
        monitoring_table.add_column("Value", style="white")
        
        monitoring_table.add_row("CPU Threshold", f"{monitoring_config.get('cpu_threshold', 90)}%")
        monitoring_table.add_row("Memory Threshold", f"{monitoring_config.get('memory_threshold', 90)}%")
        monitoring_table.add_row("Disk Threshold", f"{monitoring_config.get('disk_threshold', 90)}%")
        monitoring_table.add_row("Refresh Interval", f"{monitoring_config.get('refresh_interval', 2)}s")
        
        # Redis Configuration
        redis_config = config_data.get('redis', {})
        redis_table = Table(title="Redis Configuration")
        redis_table.add_column("Setting", style="cyan")
        redis_table.add_column("Value", style="white")
        
        redis_table.add_row("Default Host", redis_config.get('default_host', 'localhost'))
        redis_table.add_row("Default Port", str(redis_config.get('default_port', 6379)))
        redis_table.add_row("Default DB", str(redis_config.get('default_db', 0)))
        
        # Output Configuration
        output_config = config_data.get('output', {})
        output_table = Table(title="Output Configuration")
        output_table.add_column("Setting", style="cyan")
        output_table.add_column("Value", style="white")
        
        output_table.add_row("Color", str(output_config.get('color', True)))
        output_table.add_row("Verbose", str(output_config.get('verbose', False)))
        output_table.add_row("Format", output_config.get('format', 'table'))
        
        console.print(aws_table)
        console.print(monitoring_table)
        console.print(redis_table)
        console.print(output_table)
        
    except Exception as e:
        print_error(f"Error reading configuration: {e}")

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration value."""
    config_manager = ConfigManager()
    
    try:
        config_data = config_manager.load_config() or {}
        
        # Parse nested key (e.g., "aws.default_region")
        keys = key.split('.')
        current = config_data
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Convert value to appropriate type
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        # Set the value
        current[keys[-1]] = value
        
        config_manager.save_config(config_data)
        print_success(f"Set {key} = {value}")
        
    except Exception as e:
        print_error(f"Error setting configuration: {e}")

@config.command()
@click.argument('key')
def get(key):
    """Get a configuration value."""
    config_manager = ConfigManager()
    
    try:
        config_data = config_manager.load_config()
        
        if not config_data:
            print_error("No configuration found.")
            return
        
        # Parse nested key
        keys = key.split('.')
        current = config_data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                print_error(f"Configuration key '{key}' not found.")
                return
        
        print_info(f"{key} = {current}")
        
    except Exception as e:
        print_error(f"Error getting configuration: {e}")

@config.command()
def edit():
    """Open configuration file in default editor."""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists():
        print_warning("No configuration found. Run 'instancehub config init' first.")
        return
    
    try:
        editor = os.environ.get('EDITOR', 'notepad' if os.name == 'nt' else 'nano')
        os.system(f'{editor} "{config_manager.config_path}"')
        print_success("Configuration file opened in editor.")
        
    except Exception as e:
        print_error(f"Error opening configuration file: {e}")

@config.command()
def path():
    """Show configuration file path."""
    config_manager = ConfigManager()
    print_info(f"Configuration file path: {config_manager.config_path}")

@config.command()
def validate():
    """Validate configuration file."""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists():
        print_error("No configuration file found.")
        return
    
    try:
        config_data = config_manager.load_config()
        
        # Basic validation
        errors = []
        
        # Check AWS configuration
        aws_config = config_data.get('aws', {})
        if 'default_region' not in aws_config:
            errors.append("Missing aws.default_region")
        
        # Check monitoring thresholds
        monitoring_config = config_data.get('monitoring', {})
        for threshold in ['cpu_threshold', 'memory_threshold', 'disk_threshold']:
            value = monitoring_config.get(threshold)
            if value is not None and (not isinstance(value, (int, float)) or value < 0 or value > 100):
                errors.append(f"Invalid {threshold}: must be between 0 and 100")
        
        # Check Redis configuration
        redis_config = config_data.get('redis', {})
        port = redis_config.get('default_port')
        if port is not None and (not isinstance(port, int) or port < 1 or port > 65535):
            errors.append("Invalid redis.default_port: must be between 1 and 65535")
        
        if errors:
            print_error("Configuration validation failed:")
            for error in errors:
                print_error(f"  - {error}")
        else:
            print_success("Configuration is valid.")
            
    except Exception as e:
        print_error(f"Error validating configuration: {e}")
