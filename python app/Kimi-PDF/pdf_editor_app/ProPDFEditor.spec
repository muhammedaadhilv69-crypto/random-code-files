# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Get the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, 'src')

a = Analysis(
    [os.path.join(src_dir, 'main.py')],
    pathex=[src_dir, base_dir],
    binaries=[],
    datas=[
        (src_dir, 'src'),
    ],
    hiddenimports=[
        'fitz',
        'pikepdf',
        'cryptography',
        'PIL',
        'PIL._imagingtk',
        'PIL._tkinter_finder',
        'pytesseract',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'docx',
        'openpyxl',
        'python-dateutil',
        'qrcode',
        'OpenSSL',
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
    name='ProPDFEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',  # Uncomment when icon is available
)

# macOS app bundle
app = BUNDLE(
    exe,
    name='ProPDFEditor.app',
    icon=None,
    bundle_identifier='com.propdf.editor',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True',
    },
)
