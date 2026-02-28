/**
 * App Component - Main application container
 */

import React, { useState, useEffect } from 'react';
import { Dashboard } from './components/Dashboard';
import { apiService } from './services/api';
import './App.css';

function App() {
  const [processes, setProcesses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState('—');
  const [theme, setTheme] = useState(() => localStorage.getItem('pt_theme') || 'dark');
  const intervalSeconds = 3;

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('pt_theme', theme);
  }, [theme]);

  // Fetch processes from backend
  const fetchProcesses = async () => {
    try {
      const data = await apiService.getMainProcesses();
      setProcesses(data.processes || []);
      setStats(data.stats || null);
      setError(null);
      setIsConnected(true);
      setLoading(false);
      setLastUpdated(new Date().toLocaleTimeString());
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
    }, intervalSeconds * 1000);

    return () => clearInterval(interval);
  }, [intervalSeconds]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="app">
      <div className="app-container">
        <Dashboard
          processes={processes}
          stats={stats}
          loading={loading}
          error={error}
          lastUpdated={lastUpdated}
          isConnected={isConnected}
          intervalSeconds={intervalSeconds}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
      </div>
    </div>
  );
}

export default App;
