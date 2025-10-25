"""
Scan routes for disease detection
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime
import logging
from app.database import get_database
from app.models.user import UserInDB
from app.models.scan import ScanCreate, ScanInDB, ScanResponse, DetectionResult
from app.utils.dependencies import get_current_user
from app.services.storage_service import save_upload_file
from app.services.ml_service import get_ml_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scans", tags=["Disease Detection"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_scan(
    image: UploadFile = File(..., description="Crop image file"),
    crop_type: str = Form(..., description="Type of crop: chilli, groundnut, or rice"),
    description: Optional[str] = Form(None, description="Optional description"),
    language: str = Form("en"),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Upload crop image for disease detection using ML models
    
    - **image**: Crop image file (jpg, png, webp)
    - **crop_type**: Type of crop - must be one of: chilli, groundnut, rice
    - **description**: Optional description of the problem
    - **language**: Language code (en, ta, mr, kn, hi, te)
    
    Returns disease detection results with confidence scores
    """
    try:
        # Validate crop type
        crop_type = crop_type.lower()
        ml_service = get_ml_service()
        
        if crop_type not in ml_service.get_supported_crops():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid crop type: {crop_type}. "
                       f"Supported crops: {', '.join(ml_service.get_supported_crops())}"
            )
        
        # Check if model is loaded
        if not ml_service.is_model_loaded(crop_type):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Model for {crop_type} is not available. "
                       f"Please contact administrator."
            )
        
        # Save uploaded image
        logger.info(f"Saving uploaded image for {crop_type} scan...")
        image_url = await save_upload_file(image, folder="scans")
        # image_url already includes '/uploads/scans/filename.jpg'
        # Remove leading '/' and add './' for local file path
        image_path = f".{image_url}"
        
        # Run ML prediction
        logger.info(f"Running disease detection for {crop_type}...")
        try:
            prediction = await ml_service.predict(image_path, crop_type)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model inference failed: {str(e)}"
            )
        
        # Create scan record with ML results
        scan = ScanInDB(
            user_id=current_user.id,
            crop_name=crop_type.capitalize(),
            description=description or f"Disease detection for {crop_type}",
            image_url=image_url,
            language=language,
            status="completed",
            disease_name=prediction["disease"],
            reliability=prediction["confidence"],
            completed_at=datetime.utcnow()
        )
        
        # Insert into database
        scan_dict = scan.model_dump()
        scan_dict["all_predictions"] = prediction["all_predictions"]
        await db.scans.insert_one(scan_dict)
        
        logger.info(f"✓ Scan completed: {prediction['disease']} ({prediction['confidence']:.2f}%)")
        
        # Fetch high-trust community advice for this disease
        community_advice = []
        disease_name = prediction["disease"]
        
        # Find helpful advice from other farmers who dealt with same disease
        pipeline = [
            {
                "$match": {
                    "disease_name": disease_name,
                    "status": "completed"
                }
            },
            {
                "$lookup": {
                    "from": "comments",
                    "localField": "id",
                    "foreignField": "scan_id",
                    "as": "comments"
                }
            },
            {"$unwind": "$comments"},
            {
                "$match": {
                    "comments.helpful_count": {"$gte": 2}  # Lower threshold for initial scan
                }
            },
            {"$sort": {"comments.helpful_count": -1}},
            {"$limit": 3},  # Top 3 most helpful
            {
                "$project": {
                    "_id": 0,
                    "farmerName": "$comments.user_name",
                    "farmerLocation": "$comments.user_location",
                    "advice": "$comments.advice",
                    "helpfulCount": "$comments.helpful_count",
                    "timestamp": "$comments.created_at"
                }
            }
        ]
        
        try:
            cursor = db.scans.aggregate(pipeline)
            community_advice = await cursor.to_list(length=3)
            logger.info(f"Found {len(community_advice)} community solutions for {disease_name}")
        except Exception as e:
            logger.warning(f"Could not fetch community advice: {str(e)}")
        
        return {
            "success": True,
            "data": {
                "scan_id": scan.id,
                "crop_type": crop_type,
                "disease_detected": prediction["disease"],
                "confidence": prediction["confidence"],
                "all_predictions": prediction["all_predictions"],
                "image_url": f"/uploads/{image_url}",
                "timestamp": scan.created_at.isoformat(),
                "status": "completed",
                "community_advice": community_advice  # Add community solutions
            },
            "message": f"Disease detected: {prediction['disease']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating scan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scan: {str(e)}"
        )


