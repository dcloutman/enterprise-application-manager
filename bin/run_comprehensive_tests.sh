#!/bin/bash

# Enterprise Application Tracker (EAT) - Comprehensive Test Suite
# This script runs the complete test suite for both backend and frontend components

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$PROJECT_ROOT/tmp"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
TEST_RESULTS="$TMP_DIR/comprehensive_test_results.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Enterprise Application Tracker (EAT)${NC}"
echo -e "${BLUE}    Comprehensive Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Started at: $TIMESTAMP\n"

# Function to log results
log_result() {
    echo "$1" | tee -a "$TEST_RESULTS"
}

# Function to cleanup Docker containers
cleanup_containers() {
    echo -e "\n${YELLOW}Cleaning up Docker containers...${NC}"
    
    # Stop and remove all app-tracker related containers
    local containers=$(docker ps -aq --filter "name=app-tracker")
    if [ -n "$containers" ]; then
        echo -e "${YELLOW}Stopping app-tracker containers...${NC}"
        docker stop $containers 2>/dev/null || true
        echo -e "${YELLOW}Removing app-tracker containers...${NC}"
        docker rm $containers 2>/dev/null || true
    fi
    
    # Use docker compose to ensure complete cleanup
    cd "$PROJECT_ROOT" 2>/dev/null || true
    if [ -f "$COMPOSE_FILE" ]; then
        echo -e "${YELLOW}Running docker compose down...${NC}"
        docker compose -f "$COMPOSE_FILE" down --remove-orphans --volumes --timeout 10 2>/dev/null || true
    fi
    
    # Clean up any dangling networks
    local networks=$(docker network ls --filter "name=app-tracker" -q)
    if [ -n "$networks" ]; then
        echo -e "${YELLOW}Removing app-tracker networks...${NC}"
        docker network rm $networks 2>/dev/null || true
    fi
    
    # Verify cleanup
    local remaining=$(docker ps -q --filter "name=app-tracker")
    if [ -n "$remaining" ]; then
        echo -e "${RED}Warning: Some containers may still be running${NC}"
        docker ps --filter "name=app-tracker"
    else
        echo -e "${GREEN}All Docker containers cleaned up successfully${NC}"
    fi
}

# Enhanced cleanup function that handles errors gracefully
force_cleanup() {
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  EMERGENCY CLEANUP - Signal received  ${NC}"
    echo -e "${RED}========================================${NC}"
    
    # Log cleanup attempt
    log_result "## Emergency Cleanup Initiated: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Kill any running test processes
    pkill -f "npm test" 2>/dev/null || true
    pkill -f "python.*run_tests" 2>/dev/null || true
    
    # Force container cleanup
    cleanup_containers
    
    # Log final status
    log_result "## Test Suite Terminated: Emergency cleanup completed"
    
    echo -e "\n${YELLOW}Emergency cleanup completed${NC}"
    exit 130
}

# Function to run commands with timeout
run_with_timeout() {
    local timeout_duration=$1
    local description=$2
    shift 2
    
    echo -e "${YELLOW}Running: $description (timeout: ${timeout_duration}s)${NC}"
    
    if timeout "$timeout_duration" "$@"; then
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo -e "${RED}TIMEOUT: $description exceeded $timeout_duration seconds${NC}"
            log_result "$description: TIMEOUT after $timeout_duration seconds"
        else
            echo -e "${RED}FAILED: $description with exit code $exit_code${NC}"
            log_result "$description: FAILED with exit code $exit_code"
        fi
        return $exit_code
    fi
}

# Function to start services
start_services() {
    echo -e "\n${YELLOW}Starting Docker services...${NC}"
    cd "$PROJECT_ROOT"
    docker compose up -d --build
    
    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 30
    
    # Check if containers are running
    if ! docker ps | grep -q "app-tracker"; then
        echo -e "${RED}Failed to start Docker services${NC}"
        exit 1
    fi
    echo -e "${GREEN}Services started successfully${NC}"
}

# Function to run backend tests
run_backend_tests() {
    echo -e "\n${YELLOW}Running Backend Tests...${NC}"
    log_result "## Backend Test Results - $TIMESTAMP"
    
    # Get first available container
    CONTAINER=$(docker ps --filter "name=app-tracker-app" --format "{{.Names}}" | head -n1)
    
    if [ -z "$CONTAINER" ]; then
        echo -e "${RED}No app containers found${NC}"
        log_result "Backend tests: FAILED - No containers available"
        return 1
    fi
    
    echo -e "Using container: ${BLUE}$CONTAINER${NC}"
    
    # Run different test categories
    local backend_status=0
    
    echo -e "${YELLOW}Testing Models...${NC}"
    if run_with_timeout 300 "Model tests" docker exec "$CONTAINER" bash -c "cd /app/backend && python3.12 run_tests.py --models" 2>&1 | tee -a "$TEST_RESULTS"; then
        echo -e "${GREEN}Model tests: PASSED${NC}"
        log_result "Model tests: PASSED"
    else
        echo -e "${RED}Model tests: FAILED${NC}"
        log_result "Model tests: FAILED"
        backend_status=1
    fi
    
    echo -e "\n${YELLOW}Testing API...${NC}"
    if run_with_timeout 300 "API tests" docker exec "$CONTAINER" bash -c "cd /app/backend && python3.12 run_tests.py --api" 2>&1 | tee -a "$TEST_RESULTS"; then
        echo -e "${GREEN}API tests: PASSED${NC}"
        log_result "API tests: PASSED"
    else
        echo -e "${RED}API tests: FAILED${NC}"
        log_result "API tests: FAILED"
        backend_status=1
    fi
    
    echo -e "\n${YELLOW}Testing Audit System...${NC}"
    if run_with_timeout 300 "Audit tests" docker exec "$CONTAINER" bash -c "cd /app/backend && python3.12 run_tests.py --audit" 2>&1 | tee -a "$TEST_RESULTS"; then
        echo -e "${GREEN}Audit tests: PASSED${NC}"
        log_result "Audit tests: PASSED"
    else
        echo -e "${RED}Audit tests: FAILED${NC}"
        log_result "Audit tests: FAILED"
        backend_status=1
    fi
    
    return $backend_status
}

