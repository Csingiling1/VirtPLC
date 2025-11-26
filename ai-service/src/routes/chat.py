"""
Chat routes for AI assistant functionality
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from ..services.mcp_client import mcp_client
from ..database import get_db
from ..database.models import ChatSession, ChatMessage

import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

# Enhanced system prompt for industrial analytics
SYSTEM_PROMPT = """You are a concise industrial equipment monitoring assistant.

RESPONSE FORMAT:
- Start with a brief status summary (1-2 sentences)
- List key equipment categories with counts
- Note any anomalies if present
- End with total count

KEEP RESPONSES SHORT AND FACTUAL. Do not repeat information. Do not add analysis unless asked."""


async def stream_chat_response(prompt: str, symbols: List[str], context_data: str = "", conversation_history: str = ""):
    """
    Stream chat response from Ollama
    """
    # Build full prompt with context
    full_prompt = f"{SYSTEM_PROMPT}\n\nContext Data:\n{context_data}\n\nConversation History:\n{conversation_history}\n\nUser Query: {prompt}"
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "http://ollama:11434/api/generate",
                json={
                    "model": "qwen2:0.5b",
                    "prompt": full_prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 512,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=60.0
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield f"data: {json.dumps({'chunk': data['response']})}\n\n"
                                if data.get("done", False):
                                    # Generate chart suggestions based on the response
                                    chart_suggestions = generate_chart_suggestions(prompt, symbols)
                                    yield f"data: {json.dumps({'done': True, 'chart_suggestions': chart_suggestions})}\n\n"
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    yield f"data: {json.dumps({'error': 'AI service unavailable'})}\n\n"
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def generate_chart_suggestions(message: str, symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Generate intelligent chart suggestions based on context and user intent
    """
    try:
        chart_suggestions = []

        # Analyze the message to determine what kind of chart to create
        message_lower = message.lower()

        # Perform advanced intent analysis
        intent = analyze_sensor_intent(message_lower)

        # Generate dynamic title and description
        title, description = generate_chart_title_description(intent, message_lower)

        # Map time range to data source
        time_range_map = {
            '1h': 'timescale_1h',
            '24h': 'timescale_24h',
            '7d': 'timescale_7d',
            '30d': 'timescale_30d'
        }
        data_source = time_range_map.get(intent['time_range'], 'timescale_24h')

        # Create focused chart suggestion
        chart_suggestion = {
            "type": intent['chart_type'],
            "title": title,
            "description": description,
            "data_source": data_source,
            "symbols": symbols if symbols else ["intelligent_filter"],
            "metrics": intent['metrics'],
            "devices": intent['devices'],
            "context": intent['context'],
            "priority": "high"
        }

        return [chart_suggestion]
    except Exception as e:
        logger.error(f"Error generating chart suggestions: {e}")
        # Return a single chart on error
        return [{
            "type": "line_chart",
            "title": "Sensor Data Overview",
            "description": "Overview of all available sensor data",
            "data_source": "timescale_24h",
            "symbols": ["all_devices"],
            "metrics": ["temperature", "speed", "vibration"],
            "priority": "high"
        }]


