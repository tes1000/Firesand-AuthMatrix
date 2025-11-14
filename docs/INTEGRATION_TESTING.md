# Integration Testing with Docker

This document describes the integration testing infrastructure for the Auth Matrix application.

## Overview

The integration testing setup includes:

1. **FastAPI Test Server** - A containerized API with multiple authentication levels
2. **Docker Configuration** - Dockerfile and docker-compose for easy deployment
3. **Integration Tests** - Comprehensive test suite validating Auth Matrix functionality
4. **CI/CD Pipeline** - Automated testing in GitHub Actions
5. **Helper Tools** - Scripts and Makefile for convenient local testing

## Files and Structure

```
.
├── test_api/                          # Test API server
│   ├── main.py                        # FastAPI application with endpoints
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Container definition
│   ├── .dockerignore                  # Files to exclude from image
│   └── README.md                      # Test API documentation
├── tests/
│   ├── test_integration.py            # Integration tests (requires Docker)
│   └── test_fastapi_server.py         # Unit tests for API (no Docker)
├── docker-compose.yml                 # Docker Compose configuration
├── test_api_spec.json                 # Auth Matrix spec for test API
├── run_integration_tests.sh           # Helper script to run tests
├── Makefile                           # Convenient test commands
├── INTEGRATION_TESTING.md             # This file
└── .github/workflows/
    └── integration-tests.yml          # CI/CD workflow
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Actions CI/CD                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │  1. Build Docker Image (FastAPI Test Server)     │  │
│  │  2. Start Container                               │  │
│  │  3. Run Integration Tests (pytest)                │  │
│  │  4. Collect Results & Coverage                    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Docker Container (FastAPI)                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Endpoints:                                       │  │
│  │  • GET /health          (public)                  │  │
│  │  • GET /public          (public)                  │  │
│  │  • GET /user/profile    (user/admin)              │  │
│  │  • GET /user/data       (user/admin)              │  │
│  │  • GET /admin/dashboard (admin only)              │  │
│  │  • GET /admin/users     (admin only)              │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Auth Matrix Application                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Tests authorization matrix:                      │  │
│  │  • Guest role (no auth)                           │  │
│  │  • User role (user_token_123)                     │  │
│  │  • Admin role (admin_token_456)                   │  │
│  │                                                    │  │
│  │  Validates:                                        │  │
│  │  • Request sending                                 │  │
│  │  • Token handling                                  │  │
│  │  • Status code validation                          │  │
│  │  • Authorization expectations                      │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ installed
- Git repository cloned

### Method 1: Using the Helper Script (Recommended)

```bash
# Install test dependencies
pip install pytest pytest-cov requests

# Run the integration test script (builds, starts, tests, and cleans up)
./run_integration_tests.sh
```

### Method 2: Using Make

```bash
# View all available commands
make help

# Run full integration test (build + start + test + cleanup)
make integration-test

# Or run steps individually
make build              # Build Docker image
make start              # Start container
pytest tests/test_integration.py -v
make stop               # Stop container
```

### Method 3: Using Docker Compose

1. **Start the test API server:**
   ```bash
   docker-compose up -d
   ```

2. **Verify the server is running:**
   ```bash
   curl http://localhost:8000/health
   ```
   
   Expected response:
   ```json
   {"status": "healthy", "message": "API is running"}
   ```

3. **Install test dependencies:**
   ```bash
   pip install pytest pytest-cov requests
   ```

4. **Run integration tests:**
   ```bash
   pytest tests/test_integration.py -v
   ```

5. **Test with Auth Matrix GUI:**
   ```bash
   python Firesand_Auth_Matrix.py test_api_spec.json
   ```
   
   Or load `test_api_spec.json` through the GUI import feature.

6. **Stop the test API server:**
   ```bash
   docker-compose down
   ```

### Method 4: Manual Docker Commands

## Test API Endpoints

### Authentication

The test API uses Bearer token authentication:

| Role  | Token              | Access Level                          |
|-------|--------------------|---------------------------------------|
| Guest | None               | Public endpoints only                 |
| User  | `user_token_123`   | Public + User endpoints               |
| Admin | `admin_token_456`  | Public + User + Admin endpoints       |

### Endpoints

| Endpoint              | Method | Auth Required | Guest | User | Admin |
|-----------------------|--------|---------------|-------|------|-------|
| `/health`             | GET    | No            | ✅ 200 | ✅ 200 | ✅ 200  |
| `/public`             | GET    | No            | ✅ 200 | ✅ 200 | ✅ 200  |
| `/user/profile`       | GET    | Yes (User+)   | ❌ 403 | ✅ 200 | ✅ 200  |
| `/user/data`          | GET    | Yes (User+)   | ❌ 403 | ✅ 200 | ✅ 200  |
| `/admin/dashboard`    | GET    | Yes (Admin)   | ❌ 403 | ❌ 403 | ✅ 200  |
| `/admin/users`        | GET    | Yes (Admin)   | ❌ 403 | ❌ 403 | ✅ 200  |

## Integration Tests

### Test Coverage

The integration tests validate:

1. **API Connectivity**
   - Health check endpoint accessibility
   - Network connectivity between Auth Matrix and API

2. **Authentication Mechanisms**
   - No authentication (guest role)
   - Bearer token authentication (user role)
   - Bearer token authentication (admin role)
   - Invalid token handling

3. **Authorization Matrix**
   - Guest access patterns (public only)
   - User access patterns (public + user endpoints)
   - Admin access patterns (all endpoints)
   - Proper 403 Forbidden responses for unauthorized access

4. **Request Handling**
   - HTTP status code validation
   - Response parsing
   - Latency measurement
   - Error handling

5. **Auth Matrix Functionality**
   - Spec file loading
   - Token injection into requests
   - Expectation evaluation (PASS/FAIL/SKIP)
   - Result aggregation

### Running Specific Tests

```bash
# Run all integration tests
pytest tests/test_integration.py -v

