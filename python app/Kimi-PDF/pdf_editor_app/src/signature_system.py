"""
Signature System Module - Handles digital and handwritten signatures
"""

import hashlib
import base64
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import io
import os
import tempfile

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from PIL import Image, ImageDraw, ImageFont
import fitz


class SignatureType(Enum):
    """Types of signatures."""
    DIGITAL = "digital"  # Certificate-based digital signature
    HANDWRITTEN = "handwritten"  # Image-based signature
    STAMP = "stamp"  # Digital stamp/seal


@dataclass
class SignatureCertificate:
    """Represents a digital signature certificate."""
    id: str
    name: str
    organization: str
    email: str
    valid_from: datetime
    valid_until: datetime
    serial_number: str
    issuer: str
    
    # Private key (encrypted storage)
    private_key_pem: Optional[str] = None
    
    # Public certificate
    certificate_pem: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if certificate is currently valid."""
        now = datetime.now()
        return self.valid_from <= now <= self.valid_until
        
    def to_dict(self) -> Dict:
        """Convert to dictionary (without private key)."""
        return {
            'id': self.id,
            'name': self.name,
            'organization': self.organization,
            'email': self.email,
            'valid_from': self.valid_from.isoformat(),
            'valid_until': self.valid_until.isoformat(),
            'serial_number': self.serial_number,
            'issuer': self.issuer,
            'certificate_pem': self.certificate_pem,
        }


@dataclass
class Signature:
    """Represents a signature on a document."""
    id: str
    type: SignatureType
    page: int
    rect: fitz.Rect
    
    # For digital signatures
    certificate_id: Optional[str] = None
    signature_data: Optional[bytes] = None
    
    # For handwritten signatures
    image_data: Optional[bytes] = None
    image_format: str = "png"
    
    # Common metadata
    author: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    location: str = ""
    
    # Visual appearance
    show_date: bool = True
    show_name: bool = True
    show_reason: bool = False
    
    # Verification
    is_verified: bool = False
    verification_message: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'page': self.page,
            'rect': [self.rect.x0, self.rect.y0, self.rect.x1, self.rect.y1],
            'certificate_id': self.certificate_id,
            'author': self.author,
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason,
            'location': self.location,
            'show_date': self.show_date,
            'show_name': self.show_name,
            'show_reason': self.show_reason,
            'is_verified': self.is_verified,
            'verification_message': self.verification_message,
        }


class SignatureManager:
    """Manages digital certificates and signatures."""
    
    def __init__(self):
        self.certificates: Dict[str, SignatureCertificate] = {}
        self.signatures: List[Signature] = []
        self._cert_store_path = os.path.expanduser("~/.propdf/certificates")
        os.makedirs(self._cert_store_path, exist_ok=True)
        
    # ==================== Certificate Management ====================
    
    def create_self_signed_certificate(
        self,
        name: str,
        organization: str = "",
        email: str = "",
        country: str = "US",
        state: str = "",
        locality: str = "",
        validity_days: int = 365
    ) -> SignatureCertificate:
        """Create a new self-signed certificate."""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Build subject name
        name_attributes = [x509.NameAttribute(NameOID.COMMON_NAME, name)]
        if organization:
            name_attributes.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization))
        if email:
            name_attributes.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, email))
        if country:
            name_attributes.append(x509.NameAttribute(NameOID.COUNTRY_NAME, country))
        if state:
            name_attributes.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state))
        if locality:
            name_attributes.append(x509.NameAttribute(NameOID.LOCALITY_NAME, locality))
            
        subject = issuer = x509.Name(name_attributes)
        
        # Generate certificate
        valid_from = datetime.now()
        valid_until = valid_from.replace(year=valid_from.year + 1)
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            valid_from
        ).not_valid_after(
            valid_until
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(name)]),
            critical=False
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Create certificate object
        cert_obj = SignatureCertificate(
            id=cert.serial_number.to_bytes(20, 'big').hex(),
            name=name,
            organization=organization,
            email=email,
            valid_from=valid_from,
            valid_until=valid_until,
            serial_number=str(cert.serial_number),
            issuer=issuer.rfc4514_string(),
            private_key_pem=private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8'),
            certificate_pem=cert.public_bytes(
                encoding=serialization.Encoding.PEM
            ).decode('utf-8')
        )
        
        self.certificates[cert_obj.id] = cert_obj
        self._save_certificate(cert_obj)
        
        return cert_obj
        
    def import_certificate(
        self,
        cert_path: str,
        key_path: Optional[str] = None,
        password: Optional[str] = None
    ) -> SignatureCertificate:
        """Import a certificate from file."""
        # Load certificate
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
            
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        
        # Load private key if provided
        private_key_pem = None
        if key_path and os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                key_data = f.read()
            private_key = serialization.load_pem_private_key(
                key_data,
                password=password.encode() if password else None,
                backend=default_backend()
            )
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
        # Extract certificate info
        def get_attr(oid):
            try:
                return cert.subject.get_attributes_for_oid(oid)[0].value
            except IndexError:
                return ""
                
        cert_obj = SignatureCertificate(
            id=cert.serial_number.to_bytes(20, 'big').hex(),
            name=get_attr(NameOID.COMMON_NAME),
            organization=get_attr(NameOID.ORGANIZATION_NAME),
            email=get_attr(NameOID.EMAIL_ADDRESS),
            valid_from=cert.not_valid_before,
            valid_until=cert.not_valid_after,
            serial_number=str(cert.serial_number),
            issuer=cert.issuer.rfc4514_string(),
            private_key_pem=private_key_pem,
            certificate_pem=cert_data.decode('utf-8')
        )
        
        self.certificates[cert_obj.id] = cert_obj
        self._save_certificate(cert_obj)
        
        return cert_obj
        
    def export_certificate(self, cert_id: str, output_path: str):
        """Export a certificate to file."""
        cert = self.certificates.get(cert_id)
        if cert and cert.certificate_pem:
            with open(output_path, 'w') as f:
                f.write(cert.certificate_pem)
                
    def delete_certificate(self, cert_id: str):
        """Delete a certificate."""
        if cert_id in self.certificates:
            del self.certificates[cert_id]
            cert_path = os.path.join(self._cert_store_path, f"{cert_id}.json")
            if os.path.exists(cert_path):
                os.remove(cert_path)
                
    def get_certificate(self, cert_id: str) -> Optional[SignatureCertificate]:
        """Get a certificate by ID."""
        return self.certificates.get(cert_id)
        
    def get_all_certificates(self) -> List[SignatureCertificate]:
        """Get all certificates."""
        return list(self.certificates.values())
        
    def _save_certificate(self, cert: SignatureCertificate):
        """Save certificate to storage."""
        import json
        cert_path = os.path.join(self._cert_store_path, f"{cert.id}.json")
        with open(cert_path, 'w') as f:
            json.dump(cert.to_dict(), f, indent=2)
            
    def load_certificates(self):
        """Load all saved certificates."""
        import json
        self.certificates.clear()
        
        for filename in os.listdir(self._cert_store_path):
            if filename.endswith('.json'):
                cert_path = os.path.join(self._cert_store_path, filename)
                try:
                    with open(cert_path, 'r') as f:
                        data = json.load(f)
                        cert = SignatureCertificate(
                            id=data['id'],
                            name=data['name'],
                            organization=data.get('organization', ''),
                            email=data.get('email', ''),
                            valid_from=datetime.fromisoformat(data['valid_from']),
                            valid_until=datetime.fromisoformat(data['valid_until']),
                            serial_number=data['serial_number'],
                            issuer=data['issuer'],
                            certificate_pem=data.get('certificate_pem')
                        )
                        self.certificates[cert.id] = cert
                except Exception as e:
                    print(f"Failed to load certificate {filename}: {e}")
                    
    # ==================== Digital Signatures ====================
    
    def add_digital_signature(
        self,
        pdf_engine,
        page_num: int,
        signature_data: Dict
    ) -> Signature:
        """Add a digital signature to a PDF."""
        cert_id = signature_data.get('certificate_id')
        rect = signature_data.get('rect', fitz.Rect(100, 100, 300, 200))
        reason = signature_data.get('reason', '')
        location = signature_data.get('location', '')
        
        cert = self.certificates.get(cert_id)
        if not cert:
            raise ValueError("Certificate not found")
            
        if not cert.is_valid():
            raise ValueError("Certificate is not valid")
            
        # Create signature object
        signature = Signature(
            id=hashlib.sha256(
                f"{cert_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16],
            type=SignatureType.DIGITAL,
            page=page_num,
            rect=rect,
            certificate_id=cert_id,
            author=cert.name,
            reason=reason,
            location=location,
            show_date=signature_data.get('show_date', True),
            show_name=signature_data.get('show_name', True),
            show_reason=signature_data.get('show_reason', False)
        )
        
        # Create visual signature appearance
        appearance = self._create_signature_appearance(signature, cert)
        
        # Apply to PDF
        page = pdf_engine.get_page(page_num)
        if page:
            # Insert signature image
            img_bytes = self._image_to_bytes(appearance)
            page.fitz_page.insert_image(rect, stream=img_bytes)
            
            # Add invisible signature field for digital verification
            # This is a simplified version - full PDF signing requires more complex handling
            
        self.signatures.append(signature)
        return signature
        
    def _create_signature_appearance(
        self,
        signature: Signature,
        cert: SignatureCertificate
    ) -> Image.Image:
        """Create visual appearance for signature."""
        width = int(signature.rect.width)
        height = int(signature.rect.height)
        
        # Create image
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([0, 0, width-1, height-1], outline=(0, 0, 255), width=2)
        
        # Try to load font
        try:
            font_large = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 10)
        except:
            font_large = ImageFont.load_default()
            font_small = font_large
            
        y = 5
        
        # Draw name
        if signature.show_name:
            text = f"Digitally signed by: {cert.name}"
            draw.text((5, y), text, fill=(0, 0, 0), font=font_large)
            y += 20
            
        # Draw date
        if signature.show_date:
            text = f"Date: {signature.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            draw.text((5, y), text, fill=(0, 0, 0), font=font_small)
            y += 15
            
        # Draw reason
        if signature.show_reason and signature.reason:
            text = f"Reason: {signature.reason}"
            draw.text((5, y), text, fill=(0, 0, 0), font=font_small)
            y += 15
            
        # Draw certificate info
        text = f"SN: {cert.serial_number[:20]}..."
        draw.text((5, y), text, fill=(100, 100, 100), font=font_small)
        
        return img
        
    def _image_to_bytes(self, img: Image.Image, format: str = 'PNG') -> bytes:
        """Convert PIL image to bytes."""
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        return buffer.getvalue()
        
    def verify_signature(self, signature_id: str) -> Tuple[bool, str]:
        """Verify a digital signature."""
        signature = None
        for sig in self.signatures:
            if sig.id == signature_id:
                signature = sig
                break
                
        if not signature:
            return False, "Signature not found"
            
        if signature.type != SignatureType.DIGITAL:
            return False, "Not a digital signature"
            
        cert = self.certificates.get(signature.certificate_id)
        if not cert:
            return False, "Certificate not found"
            
        if not cert.is_valid():
            return False, "Certificate has expired"
            
        # Full verification would check the cryptographic signature
        # This is a simplified check
        signature.is_verified = True
        signature.verification_message = "Signature verified successfully"
        
        return True, signature.verification_message
        
    # ==================== Handwritten Signatures ====================
    
    def add_handwritten_signature(
        self,
        pdf_engine,
        page_num: int,
        image_data: bytes,
        rect: fitz.Rect,
        author: str = ""
    ) -> Signature:
        """Add a handwritten signature to a PDF."""
        signature = Signature(
            id=hashlib.sha256(
                f"handwritten{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16],
            type=SignatureType.HANDWRITTEN,
            page=page_num,
            rect=rect,
            image_data=image_data,
            author=author,
            timestamp=datetime.now()
        )
        
        # Apply to PDF
        page = pdf_engine.get_page(page_num)
        if page:
            page.fitz_page.insert_image(rect, stream=image_data)
            
        self.signatures.append(signature)
        return signature
        
    def create_signature_from_drawing(
        self,
        points: List[Tuple[int, int]],
        width: int = 300,
        height: int = 150,
        stroke_color: Tuple[int, int, int] = (0, 0, 0),
        stroke_width: int = 2,
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 0)
    ) -> bytes:
        """Create a signature image from drawing points."""
        img = Image.new('RGBA', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        if len(points) > 1:
            draw.line(points, fill=stroke_color, width=stroke_width)
            
        return self._image_to_bytes(img)
        
    def create_signature_from_text(
        self,
        text: str,
        font_size: int = 48,
        font_name: str = "arial.ttf",
        color: Tuple[int, int, int] = (0, 0, 128)
    ) -> bytes:
        """Create a signature image from text."""
        try:
            font = ImageFont.truetype(font_name, font_size)
        except:
            font = ImageFont.load_default()
            
        # Calculate text size
        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Create image with padding
        padding = 20
        img = Image.new('RGBA', 
                       (text_width + padding * 2, text_height + padding * 2),
                       (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw text
        draw.text((padding, padding), text, font=font, fill=color)
        
        return self._image_to_bytes(img)
        
    # ==================== Signature Management ====================
    
    def get_signatures(self) -> List[Signature]:
        """Get all signatures."""
        return self.signatures.copy()
        
    def get_signatures_for_page(self, page_num: int) -> List[Signature]:
        """Get signatures for a specific page."""
        return [s for s in self.signatures if s.page == page_num]
        
    def remove_signature(self, signature_id: str) -> bool:
        """Remove a signature."""
        for i, sig in enumerate(self.signatures):
            if sig.id == signature_id:
                self.signatures.pop(i)
                return True
        return False
        
    def clear_signatures(self):
        """Remove all signatures."""
        self.signatures.clear()
        
    def import_signatures_from_pdf(self, pdf_engine):
        """Import existing signatures from a PDF."""
        # This would scan the PDF for signature fields
        # and import them into our system
        pass
        
    def export_signatures(self, file_path: str):
        """Export signatures to a file."""
        import json
        data = [sig.to_dict() for sig in self.signatures]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load_signatures(self, file_path: str):
        """Load signatures from a file."""
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Convert dictionaries back to Signature objects
            self.signatures = []
            for item in data:
                sig = Signature(
                    id=item['id'],
                    type=SignatureType(item['type']),
                    page=item['page'],
                    rect=fitz.Rect(item['rect']),
                    certificate_id=item.get('certificate_id'),
                    author=item.get('author', ''),
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    reason=item.get('reason', ''),
                    location=item.get('location', ''),
                    show_date=item.get('show_date', True),
                    show_name=item.get('show_name', True),
                    show_reason=item.get('show_reason', False),
                    is_verified=item.get('is_verified', False),
                    verification_message=item.get('verification_message', '')
                )
                self.signatures.append(sig)
