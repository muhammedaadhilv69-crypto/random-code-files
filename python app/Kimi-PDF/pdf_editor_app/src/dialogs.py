"""
Dialogs Module - Custom dialogs for the PDF editor
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QGroupBox, QTabWidget, QWidget, QScrollArea,
    QFrame, QSplitter, QListWidget, QListWidgetItem,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QProgressDialog,
    QDialogButtonBox, QRadioButton, QButtonGroup,
    QSlider, QColorDialog, QFontDialog, QInputDialog,
    QWizard, QWizardPage, QStackedWidget, QToolButton,
    QSizePolicy, QGridLayout, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
from PIL import Image, ImageDraw, ImageFont
import io
import fitz


class DigitalSignatureDialog(QDialog):
    """Dialog for adding digital signatures."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Add Digital Signature")
        self.setMinimumSize(500, 400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Certificate selection
        cert_group = QGroupBox("Select Certificate")
        cert_layout = QVBoxLayout(cert_group)
        
        self.cert_combo = QComboBox()
        cert_layout.addWidget(self.cert_combo)
        
        self.cert_info = QLabel("No certificate selected")
        cert_layout.addWidget(self.cert_info)
        
        layout.addWidget(cert_group)
        
        # Signature appearance
        appear_group = QGroupBox("Signature Appearance")
        appear_layout = QFormLayout(appear_group)
        
        self.show_name_check = QCheckBox("Show signer name")
        self.show_name_check.setChecked(True)
        appear_layout.addRow(self.show_name_check)
        
        self.show_date_check = QCheckBox("Show date")
        self.show_date_check.setChecked(True)
        appear_layout.addRow(self.show_date_check)
        
        self.show_reason_check = QCheckBox("Show reason")
        appear_layout.addRow(self.show_reason_check)
        
        self.reason_edit = QLineEdit()
        self.reason_edit.setPlaceholderText("Reason for signing")
        appear_layout.addRow("Reason:", self.reason_edit)
        
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Location")
        appear_layout.addRow("Location:", self.location_edit)
        
        layout.addWidget(appear_group)
        
        # Position
        pos_group = QGroupBox("Signature Position")
        pos_layout = QFormLayout(pos_group)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(50, 500)
        self.width_spin.setValue(200)
        pos_layout.addRow("Width:", self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(30, 200)
        self.height_spin.setValue(60)
        pos_layout.addRow("Height:", self.height_spin)
        
        layout.addWidget(pos_group)
        
        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def get_signature_data(self) -> dict:
        """Get the signature configuration."""
        return {
            'certificate_id': self.cert_combo.currentData(),
            'show_name': self.show_name_check.isChecked(),
            'show_date': self.show_date_check.isChecked(),
            'show_reason': self.show_reason_check.isChecked(),
            'reason': self.reason_edit.text(),
            'location': self.location_edit.text(),
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
        }


class HandwrittenSignatureDialog(QDialog):
    """Dialog for creating handwritten signatures."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Create Handwritten Signature")
        self.setMinimumSize(600, 400)
        
        self.signature_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Tabs for different methods
        tabs = QTabWidget()
        
        # Draw tab
        draw_tab = QWidget()
        draw_layout = QVBoxLayout(draw_tab)
        
        self.canvas = SignatureCanvas()
        draw_layout.addWidget(self.canvas)
        
        draw_btn_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.canvas.clear)
        draw_btn_layout.addWidget(clear_btn)
        
        draw_btn_layout.addStretch()
        draw_layout.addLayout(draw_btn_layout)
        
        tabs.addTab(draw_tab, "Draw")
        
        # Type tab
        type_tab = QWidget()
        type_layout = QVBoxLayout(type_tab)
        
        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("Type your signature")
        type_layout.addWidget(self.type_edit)
        
        font_btn = QPushButton("Choose Font")
        font_btn.clicked.connect(self.choose_font)
        type_layout.addWidget(font_btn)
        
        self.type_preview = QLabel("Preview")
        self.type_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_preview.setMinimumHeight(100)
        self.type_preview.setFrameStyle(QFrame.Shape.StyledPanel)
        type_layout.addWidget(self.type_preview)
        
        update_preview_btn = QPushButton("Update Preview")
        update_preview_btn.clicked.connect(self.update_type_preview)
        type_layout.addWidget(update_preview_btn)
        
        tabs.addTab(type_tab, "Type")
        
        # Image tab
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        
        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setFrameStyle(QFrame.Shape.StyledPanel)
        image_layout.addWidget(self.image_label)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_image)
        image_layout.addWidget(browse_btn)
        
        tabs.addTab(image_tab, "Image")
        
        layout.addWidget(tabs)
        
        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
        self.tabs = tabs
        
    def choose_font(self):
        """Choose font for typed signature."""
        font, ok = QFontDialog.getFont(self)
        if ok:
            self.type_preview.setFont(font)
            
    def update_type_preview(self):
        """Update the typed signature preview."""
        text = self.type_edit.text()
        self.type_preview.setText(text)
        
        # Create image from text
        pixmap = self.type_preview.grab()
        buffer = io.BytesIO()
        pixmap.save(buffer, "PNG")
        self.signature_image = buffer.getvalue()
        
    def browse_image(self):
        """Browse for signature image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Signature Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            
            with open(file_path, 'rb') as f:
                self.signature_image = f.read()
                
    def get_signature_image(self) -> bytes:
        """Get the created signature image."""
        if self.tabs.currentIndex() == 0:  # Draw
            return self.canvas.get_image()
        return self.signature_image


class SignatureCanvas(QWidget):
    """Canvas for drawing signatures."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(500, 200)
        self.setStyleSheet("background-color: white; border: 1px solid black;")
        
        self.points = []
        self.current_stroke = []
        self.is_drawing = False
        
    def clear(self):
        """Clear the canvas."""
        self.points = []
        self.current_stroke = []
        self.update()
        
    def get_image(self) -> bytes:
        """Get the signature as image bytes."""
        img = Image.new('RGBA', (self.width(), self.height()), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        for stroke in self.points:
            if len(stroke) > 1:
                draw.line(stroke, fill=(0, 0, 0), width=2)
                
        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        return buffer.getvalue()
        
    def paintEvent(self, event):
        """Paint the canvas."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        
        for stroke in self.points:
            if len(stroke) > 1:
                for i in range(len(stroke) - 1):
                    painter.drawLine(stroke[i], stroke[i + 1])
                    
        painter.end()
        
    def mousePressEvent(self, event):
        """Handle mouse press."""
        self.is_drawing = True
        self.current_stroke = [event.pos()]
        
    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        if self.is_drawing:
            self.current_stroke.append(event.pos())
            self.update()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if self.is_drawing:
            self.current_stroke.append(event.pos())
            self.points.append(self.current_stroke)
            self.current_stroke = []
            self.is_drawing = False
            self.update()


class CertificateManagerDialog(QDialog):
    """Dialog for managing digital certificates."""
    
    def __init__(self, signature_manager, parent=None):
        super().__init__(parent)
        
        self.signature_manager = signature_manager
        
        self.setWindowTitle("Certificate Manager")
        self.setMinimumSize(600, 400)
        
        self.setup_ui()
        self.load_certificates()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Certificate list
        self.cert_list = QListWidget()
        layout.addWidget(self.cert_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create New")
        create_btn.clicked.connect(self.create_certificate)
        btn_layout.addWidget(create_btn)
        
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self.import_certificate)
        btn_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_certificate)
        btn_layout.addWidget(export_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_certificate)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
    def load_certificates(self):
        """Load certificates into the list."""
        self.cert_list.clear()
        
        for cert in self.signature_manager.get_all_certificates():
            item = QListWidgetItem(f"{cert.name} ({cert.organization})")
            item.setData(Qt.ItemDataRole.UserRole, cert.id)
            self.cert_list.addItem(item)
            
    def create_certificate(self):
        """Create a new self-signed certificate."""
        dialog = CreateCertificateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_certificate_data()
            self.signature_manager.create_self_signed_certificate(**data)
            self.load_certificates()
            
    def import_certificate(self):
        """Import a certificate from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Certificate", "",
            "Certificate Files (*.pem *.crt *.cer);;All Files (*)"
        )
        if file_path:
            try:
                self.signature_manager.import_certificate(file_path)
                self.load_certificates()
            except Exception as e:
                QMessageBox.critical(self, "Import Error", str(e))
                
    def export_certificate(self):
        """Export selected certificate."""
        item = self.cert_list.currentItem()
        if item:
            cert_id = item.data(Qt.ItemDataRole.UserRole)
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Certificate", "",
                "PEM Files (*.pem);;All Files (*)"
            )
            if file_path:
                self.signature_manager.export_certificate(cert_id, file_path)
                
    def delete_certificate(self):
        """Delete selected certificate."""
        item = self.cert_list.currentItem()
        if item:
            cert_id = item.data(Qt.ItemDataRole.UserRole)
            reply = QMessageBox.question(
                self, "Delete Certificate",
                "Are you sure you want to delete this certificate?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.signature_manager.delete_certificate(cert_id)
                self.load_certificates()


class CreateCertificateDialog(QDialog):
    """Dialog for creating a new certificate."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Create Certificate")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QFormLayout(self)
        
        self.name_edit = QLineEdit()
        layout.addRow("Name *:", self.name_edit)
        
        self.org_edit = QLineEdit()
        layout.addRow("Organization:", self.org_edit)
        
        self.email_edit = QLineEdit()
        layout.addRow("Email:", self.email_edit)
        
        self.country_edit = QLineEdit()
        self.country_edit.setMaxLength(2)
        self.country_edit.setText("US")
        layout.addRow("Country (2-letter):", self.country_edit)
        
        self.state_edit = QLineEdit()
        layout.addRow("State/Province:", self.state_edit)
        
        self.locality_edit = QLineEdit()
        layout.addRow("Locality:", self.locality_edit)
        
        self.validity_spin = QSpinBox()
        self.validity_spin.setRange(1, 10)
        self.validity_spin.setValue(1)
        self.validity_spin.setSuffix(" years")
        layout.addRow("Validity:", self.validity_spin)
        
        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)
        
    def get_certificate_data(self) -> dict:
        """Get certificate creation data."""
        return {
            'name': self.name_edit.text(),
            'organization': self.org_edit.text(),
            'email': self.email_edit.text(),
            'country': self.country_edit.text(),
            'state': self.state_edit.text(),
            'locality': self.locality_edit.text(),
            'validity_days': self.validity_spin.value() * 365,
        }


