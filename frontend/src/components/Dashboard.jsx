import React, { useMemo, useState } from 'react';
import { buildDashboardModel } from '../utils/scoring';
import './Dashboard.css';

const tierClass = {
  Iron: 'tier-iron',
  Bronze: 'tier-bronze',
  Silver: 'tier-silver',
  Gold: 'tier-gold',
  Platinum: 'tier-platinum',
  Diamond: 'tier-diamond'
};

const CATEGORY_COLORS = {
  'Productive': '#10b981',
  'Gaming': '#ef4444',
  'Educational': '#3b82f6',
  'Entertainment': '#f97316',
  'Neutral': '#9ca3af'
};

const SOURCE_COLORS = {
  'dictionary': '#8b5cf6',
  'cache': '#06b6d4',
  'gemini': '#f59e0b',
  'heuristic': '#ec4899',
  'devtools': '#10b981',
  'error': '#6b7280'
};

const categoryLabel = {
  CP: 'Competitive Programming',
  DEV: 'Development Tools',
  EDU: 'Educational Content',
  SOC: 'Social Media',
  ENT: 'Entertainment Streaming'
};

const formatMinutes = (value) => `${Math.max(0, value).toFixed(1)}m`;

const formatTime = (seconds) => {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
};

const getProcessIcon = (name) => {
  const lowerName = (name || '').toLowerCase();
  if (lowerName.includes('chrome') || lowerName.includes('firefox') || lowerName.includes('edge')) return '🌐';
  if (lowerName.includes('code') || lowerName.includes('studio')) return '💻';
  if (lowerName.includes('discord') || lowerName.includes('slack')) return '💬';
  if (lowerName.includes('spotify') || lowerName.includes('music')) return '🎵';
  if (lowerName.includes('valorant') || lowerName.includes('game')) return '🎮';
  if (lowerName.includes('python') || lowerName.includes('node')) return '🐍';
  return '⚙️';
};

