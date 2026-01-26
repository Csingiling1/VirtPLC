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
from ..services.claude_client import claude_client
from ..database import get_db
from ..database.models import ChatSession, ChatMessage
from ..config import settings

import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

# System prompt optimized for time-series data extraction and visualization (Ollama)
SYSTEM_PROMPT = """You are an expert Time-Series Database Assistant and Data Visualization Engineer.
You have access to a TimescaleDB (PostgreSQL) database via the query_timescale tool.

### CORE OBJECTIVE
Retrieve sensor data based on user prompts and transform it into React visualizations.

### ⚠️ CRITICAL TOOL CALLING FORMAT
When you need to query the database, you MUST use this EXACT format:
[TOOL: query_timescale {"query": "SELECT ... FROM plc_data ..."}]

DO NOT output raw JSON like {"query": "..."}
DO NOT output just the SQL query
ALWAYS wrap it in [TOOL: query_timescale {...}]

### RESPONSE MODES

**Mode 1: Simple Answer (no data needed)**
- User asks general questions: "What sensors are available?"
- Response: Direct answer in natural language

**Mode 2: Data Query (needs database)**
- User asks for data: "Show me conveyor1 RPM for last hour"
- Step 1: Call tool: [TOOL: query_timescale {"query": "SELECT ..."}]
- Step 2: Wait for data (system will execute this)
- Step 3: You will be given the data to create visualization

**Mode 3: Visualization**
- After data is retrieved, create React chart with the data embedded

### QUERY RULES
1. **NEVER TRUNCATE TIME**: Do NOT use LIMIT when user asks for time ranges (e.g., "last 24 hours")
2. **DOWNSAMPLE INSTEAD**: Use time_bucket() to reduce rows while preserving full time range
3. **ROW LIMIT**: Keep results under 150 rows using appropriate bucketing
4. **HARDCODE DATA**: Generate React components with data array embedded directly

### DATABASE SCHEMA - CRITICAL
Table: plc_data (TimescaleDB hypertable)
Columns:
- timestamp (TIMESTAMPTZ): When data was recorded
- device_id (TEXT): Device identifier
- type (TEXT): 'sensor' (simulator data) OR 'UNREAL' (Unreal Engine devices)
- rpm (FLOAT): Direct RPM value (for UNREAL type only)
- position_x (FLOAT): X position (for UNREAL type only)
- position_y (FLOAT): Y position (for UNREAL type only)
- data (JSONB): For 'sensor' type: contains signal_config->>'name' and signal_config->>'value'
- metadata (JSONB): Additional info

**CRITICAL: Two Different Data Storage Patterns**

**Pattern 1: UNREAL Devices (conveyor1, conveyor2, placer1)**
- type = 'UNREAL'
- device_id: 'conveyor1', 'conveyor2', 'placer1'
- RPM stored in: rpm column (direct float)
- Position stored in: position_x, position_y columns
- Example query:
  ```sql
  SELECT timestamp, device_id, rpm
  FROM plc_data
  WHERE type = 'UNREAL' AND device_id = 'conveyor1'
  ORDER BY timestamp DESC
  ```

**Pattern 2: Simulator Sensors (motor_speed_PLC-NY-001, etc.)**
- type = 'sensor'
- device_id format: sensorname_PLCID (e.g., 'motor_speed_PLC-NY-001')
- Value stored in: (data->'signal_config'->>'value')::float
- Sensor name in: data->'signal_config'->>'name'
- Example query:
  ```sql
  SELECT timestamp, device_id, 
         (data->'signal_config'->>'value')::float AS value
  FROM plc_data
  WHERE type = 'sensor' 
    AND data->'signal_config'->>'name' = 'motor_speed'
  ORDER BY timestamp DESC
  ```

**Device Identification:**
- If user mentions 'conveyor1', 'conveyor2', or 'placer1' → Use type='UNREAL', query rpm column
- If user mentions motors, sensors, or PLC names → Use type='sensor', query data JSONB

### ⏳ BUCKET INTERVAL GUIDE
- **Last 1 Hour**: time_bucket('30 seconds', timestamp)
- **Last 6 Hours**: time_bucket('5 minutes', timestamp)
- **Last 24 Hours**: time_bucket('15 minutes', timestamp)
- **Last 7 Days**: time_bucket('2 hours', timestamp)
- **Last 30 Days**: time_bucket('6 hours', timestamp)

### QUERY EXAMPLES

**UNREAL Device - Latest RPM:**
```sql
SELECT timestamp, device_id, rpm
FROM plc_data
WHERE type='UNREAL' AND device_id = 'conveyor1'
ORDER BY timestamp DESC LIMIT 1
```

**UNREAL Device - Time-bucketed RPM (last hour):**
```sql
SELECT time_bucket('5 minutes', timestamp) AS period,
       AVG(rpm) AS avg_rpm,
       MAX(rpm) AS max_rpm,
       MIN(rpm) AS min_rpm
FROM plc_data
WHERE type='UNREAL' 
  AND device_id = 'conveyor1'
  AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY period
ORDER BY period ASC
```

**Simulator Sensor - Latest readings:**
```sql
SELECT timestamp, device_id, 
       (data->'signal_config'->>'value')::float AS value
FROM plc_data
WHERE type='sensor' 
  AND data->'signal_config'->>'name' = 'motor_speed'
ORDER BY timestamp DESC LIMIT 50
```

**Simulator Sensor - Time-bucketed (24 hours):**
```sql
SELECT time_bucket('15 minutes', timestamp) AS period,
       device_id,
       avg((data->'signal_config'->>'value')::float) AS avg_value,
       max((data->'signal_config'->>'value')::float) AS max_value
FROM plc_data
WHERE type='sensor'
  AND data->'signal_config'->>'name' = 'motor_temp'
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY period, device_id
ORDER BY period ASC, device_id
```

**Current state (all sensors):**
```sql
SELECT DISTINCT ON (device_id) 
       timestamp, device_id,
       (data->'signal_config'->>'value')::float AS value,
       data->'signal_config'->>'name' AS sensor_name
FROM plc_data
WHERE type='sensor'
ORDER BY device_id, timestamp DESC
```

### EXECUTION PLAN
1. **Analyze**: Determine query type and time range
2. **Calculate**: Choose appropriate bucket interval for time-series
3. **Execute**: Generate [TOOL: query_timescale] call
4. **Visualize**: Create React artifact with embedded data

WORKFLOW (Internal - DO NOT output these steps):
1. Analyze query to determine what data to fetch
2. Generate SQL query and call [TOOL: query_timescale]
3. Generate React artifact with the data

OUTPUT FORMAT:
Just output the <artifact> tag with the React code inside. No explanations, no steps, no SQL shown to user.


ARTIFACT FORMAT - CRITICAL RULES:
1. ALWAYS add key prop to mapped components
2. Use unique identifiers for keys (device names, indices)
3. Filter data BEFORE passing to Line component
4. Format timestamps for readability
5. The data field for device is 'device_id' (from database query)

<artifact type="react" title="Descriptive Title">
```tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ChartComponent() {
  const data = [
    // REAL data from database embedded here as array of objects
    // Each object has: timestamp, device_id, value
    {timestamp: "2025-12-12T00:00:00Z", device_id: "motor1", value: 1500},
  ];
  
  // Get unique devices for creating separate lines
  const devices = [...new Set(data.map(d => d.device_id))];
  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
  
  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Chart Title</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(ts) => {
              const date = new Date(ts);
              return date.toLocaleTimeString();
            }}
          />
          <YAxis />
          <Tooltip 
            labelFormatter={(ts) => {
              const date = new Date(ts);
              return date.toLocaleString();
            }}
          />
          <Legend />
          {devices.map((device, idx) => {
            const deviceData = data.filter(d => d.device_id === device);
            return (
              <Line 
                key={device}
                type="monotone"
                dataKey="value"
                data={deviceData}
                name={device}
                stroke={colors[idx % colors.length]}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```
</artifact>

IMPORTANT: Always wrap map() return in braces and return statement with key prop!
"""

