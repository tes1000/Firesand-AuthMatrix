# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Firesand_Auth_Matrix.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('UI', 'UI'),  # Include the entire UI package
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
