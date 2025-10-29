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
        # Use Ollama directly (skip database for now)
        import httpx
        
        # Call Ollama API directly
        async with httpx.AsyncClient() as client:
            ollama_response = await client.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "qwen2:0.5b",
                    "prompt": f"You are a helpful AI assistant for the VirtPLC system. Context: {request.context or 'General assistance'}\n\nUser: {request.message}\n\nAssistant:",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 512
                    }
                },
                timeout=30.0
            )
            
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                response = result.get("response", "I apologize, but I couldn't generate a response at this time.")
            else:
                response = f"I apologize, but the AI service is currently unavailable. You asked: {request.message}"

        return ChatResponse(
            response=response,
            session_id=1,  # Mock session ID
            metadata={"model": "qwen2:0.5b", "tokens_used": len(response.split())}
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            response="I apologize, but I encountered an error. Please try again later.",
            session_id=1,
            metadata={"error": str(e)}
        )
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