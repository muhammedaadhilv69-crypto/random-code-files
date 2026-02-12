#!/usr/bin/env python3
"""
PDF Editor Pro - Dependency Checker
This script verifies all dependencies are properly installed
"""

import sys
import importlib.util

def check_module(module_name, package_name=None):
    """Check if a module is installed"""
    if package_name is None:
        package_name = module_name
    
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return False, f"❌ {package_name} is NOT installed"
    else:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            return True, f"✅ {package_name} is installed (version: {version})"
        except:
            return True, f"✅ {package_name} is installed"

def main():
    print("=" * 60)
    print("PDF Editor Pro - Dependency Checker")
    print("=" * 60)
    print()
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("⚠️  WARNING: Python 3.8+ is recommended")
    else:
        print("✅ Python version OK")
    
    print()
    print("Checking dependencies...")
    print("-" * 60)
    
    # Required modules
    dependencies = [
        ('tkinter', 'tkinter (built-in)'),
        ('fitz', 'PyMuPDF'),
        ('PIL', 'Pillow'),
    ]
    
    all_ok = True
    missing = []
    
    for module, package in dependencies:
        ok, message = check_module(module, package)
        print(message)
        if not ok:
            all_ok = False
            missing.append(package)
    
    print("-" * 60)
    print()
    
    if all_ok:
        print("✅ All dependencies are installed!")
        print()
        print("You can now run the application:")
        print("  python pdf_editor_pro.py")
    else:
        print("❌ Some dependencies are missing!")
        print()
        print("To install missing dependencies, run:")
        if missing:
            for pkg in missing:
                if pkg == 'tkinter (built-in)':
                    print("  # tkinter should come with Python")
                    print("  # On Ubuntu/Debian: sudo apt-get install python3-tk")
                    print("  # On macOS: should be included with Python")
                    print("  # On Windows: should be included with Python")
                elif pkg == 'PyMuPDF':
                    print("  pip install pymupdf")
                elif pkg == 'Pillow':
                    print("  pip install pillow")
        print()
        print("Or install all at once:")
        print("  pip install -r requirements.txt")
    
    print()
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
