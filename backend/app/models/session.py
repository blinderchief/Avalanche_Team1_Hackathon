"""
Session model for storing agent sessions
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Session(Base):
    """Session model for storing agent conversation sessions"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(String(255), nullable=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    status = Column(String(50), default="active")
    config = Column(JSON)
    context_data = Column(JSON)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Session(id='{self.id}', session_id='{self.session_id}')>"
