# Enterprise Application Tracker

An experimental application inventory system designed for tracking enterprise software application installations and their supporting infrastructure relationships in server-side environments. This project is in early development and serves as a proof-of-concept for centralized application tracking within enterprise server environments.

## Overview

The Enterprise Application Tracker is a web application built with Django and SvelteKit that provides tracking capabilities for business application installations on servers and their supporting infrastructure dependencies. The system focuses specifically on server-side application deployments and does not track physical hardware assets or client-side installations. The system implements role-based access control and provides a REST API for integration purposes.

### Current Features

- **Application Installation Tracking**: Track enterprise application deployments on servers with metadata
- **Server Environment Inventory**: Server-side infrastructure tracking with application relationships  
- **Database and Data Store Tracking**: Backend data storage systems used by applications
- **Role-Based Access**: Five-tier user permission system
- **REST API**: Programmatic interface for data access and manipulation
- **Audit Logging**: Comprehensive activity tracking for compliance requirements
- **File-Based Audit Trail**: All database changes logged to files with timestamps and user attribution
- **Documentation Access**: Role-based access to system documentation at `/docs`

### Scope and Limitations

- **Server-Side Focus**: Tracks application installations on server environments only
- **No Physical Asset Tracking**: Does not inventory physical hardware (servers, network equipment, etc.)
- **No Client-Side Tracking**: Does not track software installations on end-user devices
- **Future Integration**: May integrate with physical asset management systems in the future
- **Enterprise Applications**: Focuses on business applications rather than system software

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface                            │
│          SvelteKit Frontend with TypeScript                 │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP/REST API  
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend Services                          │
│    Django 4.2+ with Django REST Framework                  │
│    ├── Role-Based Access Control                           │
│    ├── Basic Audit Logging                                 │  
│    ├── Data Validation                                     │
│    └── API Authentication                                  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌─────────────┐                  ┌─────────────────────┐ │
│  │   MySQL     │                  │   File Storage      │ │
│  │  Database   │                  │   (Static Files)    │ │
│  │  (Primary)  │                  │                     │ │
│  └─────────────┘                  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/app-tracker.git
   cd app-tracker
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - **Web Interface**: http://localhost
   - **API Documentation**: http://localhost/api/docs/
   - **Admin Panel**: http://localhost/admin/
   - **System Documentation**: http://localhost/docs/ (requires access permission)

### Test User Accounts

The system includes pre-configured test accounts for development:

| Username | Role | Password | Access Level |
|----------|------|----------|--------------|
| `admin` | Application Admin | `admin123` | Full system access |
| `sysmanager` | Systems Manager | `sysmanager123` | Technical data access |
| `technician` | Technician | `technician123` | Limited write access |
| `bizmanager` | Business Manager | `bizmanager123` | Business data read access |
| `bizuser` | Business User | `bizuser123` | Basic read access |

## Security and Compliance

### Role-Based Access Control

The system implements a five-tier hierarchical permission model:

1. **Application Admin** (Level 5)
   - Complete system access
   - User management capabilities
   - Security configuration access
   - All data access including system notes

2. **Systems Manager** (Level 4)
   - Technical data management
   - System notes visibility
   - Infrastructure data access
   - No user management permissions

3. **Technician** (Level 3)
   - Limited write access to assigned resources
   - Can edit records they created
   - No access to system notes
   - No user management permissions

4. **Business Manager** (Level 2)
   - Read-only access to business data
   - Basic reporting capabilities
   - No technical data access
   - No system notes access

5. **Business User** (Level 1)
   - Basic read access to public information
   - Limited data visibility
   - No sensitive data access

### Security Implementation

- **Authentication**: Session-based authentication with timeout controls
- **Authorization**: Role-based permission checking on all operations
- **Audit Logging**: Basic activity tracking for compliance requirements
- **Data Validation**: Input validation and sanitization
- **Session Security**: Secure session management with appropriate timeouts
- **Documentation Access Control**: Role-based access to system documentation with automatic access for Application Admins
- **Comprehensive Audit Logging**: All database changes logged to files with user attribution and timestamps

## Data Models

### Core Data Models

**Applications**
- Enterprise application installation metadata and descriptions
- Server deployment relationships and configuration details
- Business ownership and technical contact information
- Technology stack and dependency tracking

**Server Environments**
- Server infrastructure inventory supporting application deployments
- Operating system and configuration details for application hosting
- Environment classifications (development, staging, production, etc.)
- System manager notes for technical documentation

**Data Stores**
- Backend database and storage system inventory
- Version and configuration tracking for data systems
- Application dependency relationships and connection details
- Performance and capacity information

**Cloud Platforms**
- Cloud service provider tracking for hosted applications
- Resource and service inventory for cloud-deployed applications
- Cost center and ownership information for cloud resources
- Service configuration and integration details

## API Integration

### REST API

The system provides a REST API at `/api/` with the following capabilities:

- **Authentication**: Token-based authentication
- **Authorization**: Role-based access control
- **Data Access**: CRUD operations for all data models
- **Filtering**: Basic search and filtering capabilities
- **Pagination**: Standard pagination for large result sets

