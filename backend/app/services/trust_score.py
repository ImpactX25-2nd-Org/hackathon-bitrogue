"""
Trust score calculation service
"""
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


class TrustScoreCalculator:
    """Calculate and update user trust scores"""
    
    # Trust score weights
    WEIGHTS = {
        "accepted_response": 10,      # Post response accepted as solution
        "helpful_vote": 2,             # Received helpful vote
        "verified_response": 3,        # AI-verified response
        "positive_feedback": 5,        # Positive feedback on suggestion (score 4-5)
        "neutral_feedback": 1,         # Neutral feedback (score 3)
        "negative_feedback": -5,       # Negative feedback (score 1-2)
        "downvote": -2,                # Received downvote
        "reported_content": -10,       # Content reported
    }
    
    BASE_SCORE = 50.0
    MIN_SCORE = 0.0
    MAX_SCORE = 100.0
    
    @staticmethod
    async def calculate_user_score(user_id: str, db: AsyncIOMotorDatabase) -> float:
        """
        Calculate user's trust score based on their activity
        
        Args:
            user_id: User ID
            db: Database instance
            
        Returns:
            Calculated trust score (0-100)
        """
        score = TrustScoreCalculator.BASE_SCORE
        
        # Count accepted responses
        accepted_responses = await db.community_posts.count_documents({
            "accepted_response_id": {"$exists": True}
        })
        accepted_by_user = 0
        async for post in db.community_posts.find({"accepted_response_id": {"$exists": True}}):
            response = await db.post_comments.find_one({
                "id": post.get("accepted_response_id"),
                "user_id": user_id
            })
            if response:
                accepted_by_user += 1
        
        score += accepted_by_user * TrustScoreCalculator.WEIGHTS["accepted_response"]
        
        # Count verified responses
        verified_count = await db.post_comments.count_documents({
            "user_id": user_id,
            "is_verified": True
        })
        score += verified_count * TrustScoreCalculator.WEIGHTS["verified_response"]
        
        # Count helpful votes
        helpful_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$helpful_count"}}}
        ]
        helpful_result = await db.post_comments.aggregate(helpful_pipeline).to_list(1)
        helpful_count = helpful_result[0]["total"] if helpful_result else 0
        score += helpful_count * TrustScoreCalculator.WEIGHTS["helpful_vote"]
        
        # Count feedback on suggestions
        feedback_pipeline = [
            {"$match": {"farmer_id": user_id}},
            {
                "$group": {
                    "_id": None,
                    "positive": {"$sum": {"$cond": [{"$gte": ["$score", 4]}, 1, 0]}},
                    "neutral": {"$sum": {"$cond": [{"$eq": ["$score", 3]}, 1, 0]}},
                    "negative": {"$sum": {"$cond": [{"$lte": ["$score", 2]}, 1, 0]}}
                }
            }
        ]
        feedback_result = await db.trust_feedback.aggregate(feedback_pipeline).to_list(1)
        
        if feedback_result:
            feedback = feedback_result[0]
            score += feedback.get("positive", 0) * TrustScoreCalculator.WEIGHTS["positive_feedback"]
            score += feedback.get("neutral", 0) * TrustScoreCalculator.WEIGHTS["neutral_feedback"]
            score += feedback.get("negative", 0) * TrustScoreCalculator.WEIGHTS["negative_feedback"]
        
        # Clamp score between min and max
        score = max(TrustScoreCalculator.MIN_SCORE, min(score, TrustScoreCalculator.MAX_SCORE))
        
        return round(score, 2)
    
    @staticmethod
    async def update_user_score(user_id: str, db: AsyncIOMotorDatabase) -> float:
        """
        Calculate and update user's trust score in database
        
        Args:
            user_id: User ID
            db: Database instance
            
        Returns:
            Updated trust score
        """
        new_score = await TrustScoreCalculator.calculate_user_score(user_id, db)
        
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"trust_score": new_score}}
        )
        
        return new_score
    
    @staticmethod
    async def increment_score(
        user_id: str, 
        action: str, 
        db: AsyncIOMotorDatabase
    ) -> float:
        """
        Increment user's trust score for a specific action
        
        Args:
            user_id: User ID
            action: Action type (key from WEIGHTS)
            db: Database instance
            
        Returns:
            Updated trust score
        """
        weight = TrustScoreCalculator.WEIGHTS.get(action, 0)
        
        if weight == 0:
            return await TrustScoreCalculator.update_user_score(user_id, db)
        
        # Get current score
        user = await db.users.find_one({"id": user_id})
        if not user:
            return TrustScoreCalculator.BASE_SCORE
        
        current_score = user.get("trust_score", TrustScoreCalculator.BASE_SCORE)
        new_score = current_score + weight
        
        # Clamp score
        new_score = max(
            TrustScoreCalculator.MIN_SCORE, 
            min(new_score, TrustScoreCalculator.MAX_SCORE)
        )
        
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"trust_score": round(new_score, 2)}}
        )
        
        return round(new_score, 2)


# Convenience function
async def update_trust_score(user_id: str, db: AsyncIOMotorDatabase) -> float:
    """Update and return user's trust score"""
    return await TrustScoreCalculator.update_user_score(user_id, db)
