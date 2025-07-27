Deployment Guide
================

This guide covers deployment scenarios for the Enterprise Application Tracker in various environments.

.. toctree::
   :maxdepth: 2
   :hidden:

Overview
--------

The Enterprise Application Tracker is designed to be deployed in various environments:

- **Docker Compose**: Development and small production deployments
- **Docker Swarm**: Medium-scale production with high availability
- **Kubernetes**: Large-scale enterprise deployments
- **Cloud Platforms**: AWS, Azure, Google Cloud Platform
- **Bare Metal**: Traditional server deployments

Architecture Components
-----------------------

**Core Services**

.. code-block::

    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   Load Balancer │    │   Web Frontend  │    │  API Backend    │
    │                 │    │                 │    │                 │
    │   Nginx/HAProxy │◄───┤   SvelteKit     │◄───┤   Django/DRF    │
    │                 │    │                 │    │                 │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                           │
                           ┌─────────────────┐             │
                           │    Database     │             │
                           │                 │◄────────────┘
                           │   MySQL 8.4     │
                           │                 │
                           └─────────────────┘

**Supporting Services**

- **File Storage**: Static files and uploads
- **Monitoring**: Health checks and system metrics
- **Elasticsearch**: Search and logging (optional)

Pre-deployment Checklist
-------------------------

**Security Requirements**

□ SSL/TLS certificates obtained and configured
□ Database credentials generated and secured
□ Environment variables configured
□ Firewall rules configured
□ Backup strategy implemented
□ Monitoring configured
□ Log aggregation setup

**Performance Requirements**

□ Resource requirements calculated
□ Storage sizing determined
□ Network bandwidth assessed
□ Load testing completed
□ Scaling parameters configured

**Compliance Requirements**

□ Data retention policies configured
□ Audit logging enabled
□ User access controls implemented
□ Security scanning completed
□ Documentation updated

Environment Configuration
-------------------------

**Environment Variables**

Create a ``.env`` file with the following variables:

.. code-block:: bash

    # Django Settings
    DJANGO_SECRET_KEY=your-very-long-secret-key-here
    DJANGO_DEBUG=False
    DJANGO_ALLOWED_HOSTS=your-domain.com,localhost
    
    # Database Configuration
    DB_NAME=app_tracker
    DB_USER=app_user
    DB_PASSWORD=secure-database-password
    DB_HOST=mysql
    DB_PORT=3306
    
    # Email Configuration
    EMAIL_HOST=smtp.your-domain.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER=noreply@your-domain.com
    EMAIL_HOST_PASSWORD=email-password
    
    # Security Settings
    SECURE_SSL_REDIRECT=True
    SECURE_HSTS_SECONDS=31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True
    SECURE_HSTS_PRELOAD=True
    
    # Application Settings
    APP_VERSION=0.0.1
    APP_ENVIRONMENT=production
    
    # File Storage
    MEDIA_ROOT=/app/media
    STATIC_ROOT=/app/static
    
    # Logging
    LOG_LEVEL=INFO
    LOG_FILE=/app/logs/app.log

**Database Configuration**

.. code-block:: sql

    -- Create database and user
    CREATE DATABASE app_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER 'app_user'@'%' IDENTIFIED BY 'secure-database-password';
    GRANT ALL PRIVILEGES ON app_tracker.* TO 'app_user'@'%';
    FLUSH PRIVILEGES;
    
    -- Configure for production
    SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
    SET GLOBAL max_connections = 200;
    SET GLOBAL query_cache_size = 67108864; -- 64MB

**Nginx Configuration**

