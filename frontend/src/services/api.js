import { API_URL } from '../utils/constants';

export const api = {
  // Create new generation job
  async createGeneration(data) {
    const response = await fetch(`${API_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error('Failed to create generation');
    }
    
    return response.json();
  },

  // Get job status
  async getJobStatus(jobId) {
    const response = await fetch(`${API_URL}/api/jobs/${jobId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get job status');
    }
    
    return response.json();
  },

  // Get job result
  async getJobResult(jobId) {
    const response = await fetch(`${API_URL}/api/jobs/${jobId}/result`);
    
    if (!response.ok) {
      throw new Error('Failed to get job result');
    }
    
    return response.json();
  },

  // Get presets
  async getPresets() {
    const response = await fetch(`${API_URL}/api/presets`);
    
    if (!response.ok) {
      throw new Error('Failed to get presets');
    }
    
    return response.json();
  },

  // Get system stats
  async getStats() {
    const response = await fetch(`${API_URL}/api/stats`);
    
    if (!response.ok) {
      throw new Error('Failed to get stats');
    }
    
    return response.json();
  }
};