# VirtPLC AI Service

**Technology Stack:** Python 3.11 + FastAPI + Ollama + MCP + TimeBase
---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               AI Service (Python + FastAPI)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐    ┌─────────────┐   │
│  │   FastAPI    │     │     MCP      │    │   Ollama    │   │
│  │  REST API    │────►│    Client    │───►│   Llama3    │   │
│  │  Port: 3001  │     │  (Backend)   │    │  Port:11434 │   │
│  └──────────────┘     └──────────────┘    └─────────────┘   │
│         │                                                   │
│         │                                                   │
│  ┌──────▼──────┐     ┌──────────────┐    ┌─────────────┐    │
│  │  WebSocket  │     │   TimeBase   │    │  PostgreSQL │    │
│  │  Port: 3002 │     │  Time Series │    │  Relational │    │
│  └─────────────┘     │  Port: 8011  │    │  Port: 5432 │    │
│                      └──────────────┘    └─────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   Redis Cache                       │    │
│  │         Sessions & Caching (Port: 6379)             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Architecture

### **TimeBase (Time Series)**
- Factory sensor metrics (temperature, vibration, speed, pressure)
- Equipment state history
- AI predictions and anomalies
- Aggregated metrics (1min, 5min, 1hour)

### **PostgreSQL (Relational)**
- User accounts and roles
- Chat sessions and messages (30-day retention)
- User dashboards and components
- Metric definitions catalog
- AI analysis logs

### **Redis (Caching)**
- Session management
- Real-time data caching
- WebSocket connection tracking

---

## Quick Start

### Prerequisites

```bash
# Required services
docker-compose up -d postgres redis timebase ollama

# Pull Ollama model
docker exec -it virtplc-ollama ollama pull llama3:8b
```

### Installation

```bash
cd ai-service

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Run Development Server

```bash
# Start FastAPI with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 3001
```

Service starts on:
- **REST API**: http://localhost:3001
- **API Docs**: http://localhost:3001/docs (Swagger UI)
- **WebSocket**: ws://localhost:3002
- **Metrics**: http://localhost:9090/metrics (Prometheus)

---

## Testing Endpoints

### Health Check

```bash
curl http://localhost:3001/health
```

### Test Endpoint (Comprehensive Service Status)

```bash
curl http://localhost:3001/test
```

**Returns:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-21T10:30:00Z",
  "mcp": {
    "enabled": true,
    "tools_available": 5,
    "tools": ["get_sensor_data", "get_equipment_status", "trigger_alert"]
  },
  "timebase": {
    "connected": true,
    "sample_data_points": 60
  },
  "ollama": {
    "host": "http://ollama:11434",
    "model": "llama3:8b"
  },
  "sample_data": [...]
}
```

### AI Analysis

```bash
# Analyze current factory status
curl -X POST http://localhost:3001/api/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["Motor1", "Motor2"]}'

# Get maintenance predictions
curl http://localhost:3001/api/analysis/predict-maintenance

# Detect anomalies
curl http://localhost:3001/api/analysis/anomalies
```

### Chat with AI

```bash
# Start chat session
curl -X POST http://localhost:3001/api/chat/session \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'

# Send message
curl -X POST http://localhost:3001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "message": "What is the current status of Motor1?"
  }'
```

### Dashboard Management

```bash
# Create custom dashboard
curl -X POST http://localhost:3001/api/dashboard/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "dashboard_name": "My Factory View",
    "components": [
      {
        "type": "line_chart",
        "name": "Motor Temperature",
        "config": {
          "metrics": ["motor1_temperature", "motor2_temperature"],
          "timeRange": "1h"
        }
      }
    ]
  }'
```

---

## MCP Integration

### What is MCP?

**Model Context Protocol** enables structured communication between AI models and data sources.

### MCP Flow

```
FastAPI AI Service
      ↓
   MCP Client
      ↓ (HTTP/WebSocket)
Spring Backend (MCP Server)
      ↓
OPC-UA / TimeBase / PostgreSQL
```

### Available MCP Tools

| Tool Name | Description | Example |
|-----------|-------------|---------|
| `get_sensor_data` | Get current sensor readings | Motor temps, vibrations |
| `get_equipment_status` | Equipment operational state | running, stopped, error |
| `get_historical_data` | Query time series data | Last 24h temperature |
| `trigger_alert` | Create maintenance alert | Predict failure in 48h |
| `get_context_for_llm` | Format context for AI | Full factory status |

### Usage Example

```python
from src.services.mcp_client import mcp_client

# Get sensor data via MCP
data = await mcp_client.get_sensor_data(
    symbols=["Motor1", "Motor2"],
    metrics=["temperature", "vibration"]
)

# Get formatted context for LLM
context = await mcp_client.get_context_for_llm(
    symbols=["Motor1"],
    include_historical=True,
    time_range_hours=24
)

# Use context in Ollama prompt
response = await ollama.generate(
    model="llama3:8b",
    prompt=f"Factory Context:\n{context}\n\nAnalyze this data:"
)
```

