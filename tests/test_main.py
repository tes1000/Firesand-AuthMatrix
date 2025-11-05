"""
Test suite for Firesands Auth Matrix
"""

import unittest
import json
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Firesand_Auth_Matrix import (
    detect_file_type,
    convert_postman_to_authmatrix,
    extract_base_url_from_postman,
    load_and_convert_spec
)


class TestFileTypeDetection(unittest.TestCase):
    """Test file type detection functionality"""
    
    def test_detect_authmatrix_format(self):
        """Test detection of AuthMatrix format files"""
        # Create a temporary file with AuthMatrix shebang
        test_content = "#!AUTHMATRIX\n{\"test\": \"data\"}"
        with open("test_authmatrix.json", "w") as f:
            f.write(test_content)
        
        try:
            result = detect_file_type("test_authmatrix.json")
            self.assertEqual(result, "authmatrix")
        finally:
            os.remove("test_authmatrix.json")
    
    def test_detect_postman_format(self):
        """Test detection of Postman format files"""
        # Create a temporary file without AuthMatrix shebang
        test_content = "{\"info\": {\"name\": \"Test Collection\"}}"
        with open("test_postman.json", "w") as f:
            f.write(test_content)
        
        try:
            result = detect_file_type("test_postman.json")
            self.assertEqual(result, "postman")
        finally:
            os.remove("test_postman.json")
    
    def test_detect_unknown_format(self):
        """Test detection of unknown format files"""
        # Create a non-existent file
        result = detect_file_type("non_existent_file.json")
        self.assertEqual(result, "unknown")


class TestPostmanConversion(unittest.TestCase):
    """Test Postman to AuthMatrix conversion functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_postman = {
            "info": {
                "name": "Test API",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {"key": "token", "value": "test-bearer-token"}
                ]
            },
            "item": [
                {
                    "name": "Get Users",
                    "request": {
                        "method": "GET",
                        "url": {
                            "raw": "https://api.example.com/users",
                            "protocol": "https",
                            "host": ["api", "example", "com"],
                            "path": ["users"]
                        }
                    }
                },
                {
                    "name": "Admin Folder",
                    "item": [
                        {
                            "name": "Get Admin Dashboard",
                            "request": {
                                "method": "GET",
                                "url": {
                                    "raw": "https://api.example.com/admin/dashboard",
                                    "protocol": "https",
                                    "host": ["api", "example", "com"],
                                    "path": ["admin", "dashboard"]
                                }
                            }
                        }
                    ]
                }
            ]
        }
    
    def test_extract_base_url(self):
        """Test base URL extraction from Postman collection"""
        result = extract_base_url_from_postman(self.sample_postman)
        self.assertEqual(result, "https://api.example.com")
    
    def test_convert_basic_collection(self):
        """Test basic conversion of Postman collection"""
        result = convert_postman_to_authmatrix(self.sample_postman)
        
        # Check basic structure
        self.assertIn("base_url", result)
        self.assertIn("roles", result)
        self.assertIn("endpoints", result)
        self.assertIn("default_headers", result)
        
        # Check base URL
        self.assertEqual(result["base_url"], "https://api.example.com")
        
        # Check roles
        self.assertIn("guest", result["roles"])
        self.assertIn("admin", result["roles"])
        
        # Check admin role auth
        admin_auth = result["roles"]["admin"]["auth"]
        self.assertEqual(admin_auth["type"], "bearer")
        self.assertEqual(admin_auth["token"], "test-bearer-token")
        
        # Check endpoints
        self.assertEqual(len(result["endpoints"]), 2)
        
        # Check endpoint names and paths
        endpoint_paths = [ep["path"] for ep in result["endpoints"]]
        self.assertIn("/users", endpoint_paths)
        self.assertIn("/admin/dashboard", endpoint_paths)
    
    def test_convert_empty_collection(self):
        """Test conversion of empty Postman collection"""
        empty_collection = {
            "info": {"name": "Empty Collection"},
            "item": []
        }
        
        result = convert_postman_to_authmatrix(empty_collection)
        self.assertEqual(len(result["endpoints"]), 0)
        self.assertIn("guest", result["roles"])


class TestSpecLoading(unittest.TestCase):
    """Test specification loading functionality"""
    
    def test_load_authmatrix_spec(self):
        """Test loading AuthMatrix specification"""
        authmatrix_content = """#!AUTHMATRIX
{
    "base_url": "https://api.test.com",
    "roles": {
        "guest": {"auth": {"type": "none"}},
        "user": {"auth": {"type": "bearer", "token": "user-token"}}
    },
    "endpoints": [
        {
            "name": "Test Endpoint",
            "method": "GET",
            "path": "/test",
            "expect": {
                "guest": {"status": 403},
                "user": {"status": 200}
            }
        }
    ]
}"""
        
        with open("test_spec.json", "w") as f:
            f.write(authmatrix_content)
        
        try:
            result = load_and_convert_spec("test_spec.json")
            
            # Check structure
            self.assertIn("base_url", result)
            self.assertIn("roles", result)
            self.assertIn("endpoints", result)
            
            # Check content
            self.assertEqual(result["base_url"], "https://api.test.com")
            self.assertEqual(len(result["roles"]), 2)
            self.assertEqual(len(result["endpoints"]), 1)
            
            # Check endpoint expectations
            endpoint = result["endpoints"][0]
            self.assertEqual(endpoint["expect"]["guest"]["status"], 403)
            self.assertEqual(endpoint["expect"]["user"]["status"], 200)
            
        finally:
            os.remove("test_spec.json")
    
    def test_load_postman_spec(self):
        """Test loading and converting Postman specification"""
        postman_content = {
            "info": {"name": "Test Collection"},
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "GET",
                        "url": "https://api.test.com/endpoint"
                    }
                }
            ]
        }
        
        with open("test_postman.json", "w") as f:
            json.dump(postman_content, f)
        
        try:
            result = load_and_convert_spec("test_postman.json")
            
            # Should be converted to AuthMatrix format
            self.assertIn("base_url", result)
            self.assertIn("roles", result)
            self.assertIn("endpoints", result)
            
            # Should have at least guest role
            self.assertIn("guest", result["roles"])
            
            # Should have the endpoint
            self.assertEqual(len(result["endpoints"]), 1)
            self.assertEqual(result["endpoints"][0]["method"], "GET")
            
        finally:
            os.remove("test_postman.json")


if __name__ == "__main__":
    unittest.main()