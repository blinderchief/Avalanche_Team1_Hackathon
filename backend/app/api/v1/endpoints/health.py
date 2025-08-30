"""
Health check and system status endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import datetime
import asyncio

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.services.mcp_manager import MCPManager
from app.services.gemini_client import GeminiClient

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": "spectraq-agent-backend",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    Detailed health check including all dependencies
    """
    health_status = {
        "overall_status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["components"]["database"] = {
            "status": "healthy",
            "response_time_ms": 0  # Could add timing
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    # Check Redis
    try:
        await redis.ping()
        health_status["components"]["redis"] = {
            "status": "healthy",
            "response_time_ms": 0
        }
    except Exception as e:
        health_status["components"]["redis"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    # Check MCP servers
    try:
        mcp_manager = MCPManager()
        mcp_status = await mcp_manager.health_check()
        health_status["components"]["mcp_servers"] = mcp_status
        
        if not mcp_status.get("healthy", False):
            health_status["overall_status"] = "degraded"
            
    except Exception as e:
        health_status["components"]["mcp_servers"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    # Check Gemini AI API
    try:
        gemini_client = GeminiClient()
        gemini_status = await gemini_client.health_check()
        health_status["components"]["gemini_api"] = gemini_status
        
        if not gemini_status.get("healthy", False):
            health_status["overall_status"] = "degraded"
            
    except Exception as e:
        health_status["components"]["gemini_api"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    return health_status


@router.get("/metrics")
async def get_system_metrics(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    Get system performance metrics
    """
    try:
        # Get Redis info
        redis_info = await redis.info()
        
        # Get database connection info
        # Note: This is a simplified version
        db_pool_size = 20  # From config
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "redis": {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory": redis_info.get("used_memory", 0),
                "used_memory_human": redis_info.get("used_memory_human", "0B"),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0)
            },
            "database": {
                "pool_size": db_pool_size,
                "status": "connected"
            },
            "system": {
                "uptime": "unknown",  # Could implement uptime tracking
                "version": "0.1.0"
            }
        }
        
        return metrics
        
    except Exception as e:
        return {
            "error": f"Failed to get metrics: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/readiness")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint
    """
    try:
        # Check if all critical services are ready
        checks = []
        
        # Database check
        try:
            await db.execute("SELECT 1")
            checks.append(("database", True, None))
        except Exception as e:
            checks.append(("database", False, str(e)))
        
        # Redis check
        try:
            await redis.ping()
            checks.append(("redis", True, None))
        except Exception as e:
            checks.append(("redis", False, str(e)))
        
        # MCP managers check
        try:
            mcp_manager = MCPManager()
            await mcp_manager.health_check()
            checks.append(("mcp_servers", True, None))
        except Exception as e:
            checks.append(("mcp_servers", False, str(e)))
        
        all_ready = all(check[1] for check in checks)
        
        return {
            "ready": all_ready,
            "checks": [
                {
                    "name": name,
                    "ready": ready,
                    "error": error
                }
                for name, ready, error in checks
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe endpoint
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
