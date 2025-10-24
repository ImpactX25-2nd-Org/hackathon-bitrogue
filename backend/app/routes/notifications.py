"""
Notifications routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from app.database import get_database
from app.models.user import UserInDB
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=dict)
async def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get user's notifications
    
    - **unread_only**: Filter for unread notifications only
    - **limit**: Maximum number of notifications to return
    """
    try:
        query = {"user_id": current_user.id}
        
        if unread_only:
            query["is_read"] = False
        
        cursor = db.notifications.find(query).sort("created_at", -1).limit(limit)
        notifications = await cursor.to_list(length=limit)
        
        return {
            "success": True,
            "data": {"notifications": notifications}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@router.patch("/{notification_id}/read", response_model=dict)
async def mark_notification_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark a notification as read"""
    try:
        notification = await db.notifications.find_one({"id": notification_id})
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Check if user owns this notification
        if notification["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        await db.notifications.update_one(
            {"id": notification_id},
            {"$set": {"is_read": True}}
        )
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )


@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a notification"""
    try:
        notification = await db.notifications.find_one({"id": notification_id})
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Check if user owns this notification
        if notification["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        await db.notifications.delete_one({"id": notification_id})
        
        return {
            "success": True,
            "message": "Notification deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )
