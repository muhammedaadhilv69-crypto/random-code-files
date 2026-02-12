# ProPDF Editor - Quick Start Guide

## Getting Started in 5 Minutes

### 1. Installation

#### Windows
```bash
# Install Python 3.8+ from python.org
# Then run:
pip install -r requirements.txt
python src/main.py
```

#### Linux (Ubuntu/Debian)
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-pyqt5 tesseract-ocr

# Install Python packages
pip3 install -r requirements.txt

# Run
python3 src/main.py
```

#### macOS
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python tesseract

# Install Python packages
pip3 install -r requirements.txt

# Run
python3 src/main.py
```

### 2. Basic Usage

#### Opening a PDF
1. Launch ProPDF Editor
2. Click **File → Open** or press **Ctrl+O**
3. Select your PDF file

#### Viewing
- **Scroll**: Mouse wheel or Page Up/Down
- **Zoom**: Ctrl++ (in), Ctrl+- (out), Ctrl+0 (reset)
- **Navigate**: Click thumbnails or use arrow keys

#### Annotating
1. Select tool from left toolbar:
   - **H** - Highlight text
   - **U** - Underline text
   - **N** - Add note
   - **S** - Sign
2. Click and drag on the page

#### Saving
- **Ctrl+S** - Save changes
- **Ctrl+Shift+S** - Save as new file

### 3. Key Features

#### Adding a Digital Signature
1. **Sign → Manage Certificates → Create New**
2. Fill in your details
3. **Sign → Digital Signature**
4. Click where you want to place it

#### Filling Forms
1. Open a PDF with form fields
2. Click on any field to enter data
3. Save with **Ctrl+S**

#### OCR (Text Extraction)
1. Open a scanned PDF
2. **Tools → OCR - Extract Text**
3. Wait for processing
4. Copy or save the extracted text

#### Merging PDFs
1. **Tools → Merge PDFs**
2. Add files using **Add PDFs** button
3. Arrange order if needed
4. Click **OK** and choose save location

#### Protecting with Password
1. **Tools → Protect PDF**
2. Enter password
3. Set permissions (print, copy, etc.)
4. Save

### 4. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open |
| Ctrl+S | Save |
| Ctrl+P | Print |
| Ctrl+Z | Undo |
| Ctrl+F | Find |
| Ctrl++ | Zoom In |
| Ctrl+- | Zoom Out |
| PgUp/PgDn | Previous/Next Page |

### 5. Tips

- **Right-click** on page for context menu
- **Drag** thumbnail to reorder pages
- **Double-click** annotation to edit
- **ESC** to cancel current operation

### 6. Troubleshooting

#### App won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### OCR not working
```bash
# Install Tesseract OCR
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
```

#### PDF won't open
- Check if file is corrupted
- Try opening with another PDF reader
- Check file permissions

### 7. Building Executable

#### Windows
```bash
python build.py windows
```
Output: `dist/windows/ProPDFEditor.exe`

#### Linux
```bash
python build.py linux
```
Output: `dist/linux/ProPDFEditor`

#### macOS
```bash
python build.py macos
```
Output: `dist/macos/ProPDFEditor.app`

### 8. Next Steps

- Read the full [README.md](README.md)
- Check [Keyboard Shortcuts](#keyboard-shortcuts)
- Explore all features in menus
- Customize settings

---

**Need Help?** Open an issue on GitHub or contact support.
