import React, { useState, useMemo } from 'react';
import './ProcessesPage.css';

const getProcessIcon = (name) => {
  const n = (name || '').toLowerCase();
  if (n.includes('chrome') || n.includes('firefox') || n.includes('edge') || n.includes('brave')) return '🌐';
  if (n.includes('code') || n.includes('studio') || n.includes('cursor')) return '💻';
  if (n.includes('discord') || n.includes('slack') || n.includes('teams')) return '💬';
  if (n.includes('spotify') || n.includes('music')) return '🎵';
  if (n.includes('game') || n.includes('valorant') || n.includes('steam')) return '🎮';
  if (n.includes('python') || n.includes('node')) return '🐍';
  if (n.includes('terminal') || n.includes('powershell') || n.includes('cmd')) return '⌨️';
  if (n.includes('explorer') || n.includes('finder')) return '📁';
  return '⚙️';
};

const formatTime = (seconds) => {
  if (!seconds || seconds < 0) return '0s';
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  if (m < 60) return `${m}m`;
  return `${Math.floor(m / 60)}h ${m % 60}m`;
};

const SORT_OPTIONS = [
  { key: 'memory', label: 'Memory' },
  { key: 'cpu', label: 'CPU' },
  { key: 'runtime', label: 'Runtime' },
  { key: 'name', label: 'Name' },
];

