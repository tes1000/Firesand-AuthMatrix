.PHONY: help build start stop test integration-test clean docker-logs

help:
	@echo "Auth Matrix Integration Testing"
	@echo ""
	@echo "Available commands:"
	@echo "  make build              - Build the test API Docker image"
	@echo "  make start              - Start the test API container"
	@echo "  make stop               - Stop the test API container"
	@echo "  make test               - Run all tests"
	@echo "  make integration-test   - Run integration tests (requires Docker)"
	@echo "  make docker-logs        - Show Docker container logs"
	@echo "  make clean              - Clean up Docker containers and images"

build:
	@echo "Building test API Docker image..."
	docker build -t authmatrix-test-api:latest ./test_api

start:
	@echo "Starting test API container..."
	docker run -d --name authmatrix-test-api -p 8000:8000 authmatrix-test-api:latest
	@echo "Waiting for API to be ready..."
	@sleep 3
	@curl -f http://localhost:8000/health && echo "✓ API is ready" || echo "✗ API failed to start"

stop:
	@echo "Stopping test API container..."
	docker stop authmatrix-test-api || true
	docker rm authmatrix-test-api || true

test:
	@echo "Running all tests..."
	pytest tests/ -v

integration-test: build start
	@echo "Running integration tests..."
	@sleep 5
	pytest tests/test_integration.py -v || true
	@$(MAKE) stop

docker-logs:
	docker logs authmatrix-test-api

clean: stop
	@echo "Cleaning up Docker resources..."
	docker rmi authmatrix-test-api:latest || true
	@echo "Clean complete"
