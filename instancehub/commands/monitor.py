"""
System monitoring commands.
"""

import click
import time
import psutil
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import BarColumn, Progress, TextColumn
from rich import print as rprint

from instancehub.utils.output import (
    console, print_success, print_error, print_warning, print_info,
    create_table, format_bytes, format_uptime
)
from instancehub.core.monitor import SystemMonitor

@click.group()
def monitor():
    """System monitoring and alerts."""
    pass

@monitor.command()
@click.option('--refresh', '-r', default=2, help='Refresh interval in seconds')
@click.option('--duration', '-d', default=0, help='Duration to run (0 for infinite)')
def dashboard(refresh, duration):
    """Real-time system monitoring dashboard."""
    system_monitor = SystemMonitor()
    
    def create_dashboard():
        """Create the dashboard layout."""
        # CPU Information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        cpu_table = Table(title="CPU Information")
        cpu_table.add_column("Metric", style="cyan")
        cpu_table.add_column("Value", style="white")
        cpu_table.add_row("Usage", f"{cpu_percent}%")
        cpu_table.add_row("Cores", str(cpu_count))
        if cpu_freq:
            cpu_table.add_row("Frequency", f"{cpu_freq.current:.0f} MHz")
        
        # Memory Information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        memory_table = Table(title="Memory Information")
        memory_table.add_column("Metric", style="cyan")
        memory_table.add_column("Value", style="white")
        memory_table.add_row("Total RAM", format_bytes(memory.total))
        memory_table.add_row("Available", format_bytes(memory.available))
        memory_table.add_row("Used", format_bytes(memory.used))
        memory_table.add_row("Usage", f"{memory.percent}%")
        memory_table.add_row("Swap Total", format_bytes(swap.total))
        memory_table.add_row("Swap Used", format_bytes(swap.used))
        
        # Disk Information
        disk_usage = psutil.disk_usage('/')
        disk_table = Table(title="Disk Information")
        disk_table.add_column("Metric", style="cyan")
        disk_table.add_column("Value", style="white")
        disk_table.add_row("Total", format_bytes(disk_usage.total))
        disk_table.add_row("Used", format_bytes(disk_usage.used))
        disk_table.add_row("Free", format_bytes(disk_usage.free))
        disk_table.add_row("Usage", f"{(disk_usage.used / disk_usage.total) * 100:.1f}%")
        
        # Network Information
        net_io = psutil.net_io_counters()
        network_table = Table(title="Network Information")
        network_table.add_column("Metric", style="cyan")
        network_table.add_column("Value", style="white")
        network_table.add_row("Bytes Sent", format_bytes(net_io.bytes_sent))
        network_table.add_row("Bytes Received", format_bytes(net_io.bytes_recv))
        network_table.add_row("Packets Sent", str(net_io.packets_sent))
        network_table.add_row("Packets Received", str(net_io.packets_recv))
        
        # System Information
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        
        system_table = Table(title="System Information")
        system_table.add_column("Metric", style="cyan")
        system_table.add_column("Value", style="white")
        system_table.add_row("Uptime", format_uptime(uptime))
        system_table.add_row("Processes", str(len(psutil.pids())))
        system_table.add_row("Load Average", str(psutil.getloadavg() if hasattr(psutil, 'getloadavg') else 'N/A'))
        
        # Create layout
        top_row = Columns([cpu_table, memory_table])
        bottom_row = Columns([disk_table, network_table, system_table])

        from rich.console import Group
        dashboard_group = Group(top_row, bottom_row)

        return Panel(dashboard_group, title="System Dashboard")
    
    try:
        if duration > 0:
            end_time = time.time() + duration
        else:
            end_time = float('inf')
        
        with Live(create_dashboard(), refresh_per_second=1/refresh) as live:
            while time.time() < end_time:
                live.update(create_dashboard())
                time.sleep(refresh)
                
    except KeyboardInterrupt:
        print_success("Dashboard stopped.")

@monitor.command()
@click.option('--threshold', '-t', default=90, help='CPU threshold percentage')
@click.option('--duration', '-d', default=60, help='Monitoring duration in seconds')
def cpu(threshold, duration):
    """Monitor CPU usage with threshold alerts."""
    system_monitor = SystemMonitor()
    
    print_info(f"Monitoring CPU usage (threshold: {threshold}%) for {duration} seconds...")
    
    start_time = time.time()
    alerts_triggered = 0
    
    try:
        while time.time() - start_time < duration:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > threshold:
                alerts_triggered += 1
                print_warning(f"CPU usage high: {cpu_percent}% (threshold: {threshold}%)")
            else:
                print_info(f"CPU usage: {cpu_percent}%")
            
            time.sleep(1)
        
        print_success(f"Monitoring completed. Alerts triggered: {alerts_triggered}")
        
    except KeyboardInterrupt:
        print_success("CPU monitoring stopped.")

@monitor.command()
@click.option('--threshold', '-t', default=90, help='Memory threshold percentage')
@click.option('--duration', '-d', default=60, help='Monitoring duration in seconds')
def memory(threshold, duration):
    """Monitor memory usage with threshold alerts."""
    system_monitor = SystemMonitor()
    
    print_info(f"Monitoring memory usage (threshold: {threshold}%) for {duration} seconds...")
    
    start_time = time.time()
    alerts_triggered = 0
    
    try:
        while time.time() - start_time < duration:
            memory = psutil.virtual_memory()
            
            if memory.percent > threshold:
                alerts_triggered += 1
                print_warning(f"Memory usage high: {memory.percent}% (threshold: {threshold}%)")
            else:
                print_info(f"Memory usage: {memory.percent}% ({format_bytes(memory.used)}/{format_bytes(memory.total)})")
            
            time.sleep(2)
        
        print_success(f"Monitoring completed. Alerts triggered: {alerts_triggered}")
        
    except KeyboardInterrupt:
        print_success("Memory monitoring stopped.")

@monitor.command()
@click.option('--path', '-p', default='/', help='Path to monitor')
@click.option('--threshold', '-t', default=90, help='Disk threshold percentage')
def disk(path, threshold):
    """Monitor disk usage."""
    try:
        disk_usage = psutil.disk_usage(path)
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        table = Table(title=f"Disk Usage: {path}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total", format_bytes(disk_usage.total))
        table.add_row("Used", format_bytes(disk_usage.used))
        table.add_row("Free", format_bytes(disk_usage.free))
        table.add_row("Usage", f"{usage_percent:.1f}%")
        
        console.print(table)
        
        if usage_percent > threshold:
            print_warning(f"Disk usage is above threshold: {usage_percent:.1f}% > {threshold}%")
        else:
            print_success(f"Disk usage is within threshold: {usage_percent:.1f}% <= {threshold}%")
            
    except Exception as e:
        print_error(f"Error monitoring disk: {e}")

@monitor.command()
def processes():
    """Show running processes."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        table = Table(title="Top Processes by CPU Usage")
        table.add_column("PID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("CPU %", style="yellow")
        table.add_column("Memory %", style="green")
        
        for proc in processes[:20]:  # Show top 20
            table.add_row(
                str(proc['pid']),
                proc['name'] or 'N/A',
                f"{proc['cpu_percent'] or 0:.1f}",
                f"{proc['memory_percent'] or 0:.1f}"
            )
        
        console.print(table)
        
    except Exception as e:
        print_error(f"Error listing processes: {e}")
