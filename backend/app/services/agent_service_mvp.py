"""
Simplified Agent Service for MVP - Processes queries using mock MCP data
"""

import uuid
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging
from dataclasses import asdict

from app.schemas.agent import (
    AgentQueryResponse, 
    ToolCall,
    DataSource,
    QueryType
)
from app.services.mcp_manager_mvp import MCPManagerMVP
from app.core.exceptions import AgentSessionError

logger = logging.getLogger(__name__)


class AgentServiceMVP:
    """Simplified Agent Service for MVP using mock MCP data"""
    
    def __init__(self, mcp_manager: MCPManagerMVP):
        self.mcp_manager = mcp_manager
        self.sessions = {}  # In-memory session storage for MVP
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentQueryResponse:
        """
        Process a user query through the SpectraQ AI Agent MVP
        
        Args:
            query: User query text
            session_id: Session ID for context continuity  
            user_id: User ID for personalization
            context: Additional context
        
        Returns:
            Agent response with mock data
        """
        start_time = datetime.utcnow()
        response_id = f"resp_{uuid.uuid4().hex[:8]}"
        
        try:
            # Analyze query to determine required tools
            query_analysis = await self._analyze_query(query)
            query_type = query_analysis.get("type", QueryType.GENERAL_CRYPTO)
            required_tools = query_analysis.get("tools", [])
            
            logger.info(f"Processing query: {query[:100]}...")
            logger.info(f"Query type: {query_type}, Required tools: {len(required_tools)}")
            
            # Execute required MCP tool calls
            tools_used = []
            data_sources = []
            tool_results = {}
            
            for tool_info in required_tools:
                try:
                    logger.info(f"Calling tool: {tool_info['server']}.{tool_info['tool']}")
                    
                    tool_result = await self.mcp_manager.call_tool(
                        tool_info["server"],
                        tool_info["tool"],
                        tool_info["parameters"]
                    )
                    
                    tool_call = ToolCall(
                        tool_name=f"{tool_info['server']}.{tool_info['tool']}",
                        parameters=tool_info["parameters"],
                        result=tool_result,
                        execution_time_ms=50,  # Mock execution time
                        error=None
                    )
                    
                    tools_used.append(tool_call)
                    
                    # Create unique key for tool results to avoid overwrites
                    if tool_info["tool"] == "get_coin_price":
                        symbol = tool_info["parameters"].get("symbol", "BTC")
                        tool_key = f"get_coin_price_{symbol}"
                    else:
                        tool_key = tool_info["tool"]
                    
                    tool_results[tool_key] = tool_result
                    
                    # Add data source info
                    data_sources.append(DataSource(
                        name=tool_info["server"].title(),
                        type="mcp",
                        last_updated=datetime.utcnow(),
                        reliability_score=0.9
                    ))
                    
                except Exception as e:
                    logger.warning(f"MCP tool call failed: {e}")
                    tools_used.append(ToolCall(
                        tool_name=f"{tool_info['server']}.{tool_info['tool']}",
                        parameters=tool_info["parameters"],
                        result=None,
                        execution_time_ms=None,
                        error=str(e)
                    ))
            
            # Generate AI response (mock for MVP)
            response_content = await self._generate_mock_response(
                query, query_type, tool_results
            )
            
            # Calculate confidence score
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
                token_usage={"prompt_tokens": 150, "completion_tokens": 300, "total_tokens": 450},  # Mock
                follow_up_suggestions=follow_ups
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise AgentSessionError(f"Query processing failed: {str(e)}", session_id)
    
    async def create_session(
        self,
        user_id: Optional[str] = None
    ) -> str:
        """Create a new agent session"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "status": "active",
            "created_at": datetime.utcnow(),
            "message_count": 0,
            "context": {"history": []}
        }
        
        self.sessions[session_id] = session_data
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details"""
        return self.sessions.get(session_id)
    
    # Private helper methods
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine type and required tools"""
        query_lower = query.lower().strip()
        
        # Handle simple greetings - no tools needed
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup", "what's up"]
        if query_lower in greetings or any(query_lower.startswith(g) for g in greetings):
            return {
                "type": QueryType.GENERAL_CRYPTO,
                "tools": [],  # No tools for greetings
                "confidence": 0.9
            }
        
        tools = []
        query_type = QueryType.GENERAL_CRYPTO
        
        # Price-related queries
        if any(word in query_lower for word in ["price", "cost", "value", "$", "bitcoin", "btc", "ethereum", "eth"]):
            query_type = QueryType.PRICE_PREDICTION
            
            # Extract coin symbol (simple keyword matching)
            symbol = "BTC"
            if any(word in query_lower for word in ["ethereum", "eth"]):
                symbol = "ETH"
            elif any(word in query_lower for word in ["cardano", "ada"]):
                symbol = "ADA"
            elif any(word in query_lower for word in ["solana", "sol"]):
                symbol = "SOL"
            
            tools.extend([
                {
                    "server": "coingecko",
                    "tool": "get_coin_price",
                    "parameters": {"symbol": symbol}
                },
                {
                    "server": "ccxt",
                    "tool": "get_ticker",
                    "parameters": {"symbol": f"{symbol}/USDT"}
                }
            ])
        
        # Market sentiment queries
        if any(word in query_lower for word in ["sentiment", "fear", "greed", "mood", "market", "feeling"]):
            query_type = QueryType.MARKET_ANALYSIS  # Changed from NEWS_SENTIMENT for better handling
            
            # If both Bitcoin and Ethereum mentioned, get data for both
            if any(word in query_lower for word in ["bitcoin", "btc"]) and any(word in query_lower for word in ["ethereum", "eth"]):
                tools.extend([
                    {
                        "server": "coingecko",
                        "tool": "get_coin_price",
                        "parameters": {"symbol": "BTC"}
                    },
                    {
                        "server": "coingecko",
                        "tool": "get_coin_price", 
                        "parameters": {"symbol": "ETH"}
                    },
                    {
                        "server": "ccxt",
                        "tool": "get_ticker",
                        "parameters": {"symbol": "ETH/USDT"}
                    }
                ])
            
            # Always add sentiment and news tools
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
        if any(word in query_lower for word in ["news", "headlines", "events", "happening", "latest"]):
            query_type = QueryType.NEWS_SENTIMENT
            tools.append({
                "server": "cryptopanic",
                "tool": "get_news",
                "parameters": {"filter": "hot"}
            })
        
        # Market analysis queries
        if any(word in query_lower for word in ["analysis", "analyze", "market", "trend", "technical"]):
            query_type = QueryType.MARKET_ANALYSIS
            tools.extend([
                {
                    "server": "coingecko",
                    "tool": "get_market_data",
                    "parameters": {}
                },
                {
                    "server": "feargreed",
                    "tool": "get_fear_greed_index",
                    "parameters": {}
                }
            ])
        
        # If no specific tools identified, use general market data
        if not tools:
            tools.extend([
                {
                    "server": "coingecko",
                    "tool": "get_coin_price",
                    "parameters": {"symbol": "BTC"}
                },
                {
                    "server": "feargreed",
                    "tool": "get_fear_greed_index",
                    "parameters": {}
                }
            ])
        
        return {
            "type": query_type,
            "tools": tools,
            "confidence": 0.8
        }
    
    async def _generate_mock_response(
        self,
        query: str,
        query_type: QueryType,
        tool_results: Dict[str, Any]
    ) -> str:
        """Generate a mock AI response based on query and tool results"""
        
        logger.info(f"Generating response for query type: {query_type}")
        logger.info(f"Available tool results: {list(tool_results.keys())}")
        
        # Handle simple greetings
        query_lower = query.lower().strip()
        if query_lower in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]:
            return "Hello! 👋 I'm SpectraQ AI Agent, your crypto market analysis assistant. I can help you with:\n\n• 📊 Real-time cryptocurrency prices and market data\n• 😱 Fear & Greed Index analysis\n• 📰 Latest crypto news and sentiment\n• 📈 Market trend analysis\n• 💡 Trading insights and predictions\n\nWhat would you like to know about the crypto market today?"
        
        # Build response based on query type and available data
        response_parts = []
        
        # Add greeting based on query type
        if query_type == QueryType.PRICE_PREDICTION:
            response_parts.append("📊 **Price Analysis Report**")
        elif query_type == QueryType.MARKET_ANALYSIS:
            response_parts.append("📈 **Market Analysis Report**")
        elif query_type == QueryType.NEWS_SENTIMENT:
            response_parts.append("📰 **Market News & Sentiment Report**")
        else:
            response_parts.append("🔍 **Crypto Market Intelligence**")
        
        response_parts.append("Here's my analysis based on the latest market data:\n")
        
        # Analyze actual tool results and provide insights
        if "get_coin_price_BTC" in tool_results:
            btc_data = tool_results["get_coin_price_BTC"]
            price = btc_data.get("price_usd", 0)
            change = btc_data.get("price_change_24h", 0)
            market_cap = btc_data.get("market_cap", 0)
            volume = btc_data.get("volume_24h", 0)
            
            response_parts.append("## Bitcoin (BTC) Analysis")
            response_parts.append(f"**Current Price:** ${price:,.2f}")
            response_parts.append(f"**24h Change:** {change:+.2f}% {'📈' if change > 0 else '📉'}")
            response_parts.append(f"**Market Cap:** ${market_cap:,.0f}")
            response_parts.append(f"**24h Volume:** ${volume:,.0f}")
            
            # Price analysis
            if change > 5:
                response_parts.append("**Analysis:** Strong bullish momentum with significant gains!")
            elif change > 0:
                response_parts.append("**Analysis:** Moderate upward movement, positive momentum.")
            elif change > -5:
                response_parts.append("**Analysis:** Slight decline, market showing resilience.")
            else:
                response_parts.append("**Analysis:** Significant bearish pressure, monitor closely.")
        
        if "get_coin_price_ETH" in tool_results:
            eth_data = tool_results["get_coin_price_ETH"]
            price = eth_data.get("price_usd", 0)
            change = eth_data.get("price_change_24h", 0)
            
            response_parts.append("\n## Ethereum (ETH) Analysis")
            response_parts.append(f"**Current Price:** ${price:,.2f}")
            response_parts.append(f"**24h Change:** {change:+.2f}% {'📈' if change > 0 else '📉'}")
            
            # Compare with BTC if both available
            if "get_coin_price_BTC" in tool_results:
                btc_price = tool_results["get_coin_price_BTC"].get("price_usd", 0)
                eth_btc_ratio = price / btc_price if btc_price > 0 else 0
                response_parts.append(f"**ETH/BTC Ratio:** {eth_btc_ratio:.4f}")
        
        # Fear & Greed Index Analysis
        if "get_fear_greed_index" in tool_results:
            fg_data = tool_results["get_fear_greed_index"]
            index = fg_data.get("index", 50)
            classification = fg_data.get("classification", "Neutral")
            trend = fg_data.get("trend", "stable")
            
            response_parts.append("\n## Market Sentiment (Fear & Greed Index)")
            response_parts.append(f"**Index Value:** {index}/100")
            response_parts.append(f"**Classification:** {classification}")
            response_parts.append(f"**Trend:** {trend.title()}")
            
            # Sentiment interpretation
            if index >= 75:
                response_parts.append("**Interpretation:** Extreme Greed - Market may be overheated, consider profit-taking.")
            elif index >= 55:
                response_parts.append("**Interpretation:** Greed - Bullish sentiment, but watch for corrections.")
            elif index >= 45:
                response_parts.append("**Interpretation:** Neutral - Balanced market sentiment.")
            elif index >= 25:
                response_parts.append("**Interpretation:** Fear - Bearish sentiment, potential buying opportunities.")
            else:
                response_parts.append("**Interpretation:** Extreme Fear - Market panic, long-term buying opportunity.")
        
        # News Analysis
        if "get_news" in tool_results:
            news_data = tool_results["get_news"]
            articles = news_data.get("articles", [])
            
            if articles:
                response_parts.append("\n## Latest Market News")
                for i, article in enumerate(articles[:3], 1):
                    title = article.get("title", "Market Update")
                    sentiment = article.get("sentiment", "neutral")
                    response_parts.append(f"{i}. **{title}**")
                    if sentiment != "neutral":
                        response_parts.append(f"   *Sentiment: {sentiment.title()}*")
        
        # Market Data Analysis
        if "get_market_data" in tool_results:
            market_data = tool_results["get_market_data"]
            dominance = market_data.get("market_dominance", "45%")
            total_volume = market_data.get("total_volume", "$32B")
            
            response_parts.append("\n## Market Overview")
            response_parts.append(f"**Bitcoin Dominance:** {dominance}")
            response_parts.append(f"**Total Market Volume:** {total_volume}")
        
        # Overall Market Assessment
        response_parts.append("\n## Overall Assessment")
        
        # Calculate market health based on available data
        bullish_signals = 0
        bearish_signals = 0
        
        if "get_coin_price_BTC" in tool_results:
            change = tool_results["get_coin_price_BTC"].get("price_change_24h", 0)
            if change > 0:
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        if "get_coin_price_ETH" in tool_results:
            change = tool_results["get_coin_price_ETH"].get("price_change_24h", 0)
            if change > 0:
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        if "get_fear_greed_index" in tool_results:
            index = tool_results["get_fear_greed_index"].get("index", 50)
            if index > 55:
                bullish_signals += 1
            elif index < 45:
                bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            response_parts.append("**Market Outlook:** Bullish momentum with positive signals across key indicators.")
        elif bearish_signals > bullish_signals:
            response_parts.append("**Market Outlook:** Bearish pressure, monitor for potential downside.")
        else:
            response_parts.append("**Market Outlook:** Mixed signals, market in consolidation phase.")
        
        # Add timestamp
        from datetime import datetime
        response_parts.append(f"\n*Analysis generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*")
        
        # Add disclaimer
        response_parts.append("\n---\n⚠️ **Disclaimer:** This analysis is for informational purposes only and not financial advice. Always do your own research and consult with financial professionals before making investment decisions.")
        
        return "\n".join(response_parts)
    
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
            QueryType.MARKET_ANALYSIS: 0.85,
            QueryType.PRICE_PREDICTION: 0.75,  # Lower due to inherent uncertainty
            QueryType.NEWS_SENTIMENT: 0.80,
            QueryType.GENERAL_CRYPTO: 0.70,
            QueryType.TRADING_ADVICE: 0.65  # Lower due to risk
        }.get(query_type, 0.70)
        
        return min(0.90, tool_success_rate * type_confidence)
    
    async def _update_session_context(
        self,
        session_id: str,
        query: str,
        response: str,
        tool_results: Dict[str, Any]
    ):
        """Update session context with new exchange"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Add to history
                session["context"]["history"].append({
                    "query": query,
                    "response": response[:200] + "...",  # Truncate for storage
                    "timestamp": datetime.utcnow().isoformat(),
                    "has_tool_data": bool(tool_results)
                })
                
                # Keep only last 10 exchanges for MVP
                session["context"]["history"] = session["context"]["history"][-10:]
                session["message_count"] = session.get("message_count", 0) + 1
                session["last_activity"] = datetime.utcnow()
                
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
                "What's the technical analysis looking like?"
            ],
            QueryType.NEWS_SENTIMENT: [
                "How is this affecting Bitcoin price?",
                "What other coins might be impacted?",
                "Show me more detailed market sentiment"
            ],
            QueryType.MARKET_ANALYSIS: [
                "What's your trading recommendation?",
                "Show me the fear and greed index",
                "What are the key support and resistance levels?"
            ],
            QueryType.GENERAL_CRYPTO: [
                "Tell me about Bitcoin price trends",
                "What's the current market sentiment?",
                "Show me recent crypto news"
            ]
        }
        
        return follow_ups.get(query_type or QueryType.GENERAL_CRYPTO, [
            "Tell me about Bitcoin's current price",
            "What's the market sentiment right now?",
            "Show me the latest crypto news"
        ])
