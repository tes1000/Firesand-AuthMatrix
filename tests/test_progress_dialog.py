"""
Tests for ProgressDialog component

These tests verify the progress dialog functionality including:
- Initialization and UI creation
- Spinner animation
- Message and detail updates
- Cancel button functionality
- Dialog lifecycle (start/stop/reset)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6 import QtCore, QtWidgets
from UI.components.ProgressDialog import ProgressDialog


@pytest.mark.ui
class TestProgressDialog:
    """Test suite for ProgressDialog component"""
    
    def test_dialog_initialization(self, qtbot):
        """Test that dialog initializes with correct properties"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Check basic properties
        assert dialog.windowTitle() == "Running Tests"
        assert dialog.isModal()
        assert dialog.minimumSize().width() == 400
        assert dialog.minimumSize().height() == 200
        
    def test_dialog_ui_components_created(self, qtbot):
        """Test that all UI components are created"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Check required components exist
        assert hasattr(dialog, 'spinner_label')
        assert hasattr(dialog, 'message_label')
        assert hasattr(dialog, 'detail_label')
        assert hasattr(dialog, 'cancel_button')
        
        # Check spinner label properties
        assert dialog.spinner_label.size() == QtCore.QSize(60, 60)
        
        # Check message label has text
        assert dialog.message_label.text() == "Sending requests..."
        
    def test_cancel_signal_emitted(self, qtbot):
        """Test that cancel button emits cancelRequested signal"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Connect signal to mock
        mock_handler = Mock()
        dialog.cancelRequested.connect(mock_handler)
        
        # Click cancel button
        dialog.cancel_button.click()
        
        # Verify signal was emitted
        mock_handler.assert_called_once()
        
    def test_cancel_button_disabled_after_click(self, qtbot):
        """Test that cancel button is disabled after clicking"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Initially enabled
        assert dialog.cancel_button.isEnabled()
        
        # Click cancel
        dialog.cancel_button.click()
        
        # Should be disabled now
        assert not dialog.cancel_button.isEnabled()
        assert dialog.cancel_button.text() == "Cancelling..."
        
    def test_set_message(self, qtbot):
        """Test updating the main message"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        test_message = "Testing endpoints..."
        dialog.set_message(test_message)
        
        assert dialog.message_label.text() == test_message
        
    def test_set_detail(self, qtbot):
        """Test updating the detail text"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        test_detail = "Completed 5 of 10 requests"
        dialog.set_detail(test_detail)
        
        assert dialog.detail_label.text() == test_detail
        
    def test_start_begins_animation(self, qtbot):
        """Test that start() begins the spinner animation"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Start should start the timer
        dialog.start()
        
        assert dialog._timer.isActive()
        assert dialog.isVisible()
        
        # Clean up
        dialog.stop()
        
    def test_stop_ends_animation(self, qtbot):
        """Test that stop() ends the spinner animation"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Start then stop
        dialog.start()
        assert dialog._timer.isActive()
        
        dialog.stop()
        assert not dialog._timer.isActive()
        assert not dialog.isVisible()
        
    def test_reset_restores_initial_state(self, qtbot):
        """Test that reset() restores dialog to initial state"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Modify state
        dialog.set_message("Custom message")
        dialog.set_detail("Custom detail")
        dialog.cancel_button.setEnabled(False)
        dialog.cancel_button.setText("Modified")
        
        # Reset
        dialog.reset()
        
        # Verify initial state restored
        assert dialog.cancel_button.isEnabled()
        assert dialog.cancel_button.text() == "Cancel"
        assert dialog.message_label.text() == "Sending requests..."
        assert dialog.detail_label.text() == ""
        assert dialog._rotation_angle == 0
        
    def test_spinner_animation_updates_rotation(self, qtbot):
        """Test that spinner animation updates rotation angle"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        initial_angle = dialog._rotation_angle
        
        # Trigger update
        dialog._update_spinner()
        
        # Rotation should have changed
        assert dialog._rotation_angle != initial_angle
        
    def test_spinner_rotation_wraps_at_360(self, qtbot):
        """Test that spinner rotation wraps around at 360 degrees"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Set angle near 360
        dialog._rotation_angle = 355
        
        # Update spinner
        dialog._update_spinner()
        
        # Should wrap around
        assert dialog._rotation_angle < 360
        
    def test_spinner_pixmap_creation(self, qtbot):
        """Test that spinner creates a valid pixmap"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        pixmap = dialog._create_spinner_pixmap()
        
        assert not pixmap.isNull()
        assert pixmap.size() == QtCore.QSize(60, 60)
        
    def test_close_event_ignored(self, qtbot):
        """Test that close event is ignored (prevents X button close)"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Create close event
        close_event = Mock()
        close_event.ignore = Mock()
        
        # Call closeEvent
        dialog.closeEvent(close_event)
        
        # Event should be ignored
        close_event.ignore.assert_called_once()
        
    def test_dialog_has_no_close_button(self, qtbot):
        """Test that dialog window flags prevent close button"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Check window flags
        flags = dialog.windowFlags()
        
        # Should be a dialog with custom window hint
        assert flags & QtCore.Qt.Dialog
        assert flags & QtCore.Qt.CustomizeWindowHint
        
    def test_timer_interval_is_appropriate(self, qtbot):
        """Test that timer interval provides smooth animation"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        dialog.start()
        
        # Timer should be running at 50ms intervals (20 FPS)
        assert dialog._timer.interval() == 50
        
        dialog.stop()


