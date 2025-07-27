#!/bin/bash
set -e

echo "Starting App Tracker services..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 3306; do
  sleep 0.1
done
echo "Database is ready!"

# Collect static files
cd /app/backend
python3.12 manage.py collectstatic --noinput

# Create superuser if it doesn't exist
python3.12 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
"

# Start Gunicorn in the background
echo "Starting Gunicorn..."
python3.12 -m gunicorn --bind 0.0.0.0:8000 --workers 3 app_tracker.wsgi:application &

# Start SvelteKit dev server with hot reload
echo "Starting SvelteKit dev server..."
cd /app/frontend
. "$NVM_DIR/nvm.sh" && npm run dev -- --host 0.0.0.0 --port 3000 &

# Keep the container running
wait
