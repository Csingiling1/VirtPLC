# VirtPLC - Complete System Architecture

## Executive Summary

**VirtPLC** is a full-stack Industrial IoT platform with multi-tenant capabilities, AI-powered analytics, and real-time data visualization. The system supports both **Ollama** (local, open-source) and **Claude** (cloud, advanced) AI models for natural language queries and React code generation.

---

## 🎯 AI Service - Dual Model Architecture

### Current Implementation Status

#### ✅ **Ollama (Fully Implemented)**
- **Model**: `qwen2:0.5b` (configurable via `OLLAMA_MODEL`)
- **Host**: `http://ollama:11434`
- **Capabilities**:
  - ✅ Natural language query understanding
  - ✅ SQL query generation via tool calling
  - ✅ React chart component generation
  - ✅ Streaming responses
  - ✅ Data visualization with embedded data

**Workflow**:
```
User Query → Ollama generates [TOOL: query_timescale] 
→ MCP executes SQL → Returns data 
→ Ollama generates React component with hardcoded data
→ Frontend renders chart
```

#### 🔧 **Claude (Configured, Awaiting API Key)**
- **Model**: `claude-3-opus-20240229` (configurable via `CLAUDE_MODEL`)
- **Config File**: `ai-service/src/config.py` (lines 28-31)
- **Client**: `ai-service/src/services/claude_client.py`
- **Capabilities** (when API key provided):
  - ✅ Advanced natural language understanding
  - ✅ Superior code generation quality
  - ✅ Multi-step reasoning for complex queries
  - ✅ Streaming responses
  - ⚠️ **LIMITATION**: Cannot execute code directly

**Configuration Required**:
```bash
# Set in .env or environment variables
CLAUDE_API_KEY=sk-ant-api03-xxxxx
CLAUDE_MODEL=claude-3-opus-20240229  # or claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4096
```

### 🔍 Code Execution Capabilities

#### ❌ **Claude CANNOT Execute Code**
Claude's API is text-generation only. It can:
- ✅ Generate React/TypeScript code
- ✅ Generate SQL queries
- ✅ Explain code and suggest improvements
- ❌ **Cannot run or execute code directly**

If you need **code execution** with Claude, you would need:
1. **External sandbox** (e.g., E2B, Replit, custom Docker container)
2. **Agent framework** (LangChain, CrewAI) to orchestrate execution
3. **Custom execution layer** in your ai-service

#### ✅ **Current Workflow Works Without Direct Execution**
```
1. User: "Show conveyor1 RPM for last hour"
2. Claude generates: SQL query + React component code
3. System executes: SQL via MCP
4. System injects: Data into React component
5. Frontend renders: Chart with real data
```

**This is MORE SECURE** than allowing Claude to execute arbitrary code.

---

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER (Port 80/443)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    NGINX Reverse Proxy                                │  │
│  │  - Rate Limiting: 10 req/s (API), 5 req/s (data), 100 req/s (static) │  │
│  │  - Security: HSTS, CSP, X-Frame-Options, Slowloris protection        │  │
│  │  - Load Balancing: Round-robin to backend instances                  │  │
│  └────┬──────────────┬──────────────┬──────────────┬─────────────────────┘  │
│       │              │              │              │                        │
└───────┼──────────────┼──────────────┼──────────────┼────────────────────────┘
        ▼              ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │Frontend │   │ Backend  │   │AI Service│   │Collector │
   │React+TS │   │Spring Boot│   │FastAPI+  │   │  Go      │
   │Port 5173│   │Port 8080 │   │ Ollama   │   │gRPC 9090 │
   └────┬────┘   └────┬─────┘   │Port 3001 │   └────┬─────┘
        │             │          └────┬─────┘        │
        │             │               │              │
