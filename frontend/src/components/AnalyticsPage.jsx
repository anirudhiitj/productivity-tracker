import React, { useMemo } from 'react';
import './AnalyticsPage.css';

const CATEGORY_META = {
  CP: { label: 'Competitive Programming', color: '#8B5CF6', bgColor: 'var(--purple-soft)', icon: '🏆', weight: '+1.2' },
  DEV: { label: 'Development', color: '#3B82F6', bgColor: 'var(--blue-soft)', icon: '💻', weight: '+1.0' },
  EDU: { label: 'Education', color: '#10B981', bgColor: 'var(--green-soft)', icon: '📚', weight: '+0.8' },
  SOC: { label: 'Social Media', color: '#F59E0B', bgColor: 'var(--yellow-soft)', icon: '💬', weight: '-0.6' },
  ENT: { label: 'Entertainment', color: '#EF4444', bgColor: 'var(--red-soft)', icon: '🎬', weight: '-0.8' },
};

const TIER_INFO = {
  Iron: { color: '#9CA3AF', min: 0, max: 25 },
  Bronze: { color: '#D97706', min: 25, max: 45 },
  Silver: { color: '#94A3B8', min: 45, max: 70 },
  Gold: { color: '#F59E0B', min: 70, max: 88 },
  Platinum: { color: '#2DD4BF', min: 88, max: 97 },
  Diamond: { color: '#818CF8', min: 97, max: 100 },
};

