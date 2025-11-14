"""
Unit tests for the FastAPI test server.

These tests validate the test API endpoints without requiring Docker.
They use FastAPI's TestClient for fast, isolated testing.
"""

import sys
import os

# Add test_api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_api'))

try:
    from fastapi.testclient import TestClient
    from main import app, VALID_TOKENS
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    import pytest


if not FASTAPI_AVAILABLE:
    pytestmark = pytest.mark.skip(reason="FastAPI not installed")


class TestFastAPIServer:
    """Unit tests for FastAPI test server endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Set up test client"""
        if FASTAPI_AVAILABLE:
            cls.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    def test_public_endpoint_no_auth(self):
        """Test public endpoint without authentication"""
        response = self.client.get("/public")
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "public"
        assert "message" in data
    
    def test_user_profile_no_auth(self):
        """Test user profile endpoint without authentication"""
        response = self.client.get("/user/profile")
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
    
    def test_user_profile_with_user_token(self):
        """Test user profile endpoint with valid user token"""
        headers = {"Authorization": "Bearer user_token_123"}
        response = self.client.get("/user/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "user"
        assert "user_id" in data
    
    def test_user_profile_with_admin_token(self):
        """Test user profile endpoint with admin token"""
        headers = {"Authorization": "Bearer admin_token_456"}
        response = self.client.get("/user/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "admin"
    
    def test_user_data_no_auth(self):
        """Test user data endpoint without authentication"""
        response = self.client.get("/user/data")
        assert response.status_code == 403
    
    def test_user_data_with_user_token(self):
        """Test user data endpoint with valid user token"""
        headers = {"Authorization": "Bearer user_token_123"}
        response = self.client.get("/user/data", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "user"
    
    def test_admin_dashboard_no_auth(self):
        """Test admin dashboard endpoint without authentication"""
        response = self.client.get("/admin/dashboard")
        assert response.status_code == 403
    
    def test_admin_dashboard_with_user_token(self):
        """Test admin dashboard endpoint with user token (should fail)"""
        headers = {"Authorization": "Bearer user_token_123"}
        response = self.client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 403
    
    def test_admin_dashboard_with_admin_token(self):
        """Test admin dashboard endpoint with admin token"""
        headers = {"Authorization": "Bearer admin_token_456"}
        response = self.client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "admin"
        assert "admin_data" in data
        assert "total_users" in data["admin_data"]
    
    def test_admin_users_no_auth(self):
        """Test admin users endpoint without authentication"""
        response = self.client.get("/admin/users")
        assert response.status_code == 403
    
    def test_admin_users_with_user_token(self):
        """Test admin users endpoint with user token (should fail)"""
        headers = {"Authorization": "Bearer user_token_123"}
        response = self.client.get("/admin/users", headers=headers)
        assert response.status_code == 403
    
    def test_admin_users_with_admin_token(self):
        """Test admin users endpoint with admin token"""
        headers = {"Authorization": "Bearer admin_token_456"}
        response = self.client.get("/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "admin"
        assert "admin_data" in data
        assert "users" in data["admin_data"]
    
    def test_invalid_token(self):
        """Test endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        response = self.client.get("/user/profile", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_malformed_authorization_header(self):
        """Test endpoint with malformed authorization header"""
        headers = {"Authorization": "NotBearer user_token_123"}
        response = self.client.get("/user/profile", headers=headers)
        # FastAPI's HTTPBearer expects "Bearer" prefix
        assert response.status_code == 403
    
    def test_not_found_endpoint(self):
        """Test accessing non-existent endpoint"""
        response = self.client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_valid_tokens_configuration(self):
        """Test that valid tokens are properly configured"""
        assert "user_token_123" in VALID_TOKENS
        assert "admin_token_456" in VALID_TOKENS
        assert VALID_TOKENS["user_token_123"] == "user"
        assert VALID_TOKENS["admin_token_456"] == "admin"


if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import pytest
        pytest.main([__file__, "-v"])
    else:
        print("FastAPI not available. Install with: pip install fastapi")
