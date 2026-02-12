"""
PDF Engine Module - Core PDF operations using PyMuPDF and pikepdf
"""

import fitz  # PyMuPDF
import pikepdf
from PIL import Image, ImageDraw, ImageFont
import io
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import copy
import hashlib
from datetime import datetime


class PDFPage:
    """Represents a single PDF page."""
    
    def __init__(self, page_num: int, fitz_page: fitz.Page):
        self.page_num = page_num
        self.fitz_page = fitz_page
        self.rotation = fitz_page.rotation
        self.annotations: List[Dict] = []
        
    @property
    def width(self) -> float:
        return self.fitz_page.rect.width
        
    @property
    def height(self) -> float:
        return self.fitz_page.rect.height
        
    def get_pixmap(self, zoom: float = 1.0, rotation: int = 0) -> fitz.Pixmap:
        """Get rendered pixmap of the page."""
        mat = fitz.Matrix(zoom, zoom)
        if rotation:
            mat = mat.prerotate(rotation)
        return self.fitz_page.get_pixmap(matrix=mat)
        
    def get_text(self) -> str:
        """Extract text from page."""
        return self.fitz_page.get_text()
        
    def search_text(self, text: str) -> List[fitz.Rect]:
        """Search for text on page and return bounding boxes."""
        return self.fitz_page.search_for(text)


@dataclass
class PDFMetadata:
    """PDF document metadata."""
    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    