export function AnalyticsPage({ model, processes, stats, intervalSeconds }) {
  const totals = model?.todayTotals || {};
  const totalMinutes = Object.values(totals).reduce((s, v) => s + (v || 0), 0) || 1;
  const productiveTotal = (totals.CP || 0) + (totals.DEV || 0) + (totals.EDU || 0);
  const unproductiveTotal = (totals.SOC || 0) + (totals.ENT || 0);

  const categories = useMemo(() =>
    Object.entries(CATEGORY_META).map(([key, meta]) => ({
      key,
      ...meta,
      minutes: totals[key] || 0,
      percent: ((totals[key] || 0) / totalMinutes) * 100,
      logScaled: Math.log(1 + (totals[key] || 0)).toFixed(2),
    })),
    [totals, totalMinutes]
  );

  const maxMinutes = Math.max(...categories.map(c => c.minutes), 1);

  const skillData = model?.skill || { mu: 0, sigma: 1, conservative: 0, samples: 0 };
  const currentTier = model?.tier || 'Iron';
  const percentile = model?.percentile || 0;

  // Build session history from localStorage
  const sessionHistory = useMemo(() => {
    try {
      const raw = localStorage.getItem('pt_daily_attention_v1');
      if (!raw) return [];
      const data = JSON.parse(raw);
      return Object.entries(data).sort(([a], [b]) => a.localeCompare(b)).slice(-7).map(([date, vals]) => ({
        date,
        productive: (vals.CP || 0) + (vals.DEV || 0) + (vals.EDU || 0),
        unproductive: (vals.SOC || 0) + (vals.ENT || 0),
        total: Object.values(vals).reduce((s, v) => s + (v || 0), 0),
      }));
    } catch { return []; }
  }, []);

  const maxHistoryMinutes = Math.max(...sessionHistory.map(d => d.total), 1);

  return (
    <div className="analytics-page">
      {/* Score Overview */}
      <div className="analytics-top">
        <div className="score-card card">
          <div className="score-card-header">
            <h3>Productivity Score</h3>
            <span className="score-formula">S = Σ(wi &middot; ln(1 + ti))</span>
          </div>
          <div className="score-display">
            <div className="score-big">{model?.score?.toFixed(2) || '0.00'}</div>
            <div className="score-breakdown">
              {categories.map((cat) => {
                const contribution = parseFloat(cat.weight) * parseFloat(cat.logScaled);
                return (
                  <div className="score-component" key={cat.key}>
                    <span className="sc-name">
                      <span className="sc-dot" style={{ background: cat.color }} />
                      {cat.key}
                    </span>
                    <span className="sc-calc">{cat.weight} × ln(1+{cat.minutes.toFixed(0)})</span>
                    <span className={`sc-value ${contribution >= 0 ? 'positive' : 'negative'}`}>
                      {contribution >= 0 ? '+' : ''}{contribution.toFixed(2)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="skill-card card">
          <h3>Skill Rating (Bayesian)</h3>
          <div className="skill-display">
            <div className="skill-main">
              <span className="skill-value">{skillData.conservative.toFixed(2)}</span>
              <span className="skill-sub">Ri = μi − 2σi</span>
            </div>
            <div className="skill-params">
              <div className="param"><span>μ (mean)</span><strong>{skillData.mu.toFixed(3)}</strong></div>
              <div className="param"><span>σ (std dev)</span><strong>{skillData.sigma.toFixed(3)}</strong></div>
              <div className="param"><span>Samples</span><strong>{skillData.samples}</strong></div>
            </div>
          </div>
        </div>
      </div>

      {/* Tier Progress */}
      <div className="tier-section card">
        <h3>Tier Progression</h3>
        <div className="tier-track">
          {Object.entries(TIER_INFO).map(([name, info]) => {
            const isActive = name === currentTier;
            const width = info.max - info.min;
            return (
              <div
                className={`tier-segment ${isActive ? 'active' : ''}`}
                key={name}
                style={{ flex: width }}
              >
                <div
                  className="tier-fill"
                  style={{
                    background: info.color,
                    width: isActive ? `${((percentile - info.min) / width) * 100}%` : (percentile > info.max ? '100%' : '0%'),
                  }}
                />
                <span className="tier-name" style={{ color: isActive ? info.color : 'var(--text-tertiary)' }}>
                  {name}
                </span>
              </div>
            );
          })}
        </div>
        <div className="tier-info-row">
          <span>Current: <strong style={{ color: TIER_INFO[currentTier]?.color }}>{currentTier}</strong></span>
          <span>Percentile: <strong>{percentile.toFixed(1)}%</strong></span>
        </div>
      </div>

      {/* Category Deep Dive */}
      <div className="category-section card">
        <h3>Category Analysis</h3>
        <div className="cat-table">
          <div className="cat-table-head">
            <span>Category</span>
            <span>Time</span>
            <span>Weight</span>
            <span>Contribution</span>
            <span className="cat-bar-col">Distribution</span>
          </div>
          {categories.map((cat) => {
            const contribution = parseFloat(cat.weight) * parseFloat(cat.logScaled);
            return (
              <div className="cat-table-row" key={cat.key}>
                <span className="cat-cell-name">
                  <span className="cat-cell-icon" style={{ background: cat.bgColor }}>{cat.icon}</span>
                  <span>{cat.label}</span>
                </span>
                <span className="cat-cell-time">{cat.minutes.toFixed(1)}m</span>
                <span className="cat-cell-weight">{cat.weight}</span>
                <span className={`cat-cell-contribution ${contribution >= 0 ? 'positive' : 'negative'}`}>
                  {contribution >= 0 ? '+' : ''}{contribution.toFixed(2)}
                </span>
                <span className="cat-cell-bar">
                  <div className="cat-bar-track">
                    <div
                      className="cat-bar-fill"
                      style={{
                        width: `${(cat.minutes / maxMinutes) * 100}%`,
                        background: cat.color,
                      }}
                    />
                  </div>
                  <span className="cat-bar-pct">{cat.percent.toFixed(0)}%</span>
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Session History */}
      <div className="history-section card">
        <h3>Session History (Last 7 days)</h3>
        {sessionHistory.length > 0 ? (
          <div className="history-chart">
            {sessionHistory.map((day) => (
              <div className="history-bar-group" key={day.date}>
                <div className="history-bar-stack" style={{ height: '140px' }}>
                  <div
                    className="hbar productive"
                    style={{ height: `${(day.productive / maxHistoryMinutes) * 100}%` }}
                    title={`Productive: ${day.productive.toFixed(0)}m`}
                  />
                  <div
                    className="hbar unproductive"
                    style={{ height: `${(day.unproductive / maxHistoryMinutes) * 100}%` }}
                    title={`Unproductive: ${day.unproductive.toFixed(0)}m`}
                  />
                </div>
                <span className="history-label">{day.date.slice(5)}</span>
                <span className="history-total">{day.total.toFixed(0)}m</span>
              </div>
            ))}
            <div className="history-legend">
              <span className="legend-item"><span className="legend-dot productive" />Productive</span>
              <span className="legend-item"><span className="legend-dot unproductive" />Leisure</span>
            </div>
          </div>
        ) : (
          <p className="empty-text">No history data yet. Keep tracking to see your trends!</p>
        )}
      </div>

      {/* Summary Stats */}
      <div className="summary-row">
        <div className="summary-stat card">
          <span className="summary-label">Total Tracked Time</span>
          <span className="summary-value">{totalMinutes.toFixed(0)}m</span>
        </div>
        <div className="summary-stat card">
          <span className="summary-label">Productive Time</span>
          <span className="summary-value positive">{productiveTotal.toFixed(1)}m</span>
        </div>
        <div className="summary-stat card">
          <span className="summary-label">Unproductive Time</span>
          <span className="summary-value negative">{unproductiveTotal.toFixed(1)}m</span>
        </div>
        <div className="summary-stat card">
          <span className="summary-label">Focus Ratio</span>
          <span className="summary-value">{((productiveTotal / Math.max(1, totalMinutes)) * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
}
