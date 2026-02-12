# PDF Editor Pro - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies (1 minute)

```bash
pip install PyMuPDF Pillow
```

### 2. Run the Application (10 seconds)

```bash
python pdf_editor_pro.py
```

### 3. Open a PDF (10 seconds)

- Press **Ctrl+O**
- Select your PDF file

## Essential Features in 60 Seconds

### View & Navigate (10 sec)
- **Arrow keys** to move between pages
- **Ctrl+0** to fit page to window
- **Ctrl++** / **Ctrl+-** to zoom

### Highlight Important Text (15 sec)
1. Click **"Highlight"** in toolbar
2. Drag over text to highlight
3. Press **Ctrl+S** to save

### Add a Comment (15 sec)
1. Click **"Text"** in toolbar  
2. Click where you want to add text
3. Type your comment
4. Click OK
5. Press **Ctrl+S** to save

### Sign the Document (20 sec)
1. Click **"Sign"** button
2. Select your signature image
3. Click where to place it
4. Press **Ctrl+S** to save

## Common Tasks

### Merge Two PDFs
1. **File → Merge PDFs**
2. Select files in order
3. Choose output location
4. Done!

### Password Protect a PDF
1. **Security → Encrypt PDF**
2. Enter passwords
3. Save encrypted file

### Compress Large PDF
1. **Tools → Compress PDF**
2. Choose output location
3. See size reduction stats

### Extract All Pages as Images
1. **File → Export to Images**
2. Select output folder
3. All pages saved as PNG files

## Keyboard Shortcuts Cheat Sheet

| Action | Shortcut |
|--------|----------|
| Open | Ctrl+O |
| Save | Ctrl+S |
| Next Page | → |
| Previous Page | ← |
| Zoom In | Ctrl++ |
| Zoom Out | Ctrl+- |
| Fit Window | Ctrl+0 |

## Building an Executable

### Windows
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="PDF_Editor_Pro" pdf_editor_pro.py
```
Executable: `dist/PDF_Editor_Pro.exe`

### Linux
```bash
pip install pyinstaller
pyinstaller --onefile --name="pdf-editor-pro" pdf_editor_pro.py
```
Executable: `dist/pdf-editor-pro`

### macOS
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="PDF Editor Pro" pdf_editor_pro.py
```
App: `dist/PDF Editor Pro.app`

## Need Help?

- **Full documentation**: See `README.md`
- **Detailed guide**: See `USER_GUIDE.md`
- **Troubleshooting**: Check README troubleshooting section

## Feature Comparison

**PDF Editor Pro vs Adobe Acrobat Pro:**

| Feature | PDF Editor Pro | Adobe Acrobat Pro |
|---------|----------------|-------------------|
| Price | **FREE** | **$239.88/year** |
| View PDFs | ✅ | ✅ |
| Annotations | ✅ | ✅ |
| Signatures | ✅ | ✅ |
| Merge/Split | ✅ | ✅ |
| Encryption | ✅ | ✅ |
| Compression | ✅ | ✅ |
| Watermarks | ✅ | ✅ |
| OCR | ✅ (with tesseract) | ✅ |

**You get all premium features for FREE!**

---

**Ready to edit PDFs like a pro? Run the app and start editing!** 🚀
