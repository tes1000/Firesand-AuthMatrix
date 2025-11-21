"""
Test suite for SpinnerWidget component

Tests the spinner widget used for loading indicators in the results table.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mark all tests in this module as UI tests
pytestmark = pytest.mark.ui


class TestSpinnerWidget:
    """Test SpinnerWidget component"""
    
    def test_spinner_widget_init(self, qtbot):
        """Test SpinnerWidget initialization"""
        from UI.components.SpinnerWidget import SpinnerWidget
        
        spinner = SpinnerWidget()
        qtbot.addWidget(spinner)
        
        assert spinner is not None
        assert spinner.size == 16
        assert not spinner.isRunning()
    
    def test_spinner_widget_custom_size(self, qtbot):
        """Test SpinnerWidget with custom size"""
        from UI.components.SpinnerWidget import SpinnerWidget
        
        spinner = SpinnerWidget(size=24)
        qtbot.addWidget(spinner)
        
        assert spinner.size == 24
        assert spinner.width() == 24
        assert spinner.height() == 24
    
    def test_spinner_start_stop(self, qtbot):
        """Test spinner start and stop methods"""
        from UI.components.SpinnerWidget import SpinnerWidget
        
        spinner = SpinnerWidget()
        qtbot.addWidget(spinner)
        
        # Initially not running
        assert not spinner.isRunning()
        
        # Start animation
        spinner.start()
        assert spinner.isRunning()
        
        # Stop animation
        spinner.stop()
        assert not spinner.isRunning()
    
    def test_spinner_auto_start_on_show(self, qtbot):
        """Test spinner automatically starts when shown"""
        from UI.components.SpinnerWidget import SpinnerWidget
        
        spinner = SpinnerWidget()
        qtbot.addWidget(spinner)
        
        # Initially hidden and not running
        spinner.hide()
        spinner.stop()
        assert not spinner.isRunning()
        
        # Show the spinner
        spinner.show()
        # Give it a moment to process the show event
        qtbot.wait(10)
        
        # Should now be running
        assert spinner.isRunning()
    
    def test_spinner_auto_stop_on_hide(self, qtbot):
        """Test spinner automatically stops when hidden"""
        from UI.components.SpinnerWidget import SpinnerWidget
        
        spinner = SpinnerWidget()
        qtbot.addWidget(spinner)
        
        # Start and show the spinner
        spinner.show()
        spinner.start()
        assert spinner.isRunning()
        
        # Hide the spinner
        spinner.hide()
        # Give it a moment to process the hide event
        qtbot.wait(10)
        
        # Should now be stopped
        assert not spinner.isRunning()
    
    def test_spinner_color_change(self, qtbot):
        """Test changing spinner color"""
        from UI.components.SpinnerWidget import SpinnerWidget
        from PySide6.QtGui import QColor
        
        spinner = SpinnerWidget()
        qtbot.addWidget(spinner)
        
        # Change color
        new_color = QColor("#0000FF")
        spinner.setColor(new_color)
        
        # Verify color is set
        assert spinner._color == new_color
    
    def test_spinner_rotation(self, qtbot):
        """Test spinner rotation animation"""
        from UI.components.SpinnerWidget import SpinnerWidget
        
        spinner = SpinnerWidget()
        qtbot.addWidget(spinner)
        
        initial_angle = spinner._rotation_angle
        
        # Start animation and wait
        spinner.start()
        qtbot.wait(100)
        
        # Rotation angle should have changed
        assert spinner._rotation_angle != initial_angle
        
        spinner.stop()


class TestResultsSectionWithSpinner:
    """Test Results section with spinner integration"""
    
    def test_results_section_init(self, qtbot):
        """Test ResultsSection initialization with spinner tracking"""
        from UI.views.Results import ResultsSection
        
        results = ResultsSection()
        qtbot.addWidget(results)
        
        assert results is not None
        assert hasattr(results, '_spinners')
        assert isinstance(results._spinners, dict)
        assert len(results._spinners) == 0
    
    def test_results_render_with_pending_status(self, qtbot):
        """Test rendering results with pending (spinner) status"""
        from UI.views.Results import ResultsSection
        
        results = ResultsSection()
        qtbot.addWidget(results)
        
        # Create test data with pending status
        test_results = {
            "GET /api/users": {
                "admin": {"status": "⏳"},
                "user": {"status": "⏳"}
            }
        }
        
        # Render the results
        results.render(test_results)
        
        # Wait for rendering to complete
        qtbot.wait(50)
        
        # Verify table structure
        assert results.table.rowCount() == 1
        assert results.table.columnCount() == 3  # Endpoint + 2 roles
        
        # Verify spinners were created
        assert len(results._spinners) == 2  # One for each role
        assert (0, 1) in results._spinners  # admin column
        assert (0, 2) in results._spinners  # user column
        
        # Verify spinners are running
        for spinner in results._spinners.values():
            assert spinner.isRunning()
    
    def test_results_update_replaces_spinner(self, qtbot):
        """Test that updating a result replaces the spinner with actual result"""
        from UI.views.Results import ResultsSection
        
        results = ResultsSection()
        qtbot.addWidget(results)
        
        # Create test data with pending status
        test_results = {
            "GET /api/users": {
                "admin": {"status": "⏳"},
                "user": {"status": "⏳"}
            }
        }
        
        # Render with pending status
        results.render(test_results)
        qtbot.wait(50)
        
        # Verify spinner exists
        assert (0, 1) in results._spinners
        
        # Update with actual result
        results.update_result("GET /api/users", "admin", {
            "status": "PASS",
            "http": 200,
            "latency_ms": 45
        })
        qtbot.wait(50)
        
        # Verify spinner was removed
        assert (0, 1) not in results._spinners
        
        # Verify result is displayed
        item = results.table.item(0, 1)
        assert item is not None
        assert "✅" in item.text()
        assert "200" in item.text()
        assert "45ms" in item.text()
    
    def test_results_cleanup_spinners(self, qtbot):
        """Test that spinners are properly cleaned up"""
        from UI.views.Results import ResultsSection
        
        results = ResultsSection()
        qtbot.addWidget(results)
        
        # Create test data with pending status
        test_results = {
            "GET /api/users": {
                "admin": {"status": "⏳"}
            }
        }
        
        # Render with pending status
        results.render(test_results)
        qtbot.wait(50)
        
        # Verify spinner exists and is running
        assert len(results._spinners) == 1
        spinner = list(results._spinners.values())[0]
        assert spinner.isRunning()
        
        # Clear the table (simulating a new render)
        results.render({})
        qtbot.wait(50)
        
        # Verify spinner was cleaned up
        assert len(results._spinners) == 0
        assert not spinner.isRunning()
    
    def test_results_mixed_status(self, qtbot):
        """Test rendering with mixed status (pending, pass, fail, skip)"""
        from UI.views.Results import ResultsSection
        
        results = ResultsSection()
        qtbot.addWidget(results)
        
        # Create test data with mixed status
        test_results = {
            "GET /api/users": {
                "admin": {"status": "⏳"},  # Pending
                "user": {"status": "PASS", "http": 200, "latency_ms": 50},
                "guest": {"status": "FAIL", "http": 403}
            },
            "GET /api/admin": {
                "admin": {"status": "PASS", "http": 200, "latency_ms": 30},
                "user": {"status": "SKIP"},
                "guest": {"status": "⏳"}  # Pending
            }
        }
        
        # Render the results
        results.render(test_results)
        qtbot.wait(50)
        
        # Verify spinners were created only for pending status
        assert len(results._spinners) == 2
        assert (0, 1) in results._spinners  # Row 0 (users), Col 1 (admin)
        assert (1, 3) in results._spinners  # Row 1 (admin), Col 3 (guest)
        
        # Verify non-pending results are displayed as items
        user_item = results.table.item(0, 2)  # user for /api/users
        assert user_item is not None
        assert "✅" in user_item.text()
        
        skip_item = results.table.item(1, 2)  # user for /api/admin
        assert skip_item is not None
        assert "⏭️" in skip_item.text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
