import React, { useMemo } from 'react';
import './OverviewPage.css';

const TIER_COLORS = {
  Iron: '#9CA3AF', Bronze: '#D97706', Silver: '#94A3B8',
  Gold: '#F59E0B', Platinum: '#2DD4BF', Diamond: '#818CF8'
};

const CATEGORY_META = {
  CP: { label: 'Competitive Programming', color: '#8B5CF6', icon: '🏆' },
  DEV: { label: 'Development', color: '#3B82F6', icon: '💻' },
  EDU: { label: 'Education', color: '#10B981', icon: '📚' },
  SOC: { label: 'Social Media', color: '#F59E0B', icon: '💬' },
  ENT: { label: 'Entertainment', color: '#EF4444', icon: '🎬' },
};

const formatTime = (seconds) => {
  if (!seconds || seconds < 0) return '0s';
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  if (m < 60) return `${m}m`;
  return `${Math.floor(m / 60)}h ${m % 60}m`;
};

const getProcessIcon = (name) => {
  const n = (name || '').toLowerCase();
  if (n.includes('chrome') || n.includes('firefox') || n.includes('edge') || n.includes('brave')) return '🌐';
  if (n.includes('code') || n.includes('studio') || n.includes('cursor')) return '💻';
  if (n.includes('discord') || n.includes('slack') || n.includes('teams')) return '💬';
  if (n.includes('spotify') || n.includes('music')) return '🎵';
  if (n.includes('game') || n.includes('valorant') || n.includes('steam')) return '🎮';
  if (n.includes('python') || n.includes('node') || n.includes('java')) return '🐍';
  if (n.includes('terminal') || n.includes('powershell') || n.includes('cmd')) return '⌨️';
  return '⚙️';
};

