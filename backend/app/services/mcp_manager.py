"""
MCP (Model Context Protocol) Manager for integrating external data sources
"""

import asyncio
import json
import subprocess
import httpx
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import os
import logging

from app.core.config import get_settings
from app.core.exceptions import MCPServerError

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class MCPServer:
    """Configuration for an MCP server"""
    name: str
    config: Dict[str, Any]
    status: str = "stopped"
    process: Optional[subprocess.Popen] = None
    last_health_check: Optional[datetime] = None
    error_count: int = 0


class MCPManager:
    """Manager for MCP servers and tool integrations"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.mcp_config: Dict[str, Any] = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def initialize(self):
        """Initialize MCP servers from configuration"""
        try:
            # Load MCP configuration
            await self._load_mcp_config()
            
            # Initialize servers with graceful error handling
            successful_servers = 0
            for server_name, config in self.mcp_config.get("mcpServers", {}).items():
                try:
                    await self._initialize_server(server_name, config)
                    successful_servers += 1
                    logger.info(f"Successfully initialized MCP server '{server_name}'")
                except Exception as server_error:
                    logger.warning(f"Failed to initialize MCP server '{server_name}': {server_error}")
                    continue
                
            logger.info(f"Initialized {successful_servers}/{len(self.mcp_config.get('mcpServers', {}))} MCP servers")
            
            if successful_servers == 0:
                logger.warning("No MCP servers initialized successfully, agent will work without MCP functionality")
            
        except Exception as e:
            logger.warning(f"Failed to initialize MCP servers: {e}")
            logger.warning("Agent will continue without MCP servers for MVP functionality")
    
    async def _load_mcp_config(self):
        """Load MCP server configuration"""
        try:
            config_path = settings.MCP_SERVERS_CONFIG_PATH
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.mcp_config = json.load(f)
                
                # Filter to only active servers
                active_servers = {}
                for name, config in self.mcp_config.get("mcpServers", {}).items():
                    if config.get("status") == "active":
                        active_servers[name] = config
                self.mcp_config["mcpServers"] = active_servers
                
                logger.info(f"Loaded MCP config from {config_path}, {len(active_servers)} active servers")
            else:
                logger.warning(f"MCP config file not found at {config_path}, using minimal config")
                # Minimal fallback config
                self.mcp_config = {
                    "mcpServers": {
                        "coingecko": {
                            "url": "https://mcp.api.coingecko.com/sse"
                        }
                    }
                }
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            # Fallback to minimal config
            self.mcp_config = {
                "mcpServers": {
                    "coingecko": {
                        "url": "https://mcp.api.coingecko.com/sse"
                    }
                }
            }
    
    async def _initialize_server(self, server_name: str, config: Dict[str, Any]):
        """Initialize a single MCP server"""
        try:
            server = MCPServer(name=server_name, config=config)
            
            # Handle different server types
            if "url" in config:
                # HTTP/SSE server
                await self._initialize_http_server(server)
            elif "command" in config:
                # Process-based server
                await self._initialize_process_server(server)
            else:
                raise ValueError(f"Invalid server configuration for {server_name}")
            
            # Only add to servers if initialization was successful
            if server.status == "running":
                self.servers[server_name] = server
                logger.info(f"Initialized MCP server: {server_name}")
            else:
                logger.warning(f"Failed to initialize MCP server {server_name}: status {server.status}")
            
        except Exception as e:
            logger.error(f"Failed to initialize server {server_name}: {e}")
            # Don't add failed servers to the list
    
    async def _initialize_http_server(self, server: MCPServer):
        """Initialize HTTP-based MCP server"""
        try:
            # Test connection
            response = await self.client.get(server.config["url"])
            if response.status_code == 200:
                server.status = "running"
            else:
                server.status = "error"
                
        except Exception as e:
            logger.error(f"Failed to connect to HTTP server {server.name}: {e}")
            server.status = "error"
    
    async def _initialize_process_server(self, server: MCPServer):
        """Initialize process-based MCP server"""
        try:
            # Prepare environment
            env = os.environ.copy()
            if "env" in server.config:
                env.update(server.config["env"])
            
            # Start the process
            process = subprocess.Popen(
                [server.config["command"]] + server.config["args"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for process to start
            await asyncio.sleep(2)
            
            # Check if process is running
            if process.poll() is None:
                server.process = process
                server.status = "running"
            else:
                stdout, stderr = process.communicate()
                raise Exception(f"Process failed to start: {stderr}")
                
        except Exception as e:
            logger.error(f"Failed to start process server {server.name}: {e}")
            server.status = "error"
    
    async def call_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call a tool on an MCP server"""
        if server_name not in self.servers:
            raise MCPServerError(f"Server {server_name} not found", server_name)
        
        server = self.servers[server_name]
        
        if server.status != "running":
            raise MCPServerError(f"Server {server_name} is not running", server_name)
        
        try:
            if "url" in server.config:
                return await self._call_http_tool(server, tool_name, parameters)
            else:
                return await self._call_process_tool(server, tool_name, parameters)
                
        except Exception as e:
            server.error_count += 1
            logger.error(f"Tool call failed on {server_name}: {e}")
            raise MCPServerError(f"Tool call failed: {e}", server_name)
    
    async def _call_http_tool(self, server: MCPServer, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call tool on HTTP-based server"""
        try:
            # Implement MCP protocol for HTTP servers
            payload = {
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }
            
            response = await self.client.post(
                server.config["url"],
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise Exception(f"HTTP tool call failed: {e}")
    
    async def _call_process_tool(self, server: MCPServer, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call tool on process-based server"""
        try:
            # Implement MCP protocol for process servers via stdin/stdout
            # This is a simplified implementation
            if server.process and server.process.poll() is None:
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": parameters
                    }
                }
                
                # Send request
                if server.process and server.process.poll() is None:
                    server.process.stdin.write(json.dumps(request) + "\n")
                    server.process.stdin.flush()
                    
                    # Read response
                    response_line = server.process.stdout.readline()
                    return json.loads(response_line.strip())
                else:
                    raise Exception("Process is not running")
            else:
                raise Exception("Process is not running")
                
        except Exception as e:
            raise Exception(f"Process tool call failed: {e}")
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools for a server"""
        if server_name not in self.servers:
            raise MCPServerError(f"Server {server_name} not found", server_name)
        
        # Implement tool listing based on MCP protocol
        try:
            return await self.call_tool(server_name, "tools/list", {})
        except Exception:
            # Return mock tools for now
            return self._get_mock_tools(server_name)
    
    def _get_mock_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """Get mock tools for development"""
        tools_map = {
            "coingecko": [
                {"name": "get_coin_price", "description": "Get current coin price"},
                {"name": "get_market_data", "description": "Get market data for coin"},
                {"name": "get_price_history", "description": "Get historical price data"}
            ],
            "ccxt": [
                {"name": "get_ticker", "description": "Get ticker data from exchange"},
                {"name": "get_orderbook", "description": "Get orderbook data"},
                {"name": "get_trades", "description": "Get recent trades"}
            ],
            "feargreed": [
                {"name": "get_fear_greed_index", "description": "Get current fear and greed index"},
                {"name": "get_fear_greed_history", "description": "Get historical fear and greed data"}
            ],
            "cryptopanic": [
                {"name": "get_news", "description": "Get crypto news"},
                {"name": "get_sentiment", "description": "Get news sentiment analysis"}
            ],
            "whaletracker": [
                {"name": "get_whale_alerts", "description": "Get whale transaction alerts"},
                {"name": "get_whale_stats", "description": "Get whale statistics"}
            ],
            "firecrawl": [
                {"name": "crawl_website", "description": "Crawl and extract website content"},
                {"name": "scrape_page", "description": "Scrape specific page content"}
            ]
        }
        
        return tools_map.get(server_name, [])
    
    async def list_all_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from all servers"""
        all_tools = []
        
        for server_name in self.servers:
            try:
                server_tools = await self.list_tools(server_name)
                for tool in server_tools:
                    tool["server"] = server_name
                    all_tools.append(tool)
            except Exception as e:
                logger.error(f"Failed to list tools for {server_name}: {e}")
        
        return all_tools
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all MCP servers"""
        health_status = {
            "healthy": True,
            "servers": {},
            "total_servers": len(self.servers),
            "running_servers": 0,
            "failed_servers": 0
        }
        
        for server_name, server in self.servers.items():
            try:
                # Check server status
                if server.status == "running":
                    if "url" in server.config:
                        # HTTP server health check
                        response = await self.client.get(server.config["url"], timeout=5.0)
                        server_healthy = response.status_code == 200
                    else:
                        # Process server health check
                        server_healthy = server.process and server.process.poll() is None
                else:
                    server_healthy = False
                
                health_status["servers"][server_name] = {
                    "status": "healthy" if server_healthy else "unhealthy",
                    "error_count": server.error_count,
                    "last_check": datetime.utcnow().isoformat()
                }
                
                if server_healthy:
                    health_status["running_servers"] += 1
                else:
                    health_status["failed_servers"] += 1
                    health_status["healthy"] = False
                    
            except Exception as e:
                health_status["servers"][server_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "error_count": server.error_count,
                    "last_check": datetime.utcnow().isoformat()
                }
                health_status["failed_servers"] += 1
                health_status["healthy"] = False
        
        return health_status
    
    async def cleanup(self):
        """Cleanup MCP servers"""
        for server_name, server in self.servers.items():
            try:
                if server.process:
                    server.process.terminate()
                    server.process.wait(timeout=5)
                    logger.info(f"Terminated MCP server: {server_name}")
            except Exception as e:
                logger.error(f"Error terminating server {server_name}: {e}")
        
        await self.client.aclose()
        logger.info("MCP Manager cleanup completed")
