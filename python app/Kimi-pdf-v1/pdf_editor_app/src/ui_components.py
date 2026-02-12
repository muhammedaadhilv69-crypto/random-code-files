"""
UI Components Module - Custom widgets for the PDF editor
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QSlider, QSpinBox, QDoubleSpinBox, QComboBox,
    QLineEdit, QTextEdit, QFrame, QSizePolicy, QGridLayout,
    QToolButton, QMenu, QInputDialog, QColorDialog, QFontDialog,
    QFileDialog, QMessageBox, QProgressDialog, QDialog,
    QDialogButtonBox, QFormLayout, QCheckBox, QGroupBox,
    QTabWidget, QListWidget, QListWidgetItem, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QRect, QPoint, QSize, QTimer,
    QPropertyAnimation, QEasingCurve, QThread
)
from PyQt6.QtGui import (
    QPixmap, QImage, QPainter, QPen, QBrush, QColor,
    QFont, QFontMetrics, QCursor, QKeyEvent, QMouseEvent,
    QWheelEvent, QPaintEvent, QResizeEvent, QTransform,
    QPolygon, QPolygonF, QIcon, QAction
)
import fitz


class PDFViewWidget(QWidget):
    """Main PDF viewing widget with annotation support."""
    
    page_changed = pyqtSignal(int)
    zoom_changed = pyqtSignal(float)
    annotation_created = pyqtSignal(object)
    text_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pdf_engine = None
        self.current_page = 0
        self.zoom = 1.0
        self.rotation = 0
        
        # Display
        self.page_pixmap = None
        self.rendered_pixmap = None
        
        # Interaction modes
        self.tool_mode = "select"  # select, pan, text_select, highlight, etc.
        self.is_panning = False
        self.is_drawing = False
        self.last_mouse_pos = QPoint()
        
        # Annotations
        self.annotations = []
        self.current_annotation = None
        self.drawing_points = []
        
        # Selection
        self.selection_rect = None
        self.selected_text = ""
        
        # Scroll offset
        self.scroll_offset = QPoint(0, 0)
        
        # Setup
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        
        # Timer for delayed rendering
        self.render_timer = QTimer()
        self.render_timer.setSingleShot(True)
        self.render_timer.timeout.connect(self.render_page)
        
    def set_document(self, pdf_engine):
        """Set the PDF document to display."""
        self.pdf_engine = pdf_engine
        self.current_page = 0
        self.scroll_offset = QPoint(0, 0)
        self.render_page()
        
    def goto_page(self, page_num: int):
        """Navigate to a specific page."""
        if self.pdf_engine and 0 <= page_num < self.pdf_engine.page_count:
            self.current_page = page_num
            self.scroll_offset = QPoint(0, 0)
            self.render_page()
            self.page_changed.emit(page_num)
            self.update()
            
    def set_zoom(self, zoom: float):
        """Set zoom level."""
        self.zoom = max(0.1, min(zoom, 5.0))
        self.render_page()
        self.zoom_changed.emit(self.zoom)
        self.update()
        
    def get_zoom(self) -> float:
        """Get current zoom level."""
        return self.zoom
        
    def fit_width(self):
        """Fit page to widget width."""
        if not self.pdf_engine or not self.pdf_engine.pages:
            return
            
        page = self.pdf_engine.get_page(self.current_page)
        if page:
            available_width = self.width() - 40
            self.zoom = available_width / page.width
            self.render_page()
            self.zoom_changed.emit(self.zoom)
            self.update()
            
    def fit_page(self):
        """Fit page to widget."""
        if not self.pdf_engine or not self.pdf_engine.pages:
            return
            
        page = self.pdf_engine.get_page(self.current_page)
        if page:
            zoom_x = (self.width() - 40) / page.width
            zoom_y = (self.height() - 40) / page.height
            self.zoom = min(zoom_x, zoom_y)
            self.render_page()
            self.zoom_changed.emit(self.zoom)
            self.update()
            
    def update_page(self):
        """Update the current page display."""
        self.render_page()
        self.update()
        
    def render_page(self):
        """Render the current page."""
        if not self.pdf_engine or not self.pdf_engine.pages:
            self.page_pixmap = None
            return
            
        page = self.pdf_engine.get_page(self.current_page)
        if not page:
            return
            
        # Get pixmap from page
        pix = page.get_pixmap(zoom=self.zoom, rotation=self.rotation)
        
        # Convert to QPixmap
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        self.page_pixmap = QPixmap.fromImage(img)
        
        # Create rendered pixmap with annotations
        self.update_rendered_pixmap()
        
    def update_rendered_pixmap(self):
        """Update the rendered pixmap with overlays."""
        if not self.page_pixmap:
            return
            
        self.rendered_pixmap = QPixmap(self.page_pixmap)
        painter = QPainter(self.rendered_pixmap)
        
        # Draw current annotation being created
        if self.is_drawing and self.drawing_points:
            self.draw_current_annotation(painter)
            
        # Draw selection rectangle
        if self.selection_rect:
            pen = QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)
            
        painter.end()
        
    def draw_current_annotation(self, painter: QPainter):
        """Draw the annotation currently being created."""
        if self.tool_mode == "highlight":
            pen = QPen(QColor(255, 255, 0, 128), 12)
            painter.setPen(pen)
            if len(self.drawing_points) > 1:
                painter.drawPolyline(QPolygon(self.drawing_points))
                
        elif self.tool_mode == "underline":
            pen = QPen(QColor(0, 0, 255), 2)
            painter.setPen(pen)
            if len(self.drawing_points) > 1:
                painter.drawPolyline(QPolygon(self.drawing_points))
                
        elif self.tool_mode == "freehand":
            pen = QPen(QColor(0, 0, 0), 2)
            painter.setPen(pen)
            if len(self.drawing_points) > 1:
                painter.drawPolyline(QPolygon(self.drawing_points))
                
        elif self.tool_mode == "rectangle":
            if len(self.drawing_points) >= 2:
                rect = QRect(self.drawing_points[0], self.drawing_points[-1]).normalized()
                pen = QPen(QColor(255, 0, 0), 2)
                painter.setPen(pen)
                painter.drawRect(rect)
                
    def set_annotation_tool(self, tool: str, **kwargs):
        """Set the current annotation tool."""
        self.tool_mode = tool
        self.setCursor(self.get_cursor_for_tool(tool))
        
    def get_cursor_for_tool(self, tool: str) -> QCursor:
        """Get cursor for a tool."""
        cursors = {
            "select": Qt.CursorShape.ArrowCursor,
            "pan": Qt.CursorShape.OpenHandCursor,
            "text_select": Qt.CursorShape.IBeamCursor,
            "highlight": Qt.CursorShape.CrossCursor,
            "underline": Qt.CursorShape.CrossCursor,
            "strikethrough": Qt.CursorShape.CrossCursor,
            "freehand": Qt.CursorShape.CrossCursor,
            "rectangle": Qt.CursorShape.CrossCursor,
            "circle": Qt.CursorShape.CrossCursor,
            "line": Qt.CursorShape.CrossCursor,
            "text": Qt.CursorShape.IBeamCursor,
            "note": Qt.CursorShape.PointingHandCursor,
            "stamp": Qt.CursorShape.CrossCursor,
        }
        return QCursor(cursors.get(tool, Qt.CursorShape.ArrowCursor))
        
    def set_signature_mode(self, signature_image: bytes):
        """Enable signature placement mode."""
        self.tool_mode = "signature"
        self.signature_image = signature_image
        self.setCursor(Qt.CursorShape.CrossCursor)
        
    def set_form_field_mode(self, field_type: str):
        """Enable form field placement mode."""
        self.tool_mode = f"form_{field_type}"
        self.setCursor(Qt.CursorShape.CrossCursor)
        
    def set_form_fill_mode(self, enabled: bool):
        """Enable/disable form fill mode."""
        self.tool_mode = "form_fill" if enabled else "select"
        
    def select_annotation(self, annotation_id: str):
        """Select an annotation."""
        # Find and highlight the annotation
        pass
        
    def cut(self):
        """Cut selected content."""
        self.copy()
        # Remove selected content
        
    def copy(self):
        """Copy selected content."""
        if self.selected_text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(self.selected_text)
            
    def paste(self):
        """Paste content."""
        from PyQt6.QtWidgets import QApplication
        text = QApplication.clipboard().text()
        if text and self.pdf_engine:
            # Insert text at current position
            pass
            
    def select_all(self):
        """Select all content on page."""
        if self.pdf_engine:
            page = self.pdf_engine.get_page(self.current_page)
            if page:
                # Select all text
                pass
                
    # ==================== Event Handlers ====================
    
    def paintEvent(self, event: QPaintEvent):
        """Paint the widget."""
        painter = QPainter(self)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(60, 63, 65))
        
        if self.rendered_pixmap:
            # Center the page
            x = (self.width() - self.rendered_pixmap.width()) // 2 + self.scroll_offset.x()
            y = (self.height() - self.rendered_pixmap.height()) // 2 + self.scroll_offset.y()
            
            # Draw shadow
            shadow_rect = QRect(x + 3, y + 3, 
                              self.rendered_pixmap.width(), 
                              self.rendered_pixmap.height())
            painter.fillRect(shadow_rect, QColor(0, 0, 0, 64))
            
            # Draw page
            painter.drawPixmap(x, y, self.rendered_pixmap)
        else:
            # Draw placeholder
            painter.setPen(QPen(QColor(128, 128, 128)))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 
                           "No PDF loaded\nOpen a PDF file to view")
            
        painter.end()
        
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize."""
        super().resizeEvent(event)
        self.render_timer.start(100)  # Delayed render
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press."""
        if not self.pdf_engine:
            return
            
        self.last_mouse_pos = event.pos()
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool_mode == "pan":
                self.is_panning = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                
            elif self.tool_mode in ["highlight", "underline", "strikethrough", 
                                   "freehand", "rectangle", "circle", "line"]:
                self.is_drawing = True
                self.drawing_points = [event.pos()]
                
            elif self.tool_mode == "select":
                # Start selection
                self.selection_rect = QRect(event.pos(), event.pos())
                
            elif self.tool_mode == "text_select":
                # Start text selection
                pass
                
            elif self.tool_mode == "signature":
                # Place signature
                self.place_signature(event.pos())
                
            elif self.tool_mode.startswith("form_"):
                # Place form field
                self.place_form_field(event.pos())
                
        self.update()
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move."""
        if not self.pdf_engine:
            return
            
        if self.is_panning:
            delta = event.pos() - self.last_mouse_pos
            self.scroll_offset += delta
            self.last_mouse_pos = event.pos()
            self.update()
            
        elif self.is_drawing:
            self.drawing_points.append(event.pos())
            self.update_rendered_pixmap()
            self.update()
            
        elif self.selection_rect:
            self.selection_rect.setBottomRight(event.pos())
            self.update()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if not self.pdf_engine:
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_panning:
                self.is_panning = False
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                
            elif self.is_drawing:
                self.is_drawing = False
                self.finish_annotation()
                
            elif self.selection_rect:
                self.finish_selection()
                
        self.update()
        
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom
            delta = event.angleDelta().y()
            if delta > 0:
                self.set_zoom(self.zoom * 1.1)
            else:
                self.set_zoom(self.zoom / 1.1)
        else:
            # Scroll
            delta = event.angleDelta().y()
            self.scroll_offset.setY(self.scroll_offset.y() + delta)
            self.update()
            
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press."""
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_operation()
        else:
            super().keyPressEvent(event)
            
    def cancel_operation(self):
        """Cancel current operation."""
        self.is_drawing = False
        self.is_panning = False
        self.drawing_points = []
        self.selection_rect = None
        self.tool_mode = "select"
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        
    def finish_annotation(self):
        """Finish creating an annotation."""
        if not self.drawing_points:
            return
            
        # Convert screen coordinates to PDF coordinates
        pdf_points = [self.screen_to_pdf(p) for p in self.drawing_points]
        
        # Create annotation based on tool mode
        annotation = {
            'type': self.tool_mode,
            'page': self.current_page,
            'points': pdf_points,
        }
        
        self.annotation_created.emit(annotation)
        self.drawing_points = []
        
    def finish_selection(self):
        """Finish text selection."""
        if self.selection_rect:
            # Extract text from selection
            pdf_rect = self.screen_rect_to_pdf(self.selection_rect)
            
            page = self.pdf_engine.get_page(self.current_page)
            if page:
                # Get text in rectangle
                self.selected_text = page.fitz_page.get_textbox(pdf_rect)
                self.text_selected.emit(self.selected_text)
                
        self.selection_rect = None
        
    def place_signature(self, pos: QPoint):
        """Place a signature at the given position."""
        # Convert to PDF coordinates
        pdf_pos = self.screen_to_pdf(pos)
        
        # Create signature annotation
        annotation = {
            'type': 'signature',
            'page': self.current_page,
            'position': pdf_pos,
            'image': getattr(self, 'signature_image', None)
        }
        
        self.annotation_created.emit(annotation)
        self.tool_mode = "select"
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
    def place_form_field(self, pos: QPoint):
        """Place a form field at the given position."""
        pdf_pos = self.screen_to_pdf(pos)
        
        field_type = self.tool_mode.replace("form_", "")
        
        annotation = {
            'type': 'form_field',
            'field_type': field_type,
            'page': self.current_page,
            'position': pdf_pos,
        }
        
        self.annotation_created.emit(annotation)
        self.tool_mode = "select"
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
    def screen_to_pdf(self, point: QPoint) -> fitz.Point:
        """Convert screen coordinates to PDF coordinates."""
        if not self.page_pixmap:
            return fitz.Point(0, 0)
            
        x = (point.x() - (self.width() - self.page_pixmap.width()) // 2 - self.scroll_offset.x()) / self.zoom
        y = (point.y() - (self.height() - self.page_pixmap.height()) // 2 - self.scroll_offset.y()) / self.zoom
        
        return fitz.Point(x, y)
        
    def screen_rect_to_pdf(self, rect: QRect) -> fitz.Rect:
        """Convert screen rectangle to PDF rectangle."""
        tl = self.screen_to_pdf(rect.topLeft())
        br = self.screen_to_pdf(rect.bottomRight())
        return fitz.Rect(tl, br)


class ThumbnailPanel(QWidget):
    """Panel displaying page thumbnails."""
    
    page_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pdf_engine = None
        self.thumbnails = []
        self.selected_page = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for thumbnails
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.scroll)
        
        # Container widget
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(10)
        self.scroll.setWidget(self.container)
        
    def set_document(self, pdf_engine):
        """Set the PDF document."""
        self.pdf_engine = pdf_engine
        self.update_thumbnails()
        
    def update_thumbnails(self):
        """Update thumbnail display."""
        # Clear existing thumbnails
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.thumbnails = []
        
        if not self.pdf_engine:
            return
            
        # Generate thumbnails
        for i in range(self.pdf_engine.page_count):
            thumb_widget = ThumbnailItem(i, self.pdf_engine)
            thumb_widget.clicked.connect(self.on_thumbnail_clicked)
            self.container_layout.addWidget(thumb_widget)
            self.thumbnails.append(thumb_widget)
            
        self.container_layout.addStretch()
        
    def on_thumbnail_clicked(self, page_num: int):
        """Handle thumbnail click."""
        self.selected_page = page_num
        self.page_selected.emit(page_num)
        
        # Update selection
        for thumb in self.thumbnails:
            thumb.set_selected(thumb.page_num == page_num)
            
    def set_current_page(self, page_num: int):
        """Set the current page."""
        self.selected_page = page_num
        for thumb in self.thumbnails:
            thumb.set_selected(thumb.page_num == page_num)


class ThumbnailItem(QFrame):
    """Single thumbnail item."""
    
    clicked = pyqtSignal(int)
    
    def __init__(self, page_num: int, pdf_engine, parent=None):
        super().__init__(parent)
        
        self.page_num = page_num
        self.pdf_engine = pdf_engine
        
        self.setFixedSize(160, 200)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Thumbnail image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(140, 160)
        layout.addWidget(self.image_label)
        
        # Page number
        self.num_label = QLabel(f"Page {page_num + 1}")
        self.num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.num_label)
        
        # Generate thumbnail
        self.generate_thumbnail()
        
    def generate_thumbnail(self):
        """Generate thumbnail image."""
        page = self.pdf_engine.get_page(self.page_num)
        if not page:
            return
            
        # Render at thumbnail size
        zoom = 140 / page.width
        pix = page.get_pixmap(zoom=zoom)
        
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        
        self.image_label.setPixmap(pixmap)
        
    def set_selected(self, selected: bool):
        """Set selection state."""
        if selected:
            self.setStyleSheet("background-color: #4b6eaf;")
        else:
            self.setStyleSheet("background-color: transparent;")
            
    def mousePressEvent(self, event):
        """Handle mouse press."""
        self.clicked.emit(self.page_num)


class AnnotationToolbar(QToolBar):
    """Toolbar for annotation tools."""
    
    tool_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Annotations", parent)
        
        self.setup_tools()
        
    def setup_tools(self):
        """Setup annotation tools."""
        self.setOrientation(Qt.Orientation.Vertical)
        
        # Selection tool
        self.add_tool("select", "Select", "arrow")
        self.addSeparator()
        
        # Text annotations
        self.add_tool("highlight", "Highlight", "highlight")
        self.add_tool("underline", "Underline", "underline")
        self.add_tool("strikethrough", "Strikethrough", "strikethrough")
        self.addSeparator()
        
        # Drawing tools
        self.add_tool("freehand", "Freehand", "pen")
        self.add_tool("line", "Line", "line")
        self.add_tool("rectangle", "Rectangle", "rect")
        self.add_tool("circle", "Circle", "circle")
        self.addSeparator()
        
        # Text tools
        self.add_tool("text", "Text", "text")
        self.add_tool("note", "Note", "note")
        self.addSeparator()
        
        # Stamp
        self.add_tool("stamp", "Stamp", "stamp")
        
    def add_tool(self, tool_id: str, tooltip: str, icon_name: str):
        """Add a tool button."""
        btn = QToolButton()
        btn.setText(tooltip[0])  # First letter as icon
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setFixedSize(32, 32)
        btn.clicked.connect(lambda: self.on_tool_clicked(tool_id, btn))
        self.addWidget(btn)
        
    def on_tool_clicked(self, tool_id: str, btn):
        """Handle tool selection."""
        # Uncheck other buttons
        for child in self.findChildren(QToolButton):
            if child != btn:
                child.setChecked(False)
                
        self.tool_selected.emit(tool_id)


class PropertiesPanel(QWidget):
    """Panel for editing properties."""
    
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Document properties
        doc_group = QGroupBox("Document Properties")
        doc_layout = QFormLayout(doc_group)
        
        self.title_edit = QLineEdit()
        self.title_edit.editingFinished.connect(
            lambda: self.property_changed.emit('title', self.title_edit.text()))
        doc_layout.addRow("Title:", self.title_edit)
        
        self.author_edit = QLineEdit()
        self.author_edit.editingFinished.connect(
            lambda: self.property_changed.emit('author', self.author_edit.text()))
        doc_layout.addRow("Author:", self.author_edit)
        
        self.subject_edit = QLineEdit()
        self.subject_edit.editingFinished.connect(
            lambda: self.property_changed.emit('subject', self.subject_edit.text()))
        doc_layout.addRow("Subject:", self.subject_edit)
        
        layout.addWidget(doc_group)
        
        # Page properties
        page_group = QGroupBox("Page Properties")
        page_layout = QFormLayout(page_group)
        
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A4", "Letter", "Legal", "Custom"])
        page_layout.addRow("Page Size:", self.page_size_combo)
        
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 360)
        self.rotation_spin.setSingleStep(90)
        page_layout.addRow("Rotation:", self.rotation_spin)
        
        layout.addWidget(page_group)
        
        # Annotation properties
        annot_group = QGroupBox("Annotation Properties")
        annot_layout = QFormLayout(annot_group)
        
        self.color_btn = QPushButton("Select Color")
        self.color_btn.clicked.connect(self.select_color)
        annot_layout.addRow("Color:", self.color_btn)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        annot_layout.addRow("Opacity:", self.opacity_slider)
        
        self.line_width_spin = QDoubleSpinBox()
        self.line_width_spin.setRange(0.1, 10)
        self.line_width_spin.setValue(1)
        annot_layout.addRow("Line Width:", self.line_width_spin)
        
        layout.addWidget(annot_group)
        
        layout.addStretch()
        
    def select_color(self):
        """Open color picker."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.property_changed.emit('color', color)
            
    def set_document_properties(self, metadata):
        """Set document properties in the panel."""
        self.title_edit.setText(metadata.title)
        self.author_edit.setText(metadata.author)
        self.subject_edit.setText(metadata.subject)


