"""
User model for authentication and user management
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    language: str = Field(default="en", pattern="^(en|ta|mr|kn|hi|te)$")
    role: Literal["farmer", "expert", "extension_worker", "admin"] = "farmer"


class UserCreate(UserBase):
    """Model for user registration"""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Model for user login"""
    identifier: str = Field(..., description="Email or phone number")
    password: str
    language: Optional[str] = "en"


class UserInDB(UserBase):
    """User model as stored in database"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    password_hash: str
    trust_score: float = Field(default=50.0, ge=0, le=100)
    avatar_url: Optional[str] = None
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "farmer@example.com",
                "name": "Ramesh Kumar",
                "phone": "9876543210",
                "language": "en",
                "role": "farmer",
                "trust_score": 75.0,
                "is_active": True
            }
        }


class UserResponse(BaseModel):
    """User response model (excludes password_hash)"""
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    language: str
    role: str
    trust_score: float
    avatar_url: Optional[str] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Model for updating user profile"""
    name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    avatar_url: Optional[str] = None


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
