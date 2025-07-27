#!/bin/bash
set -e

echo "🧹 Cleaning up development environment..."

# Stop and remove development MySQL container
if docker ps -a | grep -q "app-tracker-mysql-dev"; then
    echo "Stopping and removing MySQL development container..."
    docker stop app-tracker-mysql-dev || true
    docker rm app-tracker-mysql-dev || true
fi

echo "✅ Development cleanup complete!"