export function ProcessesPage({ processes, stats, loading, error }) {
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('memory');
  const [sortDir, setSortDir] = useState('desc');
  const [expandedPid, setExpandedPid] = useState(null);

  const sorted = useMemo(() => {
    let list = [...(processes || [])];

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(p =>
        (p.name || '').toLowerCase().includes(q) ||
        (p.window_title || '').toLowerCase().includes(q) ||
        (p.domain || '').toLowerCase().includes(q) ||
        (p.category || '').toLowerCase().includes(q)
      );
    }

    list.sort((a, b) => {
      let cmp = 0;
      switch (sortBy) {
        case 'memory': cmp = (a.memory_mb || 0) - (b.memory_mb || 0); break;
        case 'cpu': cmp = (a.cpu_percent || 0) - (b.cpu_percent || 0); break;
        case 'runtime': cmp = (a.runtime_seconds || 0) - (b.runtime_seconds || 0); break;
        case 'name': cmp = (a.name || '').localeCompare(b.name || ''); break;
        default: cmp = 0;
      }
      return sortDir === 'desc' ? -cmp : cmp;
    });

    return list;
  }, [processes, search, sortBy, sortDir]);

  const handleSort = (key) => {
    if (sortBy === key) {
      setSortDir(prev => prev === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(key);
      setSortDir('desc');
    }
  };

  if (error) {
    return <div className="proc-error"><p>Unable to load process data. Check backend connection.</p></div>;
  }

  return (
    <div className="processes-page">
      {/* Stats Bar */}
      <div className="proc-stats-bar">
        <div className="stat-chip">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/></svg>
          <span><strong>{processes?.length || 0}</strong> processes</span>
        </div>
        <div className="stat-chip">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          <span><strong>{stats?.total_cpu_percent?.toFixed(1) || '0.0'}%</strong> CPU</span>
        </div>
        <div className="stat-chip">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="6" width="20" height="12" rx="2"/><line x1="6" y1="12" x2="6" y2="12"/></svg>
          <span><strong>{stats?.total_memory_mb?.toFixed(0) || '0'}</strong> MB RAM</span>
        </div>
      </div>

      {/* Search + Sort */}
      <div className="proc-toolbar">
        <div className="proc-search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            type="text"
            placeholder="Filter processes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && <button className="clear-btn" onClick={() => setSearch('')}>&times;</button>}
        </div>
        <div className="sort-group">
          <span className="sort-label">Sort:</span>
          {SORT_OPTIONS.map((opt) => (
            <button
              key={opt.key}
              className={`sort-btn ${sortBy === opt.key ? 'active' : ''}`}
              onClick={() => handleSort(opt.key)}
            >
              {opt.label}
              {sortBy === opt.key && (
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
                  style={{ transform: sortDir === 'asc' ? 'rotate(180deg)' : 'none' }}>
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Count */}
      <div className="proc-count">{sorted.length} {sorted.length === 1 ? 'result' : 'results'}</div>

      {/* Process List */}
      <div className="proc-list">
        {loading && sorted.length === 0 ? (
          <div className="proc-loading"><div className="spinner" /><p>Loading processes...</p></div>
        ) : sorted.length === 0 ? (
          <div className="proc-empty"><p>No processes match your search.</p></div>
        ) : (
          /* Table header */
          <>
            <div className="proc-table-head">
              <span className="ptc-name">Application</span>
              <span className="ptc-cat">Category</span>
              <span className="ptc-mem">Memory</span>
              <span className="ptc-cpu">CPU</span>
              <span className="ptc-time">Runtime</span>
            </div>
            {sorted.map((proc, i) => {
              const isExpanded = expandedPid === `${proc.pid}-${i}`;
              const cpuHigh = (proc.cpu_percent || 0) > 10;
              return (
                <div className={`proc-card ${isExpanded ? 'expanded' : ''}`} key={`${proc.pid}-${i}`}>
                  <button
                    className="proc-card-row"
                    onClick={() => setExpandedPid(isExpanded ? null : `${proc.pid}-${i}`)}
                  >
                    <span className="ptc-name">
                      <span className="proc-expand-icon">{isExpanded ? '▾' : '▸'}</span>
                      <span className="proc-emoji">{getProcessIcon(proc.name)}</span>
                      <span className="proc-name-text">
                        <strong>{proc.name}</strong>
                        {proc.window_title && (
                          <small>{proc.window_title.length > 60 ? proc.window_title.substring(0, 60) + '...' : proc.window_title}</small>
                        )}
                      </span>
                    </span>
                    <span className="ptc-cat">
                      <span className={`proc-cat-badge badge-${(proc.category || 'neutral').toLowerCase()}`}>
                        {proc.category || 'Neutral'}
                      </span>
                    </span>
                    <span className="ptc-mem">
                      <span className="mem-primary">{proc.memory_mb?.toFixed(0) || 0} MB</span>
                      <span className="mem-secondary">{proc.memory_percent?.toFixed(2) || 0}%</span>
                    </span>
                    <span className={`ptc-cpu ${cpuHigh ? 'cpu-high' : ''}`}>
                      {proc.cpu_percent?.toFixed(1) || '0.0'}%
                    </span>
                    <span className="ptc-time">{formatTime(proc.runtime_seconds || 0)}</span>
                  </button>

                  {isExpanded && (
                    <div className="proc-details">
                      <div className="proc-detail-grid">
                        <div className="pd-item">
                          <span className="pd-label">PID</span>
                          <span className="pd-value mono">{proc.pid}</span>
                        </div>
                        <div className="pd-item">
                          <span className="pd-label">User</span>
                          <span className="pd-value">{proc.username || 'N/A'}</span>
                        </div>
                        <div className="pd-item">
                          <span className="pd-label">CPU Usage</span>
                          <span className="pd-value">{proc.cpu_percent?.toFixed(2) || 0}%</span>
                        </div>
                        <div className="pd-item">
                          <span className="pd-label">Memory</span>
                          <span className="pd-value">{proc.memory_mb?.toFixed(1) || 0} MB ({proc.memory_percent?.toFixed(2) || 0}%)</span>
                        </div>
                        {proc.window_title && (
                          <div className="pd-item wide">
                            <span className="pd-label">Window Title</span>
                            <span className="pd-value">{proc.window_title}</span>
                          </div>
                        )}
                        {proc.domain && (
                          <div className="pd-item">
                            <span className="pd-label">Domain</span>
                            <a href={`https://${proc.domain}`} target="_blank" rel="noopener noreferrer" className="pd-link">
                              {proc.domain}
                            </a>
                          </div>
                        )}
                        {proc.url && (
                          <div className="pd-item wide">
                            <span className="pd-label">Full URL</span>
                            <a href={proc.url} target="_blank" rel="noopener noreferrer" className="pd-link mono">
                              {proc.url.length > 90 ? proc.url.substring(0, 90) + '...' : proc.url}
                            </a>
                          </div>
                        )}
                        {proc.categorization_source && (
                          <div className="pd-item">
                            <span className="pd-label">Categorization Source</span>
                            <span className={`pd-source src-${(proc.categorization_source || '').toLowerCase()}`}>
                              {proc.categorization_source}
                            </span>
                          </div>
                        )}
                        {proc.domain_confidence !== undefined && proc.domain_confidence > 0 && (
                          <div className="pd-item">
                            <span className="pd-label">Confidence</span>
                            <div className="pd-confidence">
                              <div className="pd-conf-bar">
                                <div className="pd-conf-fill" style={{ width: `${proc.domain_confidence * 100}%` }} />
                              </div>
                              <span>{(proc.domain_confidence * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
}
