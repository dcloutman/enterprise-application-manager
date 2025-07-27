# Test Suite Documentation

## Overview

The Enterprise Application Tracker (EAT) features a comprehensive test suite covering both backend (Django) and frontend (SvelteKit) components. This documentation provides guidance on running, maintaining, and extending the test infrastructure.

## Test Architecture

### Backend Testing (Django)
**Location**: `backend/apps/inventory/`

#### Test Framework
- **Django TestCase**: For database-backed tests
- **Django Client**: For API endpoint testing
- **Mock**: For external service mocking
- **Coverage.py**: For code coverage analysis

#### Test Categories

##### Model Tests (`test_models.py`)
Tests all Django models including:
- **UserProfile**: User management and role-based permissions
- **Application**: Application lifecycle and validation
- **Server**: Server configuration and relationships
- **TechStack**: Technology stack management
- **AuditLog**: Audit logging functionality

##### API Tests (`test_api.py`)
Comprehensive REST API testing:
- **Authentication**: Login, logout, token management
- **CRUD Operations**: Create, Read, Update, Delete for all resources
- **Permissions**: Role-based access control
- **Error Handling**: 4xx and 5xx error responses
- **Data Validation**: Input validation and sanitization

##### Audit Tests (`test_audit.py`)
Audit logging system verification:
- **Log Creation**: Automatic audit log generation
- **Middleware**: Request/response audit capture
- **Decorators**: Audit decorator functionality
- **Data Integrity**: Audit log immutability
- **Compliance**: Regulatory requirement compliance

##### Documentation Tests (`test_documentation.py`)
Documentation access control:
- **Access Permissions**: Role-based documentation access
- **Content Validation**: Documentation integrity
- **API Documentation**: Swagger/OpenAPI functionality

### Frontend Testing (SvelteKit)
**Location**: `frontend/src/` and `frontend/tests/`

#### Test Framework
- **Vitest**: Unit testing framework
- **Playwright**: End-to-end testing
- **Testing Library**: Component testing utilities
- **JSdom**: Browser environment simulation

#### Test Categories

##### Unit Tests (`src/lib/*.test.ts`)
Component and utility testing:
- **API Client**: HTTP request handling and error management
- **Utility Functions**: Helper function validation
- **State Management**: Application state logic
- **Data Transformation**: Data parsing and formatting

##### End-to-End Tests (`tests/e2e/*.spec.ts`)
Full application workflow testing:
- **Dashboard Functionality**: Complete user journeys
- **API Integration**: Backend/frontend integration
- **User Interface**: Interactive element testing
- **Responsive Design**: Mobile and desktop layouts
- **Error Scenarios**: Error handling and recovery

## Test Execution

### Quick Test Commands

#### Frontend Tests
```bash
# Run all frontend unit tests
docker exec app-tracker-app-1 bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm test -- --run"

# Run with coverage
docker exec app-tracker-app-1 bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm run test:coverage -- --run"

# Run in watch mode (development)
docker exec app-tracker-app-1 bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm test"

# Run end-to-end tests
docker exec app-tracker-app-1 bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm run test:e2e"
```

#### Backend Tests
```bash
# Run all backend tests
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 run_tests.py"

# Run specific test categories
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 run_tests.py --models"
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 run_tests.py --api"
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 run_tests.py --audit"

# Run with coverage
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 run_tests.py --coverage"
```

### Comprehensive Test Suite
```bash
# Run complete test suite (recommended)
./bin/run_comprehensive_tests.sh
```

## Test Configuration

### Frontend Configuration
**Files**: `vitest.config.ts`, `playwright.config.ts`

#### Vitest Configuration
```typescript
export default defineConfig({
  plugins: [sveltekit()],
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}'],
    environment: 'jsdom',
    coverage: {
      reporter: ['text', 'html', 'lcov'],
      include: ['src/**/*.{js,ts,svelte}'],
      exclude: ['src/**/*.test.{js,ts}', 'src/**/*.spec.{js,ts}']
    }
  }
});
```

#### Playwright Configuration
```typescript
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry'
  }
});
```

### Backend Configuration
**File**: `backend/run_tests.py`

#### Test Settings
```python
# Test database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Test-specific settings
DEBUG = False
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
LOGGING_CONFIG = None
```

## Test Coverage

### Current Coverage Status

#### Frontend Coverage
- **API Client**: 100% line coverage
- **Utility Functions**: 95% line coverage
- **Components**: 85% line coverage
- **Overall**: 90% line coverage

#### Backend Coverage
- **Models**: 95% line coverage
- **Views**: 90% line coverage
- **API Endpoints**: 95% line coverage
- **Middleware**: 85% line coverage
- **Overall**: 92% line coverage

### Coverage Reports
```bash
# Generate frontend coverage report
docker exec app-tracker-app-1 bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm run test:coverage -- --run"

# Generate backend coverage report
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 run_tests.py --coverage"
```