┌───────┴─────────────┴───────────────┴──────────────┴───────────────────────┐
│                          DATA & SERVICES LAYER                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ TimescaleDB  │◄───│    Redis     │    │  PostgreSQL  │               │
│  │ Time-Series  │    │    Cache     │    │  Relational  │               │
│  │ Port 5432    │    │  Port 6379   │    │  Port 5432   │               │
│  │              │    │              │    │              │               │
│  │ • plc_data   │    │ • Sessions   │    │ • Users      │               │
│  │ • rpm column │    │ • Cache keys │    │ • ChatSessions│              │
│  │ • position_x │    │ • Rate limit │    │ • ChatMessages│              │
│  │ • data JSONB │    │              │    │              │               │
│  └──────▲───────┘    └──────▲───────┘    └──────▲───────┘               │
│         │                   │                    │                        │
│         │                   │                    │                        │
│  ┌──────┴───────────────────┴────────────────────┴─────┐                 │
│  │              MCP (Model Context Protocol)           │                 │
│  │          Backend Port 8000 (db-mcp-server)          │                 │
│  │                                                      │                 │
│  │  Tools:                                              │                 │
│  │  • query_timescale: Execute SQL on TimescaleDB      │                 │
│  │  • list_tables: Show available tables               │                 │
│  │  • describe_table: Get table schema                 │                 │
│  └──────────────────────────────────────────────────────┘                 │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                      AI PROCESSING LAYER                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │                    AI Service (FastAPI)                          │     │
│  │                                                                  │     │
│  │  ┌─────────────────────────────────────────────────────────┐   │     │
│  │  │           Chat Router (/api/ai/chat)                    │   │     │
│  │  │                                                          │   │     │
│  │  │  Endpoints:                                              │   │     │
│  │  │  • POST /message  - Non-streaming chat                  │   │     │
│  │  │  • POST /stream   - Server-sent events streaming        │   │     │
│  │  │                                                          │   │     │
│  │  │  Model Selection (via request.model):                   │   │     │
│  │  │  ┌────────────────┐        ┌──────────────────┐        │   │     │
│  │  │  │  "ollama"      │        │    "claude"      │        │   │     │
│  │  │  │  (default)     │        │  (if API key)    │        │   │     │
│  │  │  └───────┬────────┘        └────────┬─────────┘        │   │     │
│  │  │          ▼                           ▼                  │   │     │
│  │  │  ┌───────────────┐          ┌───────────────┐          │   │     │
│  │  │  │ Ollama Client │          │ Claude Client │          │   │     │
│  │  │  │ Local Model   │          │  Anthropic API│          │   │     │
│  │  │  │ qwen2:0.5b    │          │ claude-3-opus │          │   │     │
│  │  │  └───────┬───────┘          └───────┬───────┘          │   │     │
│  │  │          │                           │                  │   │     │
│  │  │          └───────────┬───────────────┘                  │   │     │
│  │  │                      ▼                                  │   │     │
│  │  │          ┌───────────────────────┐                      │   │     │
│  │  │          │  Tool Call Extraction │                      │   │     │
│  │  │          │ [TOOL: query_timescale│                      │   │     │
│  │  │          │   {"query": "SELECT"} │                      │   │     │
│  │  │          └───────────┬───────────┘                      │   │     │
│  │  │                      ▼                                  │   │     │
│  │  │          ┌───────────────────────┐                      │   │     │
│  │  │          │   MCP Tool Execution  │                      │   │     │
│  │  │          │   (SQL → TimescaleDB) │                      │   │     │
│  │  │          └───────────┬───────────┘                      │   │     │
│  │  │                      ▼                                  │   │     │
│  │  │          ┌───────────────────────┐                      │   │     │
│  │  │          │ Data Injection into   │                      │   │     │
│  │  │          │ React Component Code  │                      │   │     │
│  │  │          └───────────┬───────────┘                      │   │     │
│  │  │                      ▼                                  │   │     │
│  │  │          ┌───────────────────────┐                      │   │     │
│  │  │          │ <artifact type="react"│                      │   │     │
│  │  │          │   React TSX Chart     │                      │   │     │
│  │  │          │   with embedded data  │                      │   │     │
│  │  │          └───────────────────────┘                      │   │     │
│  │  └──────────────────────────────────────────────────────────┘   │     │
│  │                                                                  │     │
│  │  ┌──────────────────────────────────────────────────────────┐   │     │
│  │  │              MCP Client (mcp_client.py)                  │   │     │
│  │  │  • Connects to backend MCP server (port 8000)            │   │     │
│  │  │  • Executes SQL queries via tools/call RPC               │   │     │
│  │  │  • Parses TSV/JSON responses                             │   │     │
│  │  └──────────────────────────────────────────────────────────┘   │     │
│  │                                                                  │     │
│  │  ┌──────────────────────────────────────────────────────────┐   │     │
│  │  │           Database Models (PostgreSQL)                   │   │     │
│  │  │  • ChatSession - User chat sessions                      │   │     │
│  │  │  • ChatMessage - Message history (30-day retention)      │   │     │
│  │  │  • Dashboard - User dashboards                           │   │     │
│  │  │  • DashboardComponent - Chart/gauge/table configs        │   │     │
│  │  └──────────────────────────────────────────────────────────┘   │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION PIPELINE                                 │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌────────────┐   MQTT    ┌──────────┐  Validate  ┌──────────┐  gRPC     │
│  │  Simulator │──Publish─►│ Node-RED │──Enrich───►│Collector │──Write──► │
│  │  Python    │  Topic:   │ Data     │  Transform │ Go Lang  │   to      │
│  │  35 Devices│  plc/{id} │ Router   │  MQTT →    │ gRPC     │TimescaleDB│
│  │            │           │          │  HTTP      │ Server   │           │
│  └────────────┘           └──────────┘            └──────────┘           │
│                                                                            │
│  MQTT Broker (RabbitMQ)                                          │
│  • Port 1883 (internal), 1884 (external with auth)                        │
│  • Topics: plc/{device_id}, factory/alerts, system/status                 │
│                                                                            │
│  Node-RED Flows:                                                           │
│  • Data validation (range checks, type validation)                        │
│  • Metadata enrichment (location, sensor type, units)                     │
│  • Routing (different endpoints for different device types)               │
│  • Alerting (threshold violations → MQTT alerts topic)                    │
│                                                                            │
│  Collector (Go):                                                           │
│  • Receives data via gRPC (port 9090)                                     │
│  • Batches writes for performance                                         │
│  • Handles UNREAL devices (conveyor1/2/3, placer1)                        │
│  • Handles sensor devices (motor_speed_PLC-NY-001, etc.)                  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICES (Spring Boot)                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Controllers:                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │ DataController (/api/data)                                       │     │
│  │  • GET /latest - Latest sensor readings (Redis cached 5s)        │     │
│  │  • GET /hierarchical-live - Device hierarchy (Redis cached 5s)   │     │
│  │  • GET /device/{id}/history - Time-series data (Redis 60s)       │     │
│  │  • Input validation: deviceId regex, time range max 30 days      │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │ AIController (/api/ai)                                           │     │
│  │  • POST /query - Natural language queries via MCP                │     │
│  │  • GET /suggestions - AI-powered query suggestions               │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │ AdminController (/api/admin)                                     │     │
│  │  • GET /stats - System statistics                                │     │
│  │  • POST /cleanup - Trigger data cleanup                          │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │ MCPController (/api/mcp)                                         │     │
│  │  • POST /query - Direct MCP query endpoint                       │     │
│  │  • GET /tools - List available MCP tools                         │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │ FactoryController (/api/factories)                               │     │
│  │  • GET /devices - All factory devices                            │     │
│  │  • GET /metrics - Factory-wide metrics                           │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                            │
│  Services:                                                                 │
│  • PlcDataRepository - TimescaleDB queries with @Cacheable annotations    │
│  • CacheConfig - Redis cache manager (5s-5min TTLs)                       │
│  • SecurityConfig - CORS, HSTS, CSP, frame options                        │
│  • WebSocketHandler - Real-time data streaming                            │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + TypeScript)                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Pages:                                                                    │
│  • Dashboard - Real-time factory overview with device cards               │
│  • History - Time-series charts with device selector                      │
│  • AI Chat - Natural language queries with artifact rendering             │
│  • Admin - System statistics and management                               │
│                                                                            │
│  Components:                                                               │
│  • DeviceCard - Real-time sensor values with status indicators            │
│  • HistoryChart - Recharts line/area charts with zoom/pan                 │
│  • ChatInterface - SSE streaming chat with artifact preview               │
│  • ArtifactRenderer - Dynamic React component rendering from AI           │
│                                                                            │
│  Libraries:                                                                │
│  • Vite - Build tool and dev server                                       │
│  • React Router - Client-side routing                                     │
│  • Recharts - Chart visualization                                         │
│  • Tailwind CSS - Utility-first styling                                   │
│  • Shadcn/ui - Component library                                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagrams

### 1️⃣ Real-time Data Collection Flow
```
┌─────────────┐
│  Simulator  │ Generates sensor data (35 devices)
│  (Python)   │ motor_speed, temp, pressure, etc.
└──────┬──────┘
       │ MQTT Publish
       │ Topic: plc/{device_id}
       │ Payload: {"value": 1500, "timestamp": ...}
       ▼
┌──────────────┐
│ MQTT Broker  │ Eclipse Mosquitto with auth
│ (Mosquitto)  │ Port 1883 (internal)
└──────┬───────┘
       │ Subscribe
       ▼
┌──────────────┐
│  Node-RED    │ Data validation & enrichment
│ (Flow Engine)│ • Validate ranges
│              │ • Add metadata (location, type)
│              │ • Transform formats
└──────┬───────┘
       │ HTTP POST or MQTT forward
       ▼
┌──────────────┐
│  Collector   │ gRPC server (port 9090)
│    (Go)      │ Batch writes for performance
└──────┬───────┘
       │ INSERT INTO plc_data
       ▼
┌──────────────┐
│ TimescaleDB  │ Hypertable: plc_data
│ (PostgreSQL) │ Automatic partitioning by time
│              │ Compression after 7 days
└──────────────┘
```

### 2️⃣ AI Query Processing Flow (Ollama)
```
User: "Show conveyor1 RPM for last hour"
   │
   ▼
┌─────────────────────────────────────────────────────────┐
│ Frontend - AI Chat Page                                 │
│ POST /api/ai/chat/stream                                │
│ Body: {"message": "...", "model": "ollama"}             │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP POST
                       ▼
┌─────────────────────────────────────────────────────────┐
│ AI Service - Chat Router                                │
│ Step 1: Analyze query intent                            │
└──────────────────────┬──────────────────────────────────┘
                       │ Generate tool call
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Ollama Model (qwen2:0.5b)                               │
│ Input: System prompt + User query                       │
│ Output: [TOOL: query_timescale {"query": "SELECT..."}] │
└──────────────────────┬──────────────────────────────────┘
                       │ Extract tool call
                       ▼
┌─────────────────────────────────────────────────────────┐
│ AI Service - Tool Executor                              │
│ Parse: tool_name="query_timescale"                      │
│        args={"query": "SELECT time_bucket(...)"}        │
└──────────────────────┬──────────────────────────────────┘
                       │ Execute via MCP
                       ▼
┌─────────────────────────────────────────────────────────┐
│ MCP Client (ai-service)                                 │
│ POST http://backend:8000/jsonrpc                        │
│ Method: tools/call                                      │
└──────────────────────┬──────────────────────────────────┘
                       │ RPC call
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Backend MCP Server (db-mcp-server)                      │
│ Tool: query_timescale                                   │
│ Execute: SELECT time_bucket('5 minutes', timestamp),    │
│          AVG(rpm) FROM plc_data WHERE...                │
└──────────────────────┬──────────────────────────────────┘
                       │ Query TimescaleDB
                       ▼
┌─────────────────────────────────────────────────────────┐
│ TimescaleDB                                             │
│ Returns: 12 rows (5-min buckets for 1 hour)            │
│ Format: [{"period": "...", "avg_rpm": 1500}, ...]      │
└──────────────────────┬──────────────────────────────────┘
                       │ Return data
                       ▼
┌─────────────────────────────────────────────────────────┐
│ AI Service - Parse MCP Response                         │
│ Extract: 12 rows of time-series data                    │
└──────────────────────┬──────────────────────────────────┘
                       │ Send to Ollama with data
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Ollama Model (qwen2:0.5b) - Second Call                 │
│ Input: "Generate React chart with this data: [...]"     │
│ Output:                                                  │
│ <artifact type="react" title="Conveyor1 RPM">           │
│ ```tsx                                                   │
│ import { LineChart, Line, ... } from 'recharts';        │
│ const data = [                                           │
│   {"period": "10:00", "avg_rpm": 1500},                 │
│   {"period": "10:05", "avg_rpm": 1520}, ...             │
│ ];                                                       │
│ return <LineChart data={data}>...</LineChart>           │
│ ```                                                      │
│ </artifact>                                              │
└──────────────────────┬──────────────────────────────────┘
                       │ Stream response
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Frontend - Artifact Renderer                            │
│ 1. Parse artifact tags                                  │
│ 2. Extract React component code                         │
│ 3. Render in iframe sandbox                             │
│ 4. Display chart to user                                │
└─────────────────────────────────────────────────────────┘
```