# Run specific test
pytest tests/test_integration.py::TestIntegration::test_authorization_matrix_admin_role -v

# Run with coverage
pytest tests/test_integration.py --cov=. --cov-report=html

# Run with detailed output
pytest tests/test_integration.py -vv --tb=long
```

## CI/CD Pipeline

### GitHub Actions Workflow

The integration tests run automatically on:
- Pull requests to `main` branch
- Pushes to `main` branch
- Manual workflow dispatch

**Workflow steps:**
1. Checkout code
2. Set up Python 3.12
3. Install dependencies
4. Build Docker image for test API
5. Start test API container
6. Wait for API to be healthy
7. Run integration tests with pytest
8. Collect coverage reports
9. Upload results and artifacts
10. Comment on PR with results (if applicable)
11. Clean up containers

### Viewing Results

- **GitHub Actions**: Navigate to the "Actions" tab in the repository
- **PR Comments**: Automated bot comments on pull requests
- **Artifacts**: Download test reports from workflow runs

## Docker Configuration

### Dockerfile

Located at `test_api/Dockerfile`:
- Base image: `python:3.11-slim`
- Installs FastAPI, Uvicorn, and dependencies
- Exposes port 8000
- Includes health check
- Runs Uvicorn server

### docker-compose.yml

Located at repository root:
- Defines `test-api` service
- Maps port 8000:8000
- Configures health checks
- Creates isolated network

### Building and Running

```bash
# Build image
docker build -t authmatrix-test-api ./test_api

# Run container
docker run -d -p 8000:8000 --name test-api authmatrix-test-api

# View logs
docker logs test-api

# Stop container
docker stop test-api
docker rm test-api
```

## Troubleshooting

### API Not Starting

```bash
# Check if container is running
docker ps

# View logs
docker logs authmatrix-test-api

# Check if port 8000 is available
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows
```

### Tests Failing to Connect

```bash
# Verify API is accessible
curl http://localhost:8000/health

# Check Docker network
docker network inspect authmatrix-network

# Restart containers
docker-compose restart
```

### Permission Errors

```bash
# On Linux, you may need to run with sudo
sudo docker-compose up -d

# Or add your user to the docker group
sudo usermod -aG docker $USER
# Then log out and back in
```

## Development

### Adding New Endpoints

1. **Update FastAPI server** (`test_api/main.py`):
   ```python
   @app.get("/new/endpoint")
   async def new_endpoint(role: str = Depends(require_authentication)):
       return {"message": "New endpoint"}
   ```

2. **Update test spec** (`test_api_spec.json`):
   ```json
   {
     "name": "New Endpoint",
     "method": "GET",
     "path": "/new/endpoint",
     "expect": {
       "guest": {"status": 403},
       "user": {"status": 200},
       "admin": {"status": 200}
     }
   }
   ```

3. **Add integration test** (`tests/test_integration.py`):
   ```python
   def test_new_endpoint(self):
       response = requests.get(f"{self.base_url}/new/endpoint")
       assert response.status_code == 403
   ```

4. **Rebuild and test**:
   ```bash
   docker-compose down
   docker-compose up --build -d
   pytest tests/test_integration.py -v
   ```

### Modifying Authentication

To change token values or add new roles:

1. Update `test_api/main.py` `VALID_TOKENS` dictionary
2. Update `test_api_spec.json` roles section
3. Update integration tests to use new tokens
4. Rebuild Docker image

## Security Considerations

### Test Tokens

⚠️ **WARNING**: The tokens used in this test environment are hardcoded and should **NEVER** be used in production.

- `user_token_123` - For testing only
- `admin_token_456` - For testing only

### Production Use

For production environments:
- Use secure token generation (JWT, OAuth2, etc.)
- Implement token rotation
- Use environment variables for secrets
- Enable HTTPS/TLS
- Implement rate limiting
- Add comprehensive logging and monitoring

### Docker Security

- Test API runs in isolated container
- No persistent data storage
- Network isolated from host by default
- Container runs as non-root user (recommended enhancement)

## Performance

### Benchmarks

Typical performance metrics:
- Container startup: 5-10 seconds
- API response time: < 50ms
- Full integration test suite: 10-20 seconds
- Docker build time: 30-60 seconds (cached: 5 seconds)

### Optimization Tips

1. **Use Docker layer caching** - Requirements.txt copied before source
2. **Parallel tests** - Use `pytest -n auto` for parallel execution
3. **Keep containers running** - Avoid rebuilding for each test run
4. **Use docker-compose** - Faster than manual docker commands

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Auth Matrix README](README.md)

## Contributing

When adding integration tests:

1. Follow existing test patterns
2. Use descriptive test names
3. Add docstrings explaining what is tested
4. Ensure tests are idempotent
5. Clean up resources in teardown
6. Update this documentation

## Support

If you encounter issues:

1. Check Docker and API logs
2. Verify network connectivity
3. Review GitHub Actions logs
4. Create an issue with:
   - Error messages
   - Docker logs
   - Test output
   - Environment details (OS, Docker version, Python version)
