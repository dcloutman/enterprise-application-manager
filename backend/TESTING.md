# Enterprise Application Tracker - Testing Configuration

## Backend Testing

### Test Structure
```
backend/apps/inventory/
├── test_models.py          # Model functionality tests
├── test_api.py             # API endpoint tests  
├── test_audit.py           # Audit logging tests
├── test_documentation.py   # Documentation access tests
└── run_tests.py            # Test runner script
```

### Running Tests

#### Run All Tests
```bash
cd backend
python run_tests.py
```

#### Run Specific Test Suites
```bash
# Model tests only
python run_tests.py --models

# API tests only
python run_tests.py --api

# Audit logging tests only
python run_tests.py --audit

# Documentation access tests only
python run_tests.py --docs
```

#### Test Options
```bash
# Verbose output
python run_tests.py --verbose

# Keep test database (faster subsequent runs)
python run_tests.py --keepdb

# Run with coverage (if coverage.py installed)
python run_tests.py --coverage

# Fast mode (skip slow integration tests)
python run_tests.py --fast
```

### Django Management Commands for Testing
```bash
# Test audit logging system
python manage.py test_audit_logging

# Update documentation access (dry run)
python manage.py update_documentation_access --dry-run

# Update documentation access (actual run)
python manage.py update_documentation_access
```

### Test Database Setup
Tests use a separate test database that is created and destroyed automatically.
For faster subsequent test runs, use `--keepdb` flag.

### Test Coverage Areas

#### Model Tests (`test_models.py`)
- ✅ User profile creation and validation
- ✅ Role-based permission methods
- ✅ Documentation access rules
- ✅ Cloud platform model functionality
- ✅ Server environment model and constraints
- ✅ Application model and lifecycle
- ✅ Language and DataStore models
- ✅ Installation and instance relationships
- ✅ Application dependency relationships
- ✅ Record permission system

#### API Tests (`test_api.py`)
- ✅ Authentication requirements
- ✅ Role-based access control
- ✅ CRUD operations for all models
- ✅ Data validation
- ✅ User management endpoints
- ✅ Integration workflows
- ✅ Error handling

#### Audit Logging Tests (`test_audit.py`)
- ✅ Audit logger initialization
- ✅ User context management
- ✅ Log entry format and content
- ✅ Field change detection
- ✅ Model save triggers
- ✅ Audit mixin integration
- ✅ Log permissions and security
- ✅ Sensitive data handling
- ✅ Bulk operations auditing
- ✅ Management command testing

#### Documentation Access Tests (`test_documentation.py`)
- ✅ Model-level access controls
- ✅ View-level access controls
- ✅ Automatic access assignment
- ✅ Manual access management
- ✅ Role-based access updates
- ✅ Access revocation scenarios
- ✅ Management command functionality
- ✅ Security aspects
- ✅ Session handling

### Test Data and Fixtures
Tests create their own data using `setUp()` methods in each test class.
No external fixtures are required.

### Continuous Integration Recommendations
1. Run tests on every commit
2. Fail builds if any tests fail
3. Generate coverage reports
4. Run tests against multiple Python/Django versions
5. Test database migrations

### Known Test Limitations
- Some tests may skip if API endpoints are not fully implemented
- Integration tests depend on proper URL configuration
- Audit logging tests may need additional setup for file handling
- Documentation access tests depend on template and middleware setup

### Test Environment Variables
```bash
# Django settings for testing
export DJANGO_SETTINGS_MODULE=app_tracker.settings
export DJANGO_DEBUG=False

# Test database (optional, uses SQLite by default)
export TEST_DATABASE_URL=sqlite:///test_db.sqlite3

# Audit log directory for testing
export AUDIT_LOG_DIR=/tmp/test_audit_logs
```

### Troubleshooting Tests
1. **Import Errors**: Ensure Python path includes backend directory
2. **Database Errors**: Check database permissions and settings
3. **Missing Dependencies**: Install test requirements
4. **Lint Errors**: These are expected and don't affect test functionality
5. **Skipped Tests**: Some tests skip if endpoints/features aren't implemented

### Performance Testing
For performance testing of the system:
```bash
# Use Django's test framework with timing
python run_tests.py --verbose

# For load testing, consider tools like:
# - locust (for API load testing)
# - django-debug-toolbar (for query analysis)
# - pytest-benchmark (for micro-benchmarks)
```
