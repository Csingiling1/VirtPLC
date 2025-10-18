import express from 'express';
import { analyzeSensorData, predictMaintenance, detectAnomalies } from '../services/analysisService.js';
import { fetchLatestData } from '../services/backendClient.js';

const router = express.Router();

/**
 * POST /api/analysis/analyze
 * Analyze provided sensor data or fetch latest from backend
 */
router.post('/analyze', async (req, res) => {
  try {
    const { sensorData } = req.body;
    
    // Use provided data or fetch from backend
    const data = sensorData || await fetchLatestData();
    
    if (!data) {
      return res.status(400).json({ error: 'No sensor data available' });
    }

    const analysis = await analyzeSensorData(data);
    
    res.json({
      timestamp: new Date().toISOString(),
      data,
      analysis
    });
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ 
      error: 'Analysis failed',
      message: error.message 
    });
  }
});

/**
 * GET /api/analysis/predict-maintenance
 * Predict maintenance needs based on current sensor readings
 */
router.get('/predict-maintenance', async (req, res) => {
  try {
    const data = await fetchLatestData();
    
    if (!data) {
      return res.status(503).json({ error: 'Backend data unavailable' });
    }

    const prediction = await predictMaintenance(data);
    
    res.json({
      timestamp: new Date().toISOString(),
      prediction
    });
  } catch (error) {
    console.error('Prediction error:', error);
    res.status(500).json({ 
      error: 'Prediction failed',
      message: error.message 
    });
  }
});

/**
 * GET /api/analysis/anomalies
 * Detect anomalies in current sensor data
 */
router.get('/anomalies', async (req, res) => {
  try {
    const data = await fetchLatestData();
    
    if (!data) {
      return res.status(503).json({ error: 'Backend data unavailable' });
    }

    const anomalies = await detectAnomalies(data);
    
    res.json({
      timestamp: new Date().toISOString(),
      anomalies
    });
  } catch (error) {
    console.error('Anomaly detection error:', error);
    res.status(500).json({ 
      error: 'Anomaly detection failed',
      message: error.message 
    });
  }
});

/**
 * GET /api/analysis/status
 * Get AI service status and statistics
 */
router.get('/status', (req, res) => {
  res.json({
    status: 'operational',
    ollama: {
      host: process.env.OLLAMA_HOST,
      model: process.env.OLLAMA_MODEL
    },
    backend: process.env.BACKEND_API_URL,
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

export default router;
