"""
Chat endpoints for real-time messaging with SpectraQ Agent
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.schemas.chat import (
    ChatMessage,
    ChatMessageResponse,
    ChatHistoryRequest,
    ChatHistoryResponse
)
from app.services.chat_service import ChatService
from app.services.websocket_manager import WebSocketManager

router = APIRouter()
websocket_manager = WebSocketManager()


@router.post("/completions", response_model=ChatMessageResponse)
async def chat_completion(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> ChatMessageResponse:
    """
    OpenAI-compatible chat completion endpoint for SpectraQ Agent
    
    This endpoint mimics OpenAI's chat/completions API structure
    while using Gemini AI and MCP integration internally
    """
    try:
        chat_service = ChatService(db, redis)
        
        response = await chat_service.process_chat_message(
            message=message.content,
            session_id=message.session_id,
            user_id=message.user_id,
            message_type=message.message_type,
            context=message.context
        )
        
        return ChatMessageResponse(
            id=response["id"],
            object="chat.completion",
            created=int(datetime.utcnow().timestamp()),
            model="spectraq-agent-v1",
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response["content"],
                    "tool_calls": response.get("tool_calls")
                },
                "finish_reason": response.get("finish_reason", "stop")
            }],
            usage=response.get("usage", {
                "prompt_tokens": len(message.content.split()),
                "completion_tokens": len(response["content"].split()),
                "total_tokens": len(message.content.split()) + len(response["content"].split())
            }),
            session_id=message.session_id,
            tools_used=response.get("tools_used", []),
            data_sources=response.get("data_sources", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@router.post("/stream")
async def stream_chat_completion(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Streaming chat completion endpoint
    
    Returns real-time streaming responses using Server-Sent Events
    """
    try:
        chat_service = ChatService(db, redis)
        
        async def generate_stream():
            try:
                async for chunk in chat_service.stream_chat_response(
                    message=message.content,
                    session_id=message.session_id,
                    user_id=message.user_id,
                    context=message.context
                ):
                    # Format as OpenAI-compatible streaming response
                    stream_chunk = {
                        "id": chunk.get("id"),
                        "object": "chat.completion.chunk",
                        "created": int(datetime.utcnow().timestamp()),
                        "model": "spectraq-agent-v1",
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "role": "assistant" if chunk.get("type") == "start" else None,
                                "content": chunk.get("content", "")
                            },
                            "finish_reason": chunk.get("finish_reason")
                        }]
                    }
                    
                    yield f"data: {json.dumps(stream_chunk)}\n\n"
                
                # Send final chunk
                final_chunk = {
                    "id": f"chatcmpl-{datetime.utcnow().isoformat()}",
                    "object": "chat.completion.chunk", 
                    "created": int(datetime.utcnow().timestamp()),
                    "model": "spectraq-agent-v1",
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(final_chunk)}\n\n"
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                error_chunk = {
                    "error": {
                        "message": str(e),
                        "type": "server_error"
                    }
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream error: {str(e)}")


@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    user_id: str = None
):
    """
    WebSocket endpoint for real-time bidirectional chat
    """
    await websocket_manager.connect(websocket, session_id, user_id)
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message
            chat_service = ChatService()
            
            # Send typing indicator
            await websocket_manager.send_typing_indicator(session_id)
            
            # Stream response back to client
            async for chunk in chat_service.stream_chat_response(
                message=message_data["content"],
                session_id=session_id,
                user_id=user_id,
                context=message_data.get("context")
            ):
                await websocket_manager.send_message_to_session(
                    session_id,
                    {
                        "type": "response_chunk",
                        "content": chunk.get("content", ""),
                        "chunk_type": chunk.get("type"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            # Send completion indicator
            await websocket_manager.send_message_to_session(
                session_id,
                {
                    "type": "response_complete",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, session_id)
    except Exception as e:
        await websocket_manager.send_error(session_id, str(e))
        await websocket_manager.disconnect(websocket, session_id)


@router.post("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    request: ChatHistoryRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> ChatHistoryResponse:
    """
    Get chat history for a session
    """
    try:
        chat_service = ChatService(db, redis)
        
        history = await chat_service.get_chat_history(
            session_id=request.session_id,
            user_id=request.user_id,
            limit=request.limit,
            offset=request.offset,
            message_types=request.message_types
        )
        
        return ChatHistoryResponse(
            messages=history["messages"],
            total_count=history["total_count"],
            has_more=history["has_more"],
            session_id=request.session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    user_id: str = None,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
) -> Dict[str, str]:
    """
    Clear chat history for a session
    """
    try:
        chat_service = ChatService(db, redis)
        
        success = await chat_service.clear_chat_history(
            session_id=session_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return {"message": "Chat history cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")


@router.get("/sessions")
async def list_active_sessions(
    user_id: str = None,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    List active chat sessions
    """
    try:
        active_sessions = await websocket_manager.get_active_sessions(user_id)
        
        return {
            "sessions": active_sessions,
            "total_count": len(active_sessions),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")