# System prompt optimized for Claude
SYSTEM_PROMPT_CLAUDE = """You are an expert Time-Series Database Assistant and Data Visualization Engineer.
You have access to a TimescaleDB (PostgreSQL) database via the query_timescale tool. Your goal is to answer user questions by fetching data and generating React-based visualizations.

**Execution Plan:**
1.  **Analyze User Request**: Understand the user's query to determine the required data.
2.  **Generate Tool Call**: Create a `[TOOL: query_timescale]` call with the appropriate SQL query.
3.  **Receive Tool Output**: You will be given the data returned from the tool.
4.  **Generate Visualization**: Create a React component as an `<artifact>` that visualizes the data.

**Critical Rules for SQL Generation:**
*   **Time-Series Queries**: For queries over a time range (e.g., "last 24 hours"), you **MUST** use `time_bucket()` to downsample the data. Do **NOT** use `LIMIT` for time-range queries. Aim for about 100-150 data points.
*   **Current State Queries**: For queries about the current state (e.g., "what is the motor speed now?"), use `ORDER BY timestamp DESC LIMIT 1`.
*   **Bucket Intervals**:
    *   Last 1 Hour: `time_bucket('30 seconds', timestamp)`
    *   Last 24 Hours: `time_bucket('15 minutes', timestamp)`
    *   Last 7 Days: `time_bucket('2 hours', timestamp)`

**Database Schema:**
*   Table: `plc_data`
*   Columns:
    *   `timestamp` (TIMESTAMPTZ)
    *   `device_id` (TEXT)
    *   `type` (TEXT: 'sensor' or 'plc')
    *   `data` (JSONB): Contains `signal_config.name` and `signal_config.value`.
*   Common Sensor Names: `motor_speed`, `motor_temp`, `vibration`, `pressure`, `flow_rate`.

**Output Format:**
*   When you need to query data, respond ONLY with the tool call: `[TOOL: query_timescale {"query": "SELECT ..."}]`
*   After you receive the data, respond ONLY with the final React visualization inside an `<artifact>` tag. Do not include any other text or explanation.

**Artifact Format:**
*   Use the provided `recharts` library.
*   Embed the data directly into the component.
*   Ensure components in `map()` have a `key` prop.
*   Format timestamps for readability on the X-axis.

Example Artifact:
<artifact type="react" title="Motor Speed Over Time">
```tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ChartComponent() {
  const data = [
    {"period": "2025-12-18T10:00:00Z", "avg_speed": 1500},
    {"period": "2025-12-18T10:01:00Z", "avg_speed": 1502},
  ];

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="period" tickFormatter={(ts) => new Date(ts).toLocaleTimeString()} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="avg_speed" stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );
}
```
</artifact>
"""


