"""
Pydantic Models - Request/Response Schemas
Properly validates all inputs
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator

class AnalysisRequest(BaseModel):
    """
    User analysis request - supports text, file, or video URL
    At least one field must be provided (enforced in route)
    """
    text: Optional[str] = Field(
        None,
        max_length=3000,
        description="User query or situation description"
    )
    video_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL of video to analyze"
    )
    
    @validator('text')
    def text_not_empty(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Text cannot be empty string')
        return v
    
    @validator('video_url')
    def url_format_valid(cls, v):
        if v is not None and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "I posted something on social media and someone said I defamed them. What are the legal risks?",
                "video_url": None
            }
        }


class AnalysisResponse(BaseModel):
    """
    Structured legal analysis response
    Returned as JSON to all clients
    """
    qualification: str = Field(
        ...,
        description="Legal qualification of situation (e.g., 'Cybercriminal activity', 'Data protection violation')"
    )
    applicable_articles: List[str] = Field(
        ...,
        description="List of relevant law articles (e.g., ['Article 12 - Code Pénal', 'Décret 2023-X'])"
    )
    risks: str = Field(
        ...,
        description="Potential legal consequences and risks"
    )
    advice: str = Field(
        ...,
        description="Prudent recommendations to avoid legal issues"
    )
    disclaimer: str = Field(
        ...,
        description="Mandatory legal disclaimer"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "qualification": "Potential defamation / atteinte à l'honneur",
                "applicable_articles": [
                    "Article 12 - Code Pénal",
                    "Loi sur la protection de la vie privée"
                ],
                "risks": "Civil liability for damages. Possible criminal prosecution.",
                "advice": "Seek legal counsel immediately. Document all evidence.",
                "disclaimer": "⚠️ This is general legal information only, not legal advice."
            }
        }