# Function to run frontend tests
run_frontend_tests() {
    echo -e "\n${YELLOW}Running Frontend Tests...${NC}"
    log_result "## Frontend Test Results - $TIMESTAMP"
    
    CONTAINER=$(docker ps --filter "name=app-tracker-app" --format "{{.Names}}" | head -n1)
    
    if [ -z "$CONTAINER" ]; then
        echo -e "${RED}No app containers found${NC}"
        log_result "Frontend tests: FAILED - No containers available"
        return 1
    fi
    
    local frontend_status=0
    
    echo -e "${YELLOW}Running Unit Tests...${NC}"
    if run_with_timeout 300 "Frontend unit tests" docker exec "$CONTAINER" bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm test -- --run" 2>&1 | tee -a "$TEST_RESULTS"; then
        echo -e "${GREEN}Frontend unit tests: PASSED${NC}"
        log_result "Frontend unit tests: PASSED"
    else
        echo -e "${RED}Frontend unit tests: FAILED${NC}"
        log_result "Frontend unit tests: FAILED"
        frontend_status=1
    fi
    
    echo -e "\n${YELLOW}Running Coverage Tests...${NC}"
    if run_with_timeout 300 "Frontend coverage tests" docker exec "$CONTAINER" bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm run test:coverage -- --run" 2>&1 | tee -a "$TEST_RESULTS"; then
        echo -e "${GREEN}Frontend coverage tests: PASSED${NC}"
        log_result "Frontend coverage tests: PASSED"
    else
        echo -e "${RED}Frontend coverage tests: FAILED${NC}"
        log_result "Frontend coverage tests: FAILED"
        frontend_status=1
    fi
    
    echo -e "\n${YELLOW}Testing Build Process...${NC}"
    if run_with_timeout 600 "Frontend build" docker exec "$CONTAINER" bash -c "source /root/.nvm/nvm.sh && cd /app/frontend && npm run build" 2>&1 | tee -a "$TEST_RESULTS"; then
        echo -e "${GREEN}Frontend build: PASSED${NC}"
        log_result "Frontend build: PASSED"
    else
        echo -e "${RED}Frontend build: FAILED${NC}"
        log_result "Frontend build: FAILED"
        frontend_status=1
    fi
    
    return $frontend_status
}

# Function to run integration tests
run_integration_tests() {
    echo -e "\n${YELLOW}Running Integration Tests...${NC}"
    log_result "## Integration Test Results - $TIMESTAMP"
    
    CONTAINER=$(docker ps --filter "name=app-tracker-app" --format "{{.Names}}" | head -n1)
    
    if [ -z "$CONTAINER" ]; then
        echo -e "${RED}No app containers found${NC}"
        log_result "Integration tests: FAILED - No containers available"
        return 1
    fi
    
    echo -e "${YELLOW}Testing API connectivity...${NC}"
    if run_with_timeout 60 "API connectivity test" docker exec "$CONTAINER" bash -c "cd /app/backend && python3.12 -c 'import requests; r = requests.get(\"http://localhost:8000/api/health/\"); print(\"Health check:\", r.status_code)'" 2>&1 | tee -a "$TEST_RESULTS"; then
        echo -e "${GREEN}API connectivity: PASSED${NC}"
        log_result "API connectivity: PASSED"
        return 0
    else
        echo -e "${RED}API connectivity: FAILED${NC}"
        log_result "API connectivity: FAILED"
        return 1
    fi
}

# Enhanced trap to ensure cleanup on exit, interruption, or termination
trap force_cleanup SIGINT SIGTERM
trap cleanup_containers EXIT

# Initialize test results file
mkdir -p "$TMP_DIR"
echo "# Enterprise Application Tracker (EAT) - Comprehensive Test Results" > "$TEST_RESULTS"
echo "Generated: $TIMESTAMP" >> "$TEST_RESULTS"
echo "" >> "$TEST_RESULTS"

# Main execution
main() {
    local overall_status=0
    
    # Cleanup any existing containers first
    cleanup_containers
    
    # Start services
    start_services
    
    # Run all test suites with error handling
    echo -e "\n${BLUE}Starting test execution...${NC}"
    
    if ! run_backend_tests; then
        overall_status=1
        echo -e "${YELLOW}Backend tests completed with errors${NC}"
    fi
    
    if ! run_frontend_tests; then
        overall_status=1
        echo -e "${YELLOW}Frontend tests completed with errors${NC}"
    fi
    
    if ! run_integration_tests; then
        overall_status=1
        echo -e "${YELLOW}Integration tests completed with errors${NC}"
    fi
    
    # Explicit cleanup before final summary
    echo -e "\n${BLUE}Performing final cleanup...${NC}"
    cleanup_containers
    
    # Final summary
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}         Test Suite Summary${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if [ $overall_status -eq 0 ]; then
        echo -e "${GREEN}All tests completed successfully!${NC}"
        log_result "## Overall Result: SUCCESS"
    else
        echo -e "${RED}Some tests failed. Check results above.${NC}"
        log_result "## Overall Result: FAILED"
    fi
    
    echo -e "\nTest results saved to: ${BLUE}$TEST_RESULTS${NC}"
    echo -e "Completed at: $(date '+%Y-%m-%d %H:%M:%S')\n"
    
    return $overall_status
}

# Run main function
main "$@"
