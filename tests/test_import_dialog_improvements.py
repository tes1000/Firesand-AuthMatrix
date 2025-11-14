"""
Tests for ImportDialog improvements
"""
import pytest
from PySide6 import QtWidgets, QtCore
from unittest.mock import Mock, patch, mock_open
from UI.UI import ImportDialog
from UI.views.SpecStore import SpecStore


@pytest.mark.ui
class TestImportDialogSize:
    """Test that ImportDialog has the correct size"""
    
    def test_import_dialog_is_smaller(self, qtbot):
        """Test that the dialog has reduced minimum size"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        # Check minimum size is smaller than before (was 500x400)
        assert dialog.minimumSize().width() == 400
        assert dialog.minimumSize().height() == 250
        
        # Size should be reasonable
        assert dialog.size().width() >= 400
        assert dialog.size().height() >= 250

@pytest.mark.ui
class TestImportDialogFileButtons:
    """Test file browser import functionality"""
    
    def test_authmatrix_has_file_button(self, qtbot):
        """Test that AuthMatrix page has file import button"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        # Switch to AuthMatrix page
        dialog.authmatrix_radio.setChecked(True)
        qtbot.wait(10)
        
        # Find file import button
        page = dialog.content_stack.currentWidget()
        buttons = page.findChildren(QtWidgets.QPushButton)
        file_buttons = [b for b in buttons if "Import from File" in b.text()]
        
        assert len(file_buttons) == 1
        assert "📁" in file_buttons[0].text()
    
    def test_single_postman_has_file_button(self, qtbot):
        """Test that Single Postman page has file import button"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        # Switch to Single Postman page
        dialog.single_postman_radio.setChecked(True)
        qtbot.wait(10)
        
        # Find file import button
        page = dialog.content_stack.currentWidget()
        buttons = page.findChildren(QtWidgets.QPushButton)
        file_buttons = [b for b in buttons if "Import from File" in b.text()]
        
        assert len(file_buttons) == 1
        assert "📁" in file_buttons[0].text()
    
    def test_text_areas_are_collapsible(self, qtbot):
        """Test that text input areas are in collapsible groups"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        # Check AuthMatrix page
        dialog.authmatrix_radio.setChecked(True)
        qtbot.wait(10)
        
        page = dialog.content_stack.currentWidget()
        group_boxes = page.findChildren(QtWidgets.QGroupBox)
        text_groups = [g for g in group_boxes if "paste content" in g.title().lower()]
        
        assert len(text_groups) >= 1
        assert text_groups[0].isCheckable()
        
        # Check Single Postman page
        dialog.single_postman_radio.setChecked(True)
        qtbot.wait(10)
        
        page = dialog.content_stack.currentWidget()
        group_boxes = page.findChildren(QtWidgets.QGroupBox)
        text_groups = [g for g in group_boxes if "paste content" in g.title().lower()]
        
        assert len(text_groups) >= 1
        assert text_groups[0].isCheckable()


@pytest.mark.ui
class TestImportDialogFileImport:
    """Test file import functionality"""
    
    def test_import_authmatrix_from_file_success(self, qtbot, tmp_path):
        """Test importing AuthMatrix from file"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        # Create a test file
        test_file = tmp_path / "test_authmatrix.json"
        test_content = '{"base_url": "http://test.com", "default_headers": {}, "roles": {}, "endpoints": []}'
        test_file.write_text(test_content)
        
        # Mock file dialog to return our test file
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=(str(test_file), '')):
            dialog._import_authmatrix_from_file()
        
        # Check that spec was loaded
        assert store.spec.get('base_url') == 'http://test.com'
    
    def test_import_authmatrix_from_file_cancelled(self, qtbot):
        """Test cancelling file import"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        original_spec = dict(store.spec)
        
        # Mock file dialog to return empty (cancelled)
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=('', '')):
            dialog._import_authmatrix_from_file()
        
        # Spec should not change
        assert store.spec == original_spec
    
    def test_import_authmatrix_from_file_invalid(self, qtbot, tmp_path):
        """Test importing invalid AuthMatrix from file"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        # Create a test file with invalid content
        test_file = tmp_path / "invalid.json"
        test_file.write_text('{"invalid": "format"}')
        
        # Mock file dialog and message box
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=(str(test_file), '')):
            with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_msg:
                dialog._import_authmatrix_from_file()
                
                # Should show error message
                assert mock_msg.called
    
    def test_import_single_postman_from_file_success(self, qtbot, tmp_path):
        """Test importing Postman collection from file"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        # Create a test Postman collection
        test_file = tmp_path / "test_postman.json"
        test_content = '''
        {
            "info": {"name": "Test Collection"},
            "item": [{
                "name": "Test Request",
                "request": {
                    "method": "GET",
                    "url": "http://test.com/api/test"
                }
            }]
        }
        '''
        test_file.write_text(test_content)
        
        # Mock file dialog and config dialog
        with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=(str(test_file), '')):
            with patch('UI.UI.PostmanConfigDialog') as mock_config:
                mock_config.return_value.exec.return_value = QtWidgets.QDialog.Accepted
                dialog._import_single_postman_from_file()
        
        # Check that endpoints were loaded
        assert len(store.spec.get('endpoints', [])) > 0


@pytest.mark.ui
class TestImportDialogWarningMessages:
    """Test updated warning messages"""
    
    def test_authmatrix_empty_warning_mentions_file_button(self, qtbot):
        """Test that warning message mentions file import option"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        dialog.authmatrix_radio.setChecked(True)
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._import_authmatrix()
            
            assert mock_warning.called
            call_args = mock_warning.call_args[0]
            message = call_args[2]
            assert "Import from File" in message or "file" in message.lower()
    
    def test_single_postman_empty_warning_mentions_file_button(self, qtbot):
        """Test that warning message mentions file import option"""
        store = SpecStore()
        dialog = ImportDialog(store)
        qtbot.addWidget(dialog)
        
        dialog.single_postman_radio.setChecked(True)
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._import_single_postman()
            
            assert mock_warning.called
            call_args = mock_warning.call_args[0]
            message = call_args[2]
            assert "Import from File" in message or "file" in message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
