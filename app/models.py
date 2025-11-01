from pydantic import BaseModel
from typing import Optional

class OCRRequest(BaseModel):
    """OCR request model"""
    language: Optional[str] = "eng"
    config: Optional[str] = "--psm 6"

class OCRResponse(BaseModel):
    """OCR response model"""
    text: str
    confidence: Optional[float] = None
    processing_time: Optional[float] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str