.. code-block:: nginx

    # /etc/nginx/sites-available/app-tracker
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        # SSL Configuration
        ssl_certificate /etc/ssl/certs/app-tracker.crt;
        ssl_certificate_key /etc/ssl/private/app-tracker.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;
        
        # Security Headers
        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # Static Files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        location /media/ {
            alias /app/media/;
            expires 1y;
            add_header Cache-Control "public";
        }
        
        # API Backend
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30;
            proxy_send_timeout 30;
            proxy_read_timeout 30;
        }
        
        # Frontend
        location / {
            proxy_pass http://frontend:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health Check
        location /health/ {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

Production Hardening
--------------------

**Security Hardening**

.. code-block:: yaml

    # docker-compose.prod.yml security additions
    version: '3.8'
    
    services:
      backend:
        security_opt:
          - no-new-privileges:true
        read_only: true
        tmpfs:
          - /tmp
          - /var/tmp
        user: "1000:1000"
        cap_drop:
          - ALL
        cap_add:
          - NET_BIND_SERVICE
        
      mysql:
        security_opt:
          - no-new-privileges:true
        user: "999:999"
        cap_drop:
          - ALL
        environment:
          MYSQL_ROOT_PASSWORD_FILE: /run/secrets/mysql_root_password
        secrets:
          - mysql_root_password
    
    secrets:
      mysql_root_password:
        file: ./secrets/mysql_root_password.txt

**Resource Limits**

.. code-block:: yaml

    services:
      backend:
        deploy:
          resources:
            limits:
              cpus: '2.0'
              memory: 2G
            reservations:
              cpus: '0.5'
              memory: 512M
          restart_policy:
            condition: on-failure
            delay: 5s
            max_attempts: 3
        
      mysql:
        deploy:
          resources:
            limits:
              cpus: '2.0'
              memory: 4G
            reservations:
              cpus: '1.0'
              memory: 2G

**Health Checks**

.. code-block:: yaml

    services:
      backend:
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
          interval: 30s
          timeout: 10s
          retries: 3
          start_period: 40s
        
      mysql:
        healthcheck:
          test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
          interval: 30s
          timeout: 10s
          retries: 5
          start_period: 30s

High Availability Setup
-----------------------

**Database Replication**

.. code-block:: yaml

    # Master-Slave MySQL setup
    services:
      mysql-master:
        image: mysql:8.4
        environment:
          MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
          MYSQL_DATABASE: ${DB_NAME}
          MYSQL_USER: ${DB_USER}
          MYSQL_PASSWORD: ${DB_PASSWORD}
        command: >
          --server-id=1
          --log-bin=mysql-bin
          --binlog-format=ROW
          --gtid-mode=ON
          --enforce-gtid-consistency=ON
        volumes:
          - mysql_master_data:/var/lib/mysql
        networks:
          - database
        
      mysql-slave:
        image: mysql:8.4
        environment:
          MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
        command: >
          --server-id=2
          --read-only=1
          --log-bin=mysql-bin
          --binlog-format=ROW
          --gtid-mode=ON
          --enforce-gtid-consistency=ON
          --skip-slave-start
        volumes:
          - mysql_slave_data:/var/lib/mysql
        networks:
          - database
        depends_on:
          - mysql-master

**Load Balancing**

.. code-block:: yaml

    services:
      nginx:
        image: nginx:alpine
        ports:
          - "80:80"
          - "443:443"
        volumes:
          - ./nginx/nginx.conf:/etc/nginx/nginx.conf
          - ./ssl:/etc/ssl
        depends_on:
          - backend-1
          - backend-2
          - backend-3
        
      backend-1:
        <<: *backend-common
        container_name: backend-1
        
      backend-2:
        <<: *backend-common
        container_name: backend-2
        
      backend-3:
        <<: *backend-common
        container_name: backend-3

Backup and Recovery
-------------------

**Automated Backup Script**

.. code-block:: bash

    #!/bin/bash
    # backup.sh
    
    set -e
    
    BACKUP_DIR="/backups"
    DATE=$(date +%Y%m%d_%H%M%S)
    
    # Database backup
    echo "Starting database backup..."
    docker exec app-tracker_mysql_1 mysqldump \
        --single-transaction \
        --routines \
        --triggers \
        --all-databases \
        -u root -p${MYSQL_ROOT_PASSWORD} > "${BACKUP_DIR}/db_backup_${DATE}.sql"
    
    # Compress database backup
    gzip "${BACKUP_DIR}/db_backup_${DATE}.sql"
    
    # File system backup
    echo "Starting file system backup..."
    tar -czf "${BACKUP_DIR}/files_backup_${DATE}.tar.gz" \
        -C /app media logs
    
    # Encrypt backups
    echo "Encrypting backups..."
    gpg --symmetric --cipher-algo AES256 \
        "${BACKUP_DIR}/db_backup_${DATE}.sql.gz"
    gpg --symmetric --cipher-algo AES256 \
        "${BACKUP_DIR}/files_backup_${DATE}.tar.gz"
    
    # Remove unencrypted files
    rm "${BACKUP_DIR}/db_backup_${DATE}.sql.gz"
    rm "${BACKUP_DIR}/files_backup_${DATE}.tar.gz"
    
    # Clean old backups (keep 30 days)
    find "${BACKUP_DIR}" -name "*.gpg" -mtime +30 -delete
    
    echo "Backup completed successfully"

**Disaster Recovery**

.. code-block:: bash

    #!/bin/bash
    # restore.sh
    
    set -e
    
    BACKUP_FILE=$1
    if [ -z "$BACKUP_FILE" ]; then
        echo "Usage: $0 <backup_file>"
        exit 1
    fi
    
    # Decrypt backup
    gpg --decrypt "$BACKUP_FILE" > /tmp/backup.sql
    
    # Stop application
    ./bin/eatcmd stop
    
    # Start only database and wait
    docker-compose up -d mysql
    sleep 30  # Wait for MySQL to start
    
    docker exec -i app-tracker_mysql_1 mysql \
        -u root -p${MYSQL_ROOT_PASSWORD} < /tmp/backup.sql
    
    # Start full application
    ./bin/eatcmd start
    
    # Clean up
    rm /tmp/backup.sql
    
    echo "Restore completed successfully"

**Backup Verification**

.. code-block:: bash

    #!/bin/bash
    # verify-backup.sh
    
    BACKUP_FILE=$1
    
    # Decrypt and test SQL syntax
    gpg --decrypt "$BACKUP_FILE" | head -n 100 | mysql --help > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "Backup verification successful"
    else
        echo "Backup verification failed"
        exit 1
    fi

Monitoring and Logging
----------------------

**Health Check Endpoints**

.. code-block:: python

    # backend/health/views.py
    from django.http import JsonResponse
    from django.db import connection
    from django.core.cache import cache
    
    def health_check(request):
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {}
        }
        
        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['services']['database'] = 'healthy'
        except Exception as e:
            health_status['services']['database'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Cache check
        try:
            cache.set('health_check', 'ok', 10)
            cache.get('health_check')
            health_status['services']['cache'] = 'healthy'
        except Exception as e:
            health_status['services']['cache'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return JsonResponse(health_status, status=status_code)

**Log Configuration**

.. code-block:: yaml

    # docker-compose.logging.yml
    version: '3.8'
    
    x-logging: &default-logging
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "app,environment,service"
    
    services:
      backend:
        logging: *default-logging
        labels:
          - "app=app-tracker"
          - "environment=production"
          - "service=backend"
        
      frontend:
        logging: *default-logging
        labels:
          - "app=app-tracker"
          - "environment=production"
          - "service=frontend"

**Performance Monitoring**

.. code-block:: yaml

    # monitoring/docker-compose.yml
    version: '3.8'
    
    services:
      prometheus:
        image: prom/prometheus:latest
        ports:
          - "9090:9090"
        volumes:
          - ./prometheus.yml:/etc/prometheus/prometheus.yml
          - prometheus_data:/prometheus
        command:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--web.console.libraries=/etc/prometheus/console_libraries'
          - '--web.console.templates=/etc/prometheus/consoles'
          - '--storage.tsdb.retention.time=200h'
          - '--web.enable-lifecycle'
        
      grafana:
        image: grafana/grafana:latest
        ports:
          - "3001:3000"
        environment:
          GF_SECURITY_ADMIN_PASSWORD: admin123
        volumes:
          - grafana_data:/var/lib/grafana
          - ./grafana/provisioning:/etc/grafana/provisioning
        
      node-exporter:
        image: prom/node-exporter:latest
        ports:
          - "9100:9100"
        volumes:
          - /proc:/host/proc:ro
          - /sys:/host/sys:ro
          - /:/rootfs:ro
        command:
          - '--path.procfs=/host/proc'
          - '--path.sysfs=/host/sys'
          - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    
    volumes:
      prometheus_data:
      grafana_data:

Troubleshooting
---------------

**Common Issues**

1. **Database Connection Issues**
   
   .. code-block:: bash
   
       # Check service status and logs
       ./bin/eatcmd status
       ./bin/eatcmd logs
       
       # Access database through application shell
       ./bin/eatcmd shell
       # Inside container: python manage.py dbshell

2. **Memory Issues**
   
   .. code-block:: bash
   
       # Check system information
       ./bin/eatcmd info
       
       # Check Docker container stats manually
       docker stats
       
       # Increase memory limits in docker-compose.yml
       deploy:
         resources:
           limits:
             memory: 4G

3. **SSL Certificate Issues**
   
   .. code-block:: bash
   
       # Test SSL certificate
       openssl x509 -in /etc/ssl/certs/app-tracker.crt -text -noout
       
       # Verify certificate chain
       openssl verify -CAfile /etc/ssl/certs/ca-bundle.crt /etc/ssl/certs/app-tracker.crt

4. **Performance Issues**
   
   .. code-block:: bash
   
       # Monitor application performance using shell access
       ./bin/eatcmd shell
       >>> from django.db import connection
       >>> print(len(connection.queries))
       
       # Enable query logging
       LOGGING = {
           'loggers': {
               'django.db.backends': {
                   'level': 'DEBUG',
               }
           }
       }

**Log Analysis**

.. code-block:: bash

    # View application logs with follow mode
    ./bin/eatcmd logs --follow
    
    # View recent logs without follow mode
    ./bin/eatcmd logs
