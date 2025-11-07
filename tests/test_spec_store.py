"""
Test suite for SpecStore class
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

# Mock PySide6 with a better strategy that preserves real object behavior
import sys

# Create a mock Signal class that behaves like a real signal
class MockSignal:
    def __init__(self, *args, **kwargs):
        # Accept any arguments like the real Signal class
        pass
    def emit(self, *args, **kwargs):
        pass
    def connect(self, slot):
        pass

# Create a mock QtCore that has QObject as a real base class and Signal as our mock
class MockQtCore:
    QObject = object  # Use real object as base class
    Signal = MockSignal

mock_pyside6 = MagicMock()
mock_pyside6.QtCore = MockQtCore()

sys.modules['PySide6'] = mock_pyside6
sys.modules['PySide6.QtCore'] = MockQtCore()

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UI.views.SpecStore import SpecStore, AUTHMATRIX_SHEBANG


class TestSpecStore:
    """Test SpecStore functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test cases"""
        self.store = SpecStore()
    
    def test_init_default_spec(self):
        """Test SpecStore initializes with default spec"""
        assert self.store.spec["base_url"] == ""
        assert "guest" in self.store.spec["roles"]
        assert self.store.spec["roles"]["guest"]["auth"]["type"] == "none"
        assert self.store.spec["endpoints"] == []
        assert "Accept" in self.store.spec["default_headers"]
    
    def test_load_spec_authmatrix_format(self):
        """Test loading AuthMatrix format with shebang"""
        authmatrix_content = f"""{AUTHMATRIX_SHEBANG}
{{
    "base_url": "https://api.test.com",
    "roles": {{
        "admin": {{"auth": {{"type": "bearer", "token": "admin-token"}}}}
    }},
    "endpoints": [
        {{
            "name": "Test Endpoint",
            "method": "GET",
            "path": "/test",
            "expect": {{
                "admin": {{"status": 200}}
            }}
        }}
    ]
}}"""
        
        result = self.store.load_spec_from_content(authmatrix_content)
        assert result
        assert self.store.spec["base_url"] == "https://api.test.com"
        assert "admin" in self.store.spec["roles"]
        assert len(self.store.spec["endpoints"]) == 1
        assert self.store._original_postman_data is None
    
    def test_load_spec_postman_format(self):
        """Test loading Postman collection format"""
        postman_content = {
            "info": {"name": "Test Collection"},
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "POST",
                        "url": "https://api.example.com/test"
                    }
                }
            ]
        }
        
        result = self.store.load_spec_from_content(json.dumps(postman_content))
        assert result
        assert self.store.spec["base_url"] == "https://api.example.com"
        assert "guest" in self.store.spec["roles"]
        assert len(self.store.spec["endpoints"]) == 1
        assert self.store._original_postman_data is not None
    
    def test_load_spec_invalid_json(self):
        """Test loading invalid JSON content"""
        invalid_content = "{ invalid json"
        
        result = self.store.load_spec_from_content(invalid_content)
        assert not result
        # Spec should remain unchanged
        assert self.store.spec["base_url"] == ""
    
    def test_load_spec_plain_authmatrix_without_shebang(self):
        """Test loading plain AuthMatrix JSON without shebang"""
        plain_content = {
            "base_url": "https://plain.api.com",
            "roles": {
                "user": {"auth": {"type": "none"}}
            },
            "endpoints": []
        }
        
        result = self.store.load_spec_from_content(json.dumps(plain_content))
        assert result
        assert self.store.spec["base_url"] == "https://plain.api.com"
        assert "user" in self.store.spec["roles"]
    
    def test_is_postman_collection(self):
        """Test Postman collection detection"""
        # Valid Postman collection
        postman_data = {"info": {"name": "Test"}, "item": []}
        assert self.store.is_postman_collection(postman_data)
        
        # Invalid - missing info
        invalid_data = {"item": []}
        assert not self.store.is_postman_collection(invalid_data)
        
        # Invalid - missing item
        invalid_data = {"info": {"name": "Test"}}
        assert not self.store.is_postman_collection(invalid_data)
        
        # Invalid - not a dict
        assert not self.store.is_postman_collection([])
        assert not self.store.is_postman_collection("string")
        assert not self.store.is_postman_collection(None)
    
    def test_convert_postman_with_bearer_auth(self):
        """Test Postman conversion with bearer authentication"""
        postman_data = {
            "info": {"name": "Auth Test"},
            "auth": {
                "type": "bearer",
                "bearer": [
                    {"key": "token", "value": "secret-token"}
                ]
            },
            "item": [
                {
                    "name": "Protected Resource",
                    "request": {
                        "method": "GET",
                        "url": "https://api.example.com/protected"
                    }
                }
            ]
        }
        
        result = self.store.convert_postman_to_authmatrix(postman_data)
        
        assert result["base_url"] == "https://api.example.com"
        assert "admin" in result["roles"]
        assert result["roles"]["admin"]["auth"]["type"] == "bearer"
        assert result["roles"]["admin"]["auth"]["token"] == "secret-token"
        assert len(result["endpoints"]) == 1
    
    def test_convert_postman_no_auth(self):
        """Test Postman conversion without authentication"""
        postman_data = {
            "info": {"name": "No Auth Test"},
            "item": [
                {
                    "name": "Public Resource",
                    "request": {
                        "method": "GET",
                        "url": "https://api.example.com/public"
                    }
                }
            ]
        }
        
        result = self.store.convert_postman_to_authmatrix(postman_data)
        
        # Should only have guest role
        assert list(result["roles"].keys()) == ["guest"]
        assert result["roles"]["guest"]["auth"]["type"] == "none"
    
    def test_set_base_url(self):
        """Test setting base URL"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.set_base_url("https://new.api.com")
            
            assert self.store.spec["base_url"] == "https://new.api.com"
            mock_signal.emit.assert_called_once()
    
    def test_set_base_url_with_whitespace(self):
        """Test setting base URL with whitespace"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.set_base_url("  https://api.com  ")
            
            assert self.store.spec["base_url"] == "https://api.com"
            mock_signal.emit.assert_called_once()
    
    def test_set_base_url_empty(self):
        """Test setting empty base URL"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.set_base_url("")
            
            assert self.store.spec["base_url"] == ""
            mock_signal.emit.assert_called_once()
    
    def test_set_header(self):
        """Test setting headers"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.set_header("Content-Type", "application/json")
            
            assert self.store.spec["default_headers"]["Content-Type"] == "application/json"
            mock_signal.emit.assert_called_once()
    
    def test_set_header_empty_key(self):
        """Test setting header with empty key"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.set_header("", "value")
            self.store.set_header("   ", "value")
            
            # Should not add empty keys
            assert "" not in self.store.spec["default_headers"]
            assert "   " not in self.store.spec["default_headers"]
            mock_signal.emit.assert_not_called()
    
    def test_remove_header(self):
        """Test removing headers"""
        # Add a header first
        self.store.spec["default_headers"]["Test-Header"] = "test-value"
        
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.remove_header("Test-Header")
            
            assert "Test-Header" not in self.store.spec["default_headers"]
            mock_signal.emit.assert_called_once()
    
    def test_remove_header_nonexistent(self):
        """Test removing nonexistent header"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.remove_header("NonExistent")
            
            # Should not crash and should still emit signal
            mock_signal.emit.assert_called_once()
    
    def test_parse_endpoints_text_simple(self):
        """Test parsing simple endpoints text"""
        text = """/users
