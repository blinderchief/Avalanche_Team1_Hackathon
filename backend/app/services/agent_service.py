"""
Agent service for handling queries and managing agent interactions
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
from app.services.spectra_graph import SpectraQGraph
from app.core.config import get_settings
from app.core.exceptions import MCPServerError, AgentSessionError

logger = logging.getLogger(__name__)

settings = get_settings()


class AgentService:
    """Service for handling agent queries and sessions"""
    
    def __init__(self, db: AsyncSession, redis_client: Optional[redis.Redis]):
        self.db = db
        self.redis = redis_client
        self.mcp_manager = MCPManager()
        self.gemini_client = GeminiClient()
        self.spectra_graph = SpectraQGraph(
            self.mcp_manager, self.gemini_client)
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        use_langgraph: bool = False
    ) -> AgentQueryResponse:
        """
        Process a user query through the SpectraQ AI Agent
        
        Args:
            query: User query text
            session_id: Session ID for context continuity
            user_id: User ID for personalization
            context: Additional context
        
        Returns:
            Agent response
        """
        start_time = datetime.utcnow()
        response_id = f"resp_{uuid.uuid4().hex[:8]}"
        
        # Use LangGraph for enhanced processing with compliance checks
        if use_langgraph:
            try:
                graph_result = await self.spectra_graph.process_query(query, context)

                # Convert LangGraph result to AgentQueryResponse format
                return AgentQueryResponse(
                    id=response_id,
                    response=graph_result["response"],
                    session_id=session_id,
                    query_type=QueryType.COMPLIANCE_AUDIT if graph_result.get(
                        "compliance_audit") else QueryType.GENERAL_CRYPTO,
                    confidence_score=graph_result["confidence_score"],
                    tools_used=[],  # TODO: Extract from graph result
                    data_sources=[],
                    processing_time_ms=int(
                        (datetime.utcnow() - start_time).total_seconds() * 1000),
                    token_usage={},
                    follow_up_suggestions=[]
                )
            except Exception as e:
                logger.warning(
                    f"LangGraph processing failed, falling back to simple agent: {e}")

        try:
            # Analyze query to determine required tools
            query_analysis = await self._analyze_query(query)
            query_type = query_analysis.get("type", QueryType.GENERAL_CRYPTO)
            required_tools = query_analysis.get("tools", [])
            
            # Get session context if available
            session_context = await self._get_session_context(session_id) if session_id else {}
            
            # Prepare conversation context
            conversation_context = await self._prepare_conversation_context(
                query, session_context, context or {}
            )
            
            # Execute required MCP tool calls
            tools_used = []
            data_sources = []
            tool_results = {}
            
            if required_tools:
                for tool_info in required_tools:
                    try:
                        tool_result = await self.mcp_manager.call_tool(
                            tool_info["server"],
                            tool_info["tool"],
                            tool_info["parameters"]
                        )
                        
                        tool_call = ToolCall(
                            tool_name=f"{tool_info['server']}.{tool_info['tool']}",
                            parameters=tool_info["parameters"],
                            result=tool_result,
                            execution_time_ms=100,  # TODO: Measure actual time
                            error=None
                        )
                        
                        tools_used.append(tool_call)
                        tool_results[tool_info["tool"]] = tool_result
                        
                        # Add data source info
                        data_sources.append(DataSource(
                            name=tool_info["server"].title(),
                            type="mcp",
                            last_updated=datetime.utcnow(),
                            reliability_score=0.9  # TODO: Calculate actual reliability
                        ))
                        
                    except MCPServerError as e:
                        logger.warning(f"MCP tool call failed: {e}")
                        # Continue with available data - don't add failed tool to results
                        continue
                    except Exception as e:
                        logger.warning(f"Unexpected error in MCP tool call: {e}")
                        # Continue with available data
                        continue
            
            # Prepare messages for LLM
            messages = await self._build_llm_messages(
                query, conversation_context, tool_results, query_type
            )
            
            # Get AI response using Gemini AI
            llm_response = await self.gemini_client.chat_completion(
                messages=messages,
                model=settings.DEFAULT_MODEL,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract response content
            response_content = llm_response["choices"][0]["message"]["content"]
            token_usage = llm_response.get("usage", {})
            
            # Calculate confidence score based on available data
            confidence_score = self._calculate_confidence_score(
                tools_used, len(required_tools), query_type
            )
            
            # Update session context if session exists
            if session_id:
                await self._update_session_context(
                    session_id, query, response_content, tool_results
                )
            
            # Calculate processing time
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Generate follow-up suggestions
            follow_ups = await self._generate_follow_ups(query_type, response_content)
            
            return AgentQueryResponse(
                id=response_id,
                response=response_content,
                session_id=session_id,
                query_type=query_type,
                confidence_score=confidence_score,
                tools_used=tools_used,
                data_sources=data_sources,
                processing_time_ms=processing_time,
                token_usage=token_usage,
                follow_up_suggestions=follow_ups
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise AgentSessionError(f"Query processing failed: {str(e)}", session_id)
    
    async def stream_query_response(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream query response in real-time
        
        Yields:
            Response chunks with type, content, and metadata
        """
        try:
            yield {
                "type": "start",
                "content": "",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Analyze query
            yield {
                "type": "analysis",
                "content": "Analyzing your query...",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            query_analysis = await self._analyze_query(query)
            required_tools = query_analysis.get("tools", [])
            
            # Execute tools
            if required_tools:
                yield {
                    "type": "tools",
                    "content": f"Fetching data from {len(required_tools)} sources...",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            tool_results = {}
            for tool_info in required_tools:
                try:
                    tool_result = await self.mcp_manager.call_tool(
                        tool_info["server"],
                        tool_info["tool"],
                        tool_info["parameters"]
                    )
                    tool_results[tool_info["tool"]] = tool_result
                    
                    yield {
                        "type": "tool_result",
                        "content": f"Retrieved data from {tool_info['server']}",
                        "tool": tool_info["tool"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    yield {
                        "type": "tool_error",
                        "content": f"Failed to get data from {tool_info['server']}: {str(e)}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            # Generate response
            yield {
                "type": "generating",
                "content": "Analyzing data and generating response...",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Prepare context and messages
            session_context = await self._get_session_context(session_id) if session_id else {}
            conversation_context = await self._prepare_conversation_context(
                query, session_context, context or {}
            )
            
            messages = await self._build_llm_messages(
                query, conversation_context, tool_results, query_analysis.get("type")
            )
            
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
                "content": f"Error processing query: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_session(
        self,
        user_id: Optional[str] = None,
        session_config: Optional[SessionConfig] = None
    ) -> AgentSessionResponse:
        """Create a new agent session"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
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
            "created_at": datetime.utcnow().isoformat(),
            "message_count": 0,
            "context": {}
        }
        
        # Store in Redis with expiration (if available)
        if self.redis:
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
            created_at=datetime.utcnow(),
            last_activity=None,
            message_count=0,
            expires_at=datetime.utcnow() + timedelta(hours=2)
        )
    
    async def get_session(self, session_id: str) -> Optional[AgentSessionResponse]:
        """Get session details"""
        if not self.redis:
            return None
            
        try:
            session_data = await self.redis.get(f"session:{session_id}")
            if not session_data:
                return None
            
            data = json.loads(session_data)
            return AgentSessionResponse(**data)
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if not self.redis:
            return False
            
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
        if not self.redis:
            return
            
        try:
            log_entry = {
                "query": query,
                "response_length": len(response),
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in Redis list for analytics
            await self.redis.lpush("query_logs", json.dumps(log_entry))
            await self.redis.ltrim("query_logs", 0, 10000)  # Keep last 10k queries
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
    
    # Private helper methods
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine type and required tools"""
        # Simple keyword-based analysis (can be enhanced with ML)
        query_lower = query.lower()
        
        tools = []
        query_type = QueryType.GENERAL_CRYPTO
        
        # Price-related queries
        if any(word in query_lower for word in ["price", "cost", "value", "$"]):
            query_type = QueryType.PRICE_PREDICTION
            tools.append({
                "server": "coingecko",
                "tool": "get_coin_price",
                "parameters": {"symbol": "bitcoin"}  # TODO: Extract from query
            })
        
        # Market sentiment
        if any(word in query_lower for word in ["sentiment", "fear", "greed", "mood"]):
            query_type = QueryType.NEWS_SENTIMENT
            tools.extend([
                {
                    "server": "feargreed",
                    "tool": "get_fear_greed_index",
                    "parameters": {}
                },
                {
                    "server": "cryptopanic",
                    "tool": "get_news",
                    "parameters": {"filter": "rising"}
                }
            ])
        
        # News queries
        if any(word in query_lower for word in ["news", "headlines", "events"]):
            query_type = QueryType.NEWS_SENTIMENT
            tools.append({
                "server": "cryptopanic",
                "tool": "get_news",
                "parameters": {"filter": "hot"}
            })
        
        # Whale/on-chain analysis
        if any(word in query_lower for word in ["whale", "large", "transactions", "on-chain"]):
            query_type = QueryType.ON_CHAIN_ANALYSIS
            tools.append({
                "server": "whaletracker",
                "tool": "get_whale_alerts",
                "parameters": {"min_value": 1000000}
            })
        
        # Compliance audit queries
        if any(word in query_lower for word in ["audit", "compliance", "contract", "smart contract", "regulatory", "aml", "gdpr", "kyc"]):
            query_type = QueryType.COMPLIANCE_AUDIT
            # Extract contract code if present in query (simplified)
            contract_code = self._extract_contract_code(query)
            standards = self._extract_standards(query)

            if contract_code:
                tools.append({
                    "server": "complai",
                    "tool": "compliance_audit",
                    "parameters": {
                        "contract_code": contract_code,
                        "standards": standards
                    }
                })

        return {
            "type": query_type,
            "tools": tools,
            "confidence": 0.8
        }
    
    async def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context from Redis"""
        if not self.redis:
            return {}
            
        try:
            session_data = await self.redis.get(f"session:{session_id}")
            if session_data:
                data = json.loads(session_data)
                return data.get("context", {})
        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
        return {}
    
    async def _prepare_conversation_context(
        self,
        current_query: str,
        session_context: Dict[str, Any],
        additional_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare conversation context for LLM"""
        context = {
            "current_query": current_query,
            "session_history": session_context.get("history", [])[-5:],  # Last 5 exchanges
            "user_preferences": session_context.get("preferences", {}),
            **additional_context
        }
        return context
    
    async def _build_llm_messages(
        self,
        query: str,
        context: Dict[str, Any],
        tool_results: Dict[str, Any],
        query_type: Optional[QueryType]
    ) -> List[Dict[str, str]]:
        """Build messages for LLM"""
        messages = [
            {
                "role": "user",
                "content": f"""You are SpectraQ AI Agent, an expert in cryptocurrency markets and trading. 
                
Your capabilities include:
- Market analysis and price predictions
- News sentiment analysis
- On-chain data interpretation
- Trading recommendations with risk assessment

Query type: {query_type.value if query_type else 'general'}

Available data from tools:
{json.dumps(tool_results, indent=2) if tool_results else 'No additional data available'}

Provide accurate, helpful responses. Include confidence levels and cite sources when available.
Always include appropriate risk disclaimers for financial advice.

You are powered by Google Gemini AI infrastructure."""
            }
        ]
        
        # Add conversation history
        for exchange in context.get("session_history", []):
            messages.extend([
                {"role": "user", "content": exchange.get("query", "")},
                {"role": "assistant", "content": exchange.get("response", "")}
            ])
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def _calculate_confidence_score(
        self,
        tools_used: List[ToolCall],
        required_tools: int,
        query_type: QueryType
    ) -> float:
        """Calculate confidence score for the response"""
        successful_tools = sum(1 for tool in tools_used if not tool.error)
        
        if required_tools == 0:
            return 0.7  # Base confidence for general queries
        
        tool_success_rate = successful_tools / required_tools if required_tools > 0 else 1.0
        
        # Adjust based on query type
        type_confidence = {
            QueryType.MARKET_ANALYSIS: 0.9,
            QueryType.PRICE_PREDICTION: 0.7,  # Lower due to inherent uncertainty
            QueryType.NEWS_SENTIMENT: 0.85,
            QueryType.ON_CHAIN_ANALYSIS: 0.9,
            QueryType.GENERAL_CRYPTO: 0.8,
            QueryType.TRADING_ADVICE: 0.6  # Lower due to risk
        }.get(query_type, 0.7)
        
        return min(0.95, tool_success_rate * type_confidence)
    
    async def _update_session_context(
        self,
        session_id: str,
        query: str,
        response: str,
        tool_results: Dict[str, Any]
    ):
        """Update session context with new exchange"""
        try:
            session_key = f"session:{session_id}"
            session_data = await self.redis.get(session_key)
            
            if session_data:
                data = json.loads(session_data)
                
                # Add to history
                if "context" not in data:
                    data["context"] = {}
                if "history" not in data["context"]:
                    data["context"]["history"] = []
                
                data["context"]["history"].append({
                    "query": query,
                    "response": response,
                    "timestamp": datetime.utcnow().isoformat(),
                    "tools_data": tool_results
                })
                
                # Keep only last 20 exchanges
                data["context"]["history"] = data["context"]["history"][-20:]
                data["message_count"] = data.get("message_count", 0) + 1
                data["last_activity"] = datetime.utcnow().isoformat()
                
                # Update in Redis
                if self.redis:
                    await self.redis.setex(
                        session_key,
                        int(timedelta(hours=2).total_seconds()),
                        json.dumps(data, default=str)
                    )
                
        except Exception as e:
            logger.error(f"Failed to update session context: {e}")
    
    async def _generate_follow_ups(
        self,
        query_type: Optional[QueryType],
        response: str
    ) -> List[str]:
        """Generate follow-up question suggestions"""
        follow_ups = {
            QueryType.PRICE_PREDICTION: [
                "What factors are driving this price movement?",
                "How does this compare to other cryptocurrencies?",
                "What's the risk level of this prediction?"
            ],
            QueryType.NEWS_SENTIMENT: [
                "How is this affecting Bitcoin price?",
                "What other coins might be impacted?",
                "Show me the most recent news headlines"
            ],
            QueryType.ON_CHAIN_ANALYSIS: [
                "What does this mean for retail investors?",
                "Are there similar patterns in other tokens?",
                "Show me the whale transaction details"
            ],
            QueryType.MARKET_ANALYSIS: [
                "What's your trading recommendation?",
                "How does technical analysis look?",
                "What are the key support levels?"
            ],
            QueryType.COMPLIANCE_AUDIT: [
                "What are the most critical issues to fix first?",
                "How can I implement these compliance fixes?",
                "Are there any regulatory deadlines I need to meet?"
            ]
        }
        
        return follow_ups.get(query_type, [
            "Tell me more about cryptocurrency markets",
            "What should I know about crypto investing?",
            "Show me current market trends"
        ]) if query_type else [
            "Tell me more about cryptocurrency markets",
            "What should I know about crypto investing?",
            "Show me current market trends"
        ]

    def _extract_contract_code(self, query: str) -> Optional[str]:
        """Extract smart contract code from query (simplified)"""
        # Look for code blocks or contract patterns
        import re

        # Check for Solidity code blocks
        code_match = re.search(r'```solidity\s*(.*?)\s*```', query, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # Check for generic code blocks
        code_match = re.search(r'```\s*(.*?)\s*```', query, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # Look for contract keywords and extract following text
        contract_keywords = ['contract', 'function', 'pragma', 'solidity']
        if any(keyword in query.lower() for keyword in contract_keywords):
            # Return the query as potential contract code
            return query

        return None

    def _extract_standards(self, query: str) -> List[str]:
        """Extract compliance standards from query"""
        standards = []
        query_lower = query.lower()

        if 'aml' in query_lower or 'money laundering' in query_lower:
            standards.append('AML')
        if 'gdpr' in query_lower or 'privacy' in query_lower:
            standards.append('GDPR')
        if 'kyc' in query_lower or 'know your customer' in query_lower:
            standards.append('KYC')
        if 'eerc' in query_lower or 'enhanced erc' in query_lower or 'avalanche' in query_lower:
            standards.append('eERC')

        # Default standards if none specified
        if not standards:
            standards = ['AML', 'GDPR', 'KYC']

        return standards
