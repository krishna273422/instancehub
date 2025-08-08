"""
Test CLI functionality.
"""

import pytest
from click.testing import CliRunner
from instancehub.cli import main

def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'InstanceHub' in result.output

def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert '1.0.0' in result.output

def test_cli_info():
    """Test CLI info command."""
    runner = CliRunner()
    result = runner.invoke(main, ['info'])
    assert result.exit_code == 0
    assert 'InstanceHub Information' in result.output

def test_instances_help():
    """Test instances command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['instances', '--help'])
    assert result.exit_code == 0
    assert 'Manage AWS EC2 instances' in result.output

def test_monitor_help():
    """Test monitor command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['monitor', '--help'])
    assert result.exit_code == 0
    assert 'System monitoring' in result.output

def test_services_help():
    """Test services command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['services', '--help'])
    assert result.exit_code == 0
    assert 'Manage services' in result.output

def test_config_help():
    """Test config command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['config', '--help'])
    assert result.exit_code == 0
    assert 'Configuration management' in result.output
