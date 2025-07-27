Administrator Guide
===================

This guide provides comprehensive information for system administrators managing the Enterprise Application Tracker.

.. toctree::
   :maxdepth: 2

   ../security/audit-logging

System Administration Overview
------------------------------

As an Application Administrator, you have full access to all system functionality including:

- **User Management**: Create, modify, and manage user accounts and roles
- **System Configuration**: Configure application settings and security policies
- **Data Management**: Oversee all data creation, modification, and deletion
- **Security Administration**: Manage permissions, audit logs, and security settings
- **System Maintenance**: Perform backups, updates, and system monitoring

Dashboard Overview
------------------

The administrator dashboard provides a comprehensive view of system status:

**System Health Monitoring**

.. note::
   The administrator dashboard provides real-time system monitoring capabilities.

The dashboard displays:

- **Active Users**: Current logged-in users and session information
- **System Performance**: CPU, memory, and database performance metrics
- **Recent Activity**: Latest user actions and system events
- **Security Alerts**: Failed login attempts and security incidents
- **Data Statistics**: Record counts and growth trends

Quick Actions
-------------

**Most Common Administrative Tasks**

1. **Create New User Account**
   
   Navigate to *Users → Add User*
   
   .. code-block::

       Username: john.doe
       Email: john.doe@organization.com
       First Name: John
       Last Name: Doe
       Role: Business User
       Department: IT Operations
       Phone: (555) 123-4567

2. **Reset User Password**
   
   Navigate to *Users → [Select User] → Reset Password*
   
   System generates secure temporary password and sends via email.

3. **Bulk User Import**
   
   Navigate to *Users → Import → Upload CSV*
   
   CSV format:
   
   .. code-block::

       username,email,first_name,last_name,role,department,phone
       jane.smith,jane.smith@org.com,Jane,Smith,technician,IT,555-123-4568
       bob.johnson,bob.johnson@org.com,Bob,Johnson,business_manager,Finance,555-123-4569

4. **Generate System Report**
   
   Navigate to *Reports → System Usage → Generate*
   
   Reports include:
   - User activity summaries
   - Data growth trends  
   - Security incident reports
   - Performance metrics

User Management
---------------

**User Account Lifecycle**

.. list-table::
   :widths: 20 40 40
   :header-rows: 1

   * - **Stage**
     - **Actions**
     - **Considerations**
   * - **Creation**
     - Create account, assign role, send welcome email
     - Verify role appropriateness, department assignment
   * - **Active Use**
     - Monitor activity, update permissions as needed
     - Regular access reviews, role changes
   * - **Modification**
     - Update profile, change roles, reset passwords
     - Approval workflows for role elevation
   * - **Deactivation**
     - Disable account, archive data, transfer ownership
     - Data retention requirements, handover procedures
   * - **Deletion**
     - Remove account, anonymize data per policy
     - Legal requirements, audit trail preservation

**Role Assignment Guidelines**

**Business User Role**
- **Intended For**: General staff needing basic application information
- **Typical Departments**: All departments
- **Access Level**: Read-only access to public application data
- **Use Cases**: Looking up application contacts, basic reporting

**Business Manager Role**
- **Intended For**: Department managers and supervisors
- **Typical Departments**: Department heads, team leaders
- **Access Level**: Read access to business-focused data
- **Use Cases**: Department reporting, resource planning

**Technician Role**
- **Intended For**: Technical staff with hands-on responsibilities
- **Typical Departments**: IT Operations, Development teams
- **Access Level**: Edit access to assigned technical resources
- **Use Cases**: Server maintenance, application updates

**Systems Manager Role**
- **Intended For**: Senior technical staff and architects
- **Typical Departments**: IT Management, System Architecture
- **Access Level**: Full technical data access including system notes
- **Use Cases**: System planning, technical documentation, troubleshooting

**Application Administrator Role**
- **Intended For**: System administrators and security officers
- **Typical Departments**: IT Security, System Administration
- **Access Level**: Complete system access including user management
- **Use Cases**: User account management, security configuration, system maintenance