### 3️⃣ API Request with Redis Caching
```
Browser: GET /api/data/hierarchical-live
   │
   ▼
┌──────────────┐
│    Nginx     │ Reverse proxy + rate limiting
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Backend    │ Spring Boot controller
│ DataController
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ @Cacheable   │ Check Redis for cached result
│  Annotation  │ Key: "hierarchical::live-data"
└──────┬───────┘
       │
       ├─── Cache HIT (17x faster) ──► Return cached JSON
       │
       └─── Cache MISS ──┬─► Query TimescaleDB
                          │
                          ▼
                   ┌──────────────┐
                   │ TimescaleDB  │ Execute SQL
                   │ Query 10,000 │ SELECT device_id, type, rpm, 
                   │   rows       │ position_x, data->>'value'...
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │Process Results│ Group by device
                   │Build Hierarchy│ Build JSON tree
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ Store in     │ SET hierarchical::live-data
                   │ Redis Cache  │ EX 5 (5 second TTL)
                   └──────┬───────┘
                          │
                          ▼
                   Return JSON to client
```

---

## 🔐 Security Architecture

### Network Security
- **Nginx Rate Limiting**: 10 req/s (API), 5 req/s (data), 100 req/s (static)
- **Slowloris Protection**: 12s body timeout, 12s header timeout, 1K buffer limits
- **CORS Restrictions**: `http://localhost:[*]`, `http://127.0.0.1:[*]`, `http://192.168.*.*:[*]`
- **HTTP Method Filtering**: Only GET, POST, PUT, DELETE, OPTIONS, PATCH

