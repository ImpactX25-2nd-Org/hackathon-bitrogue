"""
Scan routes for disease detection - Updated with RAG+LLM
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
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
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scans", tags=["Disease Detection"])

# Global service instances (initialized in main.py startup)
rag_service: Optional[RAGService] = None
llm_service: Optional[LLMService] = None


def translate_scan_data(scan: dict, language: str) -> dict:
    """Translate scan data fields to target language using IndicTrans"""
    if language == "en" or not scan:
        logger.info(f"🔤 Translation skipped - language is 'en' or scan is empty")
        return scan
    
    logger.info(f"🌐 Starting translation to {language} for scan {scan.get('id', 'unknown')}")
    
    try:
        from app.services import translation_service
        if not translation_service.translation_service:
            logger.warning(f"⚠️ Translation service not available")
            return scan
        
        translator = translation_service.translation_service
        logger.info(f"✓ Translation service loaded successfully")
        
        # Translate disease name
        if scan.get("disease_name"):
            original = scan["disease_name"].replace("_", " ").title()
            logger.info(f"📝 Translating disease name: '{original}' (en → {language})")
            translated = translator.translate_single(original, "en", language)
            scan["disease_name_translated"] = translated
            logger.info(f"✓ Disease name translated: '{original}' → '{translated}'")
        
        # Translate AI treatment advice
        if scan.get("ai_treatment_advice"):
            original_advice = scan["ai_treatment_advice"][:50] + "..." if len(scan["ai_treatment_advice"]) > 50 else scan["ai_treatment_advice"]
            logger.info(f"📝 Translating AI advice: '{original_advice}' (en → {language})")
            translated = translator.translate_single(scan["ai_treatment_advice"], "en", language)
            scan["ai_treatment_advice"] = translated
            logger.info(f"✓ AI advice translated ({len(translated)} chars)")
        
        # Translate next steps (array)
        if scan.get("next_steps") and isinstance(scan["next_steps"], list):
            logger.info(f"📝 Translating {len(scan['next_steps'])} next steps (en → {language})")
            translated_steps = translator.translate(scan["next_steps"], "en", language)
            scan["next_steps"] = translated_steps
            logger.info(f"✓ Next steps translated: {len(translated_steps)} items")
        
        # Translate description
        if scan.get("description"):
            original_desc = scan["description"][:50] + "..." if len(scan["description"]) > 50 else scan["description"]
            logger.info(f"📝 Translating description: '{original_desc}' (en → {language})")
            translated = translator.translate_single(scan["description"], "en", language)
            scan["description"] = translated
            logger.info(f"✓ Description translated ({len(translated)} chars)")
        
        logger.info(f"🎉 Translation complete for scan {scan.get('id', 'unknown')}")
            
    except Exception as e:
        logger.error(f"❌ Translation failed for language {language}: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return scan


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
        
        # RAG + LLM Pipeline for Treatment Advice
        disease_name = prediction["disease"]
        confidence = prediction["confidence"]
        
        logger.info(f"🔍 Starting RAG+LLM pipeline for: {disease_name}")
        logger.info(f"📊 RAG service status: {'✓ Available' if rag_service else '✗ Not initialized'}")
        logger.info(f"📊 LLM service status: {'✓ Available' if llm_service else '✗ Not initialized'}")
        
        ai_treatment_advice = None
        raw_disease_info = None
        
        if rag_service and llm_service:
            try:
                # Step 1: Retrieve disease info from knowledge base
                logger.info(f"Retrieving disease info for: {disease_name}")
                raw_disease_info = rag_service.get_disease_info(disease_name)
                
                if raw_disease_info:
                    # Step 2: Format context for LLM
                    context = rag_service.format_context_for_llm(raw_disease_info)
                    
                    # Step 3: Generate AI advice using OpenRouter
                    logger.info(f"Generating AI treatment advice...")
                    ai_treatment_advice = await llm_service.generate_treatment_advice(
                        disease_name=disease_name,
                        crop_type=crop_type,
                        context=context,
                        confidence=confidence,
                        disease_info=raw_disease_info,
                        language=language
                    )
                    logger.info(f"✓ AI advice generated successfully")
                else:
                    logger.warning(f"Disease '{disease_name}' not found in knowledge base")
                    # Create minimal fallback advice
                    ai_treatment_advice = {
                        "summary": f"Disease detected: {disease_name}",
                        "immediate_actions": ["Consult agricultural expert for specific treatment"],
                        "treatment_plan": {"chemical": [], "organic": []},
                        "prevention_tips": [],
                        "timeline": "Consult expert",
                        "cost_estimate": "Varies",
                        "urgency": "medium"
                    }
            
            except Exception as e:
                logger.error(f"Error in RAG+LLM pipeline: {str(e)}")
                # Fallback: Use basic disease info if available
                if raw_disease_info:
                    treatment = raw_disease_info.get('treatment', {})
                    ai_treatment_advice = {
                        "summary": raw_disease_info.get('disease_name', disease_name),
                        "immediate_actions": treatment.get('immediate', []),
                        "treatment_plan": {
                            "chemical": treatment.get('chemical', []),
                            "organic": treatment.get('organic', [])
                        },
                        "prevention_tips": raw_disease_info.get('prevention', []),
                        "timeline": raw_disease_info.get('timeline', 'N/A'),
                        "cost_estimate": raw_disease_info.get('cost_estimate', 'N/A'),
                        "urgency": raw_disease_info.get('urgency', 'medium')
                    }
        else:
            logger.warning("RAG/LLM services not initialized - skipping AI advice generation")
        
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
        
        # Add AI treatment advice to database record
        if ai_treatment_advice:
            scan_dict["ai_treatment_advice"] = ai_treatment_advice
            scan_dict["next_steps"] = ai_treatment_advice.get("immediate_actions", [])
        else:
            scan_dict["ai_treatment_advice"] = None
            scan_dict["next_steps"] = []
        
        scan_dict["is_common"] = True  # Can be enhanced with disease frequency data
        
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
        
        # Log what we're sending back
        next_steps = ai_treatment_advice.get("immediate_actions", []) if ai_treatment_advice else []
        logger.info(f"📤 Response nextSteps count: {len(next_steps)}")
        logger.info(f"📤 AI treatment advice status: {'✓ Generated' if ai_treatment_advice else '✗ None'}")
        if next_steps:
            logger.info(f"📤 First next step: {next_steps[0][:50] if next_steps[0] else 'Empty'}...")
        
        return {
            "success": True,
            "data": {
                "scan_id": scan.id,
                "crop_type": crop_type,
                "disease_detected": prediction["disease"],
                "diseaseName": prediction["disease"],  # Frontend expects this field
                "confidence": prediction["confidence"],
                "reliability": prediction["confidence"],  # Frontend expects this field
                "all_predictions": prediction["all_predictions"],
                "image_url": f"/uploads/{image_url}",
                "timestamp": scan.created_at.isoformat(),
                "status": "completed",
                "nextSteps": next_steps,  # Frontend expects this
                "isCommon": True,  # Frontend expects this
                "ai_treatment_advice": ai_treatment_advice,  # Full AI advice for advanced features
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
    language: str = Query("en", description="Language code for translation (en, ta, kn)"),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get current user's scan history with optional translation
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **language**: Language code (en, ta, kn) for translating results
    """
    try:
        logger.info(f"📥 GET /scans - User: {current_user.id}, Language: {language}, Skip: {skip}, Limit: {limit}")
        
        # Get total count
        total = await db.scans.count_documents({"user_id": current_user.id})
        logger.info(f"📊 Found {total} total scans for user")
        
        # Get scans
        cursor = db.scans.find({"user_id": current_user.id}).sort("created_at", -1).skip(skip).limit(limit)
        scans = await cursor.to_list(length=limit)
        logger.info(f"📦 Retrieved {len(scans)} scans from database")
        
        # Convert ObjectId to string and translate
        for idx, scan in enumerate(scans):
            if "_id" in scan:
                scan["_id"] = str(scan["_id"])
            
            # Translate scan data if not English
            if language != "en":
                logger.info(f"🔄 Translating scan {idx+1}/{len(scans)} (ID: {scan.get('id', 'unknown')})")
                scan = translate_scan_data(scan, language)
        
        logger.info(f"✅ Successfully fetched and translated {len(scans)} scans")
        
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