/admin
/login"""
        
        result = self.store.parse_endpoints_text(text)
        expected = [
            ("/users", "GET", "/users"),
            ("/admin", "GET", "/admin"),
            ("/login", "GET", "/login")
        ]
        assert result == expected
    
    def test_parse_endpoints_text_with_methods(self):
        """Test parsing endpoints text with HTTP methods"""
        text = """GET /users
POST /users
PUT /users/123
DELETE /users/123"""
        
        result = self.store.parse_endpoints_text(text)
        expected = [
            ("/users", "GET", "/users"),
            ("/users", "POST", "/users"),
            ("/users/123", "PUT", "/users/123"),
            ("/users/123", "DELETE", "/users/123")
        ]
        assert result == expected
    
    def test_parse_endpoints_text_with_names(self):
        """Test parsing endpoints text with custom names"""
        text = """GET /users List all users
POST /users Create user
/login User login"""
        
        result = self.store.parse_endpoints_text(text)
        expected = [
            ("List all users", "GET", "/users"),
            ("Create user", "POST", "/users"),
            ("User login", "GET", "/login")
        ]
        assert result == expected
    
    def test_parse_endpoints_text_with_comments(self):
        """Test parsing endpoints text with comments and empty lines"""
        text = """# User endpoints
GET /users
# Empty line above

POST /users Create user
# Admin endpoints
GET /admin"""
        
        result = self.store.parse_endpoints_text(text)
        expected = [
            ("/users", "GET", "/users"),
            ("Create user", "POST", "/users"),
            ("/admin", "GET", "/admin")
        ]
        assert result == expected
    
    def test_parse_endpoints_text_missing_slash(self):
        """Test parsing endpoints text with missing leading slash"""
        text = """users
