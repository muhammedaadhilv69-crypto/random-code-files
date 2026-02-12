#!/usr/bin/env python3
"""
ProPDF Editor - Professional PDF Viewer and Editor
A production-ready PDF application with annotation, signing, and editing capabilities.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QFileDialog, QMessageBox, QLabel, QScrollArea,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QDockWidget, QMenuBar, QMenu, QStatusBar, QProgressBar,
    QDialog, QLineEdit, QPushButton, QFormLayout, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QColorDialog, QFontDialog,
    QInputDialog, QWizard, QWizardPage, QListWidget, QListWidgetItem,
    QGroupBox, QRadioButton, QSlider, QDoubleSpinBox, QFrame,
    QSizePolicy, QToolButton, QStyle, QApplication
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QSize, QTimer, QSettings,
    QPoint, QRect, QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QImage, QColor, QPainter, QPen, QBrush,
    QFont, QKeySequence, QShortcut, QCursor, QTransform,
    QAction, QPalette, QScreen
)

# Import our custom modules
from pdf_engine import PDFEngine, PDFPage
from annotation_system import AnnotationManager, AnnotationType
from signature_system import SignatureManager
from form_manager import FormManager
from ocr_engine import OCREngine
from export_manager import ExportManager
from ui_components import (
    PDFViewWidget, ThumbnailPanel, AnnotationToolbar,
    PropertiesPanel, SearchDialog, PageNavigator
)


class ProPDFEditor(QMainWindow):
    """Main application window for ProPDF Editor."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProPDF Editor - Professional PDF Editor")
        self.setMinimumSize(1200, 800)
        
        # Initialize settings
        self.settings = QSettings("ProPDF", "Editor")
        self.load_settings()
        
        # Initialize core components
        self.pdf_engine = PDFEngine()
        self.annotation_manager = AnnotationManager()
        self.signature_manager = SignatureManager()
        self.form_manager = FormManager()
        self.ocr_engine = OCREngine()
        self.export_manager = ExportManager()
        
        # State variables
        self.current_file = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.is_modified = False
        
        # Build UI
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_shortcuts()
        self.setup_statusbar()
        
        # Apply theme
        self.apply_theme()
        
    def setup_ui(self):
        """Setup the main user interface."""
        # Central widget with splitter
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        # Left panel - Thumbnails and navigation
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Thumbnail panel
        self.thumbnail_panel = ThumbnailPanel()
        self.thumbnail_panel.page_selected.connect(self.goto_page)
        left_layout.addWidget(self.thumbnail_panel)
        
        # Page navigator
        self.page_navigator = PageNavigator()
        self.page_navigator.page_changed.connect(self.goto_page)
        left_layout.addWidget(self.page_navigator)
        
        self.splitter.addWidget(self.left_panel)
        
        # Center - PDF View
        self.pdf_view = PDFViewWidget()
        self.pdf_view.page_changed.connect(self.on_page_changed)
        self.pdf_view.annotation_created.connect(self.on_annotation_created)
        self.pdf_view.zoom_changed.connect(self.on_zoom_changed)
        self.splitter.addWidget(self.pdf_view)
        
        # Right panel - Properties and annotations
        self.right_panel = QTabWidget()
        
        # Properties panel
        self.properties_panel = PropertiesPanel()
        self.properties_panel.property_changed.connect(self.on_property_changed)
        self.right_panel.addTab(self.properties_panel, "Properties")
        
        # Annotations list
        self.annotations_list = QListWidget()
        self.annotations_list.itemClicked.connect(self.on_annotation_selected)
        self.right_panel.addTab(self.annotations_list, "Annotations")
        
        # Form fields panel
        self.form_panel = QListWidget()
        self.right_panel.addTab(self.form_panel, "Form Fields")
        
        self.splitter.addWidget(self.right_panel)
        
        # Set splitter proportions
        self.splitter.setSizes([200, 800, 250])
        
        # Annotation toolbar (floating)
        self.annotation_toolbar = AnnotationToolbar()
        self.annotation_toolbar.tool_selected.connect(self.on_annotation_tool_selected)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.annotation_toolbar)
        
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New PDF", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_pdf)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_pdf)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_pdf)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_pdf_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Export submenu
        export_menu = file_menu.addMenu("&Export")
        
        export_word = QAction("Export to &Word...", self)
        export_word.triggered.connect(lambda: self.export_file("word"))
        export_menu.addAction(export_word)
        
        export_excel = QAction("Export to &Excel...", self)
        export_excel.triggered.connect(lambda: self.export_file("excel"))
        export_menu.addAction(export_excel)
        
        export_images = QAction("Export to &Images...", self)
        export_images.triggered.connect(lambda: self.export_file("images"))
        export_menu.addAction(export_images)
        
        export_text = QAction("Export to &Text...", self)
        export_text.triggered.connect(lambda: self.export_file("text"))
        export_menu.addAction(export_text)
        
        file_menu.addSeparator()
        
        print_action = QAction("&Print...", self)
        print_action.setShortcut(QKeySequence.StandardKey.Print)
        print_action.triggered.connect(self.print_pdf)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        replace_action = QAction("&Replace...", self)
        replace_action.setShortcut(QKeySequence.StandardKey.Replace)
        replace_action.triggered.connect(self.replace_text)
        edit_menu.addAction(replace_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        fit_width_action = QAction("Fit &Width", self)
        fit_width_action.triggered.connect(self.fit_width)
        view_menu.addAction(fit_width_action)
        
        fit_page_action = QAction("Fit &Page", self)
        fit_page_action.triggered.connect(self.fit_page)
        view_menu.addAction(fit_page_action)
        
        view_menu.addSeparator()
        
        rotate_left_action = QAction("Rotate &Left", self)
        rotate_left_action.triggered.connect(self.rotate_left)
        view_menu.addAction(rotate_left_action)
        
        rotate_right_action = QAction("Rotate &Right", self)
        rotate_right_action.triggered.connect(self.rotate_right)
        view_menu.addAction(rotate_right_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        ocr_action = QAction("&OCR - Extract Text", self)
        ocr_action.triggered.connect(self.perform_ocr)
        tools_menu.addAction(ocr_action)
        
        tools_menu.addSeparator()
        
        merge_action = QAction("&Merge PDFs...", self)
        merge_action.triggered.connect(self.merge_pdfs)
        tools_menu.addAction(merge_action)
        
        split_action = QAction("&Split PDF...", self)
        split_action.triggered.connect(self.split_pdf)
        tools_menu.addAction(split_action)
        
        compress_action = QAction("&Compress PDF...", self)
        compress_action.triggered.connect(self.compress_pdf)
        tools_menu.addAction(compress_action)
        
        tools_menu.addSeparator()
        
        protect_action = QAction("&Protect PDF...", self)
        protect_action.triggered.connect(self.protect_pdf)
        tools_menu.addAction(protect_action)
        
        # Annotate menu
        annotate_menu = menubar.addMenu("&Annotate")
        
        highlight_action = QAction("&Highlight", self)
        highlight_action.triggered.connect(lambda: self.set_annotation_tool("highlight"))
        annotate_menu.addAction(highlight_action)
        
        underline_action = QAction("&Underline", self)
        underline_action.triggered.connect(lambda: self.set_annotation_tool("underline"))
        annotate_menu.addAction(underline_action)
        
        strikethrough_action = QAction("&Strikethrough", self)
        strikethrough_action.triggered.connect(lambda: self.set_annotation_tool("strikethrough"))
        annotate_menu.addAction(strikethrough_action)
        
        annotate_menu.addSeparator()
        
        note_action = QAction("Add &Note", self)
        note_action.triggered.connect(lambda: self.set_annotation_tool("note"))
        annotate_menu.addAction(note_action)
        
        text_action = QAction("Add &Text", self)
        text_action.triggered.connect(lambda: self.set_annotation_tool("text"))
        annotate_menu.addAction(text_action)
        
        freehand_action = QAction("&Freehand Drawing", self)
        freehand_action.triggered.connect(lambda: self.set_annotation_tool("freehand"))
        annotate_menu.addAction(freehand_action)
        
        shape_action = QAction("&Shapes", self)
        shape_action.triggered.connect(lambda: self.set_annotation_tool("shape"))
        annotate_menu.addAction(shape_action)
        
        annotate_menu.addSeparator()
        
        stamp_action = QAction("&Stamp...", self)
        stamp_action.triggered.connect(self.add_stamp)
        annotate_menu.addAction(stamp_action)
        
        # Sign menu
        sign_menu = menubar.addMenu("&Sign")
        
        digital_sign_action = QAction("&Digital Signature...", self)
        digital_sign_action.triggered.connect(self.add_digital_signature)
        sign_menu.addAction(digital_sign_action)
        
        handwritten_sign_action = QAction("&Handwritten Signature...", self)
        handwritten_sign_action.triggered.connect(self.add_handwritten_signature)
        sign_menu.addAction(handwritten_sign_action)
        
        cert_action = QAction("&Manage Certificates...", self)
        cert_action.triggered.connect(self.manage_certificates)
        sign_menu.addAction(cert_action)
        
        # Forms menu
        forms_menu = menubar.addMenu("F&orms")
        
        add_text_field = QAction("Add &Text Field", self)
        add_text_field.triggered.connect(lambda: self.add_form_field("text"))
        forms_menu.addAction(add_text_field)
        
        add_checkbox = QAction("Add &Checkbox", self)
        add_checkbox.triggered.connect(lambda: self.add_form_field("checkbox"))
        forms_menu.addAction(add_checkbox)
        
        add_radio = QAction("Add &Radio Button", self)
        add_radio.triggered.connect(lambda: self.add_form_field("radio"))
        forms_menu.addAction(add_radio)
        
        add_dropdown = QAction("Add &Dropdown", self)
        add_dropdown.triggered.connect(lambda: self.add_form_field("dropdown"))
        forms_menu.addAction(add_dropdown)
        
        forms_menu.addSeparator()
        
        fill_form_action = QAction("&Fill Form", self)
        fill_form_action.triggered.connect(self.fill_form)
        forms_menu.addAction(fill_form_action)
        
        clear_form_action = QAction("&Clear Form", self)
        clear_form_action.triggered.connect(self.clear_form)
        forms_menu.addAction(clear_form_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
    def setup_toolbar(self):
        """Setup the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # File operations
        open_btn = QToolButton()
        open_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        open_btn.setToolTip("Open PDF")
        open_btn.clicked.connect(self.open_pdf)
        toolbar.addWidget(open_btn)
        
        save_btn = QToolButton()
        save_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        save_btn.setToolTip("Save PDF")
        save_btn.clicked.connect(self.save_pdf)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        # Navigation
        prev_btn = QToolButton()
        prev_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowLeft))
        prev_btn.setToolTip("Previous Page")
        prev_btn.clicked.connect(self.previous_page)
        toolbar.addWidget(prev_btn)
        
        next_btn = QToolButton()
        next_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        next_btn.setToolTip("Next Page")
        next_btn.clicked.connect(self.next_page)
        toolbar.addWidget(next_btn)
        
        toolbar.addSeparator()
        
        # Zoom
        zoom_out_btn = QToolButton()
        zoom_out_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        zoom_out_btn.setToolTip("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(zoom_out_btn)
        
        self.zoom_label = QLabel("100%")
        toolbar.addWidget(self.zoom_label)
        
        zoom_in_btn = QToolButton()
        zoom_in_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        zoom_in_btn.setToolTip("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(zoom_in_btn)
        
        toolbar.addSeparator()
        
        # Common annotations
        highlight_btn = QToolButton()
        highlight_btn.setText("H")
        highlight_btn.setToolTip("Highlight")
        highlight_btn.clicked.connect(lambda: self.set_annotation_tool("highlight"))
        toolbar.addWidget(highlight_btn)
        
        note_btn = QToolButton()
        note_btn.setText("N")
        note_btn.setToolTip("Add Note")
        note_btn.clicked.connect(lambda: self.set_annotation_tool("note"))
        toolbar.addWidget(note_btn)
        
        sign_btn = QToolButton()
        sign_btn.setText("S")
        sign_btn.setToolTip("Sign")
        sign_btn.clicked.connect(self.add_handwritten_signature)
        toolbar.addWidget(sign_btn)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Page navigation
        QShortcut(QKeySequence("PgUp"), self, self.previous_page)
        QShortcut(QKeySequence("PgDown"), self, self.next_page)
        QShortcut(QKeySequence("Home"), self, self.first_page)
        QShortcut(QKeySequence("End"), self, self.last_page)
        
        # Zoom
        QShortcut(QKeySequence("Ctrl+0"), self, self.reset_zoom)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        
        # Tools
        QShortcut(QKeySequence("Ctrl+F"), self, self.find_text)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.add_digital_signature)
        
    def setup_statusbar(self):
        """Setup the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.page_label = QLabel("Page: 0 / 0")
        self.statusbar.addWidget(self.page_label)
        
        self.size_label = QLabel("Size: -")
        self.statusbar.addWidget(self.size_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
        
    def apply_theme(self):
        """Apply application theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QMenuBar {
                background-color: #3c3f41;
                color: #bbbbbb;
            }
            QMenuBar::item:selected {
                background-color: #4b6eaf;
            }
            QMenu {
                background-color: #3c3f41;
                color: #bbbbbb;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #4b6eaf;
            }
            QToolBar {
                background-color: #3c3f41;
                border: none;
                spacing: 5px;
            }
            QToolButton {
                background-color: transparent;
                color: #bbbbbb;
                padding: 5px;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #4b6eaf;
            }
            QStatusBar {
                background-color: #3c3f41;
                color: #bbbbbb;
            }
            QLabel {
                color: #bbbbbb;
            }
            QTabWidget::pane {
                background-color: #2b2b2b;
                border: 1px solid #555555;
            }
            QTabBar::tab {
                background-color: #3c3f41;
                color: #bbbbbb;
                padding: 8px 15px;
                border: 1px solid #555555;
            }
            QTabBar::tab:selected {
                background-color: #4b6eaf;
            }
            QDockWidget {
                color: #bbbbbb;
                titlebar-close-icon: url(close.png);
            }
            QDockWidget::title {
                background-color: #3c3f41;
                padding: 5px;
            }
            QTreeWidget, QListWidget {
                background-color: #2b2b2b;
                color: #bbbbbb;
                border: 1px solid #555555;
            }
            QTreeWidget::item:selected, QListWidget::item:selected {
                background-color: #4b6eaf;
            }
            QScrollArea {
                border: none;
            }
        """)
        
    # ==================== File Operations ====================
    
    def new_pdf(self):
        """Create a new PDF document."""
        reply = QMessageBox.question(
            self, "New PDF",
            "Create a new PDF? Unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.pdf_engine.new_document()
            self.current_file = None
            self.current_page = 0
            self.is_modified = False
            self.update_ui()
            
    def open_pdf(self):
        """Open a PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self.load_pdf(file_path)
            
    def load_pdf(self, file_path: str):
        """Load a PDF file."""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)
            
            self.pdf_engine.load(file_path)
            self.current_file = file_path
            self.current_page = 0
            self.is_modified = False
            
            self.progress_bar.setValue(50)
            
            # Update UI components
            self.pdf_view.set_document(self.pdf_engine)
            self.thumbnail_panel.set_document(self.pdf_engine)
            self.page_navigator.set_page_count(self.pdf_engine.page_count)
            self.update_annotations_list()
            
            self.progress_bar.setValue(100)
            
            self.update_ui()
            self.statusbar.showMessage(f"Loaded: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF:\n{str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            
    def save_pdf(self):
        """Save the current PDF."""
        if self.current_file:
            self.save_pdf_to_path(self.current_file)
        else:
            self.save_pdf_as()
            
    def save_pdf_as(self):
        """Save PDF with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'
            self.save_pdf_to_path(file_path)
            self.current_file = file_path
            
    def save_pdf_to_path(self, file_path: str):
        """Save PDF to specified path."""
        try:
            self.pdf_engine.save(file_path)
            self.is_modified = False
            self.statusbar.showMessage(f"Saved: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{str(e)}")
            
    def export_file(self, format_type: str):
        """Export PDF to different formats."""
        try:
            if format_type == "word":
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Export to Word", "", "Word Documents (*.docx)"
                )
                if file_path:
                    self.export_manager.export_to_word(self.pdf_engine, file_path)
                    
            elif format_type == "excel":
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Export to Excel", "", "Excel Files (*.xlsx)"
                )
                if file_path:
                    self.export_manager.export_to_excel(self.pdf_engine, file_path)
                    
            elif format_type == "images":
                folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
                if folder:
                    self.export_manager.export_to_images(self.pdf_engine, folder)
                    
            elif format_type == "text":
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Export to Text", "", "Text Files (*.txt)"
                )
                if file_path:
                    self.export_manager.export_to_text(self.pdf_engine, file_path)
                    
            self.statusbar.showMessage(f"Export completed!", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
            
    def print_pdf(self):
        """Print the PDF."""
        from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
        
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.pdf_engine.print_document(printer)
            
    # ==================== Navigation ====================
    
    def goto_page(self, page_num: int):
        """Navigate to a specific page."""
        if 0 <= page_num < self.pdf_engine.page_count:
            self.current_page = page_num
            self.pdf_view.goto_page(page_num)
            self.page_navigator.set_current_page(page_num)
            self.update_page_label()
            
    def previous_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.goto_page(self.current_page - 1)
            
    def next_page(self):
        """Go to next page."""
        if self.current_page < self.pdf_engine.page_count - 1:
            self.goto_page(self.current_page + 1)
            
    def first_page(self):
        """Go to first page."""
        self.goto_page(0)
        
    def last_page(self):
        """Go to last page."""
        self.goto_page(self.pdf_engine.page_count - 1)
        
    def on_page_changed(self, page_num: int):
        """Handle page change from view."""
        self.current_page = page_num
        self.page_navigator.set_current_page(page_num)
        self.update_page_label()
        
    def update_page_label(self):
        """Update the page indicator."""
        self.page_label.setText(
            f"Page: {self.current_page + 1} / {self.pdf_engine.page_count}"
        )
        
    # ==================== Zoom ====================
    
    def zoom_in(self):
        """Zoom in."""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self.apply_zoom()
        
    def zoom_out(self):
        """Zoom out."""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self.apply_zoom()
        
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.zoom_level = 1.0
        self.apply_zoom()
        
    def fit_width(self):
        """Fit page to width."""
        self.pdf_view.fit_width()
        self.zoom_level = self.pdf_view.get_zoom()
        self.update_zoom_label()
        
    def fit_page(self):
        """Fit page to window."""
        self.pdf_view.fit_page()
        self.zoom_level = self.pdf_view.get_zoom()
        self.update_zoom_label()
        
    def apply_zoom(self):
        """Apply current zoom level."""
        self.pdf_view.set_zoom(self.zoom_level)
        self.update_zoom_label()
        
    def on_zoom_changed(self, zoom: float):
        """Handle zoom change from view."""
        self.zoom_level = zoom
        self.update_zoom_label()
        
    def update_zoom_label(self):
        """Update zoom percentage label."""
        self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
        
    # ==================== Rotation ====================
    
    def rotate_left(self):
        """Rotate page left."""
        self.pdf_engine.rotate_page(self.current_page, -90)
        self.pdf_view.update_page()
        self.is_modified = True
        
    def rotate_right(self):
        """Rotate page right."""
        self.pdf_engine.rotate_page(self.current_page, 90)
        self.pdf_view.update_page()
        self.is_modified = True
        
    # ==================== Annotations ====================
    
    def set_annotation_tool(self, tool_type: str):
        """Set the current annotation tool."""
        self.pdf_view.set_annotation_tool(tool_type)
        self.statusbar.showMessage(f"Tool: {tool_type.title()}", 2000)
        
    def on_annotation_tool_selected(self, tool_type: str):
        """Handle annotation tool selection."""
        self.set_annotation_tool(tool_type)
        
    def on_annotation_created(self, annotation):
        """Handle new annotation creation."""
        self.annotation_manager.add_annotation(annotation)
        self.update_annotations_list()
        self.is_modified = True
        
    def on_annotation_selected(self, item):
        """Handle annotation selection from list."""
        annotation_id = item.data(Qt.ItemDataRole.UserRole)
        self.pdf_view.select_annotation(annotation_id)
        
    def update_annotations_list(self):
        """Update the annotations list panel."""
        self.annotations_list.clear()
        for ann in self.annotation_manager.get_annotations():
            item = QListWidgetItem(f"{ann.type.name}: {ann.text or 'No text'}")
            item.setData(Qt.ItemDataRole.UserRole, ann.id)
            self.annotations_list.addItem(item)
            
    def add_stamp(self):
        """Add a stamp annotation."""
        stamps = ["APPROVED", "REVIEWED", "CONFIDENTIAL", "DRAFT", "FINAL"]
        stamp, ok = QInputDialog.getItem(
            self, "Add Stamp", "Select stamp:", stamps, 0, False
        )
        if ok:
            self.pdf_view.set_annotation_tool("stamp", stamp_text=stamp)
            
    # ==================== Signatures ====================
    
    def add_digital_signature(self):
        """Add a digital signature to the PDF."""
        dialog = DigitalSignatureDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            signature_data = dialog.get_signature_data()
            try:
                self.signature_manager.add_digital_signature(
                    self.pdf_engine, self.current_page, signature_data
                )
                self.is_modified = True
                self.statusbar.showMessage("Digital signature added!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Signature Error", str(e))
                
    def add_handwritten_signature(self):
        """Add a handwritten signature."""
        dialog = HandwrittenSignatureDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            signature_image = dialog.get_signature_image()
            self.pdf_view.set_signature_mode(signature_image)
            
    def manage_certificates(self):
        """Open certificate management dialog."""
        dialog = CertificateManagerDialog(self.signature_manager, self)
        dialog.exec()
        
    # ==================== Forms ====================
    
    def add_form_field(self, field_type: str):
        """Add a form field to the PDF."""
        self.pdf_view.set_form_field_mode(field_type)
        self.statusbar.showMessage(f"Click on page to place {field_type} field", 3000)
        
    def fill_form(self):
        """Enable form filling mode."""
        self.pdf_view.set_form_fill_mode(True)
        self.statusbar.showMessage("Form fill mode enabled", 3000)
        
    def clear_form(self):
        """Clear all form fields."""
        reply = QMessageBox.question(
            self, "Clear Form",
            "Clear all form fields?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.form_manager.clear_all_fields()
            self.pdf_view.update_page()
            self.is_modified = True
            
    # ==================== Tools ====================
    
    def perform_ocr(self):
        """Perform OCR on the current page."""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            text = self.ocr_engine.extract_text(
                self.pdf_engine, self.current_page,
                progress_callback=lambda p: self.progress_bar.setValue(p)
            )
            
            # Show extracted text
            dialog = QDialog(self)
            dialog.setWindowTitle("OCR Results")
            dialog.setMinimumSize(500, 400)
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(text)
            layout.addWidget(text_edit)
            
            btn_layout = QHBoxLayout()
            copy_btn = QPushButton("Copy to Clipboard")
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(text))
            btn_layout.addWidget(copy_btn)
            
            save_btn = QPushButton("Save to File")
            save_btn.clicked.connect(lambda: self.save_ocr_text(text))
            btn_layout.addWidget(save_btn)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            btn_layout.addWidget(close_btn)
            
            layout.addLayout(btn_layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "OCR Error", str(e))
        finally:
            self.progress_bar.setVisible(False)
            
    def save_ocr_text(self, text: str):
        """Save OCR text to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Text", "", "Text Files (*.txt)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            self.statusbar.showMessage(f"Saved to: {file_path}", 3000)
            
    def merge_pdfs(self):
        """Merge multiple PDFs."""
        dialog = MergePDFsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            files = dialog.get_selected_files()
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Save Merged PDF", "", "PDF Files (*.pdf)"
            )
            if output_path:
                try:
                    self.pdf_engine.merge_pdfs(files, output_path)
                    self.statusbar.showMessage("PDFs merged successfully!", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Merge Error", str(e))
                    
    def split_pdf(self):
        """Split the current PDF."""
        dialog = SplitPDFDialog(self.pdf_engine.page_count, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ranges = dialog.get_page_ranges()
            output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if output_folder:
                try:
                    self.pdf_engine.split_pdf(ranges, output_folder)
                    self.statusbar.showMessage("PDF split successfully!", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Split Error", str(e))
                    
    def compress_pdf(self):
        """Compress the PDF."""
        dialog = CompressPDFDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            quality = dialog.get_quality_level()
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Save Compressed PDF", "", "PDF Files (*.pdf)"
            )
            if output_path:
                try:
                    self.progress_bar.setVisible(True)
                    self.pdf_engine.compress(quality, output_path)
                    self.statusbar.showMessage("PDF compressed successfully!", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Compression Error", str(e))
                finally:
                    self.progress_bar.setVisible(False)
                    
    def protect_pdf(self):
        """Add password protection to PDF."""
        dialog = ProtectPDFDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password = dialog.get_password()
            permissions = dialog.get_permissions()
            try:
                self.pdf_engine.set_password(password, permissions)
                self.is_modified = True
                self.statusbar.showMessage("PDF protected successfully!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Protection Error", str(e))
                
    # ==================== Edit Operations ====================
    
    def undo(self):
        """Undo last action."""
        if self.pdf_engine.can_undo():
            self.pdf_engine.undo()
            self.pdf_view.update_page()
            self.is_modified = True
            
    def redo(self):
        """Redo last undone action."""
        if self.pdf_engine.can_redo():
            self.pdf_engine.redo()
            self.pdf_view.update_page()
            self.is_modified = True
            
    def cut(self):
        """Cut selected content."""
        self.pdf_view.cut()
        
    def copy(self):
        """Copy selected content."""
        self.pdf_view.copy()
        
    def paste(self):
        """Paste content."""
        self.pdf_view.paste()
        
    def select_all(self):
        """Select all content."""
        self.pdf_view.select_all()
        
    def find_text(self):
        """Open find dialog."""
        dialog = SearchDialog(self.pdf_engine, self)
        dialog.exec()
        
    def replace_text(self):
        """Open replace dialog."""
        dialog = ReplaceDialog(self.pdf_engine, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.pdf_view.update_page()
            self.is_modified = True
            
    def on_property_changed(self, property_name: str, value):
        """Handle property changes from properties panel."""
        self.pdf_engine.set_property(property_name, value)
        self.pdf_view.update_page()
        self.is_modified = True
        
    # ==================== UI Updates ====================
    
    def update_ui(self):
        """Update all UI components."""
        self.update_page_label()
        self.update_zoom_label()
        self.thumbnail_panel.update_thumbnails()
        
    def load_settings(self):
        """Load application settings."""
        self.default_open_dir = self.settings.value("default_open_dir", "")
        self.default_save_dir = self.settings.value("default_save_dir", "")
        
    def save_settings(self):
        """Save application settings."""
        self.settings.setValue("default_open_dir", self.default_open_dir)
        self.settings.setValue("default_save_dir", self.default_save_dir)
        
    # ==================== Help ====================
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About ProPDF Editor",
            """<h2>ProPDF Editor</h2>
            <p>Version 1.0.0</p>
            <p>A professional PDF viewer and editor with annotation, 
            signing, and editing capabilities.</p>
            <p>Features:</p>
            <ul>
                <li>View and edit PDF documents</li>
                <li>Annotate with highlights, notes, and drawings</li>
                <li>Digital and handwritten signatures</li>
                <li>Form filling and creation</li>
                <li>OCR text extraction</li>
                <li>Merge, split, and compress PDFs</li>
                <li>Export to multiple formats</li>
                <li>Password protection</li>
            </ul>
            <p>Built with Python and PyQt6</p>"""
        )
        
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        QMessageBox.information(
            self, "Keyboard Shortcuts",
            """<h2>Keyboard Shortcuts</h2>
            <table>
            <tr><td><b>Ctrl+O</b></td><td>Open PDF</td></tr>
            <tr><td><b>Ctrl+S</b></td><td>Save PDF</td></tr>
            <tr><td><b>Ctrl+Shift+S</b></td><td>Save As</td></tr>
            <tr><td><b>Ctrl+P</b></td><td>Print</td></tr>
            <tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
            <tr><td><b>Ctrl+Y</b></td><td>Redo</td></tr>
            <tr><td><b>Ctrl+C</b></td><td>Copy</td></tr>
            <tr><td><b>Ctrl+V</b></td><td>Paste</td></tr>
            <tr><td><b>Ctrl+F</b></td><td>Find</td></tr>
            <tr><td><b>Ctrl++</b></td><td>Zoom In</td></tr>
            <tr><td><b>Ctrl+-</b></td><td>Zoom Out</td></tr>
            <tr><td><b>Ctrl+0</b></td><td>Reset Zoom</td></tr>
            <tr><td><b>PgUp</b></td><td>Previous Page</td></tr>
            <tr><td><b>PgDown</b></td><td>Next Page</td></tr>
            <tr><td><b>Home</b></td><td>First Page</td></tr>
            <tr><td><b>End</b></td><td>Last Page</td></tr>
            </table>"""
        )
        
    def closeEvent(self, event):
        """Handle application close."""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.save_pdf()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
            
        self.save_settings()


# Import dialog classes
from dialogs import (
    DigitalSignatureDialog, HandwrittenSignatureDialog, CertificateManagerDialog,
    MergePDFsDialog, SplitPDFDialog, CompressPDFDialog, ProtectPDFDialog, ReplaceDialog
)


def main():
    """Main entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("ProPDF Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ProPDF")
    
    # Set application icon
    # app.setWindowIcon(QIcon("assets/icon.png"))
    
    window = ProPDFEditor()
    window.show()
    
    # Open file from command line if provided
    if len(sys.argv) > 1 and sys.argv[1].endswith('.pdf'):
        window.load_pdf(sys.argv[1])
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
