#!/bin/bash
set -e

echo "📦 Installing App Tracker with pipx..."

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "Error: pipx is not installed. Please install pipx first:"
    echo "  python3 -m pip install --user pipx"
    echo "  python3 -m pipx ensurepath"
    exit 1
fi

# Install the backend with pipx
echo "Installing backend with pipx..."
pipx install -e ./backend

echo "✅ App Tracker installed with pipx!"
echo ""
echo "To run the application:"
echo "  app-tracker"
echo ""
echo "The server will start on http://localhost:8000"
echo "Note: You'll need to set up the database and run migrations first:"
echo "  cd backend && python manage.py migrate"
echo "  cd backend && python manage.py createsuperuser"
