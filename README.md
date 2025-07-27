# App Tracker

A full-stack web application with Django backend and SvelteKit frontend, designed for deployment with pipx and containerized with Docker Swarm.

## Architecture

- **Backend**: Django with Gunicorn WSGI server
- **Frontend**: SvelteKit (TypeScript)
- **Database**: MySQL
- **Reverse Proxy**: Nginx
- **Container Orchestration**: Docker Swarm

## Quick Start

### 1. Development Setup

Run the development setup script to configure the entire project:

```bash
./setup-dev.sh
```

This will:
- Start a MySQL container for development
- Create Python virtual environment
- Install Django dependencies
- Install Node.js dependencies  
- Run Django migrations
- Create a superuser (admin/admin123)

The MySQL container will be accessible at `localhost:3306` with:
- Database: `app_tracker`
- User: `appuser` 
- Password: `apppassword`

### 2. Development with Docker Swarm

For a production-like environment:

```bash
# Deploy the full stack
./deploy.sh

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost/api/
# Django Admin: http://localhost/admin/
```

### 3. Local Development Servers

**Backend (Django):**
```bash
source .venv/bin/activate
cd backend && python manage.py runserver
# Runs on http://localhost:8000
```

**Frontend (SvelteKit):**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

## Deployment Options

### Option 1: pipx Deployment

Install and run with pipx for isolated Python deployment:

```bash
./install-pipx.sh
# Then run: app-tracker
```

### Option 2: Docker Swarm (Recommended)

For production deployment:

```bash
# Initialize swarm (if not done)
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml app-tracker
```

### Option 3: Manual Installation

```bash
# Backend
cd backend
pip install -e .
python manage.py migrate
python manage.py runserver

# Frontend  
cd frontend
npm install
npm run build
```

## Project Structure

```
app-tracker/
├── backend/                 # Django backend
│   ├── app_tracker/        # Main Django project
│   │   ├── core/          # Core app (models, views, etc.)
│   │   ├── settings.py    # Django settings
│   │   └── wsgi.py        # WSGI configuration
│   ├── requirements.txt   # Python dependencies
│   └── pyproject.toml     # Project metadata for pipx
├── frontend/               # SvelteKit frontend
│   ├── src/               # Source code
│   │   ├── routes/        # SvelteKit routes
│   │   └── lib/           # Shared components/utilities
│   ├── package.json       # Node.js dependencies
│   └── svelte.config.js   # SvelteKit configuration
├── docker/                 # Docker configuration
│   ├── Dockerfile         # Multi-stage build
│   ├── entrypoint.sh      # Container startup script
│   └── nginx/             # Nginx configuration
├── docker-compose.yml      # Docker Swarm configuration
└── *.sh                   # Deployment and setup scripts
```

## Services

### Application Container
- **Image**: Custom multi-stage build
- **Ports**: 8000 (Django), 3000 (SvelteKit)
- **Features**: Python 3.11, Node.js 18, MySQL client

### Database Container  
- **Image**: MySQL 8.0
- **Port**: 3306
- **Data**: Persisted in Docker volume

### Nginx Container
- **Image**: nginx:alpine with Python/Node
- **Ports**: 80, 443
- **Features**: Reverse proxy, static file serving, load balancing

## API Endpoints

- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `PATCH /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

## Development Commands

Use VS Code tasks or run manually:

```bash
# VS Code Tasks (Ctrl+Shift+P > "Tasks: Run Task")
- Setup Development Environment    # Starts MySQL + full setup
- Start Django Server
- Start SvelteKit Dev Server  
- Install Backend Dependencies
- Install Frontend Dependencies
- Django Migrate
- Start MySQL Dev Container       # Just the MySQL container
- Stop MySQL Dev Container        # Stop development MySQL
- Cleanup Development Environment # Remove dev MySQL container
- Deploy Docker Swarm
- Cleanup Docker Swarm

# Manual commands
source .venv/bin/activate && cd backend && python manage.py runserver    # Django
cd frontend && npm run dev                                               # SvelteKit  
./deploy.sh                                                             # Docker Swarm
./cleanup.sh                                                           # Remove containers
./cleanup-dev.sh                                                       # Remove dev MySQL
```

## Environment Variables

Copy `.env.example` to `.env` in the backend directory:

```bash
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=mysql://appuser:apppassword@localhost:3306/app_tracker
ALLOWED_HOSTS=localhost,127.0.0.1,app
```

## Default Credentials

- **Django Admin**: admin / admin123
- **MySQL**: appuser / apppassword

## Monitoring

```bash
# Check service status
docker service ls

# View logs
docker service logs app-tracker_app
docker service logs app-tracker_nginx  
docker service logs app-tracker_db

# Scale services
docker service scale app-tracker_app=3
```