def analyze_sensor_intent(message: str) -> Dict[str, Any]:
    """
    Advanced analysis of user message to determine sensor types, devices, and context
    Returns a dictionary with detailed intent analysis
    """
    message_lower = message.lower()
    intent = {
        'metrics': [],
        'devices': [],
        'context': 'general',
        'time_range': '24h',
        'chart_type': 'line_chart'
    }

    # Advanced sensor type detection with context
    sensor_patterns = {
        'temperature': {
            'keywords': ['temperature', 'temp', 'heat', 'thermal', 'cooling', 'hot', 'cold', 'degrees'],
            'context': ['motor', 'bearing', 'coolant', 'ambient', 'process']
        },
        'speed': {
            'keywords': ['speed', 'rpm', 'rotation', 'velocity', 'rate'],
            'context': ['motor', 'pump', 'fan', 'conveyor']
        },
        'vibration': {
            'keywords': ['vibration', 'vibe', 'oscillation', 'shake', 'frequency'],
            'context': ['motor', 'bearing', 'pump', 'compressor']
        },
        'current': {
            'keywords': ['current', 'amp', 'amperage', 'power', 'load'],
            'context': ['motor', 'pump', 'heater', 'compressor']
        },
        'pressure': {
            'keywords': ['pressure', 'psi', 'bar', 'hydraulic', 'pneumatic'],
            'context': ['pump', 'valve', 'cylinder', 'accumulator']
        },
        'flow': {
            'keywords': ['flow', 'rate', 'volume', 'throughput', 'discharge'],
            'context': ['pump', 'valve', 'pipe', 'tank']
        },
        'level': {
            'keywords': ['level', 'height', 'depth', 'volume', 'capacity'],
            'context': ['tank', 'reservoir', 'silo', 'hopper']
        },
        'position': {
            'keywords': ['position', 'angle', 'rotation', 'displacement'],
            'context': ['valve', 'actuator', 'gate', 'damper']
        }
    }

    # Detect sensor types with context awareness
    for sensor_type, config in sensor_patterns.items():
        if any(keyword in message_lower for keyword in config['keywords']):
            intent['metrics'].append(sensor_type)

            # Check for device context
            for device_context in config['context']:
                if device_context in message_lower:
                    intent['devices'].append(device_context)
                    break

    # Device-specific detection
    device_patterns = {
        'motor': ['motor', 'drive', 'actuator'],
        'pump': ['pump', 'centrifugal', 'positive displacement'],
        'fan': ['fan', 'blower', 'ventilator'],
        'conveyor': ['conveyor', 'belt', 'transport'],
        'valve': ['valve', 'gate', 'ball', 'control'],
        'compressor': ['compressor', 'air', 'gas'],
        'heater': ['heater', 'heating', 'furnace'],
        'sensor': ['sensor', 'transducer', 'detector']
    }

    for device_type, keywords in device_patterns.items():
        if any(keyword in message_lower for keyword in keywords):
            intent['devices'].append(device_type)

    # Context detection
    if any(word in message_lower for word in ['performance', 'efficiency', 'productivity', 'optimization']):
        intent['context'] = 'performance'
        if not intent['metrics']:
            intent['metrics'] = ['speed', 'current', 'vibration']
    elif any(word in message_lower for word in ['maintenance', 'failure', 'breakdown', 'repair']):
        intent['context'] = 'maintenance'
        if not intent['metrics']:
            intent['metrics'] = ['temperature', 'vibration', 'current']
    elif any(word in message_lower for word in ['energy', 'power', 'consumption', 'efficiency']):
        intent['context'] = 'energy'
        if not intent['metrics']:
            intent['metrics'] = ['current', 'power', 'voltage']

    # Time range detection
    if any(phrase in message_lower for phrase in ['last hour', 'past hour', '1 hour']):
        intent['time_range'] = '1h'
    elif any(phrase in message_lower for phrase in ['7 days', 'week', 'weekly']):
        intent['time_range'] = '7d'
    elif any(phrase in message_lower for phrase in ['30 days', 'month', 'monthly']):
        intent['time_range'] = '30d'

    # Chart type hints
    if any(word in message_lower for word in ['compare', 'comparison', 'versus', 'vs']):
        intent['chart_type'] = 'bar_chart'
    elif any(word in message_lower for word in ['distribution', 'proportion', 'percentage']):
        intent['chart_type'] = 'pie_chart'

    # If no metrics found, provide defaults based on context
    if not intent['metrics']:
        if intent['context'] == 'performance':
            intent['metrics'] = ['speed', 'current', 'vibration']
        elif intent['context'] == 'maintenance':
            intent['metrics'] = ['temperature', 'vibration']
        elif intent['context'] == 'energy':
            intent['metrics'] = ['current', 'power']
        else:
            intent['metrics'] = ['temperature', 'speed', 'current']  # General defaults

    return intent


