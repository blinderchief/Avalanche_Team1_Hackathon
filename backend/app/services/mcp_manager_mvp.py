"""
Simplified MCP Manager for MVP - Uses mock data for demonstration
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import random

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class MockMCPServer:
    """Mock MCP server for MVP"""
    name: str
    status: str = "active"
    description: str = ""
    tools: List[Dict[str, Any]] = None


class MCPManagerMVP:
    """Simplified MCP Manager for MVP using mock data"""
    
    def __init__(self):
        self.servers: Dict[str, MockMCPServer] = {}
        self.mock_data = self._initialize_mock_data()
        
    async def initialize(self):
        """Initialize mock MCP servers"""
        try:
            logger.info("Initializing MVP MCP servers with mock data...")
            
            # Create mock servers
            self.servers = {
                "coingecko": MockMCPServer(
                    name="coingecko",
                    status="active",
                    description="Market data and cryptocurrency information",
                    tools=[
                        {"name": "get_coin_price", "description": "Get current coin price"},
                        {"name": "get_market_data", "description": "Get market data for coin"},
                        {"name": "get_price_history", "description": "Get historical price data"}
                    ]
                ),
                "ccxt": MockMCPServer(
                    name="ccxt",
                    status="active", 
                    description="Exchange data and trading information",
                    tools=[
                        {"name": "get_ticker", "description": "Get ticker data from exchange"},
                        {"name": "get_orderbook", "description": "Get orderbook data"},
                        {"name": "get_trades", "description": "Get recent trades"}
                    ]
                ),
                "feargreed": MockMCPServer(
                    name="feargreed",
                    status="active",
                    description="Crypto Fear & Greed Index sentiment indicator", 
                    tools=[
                        {"name": "get_fear_greed_index", "description": "Get current fear and greed index"},
                        {"name": "get_fear_greed_history", "description": "Get historical fear and greed data"}
                    ]
                ),
                "cryptopanic": MockMCPServer(
                    name="cryptopanic",
                    status="available",
                    description="Cryptocurrency news aggregation",
                    tools=[
                        {"name": "get_news", "description": "Get crypto news"},
                        {"name": "get_sentiment", "description": "Get news sentiment analysis"}
                    ]
                ),
                "firecrawl": MockMCPServer(
                    name="firecrawl", 
                    status="available",
                    description="Web crawling and content extraction",
                    tools=[
                        {"name": "crawl_website", "description": "Crawl and extract website content"},
                        {"name": "scrape_page", "description": "Scrape specific page content"}
                    ]
                )
            }
            
            logger.info(f"Successfully initialized {len(self.servers)} mock MCP servers")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP servers: {e}")
    
    def _initialize_mock_data(self) -> Dict[str, Any]:
        """Initialize mock data for different tools"""
        return {
            "btc_price": 43250.30,
            "eth_price": 2650.45,
            "fear_greed_index": 58,
            "market_trend": "bullish",
            "news_sentiment": "positive",
            "trading_volume_24h": "2.5B"
        }
    
    async def call_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on a mock MCP server"""
        if server_name not in self.servers:
            logger.warning(f"Server {server_name} not found, returning mock data")
            return {"error": f"Server {server_name} not available", "mock_response": True}
        
        server = self.servers[server_name]
        
        try:
            logger.info(f"Calling tool {tool_name} on server {server_name} with params: {parameters}")
            
            # Generate mock response based on server and tool
            response = await self._generate_mock_response(server_name, tool_name, parameters)
            
            # Add metadata
            response.update({
                "server": server_name,
                "tool": tool_name,
                "timestamp": datetime.utcnow().isoformat(),
                "mock_data": True  # Indicate this is mock data for MVP
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Tool call failed on {server_name}: {e}")
            return {
                "error": str(e),
                "server": server_name,
                "tool": tool_name,
                "mock_data": True
            }
    
    async def _generate_mock_response(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock response data"""
        
        # CoinGecko mock responses
        if server_name == "coingecko":
            if tool_name == "get_coin_price":
                symbol = parameters.get("symbol", "BTC").upper()
                base_prices = {"BTC": 43250.30, "ETH": 2650.45, "ADA": 0.45, "SOL": 98.75}
                price = base_prices.get(symbol, 100.0)
                # Add some random variation
                price *= (1 + random.uniform(-0.02, 0.02))
                
                return {
                    "symbol": symbol,
                    "price_usd": round(price, 2),
                    "price_change_24h": round(random.uniform(-5.0, 5.0), 2),
                    "market_cap": round(price * random.randint(18000000, 21000000), 2),
                    "volume_24h": round(price * random.randint(100000, 500000), 2)
                }
                
            elif tool_name == "get_market_data":
                return {
                    "market_cap_rank": random.randint(1, 10),
                    "total_volume": f"${random.randint(20, 50)}B",
                    "market_dominance": f"{random.randint(40, 60)}%",
                    "fear_greed_index": random.randint(20, 80)
                }
                
        # CCXT mock responses  
        elif server_name == "ccxt":
            if tool_name == "get_ticker":
                return {
                    "exchange": "binance",
                    "symbol": parameters.get("symbol", "BTC/USDT"),
                    "bid": 43200.50,
                    "ask": 43210.80,
                    "last": 43205.65,
                    "volume": random.randint(1000, 5000),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        # Fear & Greed Index mock responses
        elif server_name == "feargreed":
            if tool_name == "get_fear_greed_index":
                index_value = random.randint(20, 80)
                classification = "Neutral"
                if index_value < 25:
                    classification = "Extreme Fear"
                elif index_value < 45:
                    classification = "Fear"
                elif index_value > 75:
                    classification = "Extreme Greed"
                elif index_value > 55:
                    classification = "Greed"
                
                return {
                    "index": index_value,
                    "classification": classification,
                    "timestamp": datetime.utcnow().isoformat(),
                    "historical_avg": 50,
                    "trend": "increasing" if index_value > 50 else "decreasing"
                }
                
        # CryptoPanic mock responses
        elif server_name == "cryptopanic":
            if tool_name == "get_news":
                return {
                    "articles": [
                        {
                            "title": "Bitcoin Shows Strong Recovery After Recent Dip",
                            "url": "https://example.com/news1",
                            "source": "CryptoNews",
                            "published_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                            "sentiment": "positive"
                        },
                        {
                            "title": "Ethereum 2.0 Upgrade Shows Promising Results",
                            "url": "https://example.com/news2", 
                            "source": "CoinDesk",
                            "published_at": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                            "sentiment": "positive"
                        },
                        {
                            "title": "Market Analysis: Crypto Winter May Be Ending",
                            "url": "https://example.com/news3",
                            "source": "CryptoSlate",
                            "published_at": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                            "sentiment": "neutral"
                        }
                    ],
                    "total_articles": 3,
                    "overall_sentiment": "positive"
                }
                
        # Firecrawl mock responses
        elif server_name == "firecrawl":
            if tool_name == "scrape_page":
                return {
                    "url": parameters.get("url", "https://example.com"),
                    "title": "Crypto Market Analysis",
                    "content": "Recent analysis shows positive trends in the cryptocurrency market with increased institutional adoption...",
                    "metadata": {
                        "word_count": 450,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                }
        
        # Default response
        return {
            "message": f"Mock response for {tool_name} from {server_name}",
            "parameters_received": parameters,
            "status": "success"
        }
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools for a server"""
        if server_name not in self.servers:
            return []
        
        return self.servers[server_name].tools or []
    
    async def list_all_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from all servers"""
        all_tools = []
        
        for server_name, server in self.servers.items():
            for tool in server.tools or []:
                tool_info = tool.copy()
                tool_info["server"] = server_name
                tool_info["server_description"] = server.description
                all_tools.append(tool_info)
        
        return all_tools
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all MCP servers"""
        return {
            "healthy": True,
            "servers": {
                name: {
                    "status": server.status,
                    "description": server.description,
                    "tools_count": len(server.tools or [])
                } for name, server in self.servers.items()
            },
            "total_servers": len(self.servers),
            "running_servers": len([s for s in self.servers.values() if s.status == "active"]),
            "mock_data_mode": True,
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup MCP servers"""
        logger.info("MVP MCP Manager cleanup completed (no cleanup needed for mock servers)")
