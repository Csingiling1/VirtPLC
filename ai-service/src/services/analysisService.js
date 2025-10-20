import { generateCompletion, checkOllamaHealth } from './ollamaClient.js';
import { fetchLatestData } from './backendClient.js';

let analysisInterval = null;

/**
 * Analyze sensor data using AI or rule-based approach
 */
export async function analyzeSensorData(data) {
  const isOllamaAvailable = await checkOllamaHealth();
  
  if (isOllamaAvailable) {
    return await analyzeWithAI(data);
  } else {
    console.warn('Ollama unavailable, using rule-based analysis');
    return analyzeWithRules(data);
  }
}

/**
 * AI-based analysis using Ollama
 */
async function analyzeWithAI(data) {
  const prompt = `
You are an industrial factory monitoring AI. Analyze the following sensor data and provide insights:

Motor 1: Speed ${data.motor1Speed?.toFixed(1)} RPM, Temperature ${data.motor1Temp?.toFixed(1)}°C, Running: ${data.motor1Run}
Motor 2: Speed ${data.motor2Speed?.toFixed(1)} RPM, Temperature ${data.motor2Temp?.toFixed(1)}°C, Running: ${data.motor2Run}
Conveyor: Speed ${data.conveyor1Speed?.toFixed(1)} cm/s, Running: ${data.conveyor1Run}
Sensor 1: Value ${data.sensor1Value?.toFixed(2)}
Sensor 2: ${data.sensor2Value ? 'Active' : 'Inactive'}

Provide a brief analysis (2-3 sentences) focusing on:
1. Overall system health
2. Any concerning trends
3. Recommended actions if needed
`;

  try {
    const response = await generateCompletion(prompt, {
      temperature: 0.3,
      max_tokens: 200
    });
    
    if (response) {
      return {
        method: 'AI',
        model: process.env.OLLAMA_MODEL,
        insights: response,
        ...getRuleBasedMetrics(data)
      };
    }
  } catch (error) {
    console.error('AI analysis failed:', error.message);
  }
  
  // Fallback to rule-based
  return analyzeWithRules(data);
}

/**
 * Rule-based analysis (fallback)
 */
function analyzeWithRules(data) {
  const issues = [];
  const warnings = [];
  const recommendations = [];
  
  // Motor 1 checks
  if (data.motor1Temp > 70) {
    issues.push('Motor 1 temperature critical (>70°C)');
    recommendations.push('Inspect Motor 1 cooling system');
  } else if (data.motor1Temp > 60) {
    warnings.push('Motor 1 temperature elevated (>60°C)');
  }
  
  if (data.motor1Speed > 90) {
    warnings.push('Motor 1 running at high speed');
  }
  
  // Motor 2 checks
  if (data.motor2Temp > 70) {
    issues.push('Motor 2 temperature critical (>70°C)');
    recommendations.push('Inspect Motor 2 cooling system');
  } else if (data.motor2Temp > 60) {
    warnings.push('Motor 2 temperature elevated (>60°C)');
  }
  
  // Conveyor checks
  if (data.conveyor1Speed < 15) {
    warnings.push('Conveyor speed below optimal range');
  }
  
  // Sensor checks
  if (data.sensor1Value > 90) {
    warnings.push('Sensor 1 value approaching maximum');
  }
  
  // Overall health
  let healthStatus = 'Excellent';
  if (issues.length > 0) {
    healthStatus = 'Critical';
  } else if (warnings.length > 0) {
    healthStatus = 'Warning';
  }
  
  const summary = issues.length > 0
    ? `${issues.length} critical issue(s) detected. Immediate attention required.`
    : warnings.length > 0
    ? `${warnings.length} warning(s) detected. Monitor closely.`
    : 'All systems operating within normal parameters.';
  
  return {
    method: 'Rule-Based',
    healthStatus,
    summary,
    issues,
    warnings,
    recommendations,
    ...getRuleBasedMetrics(data)
  };
}

/**
 * Get metrics for both AI and rule-based analysis
 */
function getRuleBasedMetrics(data) {
  return {
    metrics: {
      avgMotorTemp: ((data.motor1Temp + data.motor2Temp) / 2).toFixed(1),
      avgMotorSpeed: ((data.motor1Speed + data.motor2Speed) / 2).toFixed(1),
      conveyorEfficiency: (data.conveyor1Speed / 50 * 100).toFixed(1) + '%',
      systemUptime: data.motor1Run && data.motor2Run && data.conveyor1Run ? '100%' : 'Partial'
    }
  };
}

