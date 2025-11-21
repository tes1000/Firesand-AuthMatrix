"""
Test suite for Headers Delete All functionality

These tests require pytest-qt to be enabled. Run with:
    pytest -p pytest-qt tests/test_headers_delete_all.py -m ui

Or mark them with the 'ui' marker and run:
    pytest -m ui -p pytest-qt
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mark all tests in this module as UI tests
pytestmark = pytest.mark.ui


class TestHeadersDeleteAll:
    """Test Headers Delete All button functionality"""

    def test_delete_all_button_exists(self, qtbot):
        """Test that Delete All button is present in the UI"""
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets

        store = SpecStore()
        headers = KVRow(
            on_add=lambda k, v: store.set_header(k, v),
            on_remove_key=lambda k: store.remove_header(k),
            store=store,
        )
        qtbot.addWidget(headers)

        # Find Delete All button
        delete_all_buttons = [
            widget
            for widget in headers.findChildren(QtWidgets.QPushButton)
            if widget.text() == "Delete All"
        ]

        assert len(delete_all_buttons) == 1, "Delete All button should exist"

    def test_delete_all_removes_headers(self, qtbot):
        """Test that Delete All removes all headers"""
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets

        store = SpecStore()
        # Add multiple headers
        store.spec["default_headers"] = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
            "X-Custom-Header": "value",
        }

        headers = KVRow(
            on_add=lambda k, v: store.set_header(k, v),
            on_remove_key=lambda k: store.remove_header(k),
            store=store,
        )
        qtbot.addWidget(headers)

        # Mock QMessageBox to auto-accept
        with patch(
            "PySide6.QtWidgets.QMessageBox.question",
            return_value=QtWidgets.QMessageBox.Yes,
        ):
            # Trigger delete all
            headers._delete_all_headers()

        # Verify headers are reset to default
        assert store.spec["default_headers"] == {"Accept": "application/json"}

    def test_delete_all_confirmation_cancel(self, qtbot):
        """Test that canceling Delete All keeps headers"""
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets

        store = SpecStore()
        # Add multiple headers
        original_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
            "X-Custom-Header": "value",
        }
        store.spec["default_headers"] = original_headers.copy()

        headers = KVRow(
            on_add=lambda k, v: store.set_header(k, v),
            on_remove_key=lambda k: store.remove_header(k),
            store=store,
        )
        qtbot.addWidget(headers)

        # Mock QMessageBox to auto-reject
        with patch(
            "PySide6.QtWidgets.QMessageBox.question",
            return_value=QtWidgets.QMessageBox.No,
        ):
            # Trigger delete all
            headers._delete_all_headers()

        # Verify headers are unchanged
        assert store.spec["default_headers"] == original_headers

    def test_delete_all_with_no_headers(self, qtbot):
        """Test Delete All with no headers shows info message"""
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets

        store = SpecStore()
        store.spec["default_headers"] = {}

        headers = KVRow(
            on_add=lambda k, v: store.set_header(k, v),
            on_remove_key=lambda k: store.remove_header(k),
            store=store,
        )
        qtbot.addWidget(headers)

        # Mock QMessageBox.information to verify it's called
        with patch("PySide6.QtWidgets.QMessageBox.information") as mock_info:
            # Trigger delete all
            headers._delete_all_headers()

            # Verify information dialog was shown
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            assert "No Headers" in args[1]

    def test_delete_all_updates_ui(self, qtbot):
        """Test that Delete All updates the UI table"""
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets

        store = SpecStore()
        # Add multiple headers
        store.spec["default_headers"] = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
            "X-Custom-Header": "value",
        }

        headers = KVRow(
            on_add=lambda k, v: store.set_header(k, v),
            on_remove_key=lambda k: store.remove_header(k),
            store=store,
        )
        qtbot.addWidget(headers)

        # Verify initial row count
        assert headers.list.rowCount() == 3

        # Mock QMessageBox to auto-accept
        with patch(
            "PySide6.QtWidgets.QMessageBox.question",
            return_value=QtWidgets.QMessageBox.Yes,
        ):
            # Trigger delete all
            headers._delete_all_headers()

        # Wait for UI to update
        qtbot.wait(100)

        # Verify row count is updated (should have 1 row for Accept header)
        assert headers.list.rowCount() == 1
        # Verify the remaining header is Accept
        assert headers.list.item(0, 0).text() == "Accept"

    def test_delete_all_button_styling(self, qtbot):
        """Test that Delete All button has red styling"""
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets

        store = SpecStore()
        headers = KVRow(
            on_add=lambda k, v: store.set_header(k, v),
            on_remove_key=lambda k: store.remove_header(k),
            store=store,
        )
        qtbot.addWidget(headers)

        # Find Delete All button
        delete_all_buttons = [
            widget
            for widget in headers.findChildren(QtWidgets.QPushButton)
            if widget.text() == "Delete All"
        ]

        assert len(delete_all_buttons) == 1
        button = delete_all_buttons[0]

        # Verify button has red background styling
        style_sheet = button.styleSheet()
        assert "#d32f2f" in style_sheet or "background-color" in style_sheet.lower()

    def test_delete_all_emits_signal(self, qtbot):
        """Test that Delete All emits specChanged signal"""
        from UI.views.Headers import KVRow
        from UI.views.SpecStore import SpecStore
        from PySide6 import QtWidgets

        store = SpecStore()
        store.spec["default_headers"] = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
        }

        headers = KVRow(
            on_add=lambda k, v: store.set_header(k, v),
            on_remove_key=lambda k: store.remove_header(k),
            store=store,
        )
        qtbot.addWidget(headers)

        # Connect signal spy
        signal_emitted = []
        store.specChanged.connect(lambda: signal_emitted.append(True))

        # Mock QMessageBox to auto-accept
        with patch(
            "PySide6.QtWidgets.QMessageBox.question",
            return_value=QtWidgets.QMessageBox.Yes,
        ):
            # Trigger delete all
            headers._delete_all_headers()

        # Verify signal was emitted
        assert len(signal_emitted) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
