# PDF Editor Pro - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Basic Operations](#basic-operations)
4. [Annotations](#annotations)
5. [Security Features](#security-features)
6. [Advanced Features](#advanced-features)
7. [Tips & Tricks](#tips-and-tricks)

## Getting Started

### First Launch
1. Run `python pdf_editor_pro.py` or double-click the executable
2. The application window will open
3. Go to **File → Open PDF** or press **Ctrl+O**
4. Select your PDF file

### Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  Annotate  Security  Tools  Help                │ Menu Bar
├─────────────────────────────────────────────────────────────┤
│ 📂 💾 | ⬅️ [Page] ➡️ | 🔍- [100%] 🔍+ | ↶ ↷ | Tools       │ Toolbar
├──────┬──────────────────────────────────────────┬───────────┤
│Pages │                                          │Properties │
│      │                                          │           │
│ p.1  │          PDF Content Area               │ - Color   │
│ p.2  │                                          │ - Width   │
│ p.3  │                                          │ - Size    │
│      │                                          │           │
│      │                                          │Bookmarks  │
│      │                                          │ - Intro   │
└──────┴──────────────────────────────────────────┴───────────┘
│ Status: Ready                                   Page 1 of 10│
└─────────────────────────────────────────────────────────────┘
```

**Main Areas:**
- **Menu Bar**: Access all features
- **Toolbar**: Quick access to common tools
- **Thumbnail Panel** (Left): Page previews
- **Viewer** (Center): Main PDF display
- **Properties Panel** (Right): Annotation settings and bookmarks
- **Status Bar** (Bottom): Current status and page info

## Basic Operations

### Opening Files
- **Menu**: File → Open PDF
- **Shortcut**: Ctrl+O
- **Formats**: .pdf files

### Saving Files
- **Save**: Ctrl+S (overwrites current file)
- **Save As**: Ctrl+Shift+S (creates new file)
- **Auto-save**: Not enabled by default - save frequently!

### Navigation

**Mouse:**
- Click thumbnail to jump to page
- Scroll wheel to zoom (with Ctrl)
- Click and drag on scrollbars

**Keyboard:**
- **Right Arrow**: Next page
- **Left Arrow**: Previous page
- **Home**: First page
- **End**: Last page
- **Page Up/Down**: Scroll

**Page Entry:**
1. Type page number in toolbar
2. Press Enter

### Zoom Controls

**Toolbar Buttons:**
- **🔍+**: Zoom in (120% each click)
- **🔍-**: Zoom out
- **Fit**: Fit to window

**Keyboard:**
- **Ctrl++**: Zoom in
- **Ctrl+-**: Zoom out
- **Ctrl+0**: Fit to window

**Zoom Range**: 10% to 500%

### Rotation
- **↶**: Rotate left (90° counter-clockwise)
- **↷**: Rotate right (90° clockwise)
- Rotation is saved with the file

## Annotations

### Highlighting Text

1. Click **Annotate → Highlight** or toolbar button
2. Choose color (🎨 button)
3. Click and drag over text to highlight
4. Repeat for more highlights
5. Click elsewhere or ESC to exit mode

**Color Options:**
- Yellow (default)
- Green
- Blue
- Pink
- Custom (color picker)

### Adding Text

1. Click **Annotate → Add Text** or **📝 Text** button
2. Click where you want text
3. Type your text in the dialog
4. Click OK

**Text Settings:**
- Font size: 8-48pt (adjust in right panel)
- Color: Use 🎨 button
- Position: Click precise location

### Drawing Shapes

**Available Shapes:**
- Rectangle
- Circle
- Line
- Arrow

**How to Draw:**
1. Select shape from **Annotate** menu
2. Click starting point
3. Drag to end point
4. Release mouse

**Customization:**
- Line width: 1-10px (right panel slider)
- Color: 🎨 button
- Opacity: 0-100% (right panel)

### Free Drawing

1. Select **Annotate → Free Draw**
2. Click and drag to draw
3. Continue drawing as needed
4. Click elsewhere to finish

**Best for:**
- Handwritten notes
- Circling areas
- Custom marks
- Sketches

### Comments & Notes

1. Select **Annotate → Add Comment**
2. Click where to place note icon
3. Type your comment
4. Click OK

Comments appear as small icons that show text when clicked.

### Underline & Strikethrough

1. Select **Annotate → Underline** or **Strikethrough**
2. Click and drag over text
3. Line appears under/through text

### Digital Signatures

**Method 1: Image Signature**
1. Click **✍️ Sign** or **Annotate → Add Signature**
2. Select your signature image file (.png, .jpg)
3. Click where to place signature
4. Signature is embedded in PDF

**Method 2: Draw Signature**
1. Use Free Draw mode
2. Draw your signature
3. Save the file

**Tips:**
- Create transparent PNG for best results
- Resize signature image before importing
- Place signature in consistent location

### Stamps

1. Select **Annotate → Add Stamp**
2. Type stamp text or choose preset:
   - APPROVED
   - CONFIDENTIAL
   - DRAFT
   - FINAL
   - FOR REVIEW
3. Stamp appears at center (you can reposition in future versions)

**Customization:**
- Default: Red, 45° rotation, 30% opacity
- Edit `add_stamp()` function for custom stamps

## Security Features

### Encrypting PDFs (Password Protection)

1. **Security → Encrypt PDF**
2. Enter **User Password** (required to open PDF)
3. Enter **Owner Password** (required to change permissions)
4. Choose save location
5. Click Encrypt

**Security Level:** AES-256 encryption (same as Adobe Acrobat Pro)

**Permissions Included:**
- Print
- Copy text
- Add annotations

### Removing Password

1. **Security → Remove Password**
2. Enter the owner password
3. Choose save location for unprotected PDF

### Adding Watermarks

1. **Security → Add Watermark**
2. Enter watermark text (e.g., "CONFIDENTIAL")
3. Watermark added to ALL pages

**Appearance:**
- Gray color
- Large font (72pt)
- 45° diagonal rotation
- Centered on each page

**Custom Watermarks:**
Edit the `add_watermark()` function to customize:
- Color
- Font size
- Rotation angle
- Position
- Opacity

### Redacting Content

⚠️ **IMPORTANT**: Redaction permanently removes content!

1. **Security → Redact Content** or **Annotate → Redact**
2. Click and drag over content to redact
3. Content is permanently removed (not just covered)
4. Save file to apply redactions

**Use Cases:**
- Remove sensitive information
- Hide personal data
- Comply with privacy regulations

## Advanced Features

### Merging PDFs

1. **File → Merge PDFs**
2. Select 2+ PDF files (in order)
3. Choose output location
4. Click OK

**Result:** Single PDF with all pages in selected order

### Splitting PDFs

**Method 1: Each Page Separately**
1. **File → Split PDF**
2. Choose "Each page as separate PDF"
3. Select output directory
4. All pages saved as individual PDFs (page_1.pdf, page_2.pdf, etc.)

**Method 2: Split at Page**
1. **File → Split PDF**
2. Choose "Split at specific page"
3. Enter page number
4. Creates two PDFs (part_1.pdf, part_2.pdf)

### Extracting Text

1. Navigate to desired page
2. **Edit → Extract Text**
3. Text appears in new window
4. Click **Copy to Clipboard** to copy

**Uses:**
- Copy quotes
- Extract data
- Create text version
- Search content

### Exporting to Images

1. **File → Export to Images**
2. Select output directory
3. All pages saved as PNG files (page_1.png, page_2.png, etc.)

**Quality:** High resolution (2x zoom = 200 DPI equivalent)

**Uses:**
- Create thumbnails
- Insert in presentations
- Share individual pages
- Archive visual content

### Page Management

**Delete Page:**
1. Navigate to page to delete
2. **Edit → Delete Current Page**
3. Confirm deletion

**Insert Blank Page:**
1. Navigate to page
2. **Edit → Insert Blank Page**
3. Blank page inserted after current page
4. Same size as current page

### Compression

1. **Tools → Compress PDF**
2. Choose output location
3. View compression statistics

**Typical Results:**
- 50-80% size reduction
- Removes unused objects
- Optimizes images
- No quality loss for text

**When to Compress:**
- Before emailing
- For web upload
- Archive storage
- Large file sizes

### Optimization for Web

1. **Tools → Optimize for Web**
2. Choose output location

**Benefits:**
- Fast loading in browsers
- Incremental page display
- Smaller file size
- Linearized structure

### PDF/A Conversion

1. **Tools → Convert to PDF/A**
2. Choose output location

**PDF/A:** Archive format for long-term preservation
- Self-contained
- No external dependencies
- Standards-compliant

### Page Numbers

1. **Tools → Add Page Numbers**
2. Numbers added to all pages
3. Format: "Page X" at bottom center

**Customization** (edit code):
- Position
- Format (e.g., "X of Y")
- Font and size
- Color

### Headers & Footers

1. **Tools → Add Headers/Footers**
2. Enter header text (optional)
3. Enter footer text (optional)
4. Click Apply

**Position:**
- Header: Top center, 30pt from edge
- Footer: Bottom center, 30pt from edge

### Bookmarks

**View Bookmarks:**
- Check "Bookmarks" tab in right panel
- Double-click to jump to page

**Add Bookmark:**
1. Navigate to page
2. **Tools → Add Bookmarks**
3. Enter bookmark title
4. Click Add Bookmark

**Bookmark Structure:**
- Level 1: Main sections
- Nested levels: Edit code for hierarchy

## Tips & Tricks

### Productivity Tips

1. **Use Keyboard Shortcuts**
   - Much faster than clicking
   - Memorize: Ctrl+O, Ctrl+S, Arrow keys, Ctrl+0

2. **Thumbnail Navigation**
   - Click thumbnails for instant page jumps
   - Visual overview of document

3. **Fit to Window**
   - Press Ctrl+0 for optimal viewing
   - Automatically adjusts to window size

4. **Color Coding**
   - Use different colors for different purposes
   - Yellow: Important info
   - Red: Errors/issues
   - Green: Approved items
   - Blue: Notes

5. **Save Frequently**
   - Press Ctrl+S often
   - No auto-save feature yet
   - Prevent work loss

### Annotation Best Practices

1. **Keep It Clear**
   - Use appropriate colors
   - Don't over-annotate
   - Be concise

2. **Consistent Style**
   - Same line width for similar items
   - Consistent color scheme
   - Uniform font sizes

3. **Layer Annotations**
   - Text annotations on top
   - Shapes first, then text
   - Comments for detailed notes

### Performance Tips

1. **Large Files**
   - Use thumbnails for navigation
   - Compress after editing
   - Close and reopen periodically

2. **Many Annotations**
   - Save frequently
   - Consider splitting large documents
   - Group related annotations

3. **High-Resolution Export**
   - May take time for large documents
   - Close other applications
   - Export one page at a time if needed

### File Management

1. **Naming Convention**
   - Use descriptive names
   - Include version numbers
   - Add date stamps

2. **Backup Strategy**
   - Keep original files
   - Save annotated versions separately
   - Use version control

3. **Organization**
   - Folder structure
   - Tag files
   - Regular cleanup

### Troubleshooting Common Issues

**Issue: Annotations not saving**
- Solution: Press Ctrl+S after each annotation session
- Check: File permissions (can you write to folder?)

**Issue: Slow performance**
- Solution: Compress PDF (Tools → Compress)
- Check: File size (very large?)
- Try: Close and reopen application

**Issue: Can't edit encrypted PDF**
- Solution: Decrypt first (Security → Remove Password)
- Need: Owner password

**Issue: Text extraction gibberish**
- Solution: PDF may be scanned image
- Try: OCR feature (requires tesseract)

**Issue: Signature too large/small**
- Solution: Resize image before importing
- Recommendation: 200x100 pixels for signatures

### Advanced Customization

**Edit the Code to:**
- Change default colors
- Modify stamp text
- Adjust page number format
- Customize header/footer positions
- Add custom keyboard shortcuts
- Create batch processing scripts

**Key Files to Edit:**
- `pdf_editor_pro.py`: Main application
- Functions are well-commented
- Search for function names (e.g., `add_stamp`)

### Integration Ideas

1. **Batch Processing**
   - Write scripts to process multiple PDFs
   - Automate watermarking
   - Bulk compression

2. **Custom Workflows**
   - Contract signing workflow
   - Document review process
   - Archive preparation

3. **API Integration**
   - Connect to document management systems
   - Automated processing pipelines
   - Cloud storage integration

## Getting Help

**Resources:**
- README.md: Installation and features
- This guide: Detailed usage
- PyMuPDF docs: https://pymupdf.readthedocs.io/

**Common Questions:**

Q: Can I edit scanned PDFs?
A: Text editing requires searchable text. Use OCR first.

Q: Does this work on all PDFs?
A: Yes, including encrypted (with password) and forms.

Q: Can I undo changes?
A: Only before saving. Save as new file to preserve original.

Q: Is this safe for sensitive documents?
A: Yes, all processing is local. No cloud upload.

Q: Can I use this commercially?
A: Yes, completely free for any use.

---

**Enjoy your free, full-featured PDF editor!** 🎉

For updates and improvements, check the GitHub repository.
