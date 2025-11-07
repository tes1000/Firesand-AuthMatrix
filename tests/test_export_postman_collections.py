"""
Test suite for exporting AuthMatrix to multiple Postman collections
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Mock PySide6 with a better strategy that preserves real object behavior
class MockSignal:
    def __init__(self, *args, **kwargs):
        pass
    def emit(self, *args, **kwargs):
        pass
    def connect(self, slot):
        pass

class MockQtCore:
    QObject = object
    Signal = MockSignal

mock_pyside6 = MagicMock()
mock_pyside6.QtCore = MockQtCore()

sys.modules['PySide6'] = mock_pyside6
sys.modules['PySide6.QtCore'] = MockQtCore()

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UI.views.SpecStore import SpecStore


class TestExportPostmanCollections:
    """Test exporting AuthMatrix to multiple Postman collections"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test cases"""
        self.store = SpecStore()
    
    def test_export_postman_collections_basic(self):
        """Test basic export of multiple Postman collections"""
        # Set up a basic AuthMatrix spec with multiple roles
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "guest": {"auth": {"type": "none"}},
                "user": {"auth": {"type": "bearer", "token": "user-token"}},
                "admin": {"auth": {"type": "bearer", "token": "admin-token"}}
            },
            "endpoints": [
                {
                    "name": "Public Endpoint",
                    "method": "GET",
                    "path": "/public",
                    "expect": {
                        "guest": {"status": 200},
                        "user": {"status": 200},
                        "admin": {"status": 200}
                    }
                },
                {
                    "name": "User Endpoint",
                    "method": "GET",
                    "path": "/user/profile",
                    "expect": {
                        "guest": {"status": 403},
                        "user": {"status": 200},
                        "admin": {"status": 200}
                    }
                },
                {
                    "name": "Admin Endpoint",
                    "method": "GET",
                    "path": "/admin/dashboard",
                    "expect": {
                        "guest": {"status": 403},
                        "user": {"status": 403},
                        "admin": {"status": 200}
                    }
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        
        # Should generate 3 collections (one per role)
        assert len(collections) == 3
        assert "guest" in collections
        assert "user" in collections
        assert "admin" in collections
        
        # Parse guest collection
        guest_collection = json.loads(collections["guest"])
        assert guest_collection["info"]["name"] == "Guest Collection"
        assert "auth" not in guest_collection  # Guest has no auth
        assert len(guest_collection["item"]) == 1  # Only public endpoint
        assert guest_collection["item"][0]["name"] == "Public Endpoint"
        
        # Parse user collection
        user_collection = json.loads(collections["user"])
        assert user_collection["info"]["name"] == "User Collection"
        assert user_collection["auth"]["type"] == "bearer"
        assert user_collection["auth"]["bearer"][0]["value"] == "user-token"
        assert len(user_collection["item"]) == 2  # Public + user endpoints
        
        # Parse admin collection
        admin_collection = json.loads(collections["admin"])
        assert admin_collection["info"]["name"] == "Admin Collection"
        assert admin_collection["auth"]["type"] == "bearer"
        assert admin_collection["auth"]["bearer"][0]["value"] == "admin-token"
        assert len(admin_collection["item"]) == 3  # All endpoints
    
    def test_export_postman_collections_no_expectations(self):
        """Test export when endpoints have no expectations"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Endpoint 1",
                    "method": "GET",
                    "path": "/endpoint1",
                    "expect": {}  # No expectations
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        
        # Should not generate any collections since no endpoints have success expectations
        assert len(collections) == 0
    
    def test_export_postman_collections_partial_expectations(self):
        """Test export when only some endpoints have expectations for a role"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Success Endpoint",
                    "method": "GET",
                    "path": "/success",
                    "expect": {
                        "user": {"status": 200}
                    }
                },
                {
                    "name": "Forbidden Endpoint",
                    "method": "GET",
                    "path": "/forbidden",
                    "expect": {
                        "user": {"status": 403}
                    }
                },
                {
                    "name": "No Expectation",
                    "method": "GET",
                    "path": "/no-expect",
                    "expect": {}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        
        assert len(collections) == 1
        user_collection = json.loads(collections["user"])
        assert len(user_collection["item"]) == 1
        assert user_collection["item"][0]["name"] == "Success Endpoint"
    
    def test_export_postman_collections_status_list(self):
        """Test export with status codes as lists"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Multi-status Success",
                    "method": "POST",
                    "path": "/create",
                    "expect": {
                        "user": {"status": [200, 201]}  # List of success codes
                    }
                },
                {
                    "name": "Multi-status Failure",
                    "method": "POST",
                    "path": "/forbidden",
                    "expect": {
                        "user": {"status": [403, 404]}  # List of non-success codes
                    }
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        
        assert len(collections) == 1
        user_collection = json.loads(collections["user"])
        assert len(user_collection["item"]) == 1
        assert user_collection["item"][0]["name"] == "Multi-status Success"
    
    def test_export_postman_collections_edge_status_codes(self):
        """Test export with edge case status codes"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Exactly 200",
                    "method": "GET",
                    "path": "/200",
                    "expect": {"user": {"status": 200}}
                },
                {
                    "name": "Exactly 299",
                    "method": "GET",
                    "path": "/299",
                    "expect": {"user": {"status": 299}}
                },
                {
                    "name": "Exactly 199",
                    "method": "GET",
                    "path": "/199",
                    "expect": {"user": {"status": 199}}
                },
                {
                    "name": "Exactly 300",
                    "method": "GET",
                    "path": "/300",
                    "expect": {"user": {"status": 300}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        
        user_collection = json.loads(collections["user"])
        # Should include 200 and 299 (both in 2xx range)
        assert len(user_collection["item"]) == 2
        names = [item["name"] for item in user_collection["item"]]
        assert "Exactly 200" in names
        assert "Exactly 299" in names
    
    def test_export_postman_collections_with_headers(self):
        """Test that default headers are included in collections"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Custom-Header": "custom-value"
            },
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Test Endpoint",
                    "method": "GET",
                    "path": "/test",
                    "expect": {"user": {"status": 200}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        # Check headers are present
        headers = user_collection["item"][0]["request"]["header"]
        assert len(headers) == 3
        header_dict = {h["key"]: h["value"] for h in headers}
        assert header_dict["Accept"] == "application/json"
        assert header_dict["Content-Type"] == "application/json"
        assert header_dict["X-Custom-Header"] == "custom-value"
    
    def test_export_postman_collections_excludes_auth_header(self):
        """Test that Authorization header is excluded from request headers"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {
                "Accept": "application/json",
                "Authorization": "Bearer should-be-excluded"
            },
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Test Endpoint",
                    "method": "GET",
                    "path": "/test",
                    "expect": {"user": {"status": 200}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        # Check Authorization header is NOT in request headers
        headers = user_collection["item"][0]["request"]["header"]
        header_keys = [h["key"] for h in headers]
        assert "Authorization" not in header_keys
        assert "authorization" not in [k.lower() for k in header_keys]
    
    def test_export_postman_collections_url_structure(self):
        """Test that URLs are properly structured in collections"""
        self.store.spec = {
            "base_url": "https://api.example.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Test Endpoint",
                    "method": "POST",
                    "path": "/v1/users/123",
                    "expect": {"user": {"status": 201}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        url = user_collection["item"][0]["request"]["url"]
        assert url["raw"] == "https://api.example.com/v1/users/123"
        assert url["host"] == ["api", "example", "com"]
        assert url["path"] == ["v1", "users", "123"]
    
    def test_export_postman_collections_root_path(self):
        """Test handling of root path"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Root Endpoint",
                    "method": "GET",
                    "path": "/",
                    "expect": {"user": {"status": 200}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        url = user_collection["item"][0]["request"]["url"]
        assert url["path"] == []  # Root path should be empty array
    
    def test_export_postman_collections_multiple_methods(self):
        """Test collections with various HTTP methods"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Get Users",
                    "method": "GET",
                    "path": "/users",
                    "expect": {"user": {"status": 200}}
                },
                {
                    "name": "Create User",
                    "method": "POST",
                    "path": "/users",
                    "expect": {"user": {"status": 201}}
                },
                {
                    "name": "Update User",
                    "method": "PUT",
                    "path": "/users/1",
                    "expect": {"user": {"status": 200}}
                },
                {
                    "name": "Delete User",
                    "method": "DELETE",
                    "path": "/users/1",
                    "expect": {"user": {"status": 204}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        assert len(user_collection["item"]) == 4
        methods = [item["request"]["method"] for item in user_collection["item"]]
        assert methods == ["GET", "POST", "PUT", "DELETE"]
    
    def test_export_postman_collections_schema_version(self):
        """Test that collections have correct Postman schema version"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Test",
                    "method": "GET",
                    "path": "/test",
                    "expect": {"user": {"status": 200}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        assert user_collection["info"]["schema"] == "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    
    def test_export_postman_collections_empty_spec(self):
        """Test export with empty spec"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {},
            "endpoints": []
        }
        
        collections = self.store.export_as_postman_collections()
        assert len(collections) == 0
    
    def test_export_postman_collections_no_roles(self):
        """Test export when there are no roles defined"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {},
            "endpoints": [
                {
                    "name": "Test",
                    "method": "GET",
                    "path": "/test",
                    "expect": {}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        assert len(collections) == 0


class TestExportPostmanCollectionsEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.store = SpecStore()
    
    def test_export_with_special_characters_in_role_name(self):
        """Test export with special characters in role names"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "admin-user": {"auth": {"type": "bearer", "token": "token"}},
                "super_admin": {"auth": {"type": "bearer", "token": "token2"}}
            },
            "endpoints": [
                {
                    "name": "Test",
                    "method": "GET",
                    "path": "/test",
                    "expect": {
                        "admin-user": {"status": 200},
                        "super_admin": {"status": 200}
                    }
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        
        assert "admin-user" in collections
        assert "super_admin" in collections
        
        admin_collection = json.loads(collections["admin-user"])
        assert admin_collection["info"]["name"] == "Admin-user Collection"
    
    def test_export_with_unicode_in_endpoint_name(self):
        """Test export with unicode characters in endpoint names"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "获取用户信息",
                    "method": "GET",
                    "path": "/user/info",
                    "expect": {"user": {"status": 200}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        assert user_collection["item"][0]["name"] == "获取用户信息"
    
    def test_export_with_missing_base_url(self):
        """Test export when base_url is missing or empty"""
        self.store.spec = {
            "base_url": "",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Test",
                    "method": "GET",
                    "path": "/test",
                    "expect": {"user": {"status": 200}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        # Should still export, just with empty base_url
        assert user_collection["item"][0]["request"]["url"]["raw"] == "/test"
    
    def test_export_preserves_json_formatting(self):
        """Test that exported JSON is properly formatted"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Test",
                    "method": "GET",
                    "path": "/test",
                    "expect": {"user": {"status": 200}}
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        
        # Verify it's valid JSON that can be re-parsed
        for role_name, collection_json in collections.items():
            parsed = json.loads(collection_json)
            # Re-stringify and compare (should be identical)
            re_stringified = json.dumps(parsed, indent=2)
            assert collection_json == re_stringified
    
    def test_export_with_contains_and_not_contains(self):
        """Test that contains/not_contains in expectations don't affect inclusion"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "user": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Test",
                    "method": "GET",
                    "path": "/test",
                    "expect": {
                        "user": {
                            "status": 200,
                            "contains": ["success"],
                            "not_contains": ["error"]
                        }
                    }
                }
            ]
        }
        
        collections = self.store.export_as_postman_collections()
        user_collection = json.loads(collections["user"])
        
        # Should still include the endpoint based on status code
        assert len(user_collection["item"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