def generate_chart_title_description(intent: Dict[str, Any], original_message: str) -> tuple[str, str]:
    """
    Generate intelligent chart title and description based on intent analysis
    """
    metrics = intent['metrics']
    devices = intent['devices']
    context = intent['context']
    time_range = intent['time_range']

    # Create metric display names
    metric_names = {
        'temperature': 'Temperature',
        'speed': 'Speed',
        'vibration': 'Vibration',
        'current': 'Current',
        'pressure': 'Pressure',
        'flow': 'Flow',
        'level': 'Level',
        'position': 'Position',
        'power': 'Power',
        'voltage': 'Voltage'
    }

    display_metrics = [metric_names.get(m, m.title()) for m in metrics]

    # Generate title based on context
    if context == 'performance':
        title = f"Performance Metrics: {', '.join(display_metrics)}"
    elif context == 'maintenance':
        title = f"Maintenance Monitoring: {', '.join(display_metrics)}"
    elif context == 'energy':
        title = f"Energy Analysis: {', '.join(display_metrics)}"
    elif devices:
        device_names = [d.title() for d in devices]
        title = f"{', '.join(device_names)} {', '.join(display_metrics)}"
    else:
        title = f"{', '.join(display_metrics)} Overview"

    # Generate description
    time_descriptions = {
        '1h': 'last hour',
        '24h': 'last 24 hours',
        '7d': 'past week',
        '30d': 'past month'
    }
    time_desc = time_descriptions.get(time_range, 'recent period')

    if devices:
        device_str = f" from {', '.join(devices)}"
    else:
        device_str = ""

    description = f"Showing {', '.join(display_metrics).lower()} data{device_str} over the {time_desc}"

    return title, description
    if any(s.lower().startswith('motor') for s in symbols):
        chart_suggestions.extend([
            {
                "type": "line_chart",
                "title": "Motor Temperature Trends",
                "description": "Temperature monitoring for predictive maintenance",
                "data_source": "timescale_24h",
                "symbols": [s for s in symbols if s.lower().startswith('motor')],
                "metrics": ["temperature"],
                "thresholds": {"warning": 80, "critical": 90},
                "priority": "high"
            },
            {
                "type": "multi_line_chart",
                "title": "Motor Performance Metrics",
                "description": "Speed, vibration, and current analysis",
                "data_source": "timescale_1h",
                "symbols": [s for s in symbols if s.lower().startswith('motor')],
                "metrics": ["speed", "vibration", "current"],
                "priority": "medium"
            }
        ])
    
    # Conveyor analytics
    if any('conveyor' in s.lower() for s in symbols):
        chart_suggestions.append({
            "type": "bar_chart",
            "title": "Conveyor Efficiency Analysis",
            "description": "Throughput and downtime metrics",
            "data_source": "timescale_8h",
            "symbols": [s for s in symbols if 'conveyor' in s.lower()],
            "metrics": ["speed", "status", "downtime"],
            "priority": "medium"
        })
    
    # Sensor network health
    chart_suggestions.append({
        "type": "heatmap",
        "title": "Sensor Network Health",
        "description": "Signal quality and calibration status across all sensors",
        "data_source": "latest_readings",
        "symbols": symbols,
        "metrics": ["signal_quality", "calibration_status"],
        "priority": "low"
    })
    
    # Predictive analytics
    chart_suggestions.append({
        "type": "forecast_chart",
        "title": "Predictive Maintenance Forecast",
        "description": "AI-powered predictions for equipment failures",
        "data_source": "ml_predictions",
        "symbols": symbols[:3],  # Limit to top 3 for clarity
        "time_range": "7d",
        "priority": "high"
    })
    
    return chart_suggestions