class ChatRequest(BaseModel):
    message: str
    session_id: int = None
    context: Dict[str, Any] = None
    stream: bool = False
    model: str = "ollama"  # "ollama" or "claude"

class ChatResponse(BaseModel):
    response: str
    session_id: int
    metadata: Optional[Dict[str, Any]] = None
    chart_suggestions: Optional[List[Dict[str, Any]]] = None

async def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute MCP tools for database access"""
    logger.info(f"Executing MCP tool: {tool_name} with args: {args}")
    
    try:
        # Use MCP client for database operations
        if tool_name == "query" or tool_name == "query_timescale":
            sql = args.get("query") or args.get("sql", "")
            if not sql.strip():
                return {"error": "SQL query is required"}
            
            logger.info(f"Executing SQL: {sql[:200]}...")
            result = await mcp_client.call_tool("query_timescale", {"query": sql})
            
            # Parse MCP response
            if "content" in result and isinstance(result["content"], list):
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        text = content_item.get("text", "")
                        # Try to extract structured data from the text response
                        data_rows = parse_mcp_result(text)
                        if data_rows:
                            return {"success": True, "data": data_rows, "count": len(data_rows)}
                
                # Fallback: return raw text
                return {"success": True, "raw": result}
            
            return result
        
        else:
            return {"error": f"Unknown tool '{tool_name}'"}
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return {"error": f"Tool execution failed: {str(e)}"}

def parse_mcp_result(text: str) -> List[Dict[str, Any]]:
    """
    Parse MCP query result text into structured data
    Handles TSV format from db-mcp-server
    """
    try:
        lines = text.strip().split('\n')
        if len(lines) < 3:
            return []
        
        # Find header line (contains column names)
        header_idx = -1
        headers = []
        for i, line in enumerate(lines):
            if '\t' in line and not line.startswith('-'):
                headers = [h.strip() for h in line.split('\t')]
                header_idx = i
                break
        
        if header_idx == -1:
            return []
        
        # Find data rows (after separator line)
        data_rows = []
        found_separator = False
        for i in range(header_idx + 1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            if line.startswith('-'):
                found_separator = True
                continue
            if line.startswith('Total rows:'):
                break
            if found_separator and '\t' in line:
                values = [v.strip() for v in line.split('\t')]
                if len(values) == len(headers):
                    row = dict(zip(headers, values))
                    # Try to convert numeric values
                    for key in row:
                        if row[key] and row[key].replace('.', '', 1).replace('-', '', 1).isdigit():
                            try:
                                row[key] = float(row[key])
                            except:
                                pass
                    data_rows.append(row)
        
        return data_rows
    except Exception as e:
        logger.error(f"Failed to parse MCP result: {e}")
        return []

def extract_tool_call(text: str) -> Optional[Dict[str, Any]]:
    """
    Robustly extract tool calls from text, handling nested JSON and multiline strings.
    Returns: dict with 'name', 'args', 'full_match' or None
    """
    # Find start of tool call: [TOOL: toolname {
    match = re.search(r'\[TOOL:\s*(\w+)\s*(\{)', text, re.DOTALL)
    if not match:
        return None
    
    tool_name = match.group(1)
    start_brace_index = match.start(2)
    
    # Count braces to find the end of the JSON object
    brace_count = 0
    in_string = False
    escape = False
    
    for i in range(start_brace_index, len(text)):
        char = text[i]
        
        if escape:
            escape = False
            continue
            
        if char == '\\':
            escape = True
            continue
            
        if char == '"':
            in_string = not in_string
            continue
            
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                
                if brace_count == 0:
                    # Found the end of the JSON object
                    json_str = text[start_brace_index:i+1]
                    try:
                        # Verify it's valid JSON
                        args = json.loads(json_str)
                        
                        # Look for the closing ']' after the JSON
                        end_index = i + 1
                        remaining = text[end_index:]
                        closing_bracket_match = re.match(r'\s*\]', remaining)
                        full_match_end = end_index
                        if closing_bracket_match:
                            full_match_end += closing_bracket_match.end()
                            
                        full_match = text[match.start():full_match_end]
                        return {
                            "name": tool_name,
                            "args": args,
                            "full_match": full_match
                        }
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON in tool call: {e}")
                        # Continue searching in case this wasn't the real end
                        pass
    
    return None

async def stream_chat_response(prompt: str, context_data: str = "", conversation_history: str = ""):
    """
    Stream chat response with tool calling and artifact generation
    
    Workflow:
    1. Send query to Ollama to get tool call for data fetching
    2. Execute tool to get real data from database via MCP
    3. Send data back to Ollama to generate React artifact
    4. Stream the final response with artifact to client
    """
    logger.info(f"Processing query: {prompt[:100]}...")
    
    # Phase 1: Get data requirements and tool call
    yield f"data: {json.dumps({'status': '🤔 Analyzing query...'})}\n\n"
    
    initial_prompt = f"""{SYSTEM_PROMPT}

