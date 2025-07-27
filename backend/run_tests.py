#!/usr/bin/env python3
"""
Comprehensive test runner for the Enterprise Application Tracker backend.

This script runs all test suites and provides detailed reporting.

Usage:
    python run_tests.py [options]

Options:
    --verbose    : Enable verbose output
    --coverage   : Run with coverage reporting
    --fast       : Skip slow integration tests
    --models     : Run only model tests
    --api        : Run only API tests
    --audit      : Run only audit logging tests
    --docs       : Run only documentation access tests
    --help       : Show this help message
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import argparse
import time
from io import StringIO

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def setup_django():
    """Set up Django for testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_tracker.settings')
    django.setup()

def run_test_suite(test_labels, verbosity=1, keepdb=False):
    """Run a specific test suite"""
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity, keepdb=keepdb)
    
    start_time = time.time()
    failures = test_runner.run_tests(test_labels)
    end_time = time.time()
    
    return failures, end_time - start_time

def print_test_summary(test_name, failures, duration):
    """Print test summary"""
    status = "PASS" if failures == 0 else "FAIL"
    print(f"\n{test_name}: {status} ({failures} failures, {duration:.2f}s)")
    
    if failures > 0:
        print(f"  FAIL: {failures} test(s) failed")
    else:
        print(f"  PASS: All tests passed")

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Run EAT backend tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Run with coverage')
    parser.add_argument('--fast', '-f', action='store_true', help='Skip slow tests')
    parser.add_argument('--models', '-m', action='store_true', help='Run only model tests')
    parser.add_argument('--api', '-a', action='store_true', help='Run only API tests')
    parser.add_argument('--audit', action='store_true', help='Run only audit tests')
    parser.add_argument('--docs', '-d', action='store_true', help='Run only documentation tests')
    parser.add_argument('--keepdb', '-k', action='store_true', help='Preserve test database')
    
    args = parser.parse_args()
    
    # Set up Django
    setup_django()
    
    verbosity = 2 if args.verbose else 1
    total_failures = 0
    total_duration = 0
    
    print("Starting Enterprise Application Tracker Test Suite")
    print("=" * 60)
    
    # Define test suites
    test_suites = {}
    
    if args.models or not any([args.api, args.audit, args.docs]):
        test_suites['Model Tests'] = ['apps.inventory.test_models']
    
    if args.api or not any([args.models, args.audit, args.docs]):
        test_suites['API Tests'] = ['apps.inventory.test_api']
    
    if args.audit or not any([args.models, args.api, args.docs]):
        test_suites['Audit Logging Tests'] = ['apps.inventory.test_audit']
    
    if args.docs or not any([args.models, args.api, args.audit]):
        test_suites['Documentation Access Tests'] = ['apps.inventory.test_documentation']
    
    # If no specific test type requested, run all
    if not any([args.models, args.api, args.audit, args.docs]):
        test_suites = {
            'Model Tests': ['apps.inventory.test_models'],
            'API Tests': ['apps.inventory.test_api'],
            'Audit Logging Tests': ['apps.inventory.test_audit'],
            'Documentation Access Tests': ['apps.inventory.test_documentation']
        }
    
    # Run test suites
    for suite_name, test_labels in test_suites.items():
        print(f"\nRunning {suite_name}...")
        print("-" * 40)
        
        try:
            failures, duration = run_test_suite(test_labels, verbosity, args.keepdb)
            print_test_summary(suite_name, failures, duration)
            
            total_failures += failures
            total_duration += duration
            
        except Exception as e:
            print(f"ERROR: Error running {suite_name}: {e}")
            total_failures += 1
    
    # Print overall summary
    print("\n" + "=" * 60)
    print("OVERALL TEST SUMMARY")
    print("=" * 60)
    
    if total_failures == 0:
        print("ALL TESTS PASSED!")
        print(f"Total duration: {total_duration:.2f}s")
        exit_code = 0
    else:
        print(f"FAILED: {total_failures} TEST SUITE(S) FAILED")
        print(f"Total duration: {total_duration:.2f}s")
        exit_code = 1
    
    # Coverage report
    if args.coverage:
        print("\nCoverage Report")
        print("-" * 20)
        print("Coverage reporting would be implemented here")
        print("Install coverage.py and configure for detailed reports")
    
    # Recommendations
    print("\nRECOMMENDATIONS")
    print("-" * 20)
    if total_failures > 0:
        print("• Fix failing tests before deploying to production")
        print("• Review test output above for specific failure details")
    
    print("• Run tests regularly during development")
    print("• Add new tests when implementing new features")
    print("• Consider setting up continuous integration")
    
    if not args.coverage:
        print("• Use --coverage flag to analyze test coverage")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
