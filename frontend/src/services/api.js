/**
 * API Service - Fetch calls to FastAPI backend
 */

// Get API base URL dynamically (re-evaluated on each call)
// This ensures Electron's injected window.__BACKEND_URL__ is picked up
// even if it's set after module load
const getAPIBaseURL = () => {
  if (typeof window !== 'undefined' && window.__BACKEND_URL__) {
    return `${window.__BACKEND_URL__}/api`;
  }
  // Default fallback for dev mode
  return '/api';
};

console.log('[API] Initial Base URL:', getAPIBaseURL());

export const apiService = {
  /**
   * Get main processes (filtered by RAM/CPU usage)
   */
  getMainProcesses: async () => {
    try {
      const base = getAPIBaseURL();
      const response = await fetch(`${base}/processes/main`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch processes`);
      return await response.json();
    } catch (error) {
      console.error('[API] Error fetching main processes:', error);
      throw error;
    }
  },

  /**
   * Get all running processes
   */
  getAllProcesses: async () => {
    try {
      const base = getAPIBaseURL();
      const response = await fetch(`${base}/processes/all`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch all processes`);
      return await response.json();
    } catch (error) {
      console.error('[API] Error fetching all processes:', error);
      throw error;
    }
  },

  /**
   * Get process statistics
   */
  getProcessStats: async () => {
    try {
      const base = getAPIBaseURL();
      const response = await fetch(`${base}/processes/stats`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch stats`);
      return await response.json();
    } catch (error) {
      console.error('[API] Error fetching stats:', error);
      throw error;
    }
  },

  /**
   * Get processes by category
   */
  getProcessesByCategory: async (category) => {
    try {
      const base = getAPIBaseURL();
      const response = await fetch(`${base}/processes/category/${category}`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) throw new Error(`Failed to fetch ${category} processes`);
      return await response.json();
    } catch (error) {
      console.error(`[API] Error fetching ${category} processes:`, error);
      throw error;
    }
  },

  /**
   * Health check
   */
  healthCheck: async () => {
    try {
      const base = getAPIBaseURL();
      const healthUrl = base.replace('/api', '') + '/api/health';
      const response = await fetch(healthUrl);
      return await response.json();
    } catch (error) {
      console.error('[API] Health check failed:', error);
      throw error;
    }
  }
};
