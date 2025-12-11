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

# System prompt optimized for code generation
SYSTEM_PROMPT = """You are a PLC data visualization assistant. You MUST fetch real data using MCP tools and generate executable React charts.

AVAILABLE MCP TOOLS:
[TOOL: query {"sql": "SELECT ..."}] - Execute SQL query and get REAL data from database

DATABASE SCHEMA:
- Table: plc_data
- Columns: timestamp (timestamptz), device_id (text), type (text), data (jsonb), metadata (jsonb)
- Temperature stored in: data->>'temperature' (cast to float)
- Example: SELECT timestamp, device_id, (data->>'temperature')::float AS temperature FROM plc_data WHERE type = 'temperature' LIMIT 10

CRITICAL WORKFLOW (ALWAYS FOLLOW):
1. **ALWAYS use [TOOL: query] to fetch REAL data** - Never use hardcoded sample data!
2. Parse the query results and convert to JavaScript array format
3. Write 1-2 sentences explaining what data was found
4. Generate <artifact> with the REAL data embedded in the code

CHART GENERATION RULES:
1. **Data Format**: Transform SQL results into: [{timestamp: "ISO_DATE", device: "device_id", value: NUMBER}, ...]
2. **Multiple Devices**: Use separate Line component for EACH device (not data prop on Line)
3. **Colors**: Assign unique color per device from: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
4. **Timestamp Formatting**: Use tickFormatter on XAxis for readable dates
5. **Responsive**: Always wrap in ResponsiveContainer with width="100%" height={400}

EXACT ARTIFACT FORMAT (CRITICAL):
<artifact type="react" title="Descriptive Title">
```tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ChartComponent() {
  // REAL data from database (not sample data!)
  const data = [
    {timestamp: "2025-12-11T10:30:00Z", device: "plc1", value: 23.5},
    {timestamp: "2025-12-11T10:31:00Z", device: "plc1", value: 24.1},
    {timestamp: "2025-12-11T10:30:00Z", device: "plc2", value: 22.8},
    // ... more REAL data points
  ];
  
  const devices = [...new Set(data.map(d => d.device))];
  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
  
  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Chart Title</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(ts) => new Date(ts).toLocaleTimeString()} 
          />
          <YAxis />
          <Tooltip labelFormatter={(ts) => new Date(ts).toLocaleString()} />
          <Legend />
          {devices.map((device, idx) => (
            <Line 
              key={device}
              type="monotone"
              dataKey="value"
              data={data.filter(d => d.device === device)}
              name={device}
              stroke={colors[idx % colors.length]}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```
</artifact>

REMEMBER: 
- NEVER use fake/sample data - ALWAYS query database first!
- Each Line needs its own filtered dataset via data prop
- Use type="monotone" for smooth connected lines
- Always include proper timestamp formatting
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
    Stream chat response with ReAct loop and artifact generation
    """
    # Check if user wants a dashboard/chart
    wants_visualization = any(keyword in prompt.lower() for keyword in ['chart', 'dashboard', 'visualiz', 'graph', 'plot', 'show'])
    
    current_prompt = f"{SYSTEM_PROMPT}\n\nContext Data:\n{context_data}\n\nConversation History:\n{conversation_history}\n\nUser Query: {prompt}\n\nProvide a clear response. If you need data, use a tool first, then answer based on the results."
    
    max_turns = 3
    current_turn = 0
    final_response = ""
    accumulated_response = ""
    tool_results = []
    
    while current_turn < max_turns:
        current_turn += 1
        logger.info(f"ReAct turn {current_turn}/{max_turns}")
        full_response = ""
        
        # Call Ollama
        async with httpx.AsyncClient() as client:
            model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
            async with client.stream(
                "POST",
                "http://ollama:11434/api/generate",
                json={
                    "model": model,
                    "prompt": current_prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 4096
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

        # Check for artifact first (if visualization requested)
        if wants_visualization and '<artifact' in full_response:
            # Found an artifact - this is the final response
            accumulated_response += full_response
            break

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
                tool_results.append({"tool": tool_name, "args": tool_args, "result": tool_result})
                logger.info(f"Tool result length: {len(tool_result)}")
                
                # If visualization requested and we have data, create artifact
                if wants_visualization and tool_name == "query" and current_turn == 1:
                    current_prompt = f"""{SYSTEM_PROMPT}

Query: {prompt}
Data: {tool_result}

Generate:
1. 2-3 sentence summary
2. <artifact type="react" title="...">```tsx
   - import React + Recharts
   - embed the data as const
   - LineChart/BarChart component
   - export default
```</artifact>"""
                else:
                    current_prompt = f"{SYSTEM_PROMPT}\n\nQuery: {prompt}\nData: {tool_result}\n\nAnswer briefly."
                
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
    
    # Fix markdown code blocks to artifact tags
    # Match ```markdown or ```json followed by chart config
    artifact_pattern = r'```(?:markdown|json)\s*\n(\{[\s\S]*?"charts"[\s\S]*?\})\s*\n```'
    
    def replace_with_artifact(match):
        content = match.group(1)
        # Try to extract title from preceding text
        title = "Dashboard"
        if "temperature" in accumulated_response.lower():
            title = "Temperature Monitoring Dashboard"
        return f'<artifact type="react" title="{title}">\n{content}\n</artifact>'
    
    clean = re.sub(artifact_pattern, replace_with_artifact, clean)
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
