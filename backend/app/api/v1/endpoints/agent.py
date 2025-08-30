"""
Agent endpoints for SpectraQ AI Agent
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.schemas.agent import (
    AgentQueryRequest,
    AgentQueryResponse,
    AgentSessionCreate,
    AgentSessionResponse,
    AgentDeployRequest,
    AgentDeployResponse
)
from app.services.agent_service_simple import AgentService
from app.services.mcp_manager import MCPManager
from app.services.gemini_client import GeminiClient
from app.core.exceptions import AgentSessionError, MCPServerError, GeminiAPIError

router = APIRouter()


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(
    request: AgentQueryRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> AgentQueryResponse:
    """
    Process user query through SpectraQ AI Agent
    
    This endpoint handles user queries by:
    1. Analyzing the query to determine required data sources
    2. Calling relevant MCP servers to fetch data
    3. Using Gemini AI LLM for analysis and prediction
    4. Maintaining session state for context
    """
    try:
        agent_service = AgentService(db, redis)
        
        # Process the query
        result = await agent_service.process_query(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
            context=request.context
        )
        
        # Log query for analytics (background task)
        background_tasks.add_task(
            agent_service.log_query,
            request.query,
            result.response,
            request.session_id,
            request.user_id
        )
        
        return result
        
    except AgentSessionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MCPServerError as e:
        raise HTTPException(status_code=503, detail=f"Data source error: {str(e)}")
    except GeminiAPIError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stream")
async def stream_agent_response(
    request: AgentQueryRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Stream real-time responses from the agent
    
    This endpoint provides streaming responses for long-running queries
    using Server-Sent Events (SSE)
    """
    try:
        agent_service = AgentService(db, redis)
        
        async def generate_response():
            try:
                async for chunk in agent_service.stream_query_response(
                    query=request.query,
                    session_id=request.session_id,
                    user_id=request.user_id,
                    context=request.context
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                error_chunk = {
                    "type": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Streaming error")


@router.post("/session", response_model=AgentSessionResponse)
async def create_session(
    request: AgentSessionCreate,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> AgentSessionResponse:
    """
    Create a new agent session
    """
    try:
        agent_service = AgentService(db, redis)
        session = await agent_service.create_session(
            user_id=request.user_id,
            session_config=request.config
        )
        return session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/session/{session_id}", response_model=AgentSessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> AgentSessionResponse:
    """
    Get agent session details
    """
    try:
        agent_service = AgentService(db, redis)
        session = await agent_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, str]:
    """
    Delete an agent session
    """
    try:
        agent_service = AgentService(db, redis)
        success = await agent_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.post("/deploy", response_model=AgentDeployResponse)
async def deploy_agent(
    request: AgentDeployRequest,
    db: AsyncSession = Depends(get_db)
) -> AgentDeployResponse:
    """
    Deploy ElizaOS agent to Gemini AI distributed network
    
    This endpoint handles agent deployment for distributed inference
    """
    try:
        gemini_client = GeminiClient()
        
        deployment_result = await gemini_client.deploy_agent(
            agent_config=request.agent_config,
            deployment_config=request.deployment_config
        )
        
        return AgentDeployResponse(
            agent_id=deployment_result["agent_id"],
            deployment_status="deployed",
            endpoint_url=deployment_result["endpoint_url"],
            network_nodes=deployment_result.get("nodes", []),
            deployment_timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@router.get("/tools")
async def list_available_tools() -> Dict[str, Any]:
    """
    List all available MCP tools and their capabilities
    """
    try:
        mcp_manager = MCPManager()
        tools = await mcp_manager.list_all_tools()
        
        return {
            "tools": tools,
            "total_count": len(tools),
            "categories": list(set(tool.get("category", "general") for tool in tools))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list tools")


@router.get("/status")
async def get_agent_status() -> Dict[str, Any]:
    """
    Get current status of all agent components
    """
    try:
        mcp_manager = MCPManager()
        gemini_client = GeminiClient()
        
        # Check MCP servers status
        mcp_status = await mcp_manager.health_check()
        
        # Check Gemini AI API status  
        gemini_status = await gemini_client.health_check()
        
        return {
            "overall_status": "healthy" if all([mcp_status["healthy"], gemini_status["healthy"]]) else "degraded",
            "mcp_servers": mcp_status,
            "gemini_api": gemini_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
