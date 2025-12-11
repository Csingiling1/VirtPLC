# Temperature Data Queries for AI Assistant

## Correct SQL Queries for Temperature Data

### 1. Last 24 Hours (Recommended)
```sql
SELECT 
    timestamp, 
    device_id, 
    (data->>'temperature')::float AS temperature
FROM plc_data
WHERE type = 'temperature'
    AND timestamp >= NOW() - INTERVAL '24 hours'
    AND (data->>'temperature') IS NOT NULL
ORDER BY timestamp ASC
LIMIT 5000;
```

### 2. Last 1 Hour
```sql
SELECT 
    timestamp, 
    device_id, 
    (data->>'temperature')::float AS temperature
FROM plc_data
WHERE type = 'temperature'
    AND timestamp >= NOW() - INTERVAL '1 hour'
    AND (data->>'temperature') IS NOT NULL
ORDER BY timestamp ASC
LIMIT 5000;
```

### 3. Last 7 Days (with sampling to avoid too many points)
```sql
SELECT 
    time_bucket('5 minutes', timestamp) AS timestamp,
    device_id,
    AVG((data->>'temperature')::float) AS temperature
FROM plc_data
WHERE type = 'temperature'
    AND timestamp >= NOW() - INTERVAL '7 days'
    AND (data->>'temperature') IS NOT NULL
GROUP BY time_bucket('5 minutes', timestamp), device_id
ORDER BY timestamp ASC
LIMIT 5000;
```

### 4. All Devices Summary (Current Values)
```sql
SELECT DISTINCT ON (device_id)
    timestamp,
    device_id,
    (data->>'temperature')::float AS temperature
FROM plc_data
WHERE type = 'temperature'
    AND (data->>'temperature') IS NOT NULL
ORDER BY device_id, timestamp DESC;
```

## Common Issues and Fixes

### Issue 1: Getting Only Recent Data (Last 1 Minute)
**Problem**: Query doesn't specify time range properly
**Fix**: Always use `WHERE timestamp >= NOW() - INTERVAL '24 hours'`

### Issue 2: No Data Returned
**Problem**: Wrong data type filter or missing data
**Fix**: 
- Ensure `WHERE type = 'temperature'` is correct
- Add `AND (data->>'temperature') IS NOT NULL` to filter null values
- Check actual data types in database: `SELECT DISTINCT type FROM plc_data;`

### Issue 3: Disconnected Points in Chart
**Problem**: Missing `type="monotone"` in Recharts Line component
**Fix**: Add `type="monotone"` to each `<Line>` component

## MCP Server Options

### Current: FreePeak db-mcp-server (docker.io/freepeak/db-mcp-server:latest)
**Pros:**
- Simple JSON-RPC interface
- Direct PostgreSQL/TimescaleDB support
- Lightweight

**Cons:**
- Limited query optimization
- Basic error handling
- No query caching

### Alternative 1: Modelcontextprotocol/server-postgres
**Installation:**
```bash
npm install -g @modelcontextprotocol/server-postgres
```

**Docker Compose:**
```yaml
mcp-postgres:
  image: node:18-alpine
  command: npx -y @modelcontextprotocol/server-postgres postgresql://virtplc:changeme@timescale:5432/virtplc_ts
  ports:
    - "9093:9093"
  environment:
    - MCP_PORT=9093
  depends_on:
    - timescale
```

### Alternative 2: Custom FastAPI MCP Server (Recommended for Advanced Use)
Create a custom MCP server with:
- Query result caching (Redis)
- NLP-based query generation using spaCy/transformers
- Query optimization and validation
- Better error messages
- TimescaleDB-specific functions (time_bucket, etc.)

**Example:**
```python
# ai-service/mcp_server.py
from fastapi import FastAPI
from typing import Dict, Any
import spacy
from transformers import pipeline

app = FastAPI()
nlp = spacy.load("en_core_web_sm")
qa_pipeline = pipeline("question-answering")

@app.post("/query/nl")
async def natural_language_query(question: str) -> Dict[str, Any]:
    # Parse question with NLP
    doc = nlp(question)
    
    # Extract time range, metrics, devices
    time_range = extract_time_range(doc)
    metric = extract_metric(doc)  # temperature, pressure, etc.
    
    # Generate SQL
    sql = f"""
    SELECT timestamp, device_id, 
           (data->>'{metric}')::float AS {metric}
    FROM plc_data
    WHERE type = '{metric}'
      AND timestamp >= NOW() - INTERVAL '{time_range}'
    ORDER BY timestamp ASC
    LIMIT 5000
    """
    
    # Execute and return
    return await execute_query(sql)
```

## Verification Queries

### Check Available Data
```sql
-- See what types of data exist
SELECT DISTINCT type, COUNT(*) as count
FROM plc_data
GROUP BY type;

-- Check time range of data
SELECT 
    MIN(timestamp) as oldest,
    MAX(timestamp) as newest,
    MAX(timestamp) - MIN(timestamp) as duration
FROM plc_data
WHERE type = 'temperature';

-- List all devices with temperature data
SELECT DISTINCT device_id, COUNT(*) as readings
FROM plc_data
WHERE type = 'temperature'
GROUP BY device_id
ORDER BY readings DESC;
```

## Recommended Next Steps

1. **Test queries directly** in TimescaleDB to verify data exists:
   ```bash
   docker exec -it virtplc-timescale psql -U virtplc -d virtplc_ts
   ```

2. **Check MCP server logs** for query errors:
   ```bash
   docker logs virtplc-db-mcp-server
   ```

3. **Upgrade to better MCP server** if needed (see alternatives above)

4. **Add query caching** to reduce database load

5. **Implement NLP query parsing** for natural language questions
