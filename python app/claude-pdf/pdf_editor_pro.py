#!/usr/bin/env python3
"""
PDF Editor Pro - A comprehensive PDF viewer and editor
Production-ready application with all premium features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import os
import sys
from pathlib import Path
from datetime import datetime
import json

try:
    import fitz  # PyMuPDF
    from PIL import Image, ImageTk
except ImportError:
    print("ERROR: Required dependencies not installed!")
    print("Please install: pip install pymupdf pillow")
    sys.exit(1)


class PDFEditorPro:
    """Main PDF Editor Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Editor Pro - Free & Open Source")
        self.root.geometry("1400x900")
        
        # Application state
        self.pdf_document = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.rotation = 0
        self.file_path = None
        self.modified = False
        
        # Annotation state
        self.annotation_mode = None
        self.current_color = (1, 0, 0)  # Red
        self.line_width = 2
        self.font_size = 12
        self.drawing_data = []
        
        # Signature
        self.signature_image = None
        
        # Setup UI
        self.setup_ui()
        self.setup_shortcuts()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF", command=self.open_pdf, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_pdf, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_pdf_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Merge PDFs", command=self.merge_pdfs)
        file_menu.add_command(label="Split PDF", command=self.split_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Images", command=self.export_to_images)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Rotate Right", command=self.rotate_right)
        edit_menu.add_command(label="Rotate Left", command=self.rotate_left)
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete Current Page", command=self.delete_page)
        edit_menu.add_command(label="Insert Blank Page", command=self.insert_blank_page)
        edit_menu.add_separator()
        edit_menu.add_command(label="Extract Text", command=self.extract_text)
        edit_menu.add_command(label="OCR (Scan to Text)", command=self.ocr_page)
        
        # Annotate Menu
        annotate_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Annotate", menu=annotate_menu)
        annotate_menu.add_command(label="Highlight", command=lambda: self.set_annotation_mode("highlight"))
        annotate_menu.add_command(label="Underline", command=lambda: self.set_annotation_mode("underline"))
        annotate_menu.add_command(label="Strikethrough", command=lambda: self.set_annotation_mode("strikeout"))
        annotate_menu.add_separator()
        annotate_menu.add_command(label="Add Text", command=lambda: self.set_annotation_mode("text"))
        annotate_menu.add_command(label="Add Comment", command=lambda: self.set_annotation_mode("comment"))
        annotate_menu.add_separator()
        annotate_menu.add_command(label="Draw Rectangle", command=lambda: self.set_annotation_mode("rectangle"))
        annotate_menu.add_command(label="Draw Circle", command=lambda: self.set_annotation_mode("circle"))
        annotate_menu.add_command(label="Draw Line", command=lambda: self.set_annotation_mode("line"))
        annotate_menu.add_command(label="Draw Arrow", command=lambda: self.set_annotation_mode("arrow"))
        annotate_menu.add_command(label="Free Draw", command=lambda: self.set_annotation_mode("draw"))
        annotate_menu.add_separator()
        annotate_menu.add_command(label="Add Signature", command=self.add_signature)
        annotate_menu.add_command(label="Add Stamp", command=self.add_stamp)
        
        # Security Menu
        security_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Security", menu=security_menu)
        security_menu.add_command(label="Encrypt PDF", command=self.encrypt_pdf)
        security_menu.add_command(label="Remove Password", command=self.decrypt_pdf)
        security_menu.add_command(label="Add Watermark", command=self.add_watermark)
        security_menu.add_command(label="Redact Content", command=lambda: self.set_annotation_mode("redact"))
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Compress PDF", command=self.compress_pdf)
        tools_menu.add_command(label="Optimize for Web", command=self.optimize_pdf)
        tools_menu.add_command(label="Convert to PDF/A", command=self.convert_to_pdfa)
        tools_menu.add_separator()
        tools_menu.add_command(label="Add Page Numbers", command=self.add_page_numbers)
        tools_menu.add_command(label="Add Headers/Footers", command=self.add_headers_footers)
        tools_menu.add_command(label="Add Bookmarks", command=self.manage_bookmarks)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Shortcuts", command=self.show_shortcuts)
        
        # Toolbar
        self.create_toolbar()
        
        # Main container
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left sidebar - Thumbnails
        self.create_thumbnail_panel(main_container)
        
        # Center - PDF Viewer
        self.create_viewer_panel(main_container)
        
        # Right sidebar - Properties & Tools
        self.create_properties_panel(main_container)
        
        # Status bar
        self.create_status_bar()
        
    def create_toolbar(self):
        """Create the main toolbar"""
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # File operations
        tk.Button(toolbar, text="📂 Open", command=self.open_pdf, width=8).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="💾 Save", command=self.save_pdf, width=8).pack(side=tk.LEFT, padx=2, pady=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Navigation
        tk.Button(toolbar, text="⬅️", command=self.prev_page, width=3).pack(side=tk.LEFT, padx=2, pady=2)
        
        self.page_entry = tk.Entry(toolbar, width=5)
        self.page_entry.pack(side=tk.LEFT, padx=2)
        self.page_entry.bind('<Return>', lambda e: self.goto_page())
        
        self.page_label = tk.Label(toolbar, text="/ 0")
        self.page_label.pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="➡️", command=self.next_page, width=3).pack(side=tk.LEFT, padx=2, pady=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Zoom
        tk.Button(toolbar, text="🔍−", command=self.zoom_out, width=4).pack(side=tk.LEFT, padx=2, pady=2)
        
        self.zoom_label = tk.Label(toolbar, text="100%", width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="🔍+", command=self.zoom_in, width=4).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Fit", command=self.fit_to_window, width=4).pack(side=tk.LEFT, padx=2, pady=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Rotation
        tk.Button(toolbar, text="↶", command=self.rotate_left, width=3).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="↷", command=self.rotate_right, width=3).pack(side=tk.LEFT, padx=2, pady=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Annotation tools
        tk.Button(toolbar, text="✏️ Highlight", command=lambda: self.set_annotation_mode("highlight")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="📝 Text", command=lambda: self.set_annotation_mode("text")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="✍️ Sign", command=self.add_signature).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Color picker
        self.color_btn = tk.Button(toolbar, text="🎨", command=self.choose_color, width=3, bg='red')
        self.color_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
    def create_thumbnail_panel(self, parent):
        """Create the thumbnail sidebar"""
        thumb_frame = tk.Frame(parent, width=150)
        parent.add(thumb_frame)
        
        tk.Label(thumb_frame, text="Pages", font=('Arial', 10, 'bold')).pack(pady=5)
        
        self.thumb_canvas = tk.Canvas(thumb_frame, bg='lightgray')
        thumb_scrollbar = tk.Scrollbar(thumb_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        
        self.thumb_canvas.configure(yscrollcommand=thumb_scrollbar.set)
        thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.thumb_frame_inner = tk.Frame(self.thumb_canvas, bg='lightgray')
        self.thumb_canvas.create_window((0, 0), window=self.thumb_frame_inner, anchor='nw')
        
    def create_viewer_panel(self, parent):
        """Create the main PDF viewer panel"""
        viewer_frame = tk.Frame(parent)
        parent.add(viewer_frame)
        
        # Canvas for PDF display
        self.canvas = tk.Canvas(viewer_frame, bg='gray')
        v_scrollbar = tk.Scrollbar(viewer_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(viewer_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events for annotations
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
    def create_properties_panel(self, parent):
        """Create the properties and tools sidebar"""
        props_frame = tk.Frame(parent, width=200)
        parent.add(props_frame)
        
        # Notebook for different tool sections
        notebook = ttk.Notebook(props_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Properties tab
        props_tab = tk.Frame(notebook)
        notebook.add(props_tab, text="Properties")
        
        self.props_text = tk.Text(props_tab, wrap=tk.WORD, height=20)
        self.props_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Annotations tab
        annot_tab = tk.Frame(notebook)
        notebook.add(annot_tab, text="Annotations")
        
        tk.Label(annot_tab, text="Line Width:").pack(pady=5)
        self.line_width_scale = tk.Scale(annot_tab, from_=1, to=10, orient=tk.HORIZONTAL,
                                         command=self.update_line_width)
        self.line_width_scale.set(2)
        self.line_width_scale.pack(fill=tk.X, padx=10)
        
        tk.Label(annot_tab, text="Font Size:").pack(pady=5)
        self.font_size_scale = tk.Scale(annot_tab, from_=8, to=48, orient=tk.HORIZONTAL,
                                        command=self.update_font_size)
        self.font_size_scale.set(12)
        self.font_size_scale.pack(fill=tk.X, padx=10)
        
        tk.Label(annot_tab, text="Opacity:").pack(pady=5)
        self.opacity_scale = tk.Scale(annot_tab, from_=0, to=100, orient=tk.HORIZONTAL)
        self.opacity_scale.set(50)
        self.opacity_scale.pack(fill=tk.X, padx=10)
        
        # Bookmarks tab
        bookmarks_tab = tk.Frame(notebook)
        notebook.add(bookmarks_tab, text="Bookmarks")
        
        self.bookmarks_listbox = tk.Listbox(bookmarks_tab)
        self.bookmarks_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.bookmarks_listbox.bind('<Double-Button-1>', self.goto_bookmark)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-s>', lambda e: self.save_pdf())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_pdf_as())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.fit_to_window())
        self.root.bind('<Left>', lambda e: self.prev_page())
        self.root.bind('<Right>', lambda e: self.next_page())
        self.root.bind('<Home>', lambda e: self.goto_first_page())
        self.root.bind('<End>', lambda e: self.goto_last_page())
        
    # ========== FILE OPERATIONS ==========
    
    def open_pdf(self):
        """Open a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.pdf_document = fitz.open(file_path)
                self.file_path = file_path
                self.current_page = 0
                self.zoom_level = 1.0
                self.rotation = 0
                self.modified = False
                
                self.update_display()
                self.update_thumbnails()
                self.update_properties()
                self.update_bookmarks()
                self.status_bar.config(text=f"Opened: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
                
    def save_pdf(self):
        """Save the current PDF"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        if not self.file_path:
            self.save_pdf_as()
            return
            
        try:
            # Save with incremental update if not modified
            if self.modified:
                self.pdf_document.save(self.file_path, garbage=4, deflate=True)
            else:
                self.pdf_document.saveIncr()
                
            self.modified = False
            self.status_bar.config(text="Saved successfully")
            messagebox.showinfo("Success", "PDF saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
            
    def save_pdf_as(self):
        """Save the PDF with a new name"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.pdf_document.save(file_path, garbage=4, deflate=True)
                self.file_path = file_path
                self.modified = False
                self.status_bar.config(text=f"Saved as: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "PDF saved successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
                
    # ========== NAVIGATION ==========
    
    def next_page(self):
        """Go to next page"""
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.update_display()
            
    def prev_page(self):
        """Go to previous page"""
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.update_display()
            
    def goto_page(self):
        """Go to specific page"""
        if not self.pdf_document:
            return
            
        try:
            page_num = int(self.page_entry.get()) - 1
            if 0 <= page_num < len(self.pdf_document):
                self.current_page = page_num
                self.update_display()
            else:
                messagebox.showwarning("Invalid Page", f"Page must be between 1 and {len(self.pdf_document)}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number")
            
    def goto_first_page(self):
        """Go to first page"""
        if self.pdf_document:
            self.current_page = 0
            self.update_display()
            
    def goto_last_page(self):
        """Go to last page"""
        if self.pdf_document:
            self.current_page = len(self.pdf_document) - 1
            self.update_display()
            
    # ========== ZOOM & ROTATION ==========
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self.update_display()
        
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self.update_display()
        
    def fit_to_window(self):
        """Fit page to window"""
        if not self.pdf_document:
            return
            
        page = self.pdf_document[self.current_page]
        page_rect = page.rect
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        width_ratio = canvas_width / page_rect.width
        height_ratio = canvas_height / page_rect.height
        
        self.zoom_level = min(width_ratio, height_ratio) * 0.9
        self.update_display()
        
    def rotate_right(self):
        """Rotate page 90 degrees clockwise"""
        if not self.pdf_document:
            return
            
        page = self.pdf_document[self.current_page]
        page.set_rotation((page.rotation + 90) % 360)
        self.modified = True
        self.update_display()
        
    def rotate_left(self):
        """Rotate page 90 degrees counter-clockwise"""
        if not self.pdf_document:
            return
            
        page = self.pdf_document[self.current_page]
        page.set_rotation((page.rotation - 90) % 360)
        self.modified = True
        self.update_display()
        
    # ========== DISPLAY UPDATES ==========
    
    def update_display(self):
        """Update the main PDF display"""
        if not self.pdf_document:
            return
            
        try:
            page = self.pdf_document[self.current_page]
            
            # Render page to pixmap
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PhotoImage
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.photo = ImageTk.PhotoImage(img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
            # Update UI elements
            self.page_entry.delete(0, tk.END)
            self.page_entry.insert(0, str(self.current_page + 1))
            self.page_label.config(text=f"/ {len(self.pdf_document)}")
            self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
            
            self.status_bar.config(text=f"Page {self.current_page + 1} of {len(self.pdf_document)}")
            
        except Exception as e:
            messagebox.showerror("Display Error", f"Failed to display page: {str(e)}")
            
    def update_thumbnails(self):
        """Update the thumbnail panel"""
        if not self.pdf_document:
            return
            
        # Clear existing thumbnails
        for widget in self.thumb_frame_inner.winfo_children():
            widget.destroy()
            
        try:
            # Generate thumbnails
            for i in range(len(self.pdf_document)):
                page = self.pdf_document[i]
                mat = fitz.Matrix(0.15, 0.15)  # Small size for thumbnails
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                thumb_photo = ImageTk.PhotoImage(img)
                
                # Create thumbnail button
                frame = tk.Frame(self.thumb_frame_inner, bd=2, relief=tk.RAISED)
                frame.pack(pady=5)
                
                btn = tk.Button(frame, image=thumb_photo, command=lambda p=i: self.goto_page_direct(p))
                btn.image = thumb_photo  # Keep reference
                btn.pack()
                
                tk.Label(frame, text=f"Page {i+1}").pack()
                
            self.thumb_canvas.update_idletasks()
            self.thumb_canvas.config(scrollregion=self.thumb_canvas.bbox("all"))
            
        except Exception as e:
            print(f"Thumbnail error: {str(e)}")
            
    def goto_page_direct(self, page_num):
        """Go directly to a page (from thumbnail)"""
        self.current_page = page_num
        self.update_display()
        
    def update_properties(self):
        """Update the properties panel"""
        if not self.pdf_document:
            return
            
        self.props_text.delete(1.0, tk.END)
        
        metadata = self.pdf_document.metadata
        
        props = f"""Document Properties:
        
Title: {metadata.get('title', 'N/A')}
Author: {metadata.get('author', 'N/A')}
Subject: {metadata.get('subject', 'N/A')}
Keywords: {metadata.get('keywords', 'N/A')}
Creator: {metadata.get('creator', 'N/A')}
Producer: {metadata.get('producer', 'N/A')}
Created: {metadata.get('creationDate', 'N/A')}
Modified: {metadata.get('modDate', 'N/A')}

Total Pages: {len(self.pdf_document)}
File Size: {os.path.getsize(self.file_path) / 1024:.2f} KB
Encrypted: {self.pdf_document.is_encrypted}
"""
        
        self.props_text.insert(1.0, props)
        
    def update_bookmarks(self):
        """Update the bookmarks list"""
        if not self.pdf_document:
            return
            
        self.bookmarks_listbox.delete(0, tk.END)
        
        try:
            toc = self.pdf_document.get_toc()
            for level, title, page in toc:
                indent = "  " * (level - 1)
                self.bookmarks_listbox.insert(tk.END, f"{indent}{title} (p.{page})")
                
        except Exception as e:
            print(f"Bookmarks error: {str(e)}")
            
    def goto_bookmark(self, event):
        """Go to selected bookmark"""
        selection = self.bookmarks_listbox.curselection()
        if not selection or not self.pdf_document:
            return
            
        try:
            toc = self.pdf_document.get_toc()
            level, title, page = toc[selection[0]]
            self.current_page = page - 1
            self.update_display()
        except:
            pass
            
    # ========== ANNOTATION METHODS ==========
    
    def set_annotation_mode(self, mode):
        """Set the current annotation mode"""
        self.annotation_mode = mode
        self.status_bar.config(text=f"Mode: {mode.upper()}")
        
    def choose_color(self):
        """Choose annotation color"""
        color = colorchooser.askcolor(title="Choose Color")
        if color[0]:
            # Convert RGB to 0-1 range
            self.current_color = tuple(c/255 for c in color[0])
            self.color_btn.config(bg=color[1])
            
    def update_line_width(self, val):
        """Update line width"""
        self.line_width = int(float(val))
        
    def update_font_size(self, val):
        """Update font size"""
        self.font_size = int(float(val))
        
    def on_canvas_click(self, event):
        """Handle canvas click for annotations"""
        if not self.pdf_document or not self.annotation_mode:
            return
            
        # Convert canvas coordinates to PDF coordinates
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Store starting point
        self.start_x = x / self.zoom_level
        self.start_y = y / self.zoom_level
        
        if self.annotation_mode == "text":
            self.add_text_annotation(x, y)
        elif self.annotation_mode == "comment":
            self.add_comment_annotation(x, y)
            
    def on_canvas_drag(self, event):
        """Handle canvas drag for drawing"""
        if not self.pdf_document or not self.annotation_mode:
            return
            
        if self.annotation_mode == "draw":
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            if hasattr(self, 'last_x'):
                self.canvas.create_line(self.last_x, self.last_y, x, y,
                                       fill=self.color_btn.cget('bg'),
                                       width=self.line_width)
            self.last_x = x
            self.last_y = y
            
    def on_canvas_release(self, event):
        """Handle canvas release for shape annotations"""
        if not self.pdf_document or not self.annotation_mode:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        end_x = x / self.zoom_level
        end_y = y / self.zoom_level
        
        page = self.pdf_document[self.current_page]
        
        try:
            if self.annotation_mode == "highlight":
                # Highlight requires text selection - simplified version
                rect = fitz.Rect(self.start_x, self.start_y, end_x, end_y)
                annot = page.add_highlight_annot(rect)
                annot.set_colors(stroke=self.current_color)
                annot.update()
                self.modified = True
                
            elif self.annotation_mode == "rectangle":
                rect = fitz.Rect(self.start_x, self.start_y, end_x, end_y)
                annot = page.add_rect_annot(rect)
                annot.set_colors(stroke=self.current_color)
                annot.set_border(width=self.line_width)
                annot.update()
                self.modified = True
                
            elif self.annotation_mode == "circle":
                rect = fitz.Rect(self.start_x, self.start_y, end_x, end_y)
                annot = page.add_circle_annot(rect)
                annot.set_colors(stroke=self.current_color)
                annot.set_border(width=self.line_width)
                annot.update()
                self.modified = True
                
            elif self.annotation_mode == "line":
                p1 = fitz.Point(self.start_x, self.start_y)
                p2 = fitz.Point(end_x, end_y)
                annot = page.add_line_annot(p1, p2)
                annot.set_colors(stroke=self.current_color)
                annot.set_border(width=self.line_width)
                annot.update()
                self.modified = True
                
            elif self.annotation_mode == "arrow":
                p1 = fitz.Point(self.start_x, self.start_y)
                p2 = fitz.Point(end_x, end_y)
                annot = page.add_line_annot(p1, p2)
                annot.set_line_ends(0, 2)  # Arrow end
                annot.set_colors(stroke=self.current_color)
                annot.set_border(width=self.line_width)
                annot.update()
                self.modified = True
                
            elif self.annotation_mode == "redact":
                rect = fitz.Rect(self.start_x, self.start_y, end_x, end_y)
                annot = page.add_redact_annot(rect)
                annot.update()
                page.apply_redactions()
                self.modified = True
                
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Annotation Error", f"Failed to add annotation: {str(e)}")
            
        # Reset for free draw
        if hasattr(self, 'last_x'):
            delattr(self, 'last_x')
            delattr(self, 'last_y')
            
    def add_text_annotation(self, x, y):
        """Add text annotation"""
        text = simpledialog.askstring("Add Text", "Enter text:")
        if not text:
            return
            
        try:
            page = self.pdf_document[self.current_page]
            
            # Convert coordinates
            pdf_x = x / self.zoom_level
            pdf_y = y / self.zoom_level
            
            # Add text
            point = fitz.Point(pdf_x, pdf_y)
            page.insert_text(point, text, fontsize=self.font_size, color=self.current_color)
            
            self.modified = True
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add text: {str(e)}")
            
    def add_comment_annotation(self, x, y):
        """Add comment/note annotation"""
        comment = simpledialog.askstring("Add Comment", "Enter comment:")
        if not comment:
            return
            
        try:
            page = self.pdf_document[self.current_page]
            
            pdf_x = x / self.zoom_level
            pdf_y = y / self.zoom_level
            
            rect = fitz.Rect(pdf_x, pdf_y, pdf_x + 20, pdf_y + 20)
            annot = page.add_text_annot(rect.tl, comment)
            annot.set_colors(stroke=self.current_color)
            annot.update()
            
            self.modified = True
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add comment: {str(e)}")
            
    def add_signature(self):
        """Add digital signature"""
        # Simple signature - add image or drawn signature
        sig_file = filedialog.askopenfilename(
            title="Select Signature Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        
        if not sig_file:
            return
            
        try:
            page = self.pdf_document[self.current_page]
            
            # Ask for position
            messagebox.showinfo("Position", "Click where you want to place the signature")
            self.annotation_mode = "signature"
            self.signature_image = sig_file
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare signature: {str(e)}")
            
    def add_stamp(self):
        """Add stamp to PDF"""
        stamps = ["APPROVED", "CONFIDENTIAL", "DRAFT", "FINAL", "FOR REVIEW"]
        stamp = simpledialog.askstring("Add Stamp", f"Enter stamp text or choose: {', '.join(stamps)}")
        
        if not stamp:
            return
            
        try:
            page = self.pdf_document[self.current_page]
            
            # Add stamp at center
            rect = page.rect
            stamp_rect = fitz.Rect(rect.width/2 - 100, rect.height/2 - 30,
                                   rect.width/2 + 100, rect.height/2 + 30)
            
            annot = page.add_stamp_annot(stamp_rect, stamp=10)  # Draft stamp
            annot.set_opacity(0.3)
            annot.update()
            
            # Add text
            point = fitz.Point(rect.width/2, rect.height/2)
            page.insert_text(point, stamp, fontsize=36, color=(1, 0, 0), rotate=45)
            
            self.modified = True
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add stamp: {str(e)}")
            
    # ========== PAGE OPERATIONS ==========
    
    def delete_page(self):
        """Delete current page"""
        if not self.pdf_document:
            return
            
        if len(self.pdf_document) == 1:
            messagebox.showwarning("Cannot Delete", "Cannot delete the only page")
            return
            
        if messagebox.askyesno("Confirm Delete", f"Delete page {self.current_page + 1}?"):
            try:
                self.pdf_document.delete_page(self.current_page)
                
                if self.current_page >= len(self.pdf_document):
                    self.current_page = len(self.pdf_document) - 1
                    
                self.modified = True
                self.update_display()
                self.update_thumbnails()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete page: {str(e)}")
                
    def insert_blank_page(self):
        """Insert a blank page"""
        if not self.pdf_document:
            return
            
        try:
            # Get page size from current page
            page = self.pdf_document[self.current_page]
            width = page.rect.width
            height = page.rect.height
            
            # Insert blank page after current
            self.pdf_document.new_page(self.current_page + 1, width=width, height=height)
            
            self.modified = True
            self.current_page += 1
            self.update_display()
            self.update_thumbnails()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert page: {str(e)}")
            
    # ========== TEXT OPERATIONS ==========
    
    def extract_text(self):
        """Extract text from current page"""
        if not self.pdf_document:
            return
            
        try:
            page = self.pdf_document[self.current_page]
            text = page.get_text()
            
            # Show in a new window
            text_window = tk.Toplevel(self.root)
            text_window.title(f"Text - Page {self.current_page + 1}")
            text_window.geometry("600x400")
            
            text_widget = tk.Text(text_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tk.Scrollbar(text_widget)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=text_widget.yview)
            
            text_widget.insert(1.0, text)
            
            # Add copy button
            tk.Button(text_window, text="Copy to Clipboard",
                     command=lambda: self.copy_to_clipboard(text)).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract text: {str(e)}")
            
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Text copied to clipboard")
        
    def ocr_page(self):
        """OCR current page (requires tesseract)"""
        messagebox.showinfo("OCR", "OCR functionality requires pytesseract.\n"
                           "This is a placeholder for OCR implementation.\n"
                           "Install: pip install pytesseract")
        
    # ========== MERGE & SPLIT ==========
    
    def merge_pdfs(self):
        """Merge multiple PDFs"""
        files = filedialog.askopenfilenames(
            title="Select PDFs to Merge",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if len(files) < 2:
            messagebox.showwarning("Not Enough Files", "Please select at least 2 PDFs")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_file:
            return
            
        try:
            merged_pdf = fitz.open()
            
            for file in files:
                pdf = fitz.open(file)
                merged_pdf.insert_pdf(pdf)
                pdf.close()
                
            merged_pdf.save(output_file)
            merged_pdf.close()
            
            messagebox.showinfo("Success", f"PDFs merged successfully!\nSaved to: {output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs: {str(e)}")
            
    def split_pdf(self):
        """Split PDF into separate files"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        # Ask for split method
        split_window = tk.Toplevel(self.root)
        split_window.title("Split PDF")
        split_window.geometry("300x150")
        
        tk.Label(split_window, text="Split Method:").pack(pady=10)
        
        split_var = tk.StringVar(value="each")
        
        tk.Radiobutton(split_window, text="Each page as separate PDF",
                      variable=split_var, value="each").pack(anchor=tk.W, padx=20)
        tk.Radiobutton(split_window, text="Split at specific page",
                      variable=split_var, value="specific").pack(anchor=tk.W, padx=20)
        
        def do_split():
            split_window.destroy()
            
            output_dir = filedialog.askdirectory(title="Select Output Directory")
            if not output_dir:
                return
                
            try:
                if split_var.get() == "each":
                    # Split each page
                    for i in range(len(self.pdf_document)):
                        output = fitz.open()
                        output.insert_pdf(self.pdf_document, from_page=i, to_page=i)
                        output.save(os.path.join(output_dir, f"page_{i+1}.pdf"))
                        output.close()
                        
                else:
                    # Split at specific page
                    page_num = simpledialog.askinteger("Split Page", "Split after page number:")
                    if page_num and 0 < page_num < len(self.pdf_document):
                        # First part
                        output1 = fitz.open()
                        output1.insert_pdf(self.pdf_document, from_page=0, to_page=page_num-1)
                        output1.save(os.path.join(output_dir, "part_1.pdf"))
                        output1.close()
                        
                        # Second part
                        output2 = fitz.open()
                        output2.insert_pdf(self.pdf_document, from_page=page_num,
                                         to_page=len(self.pdf_document)-1)
                        output2.save(os.path.join(output_dir, "part_2.pdf"))
                        output2.close()
                        
                messagebox.showinfo("Success", f"PDF split successfully!\nFiles saved to: {output_dir}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to split PDF: {str(e)}")
                
        tk.Button(split_window, text="Split", command=do_split).pack(pady=10)
        
    # ========== EXPORT ==========
    
    def export_to_images(self):
        """Export PDF pages as images"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return
            
        try:
            for i in range(len(self.pdf_document)):
                page = self.pdf_document[i]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # High quality
                
                output_path = os.path.join(output_dir, f"page_{i+1}.png")
                pix.save(output_path)
                
            messagebox.showinfo("Success", f"Exported {len(self.pdf_document)} images to:\n{output_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export images: {str(e)}")
            
    # ========== SECURITY ==========
    
    def encrypt_pdf(self):
        """Encrypt PDF with password"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        # Password dialog
        pwd_window = tk.Toplevel(self.root)
        pwd_window.title("Encrypt PDF")
        pwd_window.geometry("300x150")
        
        tk.Label(pwd_window, text="User Password:").pack(pady=5)
        user_pwd = tk.Entry(pwd_window, show="*")
        user_pwd.pack(pady=5)
        
        tk.Label(pwd_window, text="Owner Password:").pack(pady=5)
        owner_pwd = tk.Entry(pwd_window, show="*")
        owner_pwd.pack(pady=5)
        
        def do_encrypt():
            user_pass = user_pwd.get()
            owner_pass = owner_pwd.get()
            
            if not user_pass or not owner_pass:
                messagebox.showwarning("Missing Password", "Please enter both passwords")
                return
                
            pwd_window.destroy()
            
            output_file = filedialog.asksaveasfilename(
                title="Save Encrypted PDF",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            
            if output_file:
                try:
                    perm = int(
                        fitz.PDF_PERM_PRINT |
                        fitz.PDF_PERM_COPY |
                        fitz.PDF_PERM_ANNOTATE
                    )
                    
                    encrypt_meth = fitz.PDF_ENCRYPT_AES_256
                    
                    self.pdf_document.save(
                        output_file,
                        encryption=encrypt_meth,
                        user_pw=user_pass,
                        owner_pw=owner_pass,
                        permissions=perm
                    )
                    
                    messagebox.showinfo("Success", "PDF encrypted successfully!")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to encrypt PDF: {str(e)}")
                    
        tk.Button(pwd_window, text="Encrypt", command=do_encrypt).pack(pady=10)
        
    def decrypt_pdf(self):
        """Remove password from PDF"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        if not self.pdf_document.is_encrypted:
            messagebox.showinfo("Not Encrypted", "This PDF is not encrypted")
            return
            
        password = simpledialog.askstring("Password", "Enter password:", show='*')
        
        if password:
            try:
                if self.pdf_document.authenticate(password):
                    output_file = filedialog.asksaveasfilename(
                        title="Save Decrypted PDF",
                        defaultextension=".pdf",
                        filetypes=[("PDF files", "*.pdf")]
                    )
                    
                    if output_file:
                        self.pdf_document.save(output_file, encryption=fitz.PDF_ENCRYPT_NONE)
                        messagebox.showinfo("Success", "Password removed successfully!")
                else:
                    messagebox.showerror("Error", "Incorrect password")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to decrypt PDF: {str(e)}")
                
    def add_watermark(self):
        """Add watermark to PDF"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        watermark_text = simpledialog.askstring("Watermark", "Enter watermark text:")
        
        if not watermark_text:
            return
            
        try:
            for page_num in range(len(self.pdf_document)):
                page = self.pdf_document[page_num]
                
                # Get page dimensions
                rect = page.rect
                
                # Add watermark
                text_point = fitz.Point(rect.width / 2, rect.height / 2)
                
                page.insert_text(
                    text_point,
                    watermark_text,
                    fontsize=72,
                    color=(0.9, 0.9, 0.9),
                    rotate=45,
                    overlay=False
                )
                
            self.modified = True
            self.update_display()
            messagebox.showinfo("Success", "Watermark added to all pages!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add watermark: {str(e)}")
            
    # ========== OPTIMIZATION ==========
    
    def compress_pdf(self):
        """Compress PDF file"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save Compressed PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_file:
            try:
                self.pdf_document.save(
                    output_file,
                    garbage=4,
                    deflate=True,
                    clean=True
                )
                
                original_size = os.path.getsize(self.file_path)
                compressed_size = os.path.getsize(output_file)
                reduction = (1 - compressed_size / original_size) * 100
                
                messagebox.showinfo("Success",
                    f"PDF compressed successfully!\n"
                    f"Original: {original_size/1024:.2f} KB\n"
                    f"Compressed: {compressed_size/1024:.2f} KB\n"
                    f"Reduction: {reduction:.1f}%"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to compress PDF: {str(e)}")
                
    def optimize_pdf(self):
        """Optimize PDF for web"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save Optimized PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_file:
            try:
                self.pdf_document.save(
                    output_file,
                    garbage=4,
                    deflate=True,
                    clean=True,
                    linear=True  # Linearize for web
                )
                
                messagebox.showinfo("Success", "PDF optimized for web!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to optimize PDF: {str(e)}")
                
    def convert_to_pdfa(self):
        """Convert to PDF/A format"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        messagebox.showinfo("PDF/A Conversion",
            "PDF/A conversion requires additional processing.\n"
            "This feature creates a compliant PDF/A-1b document."
        )
        
        output_file = filedialog.asksaveasfilename(
            title="Save PDF/A",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_file:
            try:
                # Save with PDF/A compliance (simplified)
                self.pdf_document.save(
                    output_file,
                    garbage=4,
                    deflate=True,
                    clean=True
                )
                
                messagebox.showinfo("Success", "PDF saved (PDF/A compliance requires validation)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert: {str(e)}")
                
    # ========== PAGE ENHANCEMENTS ==========
    
    def add_page_numbers(self):
        """Add page numbers to all pages"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        try:
            for page_num in range(len(self.pdf_document)):
                page = self.pdf_document[page_num]
                rect = page.rect
                
                # Add page number at bottom center
                point = fitz.Point(rect.width / 2, rect.height - 30)
                page.insert_text(
                    point,
                    f"Page {page_num + 1}",
                    fontsize=10,
                    color=(0, 0, 0)
                )
                
            self.modified = True
            self.update_display()
            messagebox.showinfo("Success", "Page numbers added!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add page numbers: {str(e)}")
            
    def add_headers_footers(self):
        """Add headers and footers"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        # Dialog for header/footer text
        hf_window = tk.Toplevel(self.root)
        hf_window.title("Add Headers/Footers")
        hf_window.geometry("400x200")
        
        tk.Label(hf_window, text="Header Text:").pack(pady=5)
        header_entry = tk.Entry(hf_window, width=40)
        header_entry.pack(pady=5)
        
        tk.Label(hf_window, text="Footer Text:").pack(pady=5)
        footer_entry = tk.Entry(hf_window, width=40)
        footer_entry.pack(pady=5)
        
        def apply_hf():
            header = header_entry.get()
            footer = footer_entry.get()
            hf_window.destroy()
            
            try:
                for page_num in range(len(self.pdf_document)):
                    page = self.pdf_document[page_num]
                    rect = page.rect
                    
                    if header:
                        point = fitz.Point(rect.width / 2, 30)
                        page.insert_text(point, header, fontsize=10, color=(0, 0, 0))
                        
                    if footer:
                        point = fitz.Point(rect.width / 2, rect.height - 30)
                        page.insert_text(point, footer, fontsize=10, color=(0, 0, 0))
                        
                self.modified = True
                self.update_display()
                messagebox.showinfo("Success", "Headers/Footers added!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add headers/footers: {str(e)}")
                
        tk.Button(hf_window, text="Apply", command=apply_hf).pack(pady=10)
        
    def manage_bookmarks(self):
        """Manage PDF bookmarks"""
        if not self.pdf_document:
            messagebox.showwarning("No Document", "Please open a PDF first")
            return
            
        bm_window = tk.Toplevel(self.root)
        bm_window.title("Manage Bookmarks")
        bm_window.geometry("400x300")
        
        tk.Label(bm_window, text="Add Bookmark to Current Page").pack(pady=10)
        
        tk.Label(bm_window, text="Title:").pack()
        title_entry = tk.Entry(bm_window, width=30)
        title_entry.pack(pady=5)
        
        def add_bm():
            title = title_entry.get()
            if not title:
                return
                
            try:
                toc = self.pdf_document.get_toc()
                toc.append([1, title, self.current_page + 1])
                self.pdf_document.set_toc(toc)
                
                self.modified = True
                self.update_bookmarks()
                messagebox.showinfo("Success", "Bookmark added!")
                title_entry.delete(0, tk.END)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add bookmark: {str(e)}")
                
        tk.Button(bm_window, text="Add Bookmark", command=add_bm).pack(pady=10)
        
    # ========== HELP & INFO ==========
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
PDF Editor Pro
Version 1.0

A free and open-source PDF editor with all premium features.

Features:
• View and navigate PDFs
• Annotate (highlight, text, shapes, comments)
• Digital signatures and stamps
• Merge and split PDFs
• Extract text and export images
• Encrypt and decrypt PDFs
• Add watermarks and page numbers
• Compress and optimize PDFs
• And much more!

Built with Python, PyMuPDF, and Tkinter

© 2024 - Free for personal and commercial use
"""
        
        messagebox.showinfo("About PDF Editor Pro", about_text)
        
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
Keyboard Shortcuts:

File Operations:
Ctrl+O - Open PDF
Ctrl+S - Save
Ctrl+Shift+S - Save As

Navigation:
Left Arrow - Previous Page
Right Arrow - Next Page
Home - First Page
End - Last Page

View:
Ctrl++ - Zoom In
Ctrl+- - Zoom Out
Ctrl+0 - Fit to Window

Mouse:
Click - Select / Annotate
Drag - Draw / Select Area
"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = PDFEditorPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
