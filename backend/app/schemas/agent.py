"""
Pydantic schemas for agent-related requests and responses
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class QueryType(str, Enum):
    """Types of queries the agent can handle"""
    MARKET_ANALYSIS = "market_analysis"
    PRICE_PREDICTION = "price_prediction"
    NEWS_SENTIMENT = "news_sentiment"
    ON_CHAIN_ANALYSIS = "on_chain_analysis"
    GENERAL_CRYPTO = "general_crypto"
    TRADING_ADVICE = "trading_advice"


class AgentQueryRequest(BaseModel):
    """Request schema for agent queries"""
    query: str = Field(..., description="User query text", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID for context continuity")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    query_type: Optional[QueryType] = Field(None, description="Type of query for optimization")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    stream: bool = Field(False, description="Whether to stream the response")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response", gt=0, le=8192)
    temperature: Optional[float] = Field(None, description="Response randomness", ge=0.0, le=2.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What's the predicted price of BTC next week based on current market sentiment?",
                "session_id": "session_123",
                "user_id": "user_456",
                "query_type": "price_prediction",
                "context": {"portfolio": ["BTC", "ETH"], "risk_tolerance": "medium"},
                "stream": False,
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }


class ToolCall(BaseModel):
    """Schema for tool calls made during query processing"""
    tool_name: str = Field(..., description="Name of the MCP tool called")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to the tool")
    result: Optional[Any] = Field(None, description="Result returned by the tool")
    execution_time_ms: Optional[int] = Field(None, description="Tool execution time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if tool call failed")


class DataSource(BaseModel):
    """Schema for data sources used in response generation"""
    name: str = Field(..., description="Name of the data source")
    type: str = Field(..., description="Type of data source (api, mcp, web, etc.)")
    last_updated: Optional[datetime] = Field(None, description="When the data was last updated")
    reliability_score: Optional[float] = Field(None, description="Reliability score 0-1", ge=0.0, le=1.0)


class AgentQueryResponse(BaseModel):
    """Response schema for agent queries"""
    id: str = Field(..., description="Unique response ID")
    response: str = Field(..., description="Agent's response text")
    session_id: Optional[str] = Field(None, description="Session ID used")
    query_type: Optional[QueryType] = Field(None, description="Detected query type")
    confidence_score: float = Field(..., description="Confidence in response accuracy", ge=0.0, le=1.0)
    tools_used: List[ToolCall] = Field(default_factory=list, description="Tools called during processing")
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources consulted")
    processing_time_ms: int = Field(..., description="Total processing time in milliseconds")
    token_usage: Dict[str, int] = Field(..., description="Token usage statistics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response creation time")
    follow_up_suggestions: Optional[List[str]] = Field(None, description="Suggested follow-up questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "resp_123",
                "response": "Based on current market analysis, BTC is showing bullish signals...",
                "session_id": "session_123",
                "query_type": "price_prediction",
                "confidence_score": 0.8,
                "tools_used": [
                    {
                        "tool_name": "coingecko_price_data",
                        "parameters": {"symbol": "bitcoin", "days": 30},
                        "result": {"price": 45000, "change_24h": 2.5},
                        "execution_time_ms": 250
                    }
                ],
                "data_sources": [
                    {
                        "name": "CoinGecko",
                        "type": "api",
                        "last_updated": "2025-08-30T10:00:00Z",
                        "reliability_score": 0.9
                    }
                ],
                "processing_time_ms": 1500,
                "token_usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
                "follow_up_suggestions": ["What about ETH price prediction?", "Show me the technical analysis"]
            }
        }


class SessionConfig(BaseModel):
    """Configuration for agent sessions"""
    model: Optional[str] = Field(None, description="LLM model to use")
    temperature: float = Field(0.7, description="Response randomness", ge=0.0, le=2.0)
    max_tokens: int = Field(4096, description="Maximum tokens per response", gt=0, le=8192)
    context_window: int = Field(10, description="Number of previous messages to remember", gt=0, le=50)
    tools_enabled: List[str] = Field(default_factory=lambda: ["all"], description="Enabled MCP tools")
    personalization: bool = Field(True, description="Enable personalized responses")
    risk_tolerance: Optional[str] = Field(None, description="User's risk tolerance for trading advice")


class AgentSessionCreate(BaseModel):
    """Request schema for creating agent sessions"""
    user_id: Optional[str] = Field(None, description="User ID for the session")
    config: Optional[SessionConfig] = Field(None, description="Session configuration")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional session metadata")


class AgentSessionResponse(BaseModel):
    """Response schema for agent sessions"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="Associated user ID")
    config: SessionConfig = Field(..., description="Session configuration")
    status: str = Field(..., description="Session status (active, inactive, expired)")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    message_count: int = Field(0, description="Number of messages in session")
    expires_at: Optional[datetime] = Field(None, description="Session expiration time")


class AgentDeployConfig(BaseModel):
    """Configuration for deploying agents to Gemini AI"""
    model: Optional[str] = Field(None, description="Base LLM model")
    mcp_tools: List[str] = Field(..., description="List of MCP tools to include")
    resource_requirements: Dict[str, Any] = Field(
        default_factory=lambda: {"gpu": "T4", "memory": "8GB", "replicas": 1}
    )
    network_preferences: Optional[List[str]] = Field(None, description="Preferred network regions")


class AgentDeployRequest(BaseModel):
    """Request schema for agent deployment"""
    agent_name: str = Field(..., description="Name for the deployed agent")
    agent_config: Dict[str, Any] = Field(..., description="ElizaOS agent configuration")
    deployment_config: AgentDeployConfig = Field(..., description="Deployment configuration")


class AgentDeployResponse(BaseModel):
    """Response schema for agent deployment"""
    agent_id: str = Field(..., description="Deployed agent ID")
    deployment_status: str = Field(..., description="Deployment status")
    endpoint_url: str = Field(..., description="Agent endpoint URL")
    network_nodes: List[str] = Field(default_factory=list, description="Deployed network nodes")
    deployment_timestamp: datetime = Field(..., description="Deployment time")
    estimated_cost_per_hour: Optional[float] = Field(None, description="Estimated hourly cost in USD")
