"""Models package initialization"""
from app.models.user import (
    UserBase, UserCreate, UserLogin, UserInDB, UserResponse, 
    UserUpdate, Token, TokenData
)
from app.models.scan import ScanCreate, ScanInDB, ScanResponse, DetectionResult
from app.models.community import (
    PostCreate, PostInDB, PostResponse,
    CommentCreate, CommentInDB, CommentResponse
)
from app.models.suggestion import (
    SuggestionCreate, SuggestionInDB, SuggestionResponse,
    TrustFeedback, TrustFeedbackInDB
)
from app.models.notification import (
    NotificationCreate, NotificationInDB, NotificationResponse
)

__all__ = [
    # User models
    "UserBase", "UserCreate", "UserLogin", "UserInDB", "UserResponse",
    "UserUpdate", "Token", "TokenData",
    # Scan models
    "ScanCreate", "ScanInDB", "ScanResponse", "DetectionResult",
    # Community models
    "PostCreate", "PostInDB", "PostResponse",
    "CommentCreate", "CommentInDB", "CommentResponse",
    # Suggestion models
    "SuggestionCreate", "SuggestionInDB", "SuggestionResponse",
    "TrustFeedback", "TrustFeedbackInDB",
    # Notification models
    "NotificationCreate", "NotificationInDB", "NotificationResponse",
]
