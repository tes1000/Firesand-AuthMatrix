# Test API Server for Auth Matrix

This directory contains a simple FastAPI server used for integration testing of the Auth Matrix application.

## Purpose

The test API provides:
- Public endpoints (no authentication)
- User endpoints (require user token)
- Admin endpoints (require admin token)

This allows comprehensive testing of the Auth Matrix authorization testing capabilities.

## Test Credentials

- **User Token**: `user_token_123`
- **Admin Token**: `admin_token_456`

## Running Locally

```bash
cd test_api
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### System
- `GET /health` - Health check (no auth required)

### Public
- `GET /public` - Public endpoint (no auth required)

### User
- `GET /user/profile` - User profile (requires user or admin token)
- `GET /user/data` - User data (requires user or admin token)

### Admin
- `GET /admin/dashboard` - Admin dashboard (requires admin token)
- `GET /admin/users` - User management (requires admin token)
