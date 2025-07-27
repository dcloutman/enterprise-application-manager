API Authentication
==================

The Enterprise Application Tracker API uses multiple authentication methods depending on the access pattern and security requirements.

Authentication Methods
----------------------

**1. Session Authentication**

Used for web browser access and same-origin requests:

.. code-block:: javascript

    // Login via web form
    fetch('/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            username: 'your-username',
            password: 'your-password'
        })
    });

**2. Basic Authentication**

Used for API clients and simple integrations:

.. code-block:: bash

    # Basic auth with curl
    curl -u username:password https://your-domain.com/api/servers/

.. code-block:: python

    # Basic auth with Python requests
    import requests
    from requests.auth import HTTPBasicAuth

    response = requests.get(
        'https://your-domain.com/api/servers/',
        auth=HTTPBasicAuth('username', 'password')
    )

**3. Token Authentication**

Recommended for API integrations and service-to-service access:

.. code-block:: bash

    # Get token
    curl -X POST https://your-domain.com/api/auth/token/ \
         -H "Content-Type: application/json" \
         -d '{"username": "your-username", "password": "your-password"}'

    # Use token
    curl -H "Authorization: Token your-token-here" \
         https://your-domain.com/api/servers/

.. code-block:: python

    # Token auth with Python
    import requests

    # Get token
    response = requests.post('https://your-domain.com/api/auth/token/', {
        'username': 'your-username',
        'password': 'your-password'
    })
    token = response.json()['token']

    # Use token
    headers = {'Authorization': f'Token {token}'}
    response = requests.get('https://your-domain.com/api/servers/', headers=headers)

API Permissions
---------------

API access is controlled by the same role-based permission system as the web interface:

**Permission Levels by Role**

.. list-table::
   :widths: 25 20 20 20 15
   :header-rows: 1

   * - **Endpoint Category**
     - **App Admin**
     - **Sys Manager**
     - **Technician**
     - **Biz Manager/User**
   * - User Management
     - Full CRUD
     - Read Only
     - No Access
     - No Access
   * - Server Management
     - Full CRUD
     - Full CRUD
     - Limited Edit
     - Read Only
   * - Application Management
     - Full CRUD
     - Full CRUD
     - Limited Edit
     - Read Only
   * - System Notes
     - Full Access
     - Full Access
     - No Access
     - No Access
   * - Reporting
     - All Reports
     - Technical Reports
     - Limited Reports
     - Business Reports

**HTTP Status Codes for Permissions**

* ``200 OK`` - Request successful
* ``401 Unauthorized`` - Authentication required
* ``403 Forbidden`` - Insufficient permissions
* ``404 Not Found`` - Resource not found or no permission to view

Rate Limiting
-------------

The API implements rate limiting to prevent abuse:

**Default Limits**

* **Authenticated Users**: 10,000 requests per hour
* **Unauthenticated**: 100 requests per hour
* **Administrative Endpoints**: 1,000 requests per hour

**Rate Limit Headers**

.. code-block:: text

    X-RateLimit-Limit: 10000
    X-RateLimit-Remaining: 9995
    X-RateLimit-Reset: 1609459200

**Handling Rate Limits**

.. code-block:: python

    import time
    import requests

    def api_request_with_retry(url, headers, max_retries=3):
        for attempt in range(max_retries):
            response = requests.get(url, headers=headers)
            
            if response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                continue
                
            return response
        
        raise Exception("Max retries exceeded")

API Versioning
--------------

The API uses URL-based versioning:

.. code-block:: bash

    # Current version (v1)
    curl https://your-domain.com/api/v1/servers/
    
    # When v2 is released
    curl https://your-domain.com/api/v2/servers/

**Version Support Policy**

* Current version: Full support and new features
* Previous version: Security updates and bug fixes for 12 months
* Deprecated version: 6-month notice before removal

Error Responses
---------------

The API returns consistent error responses in JSON format:

**Standard Error Format**

.. code-block:: json

    {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": {
                "field_name": ["This field is required."]
            },
            "timestamp": "2025-07-27T15:30:00Z",
            "request_id": "req_123456789"
        }
    }

**Common Error Codes**

* ``AUTHENTICATION_REQUIRED`` - User must authenticate
* ``PERMISSION_DENIED`` - Insufficient permissions
* ``VALIDATION_ERROR`` - Invalid input data
* ``NOT_FOUND`` - Resource not found
* ``RATE_LIMITED`` - Too many requests
* ``SERVER_ERROR`` - Internal server error

**Error Handling Example**

.. code-block:: python

    import requests
    import json

    def handle_api_response(response):
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 401:
            raise Exception("Authentication required")
        
        elif response.status_code == 403:
            raise Exception("Permission denied")
        
        elif response.status_code == 400:
            error_data = response.json()
            raise Exception(f"Validation error: {error_data['error']['message']}")
        
        else:
            response.raise_for_status()