User Query: {prompt}

CRITICAL ANALYSIS:
1. Identify query type (Current State / Aggregate / Time-Series)
2. If Time-Series with time range: Calculate bucket interval (never use LIMIT alone)
3. If "last N readings" for specific sensor: Use WHERE sensor_name='X' and LIMIT N
4. If time period mentioned (hours/days): Use time_bucket() with appropriate interval

Generate ONLY the tool call based on the strategy:
[TOOL: query_timescale {{"query": "SELECT ..."}}]
"""
    
    try:
        # Call Ollama for initial analysis
        first_response = ""
        async with httpx.AsyncClient(timeout=300.0) as client:
            model = settings.ollama_model
            logger.info(f"Calling Ollama model: {model}")
            
            async with client.stream(
                "POST",
                f"{settings.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": initial_prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 2048
                    }
                }
            ) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            first_response += data["response"]
                    except json.JSONDecodeError:
                        continue
        
        logger.debug(f"Initial response: {first_response[:300]}")
        
        # Phase 2: Extract and execute tool call
        tool_data = extract_tool_call(first_response)
        
        if not tool_data:
            # No tool call found, return the response as-is
            yield f"data: {json.dumps({'done': True, 'final_response': first_response.strip()})}\n\n"
            return
        
        tool_name = tool_data["name"]
        tool_args = tool_data["args"]
        
        yield f"data: {json.dumps({'status': f'📊 Fetching {tool_name} data...'})}\n\n"
        logger.info(f"Executing tool: {tool_name}")
        
        tool_result = await execute_tool(tool_name, tool_args)
        
        if "error" in tool_result:
            error_msg = f"Error fetching data: {tool_result['error']}"
            yield f"data: {json.dumps({'done': True, 'final_response': error_msg})}\n\n"
            return
        
        # Extract data rows
        data_rows = tool_result.get("data", [])
        logger.info(f"Retrieved {len(data_rows)} data rows")
        
        if not data_rows:
            yield f"data: {json.dumps({'done': True, 'final_response': 'No data found for your query.'})}\n\n"
            return
        
        # Phase 3: Generate artifact with the real data
        yield f"data: {json.dumps({'status': '🎨 Generating visualization...'})}\n\n"
        
        # Format data for artifact generation
        data_summary = f"Retrieved {len(data_rows)} rows with columns: {list(data_rows[0].keys()) if data_rows else []}"
        data_json = json.dumps(data_rows[:100], indent=2)  # Limit to 100 rows for context
        
        artifact_prompt = f"""{SYSTEM_PROMPT}

