# Building the AuthMatrix Executable

## Quick Build (Windows)

Simply run the build script:
```cmd
build.bat
```

The executable will be created at `dist\AuthMatrix.exe`

## Manual Build

1. Install PyInstaller:
```cmd
pip install pyinstaller
```

2. Build using the spec file:
```cmd
pyinstaller AuthMatrix.spec
```

3. The executable will be in the `dist` folder

## About the Spec File

The `AuthMatrix.spec` file ensures that:
- The entire `UI` package is included (all components, views, and assets)
- PySide6 dependencies are properly bundled **as dynamic libraries** (LGPL-3.0 compliant)
- All hidden imports are detected
- The binary is built as a windowed application (no console)
- License files (`THIRD_PARTY_LICENSES.md`, `LICENSE-NOTICES.txt`) are included in distributions

### LGPL-3.0 Compliance

The build configuration ensures PySide6 is dynamically linked for commercial use compliance:
- PySide6 libraries remain as separate `.so`/`.dll` files (not embedded in executable)
- Users can replace PySide6 libraries without recompiling
- License notices are automatically included in all distributions

For detailed information, see [PYSIDE6_LGPL_COMPLIANCE.md](PYSIDE6_LGPL_COMPLIANCE.md).

## Troubleshooting

### Binary doesn't show UI
- Check that `console=False` in `AuthMatrix.spec`
- Verify all UI files are present in the `UI` folder

### Missing modules error
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check `hiddenimports` list in `AuthMatrix.spec`

### Assets not loading
- Verify `UI/assets` folder exists
- Check the `datas` section in `AuthMatrix.spec`

## CI/CD

The GitHub Actions workflows will automatically:
- Run tests on pull requests (`ci.yml`)
- Build executables for Windows, macOS, and Linux on releases (`release.yml`)

## Verifying LGPL Compliance

After building, verify that PySide6 is properly dynamically linked:

### Linux
```bash
cd dist/AuthMatrix/
ldd AuthMatrix | grep -i qt
ls -la | grep -E "libQt|libPySide"
```

### Windows
```cmd
cd dist\AuthMatrix\
dir *.dll | findstr Qt
```

### macOS
```bash
cd dist/AuthMatrix.app/Contents/MacOS/
otool -L AuthMatrix | grep Qt
```

You should see Qt and PySide6 libraries as separate files, not embedded in the executable.
