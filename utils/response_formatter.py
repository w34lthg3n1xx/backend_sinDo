"""
Response Formatting - Parse & Structure Gemini Output
Ensures responses match AnalysisResponse model
"""

import json
import re
from typing import Dict, Any

from api.models import AnalysisResponse
from config import LEGAL_DISCLAIMER

def format_response(gemini_response: str) -> AnalysisResponse:
    """
    Parse Gemini response and ensure it matches AnalysisResponse model
    
    Args:
        gemini_response: Raw response from Gemini API
    
    Returns:
        AnalysisResponse validated Pydantic model
    
    Raises:
        ValueError: If response cannot be parsed
    """
    
    try:
        # Try to parse as JSON
        response_data = json.loads(gemini_response)
        
        # Validate and clean required fields
        response_data = _validate_response_fields(response_data)
        
        # Create AnalysisResponse model (validates schema)
        return AnalysisResponse(**response_data)
    
    except json.JSONDecodeError:
        # Fallback: parse as text and extract sections
        return _parse_text_response(gemini_response)
    
    except Exception as e:
        # Last resort: return generic error response
        return AnalysisResponse(
            qualification="Unable to analyze request",
            applicable_articles=[],
            risks="System error occurred during analysis",
            advice="Please try again with a clearer query",
            disclaimer=LEGAL_DISCLAIMER
        )


def _validate_response_fields(response_data: dict) -> dict:
    """
    Validate and normalize response fields
    
    Args:
        response_data: Parsed JSON response from Gemini
    
    Returns:
        Cleaned response dictionary
    """
    
    # Ensure all required fields exist
    required_fields = {
        "qualification": "",
        "applicable_articles": [],
        "risks": "",
        "advice": "",
        "disclaimer": LEGAL_DISCLAIMER
    }
    
    for field, default_value in required_fields.items():
        if field not in response_data or response_data[field] is None:
            response_data[field] = default_value
    
    # Validate field types
    if not isinstance(response_data.get("qualification"), str):
        response_data["qualification"] = str(response_data.get("qualification", ""))
    
    if not isinstance(response_data.get("applicable_articles"), list):
        articles = response_data.get("applicable_articles", [])
        if isinstance(articles, str):
            # Try to parse comma-separated or newline-separated articles
            response_data["applicable_articles"] = [
                a.strip() for a in re.split(r'[,\n]', articles) if a.strip()
            ]
        else:
            response_data["applicable_articles"] = []
    
    if not isinstance(response_data.get("risks"), str):
        response_data["risks"] = str(response_data.get("risks", ""))
    
    if not isinstance(response_data.get("advice"), str):
        response_data["advice"] = str(response_data.get("advice", ""))
    
    # Always override disclaimer with canonical one
    response_data["disclaimer"] = LEGAL_DISCLAIMER
    
    return response_data


def _parse_text_response(text: str) -> AnalysisResponse:
    """
    Fallback: parse unstructured text response
    
    Args:
        text: Raw text response from Gemini
    
    Returns:
        AnalysisResponse with extracted sections
    """
    
    sections = {
        "qualification": _extract_section(text, "qualification"),
        "applicable_articles": _extract_articles(text),
        "risks": _extract_section(text, "risks"),
        "advice": _extract_section(text, "advice"),
        "disclaimer": LEGAL_DISCLAIMER
    }
    
    return AnalysisResponse(**sections)


def _extract_section(text: str, section_name: str) -> str:
    """
    Extract section from unstructured text
    
    Args:
        text: Full text
        section_name: Section to extract
    
    Returns:
        Extracted text or empty string
    """
    
    try:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if section_name.lower() in line.lower():
                # Get next 2-3 lines as content
                content = '\n'.join(lines[i+1:min(i+4, len(lines))])
                return content.strip()
        return ""
    except Exception:
        return ""


def _extract_articles(text: str) -> list:
    """
    Extract article references from text
    
    Args:
        text: Full response text
    
    Returns:
        List of article references
    """
    
    try:
        # Match patterns like "Article 12", "Loi 2023-X", "Décret..."
        patterns = [
            r'(Article\s+\d+[A-Za-z]?(?:\s*-\s*[^,\n]*)?)',
            r'(Loi\s+\d{4}-\d+)',
            r'(Décret\s+\d{4}-\d+)',
            r'(Code\s+[A-Za-z]+)',
        ]
        
        articles = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            articles.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_articles = []
        for article in articles:
            if article.strip() not in seen:
                seen.add(article.strip())
                unique_articles.append(article.strip())
        
        return unique_articles[:10]  # Limit to 10 articles
    
    except Exception:
        return []