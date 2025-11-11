"""
Pytest configuration for test suite

This file provides shared fixtures and configuration for all tests.

pytest-qt is disabled by default in pytest.ini to avoid conflicts with
tests that mock PySide6. UI tests will automatically enable pytest-qt
when needed.
"""

import pytest
import sys


def pytest_configure(config):
    """Configure pytest markers and settings"""
    # The 'ui' marker is already defined in pytest.ini
    pass


@pytest.fixture(scope='session')
def qapp(request):
    """Session-wide QApplication instance for UI tests"""
    # Only create QApplication for UI tests
    if not any(request.node.iter_markers('ui')):
        pytest.skip("Not a UI test")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        
        # Set high DPI attributes before creating QApplication
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        yield app
        
    except ImportError as e:
        pytest.skip(f"PySide6 not available: {e}")


@pytest.fixture
def qtbot(qapp):
    """Minimal qtbot fixture replacement for UI tests"""
    class QtBot:
        """Minimal QtBot implementation"""
        def __init__(self, app):
            self.app = app
            self._widgets = []
        
        def addWidget(self, widget):
            """Track widget for cleanup"""
            self._widgets.append(widget)
            return widget
        
        def wait(self, ms):
            """Wait for ms milliseconds"""
            from PySide6.QtCore import QTimer, QEventLoop
            loop = QEventLoop()
            QTimer.singleShot(ms, loop.quit)
            loop.exec()
        
        def cleanup(self):
            """Clean up widgets"""
            for widget in self._widgets:
                try:
                    widget.close()
                    widget.deleteLater()
                except:
                    pass
            self._widgets.clear()
    
    bot = QtBot(qapp)
    yield bot
    bot.cleanup()
