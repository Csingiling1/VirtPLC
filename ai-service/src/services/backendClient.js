import axios from 'axios';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://localhost:8080';
const TIMEOUT = parseInt(process.env.BACKEND_API_TIMEOUT) || 5000;

const backendClient = axios.create({
  baseURL: BACKEND_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Fetch latest sensor data from backend
 */
export async function fetchLatestData() {
  try {
    const response = await backendClient.get('/api/data/latest');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch data from backend:', error.message);
    throw new Error('Backend connection failed');
  }
}

/**
 * Fetch historical data range from backend
 */
export async function fetchDataRange(startTime, endTime) {
  try {
    const response = await backendClient.get('/api/data/range', {
      params: { startTime, endTime }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch historical data:', error.message);
    throw new Error('Backend connection failed');
  }
}

/**
 * Check backend health
 */
export async function checkBackendHealth() {
  try {
    const response = await backendClient.get('/api/data/health');
    return response.status === 200;
  } catch (error) {
    return false;
  }
}

export default backendClient;
