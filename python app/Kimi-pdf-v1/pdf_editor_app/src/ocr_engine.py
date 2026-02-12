"""
OCR Engine Module - Optical Character Recognition for PDFs
"""

from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass
from PIL import Image
import io
import tempfile
import os


@dataclass
class OCRResult:
    """Represents OCR extraction result."""
    text: str
    confidence: float
    bounding_box: Optional[Tuple[int, int, int, int]] = None
    page: int = 0
    

class OCREngine:
    """OCR engine for extracting text from PDF images."""
    
    def __init__(self):
        self._tesseract_available = self._check_tesseract()
        self._easyocr_available = False
        self._language = 'eng'
        self._dpi = 300
        
    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is available."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
            
    def _check_easyocr(self) -> bool:
        """Check if EasyOCR is available."""
        try:
            import easyocr
            return True
        except:
            return False
            
    def is_available(self) -> bool:
        """Check if OCR is available."""
        return self._tesseract_available or self._easyocr_available
        
    def set_language(self, language: str):
        """Set OCR language."""
        self._language = language
        
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        if self._tesseract_available:
            try:
                import pytesseract
                langs = pytesseract.get_languages()
                return langs
            except:
                pass
        return ['eng']
        
    def extract_text(
        self,
        pdf_engine,
        page_num: Optional[int] = None,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> str:
        """Extract text from PDF using OCR."""
        if not self.is_available():
            raise RuntimeError("OCR engine not available. Please install Tesseract OCR.")
            
        all_text = []
        
        pages = [page_num] if page_num is not None else range(pdf_engine.page_count)
        total_pages = len(pages)
        
        for i, p_num in enumerate(pages):
            page = pdf_engine.get_page(p_num)
            if page:
                # Render page at high resolution
                pix = page.get_pixmap(zoom=self._dpi / 72)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Perform OCR
                text = self._ocr_image(img)
                all_text.append(f"--- Page {p_num + 1} ---\n{text}\n")
                
                if progress_callback:
                    progress = int((i + 1) / total_pages * 100)
                    progress_callback(progress)
                    
        return "\n".join(all_text)
        
    def _ocr_image(self, img: Image.Image) -> str:
        """Perform OCR on an image."""
        if self._tesseract_available:
            return self._ocr_with_tesseract(img)
        elif self._easyocr_available:
            return self._ocr_with_easyocr(img)
        else:
            return ""
            
    def _ocr_with_tesseract(self, img: Image.Image) -> str:
        """Perform OCR using Tesseract."""
        import pytesseract
        
        # Configure Tesseract for better accuracy
        custom_config = r'--oem 3 --psm 6'
        
        text = pytesseract.image_to_string(
            img,
            lang=self._language,
            config=custom_config
        )
        
        return text
        
    def _ocr_with_easyocr(self, img: Image.Image) -> str:
        """Perform OCR using EasyOCR."""
        import easyocr
        
        # Initialize reader (cached)
        if not hasattr(self, '_easyocr_reader'):
            self._easyocr_reader = easyocr.Reader([self._language])
            
        # Convert PIL to numpy array
        import numpy as np
        img_array = np.array(img)
        
        # Perform OCR
        results = self._easyocr_reader.readtext(img_array)
        
        # Extract text
        texts = [result[1] for result in results]
        return "\n".join(texts)
        
    def extract_text_with_boxes(
        self,
        pdf_engine,
        page_num: int
    ) -> List[OCRResult]:
        """Extract text with bounding boxes."""
        if not self.is_available():
            raise RuntimeError("OCR engine not available")
            
        page = pdf_engine.get_page(page_num)
        if not page:
            return []
            
        # Render page
        pix = page.get_pixmap(zoom=self._dpi / 72)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        results = []
        
        if self._tesseract_available:
            import pytesseract
            
            # Get detailed data
            data = pytesseract.image_to_data(
                img,
                lang=self._language,
                output_type=pytesseract.Output.DICT
            )
            
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # Filter low confidence
                    text = data['text'][i].strip()
                    if text:
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        results.append(OCRResult(
                            text=text,
                            confidence=float(data['conf'][i]) / 100,
                            bounding_box=(x, y, x + w, y + h),
                            page=page_num
                        ))
                        
        return results
        
    def search_text_in_image(
        self,
        pdf_engine,
        page_num: int,
        search_text: str
    ) -> List[Tuple[int, int, int, int]]:
        """Search for text in page image and return bounding boxes."""
        results = self.extract_text_with_boxes(pdf_engine, page_num)
        
        matches = []
        for result in results:
            if search_text.lower() in result.text.lower():
                matches.append(result.bounding_box)
                
        return matches
        
    def extract_tables(
        self,
        pdf_engine,
        page_num: int
    ) -> List[List[List[str]]]:
        """Extract tables from PDF page."""
        # This would use a table detection algorithm
        # For now, return empty list
        return []
        
    def make_pdf_searchable(
        self,
        pdf_engine,
        output_path: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ):
        """Create a searchable PDF with OCR text layer."""
        if not self.is_available():
            raise RuntimeError("OCR engine not available")
            
        # Create new PDF with OCR layer
        import fitz
        
        new_doc = fitz.open()
        
        for i in range(pdf_engine.page_count):
            page = pdf_engine.get_page(i)
            if page:
                # Get original page
                orig_page = page.fitz_page
                
                # Create new page with same dimensions
                new_page = new_doc.new_page(
                    width=orig_page.rect.width,
                    height=orig_page.rect.height
                )
                
                # Render original page as image
                pix = orig_page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Insert image
                new_page.insert_image(new_page.rect, stream=img_data)
                
                # Extract OCR text with positions
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                if self._tesseract_available:
                    import pytesseract
                    
                    # Get OCR data with positions
                    data = pytesseract.image_to_data(
                        img,
                        lang=self._language,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Add text layer
                    n_boxes = len(data['text'])
                    for j in range(n_boxes):
                        if int(data['conf'][j]) > 30:  # Minimum confidence
                            text = data['text'][j].strip()
                            if text:
                                x = data['left'][j]
                                y = data['top'][j]
                                
                                # Scale coordinates to PDF
                                scale_x = orig_page.rect.width / pix.width
                                scale_y = orig_page.rect.height / pix.height
                                
                                pdf_x = x * scale_x
                                pdf_y = y * scale_y
                                
                                # Insert invisible text
                                new_page.insert_text(
                                    (pdf_x, pdf_y),
                                    text,
                                    fontsize=8,
                                    color=(0, 0, 0),
                                    overlay=True
                                )
                                
            if progress_callback:
                progress = int((i + 1) / pdf_engine.page_count * 100)
                progress_callback(progress)
                
        # Save searchable PDF
        new_doc.save(output_path)
        new_doc.close()
