"""
System monitoring core functionality.
"""

import psutil
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SystemStats:
    """System statistics data class."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    uptime: float
    processes: int

class SystemMonitor:
    """System monitoring and alerting."""
    
    def __init__(self):
        """Initialize system monitor."""
        self.alerts = []
        self.thresholds = {
            'cpu': 90,
            'memory': 90,
            'disk': 90
        }
    
    def get_system_stats(self) -> SystemStats:
        """Get current system statistics."""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk (root partition)
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Network
        net_io = psutil.net_io_counters()
        network_sent = net_io.bytes_sent
        network_recv = net_io.bytes_recv
        
        # System
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        processes = len(psutil.pids())
        
        return SystemStats(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_sent=network_sent,
            network_recv=network_recv,
            uptime=uptime,
            processes=processes
        )
    
    def check_thresholds(self, stats: SystemStats) -> List[str]:
        """Check if any thresholds are exceeded."""
        alerts = []
        
        if stats.cpu_percent > self.thresholds['cpu']:
            alerts.append(f"CPU usage high: {stats.cpu_percent}%")
        
        if stats.memory_percent > self.thresholds['memory']:
            alerts.append(f"Memory usage high: {stats.memory_percent}%")
        
        if stats.disk_percent > self.thresholds['disk']:
            alerts.append(f"Disk usage high: {stats.disk_percent}%")
        
        return alerts
    
    def set_threshold(self, metric: str, value: float):
        """Set threshold for a metric."""
        if metric in self.thresholds:
            self.thresholds[metric] = value
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def get_cpu_info(self) -> Dict:
        """Get detailed CPU information."""
        cpu_freq = psutil.cpu_freq()
        cpu_times = psutil.cpu_times()
        
        return {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'current_freq': cpu_freq.current if cpu_freq else None,
            'min_freq': cpu_freq.min if cpu_freq else None,
            'max_freq': cpu_freq.max if cpu_freq else None,
            'user_time': cpu_times.user,
            'system_time': cpu_times.system,
            'idle_time': cpu_times.idle
        }
    
    def get_memory_info(self) -> Dict:
        """Get detailed memory information."""
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': virtual.total,
            'available': virtual.available,
            'used': virtual.used,
            'free': virtual.free,
            'percent': virtual.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self, path: str = '/') -> Dict:
        """Get detailed disk information."""
        disk_usage = psutil.disk_usage(path)
        
        return {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent': (disk_usage.used / disk_usage.total) * 100
        }
    
    def get_network_info(self) -> Dict:
        """Get network interface information."""
        net_io = psutil.net_io_counters()
        net_connections = len(psutil.net_connections())
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'connections': net_connections
        }
    
    def get_process_list(self, sort_by: str = 'cpu_percent', limit: int = 10) -> List[Dict]:
        """Get list of running processes."""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                proc_info = proc.info
                proc_info['cpu_percent'] = proc_info['cpu_percent'] or 0
                proc_info['memory_percent'] = proc_info['memory_percent'] or 0
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort processes
        if sort_by in ['cpu_percent', 'memory_percent']:
            processes.sort(key=lambda x: x[sort_by], reverse=True)
        
        return processes[:limit]
    
    def monitor_continuous(self, duration: int, interval: int = 1, 
                          callback: Optional[callable] = None):
        """Monitor system continuously for specified duration."""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            stats = self.get_system_stats()
            alerts = self.check_thresholds(stats)
            
            if callback:
                callback(stats, alerts)
            
            time.sleep(interval)
    
    def get_system_load(self) -> Optional[tuple]:
        """Get system load average (Unix-like systems only)."""
        try:
            return psutil.getloadavg()
        except AttributeError:
            # Not available on Windows
            return None
