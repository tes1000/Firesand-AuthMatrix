"""
Integration tests for Auth Matrix against the test FastAPI server.

These tests validate that the Auth Matrix application can:
1. Successfully send requests to the API
2. Handle different authentication methods (none, bearer token)
3. Correctly evaluate authorization expectations
4. Process various HTTP status codes
"""

import time
import sys
import os
import requests

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Firesand_Auth_Matrix import run_spec, load_and_convert_spec


class TestIntegration:
    """Integration tests for Auth Matrix with Docker test API"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment - ensure API is running"""
        cls.base_url = "http://localhost:8000"
        cls.max_retries = 30
        cls.retry_delay = 1
        
        # Wait for API to be ready
        print("\nWaiting for test API to be ready...")
        for i in range(cls.max_retries):
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✓ Test API is ready (attempt {i+1}/{cls.max_retries})")
                    return
            except requests.exceptions.RequestException:
                if i < cls.max_retries - 1:
                    time.sleep(cls.retry_delay)
                else:
                    raise
        
        raise RuntimeError(
            f"Test API not ready after {cls.max_retries} attempts. "
            "Please ensure the Docker container is running: docker-compose up -d"
        )
    
    def test_api_health_check(self):
        """Test that the API health endpoint is accessible"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    def test_public_endpoint_no_auth(self):
        """Test public endpoint without authentication"""
        response = requests.get(f"{self.base_url}/public")
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "public"
    
    def test_user_endpoint_with_guest(self):
        """Test user endpoint with no authentication (should fail)"""
        response = requests.get(f"{self.base_url}/user/profile")
        assert response.status_code == 403
    
    def test_user_endpoint_with_user_token(self):
        """Test user endpoint with user token (should succeed)"""
        headers = {"Authorization": "Bearer user_token_123"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "user"
    
    def test_user_endpoint_with_admin_token(self):
        """Test user endpoint with admin token (should succeed)"""
        headers = {"Authorization": "Bearer admin_token_456"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "admin"
    
    def test_admin_endpoint_with_guest(self):
        """Test admin endpoint with no authentication (should fail)"""
        response = requests.get(f"{self.base_url}/admin/dashboard")
        assert response.status_code == 403
    
    def test_admin_endpoint_with_user_token(self):
        """Test admin endpoint with user token (should fail)"""
        headers = {"Authorization": "Bearer user_token_123"}
        response = requests.get(f"{self.base_url}/admin/dashboard", headers=headers)
        assert response.status_code == 403
    
    def test_admin_endpoint_with_admin_token(self):
        """Test admin endpoint with admin token (should succeed)"""
        headers = {"Authorization": "Bearer admin_token_456"}
        response = requests.get(f"{self.base_url}/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["access_level"] == "admin"
        assert "admin_data" in data
    
    def test_invalid_token(self):
        """Test endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        assert response.status_code == 401
    
    def test_run_spec_with_test_api(self):
        """Test running the full Auth Matrix spec against the test API"""
        # Load the test spec
        spec_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_api_spec.json"
        )
        spec = load_and_convert_spec(spec_path)
        
        # Run the spec
        results = run_spec(spec)
        
        # Validate results structure
        assert isinstance(results, dict)
        assert len(results) > 0
        
        # Check each endpoint has results for all roles
        for endpoint_name, role_results in results.items():
            assert isinstance(role_results, dict)
            assert "guest" in role_results
            assert "user" in role_results
            assert "admin" in role_results
    
    def test_authorization_matrix_guest_role(self):
        """Test authorization matrix for guest role"""
        spec_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_api_spec.json"
        )
        spec = load_and_convert_spec(spec_path)
        results = run_spec(spec)
        
        # Guest should:
        # - Access public endpoints (200)
        # - Be denied user endpoints (403)
        # - Be denied admin endpoints (403)
        
        assert results["Public Endpoint"]["guest"]["status"] == "PASS"
        assert results["Public Endpoint"]["guest"]["http"] == 200
        
        assert results["User Profile"]["guest"]["status"] == "PASS"
        assert results["User Profile"]["guest"]["http"] == 403
        
        assert results["Admin Dashboard"]["guest"]["status"] == "PASS"
        assert results["Admin Dashboard"]["guest"]["http"] == 403
    
    def test_authorization_matrix_user_role(self):
        """Test authorization matrix for user role"""
        spec_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_api_spec.json"
        )
        spec = load_and_convert_spec(spec_path)
        results = run_spec(spec)
        
        # User should:
        # - Access public endpoints (200)
        # - Access user endpoints (200)
        # - Be denied admin endpoints (403)
        
        assert results["Public Endpoint"]["user"]["status"] == "PASS"
        assert results["Public Endpoint"]["user"]["http"] == 200
        
        assert results["User Profile"]["user"]["status"] == "PASS"
        assert results["User Profile"]["user"]["http"] == 200
        
        assert results["Admin Dashboard"]["user"]["status"] == "PASS"
        assert results["Admin Dashboard"]["user"]["http"] == 403
    
    def test_authorization_matrix_admin_role(self):
        """Test authorization matrix for admin role"""
        spec_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_api_spec.json"
        )
        spec = load_and_convert_spec(spec_path)
        results = run_spec(spec)
        
        # Admin should:
        # - Access public endpoints (200)
        # - Access user endpoints (200)
        # - Access admin endpoints (200)
        
        assert results["Public Endpoint"]["admin"]["status"] == "PASS"
        assert results["Public Endpoint"]["admin"]["http"] == 200
        
        assert results["User Profile"]["admin"]["status"] == "PASS"
        assert results["User Profile"]["admin"]["http"] == 200
        
        assert results["Admin Dashboard"]["admin"]["status"] == "PASS"
        assert results["Admin Dashboard"]["admin"]["http"] == 200
    
    def test_latency_measurement(self):
        """Test that latency is measured for successful requests"""
        spec_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_api_spec.json"
        )
        spec = load_and_convert_spec(spec_path)
        results = run_spec(spec)
        
        # Check that successful requests have latency measurements
        public_result = results["Public Endpoint"]["guest"]
        assert "latency_ms" in public_result
        assert isinstance(public_result["latency_ms"], int)
        assert public_result["latency_ms"] >= 0
    
    def test_all_endpoints_pass(self):
        """Test that all expectations in the spec pass"""
        spec_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_api_spec.json"
        )
        spec = load_and_convert_spec(spec_path)
        results = run_spec(spec)
        
        # Count pass/fail/skip
        total = 0
        passed = 0
        failed = 0
        skipped = 0
        
        for endpoint_name, role_results in results.items():
            for role, result in role_results.items():
                total += 1
                status = result["status"]
                if status == "PASS":
                    passed += 1
                elif status == "FAIL":
                    failed += 1
                    print(f"FAILED: {endpoint_name} - {role}: {result}")
                elif status == "SKIP":
                    skipped += 1
        
        print(f"\nResults: {passed}/{total} passed, {failed} failed, {skipped} skipped")
        
        # All configured expectations should pass
        assert failed == 0, f"Expected all tests to pass, but {failed} failed"
        assert passed > 0, "Expected some tests to pass"


if __name__ == "__main__":
    # Can be run directly with pytest or as a script
    print("Running integration tests...")
    print("Ensure Docker container is running: docker-compose up -d")
