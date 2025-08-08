"""
Service management core functionality.
"""

import redis
import socket
import subprocess
from typing import Dict, List, Optional, Tuple

class RedisManager:
    """Manages Redis connections and operations."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 password: Optional[str] = None, db: int = 0):
        """Initialize Redis manager."""
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish Redis connection."""
        try:
            self.client = redis.StrictRedis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True,
                socket_timeout=5
            )
        except Exception as e:
            raise Exception(f"Failed to create Redis client: {e}")
    
    def test_connection(self) -> bool:
        """Test Redis connection."""
        try:
            return self.client.ping()
        except Exception:
            return False
    
    def get_server_info(self) -> Optional[Dict]:
        """Get Redis server information."""
        try:
            return self.client.info()
        except Exception:
            return None
    
    def get_total_keys(self) -> int:
        """Get total number of keys in current database."""
        try:
            info = self.client.info('keyspace')
            db_key = f'db{self.db}'
            if db_key in info:
                # Parse "keys=X,expires=Y,avg_ttl=Z"
                keys_info = info[db_key]
                keys_count = int(keys_info.split(',')[0].split('=')[1])
                return keys_count
            return 0
        except Exception:
            return 0
    
    def get_keys(self, pattern: str = '*', limit: int = 100) -> List[str]:
        """Get keys matching pattern."""
        try:
            keys = []
            for key in self.client.scan_iter(match=pattern, count=limit):
                keys.append(key)
                if len(keys) >= limit:
                    break
            return keys
        except Exception:
            return []
    
    def get_key_type(self, key: str) -> str:
        """Get type of a key."""
        try:
            return self.client.type(key)
        except Exception:
            return 'unknown'
    
    def get_key_ttl(self, key: str) -> int:
        """Get TTL of a key."""
        try:
            return self.client.ttl(key)
        except Exception:
            return -2
    
    def set_key(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair."""
        try:
            if ttl:
                return self.client.setex(key, ttl, value)
            else:
                return self.client.set(key, value)
        except Exception:
            return False
    
    def get_key(self, key: str) -> Optional[str]:
        """Get value of a key."""
        try:
            return self.client.get(key)
        except Exception:
            return None
    
    def delete_key(self, key: str) -> bool:
        """Delete a key."""
        try:
            return bool(self.client.delete(key))
        except Exception:
            return False
    
    def flush_db(self) -> bool:
        """Flush current database."""
        try:
            return self.client.flushdb()
        except Exception:
            return False
    
    def get_memory_usage(self, key: str) -> Optional[int]:
        """Get memory usage of a key."""
        try:
            return self.client.memory_usage(key)
        except Exception:
            return None

class ServiceHealthChecker:
    """Check health of various services."""
    
    def __init__(self):
        """Initialize health checker."""
        self.default_ports = {
            'redis': 6379,
            'postgresql': 5432,
            'mysql': 3306,
            'mongodb': 27017,
            'elasticsearch': 9200,
            'rabbitmq': 5672,
            'memcached': 11211
        }
    
    def check_service(self, service_name: str, host: str = 'localhost', 
                     port: Optional[int] = None) -> Tuple[str, str]:
        """
        Check if a service is healthy.
        
        Returns:
            Tuple of (status, details) where status is 'healthy' or 'unhealthy'
        """
        if port is None:
            port = self.default_ports.get(service_name.lower())
            if port is None:
                return 'unhealthy', 'Unknown service or port not specified'
        
        # Check if port is open
        if not self._check_port(host, port):
            return 'unhealthy', f'Port {port} is not accessible'
        
        # Service-specific health checks
        if service_name.lower() == 'redis':
            return self._check_redis_health(host, port)
        elif service_name.lower() in ['postgresql', 'postgres']:
            return self._check_postgresql_health(host, port)
        elif service_name.lower() == 'mysql':
            return self._check_mysql_health(host, port)
        elif service_name.lower() == 'mongodb':
            return self._check_mongodb_health(host, port)
        else:
            return 'healthy', f'Port {port} is accessible'
    
    def _check_port(self, host: str, port: int, timeout: int = 5) -> bool:
        """Check if a port is open."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, socket.error):
            return False
    
    def _check_redis_health(self, host: str, port: int) -> Tuple[str, str]:
        """Check Redis health."""
        try:
            redis_client = redis.StrictRedis(host=host, port=port, socket_timeout=5)
            if redis_client.ping():
                info = redis_client.info()
                version = info.get('redis_version', 'unknown')
                return 'healthy', f'Redis {version} responding'
            else:
                return 'unhealthy', 'Redis not responding to ping'
        except Exception as e:
            return 'unhealthy', f'Redis error: {str(e)}'
    
    def _check_postgresql_health(self, host: str, port: int) -> Tuple[str, str]:
        """Check PostgreSQL health."""
        try:
            # Try to import psycopg2
            import psycopg2
            conn = psycopg2.connect(
                host=host,
                port=port,
                user='postgres',  # Default user
                connect_timeout=5
            )
            conn.close()
            return 'healthy', 'PostgreSQL accepting connections'
        except ImportError:
            return 'healthy', 'Port accessible (psycopg2 not installed for detailed check)'
        except Exception as e:
            return 'unhealthy', f'PostgreSQL error: {str(e)}'
    
    def _check_mysql_health(self, host: str, port: int) -> Tuple[str, str]:
        """Check MySQL health."""
        try:
            # Try to import mysql connector
            import mysql.connector
            conn = mysql.connector.connect(
                host=host,
                port=port,
                connection_timeout=5
            )
            conn.close()
            return 'healthy', 'MySQL accepting connections'
        except ImportError:
            return 'healthy', 'Port accessible (mysql-connector not installed for detailed check)'
        except Exception as e:
            return 'unhealthy', f'MySQL error: {str(e)}'
    
    def _check_mongodb_health(self, host: str, port: int) -> Tuple[str, str]:
        """Check MongoDB health."""
        try:
            # Try to import pymongo
            import pymongo
            client = pymongo.MongoClient(host, port, serverSelectionTimeoutMS=5000)
            client.server_info()  # Force connection
            return 'healthy', 'MongoDB accepting connections'
        except ImportError:
            return 'healthy', 'Port accessible (pymongo not installed for detailed check)'
        except Exception as e:
            return 'unhealthy', f'MongoDB error: {str(e)}'
    
    def check_multiple_services(self, services: List[str], host: str = 'localhost') -> Dict[str, Tuple[str, str]]:
        """Check multiple services at once."""
        results = {}
        for service in services:
            results[service] = self.check_service(service, host)
        return results