admin/settings"""
        
        result = self.store.parse_endpoints_text(text)
        expected = [
            ("users", "GET", "/users"),
            ("admin/settings", "GET", "/admin/settings")
        ]
        assert result == expected
    
    def test_set_endpoints(self):
        """Test setting endpoints"""
        endpoints = [
            ("Users List", "GET", "/users"),
            ("Create User", "POST", "/users")
        ]
        
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.set_endpoints(endpoints)
            
            assert len(self.store.spec["endpoints"]) == 2
            assert self.store.spec["endpoints"][0]["name"] == "Users List"
            assert self.store.spec["endpoints"][0]["method"] == "GET"
            assert self.store.spec["endpoints"][0]["path"] == "/users"
            assert self.store.spec["endpoints"][0]["expect"] == {}
            mock_signal.emit.assert_called_once()
    
    def test_update_endpoint_row(self):
        """Test updating individual endpoint"""
        # Add an endpoint first
        self.store.spec["endpoints"] = [
            {"name": "Old Name", "method": "GET", "path": "/old", "expect": {}}
        ]
        
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.update_endpoint_row(0, "New Name", "POST", "/new")
            
            endpoint = self.store.spec["endpoints"][0]
            assert endpoint["name"] == "New Name"
            assert endpoint["method"] == "POST"
            assert endpoint["path"] == "/new"
            mock_signal.emit.assert_called_once()
    
    def test_update_endpoint_row_invalid_index(self):
        """Test updating endpoint with invalid index"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.update_endpoint_row(999, "Name", "GET", "/path")
            
            # Should not crash and should not emit signal
            mock_signal.emit.assert_not_called()
    
    def test_add_endpoint(self):
        """Test adding new endpoint"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.add_endpoint("New Endpoint", "POST", "/new")
            
            assert len(self.store.spec["endpoints"]) == 1
            endpoint = self.store.spec["endpoints"][0]
            assert endpoint["name"] == "New Endpoint"
            assert endpoint["method"] == "POST"
            assert endpoint["path"] == "/new"
            assert endpoint["expect"] == {}
            mock_signal.emit.assert_called_once()
    
    def test_delete_endpoint(self):
        """Test deleting endpoint"""
        # Add endpoints first
        self.store.spec["endpoints"] = [
            {"name": "Endpoint 1", "method": "GET", "path": "/1", "expect": {}},
            {"name": "Endpoint 2", "method": "GET", "path": "/2", "expect": {}}
        ]
        
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.delete_endpoint(0)
            
            assert len(self.store.spec["endpoints"]) == 1
            assert self.store.spec["endpoints"][0]["name"] == "Endpoint 2"
            mock_signal.emit.assert_called_once()
    
    def test_delete_endpoint_invalid_index(self):
        """Test deleting endpoint with invalid index"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.delete_endpoint(999)
            
            # Should not crash and should not emit signal
            mock_signal.emit.assert_not_called()
    
    def test_add_role_bearer(self):
        """Test adding role with bearer auth"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            success, error = self.store.add_role("admin", "bearer", "admin-token")
            
            assert success
            assert error is None
            assert "admin" in self.store.spec["roles"]
            assert self.store.spec["roles"]["admin"]["auth"]["type"] == "bearer"
            assert self.store.spec["roles"]["admin"]["auth"]["token"] == "admin-token"
            mock_signal.emit.assert_called_once()
    
    def test_add_role_none_auth(self):
        """Test adding role with no auth"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            success, error = self.store.add_role("public", "none", "")
            
            assert success
            assert error is None
            assert "public" in self.store.spec["roles"]
            assert self.store.spec["roles"]["public"]["auth"]["type"] == "none"
            mock_signal.emit.assert_called_once()
    
    def test_add_role_empty_name(self):
        """Test adding role with empty name"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            success, error = self.store.add_role("", "bearer", "token")
            
            assert not success
            assert "required" in error
            mock_signal.emit.assert_not_called()
    
    def test_add_role_whitespace_name(self):
        """Test adding role with whitespace-only name"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            success, error = self.store.add_role("   ", "bearer", "token")
            
            assert not success
            assert "required" in error
            mock_signal.emit.assert_not_called()
    
    def test_remove_role(self):
        """Test removing role"""
        # Add role and endpoint expectation first
        self.store.spec["roles"]["admin"] = {"auth": {"type": "bearer", "token": "token"}}
        self.store.spec["endpoints"] = [
            {
                "name": "Test",
                "method": "GET",
                "path": "/test",
                "expect": {
                    "admin": {"status": 200},
                    "guest": {"status": 403}
                }
            }
        ]
        
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.remove_role("admin")
            
            assert "admin" not in self.store.spec["roles"]
            # Should also remove from endpoint expectations
            assert "admin" not in self.store.spec["endpoints"][0]["expect"]
            assert "guest" in self.store.spec["endpoints"][0]["expect"]
            mock_signal.emit.assert_called_once()
    
    def test_remove_role_nonexistent(self):
        """Test removing nonexistent role"""
        with patch.object(self.store, 'specChanged') as mock_signal:
            self.store.remove_role("nonexistent")
            
            # Should not crash and should NOT emit signal since no changes were made
            mock_signal.emit.assert_not_called()
    
    def test_set_endpoint_expectation(self):
        """Test setting endpoint expectation"""
        # Add endpoint and role first
        self.store.spec["endpoints"] = [
            {"name": "Test", "method": "GET", "path": "/test", "expect": {}}
        ]
        self.store.spec["roles"]["admin"] = {"auth": {"type": "bearer", "token": "token"}}
        
        with patch.object(self.store, 'specChanged') as mock_signal:
            success, error = self.store.set_endpoint_expectation(
                0, "admin", status=200, contains=["success"], not_contains=["error"]
            )
            
            assert success
            assert error is None
            
            expectation = self.store.spec["endpoints"][0]["expect"]["admin"]
            assert expectation["status"] == 200
            assert expectation["contains"] == ["success"]
            assert expectation["not_contains"] == ["error"]
            mock_signal.emit.assert_called_once()
    
    def test_set_endpoint_expectation_invalid_index(self):
        """Test setting expectation with invalid endpoint index"""
        success, error = self.store.set_endpoint_expectation(999, "admin", status=200)
        
        assert not success
        assert "Invalid endpoint index" in error
    
    def test_set_endpoint_expectation_invalid_role(self):
        """Test setting expectation for nonexistent role"""
        self.store.spec["endpoints"] = [
            {"name": "Test", "method": "GET", "path": "/test", "expect": {}}
        ]
        
        success, error = self.store.set_endpoint_expectation(0, "nonexistent", status=200)
        
        assert not success
        assert "does not exist" in error
    
    def test_remove_endpoint_expectation(self):
        """Test removing endpoint expectation"""
        # Add endpoint with expectation
        self.store.spec["endpoints"] = [
            {
                "name": "Test",
                "method": "GET",
                "path": "/test",
                "expect": {
                    "admin": {"status": 200},
                    "guest": {"status": 403}
                }
            }
        ]
        
        with patch.object(self.store, 'specChanged') as mock_signal:
            success, error = self.store.remove_endpoint_expectation(0, "admin")
            
            assert success
            assert error is None
            assert "admin" not in self.store.spec["endpoints"][0]["expect"]
            assert "guest" in self.store.spec["endpoints"][0]["expect"]
            mock_signal.emit.assert_called_once()
    
    def test_remove_endpoint_expectation_invalid_index(self):
        """Test removing expectation with invalid endpoint index"""
        success, error = self.store.remove_endpoint_expectation(999, "admin")
        
        assert not success
        assert "Invalid endpoint index" in error
    
    def test_export_as_authmatrix(self):
        """Test exporting as AuthMatrix format"""
        self.store.spec["base_url"] = "https://api.test.com"
        self.store.spec["roles"]["admin"] = {"auth": {"type": "bearer", "token": "token"}}
        
        result = self.store.export_as_authmatrix()
        
        assert result.startswith(AUTHMATRIX_SHEBANG)
        # Remove shebang and parse JSON
        json_content = result[len(AUTHMATRIX_SHEBANG):].strip()
        parsed = json.loads(json_content)
        
        assert parsed["base_url"] == "https://api.test.com"
        assert "admin" in parsed["roles"]
    
    def test_export_as_postman_with_original_data(self):
        """Test exporting as Postman when original data exists"""
        # Set original Postman data
        original_postman = {
            "info": {"name": "Original Collection"},
            "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "old-token"}]},
            "item": []
        }
        self.store._original_postman_data = original_postman
        
        result = self.store.export_as_postman()
        parsed = json.loads(result)
        
        # Should keep original structure but remove auth
        assert parsed["info"]["name"] == "Original Collection"
        assert "auth" not in parsed
    
    def test_export_as_postman_convert_from_authmatrix(self):
        """Test exporting as Postman when converting from AuthMatrix"""
        self.store.spec["base_url"] = "https://api.test.com"
        self.store.spec["endpoints"] = [
            {"name": "Test Endpoint", "method": "POST", "path": "/test"}
        ]
        self.store._original_postman_data = None
        
        result = self.store.export_as_postman()
        parsed = json.loads(result)
        
        assert "info" in parsed
        assert parsed["info"]["name"] == "AuthMatrix Export"
        assert "item" in parsed
        assert len(parsed["item"]) == 1
        
        item = parsed["item"][0]
        assert item["name"] == "Test Endpoint"
        assert item["request"]["method"] == "POST"


