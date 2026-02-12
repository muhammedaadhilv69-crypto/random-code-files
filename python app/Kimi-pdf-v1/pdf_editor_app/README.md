# ProPDF Editor - Professional PDF Viewer and Editor

A production-ready, feature-rich PDF viewer and editor built with Python and PyQt6. ProPDF Editor provides all the essential features of commercial PDF editors like Adobe Acrobat, completely free and open-source.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## Features

### Core PDF Operations
- **View PDFs** - Fast, high-quality rendering with zoom, pan, and rotation
- **Create PDFs** - Create new blank PDF documents
- **Edit PDFs** - Modify existing PDF content
- **Save & Export** - Save in various formats and compression levels

### Annotation Tools
- **Highlight** - Mark important text with customizable colors
- **Underline** - Underline text with different colors
- **Strikethrough** - Cross out text
- **Text Notes** - Add sticky notes and comments
- **Freehand Drawing** - Draw freehand annotations
- **Shapes** - Add rectangles, circles, lines, and arrows
- **Stamps** - Apply pre-defined or custom stamps (APPROVED, CONFIDENTIAL, etc.)

### Digital Signatures
- **Digital Signatures** - Create and apply certificate-based digital signatures
- **Handwritten Signatures** - Draw or import handwritten signatures
- **Certificate Management** - Create, import, and manage digital certificates
- **Signature Verification** - Verify signature authenticity

### Form Handling
- **Form Field Creation** - Create text fields, checkboxes, radio buttons, dropdowns
- **Form Filling** - Fill out existing PDF forms
- **Form Export** - Export form data
- **JavaScript Support** - Form calculations and validations

### Page Management
- **Merge PDFs** - Combine multiple PDFs into one
- **Split PDFs** - Extract pages or split by ranges
- **Reorder Pages** - Drag and drop to reorder pages
- **Rotate Pages** - Rotate individual or all pages
- **Delete Pages** - Remove unwanted pages
- **Insert Pages** - Add blank pages or from other PDFs

### OCR (Optical Character Recognition)
- **Text Extraction** - Extract text from scanned documents
- **Searchable PDFs** - Convert scanned PDFs to searchable documents
- **Multi-language Support** - OCR in multiple languages

### Export & Conversion
- **Export to Word** (.docx)
- **Export to Excel** (.xlsx)
- **Export to Images** (PNG, JPEG)
- **Export to Text** (.txt)
- **Export to HTML** (.html)
- **PDF/A** - Create archival-quality PDFs

### Security Features
- **Password Protection** - Encrypt PDFs with passwords
- **Permissions** - Control printing, copying, and editing
- **Redaction** - Permanently remove sensitive content

### Advanced Features
- **Find & Replace** - Search and replace text across pages
- **Bookmarks** - Create and manage document bookmarks
- **Links** - Add hyperlinks and internal links
- **Watermarks** - Add text or image watermarks
- **Headers & Footers** - Add page numbers and custom headers/footers
- **Compression** - Optimize PDF file size

## Screenshots

*(Screenshots will be added here)*

## Installation

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (optional, for OCR features)

### Option 1: Run from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/propdf-editor.git
cd propdf-editor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/main.py
```

### Option 2: Pre-built Binaries

Download the latest release for your platform from the [Releases](https://github.com/yourusername/propdf-editor/releases) page.

#### Windows
- Download `ProPDFEditor-Windows.exe`
- Run the executable

#### Linux
- Download `ProPDFEditor-Linux.AppImage`
- Make executable: `chmod +x ProPDFEditor-Linux.AppImage`
- Run: `./ProPDFEditor-Linux.AppImage`

#### macOS
- Download `ProPDFEditor-macOS.dmg`
- Mount the DMG and drag to Applications

## Building from Source

### Windows
```bash
python build.py windows
```

### Linux
```bash
python build.py linux
```

### macOS
```bash
python build.py macos
```

### All Platforms
```bash
python build.py all
```

## Usage

### Basic Operations

**Opening a PDF:**
- File → Open (Ctrl+O)
- Drag and drop a PDF file
- Double-click a PDF file (if set as default)

**Saving:**
- File → Save (Ctrl+S)
- File → Save As (Ctrl+Shift+S)

**Navigation:**
- Page Up/Down - Previous/Next page
- Home/End - First/Last page
- Click thumbnails in left panel

### Annotations

1. Select an annotation tool from the left toolbar or Annotate menu
2. Click and drag on the page to create the annotation
3. Customize appearance in the Properties panel

### Digital Signatures

1. Create a certificate: Sign → Manage Certificates → Create New
2. Add signature: Sign → Digital Signature
3. Click on page to place signature

### Form Filling

1. Open a PDF with form fields
2. Click on form fields to enter data
3. File → Save to preserve changes

### OCR

1. Open a scanned PDF
2. Tools → OCR - Extract Text
3. Choose output format and save

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open PDF |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save As |
| Ctrl+P | Print |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+C | Copy |
| Ctrl+V | Paste |
| Ctrl+F | Find |
| Ctrl++ | Zoom In |
| Ctrl+- | Zoom Out |
| Ctrl+0 | Reset Zoom |
| PgUp/PgDn | Previous/Next Page |
| Home/End | First/Last Page |

## Dependencies

- **PyQt6** - GUI framework
- **PyMuPDF (fitz)** - PDF rendering and manipulation
- **pikepdf** - Advanced PDF operations
- **cryptography** - Digital signatures and encryption
- **Pillow** - Image processing
- **pytesseract** - OCR functionality
- **reportlab** - PDF generation
- **python-docx** - Word export
- **openpyxl** - Excel export

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PyMuPDF team for the excellent PDF library
- PyQt6 team for the GUI framework
- All contributors and testers

## Support

For support, please open an issue on GitHub or contact us at support@propdf-editor.com

## Roadmap

- [ ] Cloud storage integration
- [ ] Collaborative editing
- [ ] Mobile app
- [ ] Plugin system
- [ ] Batch processing
- [ ] PDF comparison tool
- [ ] Advanced redaction patterns
- [ ] Voice annotations

---

**ProPDF Editor** - Professional PDF editing made free and simple.
