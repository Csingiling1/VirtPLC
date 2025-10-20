import axios from 'axios';

const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://localhost:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama2';

const ollamaClient = axios.create({
  baseURL: OLLAMA_HOST,
  timeout: 30000, // 30 seconds for AI inference
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Generate text completion using Ollama
 */
export async function generateCompletion(prompt, options = {}) {
  try {
    const response = await ollamaClient.post('/api/generate', {
      model: OLLAMA_MODEL,
      prompt,
      stream: false,
      ...options
    });
    
    return response.data.response;
  } catch (error) {
    console.error('Ollama generation error:', error.message);
    
    // Return fallback analysis if Ollama is unavailable
    if (error.code === 'ECONNREFUSED') {
      console.warn('Ollama not available, using fallback analysis');
      return null;
    }
    
    throw error;
  }
}

/**
 * Check if Ollama is available
 */
export async function checkOllamaHealth() {
  try {
    const response = await ollamaClient.get('/api/tags');
    return response.status === 200;
  } catch (error) {
    return false;
  }
}

/**
 * List available models
 */
export async function listModels() {
  try {
    const response = await ollamaClient.get('/api/tags');
    return response.data.models || [];
  } catch (error) {
    console.error('Failed to list Ollama models:', error.message);
    return [];
  }
}

export default ollamaClient;