Security Management
-------------------

**Security Policy Configuration**

**Password Policies**

.. code-block:: python

    # Configure in Django Admin → Security Settings
    
    PASSWORD_REQUIREMENTS = {
        'minimum_length': 12,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_symbols': True,
        'password_history': 12,  # Cannot reuse last 12 passwords
        'max_age_days': 90,      # Force change every 90 days
        'lockout_attempts': 5,   # Lock after 5 failed attempts
        'lockout_duration': 900  # 15 minutes lockout
    }

**Session Security**

.. code-block:: python

    SESSION_SECURITY = {
        'session_timeout': 3600,    # 1 hour
        'concurrent_sessions': {
            'business_user': 2,
            'business_manager': 3,
            'technician': 3,
            'systems_manager': 5,
            'application_admin': 10
        },
        'ip_validation': True,      # Bind session to IP
        'browser_validation': True  # Bind session to browser
    }

**Audit Configuration**

Enable comprehensive audit logging:

.. code-block:: python

    AUDIT_SETTINGS = {
        'log_login_attempts': True,
        'log_data_changes': True,
        'log_permission_changes': True,
        'log_admin_actions': True,
        'retention_days': 2555,  # 7 years
        'alert_on_suspicious_activity': True
    }

**Multi-Factor Authentication**

Configure MFA requirements by role:

1. Navigate to *Security → MFA Settings*
2. Configure role-based requirements:
   
   .. code-block::

       Application Admin: MFA Required
       Systems Manager: MFA Required for Production Access
       Technician: MFA Recommended
       Business Manager: MFA Optional
       Business User: MFA Optional

Data Management
---------------

**Data Quality Monitoring**

**Automated Data Validation**

.. code-block:: python

    # Run data quality checks
    python manage.py check_data_quality
    
    # Example output:
    Data Quality Report - 2024-01-15
    ================================
    
    Applications: 1,245 records
    - 12 missing descriptions
    - 3 invalid URLs
    - 0 duplicate names
    
    Servers: 856 records  
    - 45 missing system manager notes
    - 2 invalid IP addresses
    - 1 orphaned record (no application link)

**Data Cleanup Procedures**

1. **Duplicate Detection**
   
   .. code-block:: bash
   
       # Find potential duplicates
       python manage.py find_duplicates --model=Application --field=name
       
       # Review and merge duplicates
       python manage.py merge_duplicates --dry-run

2. **Orphaned Record Cleanup**
   
   .. code-block:: bash
   
       # Find orphaned servers (no linked application)
       python manage.py find_orphaned_records --model=Server
       
       # Clean orphaned records older than 90 days
       python manage.py cleanup_orphaned --days=90

3. **Data Archival**
   
   .. code-block:: bash
   
       # Archive inactive applications (no activity > 2 years)
       python manage.py archive_inactive_data --model=Application --days=730
       
       # Verify archive integrity
       python manage.py verify_archives

**Data Export and Import**

**Bulk Data Export**

.. code-block:: bash

    # Export all applications to CSV
    python manage.py export_data --model=Application --format=csv --output=/tmp/applications.csv
    
    # Export with filtering
    python manage.py export_data --model=Server --filter="is_active=True" --format=json

**Bulk Data Import**

.. code-block:: bash

    # Import from CSV with validation
    python manage.py import_data --model=Application --file=/tmp/applications.csv --validate
    
    # Import with conflict resolution
    python manage.py import_data --model=Server --file=/tmp/servers.json --on-conflict=update

System Monitoring
-----------------

**Performance Monitoring**

**Database Performance**

Monitor database performance through the admin interface:

- Navigate to *System → Database Performance*
- Review slow query log
- Monitor connection usage
- Check index effectiveness

