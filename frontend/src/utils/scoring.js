const WEIGHTS = {
  CP: 1.2,
  DEV: 1.0,
  EDU: 0.8,
  SOC: -0.6,
  ENT: -0.8
};

const DEFAULT_TOTALS = { CP: 0, DEV: 0, EDU: 0, SOC: 0, ENT: 0 };
const STORAGE_KEY = 'pt_daily_attention_v1';
const OBSERVATION_VARIANCE = 1.0;
const PRIOR_MEAN = 0;
const PRIOR_VARIANCE = 4;
const STREAK_MINUTES = 60;

const CP_HINTS = ['leetcode', 'codeforces', 'codechef', 'hackerrank', 'atcoder', 'hackerearth', 'kattis'];
const DEV_HINTS = ['github', 'gitlab', 'bitbucket', 'stackoverflow', 'docs', 'visual studio code', 'vscode', 'pycharm', 'intellij', 'cursor'];
const EDU_HINTS = ['course', 'tutorial', 'lecture', 'learn', 'education', 'campusx', 'documentation'];
const SOC_HINTS = ['twitter', 'x.com', 'instagram', 'facebook', 'linkedin', 'reddit', 'discord', 'whatsapp'];
const ENT_HINTS = ['youtube', 'netflix', 'primevideo', 'hotstar', 'spotify', 'twitch'];

function seededRandom(seed) {
  let state = seed;
  return () => {
    state = (state * 1664525 + 1013904223) % 4294967296;
    return state / 4294967296;
  };
}

function safeParseStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

