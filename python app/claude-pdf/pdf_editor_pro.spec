# -*- mode: python ; coding: utf-8 -*-
# PDF Editor Pro - PyInstaller Spec File
# Use this for advanced build customization
#
# Usage: pyinstaller pdf_editor_pro.spec

block_cipher = None

a = Analysis(
    ['pdf_editor_pro.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('USER_GUIDE.md', '.'),
        ('QUICKSTART.md', '.'),
    ],
    hiddenimports=[],
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
    name='PDF_Editor_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True to see debug output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Uncomment and add your icon file
)

# For macOS app bundle
# app = BUNDLE(
#     exe,
#     name='PDF Editor Pro.app',
#     icon='icon.icns',
#     bundle_identifier='com.pdfeditorpro.app',
#     info_plist={
#         'NSHighResolutionCapable': 'True',
#     },
# )
