"""
Custom exception handlers for the application
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MCPServerError(Exception):
    """Exception raised when MCP server operations fail"""
    def __init__(self, message: str, server_name: Optional[str] = None):
        self.message = message
        self.server_name = server_name
        super().__init__(self.message)


class GeminiAPIError(Exception):
    """Exception raised when Gemini AI API calls fail"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AgentSessionError(Exception):
    """Exception raised when agent session operations fail"""
    def __init__(self, message: str, session_id: Optional[str] = None):
        self.message = message
        self.session_id = session_id
        super().__init__(self.message)


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup custom exception handlers"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Request validation failed",
                    "details": exc.errors()
                }
            }
        )
    
    @app.exception_handler(MCPServerError)
    async def mcp_server_exception_handler(request: Request, exc: MCPServerError):
        """Handle MCP server errors"""
        logger.error(f"MCP Server Error ({exc.server_name}): {exc.message}")
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "type": "MCPServerError",
                    "message": f"MCP server error: {exc.message}",
                    "server": exc.server_name
                }
            }
        )
    
    @app.exception_handler(GeminiAPIError)
    async def gemini_api_exception_handler(request: Request, exc: GeminiAPIError):
        """Handle Gemini AI API errors"""
        logger.error(f"Gemini API Error: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code or 503,
            content={
                "error": {
                    "type": "GeminiAPIError",
                    "message": f"AI service error: {exc.message}"
                }
            }
        )
    
    @app.exception_handler(AgentSessionError)
    async def agent_session_exception_handler(request: Request, exc: AgentSessionError):
        """Handle agent session errors"""
        logger.error(f"Agent Session Error ({exc.session_id}): {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "type": "AgentSessionError",
                    "message": f"Session error: {exc.message}",
                    "session_id": exc.session_id
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred"
                }
            }
        )
