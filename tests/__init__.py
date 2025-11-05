"""
Test configuration and utilities
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_temp_file(content, suffix=".json"):
    """Create a temporary file with given content"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name


def create_temp_json_file(data):
    """Create a temporary JSON file with given data"""
    content = json.dumps(data, indent=2)
    return create_temp_file(content)


def cleanup_temp_file(file_path):
    """Clean up temporary file"""
    try:
        os.unlink(file_path)
    except OSError:
        pass


# Sample data for tests
SAMPLE_AUTHMATRIX_SPEC = {
    "base_url": "https://api.example.com",
    "default_headers": {
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    "roles": {
        "guest": {
            "auth": {"type": "none"}
        },
        "user": {
            "auth": {"type": "bearer", "token": "user-token-123"}
        },
        "admin": {
            "auth": {"type": "bearer", "token": "admin-token-456"}
        }
    },
    "endpoints": [
        {
            "name": "Public Health Check",
            "method": "GET",
            "path": "/health",
            "expect": {
                "guest": {"status": 200},
                "user": {"status": 200},
                "admin": {"status": 200}
            }
        },
        {
            "name": "User Profile",
            "method": "GET",
            "path": "/user/profile",
            "expect": {
                "guest": {"status": 403},
                "user": {"status": 200},
                "admin": {"status": 200}
            }
        },
        {
            "name": "Admin Dashboard",
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

SAMPLE_POSTMAN_COLLECTION = {
    "info": {
        "name": "Sample API Collection",
        "description": "A sample collection for testing",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "auth": {
        "type": "bearer",
        "bearer": [
            {"key": "token", "value": "sample-bearer-token"}
        ]
    },
    "item": [
        {
            "name": "Authentication",
            "item": [
                {
                    "name": "Login",
                    "request": {
                        "method": "POST",
                        "url": {
                            "raw": "https://api.example.com/auth/login",
                            "protocol": "https",
                            "host": ["api", "example", "com"],
                            "path": ["auth", "login"]
                        },
                        "body": {
                            "mode": "raw",
                            "raw": "{\"username\":\"test\",\"password\":\"test\"}"
                        }
                    }
                }
            ]
        },
        {
            "name": "Get User Info",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "https://api.example.com/user/{{user_id}}",
                    "protocol": "https",
                    "host": ["api", "example", "com"],
                    "path": ["user", "{{user_id}}"]
                }
            }
        },
        {
            "name": "Admin Operations",
            "item": [
                {
                    "name": "List All Users",
                    "request": {
                        "method": "GET",
                        "url": {
                            "raw": "https://api.example.com/admin/users",
                            "protocol": "https",
                            "host": ["api", "example", "com"],
                            "path": ["admin", "users"]
                        }
                    }
                },
                {
                    "name": "Delete User",
                    "request": {
                        "method": "DELETE",
                        "url": {
                            "raw": "https://api.example.com/admin/users/{{user_id}}",
                            "protocol": "https",
                            "host": ["api", "example", "com"],
                            "path": ["admin", "users", "{{user_id}}"]
                        }
                    }
                }
            ]
        }
    ]
}