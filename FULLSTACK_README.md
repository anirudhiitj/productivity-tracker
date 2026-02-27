# Productivity Tracker - Full Stack Setup

## 🎯 Overview

Complete Python + FastAPI + React application for real-time process monitoring on Windows.

**Features:**
- 📊 Real-time system process monitoring
- 🎨 White UI displaying active processes with resource usage
- 📈 Process categorization (Productive, Gaming, Educational, Entertainment, Neutral)
- 🔄 Auto-refresh every 3 seconds
- 📱 Responsive design
- ⚡ Fast, lightweight backend (FastAPI)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              React Frontend (Port 3000)                  │
│           displays process table in white UI             │
└─────────────────────────────────┬───────────────────────┘
                                  │ HTTP/REST API
                                  │ (localhost:8000)
┌─────────────────────────────────▼───────────────────────┐
│           FastAPI Backend (Port 8000)                    │
│  ├─ GET /api/processes/main - filtered processes         │
│  ├─ GET /api/processes/all - all processes             │
│  ├─ GET /api/processes/stats - memory/CPU stats        │
│  └─ GET /api/processes/category/{cat} - by category    │
└─────────────────────────────────┬───────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────┐
│            ProcessMonitor (Windows API)                  │
│  ├─ psutil - real-time process data                     │
│  ├─ CategoryEngine - activity categorization            │
│  └─ WindowTitleParser - browser domain extraction       │
└──────────────────────────────────────────────────────────┘
```

## 📋 Requirements

### System Requirements
- Windows 10/11
- Python 3.10+
- Node.js 16+ (for frontend)
- npm (comes with Node.js)

### Python Dependencies
See `requirements.txt` - automatically installed via pip

### Node Dependencies
See `frontend/package.json` - automatically installed via npm

## 🚀 Quick Start

### Option 1: Unified Launcher (Recommended)

This starts both backend and frontend automatically:

```bash
python launcher.py
```

The launcher will:
1. Check Python dependencies (install if missing)
2. Start FastAPI backend on port 8000
3. Install npm packages if needed
4. Start React frontend on port 3000
5. Open API docs and display URLs

Then visit: **http://localhost:3000**

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then visit: **http://localhost:3000**

## 📊 Dashboard

### Main Process Filtering
Displays processes that meet **ANY** of:
- Memory > 100 MB
- CPU > 1%
- Excludes system processes (svchost, dwm, etc.)

### Displayed Columns
| Column | Description |
|--------|-------------|
| **Process Name** | Executable name (chrome.exe, Code.exe, etc.) |
| **Category** | Activity type (Productive, Gaming, etc.) |
| **Memory** | RAM usage in MB and percentage |
| **CPU %** | CPU usage percentage |
| **Runtime** | Time process has been running |
| **User** | Windows user running the process |

### Category Colors
| Category | Color |
|----------|-------|
| Productive | 🟢 Green (#10b981) |
| Gaming | 🔴 Red (#ef4444) |
| Educational | 🔵 Blue (#3b82f6) |
| Entertainment | 🟠 Orange (#f97316) |
| Neutral | ⚫ Gray (#9ca3af) |

## 🔌 API Endpoints

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-02-28T10:45:30.123456",
  "service": "productivity_tracker_backend"
}
```

### `GET /api/processes/main`
Get filtered main processes (100MB+ RAM or 1%+ CPU).

**Response:**
```json
{
  "timestamp": "2026-02-28T10:45:30.123456",
  "processes": [
    {
      "pid": 5432,
      "name": "chrome.exe",
      "memory_mb": 845.5,
      "memory_percent": 6.2,
      "cpu_percent": 12.5,
      "category": "Productive",
      "runtime_seconds": 2732,
      "user": "Admin"
    }
  ],
  "stats": {
    "total_processes": 8,
    "total_memory_mb": 3421.2,
    "total_cpu_percent": 42.8
  }
}
```