**Key Metrics to Monitor**

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - **Metric**
     - **Warning Threshold**
     - **Critical Threshold**
   * - **Response Time**
     - > 2 seconds
     - > 5 seconds
   * - **Database Connections**
     - > 80% of max
     - > 95% of max
   * - **Memory Usage**
     - > 85%
     - > 95%
   * - **Disk Usage**
     - > 80%
     - > 90%
   * - **Failed Logins**
     - > 10 per hour
     - > 50 per hour

**Automated Alerts**

Configure email alerts for system events:

.. code-block:: python

    ALERT_SETTINGS = {
        'high_cpu_usage': {
            'threshold': 85,
            'recipients': ['admin@organization.com'],
            'frequency': 'immediate'
        },
        'failed_logins': {
            'threshold': 10,
            'recipients': ['security@organization.com'],
            'frequency': 'hourly_digest'
        },
        'system_errors': {
            'threshold': 1,
            'recipients': ['admin@organization.com', 'support@organization.com'],
            'frequency': 'immediate'
        }
    }

**Health Check Dashboard**

Access the system health dashboard at ``/admin/system/health/``:

- **Service Status**: Database, cache, email, storage
- **Performance Metrics**: Response times, throughput, error rates  
- **Resource Usage**: CPU, memory, disk, network
- **Security Status**: Failed logins, suspicious activity

Backup and Recovery
-------------------

**Backup Strategy**

**Automated Daily Backups**

.. code-block:: bash

    # Configure automated backup (add to crontab)
    0 2 * * * /opt/app-tracker/scripts/backup.sh >> /var/log/backup.log 2>&1

**Backup Components**

1. **Database Backup**
   - Full database dump with structure and data
   - Encrypted with GPG
   - Stored on separate storage system
   - Retention: 30 days daily, 12 months monthly

2. **File System Backup**
   - User uploaded files (/media directory)
   - System logs (/logs directory)  
   - Configuration files
   - SSL certificates

3. **Configuration Backup**
   - Environment variables
   - Docker configurations
   - Nginx configurations
   - SSL certificates

**Recovery Procedures**

**Database Recovery**