### Application Security
- **Input Validation**: Device ID regex `^[a-zA-Z0-9_-]+$`, max 100 chars
- **SQL Injection Prevention**: Parameterized queries, input sanitization
- **Time Range Limits**: Max 30 days per history query
- **File Access Protection**: Block `.env`, `.git`, `.sql`, `.log`, `.conf`, hidden files

### Headers (Nginx + Spring Security)
- **HSTS**: `max-age=31536000; includeSubDomains`
- **CSP**: `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'...`
- **X-Frame-Options**: `SAMEORIGIN`
- **X-Content-Type-Options**: `nosniff`
- **Permissions-Policy**: `geolocation=(), microphone=(), camera=()`

### Authentication (Future Enhancement)
- **JWT Tokens**: Configurable secret via `JWT_SECRET`
- **Session Management**: Redis-based with expiration
- **Multi-Tenant Isolation**: Kubernetes network policies

---

## 🗄️ Database Schemas

### TimescaleDB (plc_data table)
```sql
CREATE TABLE plc_data (
    timestamp TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'sensor' or 'UNREAL'
    rpm FLOAT,           -- For UNREAL devices (conveyor1/2/3, placer1)
    position_x FLOAT,    -- For UNREAL devices
    position_y FLOAT,    -- For UNREAL devices
    data JSONB,          -- For sensor devices (signal_config->>'value')
    metadata JSONB
);

-- Hypertable with automatic partitioning
SELECT create_hypertable('plc_data', 'timestamp');

-- Compression policy (after 7 days)
SELECT add_compression_policy('plc_data', INTERVAL '7 days');
```

