"""
Suggestion models for community suggestions
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4


class SuggestionCreate(BaseModel):
    """Model for creating a suggestion"""
    disease_name: str = Field(..., min_length=1, max_length=255)
    text: str = Field(..., min_length=1)
    details: Optional[str] = None


class SuggestionInDB(BaseModel):
    """Suggestion model as stored in database"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    disease_name: str
    user_id: str
    text: str
    details: Optional[str] = None
    usefulness_score: float = Field(default=50.0, ge=0, le=100)
    usage_count: int = 0
    positive_feedback_count: int = 0
    negative_feedback_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SuggestionResponse(BaseModel):
    """Suggestion response with author info"""
    id: str
    text: str
    author: dict
    usefulness: float
    details: Optional[str] = None
    
    class Config:
        from_attributes = True


class TrustFeedback(BaseModel):
    """Model for trust score feedback"""
    suggestion_id: str
    score: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None
    scan_id: Optional[str] = None


class TrustFeedbackInDB(BaseModel):
    """Trust feedback as stored in database"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    suggestion_id: str
    user_id: str
    farmer_id: str
    score: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
    scan_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
