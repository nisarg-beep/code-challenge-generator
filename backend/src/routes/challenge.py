from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
import json
import logging
from datetime import datetime

from ..ai_generator import generate_challenge_with_ai
from ..database.db import (
    get_challenge_quota,
    create_challenge,
    create_challenge_quota,
    reset_quota_if_needed,
    get_user_challenges
)
from ..utils import authenticate_and_get_user_details
from ..database.base import get_db
from ..database.models import Challenge

router = APIRouter()
logger = logging.getLogger(__name__)

# Schema defining what the React Frontend sends to FastAPI
class ChallengeRequest(BaseModel):
    difficulty: str
    language: str
    topic: str

@router.post("/generate-challenge")
async def generate_challenge(
    challenge_req: ChallengeRequest,  # Renamed from 'request' to avoid shadowing conflicts
    request_obj: Request, 
    db: Session = Depends(get_db)
):
    try:
        # Authenticate token context extracted from HTTP Headers
        user_details = authenticate_and_get_user_details(request_obj)
        user_id = user_details.get("user_id")

        # Quota pipeline validation logic
        quota = get_challenge_quota(db, user_id)
        if not quota:
            quota = create_challenge_quota(db, user_id)
        quota = reset_quota_if_needed(db, quota)

        # 1. Generate AI challenge via Gemini (returns a validated dictionary)
        challenge_data = generate_challenge_with_ai(
            difficulty=challenge_req.difficulty,
            language=challenge_req.language,
            topic=challenge_req.topic
        )

        # 2. Persist transactional challenge data to SQLite
        new_challenge = create_challenge(
            db=db,
            difficulty=challenge_req.difficulty,
            created_by=user_id,
            title=challenge_data["title"],
            question=challenge_data["question"],
            options=json.dumps(challenge_data["options"]),  # Stringified for SQL storage compatibility
            correct_answer_id=challenge_data["correct_answer_id"],
            explanation=challenge_data["explanation"],
            language=challenge_req.language,
            topic=challenge_req.topic
        )

        # 3. Clean operational payload returned to React Frontend
        return {
            "id": new_challenge.id,
            "difficulty": challenge_req.difficulty,
            "language": challenge_req.language,
            "topic": challenge_req.topic,
            "title": new_challenge.title,
            "question": new_challenge.question,
            "options": challenge_data["options"],  # Returns standard JSON array
            "correct_answer_id": new_challenge.correct_answer_id,
            "explanation": new_challenge.explanation,
            "timestamp": new_challenge.date_created.isoformat()
        }

    except KeyError as e:
        logger.error(f"Missing schema attribute from Gemini generation output mapping: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate challenge: structural field missing {str(e)}"
        )
    except ValidationError as e:
        # Replaced JSONDecodeError with Pydantic's ValidationError to catch Gemini mismatch issues
        logger.error(f"Gemini output structured validation alignment failed: {e.json()}")
        raise HTTPException(
            status_code=500,
            detail="AI platform generated data violating structure expectations"
        )
    except Exception as e:
        logger.error(f"Unchecked runtime anomaly handling challenge generation pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate challenge: {str(e)}"
        )


@router.get("/my-history")
async def my_history(request: Request, db: Session = Depends(get_db)):
    try:
        user_details = authenticate_and_get_user_details(request)
        user_id = user_details.get("user_id")
        challenges = get_user_challenges(db, user_id)

        formatted = []
        for c in challenges:
            try:
                # Decodes database strings seamlessly back into arrays for frontend state ingestion
                opts = json.loads(c.options) if isinstance(c.options, str) else c.options
            except json.JSONDecodeError:
                opts = ["Option A", "Option B", "Option C", "Option D"]

            formatted.append({
                "id": c.id,
                "difficulty": c.difficulty,
                "language": c.language,
                "topic": c.topic,
                "title": c.title,
                "question": c.question or c.title,
                "options": opts,
                "correct_answer_id": c.correct_answer_id,
                "explanation": c.explanation,
                "timestamp": c.date_created.isoformat() if c.date_created else datetime.now().isoformat()
            })
        return {"challenges": formatted}

    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@router.delete("/clear-history")
async def clear_history(request: Request, db: Session = Depends(get_db)):
    """
    Clears all challenge history for the authenticated user context.
    """
    try:
        user_details = authenticate_and_get_user_details(request)
        user_id = user_details.get("user_id")

        # Synchronize query execution targets directly avoiding cache serialization errors
        db.query(Challenge).filter(Challenge.created_by == user_id).delete(synchronize_session='fetch')
        db.commit()

        return {"message": "History cleared successfully"}

    except Exception as e:
        db.rollback()  # Safely roll back mutations if transaction encounters an issue
        logger.error(f"Delete history execution anomaly: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not clear history database entries: {str(e)}"
        )
    

@router.get("/quota")
async def get_quota(request: Request, db: Session = Depends(get_db)):
    """
    Fetches or initializes the challenge quota for the authenticated user.
    """
    try:
        user_details = authenticate_and_get_user_details(request)
        user_id = user_details.get("user_id")
        
        quota = get_challenge_quota(db, user_id)
        if not quota:
            quota = create_challenge_quota(db, user_id)
            
        quota = reset_quota_if_needed(db, quota)
        
        return {
            "user_id": quota.user_id,
            "quota_remaining": quota.quota_remaining,
            "last_reset_date": quota.last_reset_date.isoformat()
        }
    except Exception as e:
        logger.error(f"Quota retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve quota: {str(e)}"
        )