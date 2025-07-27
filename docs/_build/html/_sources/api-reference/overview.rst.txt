API Reference
=============

This section provides comprehensive documentation for all API endpoints in the Enterprise Application Tracker.

.. toctree::
   :maxdepth: 2

   authentication

Base URL
--------

All API endpoints are relative to the base URL:

.. code-block::

    https://your-domain.com/api/

Authentication
--------------

All API endpoints require authentication except where noted. See :doc:`authentication` for detailed authentication methods.

Standard Response Format
------------------------

All API responses follow a consistent format:

**Success Response (2xx)**

.. code-block:: json

    {
        "status": "success",
        "data": {
            // Response data here
        },
        "meta": {
            "pagination": {
                "count": 100,
                "next": "https://api.example.com/endpoint?page=2",
                "previous": null,
                "page_size": 20
            }
        }
    }

**Error Response (4xx/5xx)**

.. code-block:: json

    {
        "status": "error",
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": {
                "name": ["This field is required."],
                "email": ["Enter a valid email address."]
            }
        }
    }

HTTP Status Codes
-----------------

The API uses standard HTTP status codes:

.. list-table::
   :widths: 10 20 70
   :header-rows: 1

   * - **Code**
     - **Status**
     - **Description**
   * - 200
     - OK
     - Request successful
   * - 201
     - Created
     - Resource created successfully
   * - 204
     - No Content
     - Request successful, no content returned
   * - 400
     - Bad Request
     - Invalid request data
   * - 401
     - Unauthorized
     - Authentication required
   * - 403
     - Forbidden
     - Insufficient permissions
   * - 404
     - Not Found
     - Resource not found
   * - 409
     - Conflict
     - Resource conflict (e.g., duplicate name)
   * - 422
     - Unprocessable Entity
     - Validation error
   * - 429
     - Too Many Requests
     - Rate limit exceeded
   * - 500
     - Internal Server Error
     - Server error

Error Codes
-----------

Custom error codes provide specific error information:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - **Error Code**
     - **Description**
   * - VALIDATION_ERROR
     - Input validation failed
   * - AUTHENTICATION_FAILED
     - Invalid credentials
   * - PERMISSION_DENIED
     - Insufficient permissions for operation
   * - RESOURCE_NOT_FOUND
     - Requested resource does not exist
   * - DUPLICATE_RESOURCE
     - Resource with same identifier already exists
   * - RATE_LIMIT_EXCEEDED
     - Too many requests from client
   * - MAINTENANCE_MODE
     - System in maintenance mode
   * - INVALID_TOKEN
     - Authentication token is invalid or expired

Pagination
----------

List endpoints support pagination with the following parameters:

**Query Parameters**

- ``page`` (integer): Page number (default: 1)
- ``page_size`` (integer): Items per page (default: 20, max: 100)

**Example Request**

.. code-block:: text

    GET /api/applications/?page=2&page_size=50
    Authorization: Bearer your-token-here

**Example Response**

.. code-block:: json

    {
        "status": "success",
        "data": {
            "results": [
                // Array of resources
            ]
        },
        "meta": {
            "pagination": {
                "count": 150,
                "next": "https://api.example.com/api/applications/?page=3&page_size=50",
                "previous": "https://api.example.com/api/applications/?page=1&page_size=50",
                "page": 2,
                "page_size": 50,
                "num_pages": 3
            }
        }
    }

Filtering and Searching
-----------------------

Most list endpoints support filtering and searching:

**Common Filter Parameters**

- ``search`` (string): Full-text search across relevant fields
- ``created_after`` (datetime): Filter by creation date
- ``created_before`` (datetime): Filter by creation date
- ``modified_after`` (datetime): Filter by modification date
- ``modified_before`` (datetime): Filter by modification date
- ``created_by`` (integer): Filter by creator user ID
- ``is_active`` (boolean): Filter by active status

**Example Request**

.. code-block:: text

    GET /api/applications/?search=web&created_after=2024-01-01&is_active=true
    Authorization: Bearer your-token-here

Sorting
-------

List endpoints support sorting with the ``ordering`` parameter:

**Example Requests**

.. code-block:: text

    # Sort by name ascending
    GET /api/applications/?ordering=name
    
    # Sort by creation date descending
    GET /api/applications/?ordering=-created_date
    
    # Multiple sort fields
    GET /api/applications/?ordering=name,-created_date

Field Selection
---------------

Use the ``fields`` parameter to request specific fields only:

**Example Request**

.. code-block:: text

    GET /api/applications/?fields=id,name,description,is_active
    Authorization: Bearer your-token-here

**Example Response**

.. code-block:: json

    {
        "status": "success",
        "data": {
            "results": [
                {
                    "id": 1,
                    "name": "Customer Portal",
                    "description": "Web application for customer management",
                    "is_active": true
                }
            ]
        }
    }

Bulk Operations
---------------

Some endpoints support bulk operations for efficiency:

**Bulk Create**

