"""
Chat service for handling chat messages and conversations
"""

import uuid
import json
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime, timedelta
import logging

from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.services.gemini_client import GeminiClient
from app.schemas.chat import MessageType
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class ChatService:
    """Service for handling chat messages and conversations"""
    
    def __init__(self, db: Optional[AsyncSession] = None, redis_client: Optional[redis.Redis] = None):
        self.db = db
        self.redis = redis_client
        self.gemini_client = GeminiClient()
    
    async def process_chat_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        message_type: MessageType = MessageType.USER,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a chat message and return response"""
        try:
            # Build conversation messages
            messages = [
                {
                    "role": "system",
                    "content": "You are SpectraQ AI Agent, an expert cryptocurrency trading assistant."
                },
                {"role": "user", "content": message}
            ]
            
            # Get AI response
            response = await self.gemini_client.chat_completion(
                messages=messages,
                model=settings.DEFAULT_MODEL,
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "content": response["choices"][0]["message"]["content"],
                "usage": response.get("usage", {}),
                "tools_used": [],
                "data_sources": [],
                "finish_reason": "stop"
            }
            
        except Exception as e:
            logger.error(f"Chat message processing failed: {e}")
            return {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "content": "I apologize, but I encountered an error processing your message. Please try again.",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "error": str(e)
            }
    
    async def stream_chat_response(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat response in real-time"""
        try:
            yield {"type": "start", "id": f"msg_{uuid.uuid4().hex[:8]}"}
            
            messages = [
                {
                    "role": "system",
                    "content": "You are SpectraQ AI Agent, an expert cryptocurrency trading assistant."
                },
                {"role": "user", "content": message}
            ]
            
            async for chunk in self.gemini_client.stream_completion(
                messages=messages,
                model=settings.DEFAULT_MODEL,
                temperature=0.7
            ):
                if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                    yield {
                        "type": "content",
                        "content": chunk["choices"][0]["delta"]["content"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            yield {"type": "end", "finish_reason": "stop"}
            
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_chat_history(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        message_types: Optional[List[MessageType]] = None
    ) -> Dict[str, Any]:
        """Get chat history for a session"""
        try:
            # This would normally fetch from database
            # For now, return empty history
            return {
                "messages": [],
                "total_count": 0,
                "has_more": False
            }
            
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return {
                "messages": [],
                "total_count": 0,
                "has_more": False
            }
    
    async def clear_chat_history(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Clear chat history for a session"""
        try:
            # This would normally clear from database
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear chat history: {e}")
            return False
