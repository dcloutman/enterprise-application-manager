Test Suite Documentation
========================

Overview
--------

The Enterprise Application Tracker (EAT) includes a comprehensive test suite that covers both backend and frontend components. This document explains how to run the tests, describes the test architecture, and outlines how to maintain and extend the test infrastructure.

Test Architecture
-----------------

Backend Testing (Django)
~~~~~~~~~~~~~~~~~~~~~~~~

All backend tests are located in the ``backend/apps/inventory/`` directory. The backend test suite uses Django's built-in testing framework, along with additional tools for mocking and coverage analysis. Tests are organized by functionality, including models, API endpoints, audit logging, and documentation access.

Model tests verify the behavior of Django models such as UserProfile, Application, Server, TechStack, and AuditLog. API tests ensure that authentication, CRUD operations, permissions, error handling, and data validation work as expected. Audit tests confirm that audit logs are generated correctly and remain immutable. Documentation tests check that access to documentation is properly controlled and that API documentation is accurate.

Frontend Testing (SvelteKit)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Frontend tests are found in the ``frontend/src/`` and ``frontend/tests/`` directories. The frontend test suite uses Vitest for unit tests, Playwright for end-to-end tests, and Testing Library for component testing. Unit tests focus on components, utility functions, state management, and data transformation. End-to-end tests simulate user workflows, verify API integration, and check the user interface across different devices and scenarios.

Running Tests
-------------

To run frontend unit tests, use the following command inside the frontend container:

.. code-block:: bash

    docker exec app-tracker-app-1 bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm test -- --run"

For coverage reports, run:

.. code-block:: bash

    docker exec app-tracker-app-1 bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm run test:coverage -- --run"

To execute backend tests, use:

.. code-block:: bash

    docker exec app-tracker-app-1 bash -c "cd /app/backend && python3.12 run_tests.py"

You can also run specific backend test categories by passing arguments such as ``--models``, ``--api``, or ``--audit`` to the test runner.

A comprehensive test suite can be executed using the ``./bin/run_comprehensive_tests.sh`` script. This script manages container cleanup, enforces timeouts, and generates detailed reports.

Test Configuration
------------------

Frontend tests are configured using ``vitest.config.ts`` and ``playwright.config.ts``. These files specify which files to include, the test environment, and coverage settings. Backend tests use a dedicated test database and specific settings to ensure isolation and reproducibility.

Coverage Reports
----------------

Coverage reports for the frontend are generated in the ``frontend/coverage/`` directory, while backend coverage reports are saved in ``backend/htmlcov/``. These reports provide insight into which parts of the codebase are exercised by the tests.

Continuous Integration
----------------------

The test suite is integrated with GitHub Actions and is designed to run in containerized environments. This ensures that tests are executed in a consistent and reproducible manner, both locally and in CI/CD pipelines.

Test Data Management
--------------------

Backend tests use fixtures located in ``backend/apps/inventory/fixtures/`` to provide sample data. The test database is isolated and cleaned up automatically after each test run. Frontend tests use mock data to simulate API responses and various application states.

Writing and Maintaining Tests
-----------------------------

When adding new tests, follow the existing structure for backend and frontend tests. Backend tests should use Django's TestCase or APITestCase classes, while frontend tests should use Vitest or Playwright as appropriate. Regularly review and update tests to ensure they remain effective as the application evolves.

Debugging and Troubleshooting
----------------------------

If you encounter issues with the test suite, you can run individual tests with verbose output for more detailed information. Ensure that your Docker environment is clean and that all dependencies are up to date.

Performance and Security Testing
-------------------------------

The test suite includes support for performance and security testing using tools such as Locust, OWASP ZAP, and Bandit. These tests help ensure that the application remains performant and secure as it grows.

Conclusion
----------

The EAT test suite is designed to provide thorough coverage of both backend and frontend functionality. By following the guidelines in this document, you can run, maintain, and extend the tests to ensure the continued reliability of the application.
