# VirtPLC API Documentation

Comprehensive API reference for VirtPLC services.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Backend REST API](#backend-rest-api)
- [AI Service API](#ai-service-api)
- [WebSocket API](#websocket-api)
- [MQTT Topics](#mqtt-topics)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

## Overview

VirtPLC exposes multiple APIs for different functionalities:

- **Backend API** (Port 8080): Device management, data access, user management
- **AI Service API** (Port 3001): Natural language queries, analytics, chat
- **WebSocket API**: Real-time data streaming
- **MQTT**: Device telemetry and commands

### Base URLs

```
Development:
- Backend: http://localhost:8080/api
- AI Service: http://localhost:3001
- WebSocket: ws://localhost:8080/ws

Production:
- Backend: https://api.virtplc.com/api
- AI Service: https://ai.virtplc.com
- WebSocket: wss://api.virtplc.com/ws
```

## Authentication

### JWT Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "user": {
    "id": "123",
    "username": "user@example.com",
    "role": "admin"
  }
}
```

### Token Refresh

```http
POST /api/auth/refresh
Authorization: Bearer <refresh-token>
```

## Backend REST API

### Devices

#### Get All Devices

```http
GET /api/devices
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "deviceId": "PLC-001",
    "name": "Production Line 1",
    "type": "plc",
    "status": "active",
    "manufacturer": "Siemens",
    "model": "S7-1200",
    "ipAddress": "192.168.1.10",
    "location": "Factory Floor 1",
    "lastSeen": "2024-01-20T10:30:00Z",
    "tags": ["production", "line-1"]
  }
]
```

#### Get Device by ID

```http
GET /api/devices/{id}
Authorization: Bearer <token>
```

**Parameters:**
- `id` (path): Device ID (integer)

**Response:**
```json
{
  "id": 1,
  "deviceId": "PLC-001",
  "name": "Production Line 1",
  "type": "plc",
  "status": "active",
  "metadata": {
    "firmwareVersion": "2.1.0",
    "installDate": "2023-06-15"
  }
}
```

#### Create Device

```http
POST /api/devices
Authorization: Bearer <token>
Content-Type: application/json

{
  "deviceId": "PLC-002",
  "name": "Assembly Line",
  "type": "plc",
  "manufacturer": "Siemens",
  "ipAddress": "192.168.1.20"
}
```

**Response:** 201 Created
```json
{
  "id": 2,
  "deviceId": "PLC-002",
  "name": "Assembly Line",
  "status": "inactive",
  "createdAt": "2024-01-20T11:00:00Z"
}
```

#### Update Device

```http
PUT /api/devices/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "status": "maintenance"
}
```

#### Delete Device

```http
DELETE /api/devices/{id}
Authorization: Bearer <token>
```

**Response:** 204 No Content

### Device Data

#### Get Time-Series Data

```http
GET /api/devices/{deviceId}/data
Authorization: Bearer <token>
```

**Query Parameters:**
- `startTime` (ISO 8601): Start of time range
- `endTime` (ISO 8601): End of time range
- `metrics` (comma-separated): Specific metrics to retrieve
- `interval` (string): Aggregation interval (e.g., "5m", "1h")
- `limit` (integer): Maximum number of records (default: 1000)

**Example:**
```http
GET /api/devices/PLC-001/data?startTime=2024-01-20T00:00:00Z&endTime=2024-01-20T23:59:59Z&interval=1h
```

**Response:**
```json
{
  "deviceId": "PLC-001",
  "timeRange": {
    "start": "2024-01-20T00:00:00Z",
    "end": "2024-01-20T23:59:59Z"
  },
  "data": [
    {
      "timestamp": "2024-01-20T00:00:00Z",
      "temperature": 25.5,
      "pressure": 101.3,
      "rpm": 1500
    },
    {
      "timestamp": "2024-01-20T01:00:00Z",
      "temperature": 26.1,
      "pressure": 101.2,
      "rpm": 1520
    }
  ],
  "metadata": {
    "recordCount": 24,
    "aggregationInterval": "1h"
  }
}
```

#### Get Latest Data

```http
GET /api/devices/{deviceId}/data/latest
Authorization: Bearer <token>
```

**Response:**
```json
{
  "deviceId": "PLC-001",
  "timestamp": "2024-01-20T14:30:00Z",
  "data": {
    "temperature": 25.8,
    "pressure": 101.5,
    "rpm": 1510
  }
}
```

### Analytics

#### Get Device Statistics

```http
GET /api/analytics/devices/{deviceId}/stats
Authorization: Bearer <token>
```

**Query Parameters:**
- `metric` (string): Metric to analyze
- `startTime` (ISO 8601): Start time
- `endTime` (ISO 8601): End time

**Response:**
```json
{
  "deviceId": "PLC-001",
  "metric": "temperature",
  "statistics": {
    "min": 24.5,
    "max": 28.3,
    "avg": 26.2,
    "stddev": 0.8,
    "count": 1440
  },
  "timeRange": {
    "start": "2024-01-20T00:00:00Z",
    "end": "2024-01-20T23:59:59Z"
  }
}
```

### Alarms

#### Get Active Alarms

```http
GET /api/alarms
Authorization: Bearer <token>
```

**Query Parameters:**
- `deviceId` (string): Filter by device
- `severity` (string): Filter by severity (info, warning, critical)
- `status` (string): Filter by status (active, acknowledged, resolved)

**Response:**
```json
[
  {
    "id": 1,
    "deviceId": "PLC-001",
    "severity": "warning",
    "message": "Temperature exceeds threshold",
    "timestamp": "2024-01-20T14:15:00Z",
    "status": "active",
    "metadata": {
      "currentValue": 85.5,
      "threshold": 80.0
    }
  }
]
```

#### Acknowledge Alarm

```http
POST /api/alarms/{id}/acknowledge
Authorization: Bearer <token>
Content-Type: application/json

