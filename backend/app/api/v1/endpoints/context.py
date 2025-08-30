"""
Context synchronization endpoints for agent state management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.schemas.context import (
    ContextSyncRequest,
    ContextSyncResponse,
    ContextRetrievalRequest,
    ContextRetrievalResponse
)
from app.services.context_service import ContextService

router = APIRouter()


@router.get("/{agent_id}", response_model=ContextRetrievalResponse)
async def get_agent_context(
    agent_id: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> ContextRetrievalResponse:
    """
    Retrieve and sync agent context across nodes
    
    This endpoint provides context synchronization for distributed
    agent deployments, ensuring state consistency across the network
    """
    try:
        context_service = ContextService(db, redis)
        
        context_data = await context_service.retrieve_context(
            agent_id=agent_id,
            session_id=session_id,
            user_id=user_id
        )
        
        if not context_data:
            raise HTTPException(status_code=404, detail="Context not found")
        
        return ContextRetrievalResponse(
            agent_id=agent_id,
            session_id=session_id,
            context=context_data["context"],
            conversation_history=context_data.get("conversation_history", []),
            user_preferences=context_data.get("user_preferences", {}),
            market_data_cache=context_data.get("market_data_cache", {}),
            last_updated=context_data.get("last_updated"),
            version=context_data.get("version", 1)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve context: {str(e)}"
        )


@router.post("/sync", response_model=ContextSyncResponse)
async def sync_agent_context(
    request: ContextSyncRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> ContextSyncResponse:
    """
    Synchronize agent context across distributed nodes
    
    This endpoint handles context updates and ensures consistency
    across multiple agent instances in the Gemini AI network
    """
    try:
        context_service = ContextService(db, redis)
        
        sync_result = await context_service.sync_context(
            agent_id=request.agent_id,
            session_id=request.session_id,
            context_data=request.context_data,
            force_update=request.force_update
        )
        
        return ContextSyncResponse(
            agent_id=request.agent_id,
            session_id=request.session_id,
            sync_status=sync_result["status"],
            synchronized_nodes=sync_result.get("nodes", []),
            conflicts_resolved=sync_result.get("conflicts", []),
            sync_timestamp=datetime.utcnow(),
            version=sync_result["version"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Context synchronization failed: {str(e)}"
        )


@router.put("/{agent_id}/update")
async def update_agent_context(
    agent_id: str,
    context_updates: Dict[str, Any],
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    Update specific parts of agent context
    """
    try:
        context_service = ContextService(db, redis)
        
        result = await context_service.update_context(
            agent_id=agent_id,
            session_id=session_id,
            user_id=user_id,
            updates=context_updates
        )
        
        return {
            "message": "Context updated successfully",
            "agent_id": agent_id,
            "session_id": session_id,
            "updated_fields": list(context_updates.keys()),
            "version": result["version"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update context: {str(e)}"
        )


@router.delete("/{agent_id}/clear")
async def clear_agent_context(
    agent_id: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    preserve_preferences: bool = True,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, str]:
    """
    Clear agent context data
    """
    try:
        context_service = ContextService(db, redis)
        
        success = await context_service.clear_context(
            agent_id=agent_id,
            session_id=session_id,
            user_id=user_id,
            preserve_preferences=preserve_preferences
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Context not found")
        
        return {
            "message": "Context cleared successfully",
            "agent_id": agent_id,
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear context: {str(e)}"
        )


@router.get("/{agent_id}/sessions")
async def list_agent_sessions(
    agent_id: str,
    user_id: Optional[str] = None,
    active_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    List all sessions for an agent
    """
    try:
        context_service = ContextService(db, redis)
        
        sessions = await context_service.list_sessions(
            agent_id=agent_id,
            user_id=user_id,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
        
        return {
            "agent_id": agent_id,
            "sessions": sessions["sessions"],
            "total_count": sessions["total_count"],
            "active_count": sessions["active_count"],
            "has_more": sessions["has_more"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.post("/{agent_id}/backup")
async def backup_agent_context(
    agent_id: str,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    Create a backup of agent context
    """
    try:
        context_service = ContextService(db, redis)
        
        backup_result = await context_service.create_backup(
            agent_id=agent_id,
            session_id=session_id
        )
        
        return {
            "message": "Context backup created successfully",
            "backup_id": backup_result["backup_id"],
            "agent_id": agent_id,
            "session_id": session_id,
            "backup_size": backup_result["size"],
            "created_at": backup_result["created_at"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backup: {str(e)}"
        )


@router.post("/{agent_id}/restore/{backup_id}")
async def restore_agent_context(
    agent_id: str,
    backup_id: str,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, str]:
    """
    Restore agent context from backup
    """
    try:
        context_service = ContextService(db, redis)
        
        success = await context_service.restore_from_backup(
            agent_id=agent_id,
            backup_id=backup_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        return {
            "message": "Context restored successfully",
            "agent_id": agent_id,
            "backup_id": backup_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore context: {str(e)}"
        )