class MergePDFsDialog(QDialog):
    """Dialog for merging PDFs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Merge PDFs")
        self.setMinimumSize(500, 400)
        
        self.files = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # File list
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add PDFs")
        add_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_file)
        btn_layout.addWidget(remove_btn)
        
        up_btn = QPushButton("Move Up")
        up_btn.clicked.connect(self.move_up)
        btn_layout.addWidget(up_btn)
        
        down_btn = QPushButton("Move Down")
        down_btn.clicked.connect(self.move_down)
        btn_layout.addWidget(down_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Dialog buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def add_files(self):
        """Add PDF files to the list."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDFs", "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_list.addItem(file)
                
    def remove_file(self):
        """Remove selected file from list."""
        row = self.file_list.currentRow()
        if row >= 0:
            self.files.pop(row)
            self.file_list.takeItem(row)
            
    def move_up(self):
        """Move selected file up."""
        row = self.file_list.currentRow()
        if row > 0:
            self.files[row], self.files[row - 1] = self.files[row - 1], self.files[row]
            self.update_list()
            self.file_list.setCurrentRow(row - 1)
            
    def move_down(self):
        """Move selected file down."""
        row = self.file_list.currentRow()
        if row < len(self.files) - 1:
            self.files[row], self.files[row + 1] = self.files[row + 1], self.files[row]
            self.update_list()
            self.file_list.setCurrentRow(row + 1)
            
    def update_list(self):
        """Update the file list display."""
        self.file_list.clear()
        for file in self.files:
            self.file_list.addItem(file)
            
    def get_selected_files(self) -> list:
        """Get the list of files to merge."""
        return self.files


