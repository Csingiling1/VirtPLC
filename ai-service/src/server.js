import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { WebSocketServer } from 'ws';
import analysisRoutes from './routes/analysis.js';
import { startWebSocketServer } from './websocket/wsServer.js';
import { startPeriodicAnalysis } from './services/analysisService.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;
const WS_PORT = process.env.WS_PORT || 3002;

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:8080'],
  credentials: true
}));
app.use(express.json());

// Routes
app.use('/api/analysis', analysisRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'VirtPLC AI Service',
    timestamp: new Date().toISOString(),
    ollama: process.env.OLLAMA_HOST,
    model: process.env.OLLAMA_MODEL
  });
});

// Start Express server
app.listen(PORT, () => {
  console.log(`🚀 AI Service running on port ${PORT}`);
  console.log(`📊 Ollama host: ${process.env.OLLAMA_HOST}`);
  console.log(`🤖 Model: ${process.env.OLLAMA_MODEL}`);
  console.log(`🔗 Backend API: ${process.env.BACKEND_API_URL}`);
});

// Start WebSocket server
const wss = new WebSocketServer({ port: WS_PORT });
startWebSocketServer(wss);
console.log(`🔌 WebSocket server running on port ${WS_PORT}`);

// Start periodic analysis
startPeriodicAnalysis(wss);

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  wss.close(() => {
    console.log('WebSocket server closed');
    process.exit(0);
  });
});
