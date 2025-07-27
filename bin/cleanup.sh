#!/bin/bash
set -e

echo "🧹 Cleaning up App Tracker services..."

# Remove the stack
docker stack rm app-tracker

echo "Waiting for services to stop..."
sleep 10

# Remove unused volumes (optional - uncomment if needed)
# docker volume prune -f

echo "✅ Cleanup complete!"
