# PDF Editor Pro - Free & Open Source

A comprehensive, production-ready PDF viewer and editor with all premium features - completely free!

## Features

### 📖 **Viewing & Navigation**
- Smooth PDF viewing with zoom and rotation
- Thumbnail sidebar for quick navigation
- Keyboard shortcuts for efficient workflow
- Fit-to-window and custom zoom levels
- Bookmarks panel for quick access

### ✏️ **Annotations**
- **Highlighting** - Mark important text
- **Text annotations** - Add notes and comments
- **Shapes** - Rectangles, circles, lines, arrows
- **Free drawing** - Sketch directly on PDFs
- **Underline & Strikethrough** - Mark text
- **Comments** - Add sticky notes
- **Customizable colors and line widths**

### ✍️ **Signatures & Stamps**
- Digital signature insertion
- Custom stamps (APPROVED, CONFIDENTIAL, DRAFT, etc.)
- Image-based signatures

### 🔒 **Security Features**
- **Encryption** - Password protect PDFs (AES-256)
- **Decryption** - Remove passwords
- **Watermarks** - Add custom text watermarks
- **Redaction** - Permanently remove sensitive content

### 📄 **Page Management**
- Add, delete, and rearrange pages
- Insert blank pages
- Rotate pages individually or all at once
- Extract pages to separate PDFs

### 🔧 **PDF Tools**
- **Merge PDFs** - Combine multiple PDFs into one
- **Split PDFs** - Separate pages or split at specific points
- **Compress** - Reduce file size significantly
- **Optimize for Web** - Linearize for fast web viewing
- **PDF/A Conversion** - Archive-ready format

### 📝 **Text & Content**
- **Extract text** - Copy text from any page
- **OCR support** - Convert scanned documents to searchable PDFs (with tesseract)
- **Add page numbers** - Automatic page numbering
- **Headers & Footers** - Custom headers and footers

### 📤 **Export Options**
- Export pages as high-quality images (PNG)
- Batch export all pages
- Extract embedded images

### 🎨 **Customization**
- Adjustable annotation colors
- Variable line widths (1-10px)
- Font sizes (8-48pt)
- Opacity controls

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install PyMuPDF Pillow
```

### Step 2: Run the Application

```bash
python pdf_editor_pro.py
```

## Building Executables

### Windows (.exe)

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller --onefile --windowed --name="PDF_Editor_Pro" --icon=icon.ico pdf_editor_pro.py
```

The executable will be in the `dist/` folder.

### Linux (AppImage)

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the binary:
```bash
pyinstaller --onefile --name="pdf-editor-pro" pdf_editor_pro.py
```

3. Create AppImage (optional, requires appimagetool):
```bash
# Create directory structure
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy binary
cp dist/pdf-editor-pro AppDir/usr/bin/

# Create .desktop file
cat > AppDir/usr/share/applications/pdf-editor-pro.desktop << EOF
[Desktop Entry]
Name=PDF Editor Pro
Exec=pdf-editor-pro
Icon=pdf-editor-pro
Type=Application
Categories=Office;
EOF

# Build AppImage
appimagetool AppDir PDF_Editor_Pro-x86_64.AppImage
```

### macOS (.app)

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the application:
```bash
pyinstaller --onefile --windowed --name="PDF Editor Pro" pdf_editor_pro.py
```

The .app bundle will be in the `dist/` folder.

## Usage Guide

### Opening PDFs
- **File → Open PDF** or **Ctrl+O**
- Drag and drop (if implemented)

### Navigation
- **Arrow keys** - Previous/Next page
- **Home/End** - First/Last page
- Click thumbnails for quick navigation
- Type page number and press Enter

### Adding Annotations

1. **Highlight Text:**
   - Click "Highlight" in toolbar or menu
   - Click and drag over text

2. **Add Text:**
   - Click "Text" button
   - Click where you want to add text
   - Type your text

3. **Draw Shapes:**
   - Select shape tool (Rectangle, Circle, Line, Arrow)
   - Click and drag to create shape

4. **Free Drawing:**
   - Select "Free Draw" mode
   - Click and drag to draw