@router.get("/community/feed", response_model=dict)
async def get_community_scans(
    skip: int = 0,
    limit: int = 20,
    crop_type: Optional[str] = None,
    disease_name: Optional[str] = None,
    language: str = Query("en", description="Language code for translation (en, ta, kn)"),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get community feed of all scans for collaboration with optional translation
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **crop_type**: Filter by crop type (optional)
    - **disease_name**: Filter by disease (optional)
    - **language**: Language code (en, ta, kn) for translating results
    """
    try:
        logger.info(f"📥 GET /scans/community/feed - Language: {language}, Crop: {crop_type}, Disease: {disease_name}")
        
        # Build filter query
        query = {"status": "completed"}  # Only show completed scans
        if crop_type:
            query["crop_name"] = crop_type.capitalize()
        if disease_name:
            query["disease_name"] = {"$regex": disease_name, "$options": "i"}
        
        # Get total count
        total = await db.scans.count_documents(query)
        logger.info(f"📊 Found {total} total community scans matching filters")
        
        # Get scans with user info
        cursor = db.scans.find(query).sort("created_at", -1).skip(skip).limit(limit)
        scans = await cursor.to_list(length=limit)
        logger.info(f"📦 Retrieved {len(scans)} community scans from database")
        
        # Enrich with user data and comments count
        for idx, scan in enumerate(scans):
            # Convert ObjectId to string
            if "_id" in scan:
                scan["_id"] = str(scan["_id"])
            
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
            
            # Translate scan data if not English
            if language != "en":
                logger.info(f"🔄 Translating community scan {idx+1}/{len(scans)} (ID: {scan.get('id', 'unknown')})")
                scan = translate_scan_data(scan, language)
        
        logger.info(f"✅ Successfully fetched and translated {len(scans)} community scans")
        
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


@router.get("/{scan_id}", response_model=dict)
async def get_scan_details(
    scan_id: str,
    language: str = Query("en", description="Language code for translation (en, ta, kn)"),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed information about a specific scan with community advice and translation
    
    - **scan_id**: Scan ID
    - **language**: Language code (en, ta, kn) for translating results
    """
    try:
        logger.info(f"📥 GET /scans/{scan_id} - User: {current_user.id}, Language: {language}")
        
        scan = await db.scans.find_one({"id": scan_id})
        
        if not scan:
            logger.warning(f"⚠️ Scan {scan_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        logger.info(f"✓ Found scan: {scan.get('disease_name', 'unknown disease')}")
        
        # Check if user owns this scan
        if scan["user_id"] != current_user.id:
            logger.warning(f"⚠️ Access denied - Scan belongs to different user")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Fetch high-trust community advice for this disease
        community_advice = []
        disease_name = scan.get("disease_name")
        
        if disease_name:
            logger.info(f"🔍 Fetching community advice for disease: {disease_name}")
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
            
            # Translate community advice if not English
            if language != "en":
                logger.info(f"🔄 Translating {len(community_advice)} community advice entries (en → {language})")
                try:
                    from app.services import translation_service
                    if translation_service.translation_service:
                        translator = translation_service.translation_service
                        for idx, advice in enumerate(community_advice):
                            if advice.get("advice"):
                                original = advice["advice"][:50] + "..." if len(advice["advice"]) > 50 else advice["advice"]
                                logger.info(f"📝 Translating advice {idx+1}: '{original}'")
                                translated = translator.translate_single(advice["advice"], "en", language)
                                advice["advice"] = translated
                                logger.info(f"✓ Advice {idx+1} translated ({len(translated)} chars)")
                        logger.info(f"✅ All community advice translated")
                except Exception as e:
                    logger.error(f"❌ Failed to translate community advice: {e}")
        
        # Translate scan data if not English
        if language != "en":
            logger.info(f"🔄 Translating scan details (en → {language})")
            scan = translate_scan_data(scan, language)
            logger.info(f"✅ Scan details translated")
        
        logger.info(f"📦 Preparing response for scan {scan_id}")
        
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
        
        result = await db.comments.insert_one(comment)
        
        # Convert ObjectId to string for response
        if "_id" in comment:
            comment["_id"] = str(comment["_id"])
        
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
        
        # Convert ObjectId to string
        for comment in comments:
            if "_id" in comment:
                comment["_id"] = str(comment["_id"])
        
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


@router.get("/test/translation", response_model=dict)
async def test_translation(
    text: str = Query("Rice Sheath Blight", description="Text to translate"),
    target_lang: str = Query("ta", description="Target language (ta or kn)"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    TEST ENDPOINT: Verify IndicTrans translation works
    
    - **text**: English text to translate
    - **target_lang**: Target language code (ta or kn)
    """
    try:
        logger.info(f"🧪 TEST TRANSLATION: '{text}' (en → {target_lang})")
        
        from app.services import translation_service
        if not translation_service.translation_service:
            logger.error("❌ Translation service not initialized!")
            return {
                "success": False,
                "error": "Translation service not available",
                "message": "IndicTrans not loaded"
            }
        
        translator = translation_service.translation_service
        logger.info(f"✓ Translation service found: {translator}")
        logger.info(f"✓ Device: {translator.device}")
        logger.info(f"✓ Processor: {translator.processor}")
        
        # Test single translation
        logger.info(f"🔄 Starting translation...")
        translated = translator.translate_single(text, "en", target_lang)
        logger.info(f"✅ Translation SUCCESS!")
        logger.info(f"📝 Original: '{text}'")
        logger.info(f"📝 Translated: '{translated}'")
        
        return {
            "success": True,
            "data": {
                "original": text,
                "translated": translated,
                "source_lang": "en",
                "target_lang": target_lang,
                "device": translator.device,
                "translation_service_active": True
            },
            "message": "Translation test successful"
        }
        
    except Exception as e:
        logger.error(f"❌ Translation test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
