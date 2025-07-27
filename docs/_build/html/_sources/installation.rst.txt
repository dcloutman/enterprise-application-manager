Installation Guide
==================

This guide covers the installation and initial setup of the Enterprise Application Tracker.

Prerequisites
-------------

**System Requirements**

* Docker 20.10+ and Docker Compose 2.0+
* 4GB RAM minimum (8GB recommended)
* 20GB available disk space
* Network access for container image downloads

**Security Requirements**

* TLS/SSL certificates for production deployment
* Firewall configuration for required ports
* User accounts with appropriate permissions

Quick Installation
------------------

**1. Clone the Repository**

.. code-block:: bash

    git clone https://github.com/dcloutman/enterprise-application-manager.git
    cd enterprise-application-manager

**2. Environment Configuration**

.. code-block:: bash

    # Copy environment template
    cp .env.example .env
    
    # Edit configuration (see Configuration section)
    nano .env

**3. Start Services**

.. code-block:: bash

    # Start all services using the CLI tool
    ./bin/eatcmd start
    
    # Verify services are running
    ./bin/eatcmd status

**4. Initial Setup**

.. code-block:: bash

    # Run the initial project setup
    ./bin/eatcmd setup
    
    # Access the application shell to complete setup
    ./bin/eatcmd shell
    
    # Inside the container, run migrations and setup RBAC
    python manage.py migrate
    python setup_rbac.py
    python manage.py createsuperuser

**5. Access the Application**

* **Web Interface**: http://localhost
* **Admin Panel**: http://localhost/admin/
* **API Documentation**: http://localhost/api/

Docker Swarm Installation
-------------------------

For production high-availability deployment:

**1. Initialize Swarm**

.. code-block:: bash

    # On manager node
    docker swarm init
    
    # Join worker nodes (run on each worker)
    docker swarm join --token <token> <manager-ip>:2377

**2. Deploy Stack**

.. code-block:: bash

    # Deploy the application stack
    docker stack deploy -c docker-stack.yml app-tracker
    
    # Monitor deployment
    docker stack services app-tracker

**3. Configure Load Balancer**

.. code-block:: nginx

    # /etc/nginx/sites-available/app-tracker
    upstream app_backend {
        server node1:80;
        server node2:80;
        server node3:80;
    }
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        ssl_certificate /path/to/certificate.crt;
        ssl_certificate_key /path/to/private.key;
        
        location / {
            proxy_pass http://app_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

Configuration
-------------

**Environment Variables**

.. code-block:: bash

    # Database Configuration
    MYSQL_ROOT_PASSWORD=secure_root_password
    MYSQL_DATABASE=app_tracker
    MYSQL_USER=app_user
    MYSQL_PASSWORD=secure_app_password
    
    # Django Settings
    DJANGO_SECRET_KEY=your-secret-key-here
    DJANGO_DEBUG=False
    DJANGO_ALLOWED_HOSTS=your-domain.com,localhost
    
    # Security Settings
    DJANGO_SECURE_SSL_REDIRECT=True
    DJANGO_SECURE_HSTS_SECONDS=31536000
    DJANGO_SESSION_COOKIE_SECURE=True
    DJANGO_CSRF_COOKIE_SECURE=True
    
    # Email Configuration (optional)
    EMAIL_HOST=smtp.your-domain.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=noreply@your-domain.com
    EMAIL_HOST_PASSWORD=email_password
    EMAIL_USE_TLS=True

**Database Configuration**

For production, consider using external managed database:

.. code-block:: python

    # settings/production.py
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'app_tracker_prod',
            'USER': 'app_user',
            'PASSWORD': 'secure_password',
            'HOST': 'your-rds-endpoint.amazonaws.com',
            'PORT': '3306',
            'OPTIONS': {
                'sql_mode': 'traditional',
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }

Initial Setup
-------------

**1. Create Initial Users**

.. code-block:: bash

    # Run the RBAC setup script
    docker-compose exec app python setup_rbac.py

This creates the following default users:

* **admin** (Application Admin) - Password: admin123
* **sysmanager** (Systems Manager) - Password: manager123
* **technician** (Technician) - Password: tech123
* **bizmanager** (Business Manager) - Password: biz123
* **bizuser** (Business User) - Password: user123

****WARNING** Important**: Change these default passwords immediately in production!

**2. Configure System Settings**

Access the admin panel at http://localhost/admin/ and configure:

* Site settings (domain, site name)
* Email configuration
* Security settings
* Cloud platform credentials (if using cloud integrations)

**3. Import Initial Data**

.. code-block:: bash

    # Load sample data using the shell command (optional for testing)
    ./bin/eatcmd shell
    # Inside the container:
    python manage.py loaddata sample_data.json

Verification
------------

**1. Service Health Check**

.. code-block:: bash

    # Check all services are running
    ./bin/eatcmd status
    
    # Check logs for errors
    ./bin/eatcmd logs

**2. Web Interface Test**

1. Navigate to http://localhost
2. Login with admin credentials
3. Verify dashboard loads properly
4. Test basic navigation

**3. API Test**

.. code-block:: bash

    # Test API authentication
    curl -u admin:admin123 http://localhost/api/auth/profile/
    
    # Test API endpoints
    curl -u admin:admin123 http://localhost/api/servers/

Troubleshooting
---------------

**Common Issues**

*Service won't start*

.. code-block:: bash

    # Check application logs
    ./bin/eatcmd logs
    
    # Restart all services
    ./bin/eatcmd restart

*Database connection errors*

.. code-block:: bash

    # Check service status
    ./bin/eatcmd status
    
    # View detailed logs
    ./bin/eatcmd logs --follow
    
    # Access database shell through application
    ./bin/eatcmd shell
    # Inside container: python manage.py dbshell

*Permission denied errors*

.. code-block:: bash

    # Fix file permissions using the CLI tool
    ./bin/eatcmd setup
    
    # Fix Docker socket permissions
    sudo chmod 666 /var/run/docker.sock

**Getting Help**

* Check the logs: ``docker-compose logs``
* Review configuration: Verify ``.env`` file settings
* Database issues: Ensure MySQL container has sufficient resources
* Network issues: Check firewall and Docker network configuration

Next Steps
----------

After successful installation:

1. **Security**: Change default passwords and configure TLS
2. **Users**: Set up your organization's user accounts and roles
3. **Data**: Begin importing your IT asset inventory
4. **Integration**: Configure cloud platform integrations
5. **Backup**: Set up regular database backups
6. **Monitoring**: Configure application monitoring and alerting
