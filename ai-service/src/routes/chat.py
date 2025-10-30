"""
Chat routes for AI assistant functionality
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import json
from datetime import datetime

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
    chart_suggestions: List[Dict[str, Any]] = None


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Send a chat message and get AI response with TimescaleDB context
    """
    try:
        # Get relevant equipment symbols from the message or use defaults
        symbols = ["Motor1", "Motor2", "Conveyor1", "Sensor1"]  # Default symbols, could be enhanced with NLP
        
        # Extract equipment mentions from user message
        message_lower = request.message.lower()
        if "motor" in message_lower:
            symbols = ["Motor1", "Motor2"]
        elif "conveyor" in message_lower:
            symbols = ["Conveyor1"]
        elif "sensor" in message_lower:
            symbols = ["Sensor1", "Sensor2"]
        
        # Get TimescaleDB context via backend REST API instead of MCP
        context_parts = []
        
        try:
            import httpx
            backend_url = "http://backend:8080"
            
            # Get latest data from backend
            async with httpx.AsyncClient() as client:
                # Get latest readings
                latest_response = await client.get(f"{backend_url}/api/data/latest", timeout=10.0)
                if latest_response.status_code == 200:
                    latest_data = latest_response.json()
                    context_parts.append("## Current Sensor Data (Latest Readings)")
                    if isinstance(latest_data, list):
                        # Group by symbol for better organization
                        symbol_data = {}
                        for reading in latest_data:
                            symbol = reading.get('symbol', 'Unknown')
                            if symbol not in symbol_data:
                                symbol_data[symbol] = []
                            symbol_data[symbol].append(reading)
                        
                        for symbol, readings in symbol_data.items():
                            context_parts.append(f"### Equipment: {symbol}")
                            for reading in readings[:5]:  # Show up to 5 metrics per symbol
                                metric = reading.get('metricType', 'Unknown')
                                value = reading.get('value', 'N/A')
                                unit = reading.get('unit', '')
                                timestamp = reading.get('timestamp', 'Unknown')
                                context_parts.append(f"- {metric}: {value} {unit} (timestamp: {timestamp})")
                            if len(readings) > 5:
                                context_parts.append(f"- ... and {len(readings) - 5} more metrics")
                
                # Get recent historical data (last 24 hours)
                end_time = int(datetime.utcnow().timestamp() * 1000)
                start_time = end_time - (24 * 60 * 60 * 1000)  # 24 hours ago
                
                range_response = await client.get(
                    f"{backend_url}/api/data/range",
                    params={"startTime": start_time, "endTime": end_time},
                    timeout=10.0
                )
                if range_response.status_code == 200:
                    range_data = range_response.json()
                    context_parts.append("\n## Recent Historical Data (Last 24 Hours)")
                    if isinstance(range_data, list):
                        # Group by symbol and show summary
                        symbol_counts = {}
                        for reading in range_data:
                            symbol = reading.get('symbol', 'Unknown')
                            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
                        
                        for symbol, count in symbol_counts.items():
                            context_parts.append(f"- {symbol}: {count} readings in last 24 hours")
                
        except Exception as e:
            logger.warning(f"Failed to get backend data: {e}")
            context_parts.append("## Data Access Note: Could not retrieve live TimescaleDB data")
        
        # Build context string
        context_data = "\n".join(context_parts) if context_parts else "No TimescaleDB data available"
        
        # Enhanced prompt with TimescaleDB context
        enhanced_prompt = f"""You are a helpful AI assistant for the VirtPLC factory monitoring system.

CONTEXT FROM TIMESCALEDB:
{context_data}

USER QUESTION: {request.message}

Please provide a helpful response based on the current factory data. If the user is asking about equipment status, performance, or maintenance, reference the actual numerical data from the context above. Be specific about current readings, values, and recent activity.

IMPORTANT: When providing information about sensor data, ALWAYS include the actual numerical values, units, and timestamps from the context. If the user asks about trends, performance, or comparisons, suggest creating charts or diagrams using the available data.

If appropriate for the user's question, suggest creating embeddable charts or diagrams by mentioning: "Would you like me to generate a chart showing [describe the chart]?" The frontend can then display these as pinnable/previewable visualizations.

Assistant:"""
        
        # Call Ollama API with enhanced context
        import httpx
        
        async with httpx.AsyncClient() as client:
            ollama_response = await client.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "qwen2:0.5b",
                    "prompt": enhanced_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1024
                    }
                },
                timeout=30.0
            )
            
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                response = result.get("response", "I apologize, but I couldn't generate a response at this time.")
            else:
                response = f"I apologize, but the AI service is currently unavailable. You asked: {request.message}"

        # Detect if user is asking for charts or if charts would be helpful
        chart_suggestions = []
        message_lower = request.message.lower()
        
        if any(keyword in message_lower for keyword in ['chart', 'graph', 'plot', 'diagram', 'visualize', 'trend', 'compare']):
            # User explicitly asked for charts
            if 'motor' in message_lower or 'performance' in message_lower:
                chart_suggestions.append({
                    "type": "line_chart",
                    "title": "Motor Performance Trends",
                    "description": "Line chart showing motor metrics over time",
                    "data_source": "timescale_recent",
                    "symbols": ["Motor1", "Motor2"],
                    "metrics": ["temperature", "vibration", "current"],
                    "time_range": "24h"
                })
                chart_suggestions.append({
                    "type": "bar_chart",
                    "title": "Motor Status Comparison",
                    "description": "Bar chart comparing current motor statuses",
                    "data_source": "latest_readings",
                    "symbols": ["Motor1", "Motor2"],
                    "metrics": ["run", "fault"],
                    "time_range": "current"
                })
            elif 'sensor' in message_lower:
                chart_suggestions.append({
                    "type": "line_chart", 
                    "title": "Sensor Readings Overview",
                    "description": "Multi-sensor data visualization",
                    "data_source": "timescale_recent",
                    "symbols": ["Sensor1", "Sensor2"],
                    "time_range": "24h"
                })
                chart_suggestions.append({
                    "type": "pie_chart",
                    "title": "Sensor Distribution",
                    "description": "Pie chart showing sensor value distribution",
                    "data_source": "latest_readings",
                    "symbols": ["Sensor1", "Sensor2"],
                    "time_range": "current"
                })
        elif any(keyword in message_lower for keyword in ['how', 'what', 'status', 'performance', 'trending']):
            # Suggest charts for analytical questions
            chart_suggestions.append({
                "type": "dashboard_preview",
                "title": "Equipment Status Dashboard",
                "description": "Overview of all equipment current status",
                "data_source": "latest_readings"
            })
            if 'performance' in message_lower:
                chart_suggestions.append({
                    "type": "bar_chart",
                    "title": "Performance Metrics",
                    "description": "Bar chart of key performance indicators",
                    "data_source": "latest_readings",
                    "symbols": ["Motor1", "Motor2", "Conveyor1"],
                    "metrics": ["speed", "efficiency"],
                    "time_range": "current"
                })

        return ChatResponse(
            response=response,
            session_id=1,  # Mock session ID
            metadata={
                "model": "qwen2:0.5b", 
                "tokens_used": len(response.split()),
                "context_symbols": symbols,
                "backend_data_accessed": bool(context_parts and "Current Sensor Data" in context_data)
            },
            chart_suggestions=chart_suggestions if chart_suggestions else None
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            response="I apologize, but I encountered an error while accessing factory data. Please try again later.",
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