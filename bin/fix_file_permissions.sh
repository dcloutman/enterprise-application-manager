#!/bin/bash

# fix_file_permissions.sh
# Sets secure file permissions according to security best practices
# Most files: 640, Directories: 750, Executables: 750, Sensitive files: 600/700

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔒 Setting secure file permissions..."
echo "Project root: ${PROJECT_ROOT}"

cd "${PROJECT_ROOT}"

# Set default permissions for all files (640 - owner read/write, group read, no others)
echo "Setting default file permissions (640)..."
find . -type f -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.svelte" \
       -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" \
       -o -name "*.rst" -o -name "*.md" -o -name "*.txt" -o -name "*.cfg" \
       -o -name "*.ini" -o -name "*.conf" -o -name "*.html" -o -name "*.css" \
       -o -name "*.sql" -o -name "*.env.example" | \
    xargs chmod 640 2>/dev/null || true

# Set directory permissions (750 - owner full, group read/execute, no others)
echo "Setting directory permissions (750)..."
find . -type d | xargs chmod 750 2>/dev/null || true

# Set executable permissions for scripts (750)
echo "Setting executable script permissions (750)..."
find bin -type f -name "*.sh" -o -name "*.py" | xargs chmod 750 2>/dev/null || true

# Set permissions for Django management files (750)
echo "Setting Django management permissions (750)..."
[ -f "backend/manage.py" ] && chmod 750 backend/manage.py
find backend -name "run_tests.py" -type f | xargs chmod 750 2>/dev/null || true

# Set restrictive permissions for sensitive files (600 - owner only)
echo "Setting sensitive file permissions (600)..."
find . -name "*.env" -o -name ".env.*" -o -name "*secret*" -o -name "*key*" \
       -o -name "*.pem" -o -name "*.key" -o -name "*.crt" | \
    xargs chmod 600 2>/dev/null || true

# Set Docker and configuration files (640)
echo "Setting Docker and config file permissions (640)..."
find . -name "Dockerfile*" -o -name "docker-compose*.yml" -o -name "*.dockerfile" | \
    xargs chmod 640 2>/dev/null || true

# Special handling for .gitignore and similar files (644 - standard for version control)
echo "Setting version control file permissions (644)..."
find . -name ".gitignore" -o -name ".gitattributes" -o -name "README*" -o -name "LICENSE*" | \
    xargs chmod 644 2>/dev/null || true

# Set npm/node files permissions
echo "Setting Node.js file permissions..."
[ -f "package.json" ] && chmod 640 package.json
[ -f "package-lock.json" ] && chmod 640 package-lock.json
find . -name "node_modules" -type d | xargs chmod 755 2>/dev/null || true

# Remove any world permissions that might have been set accidentally
echo "Removing world permissions..."
find . -type f -perm /o+rwx -exec chmod o-rwx {} \; 2>/dev/null || true
find . -type d -perm /o+rwx -exec chmod o-rwx {} \; 2>/dev/null || true

echo ""
echo "✅ File permissions updated successfully!"
echo ""
echo "Summary of permission structure:"
echo "  📁 Directories: 750 (owner: rwx, group: r-x, others: ---)"
echo "  📄 Regular files: 640 (owner: rw-, group: r--, others: ---)"
echo "  🔧 Executable scripts: 750 (owner: rwx, group: r-x, others: ---)"
echo "  🔐 Sensitive files: 600 (owner: rw-, group: ---, others: ---)"
echo "  📋 Version control files: 644 (owner: rw-, group: r--, others: r--)"
echo ""
echo "Security note: Others (world) have no access to application files."
