import fitz
import re
from collections import Counter

def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        full_text = []

        for page in doc:
            blocks = page.get_text("blocks")
            page_height = page.rect.height

            for block in blocks:
                x0, y0, x1, y1, text, *_ = block

                # Supprimer header (haut 10%) et footer (bas 10%)
                if y0 < page_height * 0.1:
                    continue
                if y1 > page_height * 0.9:
                    continue

                clean_block = text.strip()
                if clean_block:
                    full_text.append(clean_block)

        text = "\n".join(full_text)

        # ------------------------
        # SUPPRESSION SOMMAIRE
        # ------------------------

        # Supprimer lignes avec trop de points (typique sommaire)
        text = re.sub(r'^.*\.{3,}.*$', '', text, flags=re.MULTILINE)

        # Supprimer lignes contenant "Sommaire" ou "Table des matières"
        text = re.sub(r'(?i)^.*(sommaire|table des matières).*$',
                    '', text, flags=re.MULTILINE)

        # ------------------------
        # SUPPRESSION NUMÉROS DE PAGE
        # ------------------------

        # Lignes avec seulement un nombre
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

        # ------------------------
        # NETTOYAGE GÉNÉRAL
        # ------------------------

        # Supprimer multiples lignes vides
        text = re.sub(r'\n\s*\n+', '\n\n', text)

        # Supprimer espaces multiples
        text = re.sub(r'[ \t]+', ' ', text)

        # Supprimer lignes très courtes inutiles (< 3 caractères)
        text = "\n".join(
            line for line in text.split("\n")
            if len(line.strip()) > 2
        )

        return text[:1000000]

    except Exception as e:
        print(f"Erreur : {e}")
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