{
  "acknowledgedBy": "operator@example.com",
  "notes": "Investigating the issue"
}
```

## AI Service API

### Chat

#### Send Message

```http
POST /chat
Content-Type: application/json

{
  "message": "Show me average temperature for PLC-001 today",
  "sessionId": "optional-session-id",
  "context": {
    "deviceId": "PLC-001"
  }
}
```

**Response:**
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "response": "The average temperature for PLC-001 today is 26.2°C",
  "data": {
    "deviceId": "PLC-001",
    "metric": "temperature",
    "value": 26.2,
    "unit": "celsius"
  },
  "visualization": {
    "type": "line-chart",
    "chartData": [...],
    "component": "React component code"
  }
}
```

#### Stream Chat Response

```http
POST /chat/stream
Content-Type: application/json

{
  "message": "Analyze factory performance"
}
```

**Response:** Server-Sent Events (SSE)
```
data: {"type":"token","content":"The"}

data: {"type":"token","content":" factory"}

data: {"type":"complete","response":"Full response text"}
```

### Natural Language Query

#### Execute Query

```http
POST /query
Content-Type: application/json

{
  "query": "What is the current RPM of conveyor1?",
  "language": "en"
}
```

**Response:**
```json
{
  "query": "What is the current RPM of conveyor1?",
  "result": {
    "deviceId": "conveyor1",
    "metric": "rpm",
    "value": 1520,
    "timestamp": "2024-01-20T14:30:00Z"
  },
  "sqlQuery": "SELECT rpm FROM plc_data WHERE device_id='conveyor1' ORDER BY timestamp DESC LIMIT 1",
  "processingTime": 45
}
```

### Analytics

#### Get Factory Summary

```http
GET /analysis/factory/summary
```

**Response:**
```json
{
  "totalDevices": 35,
  "activeDevices": 32,
  "inactiveDevices": 3,
  "totalDataPoints": 1523456,
  "lastUpdate": "2024-01-20T14:30:00Z",
  "deviceTypes": {
    "plc": 10,
    "sensor": 20,
    "actuator": 5
  },
  "health": {
    "status": "healthy",
    "score": 95.5
  }
}
```

#### Device Performance Analysis

```http
POST /analysis/device/performance
Content-Type: application/json

{
  "deviceId": "PLC-001",
  "metric": "rpm",
  "timeRange": {
    "start": "2024-01-20T00:00:00Z",
    "end": "2024-01-20T23:59:59Z"
  },
  "analysisType": "trend"
}
```

**Response:**
```json
{
  "deviceId": "PLC-001",
  "metric": "rpm",
  "analysis": {
    "trend": "increasing",
    "changePercent": 5.2,
    "anomalies": [
      {
        "timestamp": "2024-01-20T10:15:00Z",
        "value": 2100,
        "expectedRange": [1400, 1600],
        "severity": "warning"
      }
    ],
    "predictions": [
      {
        "timestamp": "2024-01-21T00:00:00Z",
        "predictedValue": 1580,
        "confidence": 0.85
      }
    ]
  }
}
```

## WebSocket API

### Real-Time Data Stream

Connect to WebSocket for real-time device data:

```javascript
const ws = new WebSocket('ws://localhost:8080/ws/data');

// Subscribe to device
ws.send(JSON.stringify({
  type: 'subscribe',
  deviceId: 'PLC-001',
  metrics: ['temperature', 'pressure']
}));

// Receive data
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Message Format:**
```json
{
  "type": "data",
  "deviceId": "PLC-001",
  "timestamp": "2024-01-20T14:30:15Z",
  "data": {
    "temperature": 26.1,
    "pressure": 101.4
  }
}
```

### Subscribe/Unsubscribe

**Subscribe:**
```json
{
  "type": "subscribe",
  "deviceId": "PLC-001",
  "metrics": ["temperature", "rpm"]
}
```

**Unsubscribe:**
```json
{
  "type": "unsubscribe",
  "deviceId": "PLC-001"
}
```

## MQTT Topics

### Topic Structure

```
factory/
├── devices/{deviceId}/telemetry    # Device data
├── devices/{deviceId}/status       # Device status
├── devices/{deviceId}/commands     # Device commands
├── processed                       # Enriched data
├── alerts                          # System alerts
└── raw                             # Raw data archive
```

### Publishing Telemetry

**Topic:** `factory/devices/{deviceId}/telemetry`

**Payload:**
```json
{
  "deviceId": "PLC-001",
  "timestamp": 1705758615000,
  "data": {
    "temperature": 26.1,
    "pressure": 101.4,
    "rpm": 1520
  }
}
```

### Subscribing to Processed Data

**Topic:** `factory/processed`

**Payload:**
```json
{
  "device_id": "PLC-001",
  "type": "sensor",
  "timestamp": 1705758615.123,
  "data": {
    "temperature": 26.1,
    "pressure": 101.4
  },
  "metadata": {
    "source": "plc",
    "node_red_version": "3.0",
    "processed_at": "2024-01-20T14:30:15Z"
  },
  "data_quality": {
    "validation": "passed",
    "completeness": 1.0
  }
}
```

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "Device with ID 'PLC-999' not found",
    "timestamp": "2024-01-20T14:30:00Z",
    "requestId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Codes

| Code | Description |
|------|-------------|
| `DEVICE_NOT_FOUND` | Device does not exist |
| `INVALID_TIME_RANGE` | Invalid time range parameters |
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `DATABASE_ERROR` | Database operation failed |
| `VALIDATION_ERROR` | Request validation failed |

## Rate Limiting

### Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/auth/*` | 5 requests | 1 minute |
| `/api/devices/*` | 100 requests | 1 minute |
| `/api/devices/*/data` | 50 requests | 1 minute |
| `/chat` | 20 requests | 1 minute |
| `/query` | 30 requests | 1 minute |

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705758675
```

### Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds",
    "retryAfter": 45
  }
}
```

## Pagination

For endpoints returning lists, use pagination parameters:

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `pageSize` (integer): Items per page (default: 20, max: 100)
- `sort` (string): Sort field
- `order` (string): Sort order (`asc` or `desc`)

**Example:**
```http
GET /api/devices?page=2&pageSize=50&sort=name&order=asc
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "pageSize": 50,
    "totalPages": 5,
    "totalItems": 234,
    "hasNext": true,
    "hasPrevious": true
  }
}
```

## SDK Examples

### JavaScript/TypeScript

```typescript
import { VirtPLCClient } from '@virtplc/sdk';

const client = new VirtPLCClient({
  baseUrl: 'http://localhost:8080/api',
  token: 'your-jwt-token'
});

// Get devices
const devices = await client.devices.list();

// Get device data
const data = await client.devices.getData('PLC-001', {
  startTime: new Date('2024-01-20T00:00:00Z'),
  endTime: new Date('2024-01-20T23:59:59Z'),
  interval: '1h'
});

// Real-time data
const stream = client.devices.stream('PLC-001');
stream.on('data', (data) => {
  console.log('New data:', data);
});
```

### Python

```python
from virtplc import VirtPLCClient
from datetime import datetime, timedelta

client = VirtPLCClient(
    base_url='http://localhost:8080/api',
    token='your-jwt-token'
)

# Get devices
devices = client.devices.list()

# Get device data
data = client.devices.get_data(
    'PLC-001',
    start_time=datetime.now() - timedelta(days=1),
    end_time=datetime.now(),
    interval='1h'
)

# Natural language query
result = client.ai.query("What is the average temperature today?")
```

## Additional Resources

- [OpenAPI/Swagger Specification](./api-documentation.html)
- [Postman Collection](./VirtPLC.postman_collection.json)
- [Authentication Guide](./OAUTH2_SETUP.md)
- [WebSocket Guide](./websocket-guide.md)
- [MQTT Integration](./mqtt-integration.md)

## Support

For API support:
- Documentation: [docs.virtplc.com](https://docs.virtplc.com)
- Issues: [GitHub Issues](https://github.com/Csingiling1/VirtPLC/issues)
- Email: api-support@virtplc.com