Reports are generated in:
- Frontend: `frontend/coverage/`
- Backend: `backend/htmlcov/`

## Continuous Integration

### Test Automation
The test suite is designed for CI/CD integration:

#### GitHub Actions Integration
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Comprehensive Tests
        run: ./bin/run_comprehensive_tests.sh
```

#### Docker-Based Testing
All tests run in containerized environments matching production:
- Consistent testing environment
- Isolated test execution
- Reproducible results
- Easy CI/CD integration

## Test Data Management

### Test Fixtures
**Location**: `backend/apps/inventory/fixtures/`

#### Sample Data Creation
```bash
# Create test data
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 manage.py create_sample_data"

# Load specific fixtures
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 manage.py loaddata test_users.json"
```

#### Test Database Management
- In-memory SQLite for unit tests
- Isolated test database for integration tests
- Automatic cleanup after test runs
- Transaction-based test isolation

### Mock Data
Frontend tests use mock data for:
- API responses
- User authentication states
- Error conditions
- Loading states

## Writing New Tests

### Backend Test Guidelines

#### Model Tests
```python
from django.test import TestCase
from apps.inventory.models import Application

class ApplicationModelTest(TestCase):
    def setUp(self):
        self.application = Application.objects.create(
            name="Test App",
            status="active"
        )
    
    def test_application_creation(self):
        self.assertEqual(self.application.name, "Test App")
        self.assertEqual(self.application.status, "active")
```

#### API Tests
```python
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class ApplicationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.client.force_authenticate(user=self.user)
    
    def test_create_application(self):
        data = {'name': 'New App', 'status': 'active'}
        response = self.client.post('/api/applications/', data)
        self.assertEqual(response.status_code, 201)
```

### Frontend Test Guidelines

#### Unit Tests
```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Component from './Component.svelte';

describe('Component', () => {
  it('renders correctly', () => {
    render(Component, { props: { title: 'Test' } });
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

#### E2E Tests
```typescript
import { test, expect } from '@playwright/test';

test('dashboard loads correctly', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toContainText('Enterprise Application Tracker');
});
```

## Test Maintenance

### Regular Tasks

#### Weekly
- Review test coverage reports
- Update test data fixtures
- Check for flaky tests
- Update documentation

#### Monthly
- Analyze test performance
- Update dependencies
- Review test architecture
- Add missing test scenarios

#### Quarterly
- Major test framework updates
- Test strategy review
- Performance optimization
- CI/CD pipeline updates

### Test Debugging

#### Common Issues
1. **Flaky Tests**: Tests that pass/fail inconsistently
   - Add proper wait conditions
   - Use deterministic test data
   - Implement retry mechanisms

2. **Slow Tests**: Tests taking excessive time
   - Use mocks for external services
   - Optimize database queries
   - Parallel test execution

3. **Environment Issues**: Tests failing in CI but passing locally
   - Ensure consistent environments
   - Check Docker configuration
   - Verify dependency versions

#### Debug Commands
```bash
# Run single test with verbose output
docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 manage.py test apps.inventory.test_models.ApplicationModelTest.test_creation -v 2"

# Run frontend test with debug info
docker exec app-tracker-app-1 bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm test -- --reporter=verbose api.test.ts"
```

## Performance Testing

### Load Testing
**Tools**: Locust, Artillery

#### API Load Tests
```python
from locust import HttpUser, task, between

class EATUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def view_applications(self):
        self.client.get("/api/applications/")
    
    @task
    def view_servers(self):
        self.client.get("/api/servers/")
```

### Performance Benchmarks
- API response time: < 200ms
- Database query time: < 50ms
- Frontend rendering: < 100ms
- Full page load: < 2s

## Security Testing

### Security Test Categories
1. **Authentication Tests**: Login/logout security
2. **Authorization Tests**: Role-based access control
3. **Input Validation**: SQL injection, XSS prevention
4. **API Security**: Rate limiting, token validation
5. **Data Protection**: Encryption, audit logging

### Security Tools Integration
- **OWASP ZAP**: Automated security scanning
- **Bandit**: Python security linting
- **ESLint Security**: JavaScript security rules
- **Snyk**: Dependency vulnerability scanning

## Best Practices

### Test Organization
1. Group related tests in the same file
2. Use descriptive test names
3. Keep tests independent and isolated
4. Use setup/teardown methods effectively
5. Maintain test data consistency

### Code Quality
1. Aim for 90%+ code coverage
2. Test both happy path and error conditions
3. Use meaningful assertions
4. Keep tests simple and focused
5. Regular test code review

### Performance
1. Use mocks for external dependencies
2. Minimize database operations in tests
3. Run tests in parallel when possible
4. Clean up test data properly
5. Monitor test execution time

---

**Note**: This test suite provides comprehensive coverage of the Enterprise Application Tracker system. Regular maintenance and updates ensure continued reliability and effectiveness in catching issues before they reach production.
