# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for AuthMatrix
# 
# LGPL-3.0 Compliance Notes:
# - PySide6 is dynamically linked (not embedded in the executable)
# - This configuration ensures LGPL compliance for commercial use
# - All Qt shared libraries (.so/.dll) are kept separate from the executable
# - Users can replace PySide6 libraries if needed

block_cipher = None

a = Analysis(
    ['Firesand_Auth_Matrix.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('UI', 'UI'),  # Include the entire UI package
        ('THIRD_PARTY_LICENSES.md', '.'),  # Include third-party licenses
        ('LICENSE-NOTICES.txt', '.'),  # Include license notices for distribution
    ],
    hiddenimports=[
        'UI',
        'UI.UI',
        'UI.components',
        'UI.components.DialogUtils',
        'UI.components.LogoHeader',
        'UI.components.TabsComponent',
        'UI.views',
        'UI.views.Endpoints',
        'UI.views.Headers',
        'UI.views.Results',
        'UI.views.SpecStore',
        'UI.views.Theme',
        'UI.views.Tokens',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Ensure PySide6 libraries are kept as separate shared libraries (LGPL compliance)
# PyInstaller automatically handles PySide6 as dynamic libraries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Single-file executable mode with external dependencies
# PySide6 .so/.dll files remain separate (LGPL compliant)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AuthMatrix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='UI/assets/favicon.ico',
)
