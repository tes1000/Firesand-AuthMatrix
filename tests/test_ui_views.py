"""
Test suite for UI views (skipped - requires PySide6 initialization)
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Skip all UI view tests unless explicitly running with pytest-qt
pytestmark = pytest.mark.skip(reason="UI tests require PySide6 and pytest-qt. Run manually with: pytest tests/test_ui_components.py tests/test_ui_views.py after 'pip install pytest-qt'")


class TestHeadersSection:
    """Test Headers view"""
    
    def test_headers_section_init(self):
        """Test HeadersSection initialization"""
        from PySide6.QtWidgets import QApplication
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        
        app = QApplication.instance() or QApplication([])
        store = SpecStore()
        # KVRow needs callbacks for on_add and on_remove_key
        headers = KVRow(lambda: None, lambda k: None, store)
        assert headers is not None


class TestTokensSection:
    """Test Tokens view"""
    
    def test_tokens_section_init(self):
        """Test TokensSection initialization"""
        from PySide6.QtWidgets import QApplication
        from UI.views.Tokens import TokensSection
        from UI.views.SpecStore import SpecStore
        
        app = QApplication.instance() or QApplication([])
        store = SpecStore()
        tokens = TokensSection(store)
        assert tokens is not None


class TestEndpointsSection:
    """Test Endpoints view"""
    
    def test_endpoints_section_init(self):
        """Test EndpointsSection initialization"""
        from PySide6.QtWidgets import QApplication
        from UI.views.Endpoints import EndpointsSection
        from UI.views.SpecStore import SpecStore
        
        app = QApplication.instance() or QApplication([])
        store = SpecStore()
        endpoints = EndpointsSection(store)
        assert endpoints is not None


class TestResultsSection:
    """Test Results view"""
    
    def test_results_section_init(self):
        """Test ResultsSection initialization"""
        from PySide6.QtWidgets import QApplication
        from UI.views.Results import ResultsSection
        
        app = QApplication.instance() or QApplication([])
        results = ResultsSection()
        assert results is not None


if __name__ == "__main__":
    pytest.main([__file__])