@router.get("", response_model=dict)
async def get_user_scans(
    skip: int = 0,
    limit: int = 10,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get current user's scan history
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    try:
        # Get total count
        total = await db.scans.count_documents({"user_id": current_user.id})
        
        # Get scans
        cursor = db.scans.find({"user_id": current_user.id}).sort("created_at", -1).skip(skip).limit(limit)
        scans = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for scan in scans:
            if "_id" in scan:
                scan["_id"] = str(scan["_id"])
        
        return {
            "success": True,
            "data": {
                "scans": scans,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch scans: {str(e)}"
        )


@router.get("/{scan_id}", response_model=dict)
async def get_scan_details(
    scan_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed information about a specific scan with community advice for the detected disease
    
    - **scan_id**: Scan ID
    """
    try:
        scan = await db.scans.find_one({"id": scan_id})
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        # Check if user owns this scan
        if scan["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Fetch high-trust community advice for this disease
        community_advice = []
        disease_name = scan.get("disease_name")
        
        if disease_name:
            # Find other scans with the same disease that have helpful comments
            # Get comments from scans with same disease, sorted by helpful_count
            pipeline = [
                # Find scans with same disease
                {
                    "$match": {
                        "disease_name": disease_name,
                        "status": "completed"
                    }
                },
                # Lookup comments for these scans
                {
                    "$lookup": {
                        "from": "comments",
                        "localField": "id",
                        "foreignField": "scan_id",
                        "as": "comments"
                    }
                },
                # Unwind comments
                {"$unwind": "$comments"},
                # Filter for helpful comments (at least 3 helpful votes)
                {
                    "$match": {
                        "comments.helpful_count": {"$gte": 3}
                    }
                },
                # Sort by helpful count
                {"$sort": {"comments.helpful_count": -1}},
                # Limit to top 5 most helpful
                {"$limit": 5},
                # Project only needed fields
                {
                    "$project": {
                        "_id": 0,
                        "farmerName": "$comments.user_name",
                        "farmerLocation": "$comments.user_location",
                        "advice": "$comments.advice",
                        "helpfulCount": "$comments.helpful_count",
                        "timestamp": "$comments.created_at"
                    }
                }
            ]
            
            cursor = db.scans.aggregate(pipeline)
            community_advice = await cursor.to_list(length=5)
            
            logger.info(f"Found {len(community_advice)} high-trust community advice for {disease_name}")
        
        # Format response to match frontend expectations
        result = DetectionResult(
            scanId=scan["id"],
            status=scan["status"],
            diseaseName=scan.get("disease_name"),
            reliability=scan.get("reliability"),
            nextSteps=scan.get("next_steps", []),
            isCommon=scan.get("is_common", False),
            imageUrl=scan["image_url"],
            cropName=scan["crop_name"],
            description=scan["description"],
            communityAdvice=community_advice
        )
        
        return {
            "success": True,
            "data": result.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch scan: {str(e)}"
        )


@router.delete("/{scan_id}", response_model=dict)
async def delete_scan(
    scan_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete a scan
    
    - **scan_id**: Scan ID
    """
    try:
        scan = await db.scans.find_one({"id": scan_id})
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        # Check if user owns this scan
        if scan["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete from database
        await db.scans.delete_one({"id": scan_id})
        
        # TODO: Delete image file from storage
        
        return {
            "success": True,
            "message": "Scan deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scan: {str(e)}"
        )


@router.get("/community/feed", response_model=dict)
async def get_community_scans(
    skip: int = 0,
    limit: int = 20,
    crop_type: Optional[str] = None,
    disease_name: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get community feed of all scans for collaboration
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **crop_type**: Filter by crop type (optional)
    - **disease_name**: Filter by disease (optional)
    """
    try:
        # Build filter query
        query = {"status": "completed"}  # Only show completed scans
        if crop_type:
            query["crop_name"] = crop_type.capitalize()
        if disease_name:
            query["disease_name"] = {"$regex": disease_name, "$options": "i"}
        
        # Get total count
        total = await db.scans.count_documents(query)
        
        # Get scans with user info
        cursor = db.scans.find(query).sort("created_at", -1).skip(skip).limit(limit)
        scans = await cursor.to_list(length=limit)
        
        # Enrich with user data and comments count
        for scan in scans:
            # Get user info
            user = await db.users.find_one({"id": scan["user_id"]})
            if user:
                scan["user_name"] = user.get("full_name", "Anonymous Farmer")
                scan["user_location"] = user.get("location", "Unknown")
            else:
                scan["user_name"] = "Anonymous Farmer"
                scan["user_location"] = "Unknown"
            
            # Count comments
            comments_count = await db.comments.count_documents({"scan_id": scan["id"]})
            scan["comments_count"] = comments_count
            
            # Remove sensitive fields
            scan.pop("user_id", None)
        
        return {
            "success": True,
            "data": {
                "scans": scans,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching community scans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch community scans: {str(e)}"
        )


@router.post("/{scan_id}/comments", response_model=dict)
async def add_comment_to_scan(
    scan_id: str,
    advice: str = Form(..., description="Advice or comment"),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Add advice/comment to a scan in the community
    
    - **scan_id**: ID of the scan
    - **advice**: Helpful advice or comment
    """
    try:
        # Check if scan exists
        scan = await db.scans.find_one({"id": scan_id})
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        # Create comment
        comment = {
            "id": f"comment_{datetime.utcnow().timestamp()}",
            "scan_id": scan_id,
            "user_id": current_user.id,
            "user_name": current_user.full_name,
            "user_location": current_user.location,
            "advice": advice,
            "helpful_count": 0,
            "created_at": datetime.utcnow()
        }
        
        await db.comments.insert_one(comment)
        
        return {
            "success": True,
            "data": comment,
            "message": "Advice added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error adding comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}"
        )


@router.get("/{scan_id}/comments", response_model=dict)
async def get_scan_comments(
    scan_id: str,
    skip: int = 0,
    limit: int = 10,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all comments/advice for a specific scan
    
    - **scan_id**: ID of the scan
    """
    try:
        # Get total count
        total = await db.comments.count_documents({"scan_id": scan_id})
        
        # Get comments
        cursor = db.comments.find({"scan_id": scan_id}).sort("helpful_count", -1).skip(skip).limit(limit)
        comments = await cursor.to_list(length=limit)
        
        return {
            "success": True,
            "data": {
                "comments": comments,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch comments: {str(e)}"
        )


@router.post("/{scan_id}/comments/{comment_id}/helpful", response_model=dict)
async def mark_comment_helpful(
    scan_id: str,
    comment_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mark a comment as helpful
    
    - **scan_id**: ID of the scan
    - **comment_id**: ID of the comment
    """
    try:
        # Increment helpful count
        result = await db.comments.update_one(
            {"id": comment_id, "scan_id": scan_id},
            {"$inc": {"helpful_count": 1}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Get updated comment
        comment = await db.comments.find_one({"id": comment_id})
        
        return {
            "success": True,
            "data": comment,
            "message": "Marked as helpful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error marking comment helpful: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark comment helpful: {str(e)}"
        )
