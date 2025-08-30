"""
Simplified database models for MVP - No foreign key constraints
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class SessionMVP(Base):
    """Simplified session model for MVP without foreign key constraints"""
    __tablename__ = "sessions_mvp"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
    config = Column(JSON)
    context_data = Column(JSON)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SessionMVP(id='{self.id}', session_id='{self.session_id}')>"


class QueryLogMVP(Base):
    """Simple query logging for MVP analytics"""
    __tablename__ = "query_logs_mvp"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True)
    query_text = Column(Text, nullable=False)
    response_length = Column(Integer)
    query_type = Column(String(100))
    processing_time_ms = Column(Integer)
    tools_used = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<QueryLogMVP(id='{self.id}', query_type='{self.query_type}')>"
