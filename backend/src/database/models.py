from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    difficulty = Column(String)
    language = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    title = Column(String)
    question = Column(Text, nullable=True)
    options = Column(Text)
    correct_answer_id = Column(Integer)
    explanation = Column(Text)
    created_by = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

# NEW: Added the missing ChallengeQuota model back in
class ChallengeQuota(Base):
    __tablename__ = "challenge_quotas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    quota_remaining = Column(Integer, default=99999)
    last_reset_date = Column(DateTime(timezone=True), server_default=func.now())