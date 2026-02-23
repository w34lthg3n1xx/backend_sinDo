"""
Image Processing - Optional OCR for Scanned Documents
"""

import base64
import io
from typing import Optional
from pathlib import Path

class ImageProcessor:
    """Handle image extraction and optional OCR"""
    
    def __init__(self, enable_ocr: bool = False):
        """
        Initialize image processor
        
        Args:
            enable_ocr: Whether to enable OCR (requires pytesseract + Tesseract binary)
        """
        self.enable_ocr = enable_ocr
        if enable_ocr:
            try:
                import pytesseract
                self.pytesseract = pytesseract
            except ImportError:
                self.enable_ocr = False
    
    def extract_text_from_image(self, file_path: str) -> str:
        """
        Extract text from image using OCR (optional)
        
        For MVP: Simply return placeholder; Gemini handles multimodal natively
        
        Args:
            file_path: Path to image file
        
        Returns:
            Extracted text (or filename if OCR disabled)
        """
        
        try:
            # Get file info
            filename = Path(file_path).name
            file_size = Path(file_path).stat().st_size / 1024  # KB
            
            if not self.enable_ocr:
                # Simple approach: Let Gemini handle the image directly
                # Return metadata for logging purposes
                return f"[Image uploaded: {filename} ({file_size:.1f}KB)]"
            
            # OCR approach (optional, not recommended for MVP)
            from PIL import Image
            
            image = Image.open(file_path)
            text = self.pytesseract.image_to_string(image, lang='fra+eng')
            
            return text if text.strip() else f"[Image: {filename}]"
        
        except Exception as e:
            # Graceful fallback
            return f"[Image extraction failed: {str(e)[:50]}]"
    
    def convert_image_to_base64(self, file_path: str) -> str:
        """
        Convert image to base64 for Gemini multimodal API
        
        Args:
            file_path: Path to image file
        
        Returns:
            Base64 encoded image string
        """
        
        try:
            with open(file_path, "rb") as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            return ""
    
    def get_mime_type_from_file(self, file_path: str) -> Optional[str]:
        """Determine MIME type from file extension"""
        
        ext = Path(file_path).suffix.lower()
        mime_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif',
        }
        return mime_map.get(ext)
    
    def validate_image_dimensions(self, file_path: str, max_width: int = 4096, max_height: int = 4096) -> bool:
        """
        Validate image dimensions (Gemini has limits)
        
        Args:
            file_path: Path to image
            max_width: Maximum allowed width
            max_height: Maximum allowed height
        
        Returns:
            True if valid, False otherwise
        """
        
        try:
            from PIL import Image
            image = Image.open(file_path)
            width, height = image.size
            
            if width > max_width or height > max_height:
                return False
            
            return True
        except Exception:
            return False