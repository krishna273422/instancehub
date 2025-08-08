"""
Service management commands (Redis, databases, etc.).
"""

import click
import redis
import subprocess
from rich.table import Table
from rich import print as rprint

from instancehub.utils.output import (
    console, print_success, print_error, print_warning, 
    create_table, format_bytes
)
from instancehub.core.services import RedisManager, ServiceHealthChecker

@click.group()
def services():
    """Manage services like Redis, databases, etc."""
    pass

@services.group()
def redis():
    """Redis service management."""
    pass

@redis.command()
@click.option('--host', '-h', default='localhost', help='Redis host')
@click.option('--port', '-p', default=6379, help='Redis port')
@click.option('--password', help='Redis password')
@click.option('--db', default=0, help='Redis database number')
def status(host, port, password, db):
    """Check Redis server status and get information."""
    try:
        redis_manager = RedisManager(host, port, password, db)
        info = redis_manager.get_server_info()
        
        if not info:
            print_error("Could not connect to Redis server.")
            return
        
        # Server Information
        server_table = Table(title="Redis Server Information")
        server_table.add_column("Property", style="cyan")
        server_table.add_column("Value", style="white")
        
        server_table.add_row("Version", info.get('redis_version', 'N/A'))
        server_table.add_row("Mode", info.get('redis_mode', 'N/A'))
        server_table.add_row("OS", info.get('os', 'N/A'))
        server_table.add_row("Uptime", f"{info.get('uptime_in_seconds', 0)} seconds")
        server_table.add_row("Connected Clients", str(info.get('connected_clients', 0)))
        
        # Memory Information
        memory_table = Table(title="Redis Memory Information")
        memory_table.add_column("Property", style="cyan")
        memory_table.add_column("Value", style="white")
        
        used_memory = info.get('used_memory', 0)
        used_memory_human = info.get('used_memory_human', 'N/A')
        used_memory_peak = info.get('used_memory_peak', 0)
        used_memory_peak_human = info.get('used_memory_peak_human', 'N/A')
        
        memory_table.add_row("Used Memory", used_memory_human)
        memory_table.add_row("Peak Memory", used_memory_peak_human)
        memory_table.add_row("Memory Fragmentation", str(info.get('mem_fragmentation_ratio', 'N/A')))
        
        # Stats Information
        stats_table = Table(title="Redis Statistics")
        stats_table.add_column("Property", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Commands", str(info.get('total_commands_processed', 0)))
        stats_table.add_row("Commands/sec", str(info.get('instantaneous_ops_per_sec', 0)))
        stats_table.add_row("Keyspace Hits", str(info.get('keyspace_hits', 0)))
        stats_table.add_row("Keyspace Misses", str(info.get('keyspace_misses', 0)))
        stats_table.add_row("Total Keys", str(redis_manager.get_total_keys()))
        
        console.print(server_table)
        console.print(memory_table)
        console.print(stats_table)
        
        print_success(f"Successfully connected to Redis at {host}:{port}")
        
    except Exception as e:
        print_error(f"Error connecting to Redis: {e}")

@redis.command()
@click.option('--host', '-h', default='localhost', help='Redis host')
@click.option('--port', '-p', default=6379, help='Redis port')
@click.option('--password', help='Redis password')
@click.option('--db', default=0, help='Redis database number')
def test(host, port, password, db):
    """Test Redis connection."""
    try:
        redis_manager = RedisManager(host, port, password, db)
        
        if redis_manager.test_connection():
            print_success(f"Successfully connected to Redis at {host}:{port}")
            
            # Test basic operations
            test_key = "instancehub:test"
            test_value = "connection_test"
            
            redis_manager.set_key(test_key, test_value)
            retrieved_value = redis_manager.get_key(test_key)
            
            if retrieved_value == test_value:
                print_success("Read/write test passed")
                redis_manager.delete_key(test_key)
                print_success("Cleanup completed")
            else:
                print_error("Read/write test failed")
        else:
            print_error(f"Could not connect to Redis at {host}:{port}")
            
    except Exception as e:
        print_error(f"Error testing Redis connection: {e}")

@redis.command()
@click.option('--host', '-h', default='localhost', help='Redis host')
@click.option('--port', '-p', default=6379, help='Redis port')
@click.option('--password', help='Redis password')
@click.option('--db', default=0, help='Redis database number')
@click.option('--pattern', default='*', help='Key pattern to match')
@click.option('--limit', default=100, help='Maximum number of keys to show')
def keys(host, port, password, db, pattern, limit):
    """List Redis keys matching pattern."""
    try:
        redis_manager = RedisManager(host, port, password, db)
        keys_list = redis_manager.get_keys(pattern, limit)
        
        if not keys_list:
            print_warning(f"No keys found matching pattern: {pattern}")
            return
        
        table = Table(title=f"Redis Keys (Pattern: {pattern})")
        table.add_column("Key", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("TTL", style="green")
        
        for key in keys_list:
            key_type = redis_manager.get_key_type(key)
            ttl = redis_manager.get_key_ttl(key)
            ttl_str = str(ttl) if ttl > 0 else "No expiry" if ttl == -1 else "Expired"
            
            table.add_row(key, key_type, ttl_str)
        
        console.print(table)
        print_info(f"Showing {len(keys_list)} keys (limit: {limit})")
        
    except Exception as e:
        print_error(f"Error listing Redis keys: {e}")

@redis.command()
@click.option('--host', '-h', default='localhost', help='Redis host')
@click.option('--port', '-p', default=6379, help='Redis port')
@click.option('--password', help='Redis password')
@click.option('--clients', '-c', default=1, help='Number of clients')
@click.option('--requests', '-n', default=10000, help='Number of requests')
@click.option('--data-size', '-d', default=100, help='Data size in bytes')
def benchmark(host, port, password, clients, requests, data_size):
    """Run Redis benchmark test."""
    try:
        print_info(f"Running Redis benchmark: {clients} clients, {requests} requests, {data_size} bytes data")
        
        cmd = [
            'redis-benchmark',
            '-h', host,
            '-p', str(port),
            '-c', str(clients),
            '-n', str(requests),
            '-d', str(data_size)
        ]
        
        if password:
            cmd.extend(['-a', password])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_success("Benchmark completed successfully")
            console.print(result.stdout)
        else:
            print_error(f"Benchmark failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print_error("Benchmark timed out after 5 minutes")
    except FileNotFoundError:
        print_error("redis-benchmark command not found. Please install Redis tools.")
    except Exception as e:
        print_error(f"Error running benchmark: {e}")

@services.command()
@click.option('--service', '-s', multiple=True, help='Service to check (can be used multiple times)')
def health(service):
    """Check health of various services."""
    health_checker = ServiceHealthChecker()
    
    services_to_check = list(service) if service else ['redis', 'postgresql', 'mysql', 'mongodb']
    
    table = Table(title="Service Health Check")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="yellow")
    
    for svc in services_to_check:
        status, details = health_checker.check_service(svc)
        status_color = "green" if status == "healthy" else "red"
        table.add_row(
            svc.title(),
            f"[{status_color}]{status}[/{status_color}]",
            details
        )
    
    console.print(table)
