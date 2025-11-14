"""
Test suite for UI components

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


class TestLogoHeader:
    """Test LogoHeader component"""
    
    def test_logo_header_init(self, qtbot):
        """Test LogoHeader initialization"""
        from UI.components.LogoHeader import LogoHeader
        
        logo_header = LogoHeader()
        qtbot.addWidget(logo_header)
        assert logo_header is not None

    def test_logo_header_signals(self, qtbot):
        """Test LogoHeader signal emissions"""
        from UI.components.LogoHeader import LogoHeader
        
        logo_header = LogoHeader()
        qtbot.addWidget(logo_header)
        
        # Test that signal attributes exist
        assert hasattr(logo_header, 'importRequested')
        assert hasattr(logo_header, 'exportRequested') 
        assert hasattr(logo_header, 'runRequested')


class TestTabsComponent:
    """Test TabsComponent"""
    
    def test_tabs_component_init(self, qtbot):
        """Test TabsComponent initialization"""
        from UI.components.TabsComponent import TabsComponent
        from UI.views.SpecStore import SpecStore
        
        store = SpecStore()
        tabs = TabsComponent(store)
        qtbot.addWidget(tabs)
        assert tabs is not None
    
    def test_tabs_component_getters(self, qtbot):
        """Test TabsComponent getter methods"""
        from UI.components.TabsComponent import TabsComponent
        from UI.views.SpecStore import SpecStore
        
        store = SpecStore()
        tabs = TabsComponent(store)
        qtbot.addWidget(tabs)
        
        # Should return the sections
        headers = tabs.get_headers()
        endpoints = tabs.get_endpoints()  
        tokens = tabs.get_tokens()
        
        assert headers is not None
        assert endpoints is not None
        assert tokens is not None


if __name__ == "__main__":
    pytest.main([__file__])
