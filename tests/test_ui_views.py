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
