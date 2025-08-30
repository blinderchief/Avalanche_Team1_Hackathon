"""
WebSocket manager for real-time chat connections
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manager for WebSocket connections and real-time messaging"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.session_users: Dict[str, Optional[str]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None):
        """Accept WebSocket connection and add to session"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        self.session_users[session_id] = user_id
        
        logger.info(f"WebSocket connected for session {session_id}")
    
    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                if session_id in self.session_users:
                    del self.session_users[session_id]
        
        logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_message_to_session(self, session_id: str, message: Dict[str, Any]):
        """Send message to all connections in a session"""
        if session_id in self.active_connections:
            disconnected = []
            
            for websocket in self.active_connections[session_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to WebSocket: {e}")
                    disconnected.append(websocket)
            
            # Remove disconnected websockets
            for websocket in disconnected:
                await self.disconnect(websocket, session_id)
    
    async def send_typing_indicator(self, session_id: str):
        """Send typing indicator to session"""
        await self.send_message_to_session(session_id, {
            "type": "typing",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_error(self, session_id: str, error_message: str):
        """Send error message to session"""
        await self.send_message_to_session(session_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of active sessions"""
        sessions = []
        
        for session_id, connections in self.active_connections.items():
            session_user = self.session_users.get(session_id)
            
            if user_id is None or session_user == user_id:
                sessions.append({
                    "session_id": session_id,
                    "user_id": session_user,
                    "connection_count": len(connections),
                    "status": "active"
                })
        
        return sessions