export function OverviewPage({ processes, stats, loading, error, isConnected, lastUpdated, model, intervalSeconds }) {
  const topActivities = useMemo(() =>
    (processes || []).filter(p => p.window_title || p.domain).slice(0, 6),
    [processes]
  );

  const categoryTotals = useMemo(() => {
    const totals = model?.todayTotals || {};
    const total = Object.values(totals).reduce((s, v) => s + (v || 0), 0) || 1;
    return Object.entries(CATEGORY_META).map(([key, meta]) => ({
      key,
      ...meta,
      minutes: totals[key] || 0,
      percent: ((totals[key] || 0) / total) * 100,
    }));
  }, [model]);

  const productiveMinutes = useMemo(() => {
    const t = model?.todayTotals || {};
    return (t.CP || 0) + (t.DEV || 0) + (t.EDU || 0);
  }, [model]);

  const unproductiveMinutes = useMemo(() => {
    const t = model?.todayTotals || {};
    return (t.SOC || 0) + (t.ENT || 0);
  }, [model]);

  if (error) {
    return (
      <div className="error-state">
        <div className="error-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <h2>Connection Failed</h2>
        <p>Unable to reach backend server. Ensure it's running on localhost:8000</p>
      </div>
    );
  }

  if (loading && (!processes || processes.length === 0)) {
    return (
      <div className="loading-state">
        <div className="spinner" />
        <p>Loading productivity data...</p>
      </div>
    );
  }

  const scorePercent = Math.min(100, Math.max(0, ((model?.score || 0) + 5) / 10 * 100));

  return (
    <div className="overview">
      {/* Hero Row */}
      <div className="hero-row">
        <div className="hero-card card">
          <div className="hero-left">
            <span className="hero-eyebrow">PRODUCTIVITY RANK</span>
            <h2 className="hero-title">
              Top <span className="hero-highlight">{model?.topPercent || 0}%</span> this session
            </h2>
            <p className="hero-desc">
              Score {model?.score?.toFixed(2) || '0.00'} &middot; Conservative {model?.skill?.conservative?.toFixed(2) || '0.00'}
            </p>
          </div>
          <div className="hero-gauge">
            <svg viewBox="0 0 120 120" className="gauge-svg">
              <circle cx="60" cy="60" r="52" fill="none" stroke="var(--border-primary)" strokeWidth="8" />
              <circle
                cx="60" cy="60" r="52"
                fill="none"
                stroke="var(--accent)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${scorePercent * 3.27} 327`}
                transform="rotate(-90 60 60)"
                style={{ transition: 'stroke-dasharray 0.8s ease' }}
              />
            </svg>
            <div className="gauge-value">
              <span className="gauge-number">{model?.score?.toFixed(1) || '0.0'}</span>
              <span className="gauge-label">Score</span>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="kpi-row">
        <div className="kpi card">
          <div className="kpi-header">
            <span className="kpi-icon" style={{ background: 'var(--accent-soft)', color: 'var(--accent)' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            </span>
            <span className="kpi-label">Tier</span>
          </div>
          <p className="kpi-value" style={{ color: TIER_COLORS[model?.tier] || 'var(--text-primary)' }}>
            {model?.tier || 'Iron'}
          </p>
          <span className="kpi-sub">{model?.percentile?.toFixed(0) || 0}th percentile</span>
        </div>

        <div className="kpi card">
          <div className="kpi-header">
            <span className="kpi-icon" style={{ background: 'var(--green-soft)', color: 'var(--green)' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </span>
            <span className="kpi-label">Streak</span>
          </div>
          <p className="kpi-value">{model?.streak?.current || 0}<small>d</small></p>
          <span className="kpi-sub">Best: {model?.streak?.best || 0} days</span>
        </div>

        <div className="kpi card">
          <div className="kpi-header">
            <span className="kpi-icon" style={{ background: 'var(--blue-soft)', color: 'var(--blue)' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            </span>
            <span className="kpi-label">Active Windows</span>
          </div>
          <p className="kpi-value">{processes?.length || 0}</p>
          <span className="kpi-sub">{stats?.total_cpu_percent?.toFixed(1) || 0}% CPU &middot; {stats?.total_memory_mb?.toFixed(0) || 0}MB</span>
        </div>

        <div className="kpi card">
          <div className="kpi-header">
            <span className="kpi-icon" style={{ background: 'var(--purple-soft)', color: 'var(--purple)' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </span>
            <span className="kpi-label">Community</span>
          </div>
          <p className="kpi-value">{model?.activeUsers || 0}</p>
          <span className="kpi-sub">{model?.similarUsers || 0} similar profiles</span>
        </div>
      </div>

      {/* Middle Row: Time Split + Categories */}
      <div className="mid-row">
        <div className="time-split card">
          <div className="card-header">
            <h3>Time Distribution</h3>
            <span className="card-badge">{(productiveMinutes + unproductiveMinutes).toFixed(0)}m total</span>
          </div>
          <div className="time-bars">
            <div className="time-bar-group">
              <div className="time-bar-label">
                <span className="time-dot productive" />
                <span>Productive</span>
                <strong>{productiveMinutes.toFixed(1)}m</strong>
              </div>
              <div className="time-bar-track">
                <div className="time-bar-fill productive" style={{ width: `${Math.min(100, (productiveMinutes / Math.max(1, productiveMinutes + unproductiveMinutes)) * 100)}%` }} />
              </div>
            </div>
            <div className="time-bar-group">
              <div className="time-bar-label">
                <span className="time-dot unproductive" />
                <span>Unproductive</span>
                <strong>{unproductiveMinutes.toFixed(1)}m</strong>
              </div>
              <div className="time-bar-track">
                <div className="time-bar-fill unproductive" style={{ width: `${Math.min(100, (unproductiveMinutes / Math.max(1, productiveMinutes + unproductiveMinutes)) * 100)}%` }} />
              </div>
            </div>
          </div>
          <div className="time-ratio">
            <div className="ratio-bar">
              <div className="ratio-segment productive" style={{ flex: Math.max(0.05, productiveMinutes) }} />
              <div className="ratio-segment unproductive" style={{ flex: Math.max(0.05, unproductiveMinutes) }} />
            </div>
            <div className="ratio-labels">
              <span>{((productiveMinutes / Math.max(1, productiveMinutes + unproductiveMinutes)) * 100).toFixed(0)}% focused</span>
              <span>{((unproductiveMinutes / Math.max(1, productiveMinutes + unproductiveMinutes)) * 100).toFixed(0)}% leisure</span>
            </div>
          </div>
        </div>

        <div className="categories card">
          <div className="card-header">
            <h3>Category Breakdown</h3>
          </div>
          <div className="category-bars">
            {categoryTotals.map((cat) => (
              <div className="cat-row" key={cat.key}>
                <div className="cat-info">
                  <span className="cat-icon">{cat.icon}</span>
                  <span className="cat-name">{cat.label}</span>
                  <span className="cat-time">{cat.minutes.toFixed(1)}m</span>
                </div>
                <div className="cat-track">
                  <div
                    className="cat-fill"
                    style={{ width: `${Math.min(100, cat.percent)}%`, background: cat.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row: Activity + Leaderboard */}
      <div className="bottom-row">
        <div className="recent-activity card">
          <div className="card-header">
            <h3>Active Windows</h3>
            <span className="card-badge live-badge">
              <span className="live-dot" />
              Live
            </span>
          </div>
          <div className="activity-list">
            {topActivities.length > 0 ? topActivities.map((act, i) => (
              <div className="activity-row" key={`${act.pid}-${i}`}>
                <span className="act-icon">{getProcessIcon(act.name)}</span>
                <div className="act-info">
                  <strong>{act.name}</strong>
                  <p>{act.window_title || act.domain || 'No title'}</p>
                </div>
                <div className="act-meta">
                  <span className={`mini-badge badge-${(act.category || 'neutral').toLowerCase()}`}>
                    {act.category || 'Neutral'}
                  </span>
                  <small>{formatTime(act.runtime_seconds || 0)}</small>
                </div>
              </div>
            )) : (
              <p className="empty-text">No active windows detected.</p>
            )}
          </div>
        </div>

        <div className="quick-leaderboard card">
          <div className="card-header">
            <h3>Leaderboard</h3>
            <span className="card-badge">#{model?.rank || '-'}</span>
          </div>
          <div className="lb-list">
            {(model?.leaderboard || []).slice(0, 8).map((entry) => (
              <div className={`lb-row ${entry.isYou ? 'lb-you' : ''}`} key={entry.id}>
                <span className="lb-rank">#{entry.rank}</span>
                <span className="lb-name">{entry.isYou ? 'You' : entry.id}</span>
                <span className="lb-score">{entry.score.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
