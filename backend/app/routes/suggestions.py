"""
Suggestions routes for community suggestions and trust feedback
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime, timedelta
from app.database import get_database
from app.models.user import UserInDB
from app.models.suggestion import (
    SuggestionCreate, SuggestionInDB, SuggestionResponse,
    TrustFeedback, TrustFeedbackInDB
)
from app.utils.dependencies import get_current_user
from app.services.trust_score import TrustScoreCalculator

router = APIRouter(prefix="/suggestions", tags=["Suggestions"])


@router.get("/{scan_id}", response_model=dict)
async def get_suggestions(
    scan_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get suggestions for a specific disease/scan
    """
    try:
        # Get scan to find disease name
        scan = await db.scans.find_one({"id": scan_id})
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        disease_name = scan.get("disease_name")
        if not disease_name:
            return {"success": True, "data": {"suggestions": []}}
        
        # Get suggestions for this disease
        cursor = db.suggestions.find(
            {"disease_name": disease_name}
        ).sort("usefulness_score", -1).limit(10)
        
        suggestions = await cursor.to_list(length=10)
        
        # Enrich with author data
        enriched_suggestions = []
        for suggestion in suggestions:
            user = await db.users.find_one({"id": suggestion["user_id"]})
            
            enriched = {
                "id": suggestion["id"],
                "text": suggestion["text"],
                "author": {
                    "id": user["id"] if user else None,
                    "name": user.get("name") if user else "Unknown",
                    "avatar": user.get("avatar_url") if user else None
                },
                "usefulness": suggestion.get("usefulness_score", 50.0),
                "details": suggestion.get("details")
            }
            enriched_suggestions.append(enriched)
        
        return {
            "success": True,
            "data": {"suggestions": enriched_suggestions}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch suggestions: {str(e)}"
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_suggestion(
    suggestion_data: SuggestionCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new suggestion for a disease
    """
    try:
        suggestion = SuggestionInDB(
            disease_name=suggestion_data.disease_name,
            user_id=current_user.id,
            text=suggestion_data.text,
            details=suggestion_data.details
        )
        
        await db.suggestions.insert_one(suggestion.model_dump())
        
        return {
            "success": True,
            "data": {"suggestionId": suggestion.id}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create suggestion: {str(e)}"
        )


@router.post("/trust-score", response_model=dict)
async def submit_trust_feedback(
    feedback_data: TrustFeedback,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Submit trust score feedback for a suggestion
    """
    try:
        # Get suggestion to find farmer_id
        suggestion = await db.suggestions.find_one({"id": feedback_data.suggestion_id})
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        # Check if user already gave feedback for this suggestion
        existing_feedback = await db.trust_feedback.find_one({
            "user_id": current_user.id,
            "suggestion_id": feedback_data.suggestion_id
        })
        
        if existing_feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already provided feedback for this suggestion"
            )
        
        # Create feedback record
        feedback = TrustFeedbackInDB(
            suggestion_id=feedback_data.suggestion_id,
            user_id=current_user.id,
            farmer_id=suggestion["user_id"],
            score=feedback_data.score,
            feedback_text=feedback_data.feedback,
            scan_id=feedback_data.scan_id
        )
        
        await db.trust_feedback.insert_one(feedback.model_dump())
        
        # Update suggestion usefulness score
        avg_score_pipeline = [
            {"$match": {"suggestion_id": feedback_data.suggestion_id}},
            {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}}
        ]
        avg_result = await db.trust_feedback.aggregate(avg_score_pipeline).to_list(1)
        
        if avg_result:
            avg_score = avg_result[0]["avg_score"]
            # Convert 1-5 scale to 0-100
            usefulness_score = ((avg_score - 1) / 4) * 100
            
            await db.suggestions.update_one(
                {"id": feedback_data.suggestion_id},
                {
                    "$set": {"usefulness_score": round(usefulness_score, 2)},
                    "$inc": {
                        "positive_feedback_count": 1 if feedback_data.score >= 4 else 0,
                        "negative_feedback_count": 1 if feedback_data.score <= 2 else 0
                    }
                }
            )
        
        # Update farmer's trust score
        farmer_id = suggestion["user_id"]
        if feedback_data.score >= 4:
            new_score = await TrustScoreCalculator.increment_score(farmer_id, "positive_feedback", db)
        elif feedback_data.score <= 2:
            new_score = await TrustScoreCalculator.increment_score(farmer_id, "negative_feedback", db)
        else:
            new_score = await TrustScoreCalculator.increment_score(farmer_id, "neutral_feedback", db)
        
        # Schedule follow-up notification (10-15 days)
        follow_up_date = datetime.utcnow() + timedelta(days=12)
        notification = {
            "id": str(feedback.id),
            "user_id": current_user.id,
            "type": "trust_score_followup",
            "title": "How did it work?",
            "message": f"Did the suggestion help solve your crop issue?",
            "metadata": {
                "suggestion_id": feedback_data.suggestion_id,
                "scan_id": feedback_data.scan_id
            },
            "is_read": False,
            "scheduled_for": follow_up_date,
            "sent_at": None,
            "created_at": datetime.utcnow()
        }
        
        await db.notifications.insert_one(notification)
        
        return {
            "success": True,
            "data": {
                "newTrustScore": new_score,
                "followUpScheduled": True,
                "followUpDate": follow_up_date.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/trust-scores/updated", response_model=dict)
async def get_updated_trust_scores(
    updated_after: str = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get updated trust scores for farmers
    """
    try:
        query = {}
        if updated_after:
            from datetime import datetime
            query["updated_at"] = {"$gte": datetime.fromisoformat(updated_after)}
        
        cursor = db.users.find(query, {"id": 1, "trust_score": 1})
        users = await cursor.to_list(length=None)
        
        farmers = [{"id": user["id"], "trustScore": user.get("trust_score", 50.0)} for user in users]
        
        return {
            "success": True,
            "data": {
                "farmers": farmers,
                "lastUpdate": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trust scores: {str(e)}"
        )
