"""
Build script for Linux AppImage using PyInstaller
"""

import PyInstaller.__main__
import os
import sys
import shutil
import subprocess

# Get paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(base_dir, 'src')
assets_dir = os.path.join(base_dir, 'assets')
build_dir = os.path.join(base_dir, 'build', 'linux')
dist_dir = os.path.join(base_dir, 'dist', 'linux')

# Clean previous builds
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)
if os.path.exists(dist_dir):
    shutil.rmtree(dist_dir)

os.makedirs(dist_dir, exist_ok=True)

# PyInstaller arguments
args = [
    os.path.join(src_dir, 'main.py'),
    '--name=ProPDFEditor',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconfirm',
    f'--distpath={dist_dir}',
    f'--workpath={build_dir}',
    f'--specpath={build_dir}',
    
    # Add data files
    f'--add-data={src_dir}:src',
    
    # Hidden imports
    '--hidden-import=fitz',
    '--hidden-import=pikepdf',
    '--hidden-import=cryptography',
    '--hidden-import=PIL',
    '--hidden-import=pytesseract',
    '--hidden-import=reportlab',
    '--hidden-import=docx',
    '--hidden-import=openpyxl',
    
    # Icon (if available)
    # f'--icon={os.path.join(assets_dir, "icon.png")}',
]

# Run PyInstaller
print("Building Linux executable...")
PyInstaller.__main__.run(args)

# Create desktop entry
desktop_entry = f"""[Desktop Entry]
Name=ProPDF Editor
Comment=Professional PDF Viewer and Editor
Exec=ProPDFEditor
Icon=propdf-editor
Type=Application
Categories=Office;Viewer;
MimeType=application/pdf;
"""

with open(os.path.join(dist_dir, 'ProPDFEditor.desktop'), 'w') as f:
    f.write(desktop_entry)

# Create AppRun script for AppImage
apprun = f"""#!/bin/bash
HERE="$(dirname "$(readlink -f "${{0}}")")"
export PATH="${{HERE}}:${{PATH}}"
export LD_LIBRARY_PATH="${{HERE}}:${{LD_LIBRARY_PATH}}"
exec "${{HERE}}/ProPDFEditor" "$@"
"""

with open(os.path.join(dist_dir, 'AppRun'), 'w') as f:
    f.write(apprun)

os.chmod(os.path.join(dist_dir, 'AppRun'), 0o755)
os.chmod(os.path.join(dist_dir, 'ProPDFEditor'), 0o755)

print(f"Build complete! Executable located at: {dist_dir}")
print("\nTo create an AppImage:")
print("1. Download appimagetool from https://github.com/AppImage/AppImageKit/releases")
print("2. Run: ./appimagetool-x86_64.AppImage dist/linux/")