5. **Add Signature:**
   - Click "Sign" button
   - Select signature image
   - Click where to place it

### Saving Work
- **Ctrl+S** - Save changes
- **Ctrl+Shift+S** - Save as new file
- All annotations are embedded in the PDF

### Merging PDFs
1. **File → Merge PDFs**
2. Select multiple PDFs in order
3. Choose output location
4. Click OK

### Splitting PDFs
1. **File → Split PDF**
2. Choose split method:
   - Each page separately
   - Split at specific page
3. Select output directory

### Encrypting PDFs
1. **Security → Encrypt PDF**
2. Enter user password (for opening)
3. Enter owner password (for permissions)
4. Choose output location

### Compressing PDFs
1. **Tools → Compress PDF**
2. Choose output location
3. View compression statistics

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open PDF | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Zoom In | Ctrl++ |
| Zoom Out | Ctrl+- |
| Fit to Window | Ctrl+0 |
| Next Page | Right Arrow |
| Previous Page | Left Arrow |
| First Page | Home |
| Last Page | End |

## Feature Comparison with Adobe Acrobat

| Feature | PDF Editor Pro | Adobe Acrobat Pro |
|---------|---------------|-------------------|
| View PDFs | ✅ Free | ✅ |
| Annotations | ✅ Free | ✅ $239.88/year |
| Digital Signatures | ✅ Free | ✅ $239.88/year |
| Merge/Split PDFs | ✅ Free | ✅ $239.88/year |
| Encrypt PDFs | ✅ Free | ✅ $239.88/year |
| Compress PDFs | ✅ Free | ✅ $239.88/year |
| Add Watermarks | ✅ Free | ✅ $239.88/year |
| Extract Text | ✅ Free | ✅ $239.88/year |
| Export to Images | ✅ Free | ✅ $239.88/year |
| OCR (with tesseract) | ✅ Free | ✅ $239.88/year |
| Redaction | ✅ Free | ✅ $239.88/year |
| Page Numbers | ✅ Free | ✅ $239.88/year |
| **Cost** | **FREE** | **$239.88/year** |

## Troubleshooting

### "ModuleNotFoundError: No module named 'fitz'"
```bash
pip install PyMuPDF
```

### "ModuleNotFoundError: No module named 'PIL'"
```bash
pip install Pillow
```

### Application won't start
- Ensure Python 3.8+ is installed
- Check all dependencies are installed
- Try running with `python3 pdf_editor_pro.py`

### PDF won't open
- Verify the file is a valid PDF
- Check if the PDF is encrypted (try decrypt option)
- Ensure you have read permissions

### Annotations not saving
- Click "Save" or press Ctrl+S
- For encrypted PDFs, you may need owner password
- Check file write permissions

## Advanced Features

### Custom Stamps
Edit the `add_stamp()` function to add your own stamp text or images.

### OCR Integration
Install tesseract for OCR functionality:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Then install Python wrapper
pip install pytesseract
```

### Batch Processing
Create scripts using the core functionality for batch operations on multiple PDFs.

## Dependencies

- **PyMuPDF (fitz)** - PDF manipulation and rendering
- **Pillow (PIL)** - Image processing
- **tkinter** - GUI framework (included with Python)

## Performance Tips

1. **Large PDFs**: Use thumbnail view for navigation
2. **Many annotations**: Save periodically to prevent data loss
3. **High-resolution exports**: May take time for large documents
4. **Compression**: Can significantly reduce file size (50-80% typical)

## Contributing

This is an open-source project. Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Fork and customize

## License

Free for personal and commercial use.

## Credits

Built with:
- Python 3
- PyMuPDF (MuPDF library)
- Tkinter
- Pillow

## Support

For issues or questions:
- Check the troubleshooting section
- Review PyMuPDF documentation: https://pymupdf.readthedocs.io/
- Python documentation: https://docs.python.org/3/

## Version History

### v1.0 (Current)
- Initial release
- Full PDF viewing and editing
- All annotation types
- Security features
- Merge/split functionality
- Export capabilities
- Compression and optimization

---

**Enjoy free PDF editing without subscription fees or limitations!** 🎉
