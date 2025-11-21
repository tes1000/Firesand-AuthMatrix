"""
Test suite for MultiCollectionExportDialog UI rendering
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import PySide6 after path setup to avoid import issues
from PySide6 import QtWidgets, QtCore

from UI.UI import MultiCollectionExportDialog


@pytest.fixture
def qapp():
    """Create QApplication instance for tests"""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    yield app


@pytest.mark.ui
class TestMultiCollectionExportDialogRendering:
    """Test that MultiCollectionExportDialog renders correctly"""

    def test_dialog_not_blank(self, qapp, qtbot):
        """Test that dialog has content and is not blank"""
        # Create test collections
        collections = {
            "admin": '{"info": {"name": "Admin Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, "item": [{"name": "Admin Endpoint", "request": {"method": "GET", "url": "https://api.test.com/admin"}}], "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "admin-token"}]}}',
            "user": '{"info": {"name": "User Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, "item": [{"name": "User Endpoint", "request": {"method": "GET", "url": "https://api.test.com/user"}}], "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "user-token"}]}}',
        }

        # Create the dialog
        dialog = MultiCollectionExportDialog(collections)
        qtbot.addWidget(dialog)

        # Verify dialog has a layout
        assert dialog.layout() is not None, "Dialog should have a layout"

        # Verify layout has children (widgets)
        layout = dialog.layout()
        assert layout.count() > 0, "Layout should have widgets"

        # Verify there's a tab widget for collections
        tab_widget = None
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and isinstance(item.widget(), QtWidgets.QTabWidget):
                tab_widget = item.widget()
                break

        assert tab_widget is not None, "Dialog should have a QTabWidget for collections"
        assert tab_widget.count() == 2, "Tab widget should have 2 tabs (admin, user)"

        # Verify tabs have the correct names
        tab_names = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        assert "Admin" in tab_names or "User" in tab_names, "Tabs should be named after roles"

    def test_dialog_has_info_label(self, qapp, qtbot):
        """Test that dialog has an info label at the top"""
        collections = {
            "admin": '{"info": {"name": "Admin Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, "item": [], "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "admin-token"}]}}',
        }

        dialog = MultiCollectionExportDialog(collections)
        qtbot.addWidget(dialog)

        # Find the info label
        layout = dialog.layout()
        info_label = None
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and isinstance(item.widget(), QtWidgets.QLabel):
                info_label = item.widget()
                break

        assert info_label is not None, "Dialog should have an info QLabel"
        assert "1 Postman collection" in info_label.text(), "Info label should show collection count"

    def test_dialog_has_buttons(self, qapp, qtbot):
        """Test that dialog has action buttons"""
        collections = {
            "admin": '{"info": {"name": "Admin Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, "item": []}',
        }

        dialog = MultiCollectionExportDialog(collections)
        qtbot.addWidget(dialog)

        # Find buttons by walking the widget tree
        buttons = dialog.findChildren(QtWidgets.QPushButton)

        assert len(buttons) > 0, "Dialog should have buttons"

        # Look for "Save All Collections..." and "Close" buttons
        button_texts = [btn.text() for btn in buttons]
        assert any("Save All" in text for text in button_texts), "Should have 'Save All Collections...' button"
        assert any("Close" in text for text in button_texts), "Should have 'Close' button"

    def test_dialog_with_multiple_collections(self, qapp, qtbot):
        """Test dialog with multiple collections creates all tabs"""
        collections = {
            "guest": '{"info": {"name": "Guest Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, "item": []}',
            "user": '{"info": {"name": "User Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, "item": []}',
            "admin": '{"info": {"name": "Admin Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, "item": []}',
        }

        dialog = MultiCollectionExportDialog(collections)
        qtbot.addWidget(dialog)

        # Find tab widget
        tab_widget = dialog.findChild(QtWidgets.QTabWidget)
        assert tab_widget is not None, "Dialog should have a QTabWidget"
        assert tab_widget.count() == 3, "Tab widget should have 3 tabs"

    def test_dialog_tab_contains_text_edit(self, qapp, qtbot):
        """Test that each tab contains a text edit showing JSON"""
        collections = {
            "admin": '{"info": {"name": "Admin Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, "item": []}',
        }

        dialog = MultiCollectionExportDialog(collections)
        qtbot.addWidget(dialog)

        # Find tab widget and get first tab
        tab_widget = dialog.findChild(QtWidgets.QTabWidget)
        assert tab_widget is not None

        first_tab = tab_widget.widget(0)
        assert first_tab is not None

        # Find text edit in the tab
        text_edit = first_tab.findChild(QtWidgets.QPlainTextEdit)
        assert text_edit is not None, "Tab should contain a QPlainTextEdit"
        assert len(text_edit.toPlainText()) > 0, "Text edit should contain JSON"
        assert '"info"' in text_edit.toPlainText(), "Text edit should show collection JSON"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
