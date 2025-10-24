"""
Authentication routes for user registration and login
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import register_user, authenticate_user
from app.utils.dependencies import get_current_user
from app.models.user import UserInDB

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user
    
    - **email**: User's email address (unique)
    - **password**: User's password (min 6 characters)
    - **name**: User's full name
    - **phone**: Optional phone number
    - **language**: Preferred language (en, ta, mr, kn, hi, te)
    """
    user = await register_user(user_data, db)
    return {
        "success": True,
        "message": "User registered successfully",
        "data": {"user": user}
    }


@router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Login with email/phone and password
    
    - **identifier**: Email address or phone number
    - **password**: User's password
    - **language**: Optional language preference
    
    Returns JWT token and user data
    """
    user, token = await authenticate_user(login_data, db)
    
    return {
        "success": True,
        "token": token.access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "language": user.language,
            "trustScore": user.trust_score,
            "role": user.role
        }
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get current authenticated user's information
    
    Requires valid JWT token in Authorization header
    """
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "language": current_user.language,
            "trustScore": current_user.trust_score,
            "role": current_user.role,
            "avatar_url": current_user.avatar_url,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at.isoformat()
        }
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Refresh JWT token
    
    Requires valid JWT token in Authorization header
    Returns new token
    """
    from app.utils.security import create_access_token
    
    new_token = create_access_token(
        data={"user_id": current_user.id, "email": current_user.email}
    )
    
    return {
        "success": True,
        "token": new_token,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name
        }
    }
