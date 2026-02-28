import React, { useMemo, useState } from 'react';
import './ActivityPage.css';

const getProcessIcon = (name) => {
  const n = (name || '').toLowerCase();
  if (n.includes('chrome') || n.includes('firefox') || n.includes('edge') || n.includes('brave')) return '🌐';
  if (n.includes('code') || n.includes('studio') || n.includes('cursor')) return '💻';
  if (n.includes('discord') || n.includes('slack') || n.includes('teams')) return '💬';
  if (n.includes('spotify') || n.includes('music')) return '🎵';
  if (n.includes('game') || n.includes('valorant') || n.includes('steam')) return '🎮';
  if (n.includes('python') || n.includes('node')) return '🐍';
  if (n.includes('terminal') || n.includes('powershell') || n.includes('cmd')) return '⌨️';
  return '⚙️';
};

const formatTime = (seconds) => {
  if (!seconds || seconds < 0) return '0s';
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  if (m < 60) return `${m}m ${seconds % 60}s`;
  return `${Math.floor(m / 60)}h ${m % 60}m`;
};

const FILTER_OPTIONS = [
  { key: 'all', label: 'All' },
  { key: 'Productive', label: 'Productive' },
  { key: 'Educational', label: 'Educational' },
  { key: 'Entertainment', label: 'Entertainment' },
  { key: 'Gaming', label: 'Gaming' },
  { key: 'Neutral', label: 'Neutral' },
];

export function ActivityPage({ processes, loading, error }) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [expandedId, setExpandedId] = useState(null);

  const filtered = useMemo(() => {
    let list = (processes || []).filter(p => p.window_title || p.domain);
    if (filter !== 'all') {
      list = list.filter(p => (p.category || 'Neutral') === filter);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(p =>
        (p.name || '').toLowerCase().includes(q) ||
        (p.window_title || '').toLowerCase().includes(q) ||
        (p.domain || '').toLowerCase().includes(q)
      );
    }
    return list;
  }, [processes, filter, search]);

  if (error) {
    return <div className="activity-error"><p>Unable to load activity data.</p></div>;
  }

  return (
    <div className="activity-page">
      <div className="activity-toolbar">
        <div className="search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Search windows, domains, apps..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button className="search-clear" onClick={() => setSearch('')}>&times;</button>
          )}
        </div>
        <div className="filter-pills">
          {FILTER_OPTIONS.map((opt) => (
            <button
              key={opt.key}
              className={`filter-pill ${filter === opt.key ? 'active' : ''}`}
              onClick={() => setFilter(opt.key)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="activity-count">
        <span>{filtered.length} active {filtered.length === 1 ? 'window' : 'windows'}</span>
      </div>

      <div className="activity-feed">
        {loading && filtered.length === 0 ? (
          <div className="activity-loading">
            <div className="spinner" />
            <p>Scanning active windows...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="activity-empty">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="1.5">
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <p>No matching activities found.</p>
          </div>
        ) : (
          filtered.map((proc, i) => {
            const isExpanded = expandedId === `${proc.pid}-${i}`;
            return (
              <div
                className={`activity-card card ${isExpanded ? 'expanded' : ''}`}
                key={`${proc.pid}-${i}`}
              >
                <button
                  className="activity-card-head"
                  onClick={() => setExpandedId(isExpanded ? null : `${proc.pid}-${i}`)}
                >
                  <div className="ac-left">
                    <span className="ac-icon">{getProcessIcon(proc.name)}</span>
                    <div className="ac-text">
                      <strong>{proc.name}</strong>
                      <p>{proc.window_title || proc.domain || 'No title available'}</p>
                    </div>
                  </div>
                  <div className="ac-right">
                    <span className={`ac-badge badge-${(proc.category || 'neutral').toLowerCase()}`}>
                      {proc.category || 'Neutral'}
                    </span>
                    <span className="ac-runtime">{formatTime(proc.runtime_seconds || 0)}</span>
                    <svg className={`ac-chevron ${isExpanded ? 'open' : ''}`} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </div>
                </button>

                {isExpanded && (
                  <div className="activity-card-body">
                    <div className="detail-grid">
                      <div className="detail-cell">
                        <span className="detail-label">PID</span>
                        <span className="detail-value mono">{proc.pid}</span>
                      </div>
                      <div className="detail-cell">
                        <span className="detail-label">CPU</span>
                        <span className="detail-value">{proc.cpu_percent?.toFixed(2) || 0}%</span>
                      </div>
                      <div className="detail-cell">
                        <span className="detail-label">Memory</span>
                        <span className="detail-value">{proc.memory_mb?.toFixed(1) || 0} MB</span>
                      </div>
                      <div className="detail-cell">
                        <span className="detail-label">Runtime</span>
                        <span className="detail-value">{formatTime(proc.runtime_seconds || 0)}</span>
                      </div>
                      {proc.domain && (
                        <div className="detail-cell wide">
                          <span className="detail-label">Domain</span>
                          <a href={`https://${proc.domain}`} target="_blank" rel="noopener noreferrer" className="detail-link">
                            {proc.domain}
                          </a>
                        </div>
                      )}
                      {proc.window_title && (
                        <div className="detail-cell wide">
                          <span className="detail-label">Window Title</span>
                          <span className="detail-value">{proc.window_title}</span>
                        </div>
                      )}
                      {proc.url && (
                        <div className="detail-cell wide">
                          <span className="detail-label">URL</span>
                          <a href={proc.url} target="_blank" rel="noopener noreferrer" className="detail-link mono">
                            {proc.url.length > 80 ? proc.url.substring(0, 80) + '...' : proc.url}
                          </a>
                        </div>
                      )}
                      {proc.categorization_source && (
                        <div className="detail-cell">
                          <span className="detail-label">Source</span>
                          <span className={`source-tag src-${(proc.categorization_source || '').toLowerCase()}`}>
                            {proc.categorization_source}
                          </span>
                        </div>
                      )}
                      {proc.domain_confidence !== undefined && (
                        <div className="detail-cell">
                          <span className="detail-label">Confidence</span>
                          <div className="confidence-bar-wrap">
                            <div className="confidence-bar" style={{ width: `${(proc.domain_confidence * 100)}%` }} />
                            <span>{(proc.domain_confidence * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
