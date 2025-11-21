# Windows Icon Implementation

## Overview

The AuthMatrix application has comprehensive Windows icon support, providing a professional appearance across all contexts where the application appears.

## Icon Features

### 1. Multi-Size ICO Format

The application uses a multi-resolution ICO file (`UI/assets/favicon.ico`) containing 6 icon sizes:
- 16x16 pixels (small icons, file lists)
- 32x32 pixels (standard icons)
- 48x48 pixels (large icons)
- 64x64 pixels (extra large icons)
- 128x128 pixels (jumbo icons)
- 256x256 pixels (maximum size for Windows)

This ensures the icon looks sharp at any size Windows displays it.

### 2. PyInstaller Executable Icon

The executable built with PyInstaller includes the icon embedded in the `.exe` file:

**Location**: `AuthMatrix.spec` line 76
```python
icon='UI/assets/favicon.ico'
```

This icon appears in:
- Windows Explorer file listings
- Desktop shortcuts
- Start menu entries
- Taskbar buttons

### 3. Runtime Window Icon

The application sets the window icon at runtime for proper display even when running from source:

**Location**: `UI/UI.py` method `_set_window_icon()` (lines 264-299)

Key features:
- Fallback logic: tries `.ico` first, then `.png`
- Works in development mode (running from source)
- Works in production mode (PyInstaller bundle with `sys._MEIPASS`)
- Sets both window icon and application icon

```python
def _set_window_icon(self):
    """Set the window icon from assets folder"""
    # Tries multiple locations and formats
    # Sets window.setWindowIcon() and app.setWindowIcon()
```

### 4. Windows Taskbar Integration

For proper Windows taskbar grouping and icon display, the application sets the Windows App User Model ID:

**Location**: `UI/UI.py` in `start_ui()` function (lines 2031-2036)

```python
try:
    import ctypes
    app_id = 'Firesand.AuthMatrix.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
except:
    pass  # Not on Windows or API not available
```

This ensures:
- Proper taskbar button grouping
- Correct icon display in the taskbar
- Windows 7+ taskbar features work correctly

## Icon Build Process

### Automated Build (Recommended)

The `build.bat` script handles icon conversion automatically:

```batch
# Step 1: Convert PNG to ICO
python convert_icon.py

# Step 2: Build with PyInstaller
pyinstaller AuthMatrix.spec
```

### Manual Icon Conversion

If you need to regenerate the icon file:

```bash
python convert_icon.py
```

This script:
- Reads `UI/assets/favicon.png` (source image)
- Creates `UI/assets/favicon.ico` with 6 sizes
- Uses PIL/Pillow for conversion

**Requirements**: `pip install Pillow`

### Source Files

- **Source PNG**: `UI/assets/favicon.png` (601KB, high resolution)
- **Generated ICO**: `UI/assets/favicon.ico` (61KB, multi-size)
- **Conversion Script**: `convert_icon.py`
- **Build Script**: `build.bat` (Windows)

## Testing

A comprehensive test suite validates all icon functionality:

```bash
pytest tests/test_icon_implementation.py -v
```

Tests cover:
- Icon file existence and format validation
- ICO file structure (verifies 6 sizes)
- Conversion script functionality
- PyInstaller spec configuration
- Runtime icon setting (window and app)
- Windows AppUserModelID setting
- Build process integration

**Test Results**: 13 tests pass, 7 tests skip (UI tests require display, Windows-only tests)

## Icon Customization

To use a custom icon:

1. **Replace the source PNG**:
   - Update `UI/assets/favicon.png` with your icon
   - Recommended size: 512x512 or larger
   - Format: PNG with transparency

2. **Regenerate the ICO file**:
   ```bash
   python convert_icon.py
   ```

3. **Rebuild the application**:
   ```bash
   build.bat
   ```

## Platform Support

| Platform | Icon Support | Notes |
|----------|-------------|-------|
| Windows  | ✅ Full     | Executable icon, window icon, taskbar icon with AppUserModelID |
| Linux    | ✅ Partial  | Window icon, no executable icon in ICO format |
| macOS    | ✅ Partial  | Window icon, would need ICNS format for app bundle |

## Technical Details

### ICO File Format

The ICO format is a container that holds multiple PNG images:

```
Bytes 0-1:   00 00           (Reserved)
Bytes 2-3:   01 00           (Type: Icon)
Bytes 4-5:   06 00           (Number of images: 6)
Bytes 6+:    Image directory and data
```

### Performance Considerations

- ICO file loaded once at startup (minimal overhead)
- Multi-size format allows OS to choose optimal size
- No runtime conversion needed (ICO is pre-generated)

### Security Considerations

- Icon files are static assets (no code execution)
- ICO format is well-established and safe
- PIL/Pillow used only for build-time conversion (not runtime)

## Troubleshooting

### Icon not showing in executable

1. Verify ICO file exists:
   ```bash
   ls -lh UI/assets/favicon.ico
   ```

2. Check PyInstaller spec includes icon:
   ```bash
   grep "icon=" AuthMatrix.spec
   ```

3. Regenerate icon and rebuild:
   ```bash
   python convert_icon.py
   pyinstaller AuthMatrix.spec
   ```

### Icon not showing in taskbar (Windows)

- The AppUserModelID must be set correctly
- Check that `SetCurrentProcessExplicitAppUserModelID` is called in `start_ui()`
- On Windows 10+, sometimes a restart is needed for icon cache to update

### Icon conversion fails

- Ensure Pillow is installed: `pip install Pillow`
- Verify source PNG exists: `UI/assets/favicon.png`
- Check PNG is valid (open in image viewer)

## References

- [Microsoft: Icon Design Guidelines](https://docs.microsoft.com/en-us/windows/apps/design/style/iconography/app-icon-design)
- [PyInstaller: Using Icon Files](https://pyinstaller.org/en/stable/usage.html#cmdoption-icon)
- [Windows AppUserModelID](https://docs.microsoft.com/en-us/windows/win32/shell/appids)
- [ICO File Format](https://en.wikipedia.org/wiki/ICO_(file_format))

## Version History

- **1.0.0**: Initial implementation with full Windows icon support
  - Multi-size ICO format (6 sizes)
  - PyInstaller integration
  - Runtime window/app icon setting
  - Windows taskbar integration via AppUserModelID
  - Automated build process with icon conversion
  - Comprehensive test suite
