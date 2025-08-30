"""
Full Agent endpoints with Gemini AI integration
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any, Optional
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import (
    AgentQueryRequest,
    AgentQueryResponse,
    AgentSessionResponse,
    SessionConfig
)
from app.services.agent_service import AgentService
from app.core.database import get_db
from app.core.exceptions import AgentSessionError, GeminiAPIError

router = APIRouter()


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(
    request: AgentQueryRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
) -> AgentQueryResponse:
    """
    Process user query through SpectraQ AI Agent with Gemini AI inference

    This endpoint handles user queries by:
    1. Analyzing the query to determine required data sources
    2. Calling relevant MCP servers to fetch real data
    3. Using Gemini AI for intelligent analysis and response generation
    4. Maintaining session state with Redis
    """
    try:
        # Get services from app state
        redis_client = http_request.app.state.redis
        agent_service = AgentService(db, redis_client)

        # Process the query
        result = await agent_service.process_query(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
            context=request.context
        )

        # Log the query for analytics
        await agent_service.log_query(
            request.query,
            result.response,
            request.session_id,
            request.user_id
        )

        return result

    except GeminiAPIError as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
    except AgentSessionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/session", response_model=AgentSessionResponse)
async def create_session(
    request: Dict[str, Any],
    http_request: Request,
    db: AsyncSession = Depends(get_db)
) -> AgentSessionResponse:
    """
    Create a new agent session
    """
    try:
        user_id = request.get("user_id")
        session_config = request.get("config")

        redis_client = http_request.app.state.redis
        agent_service = AgentService(db, redis_client)

        if session_config:
            config = SessionConfig(**session_config)
        else:
            config = SessionConfig()

        session = await agent_service.create_session(
            user_id=user_id,
            session_config=config
        )

        return session

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/session/{session_id}", response_model=AgentSessionResponse)
async def get_session(
    session_id: str,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
) -> AgentSessionResponse:
    """
    Get agent session details
    """
    try:
        redis_client = http_request.app.state.redis
        agent_service = AgentService(db, redis_client)

        session = await agent_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return session

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete an agent session
    """
    try:
        redis_client = http_request.app.state.redis
        agent_service = AgentService(db, redis_client)

        success = await agent_service.delete_session(session_id)

        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@router.get("/tools")
async def list_available_tools(http_request: Request) -> Dict[str, Any]:
    """
    List all available MCP tools and their capabilities
    """
    try:
        mcp_manager = http_request.app.state.mcp_manager
        tools = await mcp_manager.list_all_tools()

        return {
            "tools": tools,
            "total_count": len(tools),
            "servers": list(mcp_manager.servers.keys()),
            "gemini_integration": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@router.get("/status")
async def get_agent_status(http_request: Request) -> Dict[str, Any]:
    """
    Get current status of all agent components
    """
    try:
        mcp_manager = http_request.app.state.mcp_manager
        gemini_client = http_request.app.state.gemini_client

        # Check MCP servers status
        mcp_status = await mcp_manager.health_check()

        # Check Gemini API status
        gemini_status = await gemini_client.health_check()

        return {
            "overall_status": "healthy" if gemini_status["healthy"] else "degraded",
            "mcp_servers": mcp_status,
            "gemini_api": gemini_status,
            "full_ai_mode": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Simple health check
    """
    return {
        "status": "healthy",
        "service": "spectraq-agent-full",
        "ai_integration": "gemini",
        "timestamp": datetime.utcnow().isoformat()
    }
