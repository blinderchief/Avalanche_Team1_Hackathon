"""
Pydantic schemas for chat-related requests and responses
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Types of chat messages"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class MessageRole(str, Enum):
    """OpenAI-compatible message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ToolCallData(BaseModel):
    """Schema for tool call information in messages"""
    id: str = Field(..., description="Tool call ID")
    type: str = Field("function", description="Type of tool call")
    function: Dict[str, Any] = Field(..., description="Function call details")


class ChatMessage(BaseModel):
    """Schema for chat messages"""
    role: MessageRole = Field(MessageRole.USER, description="Message role")
    content: str = Field(..., description="Message content", min_length=1, max_length=4000)
    session_id: Optional[str] = Field(None, description="Session ID for context")
    user_id: Optional[str] = Field(None, description="User ID")
    message_type: MessageType = Field(MessageType.USER, description="Type of message")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    tool_calls: Optional[List[ToolCallData]] = Field(None, description="Tool calls in the message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Message metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What's the current Bitcoin price and market sentiment?",
                "session_id": "chat_session_123",
                "user_id": "user_456",
                "message_type": "user",
                "context": {"previous_query": "crypto analysis"},
                "metadata": {"timestamp": "2025-08-30T10:00:00Z"}
            }
        }


class ChatChoice(BaseModel):
    """Schema for chat completion choices"""
    index: int = Field(..., description="Choice index")
    message: Dict[str, Any] = Field(..., description="Message content")
    finish_reason: Optional[str] = Field(None, description="Reason for completion finish")


class UsageInfo(BaseModel):
    """Schema for token usage information"""
    prompt_tokens: int = Field(..., description="Tokens in the prompt")
    completion_tokens: int = Field(..., description="Tokens in the completion")
    total_tokens: int = Field(..., description="Total tokens used")


class ChatMessageResponse(BaseModel):
    """OpenAI-compatible chat completion response"""
    id: str = Field(..., description="Unique response ID")
    object: str = Field("chat.completion", description="Object type")
    created: int = Field(..., description="Unix timestamp")
    model: str = Field(..., description="Model used")
    choices: List[ChatChoice] = Field(..., description="Response choices")
    usage: UsageInfo = Field(..., description="Token usage information")
    
    # SpectraQ-specific fields
    session_id: Optional[str] = Field(None, description="Session ID")
    tools_used: List[str] = Field(default_factory=list, description="MCP tools used")
    data_sources: List[str] = Field(default_factory=list, description="Data sources consulted")
    confidence_score: Optional[float] = Field(None, description="Response confidence", ge=0.0, le=1.0)
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1693723200,
                "model": "spectraq-agent-v1",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Bitcoin is currently trading at $45,000 with bullish sentiment..."
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "total_tokens": 150
                },
                "session_id": "chat_session_123",
                "tools_used": ["coingecko", "feargreed"],
                "data_sources": ["CoinGecko API", "Fear & Greed Index"],
                "confidence_score": 0.9,
                "processing_time_ms": 2500
            }
        }


class ChatHistoryRequest(BaseModel):
    """Request schema for chat history"""
    session_id: str = Field(..., description="Session ID to get history for")
    user_id: Optional[str] = Field(None, description="User ID for authorization")
    limit: int = Field(50, description="Maximum number of messages", gt=0, le=200)
    offset: int = Field(0, description="Offset for pagination", ge=0)
    message_types: Optional[List[MessageType]] = Field(None, description="Filter by message types")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")


class MessageSummary(BaseModel):
    """Summary schema for chat messages"""
    id: str = Field(..., description="Message ID")
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(..., description="Message type")
    timestamp: datetime = Field(..., description="Message timestamp")
    token_count: Optional[int] = Field(None, description="Token count")
    tools_used: List[str] = Field(default_factory=list, description="Tools used in message")


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history"""
    messages: List[MessageSummary] = Field(..., description="Chat messages")
    total_count: int = Field(..., description="Total message count")
    has_more: bool = Field(..., description="Whether more messages are available")
    session_id: str = Field(..., description="Session ID")
    session_created: Optional[datetime] = Field(None, description="When the session was created")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class StreamChunk(BaseModel):
    """Schema for streaming response chunks"""
    id: str = Field(..., description="Chunk ID")
    type: str = Field(..., description="Chunk type (start, content, tool_call, end)")
    content: str = Field("", description="Chunk content")
    delta: Optional[Dict[str, Any]] = Field(None, description="Delta information")
    tool_call: Optional[ToolCallData] = Field(None, description="Tool call information")
    finish_reason: Optional[str] = Field(None, description="Completion finish reason")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Chunk timestamp")


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages"""
    type: str = Field(..., description="Message type")
    content: Optional[str] = Field(None, description="Message content")
    session_id: str = Field(..., description="Session ID")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
