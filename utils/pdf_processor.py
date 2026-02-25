import fitz  # pip install pymupdf

def extract_text_from_pdf(file_path: str) -> str:
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        
        # Un code numérique fait souvent entre 100k et 300k caractères.
        # On garde une marge de sécurité raisonnable.
        print(text[:500])
        return text[:1000000] 
    
    except Exception as e:
        print(f"Erreur d'extraction : {e}")
        return ""

# """
# PDF Text Extraction
# """

# import pypdf
# from typing import Optional

# def extract_text_from_pdf(file_path: str) -> str:
#     """
#     Extract text from PDF file
    
#     Args:
#         file_path: Path to temporary PDF file
    
#     Returns:
#         Extracted text (truncated if too long)
#     """
    
#     try:
#         text = ""
#         with open(file_path, "rb") as f:
#             reader = pypdf.PdfReader(f)
            
#             num_pages = len(reader.pages)
            
#             for page_num in range(num_pages):
#                 page = reader.pages[page_num]
#                 text += page.extract_text() + "\n"
        
#         return text[:3000]  # Truncate to 3000 chars
    
#     except Exception as e:
#         return f"[Error extracting PDF: {str(e)[:100]}]"