"""
Test suite for UI views

These tests require pytest-qt to be enabled. Run with:
    pytest -p pytest-qt tests/test_ui_components.py tests/test_ui_views.py

Or mark them with the 'ui' marker and run:
    pytest -m ui -p pytest-qt
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mark all tests in this module as UI tests
pytestmark = pytest.mark.ui


class TestHeadersSection:
    """Test Headers view"""
    
    def test_headers_section_init(self, qtbot):
        """Test HeadersSection initialization"""
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        
        store = SpecStore()
        # KVRow needs callbacks for on_add and on_remove_key
        headers = KVRow(lambda: None, lambda k: None, store)
        qtbot.addWidget(headers)
        assert headers is not None


class TestTokensSection:
    """Test Tokens view"""
    
    def test_tokens_section_init(self, qtbot):
        """Test TokensSection initialization"""
        from UI.views.Tokens import TokensSection
        from UI.views.SpecStore import SpecStore
        
        store = SpecStore()
        tokens = TokensSection(store)
        qtbot.addWidget(tokens)
        assert tokens is not None
    
    def test_delete_all_roles_button_exists(self, qtbot):
        """Test that Delete All button is present"""
        from UI.views.Tokens import TokensSection
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets
        
        store = SpecStore()
        tokens = TokensSection(store)
        qtbot.addWidget(tokens)
        
        # Find the Delete All button
        delete_all_btn = None
        for child in tokens.findChildren(QtWidgets.QPushButton):
            if child.text() == "Delete All":
                delete_all_btn = child
                break
        
        assert delete_all_btn is not None, "Delete All button should exist"
        assert delete_all_btn.toolTip() == "Delete all roles except the default guest role"
    
    def test_delete_all_roles_no_roles(self, qtbot, monkeypatch):
        """Test Delete All with only guest role (should show info dialog)"""
        from UI.views.Tokens import TokensSection
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets
        
        store = SpecStore()
        tokens = TokensSection(store)
        qtbot.addWidget(tokens)
        
        # Mock the information dialog
        called = []
        def mock_information(parent, title, message):
            called.append((title, message))
        
        monkeypatch.setattr(QtWidgets.QMessageBox, 'information', mock_information)
        
        # Call delete all
        tokens._delete_all_roles()
        
        # Check that info dialog was shown
        assert len(called) == 1
        assert called[0][0] == "No Roles to Delete"
        assert "guest" in called[0][1]
    
    def test_delete_all_roles_with_roles_cancel(self, qtbot, monkeypatch):
        """Test Delete All with roles but user cancels"""
        from UI.views.Tokens import TokensSection
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets
        
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        store.add_role("user", "Auth: none", "")
        
        tokens = TokensSection(store)
        qtbot.addWidget(tokens)
        
        # Mock the question dialog to return No
        def mock_question(parent, title, message, buttons, default):
            return QtWidgets.QMessageBox.No
        
        monkeypatch.setattr(QtWidgets.QMessageBox, 'question', mock_question)
        
        # Call delete all
        tokens._delete_all_roles()
        
        # Check that roles still exist (user cancelled)
        assert "admin" in store.spec["roles"]
        assert "user" in store.spec["roles"]
        assert "guest" in store.spec["roles"]
    
    def test_delete_all_roles_with_roles_confirm(self, qtbot, monkeypatch):
        """Test Delete All with roles and user confirms"""
        from UI.views.Tokens import TokensSection
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets
        
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        store.add_role("user", "Auth: none", "")
        store.add_role("moderator", "Auth: bearer", "token456")
        
        tokens = TokensSection(store)
        qtbot.addWidget(tokens)
        
        # Mock the question dialog to return Yes
        def mock_question(parent, title, message, buttons, default):
            # Verify the message contains the role names
            assert "admin" in message
            assert "user" in message
            assert "moderator" in message
            assert "guest" in message
            assert "3 role(s)" in message
            return QtWidgets.QMessageBox.Yes
        
        monkeypatch.setattr(QtWidgets.QMessageBox, 'question', mock_question)
        
        # Call delete all
        tokens._delete_all_roles()
        
        # Check that only guest remains
        assert "admin" not in store.spec["roles"]
        assert "user" not in store.spec["roles"]
        assert "moderator" not in store.spec["roles"]
        assert "guest" in store.spec["roles"]
        assert len(store.spec["roles"]) == 1
    
    def test_delete_all_roles_preserves_guest(self, qtbot, monkeypatch):
        """Test that guest role is always preserved"""
        from UI.views.Tokens import TokensSection
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets
        
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        
        tokens = TokensSection(store)
        qtbot.addWidget(tokens)
        
        # Mock the question dialog to return Yes
        def mock_question(parent, title, message, buttons, default):
            return QtWidgets.QMessageBox.Yes
        
        monkeypatch.setattr(QtWidgets.QMessageBox, 'question', mock_question)
        
        # Call delete all
        tokens._delete_all_roles()
        
        # Verify guest role still exists and has correct structure
        assert "guest" in store.spec["roles"]
        assert store.spec["roles"]["guest"]["auth"]["type"] == "none"
    
    def test_delete_all_roles_updates_table(self, qtbot, monkeypatch):
        """Test that table is refreshed after deleting all roles"""
        from UI.views.Tokens import TokensSection
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets
        
        store = SpecStore()
        store.add_role("admin", "Auth: bearer", "token123")
        store.add_role("user", "Auth: none", "")
        
        tokens = TokensSection(store)
        qtbot.addWidget(tokens)
        
        # Initial table should have 3 rows (guest, admin, user)
        assert tokens.table.rowCount() == 3
        
        # Mock the question dialog to return Yes
        def mock_question(parent, title, message, buttons, default):
            return QtWidgets.QMessageBox.Yes
        
        monkeypatch.setattr(QtWidgets.QMessageBox, 'question', mock_question)
        
        # Call delete all
        tokens._delete_all_roles()
        
        # Table should now have only 1 row (guest)
        assert tokens.table.rowCount() == 1
        assert tokens.table.item(0, 0).text() == "guest"


class TestEndpointsSection:
    """Test Endpoints view"""
    
    def test_endpoints_section_init(self, qtbot):
        """Test EndpointsSection initialization"""
        from UI.views.Endpoints import EndpointsSection
        from UI.views.SpecStore import SpecStore
        
        store = SpecStore()
        endpoints = EndpointsSection(store)
        qtbot.addWidget(endpoints)
        assert endpoints is not None
    
    def test_configure_all_dialog_edit_button(self, qtbot):
        """Test ConfigureAllEndpointsDialog has Edit button in Configure column"""
        from UI.views.Endpoints import ConfigureAllEndpointsDialog
        from UI.views.SpecStore import SpecStore
        
        store = SpecStore()
        # Add a test endpoint to populate the table
        store.spec["endpoints"] = [
            {"name": "Test Endpoint", "method": "GET", "path": "/test", "expect": {}}
        ]
        
        dialog = ConfigureAllEndpointsDialog(store)
        qtbot.addWidget(dialog)
        
        # Verify the dialog initializes
        assert dialog is not None
        
        # Verify the table has at least one row
        assert dialog.endpoints_table.rowCount() == 1
        
        # Get the button from the Configure column (column 3)
        button_widget = dialog.endpoints_table.cellWidget(0, 3)
        assert button_widget is not None
        
        # Verify the button text is "Edit" not "Configure"
        assert button_widget.text() == "Edit"
        
        # Verify tooltip is set
        assert "Configure" in button_widget.toolTip()


class TestResultsSection:
    """Test Results view"""
    
    def test_results_section_init(self, qtbot):
        """Test ResultsSection initialization"""
        from UI.views.Results import ResultsSection
        
        results = ResultsSection()
        qtbot.addWidget(results)
        assert results is not None


if __name__ == "__main__":
    pytest.main([__file__])
