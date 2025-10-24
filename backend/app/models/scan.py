"""
Scan model for disease detection
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from uuid import uuid4


class ScanCreate(BaseModel):
    """Model for creating a new scan"""
    crop_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    language: str = Field(default="en")
    

class ScanInDB(BaseModel):
    """Scan model as stored in database"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    crop_name: str
    description: str
    image_url: str
    voice_file_url: Optional[str] = None
    transcription: Optional[str] = None
    translation: Optional[str] = None
    status: Literal["processing", "completed", "failed"] = "processing"
    disease_name: Optional[str] = None
    reliability: Optional[float] = Field(None, ge=0, le=100)
    next_steps: List[str] = Field(default_factory=list)
    is_common: bool = False
    language: str = "en"
    ml_model_version: Optional[str] = None
    processing_time_seconds: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "scan_123",
                "user_id": "user_123",
                "crop_name": "Tomato",
                "description": "Yellow spots on leaves",
                "image_url": "/uploads/scan_123.jpg",
                "status": "completed",
                "disease_name": "Early Blight",
                "reliability": 92.5,
                "is_common": True
            }
        }


class ScanResponse(BaseModel):
    """Scan response model"""
    id: str
    user_id: str
    crop_name: str
    description: str
    image_url: str
    voice_file_url: Optional[str] = None
    status: str
    disease_name: Optional[str] = None
    reliability: Optional[float] = None
    next_steps: List[str] = []
    is_common: bool = False
    language: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DetectionResult(BaseModel):
    """Disease detection result response"""
    scanId: str
    status: str
    diseaseName: Optional[str] = None
    reliability: Optional[float] = None
    nextSteps: List[str] = []
    isCommon: bool = False
    imageUrl: str
    cropName: str
    description: str
    communityAdvice: List[dict] = []
