"""
Test suite for UI components (skipped - requires PySide6 initialization)
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Skip all UI component tests unless explicitly running with pytest-qt
pytestmark = pytest.mark.skip(reason="UI tests require PySide6 and pytest-qt. Run manually with: pytest tests/test_ui_components.py tests/test_ui_views.py after 'pip install pytest-qt'")


class TestLogoHeader:
    """Test LogoHeader component"""
    
    def test_logo_header_init(self):
        """Test LogoHeader initialization"""
        from PySide6.QtWidgets import QApplication
        from UI.components.LogoHeader import LogoHeader
        
        app = QApplication.instance() or QApplication([])
        logo_header = LogoHeader()
        assert logo_header is not None

    def test_logo_header_signals(self):
        """Test LogoHeader signal emissions"""
        from PySide6.QtWidgets import QApplication
        from UI.components.LogoHeader import LogoHeader
        
        app = QApplication.instance() or QApplication([])
        logo_header = LogoHeader()
        
        # Test that signal attributes exist
        assert hasattr(logo_header, 'importRequested')
        assert hasattr(logo_header, 'exportRequested') 
        assert hasattr(logo_header, 'runRequested')


class TestTabsComponent:
    """Test TabsComponent"""
    
    def test_tabs_component_init(self):
        """Test TabsComponent initialization"""
        from PySide6.QtWidgets import QApplication
        from UI.components.TabsComponent import TabsComponent
        from UI.views.SpecStore import SpecStore
        
        app = QApplication.instance() or QApplication([])
        store = SpecStore()
        tabs = TabsComponent(store)
        assert tabs is not None
    
    def test_tabs_component_getters(self):
        """Test TabsComponent getter methods"""
        from PySide6.QtWidgets import QApplication
        from UI.components.TabsComponent import TabsComponent
        from UI.views.SpecStore import SpecStore
        
        app = QApplication.instance() or QApplication([])
        store = SpecStore()
        tabs = TabsComponent(store)
        
        # Should return the sections
        headers = tabs.get_headers()
        endpoints = tabs.get_endpoints()  
        tokens = tabs.get_tokens()
        
        assert headers is not None
        assert endpoints is not None
        assert tokens is not None


if __name__ == "__main__":
    pytest.main([__file__])
