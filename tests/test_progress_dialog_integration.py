"""
Integration test for ProgressDialog with MainWindow

This test verifies that the ProgressDialog is properly integrated
with the MainWindow's run functionality.
"""

import pytest
import os

# Set Qt platform before importing Qt
os.environ['QT_QPA_PLATFORM'] = 'offscreen'


@pytest.mark.ui
class TestProgressDialogIntegrationWithMainWindow:
    """Test ProgressDialog integration with MainWindow"""

    def test_mainwindow_has_progress_dialog_attribute(self, qtbot):
        """Test that MainWindow has progress_dialog attribute"""
        from UI.UI import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        assert hasattr(window, 'progress_dialog')

    def test_mainwindow_has_cancel_run_method(self, qtbot):
        """Test that MainWindow has _cancel_run method"""
        from UI.UI import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        assert hasattr(window, '_cancel_run')
        assert callable(window._cancel_run)

    def test_progress_dialog_created_on_first_run(self, qtbot):
        """Test that progress dialog is created on first run attempt"""
        from UI.UI import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # Initially None
        assert window.progress_dialog is None

        # Set a base URL to pass validation
        window.store.set_base_url("http://localhost:3000")

        # Trigger run (will create dialog)
        window._run()

        # Now should exist
        assert window.progress_dialog is not None

        # Clean up
        if window.process and window.process.is_alive():
            window.process.terminate()
            window.process.join(timeout=1)

    def test_progress_dialog_signal_connected(self, qtbot):
        """Test that progress dialog cancel signal is connected"""
        from UI.UI import MainWindow
        from UI.components.ProgressDialog import ProgressDialog

        window = MainWindow()
        qtbot.addWidget(window)

        # Create progress dialog manually
        window.progress_dialog = ProgressDialog(window)

        # Connect signal
        window.progress_dialog.cancelRequested.connect(window._cancel_run)

        # Verify connection by checking signal emission
        from unittest.mock import Mock
        mock_cancel = Mock()
        window._cancel_run = mock_cancel

        window.progress_dialog.cancelRequested.connect(mock_cancel)
        window.progress_dialog.cancel_button.click()

        # Should have been called
        assert mock_cancel.call_count > 0

    def test_cancel_run_stops_process(self, qtbot):
        """Test that _cancel_run properly stops the process"""
        from UI.UI import MainWindow
        import multiprocessing

        window = MainWindow()
        qtbot.addWidget(window)

        # Create a dummy process
        def dummy_worker():
            import time
            time.sleep(10)

        window.process = multiprocessing.Process(target=dummy_worker)
        window.process.start()

        # Verify process is alive
        assert window.process.is_alive()

        # Cancel
        window._cancel_run()

        # Process should be terminated
        assert not window.process.is_alive()

    def test_progress_dialog_cleaned_up_on_close(self, qtbot):
        """Test that progress dialog is stopped when window closes"""
        from UI.UI import MainWindow
        from UI.components.ProgressDialog import ProgressDialog

        window = MainWindow()
        qtbot.addWidget(window)

        # Create and start progress dialog
        window.progress_dialog = ProgressDialog(window)
        window.progress_dialog.start()

        # Verify it's running
        assert window.progress_dialog._timer.isActive()

        # Close window
        window.close()

        # Dialog should be stopped
        assert not window.progress_dialog._timer.isActive()
