#!/bin/bash

# cleanup_documentation.sh
# Script to remove smart quotes and emojis from documentation files
# Ensures all documentation uses standard US English keyboard characters only

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="${PROJECT_ROOT}/docs"

echo "🔧 Starting documentation cleanup..."
echo "Project root: ${PROJECT_ROOT}"
echo "Documentation directory: ${DOCS_DIR}"

# Backup original files
BACKUP_DIR="${PROJECT_ROOT}/tmp/docs_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${BACKUP_DIR}"
echo "Creating backup in: ${BACKUP_DIR}"
cp -r "${DOCS_DIR}" "${BACKUP_DIR}/"

# Function to clean a single file
cleanup_file() {
    local file="$1"
    echo "  Processing: ${file}"
    
    # Create temporary file
    local temp_file=$(mktemp)
    
    # Smart quote replacements - handle all variants
    # Left and right double quotes
    sed 's/"/"/g; s/"/"/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    # Left and right single quotes  
    sed "s/'/'/g; s/'/'/g" "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    # Additional quote variants
    sed 's/‚/,/g; s/„/"/g; s/‹/</g; s/›/>/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    # Handle any remaining Unicode quotes by converting to standard ASCII
    perl -pi -e 's/[\x{201C}\x{201D}]/"/g' "$file"
    perl -pi -e 's/[\x{2018}\x{2019}]/'"'"'/g' "$file"
    
    # Other unicode characters
    temp_file=$(mktemp)
    sed 's/…/.../g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/–/-/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/—/--/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    
    # Emoji replacements with descriptive text
    temp_file=$(mktemp)
    sed 's/🛡️/**[ADMIN]**/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/⚙️/**[SYSTEMS]**/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/📊/**[BUSINESS]**/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/✅/**[YES]** /g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/⚠️/**WARNING**/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/🚀/**DEPLOYMENT**/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/🎯/**TARGET**/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/🛠️/**TOOLS**/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
    temp_file=$(mktemp)
    sed 's/🔧/**CONFIG**/g' "$file" > "$temp_file" && mv "$temp_file" "$file"
}

# Process all RST files
echo "Processing RST files..."
find "${DOCS_DIR}" -name "*.rst" -type f | while read -r file; do
    cleanup_file "$file"
done

echo ""
echo "Cleanup completed!"
echo "Backup created at: ${BACKUP_DIR}"
echo ""
echo "Verifying changes..."

# Verify no smart quotes remain
echo "Checking for remaining smart quotes..."
SMART_QUOTES=$(find "${DOCS_DIR}" -name "*.rst" -exec grep -l '[""'']' {} \; 2>/dev/null || true)
if [ -n "$SMART_QUOTES" ]; then
    echo "⚠️  WARNING: Smart quotes still found in:"
    echo "$SMART_QUOTES"
else
    echo "✅ No smart quotes found"
fi

# Verify no emojis remain
echo ""
echo "Checking for remaining emojis..."
EMOJIS=$(find "${DOCS_DIR}" -name "*.rst" -exec grep -l '[📊🚀✅⚠️🎯🛠️🛡️⚙️🔧]' {} \; 2>/dev/null || true)
if [ -n "$EMOJIS" ]; then
    echo "⚠️  WARNING: Emojis still found in:"
    echo "$EMOJIS"
else
    echo "✅ No emojis found"
fi

echo ""
echo "Documentation cleanup complete!"
echo "Run 'sphinx-build -b html docs docs/_build/html' to verify documentation builds correctly."
