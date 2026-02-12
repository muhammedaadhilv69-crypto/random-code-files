#!/bin/bash

# PDF Editor Pro - Build Script
# This script builds executables for different platforms

echo "========================================="
echo "PDF Editor Pro - Build Script"
echo "========================================="
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Detect OS
OS=$(uname -s)

echo "Detected OS: $OS"
echo ""

# Build based on OS
if [[ "$OS" == "Linux" ]]; then
    echo "Building for Linux..."
    echo "========================"
    
    # Build executable
    pyinstaller --onefile \
                --name="pdf-editor-pro" \
                --add-data="README.md:." \
                pdf_editor_pro.py
    
    echo ""
    echo "✓ Linux binary created: dist/pdf-editor-pro"
    echo ""
    
    # Ask if user wants to create AppImage
    read -p "Do you want to create an AppImage? (requires appimagetool) [y/N]: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v appimagetool &> /dev/null; then
            echo "Creating AppImage..."
            
            # Create directory structure
            mkdir -p AppDir/usr/bin
            mkdir -p AppDir/usr/share/applications
            mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
            
            # Copy binary
            cp dist/pdf-editor-pro AppDir/usr/bin/
            
            # Create .desktop file
            cat > AppDir/usr/share/applications/pdf-editor-pro.desktop << 'EOF'
[Desktop Entry]
Name=PDF Editor Pro
Exec=pdf-editor-pro
Icon=pdf-editor-pro
Type=Application
Categories=Office;Viewer;
Comment=Free PDF Editor with Premium Features
EOF
            
            # Create AppRun
            cat > AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
exec "${HERE}/usr/bin/pdf-editor-pro" "$@"
EOF
            chmod +x AppDir/AppRun
            
            # Build AppImage
            appimagetool AppDir PDF_Editor_Pro-x86_64.AppImage
            
            echo ""
            echo "✓ AppImage created: PDF_Editor_Pro-x86_64.AppImage"
        else
            echo "appimagetool not found. Skipping AppImage creation."
            echo "Install from: https://github.com/AppImage/AppImageKit/releases"
        fi
    fi

elif [[ "$OS" == "Darwin" ]]; then
    echo "Building for macOS..."
    echo "====================="
    
    pyinstaller --onefile \
                --windowed \
                --name="PDF Editor Pro" \
                --add-data="README.md:." \
                pdf_editor_pro.py
    
    echo ""
    echo "✓ macOS app created: dist/PDF Editor Pro.app"

elif [[ "$OS" == MINGW* ]] || [[ "$OS" == CYGWIN* ]] || [[ "$OS" == MSYS* ]]; then
    echo "Building for Windows..."
    echo "======================="
    
    pyinstaller --onefile \
                --windowed \
                --name="PDF_Editor_Pro" \
                --add-data="README.md;." \
                pdf_editor_pro.py
    
    echo ""
    echo "✓ Windows executable created: dist/PDF_Editor_Pro.exe"

else
    echo "Unknown operating system. Building generic executable..."
    
    pyinstaller --onefile \
                --name="pdf-editor-pro" \
                pdf_editor_pro.py
    
    echo ""
    echo "✓ Executable created: dist/pdf-editor-pro"
fi

echo ""
echo "========================================="
echo "Build complete!"
echo "========================================="
echo ""
echo "Your executable is in the 'dist' folder."
echo ""
echo "To run:"
if [[ "$OS" == "Linux" ]]; then
    echo "  ./dist/pdf-editor-pro"
elif [[ "$OS" == "Darwin" ]]; then
    echo "  open dist/PDF\\ Editor\\ Pro.app"
elif [[ "$OS" == MINGW* ]] || [[ "$OS" == CYGWIN* ]] || [[ "$OS" == MSYS* ]]; then
    echo "  dist\\PDF_Editor_Pro.exe"
fi
echo ""
