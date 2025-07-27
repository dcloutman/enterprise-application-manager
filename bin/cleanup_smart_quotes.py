#!/usr/bin/env python3

"""
Smart Quote Cleanup Script
Removes smart quotes and other Unicode characters from documentation files
Uses only standard Python - no external dependencies
"""

import os
import sys
import glob
import shutil
from datetime import datetime

def cleanup_smart_quotes(file_path):
    """Clean smart quotes and Unicode characters from a single file."""
    print(f"  Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Smart quote replacements
        replacements = {
            # Left and right double quotes
            '\u201c': '"',  # "
            '\u201d': '"',  # "
            # Left and right single quotes
            '\u2018': "'",  # '
            '\u2019': "'",  # '
            # Other quote variants
            '\u201a': ',',  # ‚
            '\u201e': '"',  # „
            '\u2039': '<',  # ‹
            '\u203a': '>',  # ›
            # Em and en dashes
            '\u2014': '--', # —
            '\u2013': '-',  # –
            # Ellipsis
            '\u2026': '...' # …
        }
        
        # Apply replacements
        original_content = content
        for unicode_char, replacement in replacements.items():
            content = content.replace(unicode_char, replacement)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    ✓ Fixed smart quotes in {os.path.basename(file_path)}")
        else:
            print(f"    - No changes needed in {os.path.basename(file_path)}")
            
    except Exception as e:
        print(f"    ✗ Error processing {file_path}: {e}")
        return False
    
    return True

def main():
    """Main cleanup function."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(project_root, 'docs')
    
    print("🔧 Starting smart quote cleanup with Python...")
    print(f"Project root: {project_root}")
    print(f"Documentation directory: {docs_dir}")
    
    if not os.path.exists(docs_dir):
        print(f"❌ Documentation directory not found: {docs_dir}")
        sys.exit(1)
    
    # Create backup
    backup_dir = os.path.join(project_root, 'tmp', f'docs_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Creating backup in: {backup_dir}")
    shutil.copytree(docs_dir, os.path.join(backup_dir, 'docs'))
    
    # Find all RST files
    rst_pattern = os.path.join(docs_dir, '**', '*.rst')
    rst_files = glob.glob(rst_pattern, recursive=True)
    
    if not rst_files:
        print("❌ No RST files found")
        sys.exit(1)
    
    print(f"Found {len(rst_files)} RST files to process...")
    
    # Process each file
    success_count = 0
    for rst_file in sorted(rst_files):
        if cleanup_smart_quotes(rst_file):
            success_count += 1
    
    print(f"\n✅ Processed {success_count}/{len(rst_files)} files successfully")
    print(f"Backup created at: {backup_dir}")
    
    # Verify cleanup
    print("\nVerifying cleanup...")
    remaining_issues = []
    
    for rst_file in rst_files:
        try:
            with open(rst_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for remaining smart quotes
            smart_quotes = ['\u201c', '\u201d', '\u2018', '\u2019']
            for quote in smart_quotes:
                if quote in content:
                    remaining_issues.append(rst_file)
                    break
        except Exception as e:
            print(f"Error checking {rst_file}: {e}")
    
    if remaining_issues:
        print("⚠️  WARNING: Smart quotes still found in:")
        for file_path in remaining_issues:
            print(f"  {file_path}")
    else:
        print("✅ No smart quotes found - cleanup complete!")
    
    print("\nRun 'sphinx-build -b html docs docs/_build/html' to verify documentation builds correctly.")

if __name__ == '__main__':
    main()
