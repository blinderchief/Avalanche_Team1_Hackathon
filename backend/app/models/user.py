"""
User model for storing user data
"""

from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), unique=True, nullable=False)
    wallet_address = Column(String(255), nullable=True)
    preferences = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<User(id='{self.id}', user_id='{self.user_id}')>"
