"""
Chat routes for AI assistant functionality
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import json

from ..services.mcp_client import mcp_client
from ..database import get_db
from ..database.models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: int = None
    context: Dict[str, Any] = None


class ChatResponse(BaseModel):
    response: str
    session_id: int
    metadata: Dict[str, Any] = None


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Send a chat message and get AI response
    """
    try:
        db = next(get_db())

        # Create or get session
        if request.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = ChatSession()
            db.add(session)
            db.commit()
            db.refresh(session)

        # Save user message
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=request.message,
            message_metadata=request.context or {}
        )
        db.add(user_message)

        # Get AI response
        if mcp_client.enabled:
            response = await mcp_client.chat(request.message, context=request.context)
        else:
            response = f"Mock response to: {request.message}"

        # Save AI response
        ai_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=response,
            message_metadata={"model": "mock"}
        )
        db.add(ai_message)
        db.commit()

        return ChatResponse(
            response=response,
            session_id=session.id,
            metadata={"tokens_used": len(response.split())}
        )
    except Exception as e:
        logger.error(f"Chat message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process message similar to POST endpoint
            response = f"Echo: {message_data.get('message', '')}"

            await websocket.send_text(json.dumps({
                "response": response,
                "timestamp": "now"
            }))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@router.get("/sessions")
async def get_chat_sessions():
    """
    Get user's chat sessions
    """
    try:
        db = next(get_db())
        sessions = db.query(ChatSession).filter(ChatSession.is_active == True).all()

        return {
            "sessions": [
                {
                    "id": s.id,
                    "created_at": s.created_at.isoformat(),
                    "last_activity": s.updated_at.isoformat(),
                    "message_count": len(s.messages)
                } for s in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))