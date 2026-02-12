"""
ProPDF Editor - Professional PDF Viewer and Editor

A production-ready PDF application with annotation, signing, and editing capabilities.
"""

__version__ = "1.0.0"
__author__ = "ProPDF"
__license__ = "MIT"

from .pdf_engine import PDFEngine, PDFPage, PDFMetadata
from .annotation_system import AnnotationManager, Annotation, AnnotationType
from .signature_system import SignatureManager, Signature, SignatureCertificate
from .form_manager import FormManager, FormField, FieldType
from .ocr_engine import OCREngine, OCRResult
from .export_manager import ExportManager

__all__ = [
    'PDFEngine',
    'PDFPage',
    'PDFMetadata',
    'AnnotationManager',
    'Annotation',
    'AnnotationType',
    'SignatureManager',
    'Signature',
    'SignatureCertificate',
    'FormManager',
    'FormField',
    'FieldType',
    'OCREngine',
    'OCRResult',
    'ExportManager',
]
