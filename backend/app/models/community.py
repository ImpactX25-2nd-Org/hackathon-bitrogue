"""
Community models for posts and comments
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import uuid4


class PostCreate(BaseModel):
    """Model for creating a community post"""
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    crop_name: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    language: str = Field(default="en")
    scan_id: Optional[str] = None


class PostInDB(BaseModel):
    """Community post model as stored in database"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    title: str
    description: str
    crop_name: Optional[str] = None
    image_url: Optional[str] = None
    scan_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_resolved: bool = False
    accepted_response_id: Optional[str] = None
    view_count: int = 0
    response_count: int = 0
    helpful_count: int = 0
    language: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "post_123",
                "user_id": "user_123",
                "title": "Yellowing leaves on tomato plants",
                "description": "My tomato plants are showing yellow leaves...",
                "crop_name": "Tomato",
                "tags": ["disease", "tomato"],
                "is_resolved": False
            }
        }


class PostResponse(BaseModel):
    """Post response model with user info"""
    id: str
    user_id: str
    farmer_name: Optional[str] = None
    farmer_avatar: Optional[str] = None
    trust_score: Optional[float] = None
    title: str
    description: str
    crop_name: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    is_resolved: bool
    response_count: int
    view_count: int
    helpful_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    """Model for creating a comment on a post"""
    content: str = Field(..., min_length=1)
    is_expert_advice: bool = False


class CommentInDB(BaseModel):
    """Comment model as stored in database"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    post_id: str
    user_id: str
    content: str
    is_verified: bool = False
    verification_reason: Optional[str] = None
    verification_confidence: Optional[float] = Field(None, ge=0, le=1)
    helpful_count: int = 0
    is_expert_advice: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CommentResponse(BaseModel):
    """Comment response model with user info"""
    id: str
    post_id: str
    user_id: str
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    trust_score: Optional[float] = None
    content: str
    is_verified: bool
    verification_reason: Optional[str] = None
    helpful_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
