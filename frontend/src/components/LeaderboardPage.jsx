import React, { useMemo } from 'react';
import './LeaderboardPage.css';

const TIER_INFO = {
  Iron: { color: '#9CA3AF', bg: 'rgba(156, 163, 175, 0.1)' },
  Bronze: { color: '#D97706', bg: 'rgba(217, 119, 6, 0.1)' },
  Silver: { color: '#94A3B8', bg: 'rgba(148, 163, 184, 0.1)' },
  Gold: { color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' },
  Platinum: { color: '#2DD4BF', bg: 'rgba(45, 212, 191, 0.1)' },
  Diamond: { color: '#818CF8', bg: 'rgba(129, 140, 248, 0.1)' },
};

function getTier(percentile) {
  if (percentile >= 97) return 'Diamond';
  if (percentile >= 88) return 'Platinum';
  if (percentile >= 70) return 'Gold';
  if (percentile >= 45) return 'Silver';
  if (percentile >= 25) return 'Bronze';
  return 'Iron';
}

export function LeaderboardPage({ model }) {
  const leaderboard = model?.leaderboard || [];
  const cohortSize = model?.cohortSize || 250;
  const yourRank = model?.rank || '-';
  const yourTier = model?.tier || 'Iron';
  const yourScore = model?.score || 0;
  const yourPercentile = model?.percentile || 0;

  // Tier distribution
  const tierDist = useMemo(() => {
    const dist = { Iron: 0, Bronze: 0, Silver: 0, Gold: 0, Platinum: 0, Diamond: 0 };
    leaderboard.forEach(entry => {
      const pct = ((cohortSize - entry.rank + 1) / cohortSize) * 100;
      const tier = getTier(pct);
      dist[tier] = (dist[tier] || 0) + 1;
    });
    // Estimate full cohort distribution
    return Object.entries(TIER_INFO).map(([name, info]) => {
      const estimated = name === 'Diamond' ? Math.round(cohortSize * 0.03)
        : name === 'Platinum' ? Math.round(cohortSize * 0.09)
          : name === 'Gold' ? Math.round(cohortSize * 0.18)
            : name === 'Silver' ? Math.round(cohortSize * 0.25)
              : name === 'Bronze' ? Math.round(cohortSize * 0.20)
                : Math.round(cohortSize * 0.25);
      return { name, ...info, count: estimated };
    });
  }, [leaderboard, cohortSize]);

  const maxTierCount = Math.max(...tierDist.map(t => t.count));

  return (
    <div className="leaderboard-page">
      {/* Your Position Card */}
      <div className="your-position card">
        <div className="yp-left">
          <span className="yp-eyebrow">YOUR POSITION</span>
          <div className="yp-rank">
            <span className="yp-hash">#</span>
            <span className="yp-number">{yourRank}</span>
            <span className="yp-of">of {cohortSize}</span>
          </div>
        </div>
        <div className="yp-stats">
          <div className="yp-stat">
            <span className="yp-stat-label">Score</span>
            <span className="yp-stat-value">{yourScore.toFixed(2)}</span>
          </div>
          <div className="yp-stat">
            <span className="yp-stat-label">Tier</span>
            <span className="yp-stat-value" style={{ color: TIER_INFO[yourTier]?.color }}>
              {yourTier}
            </span>
          </div>
          <div className="yp-stat">
            <span className="yp-stat-label">Percentile</span>
            <span className="yp-stat-value">{yourPercentile.toFixed(1)}%</span>
          </div>
          <div className="yp-stat">
            <span className="yp-stat-label">Top</span>
            <span className="yp-stat-value">{model?.topPercent || 0}%</span>
          </div>
        </div>
      </div>

      <div className="lb-layout">
        {/* Main Table */}
        <div className="lb-table-section card">
          <div className="lb-table-header">
            <h3>Rankings</h3>
            <span className="lb-table-count">{leaderboard.length} visible</span>
          </div>
          <div className="lb-table">
            <div className="lb-head-row">
              <span className="lbc-rank">Rank</span>
              <span className="lbc-user">User</span>
              <span className="lbc-score">Score</span>
              <span className="lbc-tier">Tier</span>
            </div>
            {leaderboard.map((entry) => {
              const pct = ((cohortSize - entry.rank + 1) / cohortSize) * 100;
              const entryTier = entry.isYou ? yourTier : getTier(pct);
              const tierInfo = TIER_INFO[entryTier] || TIER_INFO.Iron;

              return (
                <div className={`lb-data-row ${entry.isYou ? 'lb-you-row' : ''}`} key={entry.id}>
                  <span className="lbc-rank">
                    {entry.rank <= 3 ? (
                      <span className={`rank-medal rank-${entry.rank}`}>
                        {entry.rank === 1 ? '🥇' : entry.rank === 2 ? '🥈' : '🥉'}
                      </span>
                    ) : (
                      <span className="rank-num">#{entry.rank}</span>
                    )}
                  </span>
                  <span className="lbc-user">
                    {entry.isYou ? (
                      <span className="user-you">
                        <span className="you-avatar">Y</span>
                        You
                      </span>
                    ) : (
                      <span className="user-other">{entry.id}</span>
                    )}
                  </span>
                  <span className="lbc-score">{entry.score.toFixed(2)}</span>
                  <span className="lbc-tier">
                    <span
                      className="tier-badge"
                      style={{ color: tierInfo.color, background: tierInfo.bg }}
                    >
                      {entryTier}
                    </span>
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Tier Distribution */}
        <div className="tier-dist-section card">
          <h3>Tier Distribution</h3>
          <p className="tier-dist-sub">Estimated across {cohortSize} users</p>
          <div className="tier-dist-bars">
            {tierDist.map((tier) => (
              <div className="td-row" key={tier.name}>
                <span className="td-name" style={{ color: tier.color }}>{tier.name}</span>
                <div className="td-bar-track">
                  <div
                    className="td-bar-fill"
                    style={{
                      width: `${(tier.count / maxTierCount) * 100}%`,
                      background: tier.color,
                    }}
                  />
                </div>
                <span className="td-count">{tier.count}</span>
              </div>
            ))}
          </div>

          <div className="tier-legend">
            <h4>Tier Requirements</h4>
            <div className="tier-req-list">
              <div className="tier-req"><span style={{ color: TIER_INFO.Diamond.color }}>Diamond</span><span>97th+ percentile</span></div>
              <div className="tier-req"><span style={{ color: TIER_INFO.Platinum.color }}>Platinum</span><span>88th - 97th</span></div>
              <div className="tier-req"><span style={{ color: TIER_INFO.Gold.color }}>Gold</span><span>70th - 88th</span></div>
              <div className="tier-req"><span style={{ color: TIER_INFO.Silver.color }}>Silver</span><span>45th - 70th</span></div>
              <div className="tier-req"><span style={{ color: TIER_INFO.Bronze.color }}>Bronze</span><span>25th - 45th</span></div>
              <div className="tier-req"><span style={{ color: TIER_INFO.Iron.color }}>Iron</span><span>Below 25th</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
