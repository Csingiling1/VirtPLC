"""
Chat routes for AI assistant functionality with ReAct pattern and Artifact support
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json
import re
import os
from datetime import datetime

from ..services.mcp_client import mcp_client
from ..services.timescale_client import timescale_client
from ..database import get_db
from ..database.models import ChatSession, ChatMessage

import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

# Enhanced system prompt for industrial analytics with Tool Use and Artifacts
SYSTEM_PROMPT = """You are an advanced Industrial AI Assistant for VirtPLC factory monitoring system.
You have access to real-time PLC and sensor data from TimescaleDB via MCP (Model Context Protocol) tools.

AVAILABLE MCP TOOLS:
You can use these tools by responding with: [TOOL: tool_name {"arg": "value"}]

1. query - Execute SQL queries on TimescaleDB
   - Schema: plc_data(timestamp TIMESTAMPTZ, device_id TEXT, type TEXT, data JSONB, metadata JSONB)
   - Example: [TOOL: query {"sql": "SELECT device_id, data->'signal_config'->>'value' as value FROM plc_data WHERE type='sensor' ORDER BY timestamp DESC LIMIT 10"}]

2. list_tables - List all available database tables
3. describe_table - Get schema for a specific table
4. list_schemas - List all database schemas

CREATING INTERACTIVE CHARTS AND DASHBOARDS:
When asked to create charts or dashboards, generate an <artifact> tag with EXECUTABLE React/Recharts code:

<artifact type="react" title="Dashboard Name">
{
  "charts": [
    {
      "type": "line",
      "title": "Temperature Trend",
      "query": "SELECT timestamp, device_id, (data->'signal_config'->>'value')::float as value FROM plc_data WHERE device_id LIKE '%temperature%' ORDER BY timestamp DESC LIMIT 100",
      "x_field": "timestamp",
      "y_field": "value",
      "group_by": "device_id"
    }
  ]
}
</artifact>

IMPORTANT GUIDELINES:
1. Always use MCP tools to query actual data from TimescaleDB
2. When creating charts, include the FULL SQL query that fetches the data
3. Use proper field mapping: x_field, y_field, group_by
4. Chart types: line, bar, area, scatter, pie
5. After using a tool, summarize findings clearly and concisely
6. Generate artifacts with real queries, not placeholders

