"""
Annotation System Module - Handles PDF annotations
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import uuid
from datetime import datetime
import fitz


class AnnotationType(Enum):
    """Types of annotations supported."""
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    SQUIGGLY = "squiggly"
    TEXT = "text"  # Sticky note
    FREETEXT = "freetext"  # Free text on page
    INK = "ink"  # Freehand drawing
    SQUARE = "square"
    CIRCLE = "circle"
    LINE = "line"
    POLYGON = "polygon"
    POLYLINE = "polyline"
    STAMP = "stamp"
    CARET = "caret"
    FILEATTACHMENT = "fileattachment"
    SOUND = "sound"
    MOVIE = "movie"
    WIDGET = "widget"
    SCREEN = "screen"
    PRINTERMARK = "printermark"
    TRAPNET = "trapnet"
    WATERMARK = "watermark"
    THREED = "3d"
    REDACT = "redact"


@dataclass
class Annotation:
    """Represents a single annotation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: AnnotationType = AnnotationType.HIGHLIGHT
    page: int = 0
    rect: Optional[fitz.Rect] = None
    text: str = ""
    author: str = ""
    creation_date: datetime = field(default_factory=datetime.now)
    modification_date: datetime = field(default_factory=datetime.now)
    color: Tuple[float, float, float] = (1, 1, 0)  # RGB
    opacity: float = 1.0
    border_width: float = 1.0
    border_style: str = "solid"
    points: List[Tuple[float, float]] = field(default_factory=list)
    contents: str = ""  # Popup content
    subject: str = ""
    icon: str = ""
    flags: int = 0
    
    # Additional properties for specific annotation types
    font_size: float = 12.0
    font_name: str = "Helvetica"
    alignment: int = 0  # 0=left, 1=center, 2=right
    
    # For ink annotations
    ink_list: List[List[Tuple[float, float]]] = field(default_factory=list)
    
    # For stamp annotations
    stamp_text: str = ""
    stamp_image: Optional[bytes] = None
    
    # Internal reference to fitz annotation
    _fitz_annot: Optional[Any] = field(default=None, repr=False)
    
    def to_dict(self) -> Dict:
        """Convert annotation to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'page': self.page,
            'rect': [self.rect.x0, self.rect.y0, self.rect.x1, self.rect.y1] if self.rect else None,
            'text': self.text,
            'author': self.author,
            'creation_date': self.creation_date.isoformat(),
            'modification_date': self.modification_date.isoformat(),
            'color': self.color,
            'opacity': self.opacity,
            'border_width': self.border_width,
            'border_style': self.border_style,
            'points': self.points,
            'contents': self.contents,
            'subject': self.subject,
            'icon': self.icon,
            'flags': self.flags,
            'font_size': self.font_size,
            'font_name': self.font_name,
            'alignment': self.alignment,
            'ink_list': self.ink_list,
            'stamp_text': self.stamp_text,
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Annotation':
        """Create annotation from dictionary."""
        annot = cls()
        annot.id = data.get('id', str(uuid.uuid4()))
        annot.type = AnnotationType(data.get('type', 'highlight'))
        annot.page = data.get('page', 0)
        
        rect_data = data.get('rect')
        if rect_data:
            annot.rect = fitz.Rect(rect_data)
            
        annot.text = data.get('text', '')
        annot.author = data.get('author', '')
        annot.creation_date = datetime.fromisoformat(data.get('creation_date', datetime.now().isoformat()))
        annot.modification_date = datetime.fromisoformat(data.get('modification_date', datetime.now().isoformat()))
        annot.color = tuple(data.get('color', [1, 1, 0]))
        annot.opacity = data.get('opacity', 1.0)
        annot.border_width = data.get('border_width', 1.0)
        annot.border_style = data.get('border_style', 'solid')
        annot.points = data.get('points', [])
        annot.contents = data.get('contents', '')
        annot.subject = data.get('subject', '')
        annot.icon = data.get('icon', '')
        annot.flags = data.get('flags', 0)
        annot.font_size = data.get('font_size', 12.0)
        annot.font_name = data.get('font_name', 'Helvetica')
        annot.alignment = data.get('alignment', 0)
        annot.ink_list = data.get('ink_list', [])
        annot.stamp_text = data.get('stamp_text', '')
        
        return annot


class AnnotationManager:
    """Manages annotations for a PDF document."""
    
    def __init__(self):
        self.annotations: List[Annotation] = []
        self.selected_annotation: Optional[Annotation] = None
        self._undo_stack: List[List[Annotation]] = []
        self._redo_stack: List[List[Annotation]] = []
        self._max_undo = 50
        
    def add_annotation(self, annotation: Annotation) -> Annotation:
        """Add a new annotation."""
        self._save_state()
        self.annotations.append(annotation)
        return annotation
        
    def remove_annotation(self, annotation_id: str) -> bool:
        """Remove an annotation by ID."""
        self._save_state()
        
        for i, annot in enumerate(self.annotations):
            if annot.id == annotation_id:
                self.annotations.pop(i)
                return True
        return False
        
    def update_annotation(self, annotation_id: str, 
                          updates: Dict[str, Any]) -> bool:
        """Update an annotation's properties."""
        self._save_state()
        
        for annot in self.annotations:
            if annot.id == annotation_id:
                for key, value in updates.items():
                    if hasattr(annot, key):
                        setattr(annot, key, value)
                annot.modification_date = datetime.now()
                return True
        return False
        
    def get_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """Get an annotation by ID."""
        for annot in self.annotations:
            if annot.id == annotation_id:
                return annot
        return None
        
    def get_annotations_for_page(self, page_num: int) -> List[Annotation]:
        """Get all annotations for a specific page."""
        return [a for a in self.annotations if a.page == page_num]
        
    def get_annotations(self) -> List[Annotation]:
        """Get all annotations."""
        return self.annotations.copy()
        
    def select_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """Select an annotation."""
        self.selected_annotation = self.get_annotation(annotation_id)
        return self.selected_annotation
        
    def clear_selection(self):
        """Clear the current selection."""
        self.selected_annotation = None
        
    def _save_state(self):
        """Save current state for undo."""
        import copy
        state = copy.deepcopy(self.annotations)
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
            import copy
            self._redo_stack.append(copy.deepcopy(self.annotations))
            self.annotations = self._undo_stack.pop()
            
    def redo(self):
        """Redo last undone operation."""
        if self.can_redo():
            import copy
            self._undo_stack.append(copy.deepcopy(self.annotations))
            self.annotations = self._redo_stack.pop()
            
    def clear(self):
        """Clear all annotations."""
        self._save_state()
        self.annotations.clear()
        self.selected_annotation = None
        
    def import_from_pdf(self, pdf_engine):
        """Import annotations from a loaded PDF."""
        self.annotations.clear()
        
        for page_num in range(pdf_engine.page_count):
            page = pdf_engine.get_page(page_num)
            if page:
                fitz_page = page.fitz_page
                
                for fitz_annot in fitz_page.annots():
                    annot = self._convert_fitz_annot(fitz_annot, page_num)
                    if annot:
                        annot._fitz_annot = fitz_annot
                        self.annotations.append(annot)
                        
    def _convert_fitz_annot(self, fitz_annot, page_num: int) -> Optional[Annotation]:
        """Convert a fitz annotation to our Annotation class."""
        annot_type = fitz_annot.type[1]  # Get type name
        
        type_mapping = {
            'Highlight': AnnotationType.HIGHLIGHT,
            'Underline': AnnotationType.UNDERLINE,
            'StrikeOut': AnnotationType.STRIKETHROUGH,
            'Squiggly': AnnotationType.SQUIGGLY,
            'Text': AnnotationType.TEXT,
            'FreeText': AnnotationType.FREETEXT,
            'Ink': AnnotationType.INK,
            'Square': AnnotationType.SQUARE,
            'Circle': AnnotationType.CIRCLE,
            'Line': AnnotationType.LINE,
            'Polygon': AnnotationType.POLYGON,
            'PolyLine': AnnotationType.POLYLINE,
            'Stamp': AnnotationType.STAMP,
            'Caret': AnnotationType.CARET,
            'FileAttachment': AnnotationType.FILEATTACHMENT,
            'Sound': AnnotationType.SOUND,
            'Movie': AnnotationType.MOVIE,
            'Widget': AnnotationType.WIDGET,
            'Screen': AnnotationType.SCREEN,
            'PrinterMark': AnnotationType.PRINTERMARK,
            'TrapNet': AnnotationType.TRAPNET,
            'Watermark': AnnotationType.WATERMARK,
            '3D': AnnotationType.THREED,
            'Redact': AnnotationType.REDACT,
        }
        
        annot = Annotation()
        annot.type = type_mapping.get(annot_type, AnnotationType.HIGHLIGHT)
        annot.page = page_num
        annot.rect = fitz_annot.rect
        
        # Get colors
        colors = fitz_annot.colors
        if colors and colors.get('stroke'):
            annot.color = colors['stroke']
        elif colors and colors.get('fill'):
            annot.color = colors['fill']
            
        # Get other properties
        annot.opacity = fitz_annot.opacity
        annot.border_width = fitz_annot.border.get('width', 1.0) if fitz_annot.border else 1.0
        annot.text = fitz_annot.info.get('content', '')
        annot.author = fitz_annot.info.get('title', '')
        annot.subject = fitz_annot.info.get('subject', '')
        annot.creation_date = fitz_annot.info.get('creationDate', datetime.now())
        annot.modification_date = fitz_annot.info.get('modDate', datetime.now())
        
        # Get vertices for ink/polygon annotations
        if annot.type in [AnnotationType.INK, AnnotationType.POLYGON, AnnotationType.POLYLINE]:
            vertices = fitz_annot.vertices
            if vertices:
                annot.points = [(v.x, v.y) for v in vertices]
                
        # Get text content for freetext
        if annot.type == AnnotationType.FREETEXT:
            annot.text = fitz_annot.get_text()
            
        return annot
        
    def export_to_pdf(self, pdf_engine):
        """Export annotations to the PDF document."""
        for annot in self.annotations:
            self._apply_annotation(pdf_engine, annot)
            
    def _apply_annotation(self, pdf_engine, annot: Annotation):
        """Apply a single annotation to the PDF."""
        page = pdf_engine.get_page(annot.page)
        if not page:
            return
            
        fitz_page = page.fitz_page
        
        if annot.type == AnnotationType.HIGHLIGHT:
            if annot.rect:
                new_annot = fitz_page.add_highlight_annot(annot.rect)
                new_annot.set_colors(stroke=annot.color)
                new_annot.set_opacity(annot.opacity)
                new_annot.update()
                
        elif annot.type == AnnotationType.UNDERLINE:
            if annot.rect:
                new_annot = fitz_page.add_underline_annot(annot.rect)
                new_annot.set_colors(stroke=annot.color)
                new_annot.set_opacity(annot.opacity)
                new_annot.update()
                
        elif annot.type == AnnotationType.STRIKETHROUGH:
            if annot.rect:
                new_annot = fitz_page.add_strikeout_annot(annot.rect)
                new_annot.set_colors(stroke=annot.color)
                new_annot.set_opacity(annot.opacity)
                new_annot.update()
                
        elif annot.type == AnnotationType.SQUIGGLY:
            if annot.rect:
                new_annot = fitz_page.add_squiggly_annot(annot.rect)
                new_annot.set_colors(stroke=annot.color)
                new_annot.set_opacity(annot.opacity)
                new_annot.update()
                
        elif annot.type == AnnotationType.TEXT:
            if annot.rect:
                new_annot = fitz_page.add_text_annot(
                    annot.rect.tl,
                    annot.contents or annot.text,
                    icon=annot.icon or "Note"
                )
                new_annot.update()
                
        elif annot.type == AnnotationType.FREETEXT:
            if annot.rect:
                new_annot = fitz_page.add_freetext_annot(
                    annot.rect,
                    annot.text,
                    fontsize=annot.font_size,
                    fontname=annot.font_name
                )
                new_annot.update()
                
        elif annot.type == AnnotationType.INK:
            if annot.ink_list:
                new_annot = fitz_page.add_ink_annot(annot.ink_list)
                new_annot.set_colors(stroke=annot.color)
                new_annot.set_border(width=annot.border_width)
                new_annot.set_opacity(annot.opacity)
                new_annot.update()
                
        elif annot.type == AnnotationType.SQUARE:
            if annot.rect:
                new_annot = fitz_page.add_rect_annot(annot.rect)
                new_annot.set_colors(stroke=annot.color)
                new_annot.set_border(width=annot.border_width)
                new_annot.set_opacity(annot.opacity)
                new_annot.update()
                
        elif annot.type == AnnotationType.CIRCLE:
            if annot.rect:
                new_annot = fitz_page.add_circle_annot(annot.rect)
                new_annot.set_colors(stroke=annot.color)
                new_annot.set_border(width=annot.border_width)
                new_annot.set_opacity(annot.opacity)
                new_annot.update()
                
        elif annot.type == AnnotationType.LINE:
            if len(annot.points) >= 2:
                new_annot = fitz_page.add_line_annot(
                    annot.points[0],
                    annot.points[1]
                )
                new_annot.set_colors(stroke=annot.color)
                new_annot.set_border(width=annot.border_width)
                new_annot.set_opacity(annot.opacity)
                new_annot.update()
                
        elif annot.type == AnnotationType.STAMP:
            if annot.rect:
                new_annot = fitz_page.add_stamp_annot(
                    annot.rect,
                    stamp=annot.stamp_text or "Approved"
                )
                new_annot.update()
                
    def create_highlight(self, page: int, rect: fitz.Rect,
                         color: Tuple[float, float, float] = (1, 1, 0),
                         text: str = "") -> Annotation:
        """Create a highlight annotation."""
        annot = Annotation(
            type=AnnotationType.HIGHLIGHT,
            page=page,
            rect=rect,
            color=color,
            text=text
        )
        return self.add_annotation(annot)
        
    def create_underline(self, page: int, rect: fitz.Rect,
                         color: Tuple[float, float, float] = (0, 0, 1),
                         text: str = "") -> Annotation:
        """Create an underline annotation."""
        annot = Annotation(
            type=AnnotationType.UNDERLINE,
            page=page,
            rect=rect,
            color=color,
            text=text
        )
        return self.add_annotation(annot)
        
    def create_strikethrough(self, page: int, rect: fitz.Rect,
                             color: Tuple[float, float, float] = (1, 0, 0),
                             text: str = "") -> Annotation:
        """Create a strikethrough annotation."""
        annot = Annotation(
            type=AnnotationType.STRIKETHROUGH,
            page=page,
            rect=rect,
            color=color,
            text=text
        )
        return self.add_annotation(annot)
        
    def create_text_note(self, page: int, point: Tuple[float, float],
                         text: str = "", icon: str = "Note") -> Annotation:
        """Create a text note annotation."""
        rect = fitz.Rect(point[0], point[1], point[0] + 20, point[1] + 20)
        annot = Annotation(
            type=AnnotationType.TEXT,
            page=page,
            rect=rect,
            contents=text,
            icon=icon
        )
        return self.add_annotation(annot)
        
    def create_freetext(self, page: int, rect: fitz.Rect, text: str,
                        font_size: float = 12,
                        color: Tuple[float, float, float] = (0, 0, 0)) -> Annotation:
        """Create a free text annotation."""
        annot = Annotation(
            type=AnnotationType.FREETEXT,
            page=page,
            rect=rect,
            text=text,
            font_size=font_size,
            color=color
        )
        return self.add_annotation(annot)
        
    def create_ink(self, page: int, points: List[List[Tuple[float, float]]],
                   color: Tuple[float, float, float] = (0, 0, 0),
                   width: float = 1.0) -> Annotation:
        """Create an ink (freehand) annotation."""
        annot = Annotation(
            type=AnnotationType.INK,
            page=page,
            ink_list=points,
            color=color,
            border_width=width
        )
        return self.add_annotation(annot)
        
    def create_stamp(self, page: int, rect: fitz.Rect,
                     stamp_text: str = "APPROVED") -> Annotation:
        """Create a stamp annotation."""
        annot = Annotation(
            type=AnnotationType.STAMP,
            page=page,
            rect=rect,
            stamp_text=stamp_text
        )
        return self.add_annotation(annot)
        
    def create_line(self, page: int, p1: Tuple[float, float],
                    p2: Tuple[float, float],
                    color: Tuple[float, float, float] = (0, 0, 0),
                    width: float = 1.0) -> Annotation:
        """Create a line annotation."""
        annot = Annotation(
            type=AnnotationType.LINE,
            page=page,
            points=[p1, p2],
            color=color,
            border_width=width
        )
        return self.add_annotation(annot)
        
    def create_rectangle(self, page: int, rect: fitz.Rect,
                         color: Tuple[float, float, float] = (0, 0, 0),
                         fill: Optional[Tuple[float, float, float]] = None,
                         width: float = 1.0) -> Annotation:
        """Create a rectangle annotation."""
        annot = Annotation(
            type=AnnotationType.SQUARE,
            page=page,
            rect=rect,
            color=color,
            border_width=width
        )
        return self.add_annotation(annot)
        
    def create_circle(self, page: int, rect: fitz.Rect,
                      color: Tuple[float, float, float] = (0, 0, 0),
                      fill: Optional[Tuple[float, float, float]] = None,
                      width: float = 1.0) -> Annotation:
        """Create a circle annotation."""
        annot = Annotation(
            type=AnnotationType.CIRCLE,
            page=page,
            rect=rect,
            color=color,
            border_width=width
        )
        return self.add_annotation(annot)
        
    def save_to_file(self, file_path: str):
        """Save annotations to a JSON file."""
        import json
        data = [annot.to_dict() for annot in self.annotations]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    def load_from_file(self, file_path: str):
        """Load annotations from a JSON file."""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.annotations = [Annotation.from_dict(d) for d in data]
