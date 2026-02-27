"""
GETTING STARTED - Productivity Tracker Full Stack
==================================================

Follow these 3 simple steps to see your processes in real-time!
"""

print("""
╔═══════════════════════════════════════════════════════════════════╗
║     🚀 PRODUCTIVITY TRACKER - REAL-TIME PROCESS DASHBOARD 🚀      ║
╚═══════════════════════════════════════════════════════════════════╝

✨ WHAT YOU GET:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📊 A white dashboard displaying all your active processes
  ⚡ Real-time updates every 3 seconds
  🎨 Color-coded categories (Productive, Gaming, etc.)
  💾 Memory and CPU usage per process
  ⏱️  Running time for each process
  🔄 Auto-refresh capability

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 EXAMPLE DASHBOARD:

╔════════════════════════════════════════════════════════════════════╗
║       📊 PRODUCTIVITY TRACKER - Active Processes                   ║
├────────────────────────────────────────────────────────────────────┤
│ 🔄 Last Update: 10:45:30  |  Total: 8 processes                   │
├────────────┬──────────────┬────────────┬──────────┬────────────────┤
│ Process    │ Category     │ Memory     │ CPU %    │ Runtime        │
├────────────┼──────────────┼────────────┼──────────┼────────────────┤
│ chrome.exe │ 🟢 Productive│ 845 MB (6%)│  12.5%   │ 45m 32s        │
│ Valorant   │ 🔴 Gaming    │ 6.2 GB (40%)│ 58.3%   │ 1h 23m         │
│ Code.exe   │ 🟢 Productive│ 524 MB (3%)│  2.1%    │ 5h 45m         │
│ Spotify    │ 🟠 Entertain │ 312 MB (2%)│  0.8%    │ 2h 10m         │
│ Discord    │ 🟠 Entertain │ 289 MB (1%)│  1.5%    │ 3h 20m         │
└────────────┴──────────────┴────────────┴──────────┴────────────────┘
╚════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 STEP 1: QUICKEST START (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

On Windows:
  1. Double-click: launch.bat

  OR in PowerShell/CMD:
  $ python launcher.py

That's it! The launcher will:
  • Check all dependencies ✓
  • Start the Backend (FastAPI) on port 8000
  • Start the Frontend (React) on port 3000
  • Open your browser automatically


🌐 STEP 2: OPEN YOUR BROWSER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Once launchers report success, visit:

  http://localhost:3000  ← Your Dashboard

You should see your processes loading in real-time!


🔌 STEP 3: API DOCUMENTATION (Optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To see the API documentation:

  http://localhost:8000/docs  ← Swagger UI

Try the endpoints directly from your browser!


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS & TRICKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ Dashboard shows processes using > 100MB RAM or > 1% CPU
  ✓ System processes (dwm.exe, svchost.exe) are automatically hidden
  ✓ Refresh rate is 3 seconds (can be customized)
  ✓ All colors and thresholds are customizable
  ✓ Both terminals can stay open while you work


⚠️  TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: "Cannot connect to backend"
→ Make sure launcher.py is still running without errors
→ Check terminal for error messages

Problem: "Port 8000 already in use"
→ Another process is using that port
→ Find it: netstat -ano | findstr :8000
→ Kill it: taskkill /PID <PID> /F

Problem: "npm not found"
→ Node.js isn't installed
→ Download from: https://nodejs.org/
→ Make sure to add to PATH during installation

Problem: No processes showing
→ Your processes might use < 100MB RAM and < 1% CPU
→ Try: http://localhost:8000/api/processes/all (shows everything)
→ Edit thresholds in backend/process_monitor.py


📚 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Read these files for more info:

  • README.md  ← Overview of entire project
  • FULLSTACK_README.md  ← Complete full-stack guide
  • IMPLEMENTATION_SUMMARY.md  ← What was built
  • QUICKSTART.py  ← Interactive setup (python QUICKSTART.py)


🎯 WHAT HAPPENS UNDER THE HOOD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Your browser loads http://localhost:3000 (React)

2. React makes a request: GET http://localhost:8000/api/processes/main

3. FastAPI backend:
   - Uses psutil to scan all Windows processes
   - Filters by: Memory > 100MB OR CPU > 1%
   - Gets category from CategoryEngine
   - Returns JSON data

4. React renders the table with live process data

5. Repeats every 3 seconds for real-time updates


🔧 CUSTOMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Want to adjust something? Easy!

Change Memory Threshold (100MB → 50MB):
  File: backend/process_monitor.py
  Line: MIN_MEMORY_MB = 50

Change Refresh Rate (3s → 5s):
  File: frontend/src/App.jsx
  Find: }, 3000);
  Change to: }, 5000);

Change Colors:
  File: frontend/src/components/ProcessTable.jsx
  Find: CATEGORY_COLORS = {...}
  Customize the hex colors


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ CATEGORY COLORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🟢 Productive (Green)          - VS Code, GitHub, Slack, Docs
  🔴 Gaming (Red)                - Valorant, Steam, Fortnite
  🔵 Educational (Blue)          - Udemy, Coursera, Wikipedia
  🟠 Entertainment (Orange)      - YouTube, Netflix, Discord
  ⚫ Neutral (Gray)              - Everything else


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎓 EXAMPLE PROCESSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

These WILL show on dashboard:
  ✅ Chrome (1-2 GB)
  ✅ Valorant (4-8 GB, high CPU)
  ✅ Spotify (200-400 MB)
  ✅ VSCode (300-600 MB)
  ✅ Discord (250-400 MB)
  ✅ Slack (300-500 MB)
  ✅ Firefox (800MB-2GB)
  ✅ YouTube (heavy streaming)

These WON'T show (filtered out):
  ❌ explorer.exe (50 MB)
  ❌ svchost.exe (40 MB)
  ❌ dwm.exe (Desktop Window Manager, 80 MB)
  ❌ SearchIndexer.exe (40 MB)
  ❌ conhost.exe (10 MB)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 READY TO START?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Just run:

  python launcher.py

Then open: http://localhost:3000

That's all! Enjoy your real-time process dashboard! 🚀


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions? Check the docs:
  • FULLSTACK_README.md - Complete reference
  • IMPLEMENTATION_SUMMARY.md - What was built
  • http://localhost:8000/docs - API docs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
