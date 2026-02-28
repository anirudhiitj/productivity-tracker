/**
 * App - Main application shell with sidebar navigation and page routing
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Sidebar } from './components/Sidebar';
import { OverviewPage } from './components/OverviewPage';
import { ActivityPage } from './components/ActivityPage';
import { AnalyticsPage } from './components/AnalyticsPage';
import { ProcessesPage } from './components/ProcessesPage';
import { LeaderboardPage } from './components/LeaderboardPage';
import { buildDashboardModel } from './utils/scoring';
import { apiService } from './services/api';
import './App.css';

const PAGE_META = {
  overview:    { title: 'Dashboard',      subtitle: 'Your productivity at a glance' },
  activity:    { title: 'Activity Feed',  subtitle: 'Real-time window & tab tracking' },
  analytics:   { title: 'Analytics',      subtitle: 'Deep dive into your focus patterns' },
  processes:   { title: 'Processes',      subtitle: 'All monitored applications' },
  leaderboard: { title: 'Leaderboard',    subtitle: 'See how you rank against peers' },
};

function App() {
  const [activePage, setActivePage] = useState('overview');
  const [processes, setProcesses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [theme, setTheme] = useState(() => localStorage.getItem('pt_theme') || 'dark');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const intervalSeconds = 3;

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('pt_theme', theme);
  }, [theme]);

  const fetchProcesses = useCallback(async () => {
    try {
      const data = await apiService.getMainProcesses();
      setProcesses(data.processes || []);
      setStats(data.stats || null);
      setError(null);
      setIsConnected(true);
      setLoading(false);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch processes:', err);
      setError('Unable to connect to backend server');
      setIsConnected(false);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProcesses();
    const interval = setInterval(fetchProcesses, intervalSeconds * 1000);
    return () => clearInterval(interval);
  }, [fetchProcesses, intervalSeconds]);

  const toggleTheme = () => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));

  const model = useMemo(
    () => buildDashboardModel(processes, intervalSeconds),
    [processes, intervalSeconds]
  );

  const pageProps = { processes, stats, loading, error, isConnected, lastUpdated, model, intervalSeconds, theme };

  const renderPage = () => {
    switch (activePage) {
      case 'activity':    return <ActivityPage {...pageProps} />;
      case 'analytics':   return <AnalyticsPage {...pageProps} />;
      case 'processes':   return <ProcessesPage {...pageProps} />;
      case 'leaderboard': return <LeaderboardPage {...pageProps} />;
      default:            return <OverviewPage {...pageProps} />;
    }
  };

  const meta = PAGE_META[activePage] || PAGE_META.overview;

  return (
    <div className={`app-shell ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        theme={theme}
        onToggleTheme={toggleTheme}
        isConnected={isConnected}
        processCount={processes?.length || 0}
      />
      <main className="main-content">
        <header className="page-header">
          <div className="page-header-left">
            <h1 className="page-title">{meta.title}</h1>
            <p className="page-subtitle">{meta.subtitle}</p>
          </div>
          <div className="page-header-right">
            <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
              <span className="status-dot" />
              {isConnected ? 'Live' : 'Offline'}
            </div>
            {lastUpdated && (
              <span className="last-sync">{lastUpdated.toLocaleTimeString()}</span>
            )}
          </div>
        </header>
        <div className="page-content">
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

export default App;