---

## Database Schemas

### TimeBase Streams

- **`factory_metrics`** - Real-time sensor data
- **`ai_predictions`** - ML predictions and anomalies
- **`aggregated_metrics`** - Pre-computed aggregations
- **`user_interactions`** - Dashboard usage tracking

### PostgreSQL Tables

- **`users`** - User accounts
- **`chat_sessions`** - Chat session metadata
- **`chat_messages`** - Message history (30-day retention)
- **`user_dashboards`** - Custom dashboard configs
- **`dashboard_components`** - React components (AI-generated)
- **`ai_analysis_logs`** - Analysis audit log
- **`metric_definitions`** - Available metrics catalog

---

## AI Features

### 1. **Predictive Maintenance**
- Analyzes sensor trends
- Predicts equipment failures
- Recommends maintenance windows
- Uses Llama3 + rule-based algorithms

### 2. **Anomaly Detection**
- Real-time deviation detection
- Statistical thresholds
- Pattern recognition
- Severity classification

### 3. **Conversational AI**
- Natural language queries
- Factory status summaries
- Historical trend analysis
- Maintenance recommendations

### 4. **AI-Generated Dashboards**
- Users prompt: "Show me motor temperatures"
- AI generates React component config
- Saves to `dashboard_components` table
- Frontend renders dynamically

---

## Docker Deployment

### Build and Run

```bash
# Build AI service
docker-compose build ai-service

# Start all services
docker-compose up -d

# Pull Ollama model
docker exec -it virtplc-ollama ollama pull llama3:8b

# Check logs
docker logs -f virtplc-ai
```

### Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `MCP_ENABLED=true` - Enable MCP integration
- `MCP_SERVER_URL=http://backend:8000` - Backend MCP endpoint
- `OLLAMA_MODEL=llama3:8b` - LLM model to use
- `CHAT_HISTORY_RETENTION_DAYS=30` - Message retention

---

## Monitoring

### Prometheus Metrics

```bash
# Scrape metrics
curl http://localhost:9090/metrics
```

Metrics include:
- Request counts and latencies
- AI analysis execution times
- Ollama token usage
- Database query performance
- WebSocket connections

---

## 🔧 Development

### Project Structure

```
ai-service/
├── src/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings
│   ├── database/
│   │   ├── __init__.py        # DB connection
│   │   ├── models.py          # SQLAlchemy models
│   │   └── timebase_schema.py # TimeBase schemas
│   ├── routes/
│   │   ├── analysis.py        # Analysis endpoints
│   │   ├── chat.py            # Chat endpoints
│   │   └── dashboard.py       # Dashboard endpoints
│   └── services/
│       ├── mcp_client.py      # MCP integration
│       ├── timebase_client.py # TimeBase client
│       └── ollama_service.py  # Ollama integration
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

### Adding New Features

1. **New API Endpoint**: Add to `src/routes/`
2. **New Database Table**: Update `src/database/models.py`
3. **New MCP Tool**: Extend `src/services/mcp_client.py`
4. **New TimeBase Stream**: Update `src/database/timebase_schema.py`

---

## Troubleshooting

### Ollama Connection Fails

```bash
# Check Ollama is running
docker ps | grep ollama

# Test Ollama directly
curl http://localhost:11434/api/tags
```

### MCP Connection Fails

```bash
# Check backend MCP endpoint
curl http://localhost:8000/mcp/tools

# Verify MCP_ENABLED=true in .env
```

### TimeBase Connection Fails

```bash
# Check TimeBase is running
docker logs virtplc-timebase

# Verify credentials in .env
```

### PostgreSQL Connection Fails

```bash
# Check PostgreSQL is healthy
docker exec -it virtplc-postgres pg_isready -U virtplc

# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d postgres
```

---

## dditional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Ollama**: https://ollama.ai
- **TimeBase**: https://timebase.info
- **MCP Spec**: https://modelcontextprotocol.io
- **LangChain**: https://python.langchain.com

---

## Sprint 1 Tasks (for Nándi)

### Setup Checklist

- [ ] Ollama running with Llama3 8B model
- [ ] PostgreSQL initialized with schema
- [ ] Redis cache running
- [ ] TimeBase connected (or mock mode)
- [ ] MCP client initialized (or disabled for testing)
- [ ] `/health` endpoint returns 200
- [ ] `/test` endpoint shows service status

### Testing Tasks

```bash
# 1. Health check
curl http://localhost:3001/health

# 2. Comprehensive test
curl http://localhost:3001/test

# 3. Test Ollama directly
curl http://localhost:11434/api/tags

# 4. Test AI analysis (mock data)
curl -X POST http://localhost:3001/api/analysis/analyze
```

---