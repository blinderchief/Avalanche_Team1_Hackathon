"""
SpectraQ Agent Backend - FastAPI Application Entry Point
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.core.config import get_settings
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.api.v1 import api_router
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.core.exceptions import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting SpectraQ Agent Backend...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Initialize Redis
        redis_client = await init_redis()
        if redis_client:
            app.state.redis = redis_client
            logger.info("Redis initialized")
        else:
            logger.warning("Redis not available, using in-memory storage")
            app.state.redis = None
        
        # Initialize MCP servers (full version)
        from app.services.mcp_manager import MCPManager
        mcp_manager = MCPManager()
        await mcp_manager.initialize()
        app.state.mcp_manager = mcp_manager
        logger.info("MCP servers initialized")
        
        # Initialize Gemini client
        from app.services.gemini_client import GeminiClient
        gemini_client = GeminiClient()
        app.state.gemini_client = gemini_client
        logger.info("Gemini AI client initialized")
        
        logger.info("✅ SpectraQ Agent Backend startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        logger.error("Shutting down due to startup error...")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down SpectraQ Agent Backend...")
    try:
        if redis_client:
            await redis_client.close()
        await mcp_manager.cleanup()
        await gemini_client.close()
        logger.info("✅ Shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="SpectraQ Agent API",
        description="AI Agent Backend for SpectraQ Prediction Markets",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Add CORS middleware - More permissive for MVP
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for MVP debugging
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "spectraq-agent-backend"}
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "SpectraQ Agent Backend API", 
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    return app


app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
