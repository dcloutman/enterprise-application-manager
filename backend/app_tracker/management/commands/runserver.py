#!/usr/bin/env python
"""Main entry point for pipx deployment"""
import os
import sys
from django.core.management import execute_from_command_line


def main():
    """Run the Django development server"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_tracker.settings')
    
    # Run the Django development server
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:8000']
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
