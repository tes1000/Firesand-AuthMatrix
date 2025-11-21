"""
Test suite for TokensSection Delete All functionality

These tests focus on the logic without requiring UI rendering.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UI.views.SpecStore import SpecStore


class TestDeleteAllRolesLogic:
    """Test the delete all roles logic using SpecStore directly"""
    
    def test_delete_all_roles_logic_single_role(self):
        """Test deleting all roles when there's only one role besides guest"""
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        
        # Verify admin was added
        assert "admin" in store.spec["roles"]
        assert "guest" in store.spec["roles"]
        
        # Delete all non-guest roles
        roles_to_delete = [role for role in store.spec["roles"].keys() if role != "guest"]
        for role in roles_to_delete:
            store.remove_role(role)
        
        # Verify only guest remains
        assert "admin" not in store.spec["roles"]
        assert "guest" in store.spec["roles"]
        assert len(store.spec["roles"]) == 1
    
    def test_delete_all_roles_logic_multiple_roles(self):
        """Test deleting all roles when there are multiple roles"""
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        store.add_role("user", "Auth: none", "")
        store.add_role("moderator", "Auth: bearer", "token456")
        store.add_role("viewer", "Auth: none", "")
        
        # Verify all roles were added
        assert len(store.spec["roles"]) == 5  # guest + 4 new roles
        
        # Delete all non-guest roles
        roles_to_delete = [role for role in store.spec["roles"].keys() if role != "guest"]
        for role in roles_to_delete:
            store.remove_role(role)
        
        # Verify only guest remains
        assert len(store.spec["roles"]) == 1
        assert "guest" in store.spec["roles"]
    
    def test_delete_all_roles_logic_only_guest(self):
        """Test delete all when only guest role exists"""
        store = SpecStore()
        
        # Should only have guest role by default
        assert len(store.spec["roles"]) == 1
        assert "guest" in store.spec["roles"]
        
        # Try to delete all non-guest roles (should be none)
        roles_to_delete = [role for role in store.spec["roles"].keys() if role != "guest"]
        assert len(roles_to_delete) == 0
    
    def test_delete_all_roles_preserves_guest_properties(self):
        """Test that guest role properties are preserved"""
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        store.add_role("user", "Auth: none", "")
        
        # Save original guest properties
        original_guest = store.spec["roles"]["guest"].copy()
        
        # Delete all non-guest roles
        roles_to_delete = [role for role in store.spec["roles"].keys() if role != "guest"]
        for role in roles_to_delete:
            store.remove_role(role)
        
        # Verify guest properties unchanged
        assert store.spec["roles"]["guest"] == original_guest
        assert store.spec["roles"]["guest"]["auth"]["type"] == "none"
    
    def test_delete_all_roles_removes_endpoint_expectations(self):
        """Test that deleting roles also removes endpoint expectations"""
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        store.add_role("user", "Auth: none", "")
        
        # Add an endpoint
        store.add_endpoint("Test Endpoint", "GET", "/test")
        
        # Set expectations for the roles
        store.set_endpoint_expectation(0, "admin", status=200)
        store.set_endpoint_expectation(0, "user", status=403)
        store.set_endpoint_expectation(0, "guest", status=403)
        
        # Verify expectations were set
        assert "admin" in store.spec["endpoints"][0]["expect"]
        assert "user" in store.spec["endpoints"][0]["expect"]
        assert "guest" in store.spec["endpoints"][0]["expect"]
        
        # Delete all non-guest roles
        roles_to_delete = [role for role in store.spec["roles"].keys() if role != "guest"]
        for role in roles_to_delete:
            store.remove_role(role)
        
        # Verify admin and user expectations were removed, but guest remains
        assert "admin" not in store.spec["endpoints"][0]["expect"]
        assert "user" not in store.spec["endpoints"][0]["expect"]
        assert "guest" in store.spec["endpoints"][0]["expect"]
    
    def test_delete_all_roles_emits_spec_changed(self):
        """Test that deleting roles emits specChanged signal"""
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        store.add_role("user", "Auth: none", "")
        
        # Track signal emissions
        signal_count = [0]
        def on_spec_changed():
            signal_count[0] += 1
        
        store.specChanged.connect(on_spec_changed)
        
        # Delete all non-guest roles
        roles_to_delete = [role for role in store.spec["roles"].keys() if role != "guest"]
        initial_count = signal_count[0]
        for role in roles_to_delete:
            store.remove_role(role)
        
        # Verify signal was emitted for each deletion
        assert signal_count[0] == initial_count + len(roles_to_delete)
    
    def test_delete_all_roles_with_special_characters(self):
        """Test deleting roles with special characters in names"""
        store = SpecStore()
        store.add_role("admin-test", "Auth: bearer", "token123")
        store.add_role("user_test", "Auth: none", "")
        store.add_role("moderator.test", "Auth: bearer", "token456")
        
        # Verify all roles were added
        assert "admin-test" in store.spec["roles"]
        assert "user_test" in store.spec["roles"]
        assert "moderator.test" in store.spec["roles"]
        
        # Delete all non-guest roles
        roles_to_delete = [role for role in store.spec["roles"].keys() if role != "guest"]
        for role in roles_to_delete:
            store.remove_role(role)
        
        # Verify only guest remains
        assert len(store.spec["roles"]) == 1
        assert "guest" in store.spec["roles"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
