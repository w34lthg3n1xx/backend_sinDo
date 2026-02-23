"""
PDF Text Extraction
"""

import PyPDF2
from typing import Optional

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_path: Path to temporary PDF file
    
    Returns:
        Extracted text (truncated if too long)
    """
    
    try:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            
            # Limit to first 10 pages (avoid massive PDFs)
            num_pages = min(len(reader.pages), 10)
            
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
        
        return text[:3000]  # Truncate to 3000 chars
    
    except Exception as e:
        return f"[Error extracting PDF: {str(e)[:100]}]"