User Query: {prompt}

Database Query Result ({len(data_rows)} rows retrieved):
{data_summary}

Sample Data (showing first 100 of {len(data_rows)} rows):
{data_json[:2000]}

CRITICAL INSTRUCTIONS:
1. Use 'device_id' field for device names (NOT 'device')
2. For time-bucketed queries: use 'period' as time field
3. For raw timestamp queries: use 'timestamp' as time field
4. Hardcode ALL the data from query results
5. Add key={{device}} in map() functions
6. Choose appropriate chart title based on sensor type and time range

Generate ONLY the artifact (no explanations):
<artifact type="react" title="Descriptive Title">
```tsx
[React component with embedded data]
```
</artifact>
"""
        
        final_response = ""
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                f"{settings.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": artifact_prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.4,
                        "num_predict": 4096
                    }
                }
            ) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            chunk = data["response"]
                            final_response += chunk
                            # Stream chunks to client
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    except json.JSONDecodeError:
                        continue
        
        # Clean up the response to only include artifact
        # Remove the Step 1, Step 2, Step 3 headers and tool calls
        clean_response = final_response
        
        # Remove "Step X: ..." sections
        clean_response = re.sub(r'Step \d+:.*?\n', '', clean_response)
        
        # Remove tool call syntax [TOOL: ...]
        clean_response = re.sub(r'\[TOOL:.*?\]', '', clean_response, flags=re.DOTALL)
        
        # Remove any explanatory text before the artifact
        if '<artifact' in clean_response:
            # Extract just the artifact part
            artifact_match = re.search(r'(<artifact.*?</artifact>)', clean_response, re.DOTALL)
            if artifact_match:
                clean_response = artifact_match.group(1)
        elif '```tsx' in clean_response:
            # Wrap code block in artifact tags if not already wrapped
            clean_response = f'<artifact type="react" title="Data Visualization">\n{clean_response}\n</artifact>'
        
        yield f"data: {json.dumps({'done': True, 'final_response': clean_response.strip()})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in stream_chat_response: {e}", exc_info=True)
        error_msg = f"An error occurred: {str(e)}"
        yield f"data: {json.dumps({'done': True, 'final_response': error_msg})}\n\n"

async def stream_claude_response(prompt: str, context_data: str = "", conversation_history: str = ""):
    """
    Stream chat response for Claude with tool calling and artifact generation.
    """
    logger.info(f"Processing query with Claude: {prompt[:100]}...")
    yield f"data: {json.dumps({'status': '🤔 Analyzing query with Claude...'})}\n\n"

    initial_prompt = f"User Query: {prompt}\n\nAnalyze this query and generate the appropriate `[TOOL: query_timescale]` call to fetch the necessary data. Do not generate the visualization yet."

    try:
        # Phase 1: Get tool call from Claude
        first_response = await claude_client.generate_text(prompt=initial_prompt, system_prompt=SYSTEM_PROMPT_CLAUDE)
        logger.debug(f"Claude initial response: {first_response[:300]}")

        # Phase 2: Extract and execute tool call
        tool_data = extract_tool_call(first_response)
        if not tool_data:
            yield f"data: {json.dumps({'done': True, 'final_response': first_response.strip()})}\n\n"
            return

        tool_name = tool_data["name"]
        tool_args = tool_data["args"]
        yield f"data: {json.dumps({'status': f'📊 Fetching {tool_name} data...'})}\n\n"
        
        tool_result = await execute_tool(tool_name, tool_args)
        if "error" in tool_result:
            error_msg = f"Error fetching data: {tool_result['error']}"
            yield f"data: {json.dumps({'done': True, 'final_response': error_msg})}\n\n"
            return

        data_rows = tool_result.get("data", [])
        if not data_rows:
            yield f"data: {json.dumps({'done': True, 'final_response': 'No data found for your query.'})}\n\n"
            return
        
        logger.info(f"Retrieved {len(data_rows)} data rows for Claude")

        # Phase 3: Generate artifact with the real data
        yield f"data: {json.dumps({'status': '🎨 Generating visualization with Claude...'})}\n\n"
        
        data_summary = f"Retrieved {len(data_rows)} rows."
        data_json = json.dumps(data_rows[:100], indent=2)
        
        artifact_prompt = f"""You have received the following data from the `query_timescale` tool.