Example workflow for "Show temperature data":
1. [TOOL: query {"sql": "SELECT device_id FROM plc_data WHERE device_id LIKE '%temperature%' GROUP BY device_id LIMIT 5"}]
2. Analyze results
3. Generate artifact with query that fetches time-series data
4. Provide brief explanation
"""

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

async def execute_tool(tool_name: str, args: Dict[str, Any]) -> str:
    """Execute MCP tools for database access"""
    logger.info(f"Executing MCP tool: {tool_name} with args: {args}")
    
    try:
        # Use MCP client for all database operations
        if tool_name == "query":
            sql = args.get("sql", "")
            if not sql.strip():
                return json.dumps({"error": "SQL query is required"})
            
            # Execute via MCP server
            result = await mcp_client.call_tool("query", {"sql": sql})
            return json.dumps(result, default=str)
        
        elif tool_name == "list_tables":
            result = await mcp_client.call_tool("list_tables", {})
            return json.dumps(result, default=str)
        
        elif tool_name == "describe_table":
            table_name = args.get("table_name", "")
            if not table_name:
                return json.dumps({"error": "table_name is required"})
            result = await mcp_client.call_tool("describe_table", {"table_name": table_name})
            return json.dumps(result, default=str)
        
        elif tool_name == "list_schemas":
            result = await mcp_client.call_tool("list_schemas", {})
            return json.dumps(result, default=str)
        
        # Legacy fallback tools (use direct TimescaleDB)
        elif tool_name == "get_latest_readings":
            device_id = args.get("device_id")
            limit = args.get("limit", 100)
            results = timescale_client.get_latest_readings(device_id, limit)
            return json.dumps({"results": results, "count": len(results)}, default=str)
        
        elif tool_name == "get_device_stats":
            device_id = args.get("device_id")
            hours = args.get("hours", 24)
            if not device_id:
                return json.dumps({"error": "device_id is required"})
            result = timescale_client.get_device_stats(device_id, hours)
            return json.dumps({"result": result}, default=str)
        
        else:
            return json.dumps({"error": f"Unknown tool '{tool_name}'"})
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})

async def stream_chat_response(prompt: str, context_data: str = "", conversation_history: str = ""):
    """
    Stream chat response with ReAct loop
    """
    current_prompt = f"{SYSTEM_PROMPT}\n\nContext Data:\n{context_data}\n\nConversation History:\n{conversation_history}\n\nUser Query: {prompt}\n\nProvide a clear response. If you need data, use a tool first, then answer based on the results."
    
    max_turns = 3
    current_turn = 0
    final_response = ""
    accumulated_response = ""
    
    while current_turn < max_turns:
        current_turn += 1
        logger.info(f"ReAct turn {current_turn}/{max_turns}")
        full_response = ""
        
        # Call Ollama
        async with httpx.AsyncClient() as client:
            model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
            async with client.stream(
                "POST",
                "http://ollama:11434/api/generate",
                json={
                    "model": model,
                    "prompt": current_prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 1024
                    }
                },
                timeout=120.0
            ) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            chunk = data["response"]
                            full_response += chunk
                            
                    except json.JSONDecodeError:
                        continue

        logger.debug(f"Full response: {full_response[:200]}")

        # Check for tool calls
        tool_match = re.search(r'\[TOOL:\s*(\w+)\s*({.*?})\]', full_response, re.DOTALL)
        
        if tool_match and current_turn < max_turns:
            tool_name = tool_match.group(1)
            tool_args_str = tool_match.group(2)
            
            try:
                tool_args = json.loads(tool_args_str)
                logger.info(f"Calling tool: {tool_name}")
                yield f"data: {json.dumps({'status': f'🔧 {tool_name}'})}\n\n"
                
                tool_result = await execute_tool(tool_name, tool_args)
                logger.info(f"Tool result length: {len(tool_result)}")
                
                # Append result to prompt and loop
                current_prompt = f"{SYSTEM_PROMPT}\n\nUser Query: {prompt}\n\nYou called tool '{tool_name}' and got this result:\n{tool_result}\n\nNow provide a clear, helpful answer to the user. If creating a chart, use the <artifact> format with actual data from the tool result."
                accumulated_response = ""
                continue
                
            except Exception as e:
                logger.error(f"Tool error: {e}")
                yield f"data: {json.dumps({'error': f'Tool error: {str(e)}'})}\n\n"
                break
        
        # No tool call - this is the final response
        accumulated_response += full_response
        break
    
    # Clean response
    clean = re.sub(r'\[TOOL:.*?\]', '', accumulated_response, flags=re.DOTALL)
    clean = re.sub(r'\[TOOL_RESULT\]:.*?(?=\n\n|\Z)', '', clean, flags=re.DOTALL)
    clean = re.sub(r'\[RESPONSE\]', '', clean)
    clean = re.sub(r'\[END OF RESPONSE\]', '', clean)
    clean = clean.strip()
    
    yield f"data: {json.dumps({'done': True, 'final_response': clean})}\n\n"

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Send a chat message (Non-streaming wrapper)
    """
    response_text = ""
    final_text = ""
    logger.info(f"Processing chat message: {request.message[:100]}...")
    
    async for chunk_str in stream_chat_response(request.message):
        if chunk_str.startswith("data: "):
            data = json.loads(chunk_str[6:])
            if "chunk" in data:
                response_text += data["chunk"]
            if "final_response" in data:
                final_text = data["final_response"]
    
    # Use final_response if available, otherwise use accumulated response
    result = final_text if final_text else response_text
    
    logger.info(f"Chat response generated: {len(result)} chars")
    logger.debug(f"Response preview: {result[:200]}")
    
    return ChatResponse(
        response=result,
        session_id=1
    )

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming endpoint
    """
    return StreamingResponse(
        stream_chat_response(request.message),
        media_type="text/event-stream"
    )