class PDFEngine:
    """Core PDF engine for loading, rendering, and manipulating PDFs."""
    
    def __init__(self):
        self.document: Optional[fitz.Document] = None
        self.pike_document: Optional[pikepdf.Pdf] = None
        self.file_path: Optional[str] = None
        self.pages: List[PDFPage] = []
        self.metadata: PDFMetadata = PDFMetadata()
        self._undo_stack: List[Dict] = []
        self._redo_stack: List[Dict] = []
        self._max_undo = 50
        
    @property
    def page_count(self) -> int:
        """Get total number of pages."""
        return len(self.pages) if self.document else 0
        
    @property
    def is_loaded(self) -> bool:
        """Check if a document is loaded."""
        return self.document is not None
        
    def new_document(self):
        """Create a new blank PDF document."""
        self._save_state()
        self.document = fitz.open()
        self.pike_document = pikepdf.Pdf.new()
        self.file_path = None
        self.pages = []
        self.metadata = PDFMetadata()
        
        # Add first page
        self.add_page()
        
    def load(self, file_path: str):
        """Load a PDF file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        self._save_state()
        
        # Load with PyMuPDF for rendering
        self.document = fitz.open(file_path)
        
        # Load with pikepdf for advanced operations
        try:
            self.pike_document = pikepdf.open(file_path)
        except Exception:
            self.pike_document = None
            
        self.file_path = file_path
        
        # Build page list
        self.pages = []
        for i in range(len(self.document)):
            page = PDFPage(i, self.document[i])
            self.pages.append(page)
            
        # Load metadata
        self._load_metadata()
        
    def _load_metadata(self):
        """Load document metadata."""
        if self.document:
            meta = self.document.metadata
            self.metadata = PDFMetadata(
                title=meta.get('title', ''),
                author=meta.get('author', ''),
                subject=meta.get('subject', ''),
                keywords=meta.get('keywords', ''),
                creator=meta.get('creator', ''),
                producer=meta.get('producer', ''),
            )
            
    def save(self, file_path: Optional[str] = None):
        """Save the PDF document."""
        if file_path:
            self.file_path = file_path
            
        if not self.file_path:
            raise ValueError("No file path specified")
            
        # Apply any pending changes
        self._apply_changes()
        
        # Save document
        if self.document:
            self.document.save(
                self.file_path,
                garbage=4,  # Maximum compression
                deflate=True,
                clean=True
            )
            
        # Also save with pikepdf if available
        if self.pike_document:
            self.pike_document.save(self.file_path)
            
    def _apply_changes(self):
        """Apply all pending changes to the document."""
        # This method would apply annotations, form fields, etc.
        pass
        
    def _save_state(self):
        """Save current state for undo."""
        if self.document:
            state = {
                'document': copy.deepcopy(self.document),
                'pages': copy.deepcopy(self.pages),
                'metadata': copy.deepcopy(self.metadata)
            }
            self._undo_stack.append(state)
            if len(self._undo_stack) > self._max_undo:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
            
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0
        
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
        
    def undo(self):
        """Undo last operation."""
        if self.can_undo():
            state = self._undo_stack.pop()
            self._redo_stack.append({
                'document': self.document,
                'pages': self.pages,
                'metadata': self.metadata
            })
            self.document = state['document']
            self.pages = state['pages']
            self.metadata = state['metadata']
            
    def redo(self):
        """Redo last undone operation."""
        if self.can_redo():
            state = self._redo_stack.pop()
            self._undo_stack.append({
                'document': self.document,
                'pages': self.pages,
                'metadata': self.metadata
            })
            self.document = state['document']
            self.pages = state['pages']
            self.metadata = state['metadata']
            
    # ==================== Page Operations ====================
    
    def get_page(self, page_num: int) -> Optional[PDFPage]:
        """Get a specific page."""
        if 0 <= page_num < len(self.pages):
            return self.pages[page_num]
        return None
        
    def add_page(self, width: float = 612, height: float = 792, 
                 index: Optional[int] = None) -> PDFPage:
        """Add a new blank page."""
        self._save_state()
        
        if index is None:
            index = len(self.pages)
            
        rect = fitz.Rect(0, 0, width, height)
        self.document.new_page(pno=index, width=width, height=height)
        
        # Rebuild page list
        self.pages = []
        for i in range(len(self.document)):
            page = PDFPage(i, self.document[i])
            self.pages.append(page)
            
        return self.pages[index]
        
    def delete_page(self, page_num: int):
        """Delete a page."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            self.document.delete_page(page_num)
            self.pages.pop(page_num)
            
            # Update page numbers
            for i, page in enumerate(self.pages):
                page.page_num = i
                
    def move_page(self, from_index: int, to_index: int):
        """Move a page to a different position."""
        self._save_state()
        
        if 0 <= from_index < len(self.pages) and 0 <= to_index <= len(self.pages):
            self.document.move_page(from_index, to_index)
            
            # Rebuild page list
            self.pages = []
            for i in range(len(self.document)):
                page = PDFPage(i, self.document[i])
                self.pages.append(page)
                
    def rotate_page(self, page_num: int, angle: int):
        """Rotate a page."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            page.set_rotation(page.rotation + angle)
            self.pages[page_num].rotation = page.rotation
            
    def duplicate_page(self, page_num: int):
        """Duplicate a page."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            self.document.fullcopy_page(page_num, page_num + 1)
            
            # Rebuild page list
            self.pages = []
            for i in range(len(self.document)):
                page = PDFPage(i, self.document[i])
                self.pages.append(page)
                
    def insert_image_page(self, image_path: str, index: Optional[int] = None):
        """Insert an image as a new page."""
        self._save_state()
        
        if index is None:
            index = len(self.pages)
            
        # Open image to get dimensions
        img = Image.open(image_path)
        width, height = img.size
        
        # Create new page with image dimensions
        page = self.add_page(width, height, index)
        
        # Insert image
        rect = fitz.Rect(0, 0, width, height)
        page.fitz_page.insert_image(rect, filename=image_path)
        
    # ==================== Content Operations ====================
    
    def insert_text(self, page_num: int, text: str, x: float, y: float,
                    font_size: float = 12, color: Tuple[float, float, float] = (0, 0, 0),
                    font_name: str = "helv"):
        """Insert text on a page."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            
            # Map font names
            font_map = {
                "helv": fitz.Font("helv"),
                "cour": fitz.Font("cour"),
                "tiro": fitz.Font("tiro"),
                "symb": fitz.Font("symb"),
            }
            font = font_map.get(font_name, fitz.Font("helv"))
            
            # Insert text
            page.insert_text(
                (x, y),
                text,
                fontsize=font_size,
                font=font,
                color=color
            )
            
    def insert_image(self, page_num: int, image_path: str, 
                     rect: Optional[fitz.Rect] = None):
        """Insert an image on a page."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            
            if rect is None:
                # Default size
                img = Image.open(image_path)
                width, height = img.size
                rect = fitz.Rect(0, 0, width, height)
                
            page.insert_image(rect, filename=image_path)
            
    def draw_shape(self, page_num: int, shape_type: str, 
                   points: List[Tuple[float, float]],
                   color: Tuple[float, float, float] = (0, 0, 0),
                   width: float = 1.0, fill: Optional[Tuple[float, float, float]] = None):
        """Draw a shape on a page."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            shape = page.new_shape()
            
            if shape_type == "line" and len(points) >= 2:
                shape.draw_line(points[0], points[1])
            elif shape_type == "rectangle" and len(points) >= 2:
                rect = fitz.Rect(points[0], points[1])
                shape.draw_rect(rect)
            elif shape_type == "circle" and len(points) >= 2:
                rect = fitz.Rect(points[0], points[1])
                shape.draw_oval(rect)
            elif shape_type == "polygon" and len(points) >= 3:
                shape.draw_polyline(points)
                
            shape.finish(color=color, fill=fill, width=width)
            shape.commit()
            
    def add_highlight(self, page_num: int, rect: fitz.Rect, 
                      color: Tuple[float, float, float] = (1, 1, 0)):
        """Add highlight annotation."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            highlight = page.add_highlight_annot(rect)
            highlight.set_colors(stroke=color)
            highlight.update()
            
    def add_underline(self, page_num: int, rect: fitz.Rect,
                      color: Tuple[float, float, float] = (0, 0, 1)):
        """Add underline annotation."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            underline = page.add_underline_annot(rect)
            underline.set_colors(stroke=color)
            underline.update()
            
    def add_strikethrough(self, page_num: int, rect: fitz.Rect,
                          color: Tuple[float, float, float] = (1, 0, 0)):
        """Add strikethrough annotation."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            strike = page.add_strikeout_annot(rect)
            strike.set_colors(stroke=color)
            strike.update()
            
    def add_text_annotation(self, page_num: int, rect: fitz.Rect, 
                            text: str, icon: str = "Note"):
        """Add a text annotation (sticky note)."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            annot = page.add_text_annot(rect.tl, text, icon=icon)
            annot.update()
            
    def add_freehand(self, page_num: int, points: List[Tuple[float, float]],
                     color: Tuple[float, float, float] = (0, 0, 0),
                     width: float = 1.0):
        """Add freehand drawing annotation."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            
            # Create ink annotation
            vertices = []
            for point in points:
                vertices.append((point[0], point[1]))
                
            annot = page.add_ink_annot([vertices])
            annot.set_colors(stroke=color)
            annot.set_border(width=width)
            annot.update()
            
    def delete_annotation(self, page_num: int, annot_index: int):
        """Delete an annotation."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            annots = list(page.annots())
            if 0 <= annot_index < len(annots):
                page.delete_annot(annots[annot_index])
                
    # ==================== Search & Replace ====================
    
    def search(self, text: str, case_sensitive: bool = False,
               whole_words: bool = False) -> List[Dict]:
        """Search for text in the document."""
        results = []
        
        for page_num, page in enumerate(self.pages):
            rects = page.search_text(text)
            for rect in rects:
                results.append({
                    'page': page_num,
                    'rect': rect,
                    'text': text
                })
                
        return results
        
    def replace_text(self, page_num: int, old_text: str, new_text: str,
                     rect: Optional[fitz.Rect] = None):
        """Replace text on a page."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.document[page_num]
            
            # Use redaction to remove old text
            if rect:
                page.add_redact_annot(rect, text=new_text)
            else:
                # Search for text and redact
                rects = page.search_text(old_text)
                for r in rects:
                    page.add_redact_annot(r, text=new_text)
                    
            page.apply_redactions()
            
    # ==================== Advanced Operations ====================
    
    def merge_pdfs(self, file_paths: List[str], output_path: str):
        """Merge multiple PDFs into one."""
        merged = fitz.open()
        
        for file_path in file_paths:
            doc = fitz.open(file_path)
            merged.insert_pdf(doc)
            doc.close()
            
        merged.save(output_path)
        merged.close()
        
    def split_pdf(self, page_ranges: List[Tuple[int, int]], output_folder: str):
        """Split PDF into multiple files."""
        base_name = Path(self.file_path).stem if self.file_path else "split"
        
        for i, (start, end) in enumerate(page_ranges):
            new_doc = fitz.open()
            new_doc.insert_pdf(self.document, from_page=start, to_page=end)
            
            output_path = os.path.join(output_folder, f"{base_name}_part{i+1}.pdf")
            new_doc.save(output_path)
            new_doc.close()
            
    def compress(self, quality: str, output_path: str):
        """Compress PDF with specified quality."""
        # Quality settings
        quality_settings = {
            'low': {'dpi': 72, 'quality': 30},
            'medium': {'dpi': 150, 'quality': 60},
            'high': {'dpi': 200, 'quality': 80},
            'maximum': {'dpi': 300, 'quality': 95}
        }
        
        settings = quality_settings.get(quality, quality_settings['medium'])
        
        # Create compressed copy
        compressed = fitz.open()
        
        for page_num in range(len(self.document)):
            page = self.document[page_num]
            new_page = compressed.new_page(
                width=page.rect.width,
                height=page.rect.height
            )
            
            # Render page at lower resolution
            mat = fitz.Matrix(
                settings['dpi'] / 72,
                settings['dpi'] / 72
            )
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to image and compress
            img_data = pix.tobytes("jpeg", jpg_quality=settings['quality'])
            new_page.insert_image(new_page.rect, stream=img_data)
            
        compressed.save(output_path, garbage=4, deflate=True)
        compressed.close()
        
    def set_password(self, password: str, permissions: Dict[str, bool]):
        """Set password protection."""
        if self.pike_document:
            # Set encryption
            self.pike_document.save(
                self.file_path,
                encryption=pikepdf.Encryption(
                    owner=password,
                    user=password,
                    allow=pikepdf.Permissions(
                        print=permissions.get('print', True),
                        modify=permissions.get('modify', False),
                        copy=permissions.get('copy', True),
                        annotate=permissions.get('annotate', True),
                    )
                )
            )
            
    def remove_password(self, password: str):
        """Remove password protection."""
        if self.pike_document:
            self.pike_document.save(self.file_path)
            
    def add_watermark(self, text: str, page_num: Optional[int] = None,
                      font_size: float = 50,
                      color: Tuple[float, float, float] = (0.5, 0.5, 0.5),
                      opacity: float = 0.3,
                      rotation: float = 45):
        """Add watermark to page(s)."""
        self._save_state()
        
        pages = [self.pages[page_num]] if page_num is not None else self.pages
        
        for page in pages:
            # Calculate center position
            center_x = page.width / 2
            center_y = page.height / 2
            
            # Create watermark text
            page.fitz_page.insert_text(
                (center_x, center_y),
                text,
                fontsize=font_size,
                color=color,
                rotate=rotation,
                overlay=True
            )
            
    def add_header_footer(self, header: Optional[str] = None,
                          footer: Optional[str] = None,
                          font_size: float = 10,
                          page_numbers: bool = False):
        """Add header and/or footer to all pages."""
        self._save_state()
        
        for page_num, page in enumerate(self.pages):
            if header:
                page.fitz_page.insert_text(
                    (page.width / 2, 30),
                    header,
                    fontsize=font_size,
                    color=(0, 0, 0)
                )
                
            if footer:
                text = footer
                if page_numbers:
                    text += f" - Page {page_num + 1}"
                    
                page.fitz_page.insert_text(
                    (page.width / 2, page.height - 30),
                    text,
                    fontsize=font_size,
                    color=(0, 0, 0)
                )
                
    def extract_images(self, page_num: Optional[int] = None) -> List[Dict]:
        """Extract images from page(s)."""
        images = []
        
        pages = [self.pages[page_num]] if page_num is not None else self.pages
        
        for p_num, page in enumerate(pages):
            img_list = page.fitz_page.get_images()
            
            for img_index, img in enumerate(img_list, start=1):
                xref = img[0]
                base_image = self.document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                images.append({
                    'page': p_num,
                    'index': img_index,
                    'xref': xref,
                    'ext': image_ext,
                    'bytes': image_bytes,
                    'width': base_image.get('width'),
                    'height': base_image.get('height')
                })
                
        return images
        
    def get_links(self, page_num: int) -> List[Dict]:
        """Get all links on a page."""
        if 0 <= page_num < len(self.pages):
            page = self.pages[page_num]
            links = page.fitz_page.get_links()
            return links
        return []
        
    def add_link(self, page_num: int, rect: fitz.Rect, 
                 uri: Optional[str] = None,
                 target_page: Optional[int] = None):
        """Add a link to a page."""
        self._save_state()
        
        if 0 <= page_num < len(self.pages):
            page = self.pages[page_num]
            
            if uri:
                page.fitz_page.insert_link({
                    'kind': fitz.LINK_URI,
                    'from': rect,
                    'uri': uri
                })
            elif target_page is not None:
                page.fitz_page.insert_link({
                    'kind': fitz.LINK_GOTO,
                    'from': rect,
                    'page': target_page
                })
                
    def get_bookmarks(self) -> List[Dict]:
        """Get document bookmarks/outline."""
        if self.document:
            toc = self.document.get_toc()
            bookmarks = []
            for item in toc:
                bookmarks.append({
                    'level': item[0],
                    'title': item[1],
                    'page': item[2] - 1  # Convert to 0-based
                })
            return bookmarks
        return []
        
    def add_bookmark(self, title: str, page_num: int, 
                     parent: Optional[int] = None):
        """Add a bookmark."""
        self._save_state()
        
        if self.document:
            self.document.set_toc(
                self.document.get_toc() + [[1, title, page_num + 1]]
            )
            
    def set_metadata(self, metadata: PDFMetadata):
        """Set document metadata."""
        self._save_state()
        
        if self.document:
            self.document.set_metadata({
                'title': metadata.title,
                'author': metadata.author,
                'subject': metadata.subject,
                'keywords': metadata.keywords,
                'creator': metadata.creator,
                'producer': metadata.producer,
            })
            self.metadata = metadata
            
    def set_property(self, property_name: str, value: Any):
        """Set a document property."""
        if hasattr(self.metadata, property_name):
            setattr(self.metadata, property_name, value)
            self.set_metadata(self.metadata)
            
    def print_document(self, printer):
        """Print the document."""
        # This would integrate with Qt's print system
        pass
        
    def close(self):
        """Close the document and free resources."""
        if self.document:
            self.document.close()
            self.document = None
        if self.pike_document:
            self.pike_document.close()
            self.pike_document = None
        self.pages = []
        self.file_path = None
