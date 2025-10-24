"""
Notification models
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
from datetime import datetime
from uuid import uuid4


class NotificationCreate(BaseModel):
    """Model for creating a notification"""
    type: Literal["trust_score_followup", "post_response", "post_resolved", 
                  "scan_completed", "trending_alert", "system"]
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scheduled_for: Optional[datetime] = None


class NotificationInDB(BaseModel):
    """Notification model as stored in database"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    type: str
    title: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_read: bool = False
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationResponse(BaseModel):
    """Notification response model"""
    id: str
    type: str
    title: str
    message: str
    metadata: Dict[str, Any]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
