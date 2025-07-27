#!/bin/bash
set -e

echo "🛠️  Setting up App Tracker for local development..."

# Start MySQL container for development
echo "Starting MySQL container for development..."
if ! docker ps | grep -q "app-tracker-mysql-dev"; then
    echo "Starting MySQL development container..."
    docker run -d \
        --name app-tracker-mysql-dev \
        -e MYSQL_DATABASE=app_tracker \
        -e MYSQL_ROOT_PASSWORD=rootpassword \
        -e MYSQL_USER=appuser \
        -e MYSQL_PASSWORD=apppassword \
        -p 3307:3306 \
        mysql:8.4
    
    echo "Waiting for MySQL to be ready..."
    sleep 15
    
    # Wait for MySQL to be truly ready
    while ! docker exec app-tracker-mysql-dev mysqladmin ping -h localhost --silent; do
        echo "Waiting for MySQL to start..."
        sleep 2
    done
    
    echo "MySQL is ready!"
else
    echo "MySQL container already running"
    
    # Verify it's actually responsive
    if ! docker exec app-tracker-mysql-dev mysqladmin ping -h localhost --silent; then
        echo "MySQL container exists but not responsive, restarting..."
        docker restart app-tracker-mysql-dev
        sleep 10
        while ! docker exec app-tracker-mysql-dev mysqladmin ping -h localhost --silent; do
            echo "Waiting for MySQL to start..."
            sleep 2
        done
    fi
fi

# Setup backend
echo "Setting up Django backend..."

# Check if virtual environment exists at root level
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment at project root..."
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Copy environment file
if [ ! -f "backend/.env" ]; then
    echo "Creating .env file..."
    cp backend/.env.example backend/.env
fi

# Run Django setup
echo "Running Django migrations..."
cd backend
python manage.py migrate

echo "Creating Django superuser (skip if exists)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

cd ..

# Setup frontend
echo "Setting up SvelteKit frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

cd ..

echo "✅ Development setup complete!"
echo ""
echo "MySQL container is running on port 3307 (to avoid conflicts with system MySQL)"
echo "Database: app_tracker, User: appuser, Password: apppassword"
echo ""
echo "To start development servers:"
echo ""
echo "Backend (Django):"
echo "  source .venv/bin/activate"
echo "  cd backend && python manage.py runserver"
echo ""
echo "Frontend (SvelteKit):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Or use Docker Swarm for full deployment:"
echo "  ./deploy.sh"
echo ""
echo "Access points:"
echo "  Django Admin: http://localhost:8000/admin/ (admin/admin123)"
echo "  Frontend: http://localhost:3000"
echo ""
echo "To stop MySQL container when done:"
echo "  docker stop app-tracker-mysql-dev"
echo "  docker rm app-tracker-mysql-dev"