Database Query Result ({len(data_rows)} rows retrieved):
{data_summary}

Sample Data (showing first 100 of {len(data_rows)} rows):
{data_json[:2000]}

Now, generate the final React component artifact based on the user's original query: "{prompt}"
"""
        
        final_response = ""
        async for chunk in claude_client.stream_text(prompt=artifact_prompt, system_prompt=SYSTEM_PROMPT_CLAUDE):
            final_response += chunk
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        if '<artifact' not in final_response:
             final_response = f'<artifact type="react" title="Data Visualization">\n```tsx\n{final_response}\n```\n</artifact>'

        yield f"data: {json.dumps({'done': True, 'final_response': final_response.strip()})}\n\n"

    except Exception as e:
        logger.error(f"Error in stream_claude_response: {e}", exc_info=True)
        error_msg = f"An error occurred with Claude: {str(e)}"
        yield f"data: {json.dumps({'done': True, 'final_response': error_msg})}\n\n"


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Send a chat message (Non-streaming wrapper)
    """
    response_text = ""
    final_text = ""
    logger.info(f"Processing chat message with {request.model}: {request.message[:100]}...")
    
    # Choose the appropriate streaming function based on model
    if request.model.lower() == "claude":
        stream_func = stream_claude_response
    else:
        stream_func = stream_chat_response
    
    async for chunk_str in stream_func(request.message):
        if chunk_str.startswith("data: "):
            data = json.loads(chunk_str[6:])
            if "chunk" in data:
                response_text += data["chunk"]
            if "final_response" in data:
                final_text = data["final_response"]
    
    result = final_text if final_text else response_text
    
    logger.info(f"Chat response generated with {request.model}: {len(result)} chars")
    return ChatResponse(response=result, session_id=1)

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming endpoint with model selection
    """
    # Choose the appropriate streaming function based on model
    if request.model.lower() == "claude":
        stream_func = stream_claude_response
    else:
        stream_func = stream_chat_response
    
    return StreamingResponse(
        stream_func(request.message),
        media_type="text/event-stream"
    )


@router.post("/claude")
async def chat_with_claude(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint specifically for Claude AI model.
    Provides direct access to Claude without the complex tool-calling system.
    """
    try:
        logger.info(f"Processing Claude chat request: {request.message[:100]}...")

        # Claude system prompt - more conversational and helpful
        claude_system_prompt = """You are Claude, an AI assistant specialized in industrial IoT systems and data analysis.

You have access to a VirtPLC system with:
- Real-time sensor data from industrial equipment
- Time-series database with historical data
- PLC control systems and automation
- Data visualization capabilities

Help users with:
- Analyzing sensor data and trends
- Troubleshooting industrial equipment
- Optimizing manufacturing processes
- Predictive maintenance insights
- Data visualization recommendations

Be conversational, helpful, and provide actionable insights. If users need specific data queries, suggest what information would be helpful to retrieve."""

        # Generate response using Claude
        response_text = await claude_client.generate_text(
            prompt=request.message,
            system_prompt=claude_system_prompt
        )

        # Create response
        response = ChatResponse(
            response=response_text,
            session_id=request.session_id or 1,
            metadata={
                "model": "claude",
                "provider": "anthropic",
                "system_prompt": "industrial_iot_specialist"
            }
        )

        logger.info(f"Claude response generated, length: {len(response_text)}")
        return response

    except Exception as e:
        logger.error(f"Error in Claude chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Claude service error: {str(e)}"
        )
