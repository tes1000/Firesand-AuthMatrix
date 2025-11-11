@echo off
echo ============================================
echo Building AuthMatrix Executable
echo ============================================
echo.

echo Step 1: Converting favicon.png to favicon.ico...
python convert_icon.py
if errorlevel 1 (
    echo ERROR: Failed to convert icon
    pause
    exit /b 1
)
echo Icon conversion completed successfully
echo.

echo Step 2: Building executable with PyInstaller...
pyinstaller AuthMatrix.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)
echo.

echo ============================================
echo Build completed successfully!
echo Executable location: dist\AuthMatrix.exe
echo ============================================
pause
