/**
 * ProcessTable Component - Display processes in a table format
 * Now includes window title, domain, and categorization details
 */

import React, { useState } from 'react';
import './ProcessTable.css';

const CATEGORY_COLORS = {
  'Productive': '#10b981',      // Green
  'Gaming': '#ef4444',          // Red
  'Educational': '#3b82f6',     // Blue
  'Entertainment': '#f97316',   // Orange
  'Neutral': '#9ca3af'          // Gray
};

const SOURCE_COLORS = {
  'dictionary': '#8b5cf6',      // Purple - Most reliable
  'cache': '#06b6d4',           // Cyan - Cached result
  'gemini': '#f59e0b',          // Amber - AI-powered
  'heuristic': '#ec4899',       // Pink - Pattern-based
  'error': '#6b7280'            // Gray - Error fallback
};

const SOURCE_LABELS = {
  'dictionary': '📖 Dictionary',
  'cache': '⚡ Cached',
  'gemini': '🤖 AI',
  'heuristic': '🔍 Heuristic',
  'error': '❌ Error'
};

const BROWSER_NAMES = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 'brave.exe', 'chrome', 'firefox', 'msedge', 'opera', 'brave'];

const isBrowser = (name) => BROWSER_NAMES.includes((name || '').toLowerCase());

const getDisplayName = (proc) => {
  if (isBrowser(proc.name)) {
    if (proc.window_title) return proc.window_title.length > 60 ? proc.window_title.substring(0, 57) + '...' : proc.window_title;
    if (proc.domain) return proc.domain;
  }
  return proc.name;
};

export const ProcessTable = ({ processes, loading, error, stats }) => {
  const [expandedRow, setExpandedRow] = useState(null);

  if (error) {
    return (
      <div className="error-container">
        <h2>⚠️ Error Loading Processes</h2>
        <p>{error}</p>
        <p className="error-hint">Make sure the backend server is running on localhost:8000</p>
      </div>
    );
  }

  if (loading && (!processes || processes.length === 0)) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading processes...</p>
      </div>
    );
  }

  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (minutes < 60) return `${minutes}m ${secs}s`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false 
    });
  };

  const toggleRow = (pid) => {
    setExpandedRow(expandedRow === pid ? null : pid);
  };

  return (
    <div className="process-table-container">
      <div className="table-header">
        <h1>📊 PRODUCTIVITY TRACKER - Active Processes</h1>
        <div className="header-info">
          <span className="last-update">🔄 Last Update: {formatTimestamp(new Date().toISOString())}</span>
          {stats && (
            <span className="stats-info">
              Total: {stats.total_processes} processes | 
              Memory: {stats.total_memory_mb.toFixed(1)}MB | 
              CPU: {stats.total_cpu_percent.toFixed(1)}%
            </span>
          )}
        </div>
      </div>

      {processes && processes.length > 0 ? (
        <div className="process-list">
          {processes.map((proc, index) => (
            <div key={`${proc.pid}-${index}`} className="process-item">
              <div 
                className="process-row"
                onClick={() => toggleRow(proc.pid)}
                style={{ cursor: 'pointer' }}
              >
                <div className="row-content">
                  <div className="col-name">
                    <span className="expand-icon">
                      {expandedRow === proc.pid ? '▼' : '▶'}
                    </span>
                    <span className="process-icon">⚙️</span>
                    <span className="process-name">{getDisplayName(proc)}</span>
                    {isBrowser(proc.name) && proc.domain && (
                      <span className="process-domain-hint">{proc.domain}</span>
                    )}
                  </div>
                  
                  <div className="col-category">
                    <span 
                      className="category-badge"
                      style={{ 
                        backgroundColor: CATEGORY_COLORS[proc.category] || CATEGORY_COLORS.Neutral,
                        color: '#fff'
                      }}
                    >
                      {proc.category || 'Neutral'}
                    </span>
                  </div>
                  
                  <div className="col-memory">
                    <span className="memory-value">{proc.memory_mb.toFixed(0)}MB</span>
                    <span className="memory-percent">({proc.memory_percent.toFixed(2)}%)</span>
                  </div>
                  
                  <div className="col-cpu">
                    <span className={`cpu-value ${proc.cpu_percent > 10 ? 'high-cpu' : ''}`}>
                      {proc.cpu_percent.toFixed(2)}%
                    </span>
                  </div>
                  
                  <div className="col-runtime">
                    {formatTime(proc.runtime_seconds)}
                  </div>
                  
                  <div className="col-user">
                    {proc.username}
                  </div>
                </div>
              </div>

              {/* Expanded Details Row */}
              {expandedRow === proc.pid && (
                <div className="process-details">
                  <div className="details-section">
                    {proc.window_title && (
                      <div className="detail-item">
                        <span className="detail-label">🪟 Window Title:</span>
                        <span className="detail-value" title={proc.window_title}>
                          {proc.window_title}
                        </span>
                      </div>
                    )}
                    
                    {proc.domain && (
                      <div className="detail-item">
                        <span className="detail-label">🌐 Domain:</span>
                        <span className="detail-value">
                          <a 
                            href={`https://${proc.domain}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="domain-link"
                          >
                            {proc.domain}
                          </a>
                        </span>
                      </div>
                    )}
                    
                    {proc.domain && proc.categorization_source && (
                      <div className="detail-item">
                        <span className="detail-label">📊 Categorization:</span>
                        <div className="source-info">
                          <span 
                            className="source-badge"
                            style={{ backgroundColor: SOURCE_COLORS[proc.categorization_source] || SOURCE_COLORS.error }}
                          >
                            {SOURCE_LABELS[proc.categorization_source] || 'Unknown'}
                          </span>
                          {proc.domain_confidence > 0 && (
                            <span className="confidence-score">
                              Confidence: {(proc.domain_confidence * 100).toFixed(0)}%
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="no-data">
          <p>No main processes found</p>
        </div>
      )}

      <div className="table-footer">
        <p className="auto-refresh">🔄 Auto-refreshes every 3 seconds</p>
        <p className="source-legend">
          <strong>Categorization Sources:</strong>
          {Object.entries(SOURCE_LABELS).map(([key, label]) => (
            <span key={key} className="legend-item">
              <span 
                className="legend-color" 
                style={{ backgroundColor: SOURCE_COLORS[key] }}
              ></span>
              {label}
            </span>
          ))}
        </p>
      </div>
    </div>
  );
};