function persistStorage(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

function classifyProcess(process) {
  const processName = (process.name || '').toLowerCase();
  const title = (process.window_title || '').toLowerCase();
  const domain = (process.domain || '').toLowerCase();
  const category = (process.category || '').toLowerCase();
  const text = `${processName} ${title} ${domain} ${category}`;

  if (CP_HINTS.some((hint) => text.includes(hint))) return 'CP';
  if (SOC_HINTS.some((hint) => text.includes(hint))) return 'SOC';

  const hasEntHint = ENT_HINTS.some((hint) => text.includes(hint));
  const hasEduHint = EDU_HINTS.some((hint) => text.includes(hint));

  if (hasEntHint && !hasEduHint) return 'ENT';
  if (hasEduHint) return 'EDU';
  if (DEV_HINTS.some((hint) => text.includes(hint))) return 'DEV';

  if (category === 'productive') return 'DEV';
  if (category === 'educational') return 'EDU';
  if (category === 'entertainment' || category === 'gaming') return 'ENT';

  return null;
}

function addSnapshotToTotals(processes, intervalSeconds) {
  const storage = safeParseStorage();
  const date = todayKey();
  const existing = storage[date] || { ...DEFAULT_TOTALS };
  const activeBuckets = new Set();

  for (const process of processes || []) {
    const bucket = classifyProcess(process);
    if (!bucket) continue;
    activeBuckets.add(bucket);
  }

  const minutesPerCycle = intervalSeconds / 60;
  for (const bucket of activeBuckets) {
    existing[bucket] = (existing[bucket] || 0) + minutesPerCycle;
  }

  storage[date] = existing;
  persistStorage(storage);
  return existing;
}

function attentionComponents(totals) {
  const components = Object.keys(WEIGHTS).map((key) => {
    const activeMinutes = totals[key] || 0;
    const logScaled = Math.log(1 + activeMinutes);
    const weighted = WEIGHTS[key] * logScaled;
    return { key, activeMinutes, logScaled, weighted, weight: WEIGHTS[key] };
  });

  const score = components.reduce((sum, item) => sum + item.weighted, 0);
  return { components, score };
}

function buildSkillFromHistory(historyMap) {
  const days = Object.keys(historyMap).sort();
  let mu = PRIOR_MEAN;
  let variance = PRIOR_VARIANCE;

  for (const day of days) {
    const totals = historyMap[day] || DEFAULT_TOTALS;
    const { score } = attentionComponents(totals);

    const nextMu = (OBSERVATION_VARIANCE * mu + variance * score) / (OBSERVATION_VARIANCE + variance);
    const nextVariance = (OBSERVATION_VARIANCE * variance) / (OBSERVATION_VARIANCE + variance);
    mu = nextMu;
    variance = nextVariance;
  }

  const sigma = Math.sqrt(variance);
  const conservative = mu - 2 * sigma;

  return { mu, sigma, conservative, variance, samples: days.length };
}

function computeStreak(historyMap) {
  const days = Object.keys(historyMap).sort().reverse();
  let streak = 0;
  let graceUsed = false;

  for (const day of days) {
    const totals = historyMap[day] || DEFAULT_TOTALS;
    const positiveMinutes = (totals.CP || 0) + (totals.DEV || 0) + (totals.EDU || 0);

    if (positiveMinutes >= STREAK_MINUTES) {
      streak += 1;
      continue;
    }

    if (!graceUsed) {
      graceUsed = true;
      continue;
    }

    break;
  }

  const best = days.reduce((bestValue, day) => {
    const totals = historyMap[day] || DEFAULT_TOTALS;
    const positiveMinutes = (totals.CP || 0) + (totals.DEV || 0) + (totals.EDU || 0);
    return positiveMinutes >= STREAK_MINUTES ? bestValue + 1 : bestValue;
  }, 0);

  return { current: streak, best, threshold: STREAK_MINUTES, graceUsed };
}

function percentileRank(value, population) {
  if (!population.length) return 50;
  const lessOrEqual = population.filter((x) => x <= value).length;
  return (lessOrEqual / population.length) * 100;
}

function pickTier(percentile) {
  if (percentile >= 97) return 'Diamond';
  if (percentile >= 88) return 'Platinum';
  if (percentile >= 70) return 'Gold';
  if (percentile >= 45) return 'Silver';
  if (percentile >= 25) return 'Bronze';
  return 'Iron';
}

function cohortFromUser(userScore, userTotals) {
  const seed = Number(todayKey().replaceAll('-', ''));
  const rand = seededRandom(seed);
  const size = 250;

  const peers = [];
  for (let i = 0; i < size - 1; i += 1) {
    const r = rand();
    const peerScore = Math.max(-5, userScore * (0.55 + r * 1.1) + (rand() - 0.5) * 2.2);
    const spread = 0.45 + rand();
    const peerTotals = {
      CP: Math.max(0, (userTotals.CP || 25) * spread * (0.4 + rand())),
      DEV: Math.max(0, (userTotals.DEV || 25) * spread * (0.4 + rand())),
      EDU: Math.max(0, (userTotals.EDU || 15) * spread * (0.4 + rand())),
      SOC: Math.max(0, (userTotals.SOC || 10) * spread * (0.2 + rand())),
      ENT: Math.max(0, (userTotals.ENT || 10) * spread * (0.2 + rand()))
    };

    peers.push({ id: `user_${i + 1}`, score: peerScore, totals: peerTotals, activeNow: rand() > 0.45 });
  }

  peers.push({ id: 'you', score: userScore, totals: userTotals, activeNow: true, isYou: true });
  peers.sort((a, b) => b.score - a.score);
  peers.forEach((item, index) => {
    item.rank = index + 1;
  });

  return peers;
}

function cosineSimilarity(a, b) {
  const keys = ['CP', 'DEV', 'EDU', 'SOC', 'ENT'];
  let dot = 0;
  let normA = 0;
  let normB = 0;
  keys.forEach((key) => {
    const av = a[key] || 0;
    const bv = b[key] || 0;
    dot += av * bv;
    normA += av * av;
    normB += bv * bv;
  });
  if (!normA || !normB) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

export function buildDashboardModel(processes, intervalSeconds = 3) {
  const todayTotals = addSnapshotToTotals(processes, intervalSeconds);
  const history = safeParseStorage();

  const { components, score } = attentionComponents(todayTotals);
  const skill = buildSkillFromHistory(history);
  const peers = cohortFromUser(score, todayTotals);

  const populationScores = peers.map((x) => x.score);
  const percentile = percentileRank(score, populationScores);
  const tier = pickTier(percentile);

  const you = peers.find((x) => x.isYou) || { rank: peers.length };
  const topPercent = Math.max(1, Math.ceil((you.rank / peers.length) * 100));

  const similarUsers = peers.filter((p) => !p.isYou && cosineSimilarity(p.totals, todayTotals) >= 0.9).length;
  const activeUsers = peers.filter((p) => p.activeNow).length;

  const domainPercentiles = components.map((item) => {
    const bucketValues = peers.map((peer) => peer.totals[item.key] || 0);
    return {
      ...item,
      percentile: percentileRank(item.activeMinutes, bucketValues)
    };
  });

  const streak = computeStreak(history);

  return {
    score,
    components,
    todayTotals,
    skill,
    tier,
    percentile,
    topPercent,
    rank: you.rank,
    cohortSize: peers.length,
    leaderboard: peers.slice(0, 12),
    similarUsers,
    activeUsers,
    domainPercentiles,
    streak,
    mobilePayload: {
      user_id: 'anon_local',
      date: todayKey(),
      totals: {
        CP: Math.round(todayTotals.CP),
        DEV: Math.round(todayTotals.DEV),
        EDU: Math.round(todayTotals.EDU),
        SOC: Math.round(todayTotals.SOC),
        ENT: Math.round(todayTotals.ENT)
      },
      units: 'minutes'
    }
  };
}
