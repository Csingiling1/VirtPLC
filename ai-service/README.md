# VirtPLC AI Service

**Branch:** `feature/AI` | **Subteam:** AI Analysis | **Accenture Challenge**

AI-powered predictive analysis service using Ollama with Llama3 (8B-17B) for factory monitoring, anomaly detection, and maintenance prediction.

## 🧠 Features

- **Real-time Analysis**: Continuous monitoring and analysis of sensor data
- **Predictive Maintenance**: AI-powered predictions for equipment maintenance needs
- **Anomaly Detection**: Identify unusual patterns in factory operations
- **WebSocket Streaming**: Real-time push notifications for alerts and predictions
- **Ollama Integration**: Local LLM for intelligent analysis
- **Fallback Mode**: Rule-based analysis when AI is unavailable

## 🏗️ Architecture

```
AI Service (Node.js + Express)
├── REST API (port 3001)
│   ├── POST /api/analysis/analyze
│   ├── GET /api/analysis/predict-maintenance
│   ├── GET /api/analysis/anomalies
│   └── GET /api/analysis/status
├── WebSocket Server (port 3002)
│   └── Real-time broadcasts
└── Ollama Client
    └── Local LLM inference
```

## 📁 Project Structure

```
ai-service/
├── src/
│   ├── server.js              # Main Express server
│   ├── routes/
│   │   └── analysis.js        # API route handlers
│   ├── services/
│   │   ├── backendClient.js   # HTTP client for backend API
│   │   ├── ollamaClient.js    # Ollama LLM client
│   │   └── analysisService.js # Core analysis logic
│   ├── websocket/
│   │   └── wsServer.js        # WebSocket server
│   └── models/                # (Reserved for data models)
├── package.json
├── .env.example
├── Dockerfile
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 20+**
- **Ollama with Llama3** (runs in Docker Compose, or install manually)
  ```bash
  # With Docker Compose (recommended):
  docker-compose up -d ollama
  docker exec -it virtplc-ollama ollama pull llama3:8b
  
  # OR install manually: https://ollama.ai/download
  ollama pull llama3:8b
  ollama serve
  ```
- **Backend API** running on port 8080

### Installation

```bash
cd ai-service
npm install
cp .env.example .env
```

### Configuration (.env)

```env
PORT=3001
NODE_ENV=development
BACKEND_API_URL=http://localhost:8080
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3:8b
WS_PORT=3002
ANALYSIS_INTERVAL=5000
```

### Run Development Server

```bash
npm run dev
```

Service starts on:
- **REST API**: http://localhost:3001
- **WebSocket**: ws://localhost:3002

### Run Production Server

```bash
npm start
```

## 🐳 Docker

**Build:**
```bash
docker build -t virtplc-ai-service .
```

**Run:**
```bash
docker run -p 3001:3001 -p 3002:3002 \
  -e BACKEND_API_URL=http://backend:8080 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  virtplc-ai-service
```

## 📡 API Endpoints

### POST /api/analysis/analyze

Analyze sensor data using AI or rule-based approach.

**Request:**
```json
{
  "sensorData": {
    "motor1Speed": 75.3,
    "motor1Temp": 42.1,
    "motor2Speed": 68.9,
    "motor2Temp": 38.5,
    "conveyor1Speed": 25.6,
    "sensor1Value": 54.2,
    "sensor2Value": true
  }
}
```

**Response:**
```json
{
  "timestamp": "2025-10-19T12:00:00.000Z",
  "data": { ... },
  "analysis": {
    "method": "AI",
    "model": "llama2",
    "insights": "System health is good. Motor temperatures within normal range...",
    "metrics": {
      "avgMotorTemp": "40.3",
      "avgMotorSpeed": "72.1",
      "conveyorEfficiency": "51.2%"
    }
  }
}
```

### GET /api/analysis/predict-maintenance

Predict maintenance needs based on current readings.

**Response:**
```json
{
  "timestamp": "2025-10-19T12:00:00.000Z",
  "prediction": {
    "maintenanceNeeded": true,
    "predictions": [
      {
        "component": "Motor 1",
        "priority": "Medium",
        "estimatedDays": 14,
        "reason": "High temperature and speed indicate increased wear",
        "confidence": 0.75
      }
    ],
    "nextScheduledCheck": "2025-10-26T12:00:00.000Z"
  }
}
```

### GET /api/analysis/anomalies

Detect anomalies in current sensor readings.

**Response:**
```json
{
  "timestamp": "2025-10-19T12:00:00.000Z",
  "anomalies": {
    "anomaliesDetected": true,
    "count": 1,
    "anomalies": [
      {
        "type": "Temperature Imbalance",
        "severity": "Medium",
        "description": "Motor temperature difference is 25.3°C (normal: <20°C)",
        "affectedComponents": ["Motor 1", "Motor 2"]
      }
    ]
  }
}
```

### GET /api/analysis/status

Get service status and configuration.

**Response:**
```json
{
  "status": "operational",
  "ollama": {
    "host": "http://localhost:11434",
    "model": "llama2"
  },
  "backend": "http://localhost:8080",
  "uptime": 1234.56,
  "timestamp": "2025-10-19T12:00:00.000Z"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "VirtPLC AI Service",
  "timestamp": "2025-10-19T12:00:00.000Z",
  "ollama": "http://localhost:11434",
  "model": "llama2"
}
```

## 🔌 WebSocket API

Connect to `ws://localhost:3002` for real-time updates.

