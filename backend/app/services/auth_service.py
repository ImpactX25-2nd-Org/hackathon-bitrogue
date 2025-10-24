"""
Authentication service for user registration and login
"""
from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserCreate, UserLogin, UserInDB, Token, UserResponse
from app.utils.security import verify_password, get_password_hash, create_access_token
from fastapi import HTTPException, status


async def register_user(user_data: UserCreate, db: AsyncIOMotorDatabase) -> UserResponse:
    """
    Register a new user
    
    Args:
        user_data: User registration data
        db: Database instance
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user_data.email},
            {"phone": user_data.phone} if user_data.phone else {"email": user_data.email}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    
    # Create new user
    user_in_db = UserInDB(
        **user_data.model_dump(exclude={"password"}),
        password_hash=get_password_hash(user_data.password)
    )
    
    # Insert into database
    await db.users.insert_one(user_in_db.model_dump())
    
    return UserResponse(**user_in_db.model_dump())


async def authenticate_user(
    login_data: UserLogin, 
    db: AsyncIOMotorDatabase
) -> tuple[UserInDB, Token]:
    """
    Authenticate user and return user data with token
    
    Args:
        login_data: Login credentials
        db: Database instance
        
    Returns:
        Tuple of (user, token)
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email or phone
    user_dict = await db.users.find_one({
        "$or": [
            {"email": login_data.identifier},
            {"phone": login_data.identifier}
        ]
    })
    
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = UserInDB(**user_dict)
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login time
    await db.users.update_one(
        {"id": user.id},
        {"$set": {"last_login_at": datetime.utcnow()}}
    )
    
    # Create access token
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email}
    )
    
    token = Token(access_token=access_token)
    
    return user, token


async def get_user_by_id(user_id: str, db: AsyncIOMotorDatabase) -> Optional[UserInDB]:
    """
    Get user by ID
    
    Args:
        user_id: User ID
        db: Database instance
        
    Returns:
        User data or None if not found
    """
    user_dict = await db.users.find_one({"id": user_id})
    
    if user_dict:
        return UserInDB(**user_dict)
    
    return None
