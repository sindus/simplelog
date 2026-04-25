# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for SimpleLog.
  Linux : produces dist/simplelog/ (directory) + wrapped into AppImage / .deb
  macOS : produces dist/SimpleLog.app  (bundle)  + wrapped into .dmg
"""
import sys

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=[
        "boto3",
        "botocore",
        "botocore.handlers",
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtSvg",
        "PyQt6.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "test"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="simplelog",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no terminal window; stdin pipe still works
    disable_windowed_traceback=False,
    argv_emulation=False,   # set True only if needed on macOS CLI
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="simplelog",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="SimpleLog.app",
        icon=None,
        bundle_identifier="com.sindus.simplelog",
        info_plist={
            "CFBundleName": "SimpleLog",
            "CFBundleDisplayName": "SimpleLog",
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleVersion": "1.0.0",
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,
            "LSMinimumSystemVersion": "12.0",
        },
    )
