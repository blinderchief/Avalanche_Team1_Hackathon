"""
Simplified Agent service for handling queries and managing agent interactions
"""

import uuid
import asyncio
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime, timedelta
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.schemas.agent import (
    AgentQueryResponse, 
    AgentSessionResponse,
    SessionConfig,
    ToolCall,
    DataSource,
    QueryType
)
from app.services.mcp_manager import MCPManager
from app.services.gemini_client import GeminiClient
from app.core.exceptions import AgentSessionError, MCPServerError, GeminiAPIError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class AgentService:
    """Service for handling agent queries and sessions"""
    
    def __init__(self, db: AsyncSession, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.mcp_manager = MCPManager()
        self.gemini_client = GeminiClient()
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentQueryResponse:
        """Process a user query through the SpectraQ AI Agent"""
        start_time = datetime.utcnow()
        response_id = f"resp_{uuid.uuid4().hex[:8]}"
        
        try:
            # Simple query analysis
            query_type = QueryType.GENERAL_CRYPTO
            if "price" in query.lower():
                query_type = QueryType.PRICE_PREDICTION
            elif "sentiment" in query.lower():
                query_type = QueryType.NEWS_SENTIMENT
            
            # Build messages for LLM
            messages = [
                {
                    "role": "system",
                    "content": "You are SpectraQ AI Agent, an expert in cryptocurrency markets."
                },
                {"role": "user", "content": query}
            ]
            
            # Get AI response
            llm_response = await self.gemini_client.chat_completion(
                messages=messages,
                model=settings.DEFAULT_MODEL,
                temperature=0.7,
                max_tokens=1000
            )
            
            response_content = llm_response["choices"][0]["message"]["content"]
            token_usage = llm_response.get("usage", {
                "prompt_tokens": len(query.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(query.split()) + len(response_content.split())
            })
            
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return AgentQueryResponse(
                id=response_id,
                response=response_content,
                session_id=session_id,
                query_type=query_type,
                confidence_score=0.8,
                tools_used=[],
                data_sources=[],
                processing_time_ms=processing_time,
                token_usage=token_usage,
                follow_up_suggestions=["Tell me more", "What about other coins?"]
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise AgentSessionError(f"Query processing failed: {str(e)}", session_id or "unknown")
    
    async def stream_query_response(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream query response in real-time"""
        try:
            yield {
                "type": "start",
                "content": "Processing your query...",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": "You are SpectraQ AI Agent, an expert in cryptocurrency markets."
                },
                {"role": "user", "content": query}
            ]
            
            # Stream LLM response
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
            
            yield {
                "type": "complete",
                "content": "",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_session(
        self,
        user_id: Optional[str] = None,
        session_config: Optional[SessionConfig] = None
    ) -> AgentSessionResponse:
        """Create a new agent session"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        created_at = datetime.utcnow()
        
        if not session_config:
            session_config = SessionConfig(
                model=settings.DEFAULT_MODEL,
                temperature=0.7,
                max_tokens=4096,
                context_window=10,
                tools_enabled=["all"],
                personalization=True,
                risk_tolerance="medium"
            )
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "config": session_config.model_dump(),
            "status": "active",
            "created_at": created_at.isoformat(),
            "message_count": 0,
            "context": {}
        }
        
        # Store in Redis
        await self.redis.setex(
            f"session:{session_id}",
            int(timedelta(hours=2).total_seconds()),
            json.dumps(session_data, default=str)
        )
        
        return AgentSessionResponse(
            session_id=session_id,
            user_id=user_id,
            config=session_config,
            status="active",
            created_at=created_at,
            last_activity=None,
            message_count=0,
            expires_at=created_at + timedelta(hours=2)
        )
    
    async def get_session(self, session_id: str) -> Optional[AgentSessionResponse]:
        """Get session details"""
        try:
            session_data = await self.redis.get(f"session:{session_id}")
            if not session_data:
                return None
            
            data = json.loads(session_data)
            
            # Convert string dates back to datetime
            created_at = datetime.fromisoformat(data["created_at"])
            config = SessionConfig(**data["config"])
            
            return AgentSessionResponse(
                session_id=data["session_id"],
                user_id=data.get("user_id"),
                config=config,
                status=data["status"],
                created_at=created_at,
                last_activity=None,
                message_count=data.get("message_count", 0),
                expires_at=created_at + timedelta(hours=2)
            )
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            result = await self.redis.delete(f"session:{session_id}")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    async def log_query(
        self,
        query: str,
        response: str,
        session_id: Optional[str],
        user_id: Optional[str]
    ):
        """Log query for analytics (background task)"""
        try:
            log_entry = {
                "query": query,
                "response_length": len(response),
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in Redis list for analytics
            self.redis.lpush("query_logs", json.dumps(log_entry))
            self.redis.ltrim("query_logs", 0, 10000)  # Keep last 10k queries
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
