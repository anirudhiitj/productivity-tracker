/**
 * App Component - Main application container
 */

import React, { useState, useEffect } from 'react';
import { ProcessTable } from './components/ProcessTable';
import { apiService } from './services/api';
import './App.css';

function App() {
  const [processes, setProcesses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // Fetch processes from backend
  const fetchProcesses = async () => {
    try {
      const data = await apiService.getMainProcesses();
      setProcesses(data.processes || []);
      setStats(data.stats || null);
      setError(null);
      setIsConnected(true);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch processes:', err);
      setError('Unable to connect to backend server. Make sure it\'s running on http://localhost:8000');
      setIsConnected(false);
      setLoading(false);
    }
  };

  // Initial load and setup interval
  useEffect(() => {
    // Fetch immediately
    fetchProcesses();

    // Setup auto-refresh every 3 seconds
    const interval = setInterval(() => {
      fetchProcesses();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <div className="app-container">
        <ProcessTable 
          processes={processes} 
          loading={loading} 
          error={error}
          stats={stats}
        />
        
        {isConnected && (
          <div className="connection-status">
            ✅ Connected to backend (localhost:8000)
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
