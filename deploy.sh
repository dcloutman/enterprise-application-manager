#!/bin/bash
set -e

echo "🚀 Starting App Tracker deployment..."

# Initialize Docker Swarm if not already initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "Initializing Docker Swarm..."
    docker swarm init
fi

# Build and deploy the stack
echo "Building and deploying services..."
docker stack deploy -c docker-compose.yml app-tracker

echo "✅ Deployment complete!"
echo ""
echo "Services starting up..."
echo "- Frontend will be available at: http://localhost"
echo "- Backend API will be available at: http://localhost/api/"  
echo "- Django Admin will be available at: http://localhost/admin/"
echo "- MySQL will be available at: localhost:3306"
echo ""
echo "To check service status:"
echo "  docker service ls"
echo ""
echo "To view logs:"
echo "  docker service logs app-tracker_app"
echo "  docker service logs app-tracker_nginx"
echo "  docker service logs app-tracker_db"
