"""
Configuration management functionality.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional, Any

class ConfigManager:
    """Manages InstanceHub configuration."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager."""
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use user's home directory
            self.config_dir = Path.home() / '.instancehub'
        
        self.config_path = self.config_dir / 'config.yaml'
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    def config_exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_path.exists()
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        if not self.config_exists():
            return None
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load configuration: {e}")
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save configuration: {e}")
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        config = self.load_config()
        if not config:
            return default
        
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set_value(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        config = self.load_config() or {}
        
        keys = key.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        self.save_config(config)
    
    def get_aws_config(self) -> Dict[str, Any]:
        """Get AWS configuration."""
        return self.get_value('aws', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.get_value('monitoring', {
            'cpu_threshold': 90,
            'memory_threshold': 90,
            'disk_threshold': 90,
            'refresh_interval': 2
        })
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return self.get_value('redis', {
            'default_host': 'localhost',
            'default_port': 6379,
            'default_db': 0
        })
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self.get_value('output', {
            'color': True,
            'verbose': False,
            'format': 'table'
        })
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
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
            },
            'services': {
                'health_check_timeout': 5,
                'default_ports': {
                    'redis': 6379,
                    'postgresql': 5432,
                    'mysql': 3306,
                    'mongodb': 27017
                }
            }
        }
    
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        default_config = self.create_default_config()
        self.save_config(default_config)
    
    def backup_config(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the current configuration."""
        if not self.config_exists():
            raise Exception("No configuration file to backup")
        
        if backup_path is None:
            backup_path = str(self.config_path) + '.backup'
        
        import shutil
        shutil.copy2(self.config_path, backup_path)
        return backup_path
    
    def restore_config(self, backup_path: str) -> None:
        """Restore configuration from backup."""
        if not os.path.exists(backup_path):
            raise Exception(f"Backup file not found: {backup_path}")
        
        import shutil
        shutil.copy2(backup_path, self.config_path)
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, errors)."""
        config = self.load_config()
        if not config:
            return False, ["No configuration found"]
        
        errors = []
        
        # Validate AWS configuration
        aws_config = config.get('aws', {})
        if not aws_config.get('default_region'):
            errors.append("Missing aws.default_region")
        
        # Validate monitoring thresholds
        monitoring_config = config.get('monitoring', {})
        for threshold in ['cpu_threshold', 'memory_threshold', 'disk_threshold']:
            value = monitoring_config.get(threshold)
            if value is not None:
                if not isinstance(value, (int, float)) or value < 0 or value > 100:
                    errors.append(f"Invalid {threshold}: must be between 0 and 100")
        
        # Validate Redis configuration
        redis_config = config.get('redis', {})
        port = redis_config.get('default_port')
        if port is not None:
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append("Invalid redis.default_port: must be between 1 and 65535")
        
        return len(errors) == 0, errors
