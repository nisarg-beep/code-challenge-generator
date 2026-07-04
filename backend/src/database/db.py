from sqlalchemy.orm import Session
from datetime import datetime
from . import models
# Note: Do not import Base or engine here if not needed,
# or import them from .base if they are.

def get_challenge_quota(db: Session, user_id: str):
    return (db.query(models.ChallengeQuota)
            .filter(models.ChallengeQuota.user_id == user_id)
            .first())




def create_challenge_quota(db: Session, user_id: str):
    """
    Creates a quota for a new user.
    We initialize it with a high number to signify unlimited/high access.
    """
    db_quota = models.ChallengeQuota(user_id=user_id, quota_remaining=99999)
    db.add(db_quota)
    db.commit()
    db.refresh(db_quota)
    return db_quota


def reset_quota_if_needed(db: Session, quota: models.ChallengeQuota):
    """
    Modified to always ensure the user has 'unlimited' (99999) questions.
    This effectively disables the 24-hour restriction.
    """
    quota.quota_remaining = 99999
    quota.last_reset_date = datetime.now()
    db.commit()
    db.refresh(quota)
    return quota


def create_challenge(
        db: Session,
        difficulty: str,
        created_by: str,
        title: str,
        question: str,      # NEW PARAMETER
        options: str,
        correct_answer_id: int,
        explanation: str,
        language: str = None, # NEW PARAMETER
        topic: str = None     # NEW PARAMETER
):
    # 1. Create the challenge entry with new fields
    db_challenge = models.Challenge(
        difficulty=difficulty,
        created_by=created_by,
        title=title,
        question=question,     # SAVED TO DB
        options=options,
        correct_answer_id=correct_answer_id,
        explanation=explanation,
        language=language,     # SAVED TO DB
        topic=topic            # SAVED TO DB
    )
    db.add(db_challenge)

    # 2. Logic to handle the quota decrement
    # To keep the app from breaking, we fetch the quota and just keep it high
    quota = get_challenge_quota(db, created_by)
    if quota:
        quota.quota_remaining = 99999  # Keep it at a high number every time a challenge is made

    db.commit()
    db.refresh(db_challenge)
    return db_challenge


def get_user_challenges(db: Session, user_id: str):
    return db.query(models.Challenge).filter(models.Challenge.created_by == user_id).all()