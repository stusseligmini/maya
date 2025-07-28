#!/usr/bin/env python3
"""
Maya AI Content System Entry Point

This script provides a convenient way to run the Maya system
with different configurations and modes.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_api_server(host='0.0.0.0', port=8000, reload=False):
    """Run the FastAPI server."""
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'maya.api.app:app',
        '--host', host,
        '--port', str(port)
    ]
    
    if reload:
        cmd.append('--reload')
    
    print(f"Starting Maya API server on {host}:{port}")
    subprocess.run(cmd)

def run_cli():
    """Run the Maya CLI."""
    from maya.cli import main
    main()

def run_tests(pattern=None, coverage=False):
    """Run tests with optional coverage."""
    cmd = [sys.executable, '-m', 'pytest']
    
    if pattern:
        cmd.extend(['-k', pattern])
    
    if coverage:
        cmd.extend(['--cov=maya', '--cov-report=html', '--cov-report=term'])
    
    print("Running Maya tests...")
    subprocess.run(cmd)

def setup_environment():
    """Set up the development environment."""
    print("Setting up Maya development environment...")
    
    # Create .env file if it doesn't exist
    env_file = project_root / '.env'
    env_example = project_root / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print("Please edit .env file with your configuration")
    
    # Create necessary directories
    dirs = ['logs', 'models/cache']
    for dir_path in dirs:
        (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    print("Environment setup complete!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Maya AI Content System')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # API server command
    api_parser = subparsers.add_parser('api', help='Run API server')
    api_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    api_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    api_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    # CLI command
    cli_parser = subparsers.add_parser('cli', help='Run Maya CLI')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--pattern', help='Test pattern to match')
    test_parser.add_argument('--coverage', action='store_true', help='Enable coverage reporting')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up development environment')
    
    args = parser.parse_args()
    
    if args.command == 'api':
        run_api_server(args.host, args.port, args.reload)
    elif args.command == 'cli':
        run_cli()
    elif args.command == 'test':
        run_tests(args.pattern, args.coverage)
    elif args.command == 'setup':
        setup_environment()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()