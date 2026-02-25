"""
Configuration - Legal Assistant Backend
"""

import os
from dotenv import load_dotenv
from typing import Optional, Set

# ===== GEMINI API CONFIGURATION =====
load_dotenv()
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable must be set")

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.2  # Low variance for consistency
GEMINI_MAX_TOKENS = 2000
GEMINI_TOP_P = 0.9

# ===== SECURITY & SIZE LIMITS =====
MAX_FILE_SIZE_MB = 5
MAX_TEXT_LENGTH = 3000
MAX_URL_LENGTH = 500
REQUEST_TIMEOUT_SECONDS = 30

# ===== ALLOWED MIME TYPES =====
ALLOWED_FILE_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

# ===== PROMPT INJECTION KEYWORDS (Simple Blocklist) =====
PROMPT_INJECTION_KEYWORDS: Set[str] = {
    "ignore", "bypass", "forget", "override", "system prompt",
    "instruction", "directive", "rule:", "new goal", "disregard",
    "disable", "turn off", "ignore all", "forget instructions",
    "act as", "pretend", "roleplay", "jailbreak", "exploit",
}

# ===== LEGAL DOCUMENT DATABASE PATH =====
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database")
if not os.path.exists(DATABASE_PATH):
    os.makedirs(DATABASE_PATH)

# ===== MANDATORY LEGAL DISCLAIMER =====
LEGAL_DISCLAIMER = (
    "⚠️ LEGAL DISCLAIMER: This response constitutes GENERAL LEGAL INFORMATION ONLY "
    "and is NOT personalized legal advice. It is provided by an automated system based on AI analysis. "
    "For critical legal matters, consult a qualified attorney in your jurisdiction. "
    "The application providers assume no liability for the accuracy or completeness of this information."
)

# ===== RATE LIMITING =====
RATE_LIMIT_REQUESTS_PER_MINUTE = 10
RATE_LIMIT_CLEANUP_INTERVAL_SECONDS = 60

# ===== SECURITY HEADERS =====
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}

# ===== ENVIRONMENT =====
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# ===== OCR SETTINGS =====
ENABLE_OCR = os.getenv("ENABLE_OCR", "false").lower() == "true"
OCR_MAX_CHARS = 5000  

# ===== GEMINI SAFETY SETTINGS =====
# GEMINI_SAFETY_SETTINGS = [
#     {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "threshold": "BLOCK_ALL"
#     },
#     {
#         "category": "HARM_CATEGORY_HARASSMENT",
#         "threshold": "BLOCK_ALL"
#     },
#     {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "threshold": "BLOCK_SOME"
#     },
#     {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "threshold": "BLOCK_SOME"
#     }
# ]