export function Dashboard({ processes, stats, loading, error, lastUpdated, isConnected, intervalSeconds = 3, theme, onToggleTheme }) {
  const model = useMemo(() => buildDashboardModel(processes, intervalSeconds), [processes, intervalSeconds]);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [expandedRow, setExpandedRow] = useState(null);

  if (error) {
    return (
      <div className="state-box error-box">
        <h2>Backend unavailable</h2>
        <p>{error}</p>
      </div>
    );
  }

  if (loading && (!processes || processes.length === 0)) {
    return (
      <div className="state-box loading-box">
        <div className="loader" />
        <p>Loading productivity telemetry...</p>
      </div>
    );
  }

  const liveActivities = (processes || []).filter((p) => p.window_title || p.domain).slice(0, 16);

  return (
    <div className="dashboard-root">
      <header className="topbar">
        <div>
          <h1>FocusRank</h1>
          <p>Attention model, leaderboard, streaks, and tiered progress</p>
        </div>
        <div className="topbar-actions">
          <button type="button" className="theme-btn" onClick={onToggleTheme}>
            {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
          </button>
          <span className={`connection-pill ${isConnected ? 'ok' : 'bad'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </header>

      <section className="kpi-grid">
        <article className="kpi-card">
          <h3>Attention Score</h3>
          <p className="kpi-value">{model.score.toFixed(2)}</p>
          <small>Xi = Σc wc · log(1 + Aic)</small>
        </article>
        <article className="kpi-card">
          <h3>Skill Rating</h3>
          <p className="kpi-value">{model.skill.conservative.toFixed(2)}</p>
          <small>Conservative: Ri = μi - 2σi</small>
        </article>
        <article className="kpi-card">
          <h3>Tier</h3>
          <p className={`kpi-value ${tierClass[model.tier]}`}>{model.tier}</p>
          <small>{model.percentile.toFixed(1)} percentile</small>
        </article>
        <article className="kpi-card">
          <h3>Streak</h3>
          <p className="kpi-value">{model.streak.current} days</p>
          <small>Threshold: {model.streak.threshold} productive mins/day</small>
        </article>
        <article className="kpi-card">
          <h3>Leaderboard</h3>
          <p className="kpi-value">Top {model.topPercent}%</p>
          <small>Rank #{model.rank} / {model.cohortSize}</small>
        </article>
        <article className="kpi-card">
          <h3>Community Pulse</h3>
          <p className="kpi-value">{model.activeUsers} active</p>
          <small>{model.similarUsers} users with similar task profile</small>
        </article>
      </section>

      <section className="panel-grid">
        <article className="panel leaderboard-panel">
          <div className="panel-title-row">
            <h2>Leaderboard</h2>
            <span>Updated: {lastUpdated}</span>
          </div>
          <div className="leaderboard-table">
            <div className="head row">
              <span>Rank</span>
              <span>User</span>
              <span>Score</span>
              <span>Tier</span>
            </div>
            {model.leaderboard.map((entry) => {
              const entryPercentile = ((model.cohortSize - entry.rank + 1) / model.cohortSize) * 100;
              const entryTier = entry.isYou ? model.tier : (entryPercentile >= 97 ? 'Diamond' : entryPercentile >= 88 ? 'Platinum' : entryPercentile >= 70 ? 'Gold' : entryPercentile >= 45 ? 'Silver' : entryPercentile >= 25 ? 'Bronze' : 'Iron');
              return (
                <div className={`row ${entry.isYou ? 'you-row' : ''}`} key={entry.id}>
                  <span>#{entry.rank}</span>
                  <span>{entry.isYou ? 'You' : entry.id}</span>
                  <span>{entry.score.toFixed(2)}</span>
                  <span className={tierClass[entryTier]}>{entryTier}</span>
                </div>
              );
            })}
          </div>
        </article>

        <article className="panel categories-panel">
          <h2>Category Performance</h2>
          <div className="category-list">
            {model.domainPercentiles.map((item) => (
              <div className="category-item" key={item.key}>
                <div>
                  <h4>{categoryLabel[item.key]}</h4>
                  <p>{formatMinutes(item.activeMinutes)} • log={item.logScaled.toFixed(2)}</p>
                </div>
                <div className="category-metrics">
                  <strong className={item.weighted >= 0 ? 'good' : 'bad'}>{item.weighted.toFixed(2)}</strong>
                  <small>Top {(100 - item.percentile).toFixed(0)}%</small>
                </div>
              </div>
            ))}
          </div>
        </article>
      </section>

      {/* Full Process Table */}
      <section className="process-table-section">
        <div className="table-header">
          <h2>🔍 All Active Processes</h2>
          <div className="table-stats">
            <span>Total: {processes?.length || 0} processes</span>
            <span>Memory: {stats?.total_memory_mb?.toFixed?.(1) || '0.0'}MB</span>
            <span>CPU: {stats?.total_cpu_percent?.toFixed?.(1) || '0.0'}%</span>
          </div>
        </div>

        <div className="process-list">
          {processes && processes.length > 0 ? (
            processes.map((proc) => {
              const isExpanded = expandedRow === proc.pid;
              return (
                <div className="process-item" key={`${proc.pid}-${proc.window_title || proc.name}`}>
                  <div 
                    className="process-row" 
                    onClick={() => setExpandedRow(isExpanded ? null : proc.pid)}
                  >
                    <div className="row-content">
                      <div className="col-name">
                        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                        <span className="process-icon">{getProcessIcon(proc.name)}</span>
                        <div className="name-info">
                          <strong>{proc.name}</strong>
                          {proc.window_title && (
                            <small className="window-title-preview">
                              {proc.window_title.substring(0, 60)}{proc.window_title.length > 60 ? '...' : ''}
                            </small>
                          )}
                        </div>
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
                        <span className="memory-value">{proc.memory_mb?.toFixed?.(0) || 0}MB</span>
                        <span className="memory-percent">({proc.memory_percent?.toFixed?.(2) || 0}%)</span>
                      </div>

                      <div className="col-cpu">
                        <span className={`cpu-value ${(proc.cpu_percent || 0) > 10 ? 'high-cpu' : ''}`}>
                          {proc.cpu_percent?.toFixed?.(2) || 0}%
                        </span>
                      </div>

                      <div className="col-runtime">
                        {formatTime(proc.runtime_seconds || 0)}
                      </div>

                      <div className="col-user">
                        {proc.username || 'N/A'}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="process-details">
                      <div className="details-grid">
                        <div className="detail-item">
                          <span className="detail-label">🔢 PID:</span>
                          <span className="detail-value">{proc.pid}</span>
                        </div>

                        {proc.window_title && (
                          <div className="detail-item">
                            <span className="detail-label">🪟 Window Title:</span>
                            <span className="detail-value">{proc.window_title}</span>
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

                        {proc.categorization_source && (
                          <div className="detail-item">
                            <span className="detail-label">📊 Source:</span>
                            <span 
                              className="source-badge"
                              style={{ 
                                backgroundColor: SOURCE_COLORS[proc.categorization_source] || SOURCE_COLORS.error,
                                color: '#fff',
                                padding: '4px 8px',
                                borderRadius: '4px',
                                fontSize: '12px'
                              }}
                            >
                              {proc.categorization_source}
                            </span>
                          </div>
                        )}

                        {proc.domain_confidence !== undefined && (
                          <div className="detail-item">
                            <span className="detail-label">✅ Confidence:</span>
                            <span className="detail-value">{(proc.domain_confidence * 100).toFixed(0)}%</span>
                          </div>
                        )}

                        {proc.url && (
                          <div className="detail-item full-width">
                            <span className="detail-label">🔗 URL:</span>
                            <span className="detail-value">
                              <a 
                                href={proc.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="url-link"
                              >
                                {proc.url.substring(0, 100)}{proc.url.length > 100 ? '...' : ''}
                              </a>
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="empty-state">
              <p>No processes currently tracked.</p>
            </div>
          )}
        </div>
      </section>

      <footer className="footer-row">
        <span>Last updated: {lastUpdated}</span>
        <span>Refresh: {intervalSeconds}s</span>
      </footer>
    </div>
  );
}

