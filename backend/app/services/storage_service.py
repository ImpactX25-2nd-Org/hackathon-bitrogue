"""
File storage service for handling image and file uploads
"""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from app.config import settings

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE


async def save_upload_file(file: UploadFile, folder: str = "scans") -> str:
    """
    Save an uploaded file to disk
    
    Args:
        file: Uploaded file
        folder: Subfolder to save file in (scans, posts, avatars)
        
    Returns:
        Relative file path
        
    Raises:
        HTTPException: If file type or size is invalid
    """
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_FOLDER) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Full file path
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            
            # Check file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / 1024 / 1024}MB"
                )
            
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Return relative path
    return f"/uploads/{folder}/{unique_filename}"


async def delete_file(file_path: str) -> bool:
    """
    Delete a file from disk
    
    Args:
        file_path: Relative file path (e.g., /uploads/scans/file.jpg)
        
    Returns:
        True if deleted, False if file not found
    """
    try:
        # Convert relative path to absolute
        full_path = Path(settings.UPLOAD_FOLDER).parent / file_path.lstrip('/')
        
        if full_path.exists():
            os.remove(full_path)
            return True
        return False
    except Exception:
        return False


def get_file_url(file_path: str, base_url: str = "http://localhost:8000") -> str:
    """
    Get full URL for a file
    
    Args:
        file_path: Relative file path
        base_url: Base URL of the server
        
    Returns:
        Full URL to the file
    """
    if file_path.startswith('http'):
        return file_path
    
    return f"{base_url}{file_path}"