@pytest.mark.ui
class TestProgressDialogIntegration:
    """Integration tests for ProgressDialog"""
    
    def test_multiple_start_stop_cycles(self, qtbot):
        """Test that dialog can be started and stopped multiple times"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Multiple cycles
        for i in range(3):
            dialog.start()
            assert dialog._timer.isActive()
            assert dialog.isVisible()
            
            qtbot.wait(100)  # Wait a bit for animation
            
            dialog.stop()
            assert not dialog._timer.isActive()
            assert not dialog.isVisible()
            
    def test_reset_between_runs(self, qtbot):
        """Test resetting dialog between runs"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # First run
        dialog.set_message("First run")
        dialog.start()
        dialog.cancel_button.click()  # Disable button
        dialog.stop()
        
        # Reset for second run
        dialog.reset()
        
        # Should be ready for second run
        assert dialog.cancel_button.isEnabled()
        assert dialog.message_label.text() == "Sending requests..."
        
    def test_cancel_during_animation(self, qtbot):
        """Test cancelling while animation is running"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        mock_handler = Mock()
        dialog.cancelRequested.connect(mock_handler)
        
        # Start animation
        dialog.start()
        qtbot.wait(100)  # Let animation run
        
        # Cancel
        dialog.cancel_button.click()
        
        # Signal should be emitted even during animation
        mock_handler.assert_called_once()
        
        # Clean up
        dialog.stop()


@pytest.mark.ui  
class TestProgressDialogStyling:
    """Tests for dialog styling and appearance"""
    
    def test_dialog_has_stylesheet(self, qtbot):
        """Test that dialog has custom stylesheet applied"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        stylesheet = dialog.styleSheet()
        
        # Should have some styling
        assert len(stylesheet) > 0
        assert "QDialog" in stylesheet
        assert "QPushButton" in stylesheet
        
    def test_message_label_styling(self, qtbot):
        """Test that message label has appropriate styling"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Check message label properties
        assert dialog.message_label.wordWrap()
        assert dialog.message_label.alignment() == QtCore.Qt.AlignCenter
        
    def test_detail_label_styling(self, qtbot):
        """Test that detail label has appropriate styling"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Check detail label properties
        assert dialog.detail_label.wordWrap()
        assert dialog.detail_label.alignment() == QtCore.Qt.AlignCenter
        
    def test_cancel_button_has_fixed_width(self, qtbot):
        """Test that cancel button has fixed width for consistency"""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)
        
        # Button should have fixed width
        assert dialog.cancel_button.width() == 120


# Non-UI tests (with mocked PySide6)
class TestProgressDialogNonUI:
    """Tests that can run without full Qt application"""
    
    def test_progress_dialog_import(self):
        """Test that ProgressDialog can be imported"""
        from UI.components.ProgressDialog import ProgressDialog
        # If we get here without exception, import succeeded
        assert ProgressDialog is not None
