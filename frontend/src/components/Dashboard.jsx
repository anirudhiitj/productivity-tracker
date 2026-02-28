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

export function Dashboard({ processes, stats, loading, error, lastUpdated, isConnected, intervalSeconds = 3, theme, onToggleTheme }) {
  const model = useMemo(() => buildDashboardModel(processes, intervalSeconds), [processes, intervalSeconds]);
  const [selectedActivity, setSelectedActivity] = useState(null);

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

      <section className="panel-grid">
        <article className="panel live-panel">
          <h2>Live Activities</h2>
          <p className="panel-sub">Single-expand behavior: one activity detail open at a time.</p>
          <div className="activity-list">
            {liveActivities.length === 0 && <p className="muted">No active browser/app items right now.</p>}
            {liveActivities.map((item, index) => {
              const id = `${item.pid}-${index}`;
              const isOpen = selectedActivity === id;
              return (
                <div className="activity-item" key={id}>
                  <button type="button" className="activity-head" onClick={() => setSelectedActivity(isOpen ? null : id)}>
                    <span>{item.domain || item.name}</span>
                    <span>{isOpen ? '−' : '+'}</span>
                  </button>
                  {isOpen && (
                    <div className="activity-details">
                      <p><strong>Title:</strong> {item.window_title || 'N/A'}</p>
                      <p><strong>Category:</strong> {item.category || 'Neutral'}</p>
                      <p><strong>Memory:</strong> {item.memory_mb?.toFixed?.(1) || 0}MB</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </article>

        <article className="panel mobile-panel">
          <h2>Mobile End-of-Day Sync</h2>
          <p className="panel-sub">Aggregated minutes only, no raw browsing content.</p>
          <pre>{JSON.stringify(model.mobilePayload, null, 2)}</pre>
        </article>
      </section>

      <footer className="footer-row">
        <span>Total processes: {stats?.total_processes ?? processes.length}</span>
        <span>Memory: {stats?.total_memory_mb?.toFixed?.(1) ?? '0.0'}MB</span>
        <span>CPU: {stats?.total_cpu_percent?.toFixed?.(1) ?? '0.0'}%</span>
      </footer>
    </div>
  );
}
