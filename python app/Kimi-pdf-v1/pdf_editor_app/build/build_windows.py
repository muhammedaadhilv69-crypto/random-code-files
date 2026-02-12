"""
Build script for Windows executable using PyInstaller
"""

import PyInstaller.__main__
import os
import sys
import shutil

# Get paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(base_dir, 'src')
assets_dir = os.path.join(base_dir, 'assets')
build_dir = os.path.join(base_dir, 'build', 'windows')
dist_dir = os.path.join(base_dir, 'dist', 'windows')

# Clean previous builds
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)
if os.path.exists(dist_dir):
    shutil.rmtree(dist_dir)

# PyInstaller arguments
args = [
    os.path.join(src_dir, 'main.py'),
    '--name=ProPDFEditor',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconfirm',
    '--enable-shared',
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
    # f'--icon={os.path.join(assets_dir, "icon.ico")}',
    
    # Version info
    '--version-file=version.txt',
]

# Run PyInstaller
print("Building Windows executable...")
PyInstaller.__main__.run(args)

print(f"Build complete! Executable located at: {dist_dir}")
