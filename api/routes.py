"""
API Routes - /analyze endpoint with proper request/response models
"""

import tempfile
import os
import gc
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from api.models import AnalysisRequest, AnalysisResponse
from services.gemini_service import GeminiService
from services.legal_context_loader import LegalContextLoader
from services.prompt_builder import PromptBuilder
from utils.pdf_processor import extract_text_from_pdf
from utils.image_processor import ImageProcessor
from utils.text_sanitizer import sanitize_and_validate_text
from utils.response_formatter import format_response
from utils.file_cleanup import cleanup_temp_file, secure_delete_file
from config import (
    MAX_FILE_SIZE_MB,
    ALLOWED_FILE_TYPES,
)

router = APIRouter()

gemini_service = GeminiService()
legal_loader = LegalContextLoader()
prompt_builder = PromptBuilder()
image_processor = ImageProcessor(enable_ocr=False)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
) -> AnalysisResponse:
    """
    Main analysis endpoint - Legal assistant
    
    Accept:
    - text: User query (max 3000 chars)
    - file: PDF or image (max 5MB)
    - video_url: URL to analyze (max 500 chars)
    
    Returns: AnalysisResponse (Pydantic model serialized to JSON)
    
    Example:
        curl -X POST http://localhost:8000/api/analyze \\
        -F "text=Is posting someone's private photo illegal?"
    """
    
    temp_files = []  
    
    try:
        if not text and not file and not video_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide at least one of: text, file, or video_url"
            )
        
        try:
            request_data = AnalysisRequest(text=text, video_url=video_url)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        extracted_text = ""
        if request_data.text:
            extracted_text = sanitize_and_validate_text(request_data.text)
        
        if file:
            if file.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file.content_type}.\nAllowed: {list(ALLOWED_FILE_TYPES.keys())}"
                )
            
            file_content = await file.read()
            file_size_mb = len(file_content) / (1024 * 1024)
            
            if file_size_mb > MAX_FILE_SIZE_MB:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit"
                )
            
            suffix = ALLOWED_FILE_TYPES.get(file.content_type, ".tmp")
            temp_file_path = tempfile.mkstemp(suffix=suffix)
            temp_files.append(temp_file_path)
            
            with open(temp_file_path, "wb") as f:
                f.write(file_content)
            
            if file.content_type == "application/pdf":
                extracted_text += "\n[PDF Document Content]:\n"
                extracted_text += extract_text_from_pdf(temp_file_path)
            
            elif file.content_type.startswith("image/"):
                extracted_text += f"\n[Image Document: {file.filename}]"
        
        if request_data.video_url:
            extracted_text += f"\n[Video URL for Analysis]: {request_data.video_url}"
        
        if len(extracted_text) > 3000:
            extracted_text = extracted_text[:3000] + "...[truncated]"
        
        legal_context = legal_loader.load_relevant_context(extracted_text)
        
        system_prompt = prompt_builder.build_system_prompt(legal_context)
        user_message = prompt_builder.build_user_message(extracted_text)
        
        gemini_response = await gemini_service.analyze(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        response: AnalysisResponse = format_response(gemini_response)
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        # return AnalysisResponse(
        #     qualification="Analysis Error",
        #     applicable_articles=[],
        #     risks="The system encountered an error during analysis",
        #     advice="Please try again with a different query",
        #     disclaimer="This is general information only"
        # )
        print("ERROR:", e)
        raise e
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                secure_delete_file(temp_file)
        
        gc.collect()