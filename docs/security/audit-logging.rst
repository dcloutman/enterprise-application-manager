Audit Logging System
====================

Overview
--------

The Enterprise Application Tracker (EAT) includes a comprehensive audit logging system that tracks all user actions and system changes for compliance, security, and operational monitoring purposes.

Architecture
------------

Core Components
~~~~~~~~~~~~~~~

AuditLog Model
^^^^^^^^^^^^^^

**Location**: ``backend/apps/inventory/models.py``

The ``AuditLog`` model captures detailed information about every action performed in the system:

.. code-block:: python

    class AuditLog(models.Model):
        user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
        action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT
        resource_type = models.CharField(max_length=50)  # Application, Server, TechStack, etc.
        resource_id = models.CharField(max_length=50, null=True, blank=True)
        details = models.JSONField(default=dict)  # Additional context and changes
        ip_address = models.GenericIPAddressField(null=True, blank=True)
        user_agent = models.TextField(null=True, blank=True)
        timestamp = models.DateTimeField(auto_now_add=True)

Audit Middleware
^^^^^^^^^^^^^^^^

**Location**: ``backend/apps/inventory/middleware.py``

Custom middleware that automatically captures audit information for all requests:

- Extracts user information from authenticated sessions
- Captures IP addresses and user agents
- Tracks request timing and response status
- Handles both successful operations and errors

Audit Decorators
^^^^^^^^^^^^^^^^^

**Location**: ``backend/apps/inventory/decorators.py``

Decorators for easy audit logging integration:

- ``@audit_action(action, resource_type)`` - Logs specific actions
- ``@audit_view`` - Automatically audits view access
- ``@audit_model_changes`` - Tracks model CRUD operations

Logged Events
-------------

Authentication Events
~~~~~~~~~~~~~~~~~~~~~

- User login/logout
- Failed authentication attempts
- Session timeouts
- Password changes

Data Operations
~~~~~~~~~~~~~~~

- **CREATE**: New records added to any model
- **UPDATE**: Changes to existing records (with before/after values)
- **DELETE**: Record deletions (with preserved data)
- **VIEW**: Access to sensitive data or reports

Administrative Actions
~~~~~~~~~~~~~~~~~~~~~~

- User role changes
- Permission modifications
- System configuration changes
- Bulk data operations

API Access
~~~~~~~~~~

- All REST API endpoint access
- Authentication token usage
- Rate limiting violations
- API error responses

Audit Data Structure
--------------------

Standard Fields
~~~~~~~~~~~~~~~

All audit logs include these standard fields:

- **timestamp**: When the action occurred
- **user**: Who performed the action (null for anonymous)
- **action**: What type of action (CREATE, UPDATE, DELETE, VIEW, etc.)
- **resource_type**: What kind of resource was affected
- **resource_id**: Specific identifier of the resource
- **ip_address**: Source IP address
- **user_agent**: Browser/client information

Details Field
~~~~~~~~~~~~~

The ``details`` JSON field contains action-specific information:

For CREATE operations
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

    {
      "new_values": {
        "name": "New Application",
        "status": "active",
        "owner": "john.doe"
      }
    }

For UPDATE operations
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

    {
      "changes": {
        "status": {"old": "inactive", "new": "active"},
        "last_updated": {"old": "2025-01-01", "new": "2025-01-15"}
      }
    }

For DELETE operations
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

    {
      "deleted_values": {
        "name": "Removed Application",
        "id": 123,
        "last_status": "inactive"
      }
    }

Audit Log Access
----------------

Web Interface
~~~~~~~~~~~~~

**Location**: Admin interface at ``/admin/inventory/auditlog/``

Features:

- Searchable and filterable audit logs
- Date range filtering
- User-specific activity views
- Resource-type filtering
- Export capabilities

API Access
~~~~~~~~~~

**Endpoint**: ``/api/audit/``

Query parameters:

- ``user``: Filter by user ID
- ``action``: Filter by action type
- ``resource_type``: Filter by resource type
- ``start_date``: Filter from date
- ``end_date``: Filter to date
- ``ip_address``: Filter by IP address

Programmatic Access
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.inventory.models import AuditLog

    # Get all logs for a specific user
    user_logs = AuditLog.objects.filter(user=user)

    # Get all changes to a specific application
    app_logs = AuditLog.objects.filter(
        resource_type='Application',
        resource_id='123'
    )

    # Get all failed login attempts
    failed_logins = AuditLog.objects.filter(
        action='LOGIN_FAILED'
    )

Security Features
-----------------

Data Protection
~~~~~~~~~~~~~~~

