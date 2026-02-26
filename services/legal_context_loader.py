"""
Legal Document Loader - Load from database/ folder
"""

import os
from config import DATABASE_PATH
from utils.pdf_processor import extract_text_from_pdf


class LegalContextLoader:
    """Load relevant legal texts from database/ folder"""
    
    def __init__(self):
        self.database_path = DATABASE_PATH
        self.documents = self._load_documents()
    
    def _load_documents(self) -> dict:
        """Load all legal documents from database/ on startup"""
        documents = {}
        
        if not os.path.exists(self.database_path):
            return documents
        
        for filename in os.listdir(self.database_path):
            if filename.endswith((".txt", ".md", ".pdf")):
                filepath = os.path.join(self.database_path, filename)
                try:
                    documents[filename] = extract_text_from_pdf(filepath)
                except Exception:
                    pass
        
        return documents
    
    def load_relevant_context(self, user_query: str) -> str: ##### Must be refined
        """
        Simple keyword matching to select relevant legal documents
        """
        
        keywords = {
            "cybercrime": ["codes_numeriques", "cybercriminalite"],
            "data": ["protection_donnees", "gdpr"],
            "social": ["reseaux_sociaux", "harcelement"],
            "privacy": ["vie_privee", "protection_donnees"],
            "identity": ["identite", "usurpation"],
        }
        
        relevant_docs = ""
        user_query_lower = user_query.lower()
        
        for doc_name, doc_content in self.documents.items():
            doc_name_lower = doc_name.lower()
            
            if any(term in doc_name_lower for term in ["numerique", "donnees", "TIC"]):
                relevant_docs += f"\n\n=== {doc_name} ===\n{doc_content[:2000]}"  ##### Why truncate to 2000?
        
        return relevant_docs if relevant_docs else self._default_context()
    
    def _default_context(self) -> str:
        """Default legal context if no specific documents loaded"""
        return """
Contexte juridique général:
- Respect des lois numériques nationales
- Protection des données personnelles
- Prévention de la cybercriminalité
- Conformité aux réglementations TIC
        """