/**
 * Predict maintenance needs
 */
export async function predictMaintenance(data) {
  const predictions = [];
  
  // Motor 1 maintenance prediction
  if (data.motor1Temp > 65 || data.motor1Speed > 85) {
    predictions.push({
      component: 'Motor 1',
      priority: data.motor1Temp > 70 ? 'High' : 'Medium',
      estimatedDays: data.motor1Temp > 70 ? 7 : 14,
      reason: 'High temperature and speed indicate increased wear',
      confidence: 0.75
    });
  }
  
  // Motor 2 maintenance prediction
  if (data.motor2Temp > 65 || data.motor2Speed > 85) {
    predictions.push({
      component: 'Motor 2',
      priority: data.motor2Temp > 70 ? 'High' : 'Medium',
      estimatedDays: data.motor2Temp > 70 ? 7 : 14,
      reason: 'High temperature and speed indicate increased wear',
      confidence: 0.75
    });
  }
  
  // Conveyor maintenance
  if (data.conveyor1Speed < 20) {
    predictions.push({
      component: 'Conveyor 1',
      priority: 'Low',
      estimatedDays: 30,
      reason: 'Reduced speed may indicate belt wear',
      confidence: 0.60
    });
  }
  
  return {
    maintenanceNeeded: predictions.length > 0,
    predictions,
    nextScheduledCheck: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
  };
}

/**
 * Detect anomalies in sensor data
 */
export async function detectAnomalies(data) {
  const anomalies = [];
  
  // Temperature anomaly detection
  const tempDiff = Math.abs(data.motor1Temp - data.motor2Temp);
  if (tempDiff > 20) {
    anomalies.push({
      type: 'Temperature Imbalance',
      severity: 'Medium',
      description: `Motor temperature difference is ${tempDiff.toFixed(1)}°C (normal: <20°C)`,
      affectedComponents: ['Motor 1', 'Motor 2']
    });
  }
  
  // Speed anomaly detection
  const speedDiff = Math.abs(data.motor1Speed - data.motor2Speed);
  if (speedDiff > 30) {
    anomalies.push({
      type: 'Speed Imbalance',
      severity: 'Low',
      description: `Motor speed difference is ${speedDiff.toFixed(1)} RPM (normal: <30 RPM)`,
      affectedComponents: ['Motor 1', 'Motor 2']
    });
  }
  
  // Sensor value anomaly
  if (data.sensor1Value < 10 || data.sensor1Value > 95) {
    anomalies.push({
      type: 'Sensor Reading Anomaly',
      severity: data.sensor1Value < 10 ? 'High' : 'Medium',
      description: `Sensor 1 reading ${data.sensor1Value.toFixed(2)} is outside normal range (10-95)`,
      affectedComponents: ['Sensor 1']
    });
  }
  
  return {
    anomaliesDetected: anomalies.length > 0,
    count: anomalies.length,
    anomalies
  };
}

/**
 * Start periodic analysis and broadcast via WebSocket
 */
export function startPeriodicAnalysis(wss) {
  const interval = parseInt(process.env.ANALYSIS_INTERVAL) || 5000;
  
  console.log(`🔄 Starting periodic analysis every ${interval}ms`);
  
  analysisInterval = setInterval(async () => {
    try {
      const data = await fetchLatestData();
      const analysis = await analyzeSensorData(data);
      const anomalies = await detectAnomalies(data);
      
      // Broadcast to all WebSocket clients
      const message = JSON.stringify({
        type: 'analysis',
        timestamp: new Date().toISOString(),
        data,
        analysis,
        anomalies
      });
      
      wss.clients.forEach(client => {
        if (client.readyState === 1) { // WebSocket.OPEN
          client.send(message);
        }
      });
      
      console.log(`📊 Analysis broadcast to ${wss.clients.size} client(s)`);
    } catch (error) {
      console.error('Periodic analysis error:', error.message);
    }
  }, interval);
}

/**
 * Stop periodic analysis
 */
export function stopPeriodicAnalysis() {
  if (analysisInterval) {
    clearInterval(analysisInterval);
    analysisInterval = null;
    console.log('⏹️  Periodic analysis stopped');
  }
}