Security Considerations
-----------------------

**HTTPS Required**

All API access must use HTTPS in production:

.. code-block:: python

    # Good - uses HTTPS
    requests.get('https://your-domain.com/api/servers/')
    
    # Bad - HTTP will be redirected or blocked
    requests.get('http://your-domain.com/api/servers/')

**Token Security**

* Store tokens securely (not in code or logs)
* Use environment variables or secure credential stores
* Rotate tokens regularly
* Revoke unused tokens

.. code-block:: python

    import os
    import requests

    # Good - token from environment
    token = os.environ['EAT_API_TOKEN']
    headers = {'Authorization': f'Token {token}'}

**Request Signing (Advanced)**

For high-security environments, implement request signing:

.. code-block:: python

    import hmac
    import hashlib
    import time

    def sign_request(method, url, body, secret_key):
        timestamp = str(int(time.time()))
        string_to_sign = f"{method}\n{url}\n{body}\n{timestamp}"
        signature = hmac.new(
            secret_key.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'X-EAT-Timestamp': timestamp,
            'X-EAT-Signature': signature
        }

API Testing
-----------

**Using curl**

.. code-block:: bash

    # Test authentication
    curl -u admin:password https://your-domain.com/api/auth/profile/
    
    # Test permissions
    curl -u technician:password https://your-domain.com/api/users/
    # Should return 403 Forbidden
    
    # Test data access
    curl -u sysmanager:password https://your-domain.com/api/servers/

**Using Python requests**

.. code-block:: python

    import requests
    from requests.auth import HTTPBasicAuth

    # Base configuration
    BASE_URL = 'https://your-domain.com/api'
    auth = HTTPBasicAuth('username', 'password')

    # Test endpoints
    endpoints = [
        '/auth/profile/',
        '/servers/',
        '/applications/',
        '/users/'  # May fail with 403 for non-admins
    ]

    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}", auth=auth)
        print(f"{endpoint}: {response.status_code}")

**Using Postman**

1. **Set up authentication**:
   - Type: Basic Auth
   - Username/Password: Your credentials

2. **Create environment variables**:
   - ``base_url``: https://your-domain.com/api
   - ``username``: Your username
   - ``password``: Your password

3. **Test collection**:
   - Import the provided Postman collection
   - Run automated tests
   - Verify responses and status codes

**Automated Testing**

.. code-block:: python

    import unittest
    import requests
    from requests.auth import HTTPBasicAuth

    class APITestCase(unittest.TestCase):
        def setUp(self):
            self.base_url = 'https://your-domain.com/api'
            self.admin_auth = HTTPBasicAuth('admin', 'admin_password')
            self.user_auth = HTTPBasicAuth('user', 'user_password')

        def test_authentication_required(self):
            response = requests.get(f"{self.base_url}/servers/")
            self.assertEqual(response.status_code, 401)

        def test_admin_access(self):
            response = requests.get(f"{self.base_url}/users/", auth=self.admin_auth)
            self.assertEqual(response.status_code, 200)

        def test_user_permissions(self):
            response = requests.get(f"{self.base_url}/users/", auth=self.user_auth)
            self.assertEqual(response.status_code, 403)

SDK and Libraries
-----------------

**Python SDK (Recommended)**

.. code-block:: python

    # Install the SDK
    pip install eat-api-client

    # Use the SDK
    from eat_api import EATClient

    client = EATClient(
        base_url='https://your-domain.com',
        username='your-username',
        password='your-password'
    )

    # Get servers
    servers = client.servers.list()
    
    # Create application
    app = client.applications.create({
        'name': 'My Application',
        'description': 'Application description',
        'lifecycle_stage': 'development'
    })

**JavaScript/Node.js SDK**

.. code-block:: javascript

    // Install the SDK
    npm install eat-api-client

    // Use the SDK
    const EATClient = require('eat-api-client');

    const client = new EATClient({
        baseURL: 'https://your-domain.com',
        username: 'your-username',
        password: 'your-password'
    });

    // Get servers
    client.servers.list()
        .then(servers => console.log(servers))
        .catch(error => console.error(error));

**Custom Integration Example**

.. code-block:: python

    class EATAPIClient:
        def __init__(self, base_url, username, password):
            self.base_url = base_url.rstrip('/')
            self.auth = HTTPBasicAuth(username, password)
            self.session = requests.Session()
            self.session.auth = self.auth

        def get(self, endpoint):
            url = f"{self.base_url}/api{endpoint}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()

        def post(self, endpoint, data):
            url = f"{self.base_url}/api{endpoint}"
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()

        def servers(self):
            return self.get('/servers/')

        def create_application(self, app_data):
            return self.post('/applications/', app_data)
