#!/usr/bin/env python3
"""
Main build script for ProPDF Editor
"""

import argparse
import os
import sys
import subprocess
import shutil

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    req_file = os.path.join(base_dir, 'requirements.txt')
    
    if os.path.exists(req_file):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
    
    # Install PyInstaller if not present
    try:
        import PyInstaller
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

def build_windows():
    """Build Windows executable."""
    print("Building for Windows...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    build_script = os.path.join(base_dir, 'build', 'build_windows.py')
    
    if os.path.exists(build_script):
        subprocess.check_call([sys.executable, build_script])
    else:
        print(f"Build script not found: {build_script}")

def build_linux():
    """Build Linux executable."""
    print("Building for Linux...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    build_script = os.path.join(base_dir, 'build', 'build_linux.py')
    
    if os.path.exists(build_script):
        subprocess.check_call([sys.executable, build_script])
    else:
        print(f"Build script not found: {build_script}")

def build_macos():
    """Build macOS app bundle."""
    print("Building for macOS...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    dist_dir = os.path.join(base_dir, 'dist', 'macos')
    build_dir = os.path.join(base_dir, 'build', 'macos')
    
    # Clean previous builds
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir, exist_ok=True)
    
    # PyInstaller arguments for macOS
    args = [
        os.path.join(src_dir, 'main.py'),
        '--name=ProPDFEditor',
        '--windowed',
        '--clean',
        '--noconfirm',
        f'--distpath={dist_dir}',
        f'--workpath={build_dir}',
        f'--specpath={build_dir}',
        
        # macOS specific
        '--osx-bundle-identifier=com.propdf.editor',
        
        # Add data files
        f'--add-data={src_dir}:src',
        
        # Hidden imports
        '--hidden-import=fitz',
        '--hidden-import=pikepdf',
        '--hidden-import=cryptography',
        '--hidden-import=PIL',
        '--hidden-import=pytesseract',
        '--hidden-import=reportlab',
    ]
    
    import PyInstaller.__main__
    PyInstaller.__main__.run(args)
    
    print(f"Build complete! App bundle located at: {dist_dir}")

def run_app():
    """Run the application directly."""
    print("Running ProPDF Editor...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, 'src', 'main.py')
    
    if os.path.exists(main_script):
        subprocess.check_call([sys.executable, main_script])
    else:
        print(f"Main script not found: {main_script}")

def main():
    parser = argparse.ArgumentParser(description='Build script for ProPDF Editor')
    parser.add_argument('command', choices=['install', 'windows', 'linux', 'macos', 'all', 'run'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'install':
        install_dependencies()
    elif args.command == 'windows':
        install_dependencies()
        build_windows()
    elif args.command == 'linux':
        install_dependencies()
        build_linux()
    elif args.command == 'macos':
        install_dependencies()
        build_macos()
    elif args.command == 'all':
        install_dependencies()
        build_windows()
        build_linux()
        build_macos()
    elif args.command == 'run':
        run_app()

if __name__ == '__main__':
    main()