- Audit logs are write-only for most users
- Sensitive data is hashed or redacted in logs
- IP addresses can be anonymized for privacy compliance
- Automatic log rotation and archival

Tamper Protection
~~~~~~~~~~~~~~~~~

- Audit logs cannot be modified after creation
- Digital signatures for critical operations
- Checksum validation for log integrity
- Separate database schema with restricted access

Retention Policies
~~~~~~~~~~~~~~~~~~

- Configurable retention periods
- Automatic archival to long-term storage
- Compliance with regulatory requirements
- Secure deletion procedures

Configuration
-------------

Settings
~~~~~~~~

**Location**: ``backend/settings/base.py``

.. code-block:: python

    # Audit logging configuration
    AUDIT_LOGGING = {
        'ENABLED': True,
        'LOG_ANONYMOUS_USERS': False,
        'LOG_VIEW_ACTIONS': True,
        'RETENTION_DAYS': 2555,  # 7 years
        'ANONYMIZE_IP': False,
        'HASH_SENSITIVE_DATA': True
    }

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

- ``AUDIT_LOG_LEVEL``: Set logging verbosity
- ``AUDIT_RETENTION_DAYS``: Override default retention
- ``AUDIT_ANONYMIZE_IP``: Enable IP anonymization

Monitoring and Alerting
------------------------

Log Monitoring
~~~~~~~~~~~~~~

The system monitors audit logs for:

- Unusual access patterns
- Multiple failed login attempts
- Privilege escalation attempts
- Bulk data operations
- After-hours access

Alert Triggers
~~~~~~~~~~~~~~

Automated alerts are sent for:

- Failed authentication spikes
- Administrative action outside business hours
- Bulk data exports
- Suspicious IP address patterns
- Database schema changes

Compliance Features
-------------------

Regulatory Compliance
~~~~~~~~~~~~~~~~~~~~~

The audit system supports:

- **SOX**: Financial data access tracking
- **HIPAA**: Healthcare data access logs
- **GDPR**: Data processing activity logs
- **PCI DSS**: Payment data access monitoring

Report Generation
~~~~~~~~~~~~~~~~~

Available compliance reports:

- User activity summaries
- Data access reports
- Administrative action logs
- Security incident timelines
- Compliance attestation reports

Testing
-------

Audit System Tests
~~~~~~~~~~~~~~~~~~

**Location**: ``backend/apps/inventory/test_audit.py``

Test coverage includes:

- Audit log creation for all CRUD operations
- Middleware functionality
- Decorator behavior
- API endpoint security
- Report generation
- Data retention policies

Running Audit Tests
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Run all audit tests
    python manage.py test apps.inventory.test_audit

    # Run specific audit test categories
    python manage.py test apps.inventory.test_audit.AuditLogModelTests
    python manage.py test apps.inventory.test_audit.AuditMiddlewareTests

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

Missing Audit Logs
^^^^^^^^^^^^^^^^^^^

1. Check if audit logging is enabled in settings
2. Verify middleware is properly configured
3. Check database permissions
4. Review log retention settings

Performance Impact
^^^^^^^^^^^^^^^^^^

1. Monitor database query performance
2. Consider async log writing
3. Implement log batching
4. Archive old logs regularly

Storage Concerns
^^^^^^^^^^^^^^^^

1. Monitor audit log table size
2. Implement proper indexing
3. Configure log rotation
4. Set up archival processes

Debug Commands
~~~~~~~~~~~~~~

.. code-block:: bash

    # Check audit log status
    python manage.py shell -c "from apps.inventory.models import AuditLog; print(f'Total logs: {AuditLog.objects.count()}')"

    # Verify recent activity
    python manage.py shell -c "from apps.inventory.models import AuditLog; print(AuditLog.objects.order_by('-timestamp')[:5])"

    # Check configuration
    python manage.py shell -c "from django.conf import settings; print(settings.AUDIT_LOGGING)"

Best Practices
--------------

Implementation Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Always use audit decorators for sensitive operations
2. Include meaningful context in audit details
3. Test audit functionality with all new features
4. Regularly review audit logs for anomalies
5. Maintain separate audit database permissions

Security Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~

1. Restrict audit log access to authorized personnel
2. Regularly backup audit logs
3. Monitor for audit log tampering attempts
4. Implement log forwarding to SIEM systems
5. Encrypt audit logs at rest

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

1. Use async logging for high-traffic operations
2. Implement proper database indexing
3. Consider log sampling for very high-volume systems
4. Use connection pooling for audit database
5. Monitor and tune query performance

.. note::
   This audit logging system is designed to provide comprehensive tracking while maintaining system performance and security. Regular reviews and updates ensure continued effectiveness and compliance.