class SplitPDFDialog(QDialog):
    """Dialog for splitting PDF."""
    
    def __init__(self, page_count: int, parent=None):
        super().__init__(parent)
        
        self.page_count = page_count
        
        self.setWindowTitle("Split PDF")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QFormLayout(self)
        
        layout.addRow(QLabel(f"Total pages: {self.page_count}"))
        
        # Split method
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Split by page ranges",
            "Split every N pages",
            "Extract specific pages"
        ])
        layout.addRow("Method:", self.method_combo)
        
        # Page ranges
        self.ranges_edit = QLineEdit()
        self.ranges_edit.setPlaceholderText("e.g., 1-5, 6-10, 11-end")
        layout.addRow("Page ranges:", self.ranges_edit)
        
        # Split every N pages
        self.every_n_spin = QSpinBox()
        self.every_n_spin.setRange(1, self.page_count)
        self.every_n_spin.setValue(1)
        layout.addRow("Split every:", self.every_n_spin)
        
        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)
        
    def get_page_ranges(self) -> list:
        """Get the page ranges for splitting."""
        method = self.method_combo.currentIndex()
        
        if method == 0:  # By ranges
            ranges = []
            for part in self.ranges_edit.text().split(','):
                part = part.strip()
                if '-' in part:
                    start, end = part.split('-')
                    start = int(start) - 1
                    end = self.page_count - 1 if end == 'end' else int(end) - 1
                    ranges.append((start, end))
            return ranges
            
        elif method == 1:  # Every N pages
            n = self.every_n_spin.value()
            ranges = []
            for i in range(0, self.page_count, n):
                ranges.append((i, min(i + n - 1, self.page_count - 1)))
            return ranges
            
        else:  # Extract specific pages
            # Parse specific pages
            pages = []
            for part in self.ranges_edit.text().split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages.extend(range(start - 1, end))
                else:
                    pages.append(int(part) - 1)
            return [(p, p) for p in pages]


