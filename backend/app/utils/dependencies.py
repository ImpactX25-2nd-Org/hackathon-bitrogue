"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.utils.security import decode_access_token
from app.database import get_database
from app.models.user import UserInDB
from motor.motor_asyncio import AsyncIOMotorDatabase

# Security scheme for JWT bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> UserInDB:
    """
    Dependency to get the current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user_dict = await db.users.find_one({"id": user_id})
    
    if user_dict is None:
        raise credentials_exception
    
    # Check if user is active
    user = UserInDB(**user_dict)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Dependency to ensure the current user is active
    (Alias for get_current_user, can be extended with additional checks)
    """
    return current_user


async def require_admin(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Dependency to require admin role
    
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Optional[UserInDB]:
    """
    Dependency for optional authentication
    Returns user if valid token provided, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if payload is None:
            return None
        
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        
        user_dict = await db.users.find_one({"id": user_id})
        if user_dict is None:
            return None
        
        return UserInDB(**user_dict)
    except Exception:
        return None
