"""
Pydantic schemas for context synchronization
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class ContextData(BaseModel):
    """Schema for context data structure"""
    conversation_history: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Conversation history"
    )
    user_preferences: Dict[str, Any] = Field(
        default_factory=dict, 
        description="User preferences and settings"
    )
    market_data_cache: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Cached market data"
    )
    analysis_results: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Previous analysis results"
    )
    tool_states: Dict[str, Any] = Field(
        default_factory=dict, 
        description="State of MCP tools"
    )
    session_metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Session-specific metadata"
    )


class ContextSyncRequest(BaseModel):
    """Request schema for context synchronization"""
    agent_id: str = Field(..., description="Agent ID to sync context for")
    session_id: Optional[str] = Field(None, description="Session ID for context scope")
    context_data: ContextData = Field(..., description="Context data to synchronize")
    force_update: bool = Field(False, description="Force update even if versions conflict")
    sync_strategy: str = Field("merge", description="Sync strategy: merge, replace, or append")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "spectraq_agent_123",
                "session_id": "session_456",
                "context_data": {
                    "conversation_history": [
                        {"role": "user", "content": "What's BTC price?", "timestamp": "2025-08-30T10:00:00Z"},
                        {"role": "assistant", "content": "BTC is at $45,000", "timestamp": "2025-08-30T10:00:30Z"}
                    ],
                    "user_preferences": {
                        "preferred_currency": "USD",
                        "risk_tolerance": "medium"
                    },
                    "market_data_cache": {
                        "btc_price": {"value": 45000, "timestamp": "2025-08-30T10:00:00Z"}
                    }
                },
                "force_update": False,
                "sync_strategy": "merge"
            }
        }


class ConflictResolution(BaseModel):
    """Schema for conflict resolution information"""
    field_path: str = Field(..., description="Path to the conflicting field")
    local_value: Any = Field(..., description="Local value")
    remote_value: Any = Field(..., description="Remote value")
    resolved_value: Any = Field(..., description="Final resolved value")
    resolution_strategy: str = Field(..., description="Strategy used to resolve conflict")


class ContextSyncResponse(BaseModel):
    """Response schema for context synchronization"""
    agent_id: str = Field(..., description="Agent ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    sync_status: str = Field(..., description="Sync status: success, partial, failed")
    synchronized_nodes: List[str] = Field(
        default_factory=list, 
        description="List of nodes that were synchronized"
    )
    conflicts_resolved: List[ConflictResolution] = Field(
        default_factory=list, 
        description="Conflicts that were resolved during sync"
    )
    sync_timestamp: datetime = Field(..., description="When synchronization completed")
    version: int = Field(..., description="New context version after sync")
    errors: Optional[List[str]] = Field(None, description="Any errors that occurred")


class ContextRetrievalRequest(BaseModel):
    """Request schema for context retrieval"""
    agent_id: str = Field(..., description="Agent ID")
    session_id: Optional[str] = Field(None, description="Session ID filter")
    user_id: Optional[str] = Field(None, description="User ID filter")
    include_history: bool = Field(True, description="Include conversation history")
    include_cache: bool = Field(True, description="Include cached data")
    max_history_items: int = Field(100, description="Maximum history items to return", gt=0, le=1000)


class ContextRetrievalResponse(BaseModel):
    """Response schema for context retrieval"""
    agent_id: str = Field(..., description="Agent ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    context: ContextData = Field(..., description="Retrieved context data")
    conversation_history: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Conversation history"
    )
    user_preferences: Dict[str, Any] = Field(
        default_factory=dict, 
        description="User preferences"
    )
    market_data_cache: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Market data cache"
    )
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    version: int = Field(..., description="Context version")
    node_id: Optional[str] = Field(None, description="Node that provided the context")


class SessionInfo(BaseModel):
    """Schema for session information"""
    session_id: str = Field(..., description="Session ID")
    agent_id: str = Field(..., description="Associated agent ID")
    user_id: Optional[str] = Field(None, description="User ID")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: Optional[datetime] = Field(None, description="Last activity time")
    message_count: int = Field(..., description="Number of messages in session")
    context_size_bytes: Optional[int] = Field(None, description="Context size in bytes")


class BackupInfo(BaseModel):
    """Schema for context backup information"""
    backup_id: str = Field(..., description="Backup ID")
    agent_id: str = Field(..., description="Agent ID")
    session_id: Optional[str] = Field(None, description="Session ID if session-specific")
    created_at: datetime = Field(..., description="Backup creation time")
    size_bytes: int = Field(..., description="Backup size in bytes")
    compression: Optional[str] = Field(None, description="Compression method used")
    checksum: Optional[str] = Field(None, description="Backup checksum for integrity")


class ContextUpdateRequest(BaseModel):
    """Request schema for updating specific context fields"""
    updates: Dict[str, Any] = Field(..., description="Fields to update")
    merge_strategy: str = Field("merge", description="Update strategy: merge, replace")
    create_backup: bool = Field(False, description="Create backup before update")