**Two Data Patterns**:
1. **UNREAL Devices** (conveyor1, conveyor2, placer1)
   - `type = 'UNREAL'`
   - RPM in `rpm` column
   - Position in `position_x`, `position_y`

2. **Simulator Sensors** (motor_speed_PLC-NY-001, etc.)
   - `type = 'sensor'`
   - Value in `(data->'signal_config'->>'value')::float`
   - Sensor name in `data->'signal_config'->>'name'`

### PostgreSQL (AI Service)
```sql
-- Chat sessions
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Chat messages (30-day retention)
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES chat_sessions(id),
    role VARCHAR(20), -- 'user' or 'assistant'
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User dashboards
CREATE TABLE dashboards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(255),
    description TEXT,
    layout JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dashboard components
CREATE TABLE dashboard_components (
    id SERIAL PRIMARY KEY,
    dashboard_id INTEGER REFERENCES dashboards(id),
    component_type VARCHAR(50), -- 'chart', 'gauge', 'table', 'alert'
    config JSONB, -- React component props, chart config
    position_x INTEGER,
    position_y INTEGER,
    ai_generated BOOLEAN DEFAULT FALSE
);
```

### Redis Cache Keys
```
devices::all-devices             TTL: 5s
devices::sensors                 TTL: 5s
devices::unreal                  TTL: 5s
hierarchical::live-data          TTL: 5s
history::{deviceId}-{start}-{end} TTL: 60s
metadata::device-definitions     TTL: 5min
```

---

## 🚀 Deployment Options

### 1. Docker Compose (Development/Single-Tenant)
```bash
./deploy.sh dev   # Hot reload, debugging enabled
./deploy.sh prod  # Production optimized, single tenant
```

### 2. Kubernetes (Multi-Tenant SaaS)
```bash
./setup-k8s.sh    # Automated setup with 2 demo tenants

# Manual tenant provisioning
cd kubernetes
./provision-tenant.sh acme123 "ACME Corp" acme.virtplc.com
```

**Multi-Tenant Architecture**:
- **Shared Infrastructure**: postgres, redis, ollama, mqtt (virtplc-system namespace)
- **Isolated Tenants**: Separate namespace per company (virtplc-tenant-acme123)
- **Network Policies**: Cross-tenant traffic blocked
- **Database Schemas**: tenant_acme123, tenant_techcorp456
- **Custom Domains**: acme.virtplc.com, techcorp.virtplc.com

---

## 📈 Performance Metrics

### Redis Cache Performance
- **Cache Hit**: 0.010s - 0.064s (17x faster)
- **Cache Miss**: 0.170s - 0.349s (full database query)
- **TTL Strategy**: 5s (devices), 60s (history), 5min (metadata)

### Database Compression
- **Raw Data**: ~1.2GB per month (35 devices, 1s interval)
- **Compressed**: ~300MB after 7 days (4x reduction)
- **Retention**: 2 months, cleanup removes oldest 25%

### API Rate Limits (Nginx)
- **API Endpoints**: 10 requests/second
- **Data Endpoints**: 5 requests/second
- **Static Assets**: 100 requests/second
- **Concurrent Connections**: 10 per IP

---

## 🔄 Data Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ Data Ingestion (Real-time)                             │
│ • Simulator generates data every 1 second              │
│ • 35 devices × 1 update/sec = 35 inserts/sec           │
│ • ~3 million rows per day                              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ TimescaleDB Storage (Days 0-7)                          │
│ • Uncompressed chunks                                   │
│ • Fast writes and queries                               │
│ • Full resolution data                                  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ (After 7 days)
┌─────────────────────────────────────────────────────────┐
│ Compression (Days 7-60)                                 │
│ • Automatic compression policy                          │
│ • ~4x storage reduction                                 │
│ • Slower queries (still acceptable)                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ (After 60 days)
┌─────────────────────────────────────────────────────────┐
│ Cleanup (Every 2 months)                                │
│ • Cron job: scripts/timescale_cleanup.sh                │
│ • Deletes oldest 25% of data                            │
│ • Keeps last ~45 days of history                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack Summary