class CompressPDFDialog(QDialog):
    """Dialog for compressing PDF."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Compress PDF")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QFormLayout(self)
        
        # Quality selection
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "Low (smallest file, lower quality)",
            "Medium (balanced)",
            "High (larger file, better quality)",
            "Maximum (best quality)"
        ])
        self.quality_combo.setCurrentIndex(1)
        layout.addRow("Compression level:", self.quality_combo)
        
        # Info
        info = QLabel(
            "Compression reduces file size by optimizing images and removing redundant data."
        )
        info.setWordWrap(True)
        layout.addRow(info)
        
        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)
        
    def get_quality_level(self) -> str:
        """Get selected quality level."""
        levels = ['low', 'medium', 'high', 'maximum']
        return levels[self.quality_combo.currentIndex()]


class ProtectPDFDialog(QDialog):
    """Dialog for password protecting PDF."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Protect PDF")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QFormLayout(self)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Password:", self.password_edit)
        
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Confirm password:", self.confirm_edit)
        
        # Permissions
        perms_group = QGroupBox("Permissions")
        perms_layout = QVBoxLayout(perms_group)
        
        self.print_check = QCheckBox("Allow printing")
        self.print_check.setChecked(True)
        perms_layout.addWidget(self.print_check)
        
        self.copy_check = QCheckBox("Allow copying text/images")
        self.copy_check.setChecked(True)
        perms_layout.addWidget(self.copy_check)
        
        self.modify_check = QCheckBox("Allow modifications")
        perms_layout.addWidget(self.modify_check)
        
        self.annotate_check = QCheckBox("Allow annotations")
        self.annotate_check.setChecked(True)
        perms_layout.addWidget(self.annotate_check)
        
        layout.addRow(perms_group)
        
        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.validate_and_accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)
        
    def validate_and_accept(self):
        """Validate input before accepting."""
        if self.password_edit.text() != self.confirm_edit.text():
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return
            
        if len(self.password_edit.text()) < 4:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 4 characters.")
            return
            
        self.accept()
        
    def get_password(self) -> str:
        """Get the password."""
        return self.password_edit.text()
        
    def get_permissions(self) -> dict:
        """Get permission settings."""
        return {
            'print': self.print_check.isChecked(),
            'copy': self.copy_check.isChecked(),
            'modify': self.modify_check.isChecked(),
            'annotate': self.annotate_check.isChecked(),
        }


