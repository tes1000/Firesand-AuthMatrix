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
    
    def test_configure_all_endpoints_dialog_full_width(self, qtbot):
        """Test ConfigureAllEndpointsDialog uses full-width sizing"""
        from UI.views.Endpoints import ConfigureAllEndpointsDialog
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets
        
        store = SpecStore()
        # Add at least one endpoint to avoid the "No Endpoints" message
        store.spec["endpoints"] = [
            {"name": "Test", "method": "GET", "path": "/test"}
        ]
        
        dialog = ConfigureAllEndpointsDialog(store)
        qtbot.addWidget(dialog)
        
        # Verify dialog was created
        assert dialog is not None
        
        # Get screen dimensions to verify sizing
        screen = QtWidgets.QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            expected_width = min(int(available.width() * 0.9), 1600)
            expected_height = min(int(available.height() * 0.7), 800)
            
            # Check that dialog size matches expected full-width dimensions
            assert dialog.width() == expected_width
            assert dialog.height() == expected_height
        else:
            # Fallback case
            assert dialog.width() == 1200
            assert dialog.height() == 700


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