**Message Types:**

1. **Connected** (server → client on connect)
```json
{
  "type": "connected",
  "message": "Connected to VirtPLC AI Service",
  "timestamp": "2025-10-19T12:00:00.000Z"
}
```

2. **Analysis Broadcast** (server → client every 5s)
```json
{
  "type": "analysis",
  "timestamp": "2025-10-19T12:00:00.000Z",
  "data": { /* sensor data */ },
  "analysis": { /* AI insights */ },
  "anomalies": { /* detected anomalies */ }
}
```

3. **Acknowledgment** (server → client)
```json
{
  "type": "ack",
  "received": { /* echoed message */ },
  "timestamp": "2025-10-19T12:00:00.000Z"
}
```

## 🤖 Ollama Integration

### Setup Ollama

1. **Install Ollama**: https://ollama.ai/download
2. **Pull Model**:
   ```bash
   ollama pull llama2
   # or for smaller model:
   ollama pull llama2:7b
   ```
3. **Start Ollama**:
   ```bash
   ollama serve
   ```

### Supported Models

- `llama2` (default)
- `llama2:7b` (smaller, faster)
- `mistral`
- `codellama`

Change model in `.env`:
```env
OLLAMA_MODEL=mistral
```

### Fallback Mode

If Ollama is unavailable, the service automatically falls back to rule-based analysis:
- Temperature thresholds
- Speed limits
- Sensor value ranges
- Component health rules

## 🔗 Integration

### Frontend Integration

```javascript
// REST API call
const response = await fetch('http://localhost:3001/api/analysis/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ sensorData })
});
const analysis = await response.json();

// WebSocket connection
const ws = new WebSocket('ws://localhost:3002');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'analysis') {
    console.log('Real-time analysis:', message.analysis);
  }
};
```

### Backend Integration

The AI service automatically polls backend at `/api/data/latest` every 5 seconds.

Ensure backend is running:
```bash
cd backend
mvn spring-boot:run
```

## 📊 Analysis Methods

### AI-Based (Ollama)

- Natural language insights
- Context-aware recommendations
- Adaptive learning (future)
- Confidence scoring

### Rule-Based (Fallback)

- **Motor Health**:
  - Temp > 70°C: Critical
  - Temp > 60°C: Warning
  - Speed > 90 RPM: High load
  
- **Conveyor Health**:
  - Speed < 15 cm/s: Suboptimal
  
- **Sensors**:
  - Value > 90: Near maximum
  - Value < 10: Anomaly

## 🛠️ Development

### Add New Analysis Type

1. Create function in `services/analysisService.js`
2. Add route in `routes/analysis.js`
3. Update WebSocket broadcast if needed

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3001 | REST API port |
| `WS_PORT` | 3002 | WebSocket port |
| `BACKEND_API_URL` | http://localhost:8080 | Backend endpoint |
| `OLLAMA_HOST` | http://localhost:11434 | Ollama server |
| `OLLAMA_MODEL` | llama2 | LLM model name |
| `ANALYSIS_INTERVAL` | 5000 | Polling interval (ms) |
| `PREDICTION_THRESHOLD` | 0.7 | Confidence threshold |

## 📝 TODO

- [ ] Add historical trend analysis
- [ ] Implement model fine-tuning
- [ ] Add alert severity levels
- [ ] Integrate with notification system
- [ ] Add authentication for WebSocket
- [ ] Store analysis results in database
- [ ] Add performance metrics tracking
- [ ] Implement rate limiting

## 📚 Technologies

- **Node.js 20**: Runtime
- **Express 4**: REST API framework
- **ws**: WebSocket library
- **Axios**: HTTP client
- **Ollama**: Local LLM inference
- **Docker**: Containerization

## 📄 License

Part of VirtPLC project for Accenture internship.
