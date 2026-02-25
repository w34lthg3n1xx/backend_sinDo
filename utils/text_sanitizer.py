"""
Input Validation & Prompt Injection Prevention
"""

import re
from typing import Optional
from config import PROMPT_INJECTION_KEYWORDS, MAX_TEXT_LENGTH

def sanitize_and_validate_text(user_input: Optional[str]) -> str:
    """
    Sanitize user input and prevent prompt injection
    
    Args:
        user_input: Raw user text
    
    Returns:
        Sanitized text
    """
    
    if not user_input:
        return ""
    
    # Strip whitespace
    text = user_input.strip()
    
    # Check length
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
    
    # Check for prompt injection keywords
    text_lower = text.lower()
    for keyword in PROMPT_INJECTION_KEYWORDS:
        if keyword in text_lower:
            # Replace with neutral marker
            text = text.replace(keyword, "[REDACTED]")
        text = re.sub(r'(system\s*:|ignore|bypass|forget|override)', '[REDACTED]', text, flags=re.IGNORECASE)
    
    # Remove multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def validate_url(url: Optional[str]) -> bool:
    """Basic URL validation"""
    if not url:
        return False
    
    return url.startswith(("http://", "https://")) and len(url) < 500