class PageNavigator(QWidget):
    """Page navigation widget."""
    
    page_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.page_count = 0
        self.current_page = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Previous button
        self.prev_btn = QPushButton("<")
        self.prev_btn.setFixedSize(30, 30)
        self.prev_btn.clicked.connect(self.go_previous)
        layout.addWidget(self.prev_btn)
        
        # Page input
        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 1)
        self.page_spin.setFixedWidth(60)
        self.page_spin.valueChanged.connect(self.on_page_changed)
        layout.addWidget(self.page_spin)
        
        # Page count label
        self.count_label = QLabel("/ 1")
        layout.addWidget(self.count_label)
        
        # Next button
        self.next_btn = QPushButton(">")
        self.next_btn.setFixedSize(30, 30)
        self.next_btn.clicked.connect(self.go_next)
        layout.addWidget(self.next_btn)
        
        layout.addStretch()
        
    def set_page_count(self, count: int):
        """Set the total page count."""
        self.page_count = count
        self.page_spin.setRange(1, max(1, count))
        self.count_label.setText(f"/ {count}")
        
    def set_current_page(self, page: int):
        """Set the current page."""
        self.current_page = page
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(page + 1)
        self.page_spin.blockSignals(False)
        
        # Update button states
        self.prev_btn.setEnabled(page > 0)
        self.next_btn.setEnabled(page < self.page_count - 1)
        
    def on_page_changed(self, value: int):
        """Handle page spin box change."""
        self.page_changed.emit(value - 1)
        
    def go_previous(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.page_changed.emit(self.current_page - 1)
            
    def go_next(self):
        """Go to next page."""
        if self.current_page < self.page_count - 1:
            self.page_changed.emit(self.current_page + 1)


class SearchDialog(QDialog):
    """Search dialog."""
    
    def __init__(self, pdf_engine, parent=None):
        super().__init__(parent)
        
        self.pdf_engine = pdf_engine
        self.results = []
        self.current_result = 0
        
        self.setWindowTitle("Find")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        self.search_input.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Find")
        self.search_btn.clicked.connect(self.search)
        search_layout.addWidget(self.search_btn)
        
        layout.addLayout(search_layout)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.case_check = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_check)
        
        self.whole_word_check = QCheckBox("Whole words")
        options_layout.addWidget(self.whole_word_check)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.goto_result)
        layout.addWidget(self.results_list)
        
        # Navigation
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.previous_result)
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_result)
        nav_layout.addWidget(self.next_btn)
        
        nav_layout.addStretch()
        
        self.status_label = QLabel("")
        nav_layout.addWidget(self.status_label)
        
        layout.addLayout(nav_layout)
        
        # Close button
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def search(self):
        """Perform search."""
        text = self.search_input.text()
        if not text:
            return
            
        case_sensitive = self.case_check.isChecked()
        whole_words = self.whole_word_check.isChecked()
        
        self.results = self.pdf_engine.search(text, case_sensitive, whole_words)
        
        # Update results list
        self.results_list.clear()
        for result in self.results:
            item = QListWidgetItem(
                f"Page {result['page'] + 1}: {text[:50]}"
            )
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)
            
        self.status_label.setText(f"{len(self.results)} results found")
        self.current_result = 0
        
    def goto_result(self, item):
        """Go to selected result."""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result and self.parent():
            self.parent().goto_page(result['page'])
            
    def previous_result(self):
        """Go to previous result."""
        if self.results and self.current_result > 0:
            self.current_result -= 1
            self.results_list.setCurrentRow(self.current_result)
            self.goto_result(self.results_list.currentItem())
            
    def next_result(self):
        """Go to next result."""
        if self.results and self.current_result < len(self.results) - 1:
            self.current_result += 1
            self.results_list.setCurrentRow(self.current_result)
            self.goto_result(self.results_list.currentItem())
