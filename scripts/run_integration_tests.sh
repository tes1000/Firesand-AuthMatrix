#!/bin/bash
# Script to run integration tests with Docker

set -e

echo "=== Auth Matrix Integration Tests ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo ""
    echo "Please install pytest first using one of the following:"
    echo "  pip install pytest"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Warning: docker-compose not found, using 'docker compose'${NC}"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "Step 1: Building Docker image..."
docker build -t authmatrix-test-api:latest ../test_api
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build Docker image${NC}"
    exit 1
fi

echo ""
echo "Step 2: Starting test API container..."
docker run -d --name authmatrix-test-api -p 8000:8000 authmatrix-test-api:latest
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Container started${NC}"
else
    echo -e "${RED}✗ Failed to start container${NC}"
    exit 1
fi

echo ""
echo "Step 3: Waiting for API to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is ready${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ API failed to start${NC}"
    echo "Container logs:"
    docker logs authmatrix-test-apiq
    docker stop authmatrix-test-api
    docker rm authmatrix-test-api
    exit 1
fi

echo ""
echo "Step 4: Running integration tests..."
pytest ../tests/test_integration.py -v
TEST_RESULT=$?

echo ""
echo "Step 5: Cleaning up..."
docker stop authmatrix-test-api
docker rm authmatrix-test-api

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}=== All tests passed! ===${NC}"
    exit 0
else
    echo -e "${RED}=== Some tests failed ===${NC}"
    exit 1
fi
