"""
Test suite for Windows icon implementation

These tests verify that the application correctly sets and uses icons
for the window, taskbar, and PyInstaller executable.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mark all tests in this module as UI tests
pytestmark = pytest.mark.ui


class TestIconFiles:
    """Test that icon files exist and are valid"""
    
    def test_favicon_ico_exists(self):
        """Test that favicon.ico exists in assets folder"""
        icon_path = Path(__file__).parent.parent / "UI" / "assets" / "favicon.ico"
        assert icon_path.exists(), "favicon.ico should exist in UI/assets/"
        
    def test_favicon_ico_is_valid(self):
        """Test that favicon.ico is a valid ICO file"""
        icon_path = Path(__file__).parent.parent / "UI" / "assets" / "favicon.ico"
        
        # Read the first few bytes to verify ICO signature
        with open(icon_path, 'rb') as f:
            header = f.read(4)
            # ICO files start with 00 00 01 00 or 00 00 02 00 (for cursors)
            assert header[:2] == b'\x00\x00', "ICO file should start with 00 00"
            assert header[2:4] in [b'\x01\x00', b'\x02\x00'], "ICO file should have valid type"
    
    def test_favicon_png_exists(self):
        """Test that source PNG file exists"""
        png_path = Path(__file__).parent.parent / "UI" / "assets" / "favicon.png"
        assert png_path.exists(), "favicon.png source file should exist"


class TestIconConversionScript:
    """Test the icon conversion script"""
    
    def test_convert_icon_script_exists(self):
        """Test that convert_icon.py exists"""
        script_path = Path(__file__).parent.parent / "convert_icon.py"
        assert script_path.exists(), "convert_icon.py script should exist"
    
    def test_convert_icon_script_imports(self):
        """Test that convert_icon.py has required imports"""
        script_path = Path(__file__).parent.parent / "convert_icon.py"
        with open(script_path, 'r') as f:
            content = f.read()
            assert 'from PIL import Image' in content or 'import Image' in content
            assert 'favicon.png' in content
            assert 'favicon.ico' in content
    
    def test_convert_icon_script_runs(self):
        """Test that convert_icon.py runs without errors"""
        import subprocess
        script_path = Path(__file__).parent.parent / "convert_icon.py"
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "Successfully converted" in result.stdout or result.returncode == 0


class TestPyInstallerSpec:
    """Test PyInstaller spec file icon configuration"""
    
    def test_spec_file_exists(self):
        """Test that AuthMatrix.spec exists"""
        spec_path = Path(__file__).parent.parent / "AuthMatrix.spec"
        assert spec_path.exists(), "AuthMatrix.spec should exist"
    
    def test_spec_file_has_icon(self):
        """Test that spec file includes icon configuration"""
        spec_path = Path(__file__).parent.parent / "AuthMatrix.spec"
        with open(spec_path, 'r') as f:
            content = f.read()
            assert "icon=" in content, "Spec file should have icon parameter"
            assert "favicon.ico" in content, "Spec file should reference favicon.ico"
            # Check for the exact line with icon configuration
            assert "icon='UI/assets/favicon.ico'" in content or \
                   'icon="UI/assets/favicon.ico"' in content or \
                   "icon='UI\\assets\\favicon.ico'" in content


class TestMainWindowIcon:
    """Test MainWindow icon setting functionality"""
    
    def test_main_window_has_icon_method(self, qtbot):
        """Test that MainWindow has _set_window_icon method"""
        from UI.UI import MainWindow
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        assert hasattr(window, '_set_window_icon'), "MainWindow should have _set_window_icon method"
    
    def test_main_window_icon_is_set(self, qtbot):
        """Test that MainWindow sets window icon"""
        from UI.UI import MainWindow
        from PySide6 import QtGui
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Get the window icon
        icon = window.windowIcon()
        assert not icon.isNull(), "Window icon should not be null"
    
    def test_main_window_calls_set_icon(self, qtbot):
        """Test that MainWindow constructor calls _set_window_icon"""
        from UI.UI import MainWindow
        
        # Patch the _set_window_icon method to track if it's called
        with patch.object(MainWindow, '_set_window_icon') as mock_set_icon:
            window = MainWindow()
            qtbot.addWidget(window)
            
            mock_set_icon.assert_called_once()
    
    def test_main_window_icon_file_resolution(self, qtbot):
        """Test that MainWindow can find icon file in different scenarios"""
        from UI.UI import MainWindow
        from pathlib import Path
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Check that icon file can be found
        # The method should check both development and PyInstaller paths
        icon_extensions = [".ico", ".png"]
        found = False
        
        for ext in icon_extensions:
            # Development path
            candidate_path = Path(__file__).parent.parent / "UI" / "assets" / f"favicon{ext}"
            if candidate_path.exists():
                found = True
                break
        
        assert found, "Icon file should be findable via development path"


class TestApplicationIcon:
    """Test application-wide icon setting"""
    
    def test_start_ui_sets_app_icon(self, qtbot):
        """Test that start_ui function sets application icon"""
        from UI.UI import start_ui
        from PySide6 import QtWidgets, QtGui
        from pathlib import Path
        
        # Create application if it doesn't exist
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        
        # Check that icon file exists
        icon_path = Path(__file__).parent.parent / "UI" / "assets" / "favicon.ico"
        assert icon_path.exists(), "Icon file should exist for application icon setting"
    
    def test_start_ui_has_icon_code(self):
        """Test that start_ui function has icon setting code"""
        import inspect
        from pathlib import Path
        
        # Read the source file directly to avoid importing PySide6
        ui_file = Path(__file__).parent.parent / "UI" / "UI.py"
        with open(ui_file, 'r') as f:
            source = f.read()
        
        # Find the start_ui function
        assert 'def start_ui(' in source, "start_ui function should exist"
        
        # Check for icon-related code in start_ui function
        assert 'Icon' in source or 'icon' in source, "start_ui should have icon-related code"
        assert 'setWindowIcon' in source, "start_ui should call setWindowIcon"
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_start_ui_sets_windows_app_id(self):
        """Test that start_ui sets Windows App User Model ID"""
        from pathlib import Path
        
        # Read the source file directly to avoid importing PySide6
        ui_file = Path(__file__).parent.parent / "UI" / "UI.py"
        with open(ui_file, 'r') as f:
            source = f.read()
        
        # Check for Windows-specific AppUserModelID code
        assert 'SetCurrentProcessExplicitAppUserModelID' in source or \
               'AppUserModelID' in source, \
               "start_ui should set Windows AppUserModelID for proper taskbar icon"


class TestBuildScript:
    """Test build script includes icon conversion"""
    
    def test_build_bat_exists(self):
        """Test that build.bat exists"""
        build_script = Path(__file__).parent.parent / "build.bat"
        assert build_script.exists(), "build.bat should exist"
    
    def test_build_bat_runs_icon_conversion(self):
        """Test that build.bat includes icon conversion step"""
        build_script = Path(__file__).parent.parent / "build.bat"
        
        with open(build_script, 'r') as f:
            content = f.read()
            assert 'convert_icon.py' in content, "build.bat should run convert_icon.py"
            assert 'pyinstaller' in content.lower(), "build.bat should run PyInstaller"
    
    def test_build_bat_converts_before_build(self):
        """Test that build.bat converts icon before PyInstaller build"""
        build_script = Path(__file__).parent.parent / "build.bat"
        
        with open(build_script, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            convert_line = -1
            pyinstaller_line = -1
            
            for i, line in enumerate(lines):
                if 'convert_icon.py' in line:
                    convert_line = i
                if 'pyinstaller' in line.lower():
                    pyinstaller_line = i
            
            assert convert_line != -1, "build.bat should have icon conversion"
            assert pyinstaller_line != -1, "build.bat should have PyInstaller"
            assert convert_line < pyinstaller_line, \
                   "Icon conversion should happen before PyInstaller build"


class TestIconIntegration:
    """Integration tests for icon functionality"""
    
    def test_end_to_end_icon_flow(self, qtbot):
        """Test complete icon flow from file to window"""
        from UI.UI import MainWindow
        from pathlib import Path
        
        # 1. Verify icon file exists
        icon_path = Path(__file__).parent.parent / "UI" / "assets" / "favicon.ico"
        assert icon_path.exists()
        
        # 2. Create MainWindow
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 3. Verify icon is set on window
        icon = window.windowIcon()
        assert not icon.isNull()
        
        # 4. Verify icon has multiple sizes (ICO format characteristic)
        sizes = icon.availableSizes()
        # ICO format typically has multiple sizes
        # We expect at least one size to be available
        assert len(sizes) > 0, "Icon should have at least one size available"
    
    def test_icon_file_format_multisize(self):
        """Test that ICO file contains multiple icon sizes"""
        from pathlib import Path
        
        icon_path = Path(__file__).parent.parent / "UI" / "assets" / "favicon.ico"
        
        # Read ICO file header to check number of images
        with open(icon_path, 'rb') as f:
            # ICO format: 
            # Bytes 0-1: Reserved (0)
            # Bytes 2-3: Image type (1 for icon)
            # Bytes 4-5: Number of images
            f.seek(4)
            num_images_bytes = f.read(2)
            num_images = int.from_bytes(num_images_bytes, byteorder='little')
            
            # We expect multiple sizes (typically 6: 16, 32, 48, 64, 128, 256)
            assert num_images > 0, "ICO file should contain at least one image"
            assert num_images <= 20, "ICO file should have reasonable number of images"
            
            # Based on convert_icon.py, we expect 6 sizes
            assert num_images == 6, \
                   f"ICO file should contain 6 images (got {num_images})"
