"""
API v1 Router - Main router for all v1 endpoints (MVP version)
"""

from fastapi import APIRouter

from app.api.v1.endpoints import agent_mvp, chat, context, health

api_router = APIRouter()

# Include all endpoint routers (using MVP agent)
api_router.include_router(
    agent_mvp.router, prefix="/agent", tags=["agent"]
)
api_router.include_router(
    chat.router, prefix="/chat", tags=["chat"]
)
api_router.include_router(
    context.router, prefix="/context", tags=["context"]
)
api_router.include_router(
    health.router, prefix="/health", tags=["health"]
)
