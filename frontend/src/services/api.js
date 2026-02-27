/**
 * API Service - Fetch calls to FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

export const apiService = {
  /**
   * Get main processes (filtered by RAM/CPU usage)
   */
  getMainProcesses: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/processes/main`);
      if (!response.ok) throw new Error('Failed to fetch processes');
      return await response.json();
    } catch (error) {
      console.error('Error fetching main processes:', error);
      throw error;
    }
  },

  /**
   * Get all running processes
   */
  getAllProcesses: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/processes/all`);
      if (!response.ok) throw new Error('Failed to fetch all processes');
      return await response.json();
    } catch (error) {
      console.error('Error fetching all processes:', error);
      throw error;
    }
  },

  /**
   * Get process statistics
   */
  getProcessStats: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/processes/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      return await response.json();
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  },

  /**
   * Get processes by category
   */
  getProcessesByCategory: async (category) => {
    try {
      const response = await fetch(`${API_BASE_URL}/processes/category/${category}`);
      if (!response.ok) throw new Error(`Failed to fetch ${category} processes`);
      return await response.json();
    } catch (error) {
      console.error(`Error fetching ${category} processes:`, error);
      throw error;
    }
  },

  /**
   * Health check
   */
  healthCheck: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};
