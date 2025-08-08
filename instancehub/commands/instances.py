"""
AWS EC2 instance management commands.
"""

import click
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from rich.table import Table
from rich import print as rprint

from instancehub.utils.output import (
    console, print_success, print_error, print_warning, 
    create_table, create_progress
)
from instancehub.core.aws import EC2Manager

@click.group()
def instances():
    """Manage AWS EC2 instances."""
    pass

@instances.command()
@click.option('--region', '-r', default='us-east-1', help='AWS region')
@click.option('--state', '-s', help='Filter by instance state (running, stopped, etc.)')
@click.option('--tag', '-t', help='Filter by tag (key=value)')
def list(region, state, tag):
    """List all EC2 instances."""
    try:
        ec2_manager = EC2Manager(region)
        instances_data = ec2_manager.list_instances(state_filter=state, tag_filter=tag)
        
        if not instances_data:
            print_warning("No instances found matching the criteria.")
            return
        
        table = Table(title=f"EC2 Instances in {region}")
        table.add_column("Instance ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("State", style="yellow")
        table.add_column("Type", style="blue")
        table.add_column("Public IP", style="magenta")
        table.add_column("Private IP", style="white")
        
        for instance in instances_data:
            state_color = "green" if instance['state'] == "running" else "red"
            table.add_row(
                instance['id'],
                instance['name'],
                f"[{state_color}]{instance['state']}[/{state_color}]",
                instance['type'],
                instance['public_ip'] or "N/A",
                instance['private_ip'] or "N/A"
            )
        
        console.print(table)
        
    except NoCredentialsError:
        print_error("AWS credentials not found. Please configure your credentials.")
    except ClientError as e:
        print_error(f"AWS error: {e}")
    except Exception as e:
        print_error(f"Error listing instances: {e}")

@instances.command()
@click.argument('instance_id')
@click.option('--region', '-r', default='us-east-1', help='AWS region')
@click.option('--wait', '-w', is_flag=True, help='Wait for instance to start')
def start(instance_id, region, wait):
    """Start an EC2 instance."""
    try:
        ec2_manager = EC2Manager(region)
        
        with create_progress() as progress:
            task = progress.add_task("Starting instance...", total=None)
            result = ec2_manager.start_instance(instance_id, wait=wait)
            progress.update(task, completed=True)
        
        if result:
            print_success(f"Instance {instance_id} started successfully.")
        else:
            print_error(f"Failed to start instance {instance_id}.")
            
    except Exception as e:
        print_error(f"Error starting instance: {e}")

@instances.command()
@click.argument('instance_id')
@click.option('--region', '-r', default='us-east-1', help='AWS region')
@click.option('--wait', '-w', is_flag=True, help='Wait for instance to stop')
def stop(instance_id, region, wait):
    """Stop an EC2 instance."""
    try:
        ec2_manager = EC2Manager(region)
        
        with create_progress() as progress:
            task = progress.add_task("Stopping instance...", total=None)
            result = ec2_manager.stop_instance(instance_id, wait=wait)
            progress.update(task, completed=True)
        
        if result:
            print_success(f"Instance {instance_id} stopped successfully.")
        else:
            print_error(f"Failed to stop instance {instance_id}.")
            
    except Exception as e:
        print_error(f"Error stopping instance: {e}")

@instances.command()
@click.argument('instance_id')
@click.option('--region', '-r', default='us-east-1', help='AWS region')
def status(instance_id, region):
    """Get detailed status of an EC2 instance."""
    try:
        ec2_manager = EC2Manager(region)
        instance_info = ec2_manager.get_instance_details(instance_id)
        
        if not instance_info:
            print_error(f"Instance {instance_id} not found.")
            return
        
        table = Table(title=f"Instance Details: {instance_id}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in instance_info.items():
            table.add_row(key, str(value))
        
        console.print(table)
        
    except Exception as e:
        print_error(f"Error getting instance status: {e}")

@instances.command()
@click.argument('instance_id')
@click.option('--region', '-r', default='us-east-1', help='AWS region')
@click.option('--wait', '-w', is_flag=True, help='Wait for restart to complete')
def restart(instance_id, region, wait):
    """Restart an EC2 instance."""
    try:
        ec2_manager = EC2Manager(region)
        
        with create_progress() as progress:
            task = progress.add_task("Restarting instance...", total=None)
            result = ec2_manager.restart_instance(instance_id, wait=wait)
            progress.update(task, completed=True)
        
        if result:
            print_success(f"Instance {instance_id} restarted successfully.")
        else:
            print_error(f"Failed to restart instance {instance_id}.")
            
    except Exception as e:
        print_error(f"Error restarting instance: {e}")