.. code-block:: bash

    # List available backups
    ls -la /backups/*.sql.gpg
    
    # Decrypt and restore specific backup
    gpg --decrypt /backups/db_backup_20240115_020000.sql.gpg | \
    docker exec -i app-tracker_mysql_1 mysql -u root -p${MYSQL_ROOT_PASSWORD}

**Full System Recovery**

.. code-block:: bash

    # Full disaster recovery procedure
    ./scripts/disaster-recovery.sh /backups/backup_20240115_020000/

**Testing Recovery Procedures**

.. code-block:: bash

    # Test backup integrity monthly
    ./scripts/test-backup-integrity.sh
    
    # Perform full recovery test quarterly  
    ./scripts/full-recovery-test.sh

Maintenance Procedures
----------------------

**Regular Maintenance Tasks**

**Daily Tasks**
- Review system health dashboard
- Check backup completion
- Monitor security alerts
- Review failed login attempts

**Weekly Tasks**
- Analyze performance trends
- Review user activity reports
- Check data quality reports
- Update security patches (if available)

**Monthly Tasks**
- User access review
- Clean up orphaned data
- Generate compliance reports
- Test backup recovery
- Performance optimization review

**Quarterly Tasks**
- Full security audit
- Disaster recovery test
- User role review
- System capacity planning
- Update documentation

**System Updates**

**Application Updates**

.. code-block:: bash

    # Update to new version
    ./scripts/update-application.sh --version=0.0.2 --backup
    
    # Rollback if needed
    ./scripts/rollback-application.sh --to-version=0.0.1

**Security Updates**

.. code-block:: bash

    # Update base system packages
    docker-compose exec backend apt update && apt upgrade -y
    
    # Update Python packages
    docker-compose exec backend pip install --upgrade -r requirements.txt
    
    # Restart services
    docker-compose restart

**Database Maintenance**

.. code-block:: sql

    -- Monthly optimization
    OPTIMIZE TABLE applications, servers, data_stores, users;
    
    -- Analyze table statistics
    ANALYZE TABLE applications, servers, data_stores, users;
    
    -- Check table integrity
    CHECK TABLE applications, servers, data_stores, users;

Troubleshooting Guide
---------------------

**Common Issues and Solutions**

**Issue 1: High Memory Usage**

*Symptoms*: Slow response times, container restarts

*Diagnosis*:
.. code-block:: bash

    # Check container memory usage
    docker stats
    
    # Check database memory usage
    docker exec app-tracker_mysql_1 mysql -u root -p -e "SHOW STATUS LIKE 'innodb_buffer_pool%'"

*Solutions*:
- Increase container memory limits
- Optimize database queries
- Enable query caching
- Consider database sharding

**Issue 2: Database Connection Errors**

*Symptoms*: "Connection refused" errors, timeout errors

*Diagnosis*:
.. code-block:: bash

    # Check database connectivity using CLI shell
    ./bin/eatcmd shell
    # Inside container: python manage.py dbshell
    
    # Check application logs
    ./bin/eatcmd logs

*Solutions*:
- Check database service status
- Verify credentials
- Increase connection pool size
- Check firewall rules

**Issue 3: Authentication Issues**

*Symptoms*: Users cannot log in, permission denied errors

*Diagnosis*:
.. code-block:: bash

    # Check application logs for authentication issues
    ./bin/eatcmd logs | grep -i auth
    
    # Check user status using application shell
    ./bin/eatcmd shell
    # Inside container:
    # python manage.py shell -c "
    # from django.contrib.auth.models import User
    # user = User.objects.get(username='problematic_user')
    # print(f'Active: {user.is_active}, Staff: {user.is_staff}')
    # "

*Solutions*:
- Verify user account is active
- Check password expiration
- Verify role assignments
- Clear user sessions

**Issue 4: Performance Degradation**

*Symptoms*: Slow page loads, high CPU usage

*Diagnosis*:
.. code-block:: bash

    # Check slow queries
    docker exec app-tracker_mysql_1 mysql -u root -p -e "
    SELECT query_time, lock_time, rows_examined, sql_text 
    FROM mysql.slow_log 
    ORDER BY query_time DESC 
    LIMIT 10;"
    
    # Check application performance
    docker exec app-tracker_backend_1 python manage.py shell -c "
    from django.db import connection
    print(f'Query count: {len(connection.queries)}')
    "

*Solutions*:
- Add database indexes
- Optimize slow queries
- Enable caching
- Scale horizontally

Emergency Procedures
--------------------

**Security Incident Response**

**Suspected Data Breach**

1. **Immediate Actions**
   - Document the incident time and details
   - Preserve system logs
   - Isolate affected systems if needed
   - Notify security team

2. **Investigation**
   .. code-block:: bash
   
       # Check for unauthorized access
       grep -i "failed\|unauthorized\|suspicious" /var/log/auth.log
       
       # Review database access logs
       docker exec app-tracker_mysql_1 mysql -u root -p -e "
       SELECT * FROM mysql.general_log 
       WHERE event_time > '2024-01-15 00:00:00' 
       AND command_type = 'Query';"

3. **Containment**
   - Reset passwords for affected accounts
   - Temporarily disable compromised accounts
   - Update firewall rules if needed

4. **Recovery**
   - Restore from clean backup if necessary
   - Apply security patches
   - Update access controls

**System Outage**

1. **Assessment**
   .. code-block:: bash
   
       # Check all services using CLI tool
       ./bin/eatcmd status
       
       # Get system information
       ./bin/eatcmd info
       
       # Check system resources
       df -h && free -h && top

2. **Recovery Actions**
   .. code-block:: bash
   
       # Restart all services
       ./bin/eatcmd restart
       
       # Stop and start if needed
       ./bin/eatcmd stop
       ./bin/eatcmd start

3. **Post-Incident**
   - Document root cause
   - Implement preventive measures
   - Update monitoring
   - Notify stakeholders
