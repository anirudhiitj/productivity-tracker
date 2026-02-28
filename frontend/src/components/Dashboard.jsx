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

const categoryLabel = {
  CP: 'Competitive Programming',
  DEV: 'Development Tools',
  EDU: 'Educational Content',
  SOC: 'Social Media',
  ENT: 'Entertainment Streaming'
};

const formatMinutes = (value) => `${Math.max(0, value).toFixed(1)}m`;
const toClassSuffix = (value = '') => value.toLowerCase().replace(/[^a-z0-9]+/g, '-');

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

export function Dashboard({
  processes,
  stats,
  loading,
  error,
  lastUpdated,
  isConnected,
  intervalSeconds = 3,
  theme,
  onToggleTheme
}) {
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
  const topFocusSignals = model.domainPercentiles.slice(0, 4);

  return (
    <div className="dashboard-root">
      <header className="shell-header">
        <div className="brand-block">
          <h1>FocusRank OS</h1>
          <p>AI productivity intelligence • realtime activity feed • ranking engine</p>
        </div>
        <nav className="shell-nav" aria-label="Primary">
          <button className="nav-chip active" type="button">Overview</button>
          <button className="nav-chip" type="button">Leaderboard</button>
          <button className="nav-chip" type="button">Signals</button>
          <button className="nav-chip" type="button">Processes</button>
        </nav>
        <div className="topbar-actions">
          <button type="button" className="theme-btn" onClick={onToggleTheme}>
            {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
          </button>
          <span className={`connection-pill ${isConnected ? 'ok' : 'bad'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </header>

      <div className="shell-grid">
        <main className="feed-column">
          <section className="hero-card">
            <div>
              <p className="label">Your Productivity Rank</p>
              <h2>Top {model.topPercent}% this session</h2>
              <p className="hero-subtitle">Conservative score {model.skill.conservative.toFixed(2)} • Tier {model.tier}</p>
            </div>
            <div className="hero-metrics">
              <div>
                <small>Attention Score</small>
                <strong>{model.score.toFixed(2)}</strong>
              </div>
              <div>
                <small>Current Streak</small>
                <strong>{model.streak.current}d</strong>
              </div>
              <div>
                <small>Leaderboard</small>
                <strong>#{model.rank}</strong>
              </div>
            </div>
          </section>

          <section className="kpi-grid">
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
              <h3>Community Pulse</h3>
              <p className="kpi-value">{model.activeUsers}</p>
              <small>{model.similarUsers} users with similar profile</small>
            </article>
            <article className="kpi-card">
              <h3>Refresh</h3>
              <p className="kpi-value">{intervalSeconds}s</p>
              <small>Last sync: {lastUpdated}</small>
            </article>
          </section>

          <section className="panel activity-feed-panel">
            <div className="panel-title-row">
              <h2>Live Activity Feed</h2>
              <span>{liveActivities.length} live windows</span>
            </div>
            <div className="activity-list">
              {liveActivities.length > 0 ? (
                liveActivities.slice(0, 8).map((activity, idx) => {
                  const selected = selectedActivity === idx;
                  return (
                    <article className={`activity-card ${selected ? 'selected' : ''}`} key={`${activity.pid}-${idx}`}>
                      <button
                        type="button"
                        className="activity-head"
                        onClick={() => setSelectedActivity(selected ? null : idx)}
                      >
                        <div className="activity-main">
                          <span className="activity-icon">{getProcessIcon(activity.name)}</span>
                          <div>
                            <strong>{activity.name}</strong>
                            <p>{activity.window_title || activity.domain || 'No title available'}</p>
                          </div>
                        </div>
                        <div className="activity-meta">
                          <span className={`category-badge cat-${toClassSuffix(activity.category || 'neutral')}`}>
                            {activity.category || 'Neutral'}
                          </span>
                          <small>{formatTime(activity.runtime_seconds || 0)}</small>
                        </div>
                      </button>
                      {selected && (
                        <div className="activity-details">
                          <p><strong>CPU:</strong> {activity.cpu_percent?.toFixed?.(2) || 0}%</p>
                          <p><strong>Memory:</strong> {activity.memory_mb?.toFixed?.(1) || 0} MB</p>
                          <p><strong>User:</strong> {activity.username || 'N/A'}</p>
                        </div>
                      )}
                    </article>
                  );
                })
              ) : (
                <p className="muted">No active windows detected yet.</p>
              )}
            </div>
          </section>

          <section className="panel leaderboard-panel">
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
                const entryTier = entry.isYou
                  ? model.tier
                  : (entryPercentile >= 97 ? 'Diamond'
                    : entryPercentile >= 88 ? 'Platinum'
                      : entryPercentile >= 70 ? 'Gold'
                        : entryPercentile >= 45 ? 'Silver'
                          : entryPercentile >= 25 ? 'Bronze'
                            : 'Iron');
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
          </section>

          <section className="process-table-section">
            <div className="table-header">
              <h2>Process Intelligence</h2>
              <div className="table-stats">
                <span>Total {processes?.length || 0}</span>
                <span>{stats?.total_memory_mb?.toFixed?.(1) || '0.0'}MB RAM</span>
                <span>{stats?.total_cpu_percent?.toFixed?.(1) || '0.0'}% CPU</span>
              </div>
            </div>

            <div className="process-list">
              {processes && processes.length > 0 ? (
                processes.map((proc) => {
                  const isExpanded = expandedRow === proc.pid;
                  return (
                    <div className="process-item" key={`${proc.pid}-${proc.window_title || proc.name}`}>
                      <div className="process-row" onClick={() => setExpandedRow(isExpanded ? null : proc.pid)}>
                        <div className="row-content">
                          <div className="col-name">
                            <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                            <span className="process-icon">{getProcessIcon(proc.name)}</span>
                            <div className="name-info">
                              <strong>{proc.name}</strong>
                              {proc.window_title && (
                                <small className="window-title-preview">
                                  {proc.window_title.substring(0, 80)}{proc.window_title.length > 80 ? '...' : ''}
                                </small>
                              )}
                            </div>
                          </div>

                          <div className="col-category">
                            <span className={`category-badge cat-${toClassSuffix(proc.category || 'neutral')}`}>
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

                      {isExpanded && (
                        <div className="process-details">
                          <div className="details-grid">
                            <div className="detail-item">
                              <span className="detail-label">PID</span>
                              <span className="detail-value">{proc.pid}</span>
                            </div>

                            {proc.window_title && (
                              <div className="detail-item">
                                <span className="detail-label">Window</span>
                                <span className="detail-value">{proc.window_title}</span>
                              </div>
                            )}

                            {proc.domain && (
                              <div className="detail-item">
                                <span className="detail-label">Domain</span>
                                <span className="detail-value">
                                  <a href={`https://${proc.domain}`} target="_blank" rel="noopener noreferrer" className="domain-link">
                                    {proc.domain}
                                  </a>
                                </span>
                              </div>
                            )}

                            {proc.categorization_source && (
                              <div className="detail-item">
                                <span className="detail-label">Source</span>
                                <span className={`source-badge src-${toClassSuffix(proc.categorization_source)}`}>
                                  {proc.categorization_source}
                                </span>
                              </div>
                            )}

                            {proc.domain_confidence !== undefined && (
                              <div className="detail-item">
                                <span className="detail-label">Confidence</span>
                                <span className="detail-value">{(proc.domain_confidence * 100).toFixed(0)}%</span>
                              </div>
                            )}

                            {proc.url && (
                              <div className="detail-item full-width">
                                <span className="detail-label">URL</span>
                                <span className="detail-value">
                                  <a href={proc.url} target="_blank" rel="noopener noreferrer" className="url-link">
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
        </main>

        <aside className="rail-column">
          <article className="panel rail-card">
            <h3>Session Status</h3>
            <ul>
              <li><span>Connection</span><strong className={isConnected ? 'good' : 'bad'}>{isConnected ? 'Online' : 'Offline'}</strong></li>
              <li><span>Last Update</span><strong>{lastUpdated}</strong></li>
              <li><span>Tracked Apps</span><strong>{processes?.length || 0}</strong></li>
              <li><span>Productive Threshold</span><strong>{model.streak.threshold}m/day</strong></li>
            </ul>
          </article>

          <article className="panel rail-card">
            <h3>Focus Signals</h3>
            <div className="signal-list">
              {topFocusSignals.map((signal) => (
                <div className="signal-item" key={signal.key}>
                  <div>
                    <strong>{categoryLabel[signal.key]}</strong>
                    <p>{formatMinutes(signal.activeMinutes)} active</p>
                  </div>
                  <span className={signal.weighted >= 0 ? 'good' : 'bad'}>{signal.weighted.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="panel rail-card">
            <h3>Category Performance</h3>
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
        </aside>
      </div>

      <footer className="footer-row">
        <span>Last updated: {lastUpdated}</span>
        <span>Refresh: {intervalSeconds}s</span>
      </footer>
    </div>
  );
}
