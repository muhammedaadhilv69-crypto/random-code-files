@echo off
REM PDF Editor Pro - Windows Build Script

echo =========================================
echo PDF Editor Pro - Windows Build Script
echo =========================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

echo Building Windows executable...
echo =============================
echo.

REM Build executable
pyinstaller --onefile ^
            --windowed ^
            --name="PDF_Editor_Pro" ^
            --add-data="README.md;." ^
            pdf_editor_pro.py

echo.
echo =========================================
echo Build complete!
echo =========================================
echo.
echo Your executable is at: dist\PDF_Editor_Pro.exe
echo.
echo To run:
echo   dist\PDF_Editor_Pro.exe
echo.
echo You can also create a shortcut to this file.
echo.

pause
