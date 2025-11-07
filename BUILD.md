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
- PySide6 dependencies are properly bundled
- All hidden imports are detected
- The binary is built as a windowed application (no console)

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
