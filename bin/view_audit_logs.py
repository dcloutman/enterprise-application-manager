#!/usr/bin/env python3
"""
Audit Log Viewer for Enterprise Application Tracker

This script demonstrates how to read and parse the audit log files.
The logs are designed to be both human-readable and script-parseable.

Usage:
    python view_audit_logs.py [--json-only] [--user USERNAME] [--action ACTION] [--model MODEL] [--since DATETIME]
"""

import json
import argparse
import sys
from datetime import datetime
import os


def parse_log_entry(line):
    """Parse a single audit log entry"""
    try:
        # Extract JSON from the end of the line
        json_start = line.rfind('| JSON: ')
        if json_start == -1:
            return None
        
        json_str = line[json_start + 8:].strip()  # Remove '| JSON: ' prefix
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        return None


def filter_entry(entry, filters):
    """Check if entry matches the provided filters"""
    if not entry:
        return False
    
    # User filter
    if filters.get('user') and entry.get('user', '').lower() != filters['user'].lower():
        return False
    
    # Action filter
    if filters.get('action') and entry.get('action', '').lower() != filters['action'].lower():
        return False
    
    # Model filter
    if filters.get('model') and filters['model'].lower() not in entry.get('model', '').lower():
        return False
    
    # Since filter (timestamp)
    if filters.get('since'):
        try:
            entry_time = datetime.strptime(entry.get('timestamp', ''), '%Y-%m-%d %H:%M:%S')
            if entry_time < filters['since']:
                return False
        except ValueError:
            pass
    
    return True


def format_entry_human(entry):
    """Format entry for human reading"""
    timestamp = entry.get('timestamp', 'Unknown')
    action = entry.get('action', 'Unknown')
    model = entry.get('model', 'Unknown')
    object_id = entry.get('object_id', 'Unknown')
    user = entry.get('user', 'Unknown')
    object_str = entry.get('object_str', 'Unknown')
    
    result = f"[{timestamp}] {action} {model}#{object_id} by {user}: {object_str}"
    
    # Add changes for UPDATE operations
    if action == 'UPDATE' and entry.get('changes'):
        changes_list = []
        for field, change in entry['changes'].items():
            old_val = change.get('old', 'None')
            new_val = change.get('new', 'None')
            changes_list.append(f"{field}: {old_val} -> {new_val}")
        if changes_list:
            result += f"\n    Changes: {'; '.join(changes_list)}"
    
    # Add additional info if present
    if entry.get('additional_info'):
        info_list = []
        for key, value in entry['additional_info'].items():
            info_list.append(f"{key}: {value}")
        if info_list:
            result += f"\n    Info: {'; '.join(info_list)}"
    
    return result


def main():
    parser = argparse.ArgumentParser(description='View and filter audit logs')
    parser.add_argument('--log-file', 
                       help='Path to audit log file (default: ./logs/audit.log)')
    parser.add_argument('--json-only', action='store_true',
                       help='Output only JSON data for script processing')
    parser.add_argument('--user', 
                       help='Filter by username')
    parser.add_argument('--action', 
                       help='Filter by action (CREATE, UPDATE, DELETE)')
    parser.add_argument('--model', 
                       help='Filter by model name (partial match)')
    parser.add_argument('--since', 
                       help='Show entries since date/time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--tail', type=int, default=0,
                       help='Show last N entries (default: all)')
    
    args = parser.parse_args()
    
    # Determine log file path
    if args.log_file:
        log_file = args.log_file
    else:
        # Try common locations
        possible_paths = [
            './logs/audit.log',
            '/var/log/app-tracker/audit.log',
            '../logs/audit.log'
        ]
        log_file = None
        for path in possible_paths:
            if os.path.exists(path):
                log_file = path
                break
        
        if not log_file:
            print("Error: Could not find audit.log file. Please specify path with --log-file")
            print(f"Searched: {', '.join(possible_paths)}")
            sys.exit(1)
    
    # Build filters
    filters = {}
    if args.user:
        filters['user'] = args.user
    if args.action:
        filters['action'] = args.action.upper()
    if args.model:
        filters['model'] = args.model
    if args.since:
        try:
            filters['since'] = datetime.strptime(args.since, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print("Error: --since must be in format 'YYYY-MM-DD HH:MM:SS'")
            sys.exit(1)
    
    # Read and process log file
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            print("Audit log file is empty")
            return
        
        # Apply tail filter
        if args.tail > 0:
            lines = lines[-args.tail:]
        
        matching_entries = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            entry = parse_log_entry(line)
            if entry and filter_entry(entry, filters):
                matching_entries.append((line, entry))
        
        if not matching_entries:
            print("No matching audit log entries found")
            return
        
        print(f"Found {len(matching_entries)} matching audit log entries")
        print("=" * 80)
        
        for line, entry in matching_entries:
            if args.json_only:
                print(json.dumps(entry, indent=2))
            else:
                print(format_entry_human(entry))
            print("-" * 80)
    
    except FileNotFoundError:
        print(f"Error: Could not find audit log file: {log_file}")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading audit log file: {log_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading audit log: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