### `GET /api/processes/all`
Get ALL running processes (200+ results).

### `GET /api/processes/stats`
Get aggregate statistics only.

### `GET /api/processes/category/{category}`
Filter by category: `Productive`, `Gaming`, `Educational`, `Entertainment`, `Neutral`

## 📁 Project Structure

```
productivity_tracker/
├── backend/
│   ├── main.py                    # FastAPI app entry
│   ├── process_monitor.py         # Core process monitoring logic
│   ├── routers/
│   │   └── processes.py           # API endpoints
│   └── __init__.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main React component
│   │   ├── App.css                # Global styles
│   │   ├── components/
│   │   │   ├── ProcessTable.jsx   # Process table component
│   │   │   └── ProcessTable.css   # Table styles
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   ├── index.js               # React entry
│   │   ├── index.css              # Base styles
│   ├── public/
│   │   └── index.html             # HTML template
│   ├── package.json               # npm dependencies
│   ├── vite.config.js             # Vite build config
│   └── .gitignore
│
├── client/                        # Original codebase (unchanged)
│   ├── agent.py
│   ├── process_tracker.py
│   ├── category_engine.py
│   ├── window_parser.py
│   └── ...
│
├── launcher.py                    # Unified launcher script
├── requirements.txt               # Python dependencies
└── README.md
```

## 🔧 Configuration

### Process Thresholds (Backend)
Edit `backend/process_monitor.py`:
```python
MIN_MEMORY_MB = 100  # Minimum RAM for main processes
MIN_CPU_PERCENT = 1.0  # Minimum CPU for main processes
```

### Refresh Interval (Frontend)
Edit `frontend/src/App.jsx`:
```javascript
const interval = setInterval(() => {
  fetchProcesses();
}, 3000);  // Refresh every 3 seconds
```

### Category Colors (Frontend)
Edit `frontend/src/components/ProcessTable.jsx`:
```javascript
const CATEGORY_COLORS = {
  'Productive': '#10b981',
  'Gaming': '#ef4444',
  ...
}
```

## 🐛 Troubleshooting

### "Failed to connect to backend"
- Make sure FastAPI backend is running on port 8000
- Check: `http://localhost:8000/docs`
- Backend logs should show if it started

### "npm not found"
- Install Node.js: https://nodejs.org/
- Restart terminal after installation

### "Port 8000 already in use"
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### "Port 3000 already in use"
Frontend will try next available port (3001, 3002, etc).

### Process list is empty
- Your processes may be using < 100MB RAM and < 1% CPU
- Check `http://localhost:8000/api/processes/all` for all processes
- Lower thresholds in `ProcessMonitor` if needed

## 📊 Features Explained

### Real-Time Updates
Frontend polls backend every 3 seconds for fresh data. No WebSocket needed for simplicity.

### Process Categorization
Uses existing `CategoryEngine` from original codebase to classify:
- **Productive**: VS Code, GitHub, Slack, Google Docs
- **Gaming**: Valorant, Steam, CS:GO, Fortnite
- **Educational**: Udemy, Coursera, Khan Academy
- **Entertainment**: YouTube, Netflix, Spotify, Discord
- **Neutral**: Everything else

### Memory Calculation
- Shows absolute MB and percentage of total system RAM
- %CPU from psutil (averaged over polling interval)

## 🚀 Future Enhancements

- [ ] WebSocket for true real-time updates (no polling)
- [ ] Historical charts (time spent per app)
- [ ] Multi-machine monitoring (network sync)
- [ ] Notifications/alerts on app usage
- [ ] Process blocking/limiting features
- [ ] Dark mode toggle
- [ ] Export data to CSV/JSON

## 📜 License

Part of Productivity Tracker system. See main README.md

## 📞 Support

For issues or questions:
1. Check logs in both backend and frontend terminals
2. Visit API docs: `http://localhost:8000/docs`
3. Check browser console (F12 in frontend)