| Layer           | Technology              | Purpose                          |
|-----------------|-------------------------|----------------------------------|
| **Frontend**    | React 18 + TypeScript   | Interactive UI                   |
|                 | Vite                    | Build tool & dev server          |
|                 | Recharts                | Chart visualization              |
|                 | Tailwind CSS            | Styling                          |
|                 | Shadcn/ui               | Component library                |
| **Backend**     | Spring Boot 3.2         | REST API & business logic        |
|                 | Java 21                 | Programming language             |
|                 | Spring Data JPA         | ORM for PostgreSQL               |
|                 | Spring Data Redis       | Caching layer                    |
|                 | Spring Security         | Authentication & CORS            |
| **AI Service**  | FastAPI                 | Python web framework             |
|                 | Ollama                  | Local LLM (qwen2:0.5b)           |
|                 | Claude API (optional)   | Cloud LLM (claude-3-opus)        |
|                 | MCP Client              | Database tool calling            |
| **Data Store**  | TimescaleDB             | Time-series data                 |
|                 | PostgreSQL              | Relational data                  |
|                 | Redis                   | Cache & sessions                 |
| **Messaging**   | MQTT (Mosquitto)        | Device communication             |
|                 | Node-RED                | Data enrichment & routing        |
| **Collector**   | Go + gRPC               | High-performance data ingestion  |
| **Proxy**       | Nginx (Alpine)          | Reverse proxy & rate limiting    |
| **Simulator**   | Python 3.11             | PLC/factory simulator            |

---

## 🎯 Key Features Summary

### ✅ Implemented
- Real-time PLC data collection (MQTT → Node-RED → Collector → TimescaleDB)
- Redis caching (5s-60s TTLs, 17x performance improvement)
- AI-powered natural language queries with Ollama
- React chart generation from SQL data
- MCP-based database access for AI models
- Multi-model support (Ollama + Claude)
- Security hardening (HSTS, CSP, input validation, rate limiting)
- Data compression (4x reduction after 7 days)
- Kubernetes multi-tenant architecture

### 🔧 Claude Integration Status
- ✅ **Configured**: `claude_client.py` ready
- ✅ **Routing**: Chat endpoint supports `model="claude"`
- ✅ **Streaming**: SSE streaming implemented
- ⏳ **Pending**: API key (`CLAUDE_API_KEY`)
- ⚠️ **Limitation**: Cannot execute code (text generation only)

### 🚀 Recommended Next Steps for Claude
1. **Get API key**: https://console.anthropic.com/
2. **Set environment variable**:
   ```bash
   export CLAUDE_API_KEY=sk-ant-api03-xxxxx
   ```
3. **Restart ai-service**:
   ```bash
   docker-compose restart ai-service
   ```
4. **Test with frontend**:
   - Select "Claude" model in chat dropdown
   - Query: "Show conveyor1 RPM for last hour"
   - Expect higher-quality React components

### 💡 Claude vs Ollama Comparison

| Feature              | Ollama (qwen2:0.5b) | Claude (claude-3-opus) |
|----------------------|---------------------|------------------------|
| **Cost**             | Free (local)        | Pay-per-token          |
| **Speed**            | Fast (local GPU)    | Depends on API         |
| **Code Quality**     | Good                | Excellent              |
| **Context Window**   | 2K tokens           | 200K tokens            |
| **Chart Variety**    | Line, bar, area     | All chart types        |
| **Error Handling**   | Basic               | Advanced               |
| **Code Execution**   | No                  | No (same limitation)   |
| **Privacy**          | Full (local)        | Cloud (Anthropic)      |

**Recommendation**: Use **Ollama** for development/testing (free, fast), use **Claude** for production (higher quality) when you have the API key.

---

## 📞 Contact & Support

For deployment questions, see:
- **[SECURITY.md](../SECURITY.md)** - Security audit results
- **[kubernetes/README.md](../kubernetes/README.md)** - Multi-tenant setup
- **[ai-service/README.md](../ai-service/README.md)** - AI service details

---

**Last Updated**: January 8, 2026  
**Architecture Version**: 3.0 (Redis + Security + Claude Support)