class ChatRequest(BaseModel):
    message: str
    session_id: int = None
    context: Dict[str, Any] = None
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    session_id: int
    metadata: Optional[Dict[str, Any]] = None
    chart_suggestions: Optional[List[Dict[str, Any]]] = None


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Send a chat message and get AI response with TimescaleDB context
    """
    import sys
    print(f"DEBUG: Received chat request: {request.message}", file=sys.stderr)
    try:
        # Get relevant equipment symbols from the message or use defaults
        symbols = ["Motor1", "Motor2", "Conveyor1", "Sensor1"]  # Default symbols, could be enhanced with NLP
        
        # Extract equipment mentions from user message
        message_lower = request.message.lower()
        is_broad_query = any(word in message_lower for word in ["all", "status", "overview", "summary", "everything"])
        
        if "motor" in message_lower and not is_broad_query:
            symbols = ["Motor1", "Motor2"]
        elif "conveyor" in message_lower and not is_broad_query:
            symbols = ["Conveyor1"]
        elif "sensor" in message_lower and not is_broad_query:
            symbols = ["Sensor1", "Sensor2"]
        else:
            symbols = ["Motor1", "Motor2", "Conveyor1", "Sensor1"]  # Default symbols
        
        # Get TimescaleDB context via direct API calls
        context_parts = []
        
        if not is_broad_query:
            # For specific queries, get detailed sensor data
            try:
                logger.info("Getting detailed sensor data for specific query")
                # Get latest sensor readings via simulator API
                async with httpx.AsyncClient() as client:
                    sim_response = await client.get("http://simulator:8080/api/stream/latest", timeout=10.0)
                    if sim_response.status_code == 200:
                        sim_data = sim_response.json()
                        logger.info(f"Simulator API response received with {len(sim_data.get('tenants', []))} tenants")
                        
                        # Extract sensor data from hierarchical structure
                        all_sensors = []
                        if "tenants" in sim_data:
                            for tenant in sim_data["tenants"]:
                                for manufacturer in tenant.get("manufacturers", []):
                                    for factory in manufacturer.get("factories", []):
                                        for plc in factory.get("plcs", []):
                                            for sensor in plc.get("sensors", []):
                                                sensor["plc_id"] = plc["id"]
                                                sensor["factory_id"] = factory["id"]
                                                all_sensors.append(sensor)
                        
                        logger.info(f"Extracted {len(all_sensors)} sensors from simulator API")
                        if all_sensors:
                            context_parts.append("## Current Sensor Data")
                            logger.info(f"Adding context for {len(all_sensors)} sensors")
                            
                            # Filter sensors based on symbols/keywords
                            relevant_sensors = []
                            for sensor in all_sensors:
                                sensor_name = sensor.get('name', '').lower()
                                message_lower = request.message.lower()
                                
                                # Check if sensor matches query keywords
                                if ('motor' in message_lower and 'motor' in sensor_name) or \
                                   ('conveyor' in message_lower and ('conveyor' in sensor_name or 'belt' in sensor_name)) or \
                                   ('sensor' in message_lower and 'sensor' in sensor_name) or \
                                   ('temperature' in message_lower and 'temperature' in sensor_name) or \
                                   ('pressure' in message_lower and 'pressure' in sensor_name):
                                    relevant_sensors.append(sensor)
                            
                            if relevant_sensors:
                                # Provide count and summary instead of individual values
                                sensor_types = {}
                                for sensor in relevant_sensors:
                                    name = sensor.get('name', 'Unknown')
                                    if name not in sensor_types:
                                        sensor_types[name] = 0
                                    sensor_types[name] += 1
                                
                                context_parts.append(f"Found {len(relevant_sensors)} relevant sensors:")
                                for sensor_type, count in sensor_types.items():
                                    context_parts.append(f"- {sensor_type}: {count} sensor(s)")
                            else:
                                context_parts.append("No sensors found matching your query. Available sensors include motors, conveyors, and various process sensors.")
            except Exception as e:
                logger.error(f"Failed to get sensor data: {e}")
                context_parts.append("Could not retrieve live sensor data")
        else:
            # For broad queries, provide high-level overview only
            try:
                async with httpx.AsyncClient() as client:
                    sim_response = await client.get("http://simulator:8080/api/stream/latest", timeout=10.0)
                    if sim_response.status_code == 200:
                        sim_data = sim_response.json()
                        
                        # Count sensors by category for overview
                        all_sensors = []
                        if "tenants" in sim_data:
                            for tenant in sim_data["tenants"]:
                                for manufacturer in tenant.get("manufacturers", []):
                                    for factory in manufacturer.get("factories", []):
                                        for plc in factory.get("plcs", []):
                                            for sensor in plc.get("sensors", []):
                                                all_sensors.append(sensor)
                        
                        motor_sensors = [s for s in all_sensors if 'motor' in s.get('name', '').lower()]
                        conveyor_sensors = [s for s in all_sensors if 'conveyor' in s.get('name', '').lower() or 'belt' in s.get('name', '').lower()]
                        temperature_sensors = [s for s in all_sensors if 'temperature' in s.get('name', '').lower()]
                        pressure_sensors = [s for s in all_sensors if 'pressure' in s.get('name', '').lower()]
                        
                        context_parts.append("## Equipment Status Overview")
                        context_parts.append(f"- **Motors**: {len(motor_sensors)} sensors monitoring performance")
                        context_parts.append(f"- **Conveyors**: {len(conveyor_sensors)} sensors monitoring operation")
                        context_parts.append(f"- **Temperature**: {len(temperature_sensors)} sensors across equipment")
                        context_parts.append(f"- **Pressure Systems**: {len(pressure_sensors)} sensors monitoring hydraulics")
                        context_parts.append(f"- **Other Sensors**: {len(all_sensors) - len(motor_sensors) - len(conveyor_sensors) - len(temperature_sensors) - len(pressure_sensors)} additional sensors")
                        context_parts.append(f"**Total Equipment Monitored**: {len(all_sensors)} sensors across {len(set(s.get('plc_id', 'Unknown') for s in all_sensors))} PLCs")
            except Exception as e:
                logger.error(f"Failed to get overview data: {e}")
                context_parts.append("Could not retrieve equipment overview")
        
        # Build context string
        context_data = "\n".join(context_parts) if context_parts else "No TimescaleDB data available"
        
        # Build conversation history if provided
        conversation_history = ""
        if request.context and 'messages' in request.context:
            conversation_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in request.context['messages']])
        
        # Build full prompt with context
        full_prompt = f"{SYSTEM_PROMPT}\n\nContext Data:\n{context_data}\n\nConversation History:\n{conversation_history}\n\nUser Query: {request.message}"
        
        # If streaming is requested, use streaming endpoint
        if request.stream:
            return StreamingResponse(
                stream_chat_response(request.message, symbols, context_data, conversation_history),
                media_type="text/plain"
            )

        # Call Ollama API with enhanced context
        async with httpx.AsyncClient() as client:
            ollama_response = await client.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "qwen2:0.5b",
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower temperature for more consistent analytics
                        "num_predict": 2048,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=60.0
            )
            
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                response = result.get("response", "I apologize, but I couldn't generate a response at this time.")
            else:
                print(f"DEBUG: Ollama response status: {ollama_response.status_code}", file=sys.stderr)
                response = f"I apologize, but the AI service is currently unavailable. You asked: {request.message}"

        print(f"DEBUG: About to generate chart suggestions", file=sys.stderr)
        # Generate intelligent chart suggestions
        try:
            chart_suggestions = generate_chart_suggestions(request.message, symbols)
            print(f"DEBUG: Generated {len(chart_suggestions)} chart suggestions", file=sys.stderr)
        except Exception as e:
            print(f"DEBUG: Error generating chart suggestions: {e}", file=sys.stderr)
            chart_suggestions = []

        return ChatResponse(
            response=response,
            session_id=1,  # Mock session ID
            metadata={
                "model": "qwen2:0.5b", 
                "tokens_used": len(response.split()),
                "context_symbols": symbols,
                "backend_data_accessed": bool(context_parts and "Current Sensor Data" in context_data)
            },
            chart_suggestions=chart_suggestions
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        chart_suggestions = []
        return ChatResponse(
            response="I apologize, but I encountered an error while accessing factory data. Please try again later.",
            session_id=1,
            metadata={"error": str(e)},
            chart_suggestions=chart_suggestions
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