.. code-block:: text

    POST /api/applications/bulk/
    Content-Type: application/json
    Authorization: Bearer your-token-here

    {
        "operations": [
            {
                "name": "App 1",
                "description": "First application"
            },
            {
                "name": "App 2", 
                "description": "Second application"
            }
        ]
    }

**Bulk Update**

.. code-block:: text

    PATCH /api/applications/bulk/
    Content-Type: application/json
    Authorization: Bearer your-token-here

    {
        "operations": [
            {
                "id": 1,
                "is_active": false
            },
            {
                "id": 2,
                "description": "Updated description"
            }
        ]
    }

**Bulk Delete**

.. code-block:: text

    DELETE /api/applications/bulk/
    Content-Type: application/json
    Authorization: Bearer your-token-here

    {
        "ids": [1, 2, 3, 4, 5]
    }

Rate Limiting
-------------

API endpoints are rate limited to prevent abuse:

.. list-table::
   :widths: 30 35 35
   :header-rows: 1

   * - **User Role**
     - **Requests per Minute**
     - **Burst Limit**
   * - Business User
     - 60
     - 120
   * - Business Manager
     - 120
     - 240
   * - Technician
     - 180
     - 360
   * - Systems Manager
     - 300
     - 600
   * - Application Admin
     - 600
     - 1200

**Rate Limit Headers**

Responses include rate limit information:

.. code-block:: text

    HTTP/1.1 200 OK
    X-RateLimit-Limit: 60
    X-RateLimit-Remaining: 45
    X-RateLimit-Reset: 1640995200

When rate limit is exceeded:

.. code-block:: text

    HTTP/1.1 429 Too Many Requests
    X-RateLimit-Limit: 60
    X-RateLimit-Remaining: 0
    X-RateLimit-Reset: 1640995200
    Retry-After: 60

    {
        "status": "error",
        "error": {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Rate limit exceeded. Try again in 60 seconds."
        }
    }

Webhooks
--------

The system supports webhooks for real-time notifications:

**Webhook Events**

- ``application.created``
- ``application.updated``
- ``application.deleted``
- ``server.created``
- ``server.updated``
- ``server.deleted``
- ``user.created``
- ``user.updated``
- ``user.role_changed``

**Webhook Payload**

.. code-block:: json

    {
        "event": "application.created",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "id": 123,
            "name": "New Application",
            "created_by": {
                "id": 45,
                "username": "john.doe"
            }
        },
        "webhook": {
            "id": "webhook_123",
            "url": "https://your-server.com/webhook"
        }
    }

**Webhook Configuration**

.. code-block:: text

    POST /api/webhooks/
    Content-Type: application/json
    Authorization: Bearer your-token-here

    {
        "url": "https://your-server.com/webhook",
        "events": ["application.created", "application.updated"],
        "is_active": true,
        "secret": "your-webhook-secret"
    }

API Versioning
--------------

The API uses header-based versioning:

.. code-block:: text

    GET /api/applications/
    Accept: application/json; version=1.0
    Authorization: Bearer your-token-here

**Supported Versions**

- ``1.0`` (current): Current stable version
- ``0.9`` (deprecated): Legacy version, will be removed in 6 months

**Version Compatibility**

When no version is specified, the latest stable version is used. Breaking changes will result in a new major version.

SDK and Client Libraries
-------------------------

Official SDKs are available for popular programming languages:

**Python SDK**

.. code-block:: bash

    pip install app-tracker-sdk

.. code-block:: python

    from app_tracker import APIClient

    client = APIClient(
        base_url='https://your-domain.com/api/',
        token='your-auth-token'
    )

    # List applications
    applications = client.applications.list()

    # Get specific application
    app = client.applications.get(id=123)

    # Create new application
    new_app = client.applications.create({
        'name': 'My Application',
        'description': 'Application description'
    })

**JavaScript SDK**

.. code-block:: bash

    npm install @yourorg/app-tracker-sdk

.. code-block:: javascript

    import { APIClient } from '@yourorg/app-tracker-sdk';

    const client = new APIClient({
        baseURL: 'https://your-domain.com/api/',
        token: 'your-auth-token'
    });

    // List applications
    const applications = await client.applications.list();

    // Get specific application
    const app = await client.applications.get(123);

    // Create new application
    const newApp = await client.applications.create({
        name: 'My Application',
        description: 'Application description'
    });

Testing and Development
-----------------------

**API Testing**

Use the interactive API documentation at ``/api/docs/`` for testing endpoints.

**Development Environment**

For development, use the test server:

.. code-block::

    https://dev.your-domain.com/api/

**Mock Data**

Test endpoints with sample data:

.. code-block:: text

    GET /api/test/sample-data/
    Authorization: Bearer your-test-token

This returns sample data for all resource types for testing purposes.

**API Health Check**

Monitor API health:

.. code-block:: text

    GET /api/health/

.. code-block:: json

    {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z",
        "services": {
            "database": "healthy",
            "cache": "healthy",
            "storage": "healthy"
        },
        "version": "0.0.1"
    }
