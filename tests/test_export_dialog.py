"""
Test suite for the simplified ExportDialog
"""

import pytest
import json
import sys
import os
import tempfile
from unittest.mock import MagicMock


# Mock PySide6
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

sys.modules["PySide6"] = mock_pyside6
sys.modules["PySide6.QtCore"] = MockQtCore()

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UI.views.SpecStore import SpecStore


class TestExportDialogIntegration:
    """Test the export dialog file-saving integration"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test cases"""
        self.store = SpecStore()
        # Set up a basic AuthMatrix spec with multiple roles
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {
                "guest": {"auth": {"type": "none"}},
                "user": {"auth": {"type": "bearer", "token": "user-token"}},
                "admin": {"auth": {"type": "bearer", "token": "admin-token"}},
            },
            "endpoints": [
                {
                    "name": "Public Endpoint",
                    "method": "GET",
                    "path": "/public",
                    "expect": {
                        "guest": {"status": 200},
                        "user": {"status": 200},
                        "admin": {"status": 200},
                    },
                },
                {
                    "name": "User Endpoint",
                    "method": "GET",
                    "path": "/user/profile",
                    "expect": {
                        "guest": {"status": 403},
                        "user": {"status": 200},
                        "admin": {"status": 200},
                    },
                },
                {
                    "name": "Admin Endpoint",
                    "method": "GET",
                    "path": "/admin/dashboard",
                    "expect": {
                        "guest": {"status": 403},
                        "user": {"status": 403},
                        "admin": {"status": 200},
                    },
                },
            ],
        }

    def test_export_authmatrix_to_file(self):
        """Test exporting AuthMatrix format to a file"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name

        try:
            # Export AuthMatrix format
            content = self.store.export_as_authmatrix()

            # Write to file (simulating what the dialog would do)
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Verify file exists and contains correct content
            assert os.path.exists(temp_file)

            with open(temp_file, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Should have shebang
            assert file_content.startswith("#!AUTHMATRIX\n")

            # Remove shebang and parse JSON
            json_content = "\n".join(file_content.splitlines()[1:])
            parsed = json.loads(json_content)

            # Verify structure
            assert parsed["base_url"] == "https://api.test.com"
            assert "guest" in parsed["roles"]
            assert "user" in parsed["roles"]
            assert "admin" in parsed["roles"]
            assert len(parsed["endpoints"]) == 3

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_export_postman_collections_to_directory(self):
        """Test exporting multiple Postman collections to a directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export Postman collections
            collections = self.store.export_as_postman_collections()

            # Should generate 3 collections
            assert len(collections) == 3
            assert "guest" in collections
            assert "user" in collections
            assert "admin" in collections

            # Write all collections to files (simulating what the dialog would do)
            saved_files = []
            for role_name, collection_json in collections.items():
                filename = os.path.join(
                    temp_dir, f"{role_name}.postman_collection.json"
                )
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(collection_json)
                saved_files.append(filename)

            # Verify all files exist
            assert len(saved_files) == 3

            # Verify each file contains valid JSON
            for filename in saved_files:
                assert os.path.exists(filename)

                with open(filename, "r", encoding="utf-8") as f:
                    content = json.load(f)

                # Verify Postman collection structure
                assert "info" in content
                assert "item" in content
                assert "schema" in content["info"]

            # Verify guest collection has no auth
            guest_file = os.path.join(temp_dir, "guest.postman_collection.json")
            with open(guest_file, "r", encoding="utf-8") as f:
                guest_data = json.load(f)
            assert "auth" not in guest_data
            assert len(guest_data["item"]) == 1  # Only public endpoint

            # Verify user collection has auth
            user_file = os.path.join(temp_dir, "user.postman_collection.json")
            with open(user_file, "r", encoding="utf-8") as f:
                user_data = json.load(f)
            assert "auth" in user_data
            assert user_data["auth"]["type"] == "bearer"
            assert len(user_data["item"]) == 2  # Public + user endpoints

            # Verify admin collection has auth
            admin_file = os.path.join(temp_dir, "admin.postman_collection.json")
            with open(admin_file, "r", encoding="utf-8") as f:
                admin_data = json.load(f)
            assert "auth" in admin_data
            assert admin_data["auth"]["type"] == "bearer"
            assert len(admin_data["item"]) == 3  # All endpoints

    def test_export_authmatrix_empty_spec(self):
        """Test exporting empty AuthMatrix spec"""
        self.store.spec = {
            "base_url": "",
            "default_headers": {},
            "roles": {},
            "endpoints": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name

        try:
            content = self.store.export_as_authmatrix()

            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Verify file exists
            assert os.path.exists(temp_file)

            # Verify it's valid JSON (even if empty)
            with open(temp_file, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Remove shebang and parse
            json_content = "\n".join(file_content.splitlines()[1:])
            parsed = json.loads(json_content)
            assert isinstance(parsed, dict)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_export_postman_collections_no_success_endpoints(self):
        """Test exporting when no endpoints have success status"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {"user": {"auth": {"type": "bearer", "token": "token"}}},
            "endpoints": [
                {
                    "name": "Forbidden Endpoint",
                    "method": "GET",
                    "path": "/forbidden",
                    "expect": {"user": {"status": 403}},
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            collections = self.store.export_as_postman_collections()

            # Should not generate any collections
            assert len(collections) == 0

            # Verify no files would be created
            files = os.listdir(temp_dir)
            assert len(files) == 0

    def test_file_naming_convention(self):
        """Test that collection files follow the expected naming convention"""
        with tempfile.TemporaryDirectory() as temp_dir:
            collections = self.store.export_as_postman_collections()

            expected_files = [
                "guest.postman_collection.json",
                "user.postman_collection.json",
                "admin.postman_collection.json",
            ]

            # Write collections with expected naming
            for role_name in collections.keys():
                filename = os.path.join(
                    temp_dir, f"{role_name}.postman_collection.json"
                )
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(collections[role_name])

            # Verify all expected files exist
            actual_files = sorted(os.listdir(temp_dir))
            assert actual_files == sorted(expected_files)

    def test_unicode_handling_in_files(self):
        """Test that unicode characters are properly handled in exported files"""
        self.store.spec = {
            "base_url": "https://api.test.com",
            "default_headers": {"Accept": "application/json"},
            "roles": {"用户": {"auth": {"type": "bearer", "token": "token"}}},
            "endpoints": [
                {
                    "name": "获取用户信息",
                    "method": "GET",
                    "path": "/user/info",
                    "expect": {"用户": {"status": 200}},
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            collections = self.store.export_as_postman_collections()

            for role_name, collection_json in collections.items():
                filename = os.path.join(
                    temp_dir, f"{role_name}.postman_collection.json"
                )
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(collection_json)

                # Read back and verify
                with open(filename, "r", encoding="utf-8") as f:
                    content = json.load(f)

                # Should preserve unicode
                assert content["item"][0]["name"] == "获取用户信息"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
