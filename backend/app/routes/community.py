"""
Community routes for posts and comments
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime
from app.database import get_database
from app.models.user import UserInDB
from app.models.community import PostCreate, PostInDB, CommentCreate, CommentInDB
from app.utils.dependencies import get_current_user, optional_user
from app.services.storage_service import save_upload_file
from app.services.trust_score import TrustScoreCalculator

router = APIRouter(prefix="/community", tags=["Community"])


@router.post("/posts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    description: str = Form(...),
    crop_name: Optional[str] = Form(None),
    tags: str = Form(""),
    language: str = Form("en"),
    scan_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new community post
    
    - **title**: Post title
    - **description**: Detailed description
    - **crop_name**: Optional crop name
    - **tags**: Comma-separated tags
    - **language**: Language code
    - **scan_id**: Optional scan ID if sharing from detection
    - **image**: Optional image upload
    """
    try:
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Save image if provided
        image_url = None
        if image:
            image_url = await save_upload_file(image, folder="posts")
        
        # Create post
        post = PostInDB(
            user_id=current_user.id,
            title=title,
            description=description,
            crop_name=crop_name,
            tags=tag_list,
            language=language,
            scan_id=scan_id,
            image_url=image_url
        )
        
        await db.community_posts.insert_one(post.model_dump())
        
        return {
            "success": True,
            "data": {
                "postId": post.id,
                "post": post.model_dump()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


@router.get("/posts", response_model=dict)
async def get_posts(
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    crop_name: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: Optional[UserInDB] = Depends(optional_user)
):
    """
    Get community posts with filtering and pagination
    
    - **status_filter**: Filter by 'resolved' or 'unresolved'
    - **search**: Search in title and description
    - **crop_name**: Filter by crop name
    - **page**: Page number (1-indexed)
    - **limit**: Results per page
    """
    try:
        # Build query
        query = {}
        
        if status_filter == "resolved":
            query["is_resolved"] = True
        elif status_filter == "unresolved":
            query["is_resolved"] = False
        
        if crop_name:
            query["crop_name"] = {"$regex": crop_name, "$options": "i"}
        
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get total count
        total = await db.community_posts.count_documents(query)
        
        # Get posts
        cursor = db.community_posts.find(query).sort("created_at", -1).skip(skip).limit(limit)
        posts = await cursor.to_list(length=limit)
        
        # Enrich posts with user data
        enriched_posts = []
        for post in posts:
            user = await db.users.find_one({"id": post["user_id"]})
            if user:
                post["farmer_name"] = user.get("name")
                post["farmer_avatar"] = user.get("avatar_url")
                post["trust_score"] = user.get("trust_score", 50.0)
            enriched_posts.append(post)
        
        return {
            "success": True,
            "data": {
                "posts": enriched_posts,
                "totalCount": total,
                "page": page,
                "hasMore": skip + limit < total
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch posts: {str(e)}"
        )


@router.get("/posts/{post_id}", response_model=dict)
async def get_post_details(
    post_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get detailed information about a specific post including comments"""
    try:
        post = await db.community_posts.find_one({"id": post_id})
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Increment view count
        await db.community_posts.update_one(
            {"id": post_id},
            {"$inc": {"view_count": 1}}
        )
        
        # Get user data
        user = await db.users.find_one({"id": post["user_id"]})
        if user:
            post["farmer_name"] = user.get("name")
            post["farmer_avatar"] = user.get("avatar_url")
            post["trust_score"] = user.get("trust_score", 50.0)
        
        # Get comments
        cursor = db.post_comments.find({"post_id": post_id}).sort("created_at", -1)
        comments = await cursor.to_list(length=None)
        
        # Enrich comments with user data
        enriched_comments = []
        for comment in comments:
            comment_user = await db.users.find_one({"id": comment["user_id"]})
            if comment_user:
                comment["author_name"] = comment_user.get("name")
                comment["author_avatar"] = comment_user.get("avatar_url")
                comment["trust_score"] = comment_user.get("trust_score", 50.0)
            enriched_comments.append(comment)
        
        return {
            "success": True,
            "data": {
                "post": post,
                "responses": enriched_comments
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch post: {str(e)}"
        )


@router.post("/posts/{post_id}/respond", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add a response/comment to a post"""
    try:
        # Check if post exists
        post = await db.community_posts.find_one({"id": post_id})
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Create comment
        comment = CommentInDB(
            post_id=post_id,
            user_id=current_user.id,
            content=comment_data.content,
            is_expert_advice=comment_data.is_expert_advice,
            is_verified=False  # TODO: Run AI verification
        )
        
        await db.post_comments.insert_one(comment.model_dump())
        
        # Update post response count
        await db.community_posts.update_one(
            {"id": post_id},
            {"$inc": {"response_count": 1}}
        )
        
        return {
            "success": True,
            "data": {
                "responseId": comment.id,
                "aiVerification": {
                    "isVerified": False,
                    "confidence": 0.0,
                    "reason": "AI verification pending"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}"
        )


@router.post("/posts/{post_id}/resolve", response_model=dict)
async def resolve_post(
    post_id: str,
    accepted_response_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark a post as resolved with an accepted response"""
    try:
        post = await db.community_posts.find_one({"id": post_id})
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if user owns the post
        if post["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only post owner can mark as resolved"
            )
        
        # Verify response exists
        response = await db.post_comments.find_one({"id": accepted_response_id, "post_id": post_id})
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found"
            )
        
        # Update post
        await db.community_posts.update_one(
            {"id": post_id},
            {
                "$set": {
                    "is_resolved": True,
                    "accepted_response_id": accepted_response_id,
                    "resolved_at": datetime.utcnow()
                }
            }
        )
        
        # Update trust score of responder
        responder_id = response["user_id"]
        await TrustScoreCalculator.increment_score(responder_id, "accepted_response", db)
        
        return {
            "success": True,
            "message": "Post marked as resolved",
            "trustScoreUpdated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve post: {str(e)}"
        )
