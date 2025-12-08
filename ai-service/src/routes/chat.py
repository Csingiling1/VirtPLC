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
from ..database import get_db
from ..database.models import ChatSession, ChatMessage

import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

# Enhanced system prompt for industrial analytics with Tool Use and Artifacts
SYSTEM_PROMPT = """You are an advanced Industrial AI Assistant for VirtPLC.
You are capable of complex data analysis, SQL querying, and dashboard generation.

AVAILABLE TOOLS:
- execute_query(query: str): Run a SQL query on the TimescaleDB 'virtplc_ts' database.
  - Table: sensor_data
  - Columns: time (TIMESTAMPTZ), tag_name (TEXT), value (DOUBLE PRECISION), quality (TEXT)
  - Example: SELECT time_bucket('1 hour', time) as bucket, avg(value) FROM sensor_data WHERE tag_name = 'temperature' GROUP BY bucket

TOOL USE SYNTAX:
To use a tool, you MUST use this exact format on a new line:
[TOOL: tool_name {"arg_name": "arg_value"}]

Example:
[TOOL: execute_query {"query": "SELECT avg(value) FROM sensor_data"}]

ARTIFACT GENERATION:
To create a dashboard or chart, use the <artifact> tag. This will render a UI component for the user.
Format:
<artifact type="dashboard" title="Dashboard Title">
{
  "charts": [
    {
      "type": "line" | "bar" | "scatter" | "area",
      "title": "Chart Title",
      "data_source": "sql",
      "query": "SELECT ...",
      "x_axis": "time",
      "y_axis": "value"
    }
  ]
}
</artifact>

GUIDELINES:
1. When asked for aggregations (avg, min, max), ALWAYS use the execute_query tool.
2. Compare values by writing SQL queries that fetch data from different time ranges.
3. If the user asks for a chart, generate an <artifact>.
4. Be concise in your text response, let the data and artifacts speak.
5. You can chain tool calls. After getting a tool result, you can call another tool or give the final answer.
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
    """Execute a tool via MCP client"""
    logger.info(f"Executing tool: {tool_name} with args: {args}")
    
    if tool_name == "execute_query":
        # Ensure query is safe-ish (basic check)
        query = args.get("query", "")
        if not query.lower().strip().startswith("select"):
            return "Error: Only SELECT queries are allowed."
        
        try:
            # Use MCP client to execute
            # We assume the tool name in MCP server is 'query' or 'execute_query'
            # If not, we might need to adjust.
            result = await mcp_client.call_tool("query", {"query": query})
            if "error" in result:
                return f"Tool Error: {result['error']}"
            return json.dumps(result)
        except Exception as e:
            return f"Tool Execution Failed: {str(e)}"
            
    return f"Error: Unknown tool '{tool_name}'"

async def stream_chat_response(prompt: str, context_data: str = "", conversation_history: str = ""):
    """
    Stream chat response with ReAct loop
    """
    current_prompt = f"{SYSTEM_PROMPT}\n\nContext Data:\n{context_data}\n\nConversation History:\n{conversation_history}\n\nUser Query: {prompt}"
    
    max_turns = 5
    current_turn = 0
    
    while current_turn < max_turns:
        current_turn += 1
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
                        "temperature": 0.1,
                        "num_predict": 2048
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
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                            
                    except json.JSONDecodeError:
                        continue

        # Check for tool calls
        tool_match = re.search(r'\[TOOL:\s*(\w+)\s*({.*?})\]', full_response, re.DOTALL)
        
        if tool_match:
            tool_name = tool_match.group(1)
            tool_args_str = tool_match.group(2)
            
            try:
                tool_args = json.loads(tool_args_str)
                yield f"data: {json.dumps({'status': f'Running tool: {tool_name}'})}\n\n"
                
                tool_result = await execute_tool(tool_name, tool_args)
                
                # Append result to prompt and loop
                current_prompt += f"\n\n{full_response}\n\n[TOOL_RESULT]:\n{tool_result}\n\n"
                continue
                
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'error': 'Failed to parse tool arguments'})}\n\n"
                break
        
        # If no tool call, we are done
        break
    
    yield f"data: {json.dumps({'done': True})}\n\n"

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Send a chat message (Non-streaming wrapper)
    """
    response_text = ""
    async for chunk_str in stream_chat_response(request.message):
        if chunk_str.startswith("data: "):
            data = json.loads(chunk_str[6:])
            if "chunk" in data:
                response_text += data["chunk"]
    
    return ChatResponse(
        response=response_text,
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
