# AI Service & Frontend Fixes

## Issues Fixed

### 1. Chart Data Loading Error (500 Status Code)
**Problem**: Frontend received "Request failed with status code 500" when loading charts

**Root Cause**: 
- `dashboard.py` was importing `timebase_service` which didn't have `get_historical_data()` method
- Routes were calling non-existent MCP client methods

**Fix Applied**:
- Changed `dashboard.py` to import `timescale_service` instead of `timebase_service`
- Updated `/api/dashboard/metrics` to use `timescale_service.get_latest_data()`
- Updated `/api/dashboard/chart-data` to use `timescale_service.get_device_data()`
- Created `TimescaleService` wrapper class with async methods:
  - `get_latest_data(limit)` - Get latest data points
  - `get_device_data(device_id, start_time, end_time)` - Get device time series
  - `get_historical_data_for_range(start_time, end_time, limit)` - Get historical data
- Updated `analysis.py` routes to use TimescaleDB instead of MCP client

### 2. Node-RED Authentication
**Problem**: Default admin/admin credentials didn't work

**Fix Applied**:
- Disabled authentication in `/nodered/settings.js` for development
- Commented out `adminAuth` section
- Restarted Node-RED container
- Access now available at `http://localhost:1880` without login

### 3. Empty Data Returns
**Status**: Working as expected - endpoints return empty arrays when no data exists
- `/api/analysis/historical` - ✅ Working (returns {"data": [], "count": 0})
- `/api/dashboard/chart-data` - ✅ Working (returns {"data": [], "device_id": "..."})

## Claude Artifacts Style Code Generation

The AI service already supports Claude Artifacts! Here's how it works:

### Backend (AI Service)
**File**: `/ai-service/src/routes/chat.py`

**Features**:
1. **Tool Use Syntax**: 
   ```
   [TOOL: tool_name {"arg_name": "arg_value"}]
   ```

2. **Artifact Generation**:
   ```xml
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
   ```

3. **Available Tools**:
   - `execute_query(query)` - Run SQL on TimescaleDB
   - `get_latest_readings(device_id, limit)` - Get latest sensor data
   - `get_device_stats(device_id, hours)` - Get device statistics
   - `get_factory_summary(factory_id)` - Get factory overview
   - `search_devices(search_term)` - Search devices

### Frontend Integration
**File**: `/frontend/src/components/ArtifactRenderer.tsx`

The frontend needs to:
1. Parse `<artifact>` tags from AI responses
2. Render appropriate UI components based on artifact type
3. Execute SQL queries for chart data
4. Display charts using Recharts library

**Current Status**: Backend ready, frontend artifact renderer needs verification

## Testing Endpoints

### Health Check
```bash
curl http://localhost:3001/health
```

### Chart Data
```bash
curl "http://localhost:3001/api/dashboard/chart-data?device_id=conveyor1&hours=24"
```

### Historical Data
```bash
curl "http://localhost:3001/api/analysis/historical?start_time=2025-12-11T00:00:00Z&end_time=2025-12-11T01:00:00Z&limit=100"
```

### Chat with Artifacts
```bash
curl -X POST http://localhost:3001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me a chart of conveyor RPM over the last hour",
    "stream": false
  }'
```

## Next Steps

1. **Populate Test Data**: Add sample data to TimescaleDB via Collector
2. **Test Node-RED Flow**: Publish test MQTT messages to populate database
3. **Verify Artifact Rendering**: Test frontend artifact renderer with AI-generated charts
4. **Add Authentication**: Re-enable Node-RED auth with proper credentials
5. **Code Execution Sandbox**: Implement safe code execution for "Run Code" feature

## Data Flow for Chart Generation

```
User Request
   ↓
Frontend (AIAssistant.tsx)
   ↓
POST /api/chat/message
   ↓
AI Service (chat.py)
   ↓
Ollama LLM generates <artifact>
   ↓
Frontend parses artifact
   ↓
ArtifactRenderer.tsx
   ↓
Execute SQL query → TimescaleDB
   ↓
Render Chart (Recharts)
```

## Files Modified

1. `/ai-service/src/routes/dashboard.py` - Changed to use TimescaleDB
2. `/ai-service/src/routes/analysis.py` - Changed to use TimescaleDB  
3. `/ai-service/src/services/timescale_client.py` - Added TimescaleService class
4. `/nodered/settings.js` - Disabled authentication
5. `/docker-compose.yml` - Updated Node-RED and Collector services

## Service Status

- ✅ AI Service (virtplc-ai) - Running on port 3001
- ✅ Frontend (virtplc-frontend) - Running on port 3000
- ✅ Node-RED (virtplc-nodered) - Running on port 1880 (no auth)
- ✅ MQTT Broker (virtplc-mqtt) - Running on port 1883
- ✅ Collector (virtplc-collector) - Running, subscribed to `collector/ingest`
- ✅ TimescaleDB (virtplc-timescale) - Running on port 15433
