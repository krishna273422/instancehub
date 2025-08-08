# InstanceHub 🚀

A powerful CLI tool for managing cloud instances, monitoring systems, and handling services. Built with Python and designed for developers and system administrators.

## Features

### 🌩️ Cloud Instance Management
- **AWS EC2 Support**: List, start, stop, restart instances
- **Real-time Status**: Get detailed instance information
- **Filtering**: Filter by state, tags, and regions
- **Batch Operations**: Manage multiple instances at once

### 📊 System Monitoring
- **Real-time Dashboard**: Beautiful terminal dashboard with live metrics
- **Resource Monitoring**: CPU, memory, disk, and network monitoring
- **Threshold Alerts**: Configurable alerts for resource usage
- **Process Management**: View and monitor running processes

### 🔧 Service Management
- **Redis Management**: Connect, monitor, and benchmark Redis instances
- **Health Checks**: Check health of various services (Redis, PostgreSQL, MySQL, MongoDB)
- **Connection Testing**: Test service connectivity and performance
- **Service Statistics**: Get detailed service metrics

### ⚙️ Configuration Management
- **YAML Configuration**: Easy-to-edit configuration files
- **Environment Support**: Multiple environment configurations
- **Validation**: Built-in configuration validation
- **Backup/Restore**: Configuration backup and restore functionality

## Installation

### From Source
```bash
git clone https://github.com/yourusername/instancehub.git
cd instancehub
pip install -e .
```

### Using pip (when published)
```bash
pip install instancehub
```

## Quick Start

1. **Initialize configuration**:
   ```bash
   instancehub config init
   ```

2. **List AWS instances**:
   ```bash
   instancehub instances list --region us-east-1
   ```

3. **Start monitoring dashboard**:
   ```bash
   instancehub monitor dashboard
   ```

4. **Check Redis status**:
   ```bash
   instancehub services redis status
   ```

## Usage Examples

### Instance Management
```bash
# List all instances
instancehub instances list

# List running instances in specific region
instancehub instances list --region us-west-2 --state running

# Start an instance
instancehub instances start i-1234567890abcdef0 --wait

# Stop an instance
instancehub instances stop i-1234567890abcdef0

# Get instance details
instancehub instances status i-1234567890abcdef0
```

### System Monitoring
```bash
# Real-time dashboard
instancehub monitor dashboard --refresh 1

# Monitor CPU with alerts
instancehub monitor cpu --threshold 80 --duration 300

# Monitor memory usage
instancehub monitor memory --threshold 85

# Check disk usage
instancehub monitor disk --path /var --threshold 90

# List top processes
instancehub monitor processes
```

### Service Management
```bash
# Check Redis status
instancehub services redis status --host localhost --port 6379

# Test Redis connection
instancehub services redis test

# List Redis keys
instancehub services redis keys --pattern "user:*" --limit 50

# Run Redis benchmark
instancehub services redis benchmark --clients 10 --requests 1000

# Health check multiple services
instancehub services health --service redis --service postgresql
```

### Configuration
```bash
# Show current configuration
instancehub config show

# Set a configuration value
instancehub config set aws.default_region us-west-2

# Get a configuration value
instancehub config get monitoring.cpu_threshold

# Edit configuration file
instancehub config edit

# Validate configuration
instancehub config validate
```

## Configuration

InstanceHub uses a YAML configuration file located at `~/.instancehub/config.yaml`. 

### Example Configuration
```yaml
aws:
  default_region: us-east-1
  profile: default

monitoring:
  cpu_threshold: 90
  memory_threshold: 90
  disk_threshold: 90
  refresh_interval: 2

redis:
  default_host: localhost
  default_port: 6379
  default_db: 0

output:
  color: true
  verbose: false
  format: table
```

## Requirements

- Python 3.8+
- AWS CLI configured (for AWS features)
- Redis server (for Redis features)

### Python Dependencies
- click >= 8.0.0
- boto3 >= 1.26.0
- psutil >= 5.9.0
- redis >= 4.5.0
- pyyaml >= 6.0
- rich >= 13.0.0

## Development

### Setup Development Environment
```bash
git clone https://github.com/yourusername/instancehub.git
cd instancehub
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
```bash
black instancehub/
flake8 instancehub/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI framework
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- AWS integration via [Boto3](https://boto3.amazonaws.com/)
- System monitoring with [psutil](https://psutil.readthedocs.io/)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/instancehub/issues) on GitHub.