### API Examples

```bash
# Authentication
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# List applications
curl -H "Authorization: Bearer <token>" \
  http://localhost/api/applications/

# Create new application
curl -X POST http://localhost/api/applications/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My App", "description": "Application description"}'
```

## Deployment

### Development

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run database migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

### Production

```bash
# Production deployment with Docker Swarm
docker stack deploy -c docker-compose.prod.yml app-tracker

# Or with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Key environment variables for deployment:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com

# Database Configuration
DB_NAME=app_tracker
DB_USER=app_user
DB_PASSWORD=secure-password
DB_HOST=mysql
DB_PORT=3306

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# Application Version
APP_VERSION=0.0.1
```

## Documentation

Basic documentation is available in the `/docs` directory and served through the web application at `/docs`:

- **User Guide**: Basic user instructions for each role
- **API Reference**: REST API endpoint documentation  
- **Administration Guide**: System administration procedures
- **Development Guide**: Developer setup and contribution information

### Documentation Access Control

Access to system documentation is controlled through role-based permissions:

- **Application Administrators**: Automatic access (non-revokable)
- **Systems Managers**: Automatic access on account creation (revokable by admins)
- **Other Users**: Access must be explicitly granted by Application Administrators

Documentation access can be managed through the Django admin interface under User Profiles.

## Audit Logging

The system provides comprehensive audit logging of all database changes to ensure compliance and accountability:

### Audit Log Features

- **Complete Coverage**: Every CREATE, UPDATE, and DELETE operation is logged
- **User Attribution**: All changes include the username of the person who made the change
- **Timestamp Precision**: MySQL datetime format for easy sorting and filtering
- **Change Details**: For UPDATE operations, logs show old and new values for each changed field
- **Human & Script Readable**: Dual format for both human review and automated processing
- **File-Based Storage**: Logs stored securely in files, not accessible via web interface

### Log Format

Each audit entry contains:
- **Timestamp**: MySQL datetime format (YYYY-MM-DD HH:MM:SS)
- **Action**: CREATE, UPDATE, or DELETE
- **Model**: Which data model was affected
- **Object ID**: Primary key of the affected record
- **User**: Username who made the change
- **Changes**: Field-by-field old/new values for updates
- **JSON Data**: Machine-readable format for automated processing

### Log Location

- **Production**: `/var/log/app-tracker/audit.log`
- **Development**: `./logs/audit.log`
- **Docker**: Mounted volume for persistent logging

### Viewing Audit Logs

Use the included log viewer script:

```bash
# View recent audit entries
python view_audit_logs.py --tail 50

# Filter by user
python view_audit_logs.py --user admin

# Filter by action type
python view_audit_logs.py --action UPDATE

# Filter by time range
python view_audit_logs.py --since "2025-07-27 10:00:00"

# Get JSON output for scripting
python view_audit_logs.py --json-only --user admin
```

### Testing Audit Logging

Test the audit system with the management command:

```bash
python manage.py test_audit_logging --user admin
```

### Building Documentation

```bash
# Install Sphinx and dependencies
pip install sphinx sphinx-rtd-theme

# Build HTML documentation
cd docs
sphinx-build -b html . _build/html

# View documentation
open _build/html/index.html
```

## Technology Stack

### Backend
- **Django 4.2+**: Web framework
- **Django REST Framework**: API development
- **MySQL 8.4**: Primary database
- **Gunicorn**: WSGI server

### Frontend
- **SvelteKit**: Frontend framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Development orchestration
- **Docker Swarm**: Production deployment
- **Nginx**: Reverse proxy and load balancer

## Contributing

This is an experimental project. Please see the [Development Guide](docs/development/index.rst) for:

- Development environment setup
- Basic coding standards
- Testing procedures
- Pull request process

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/app-tracker.git
cd app-tracker

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Install development dependencies
docker-compose exec backend pip install -r requirements-dev.txt
docker-compose exec frontend npm install
```

## License

This project is licensed under the Enterprise License. Contact your organization for licensing details.

## Support

### Getting Help

1. **Documentation**: Check the comprehensive documentation in `/docs`
2. **API Issues**: Consult the API reference and error codes
3. **Security Questions**: Review the security implementation guide
4. **Technical Support**: Contact your system administrator

### Issue Reporting

For bug reports and feature requests:
1. Check existing issues first
2. Provide detailed reproduction steps
3. Include system information and logs
4. Follow the issue template

## Project Status

- **Version**: 0.0.1 (Experimental Release)
- **Status**: Development/Experimental
- **Last Updated**: July 2025
- **Maintenance**: Active development

## Changelog

### Version 0.0.1 (July 2025)
- Initial experimental release
- Basic application inventory functionality
- Role-based access control system
- REST API implementation
- Basic security features
- Initial documentation
- Docker-based deployment

---

**Enterprise Application Tracker** - Experimental Application Inventory System  
© 2025 David Cloutman