class TestSpecStoreEdgeCases:
    """Test SpecStore edge cases and error conditions"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.store = SpecStore()
    
    def test_load_spec_ensures_required_fields(self):
        """Test that loading spec ensures all required fields exist"""
        minimal_content = '{"base_url": "https://api.com"}'
        
        result = self.store.load_spec_from_content(minimal_content)
        assert result
        
        # Should have all required fields
        assert "base_url" in self.store.spec
        assert "default_headers" in self.store.spec
        assert "roles" in self.store.spec
        assert "endpoints" in self.store.spec
        assert "guest" in self.store.spec["roles"]
    
    def test_convert_postman_with_complex_url_structure(self):
        """Test Postman conversion with complex URL structures"""
        postman_data = {
            "info": {"name": "Complex URLs"},
            "item": [
                {
                    "name": "Complex URL",
                    "request": {
                        "method": "GET",
                        "url": {
                            "raw": "https://api.example.com:8080/v1/users?page=1&limit=10",
                            "protocol": "https",
                            "host": ["api", "example", "com"],
                            "port": "8080",
                            "path": ["v1", "users"],
                            "query": [
                                {"key": "page", "value": "1"},
                                {"key": "limit", "value": "10"}
                            ]
                        }
                    }
                }
            ]
        }
        
        result = self.store.convert_postman_to_authmatrix(postman_data)
        assert result["base_url"] == "https://api.example.com:8080"
        assert result["endpoints"][0]["path"] == "/v1/users"
    
    def test_extract_base_url_with_various_formats(self):
        """Test base URL extraction with various URL formats"""
        test_cases = [
            # (postman_data, expected_base_url)
            ({
                "item": [{
                    "request": {
                        "url": {
                            "protocol": "http",
                            "host": ["localhost"],
                            "path": ["api"]
                        }
                    }
                }]
            }, "http://localhost"),
            ({
                "item": [{
                    "request": {
                        "url": {
                            "protocol": "https",
                            "host": ["api", "example", "com"],
                            "port": "443",
                            "path": ["v1"]
                        }
                    }
                }]
            }, "https://api.example.com:443"),
            ({
                "item": [{
                    "request": {
                        "url": "http://127.0.0.1:3000/test"
                    }
                }]
            }, "http://127.0.0.1:3000")
        ]
        
        for postman_data, expected in test_cases:
            result = self.store.extract_base_url_from_postman(postman_data)
            assert result == expected
    
    def test_parse_endpoints_text_edge_cases(self):
        """Test endpoint parsing with edge cases"""
        # Empty input
        result = self.store.parse_endpoints_text("")
        assert result == []
        
        # None input
        result = self.store.parse_endpoints_text(None)
        assert result == []
        
        # Only comments and empty lines
        result = self.store.parse_endpoints_text("# Comment\n\n  \n# Another comment")
        assert result == []
        
        # Mixed case HTTP methods
        text = "get /users\npost /users\nPUT /users/1"
        result = self.store.parse_endpoints_text(text)
        assert result[0][1] == "GET"  # Should be uppercase
        assert result[1][1] == "POST"
        assert result[2][1] == "PUT"
    
    def test_role_operations_with_special_characters(self):
        """Test role operations with special characters and edge cases"""
        # Role with special characters
        success, error = self.store.add_role("admin-user", "bearer", "token-123")
        assert success
        assert "admin-user" in self.store.spec["roles"]
        
        # Role with unicode characters
        success, error = self.store.add_role("用户", "none", "")
        assert success
        assert "用户" in self.store.spec["roles"]
        
        # Very long role name
        long_name = "a" * 1000
        success, error = self.store.add_role(long_name, "bearer", "token")
        assert success
        
        # Very long token
        long_token = "t" * 10000
        success, error = self.store.add_role("long-token-user", "bearer", long_token)
        assert success
        assert self.store.spec["roles"]["long-token-user"]["auth"]["token"] == long_token


if __name__ == "__main__":
    pytest.main([__file__])