class ReplaceDialog(QDialog):
    """Dialog for find and replace."""
    
    def __init__(self, pdf_engine, parent=None):
        super().__init__(parent)
        
        self.pdf_engine = pdf_engine
        
        self.setWindowTitle("Find and Replace")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI."""
        layout = QFormLayout(self)
        
        self.find_edit = QLineEdit()
        layout.addRow("Find:", self.find_edit)
        
        self.replace_edit = QLineEdit()
        layout.addRow("Replace with:", self.replace_edit)
        
        # Options
        self.case_check = QCheckBox("Case sensitive")
        layout.addRow(self.case_check)
        
        self.whole_word_check = QCheckBox("Whole words only")
        layout.addRow(self.whole_word_check)
        
        # Scope
        scope_group = QGroupBox("Scope")
        scope_layout = QVBoxLayout(scope_group)
        
        self.current_page_radio = QRadioButton("Current page only")
        self.current_page_radio.setChecked(True)
        scope_layout.addWidget(self.current_page_radio)
        
        self.all_pages_radio = QRadioButton("All pages")
        scope_layout.addWidget(self.all_pages_radio)
        
        layout.addRow(scope_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        find_btn = QPushButton("Find Next")
        find_btn.clicked.connect(self.find_next)
        btn_layout.addWidget(find_btn)
        
        replace_btn = QPushButton("Replace")
        replace_btn.clicked.connect(self.replace)
        btn_layout.addWidget(replace_btn)
        
        replace_all_btn = QPushButton("Replace All")
        replace_all_btn.clicked.connect(self.replace_all)
        btn_layout.addWidget(replace_all_btn)
        
        btn_layout.addStretch()
        layout.addRow(btn_layout)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        layout.addRow(close_btn)
        
        self.current_result = 0
        self.results = []
        
    def find_next(self):
        """Find next occurrence."""
        text = self.find_edit.text()
        if not text:
            return
            
        case_sensitive = self.case_check.isChecked()
        whole_words = self.whole_word_check.isChecked()
        
        if not self.results:
            self.results = self.pdf_engine.search(text, case_sensitive, whole_words)
            
        if self.results and self.current_result < len(self.results):
            result = self.results[self.current_result]
            if self.parent():
                self.parent().goto_page(result['page'])
            self.current_result += 1
            
    def replace(self):
        """Replace current occurrence."""
        if self.results and self.current_result > 0:
            result = self.results[self.current_result - 1]
            old_text = self.find_edit.text()
            new_text = self.replace_edit.text()
            
            self.pdf_engine.replace_text(
                result['page'],
                old_text,
                new_text,
                result.get('rect')
            )
            
    def replace_all(self):
        """Replace all occurrences."""
        text = self.find_edit.text()
        if not text:
            return
            
        case_sensitive = self.case_check.isChecked()
        whole_words = self.whole_word_check.isChecked()
        
        results = self.pdf_engine.search(text, case_sensitive, whole_words)
        
        old_text = self.find_edit.text()
        new_text = self.replace_edit.text()
        
        for result in results:
            self.pdf_engine.replace_text(
                result['page'],
                old_text,
                new_text,
                result.get('rect')
            )
            
        QMessageBox.information(self, "Replace Complete", 
                               f"Replaced {len(results)} occurrences.")
