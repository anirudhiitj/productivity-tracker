# 🚀 Deployment Guide - Ship Your App to Users

## Quick Options Overview

| Option | Target | Effort | Best For |
|--------|--------|--------|----------|
| **Electron App** | Windows/Mac/Linux | Medium | Desktop users |
| **Website** | Browser (any device) | Low | Web access |
| **Portable .exe** | Windows only | Medium | Single-file distribution |
| **Installer (.msi/.dmg)** | Windows/Mac | High | Professional distribution |

---

## 🎯 Option 1: ELECTRON APP (Recommended for Desktop)

### Why Electron?
- Single codebase runs on Windows, Mac, Linux
- Users download `.exe` / `.dmg` / `.AppImage` and run it
- Auto-updater support
- No need for users to install Python/Node

### Step 1: Install Electron Dependencies

```bash
cd frontend
npm install electron electron-builder --save-dev
npm install concurrently cross-env --save-dev
```

### Step 2: Create Electron Main Process

Create `frontend/public/main.js`:

```javascript
const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = require('electron-is-dev');

let mainWindow;
let backendProcess;

// Start backend server
function startBackend() {
  const backendPath = path.join(__dirname, '../../backend');
  
  if (isDev) {
    // In development, Python is already running
    console.log('Development mode: connect to existing backend');
  } else {
    // In production, bundle Python executable
    const pythonExe = path.join(process.resourcesPath, 'backend', 'python.exe'); // Windows
    // or path.join(process.resourcesPath, 'backend', 'python') // Mac/Linux
    
    backendProcess = spawn(pythonExe, ['-m', 'uvicorn', 'backend.main:app', '--port', '8000']);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png')
  });

  const startUrl = isDev
    ? 'http://localhost:3000' // Dev server
    : `file://${path.join(__dirname, '../dist/index.html')}`; // Production build

  mainWindow.loadURL(startUrl);

  if (isDev) mainWindow.webDevTools.openDevTools();

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', () => {
  startBackend();
  setTimeout(createWindow, 2000); // Wait for backend to start
});

app.on('window-all-closed', () => {
  // Kill backend process
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) createWindow();
});

// Create app menu
const createMenu = () => {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' }
      ]
    }
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
};

app.on('ready', createMenu);
```

### Step 3: Update package.json (frontend)

Add these scripts and build config:

```json
{
  "scripts": {
    "react-dev": "vite --host 127.0.0.1 --port 3000",
    "react-build": "vite build",
    "electron-dev": "electron .",
    "electron-start": "concurrently \"npm run react-dev\" \"wait-on http://localhost:3000 && npm run electron-dev\"",
    "electron-build": "npm run react-build && electron-builder",
    "dist": "npm run electron-build"
  },
  "main": "public/main.js",
  "homepage": "./",
  "build": {
    "appId": "com.productivity-tracker.app",
    "productName": "FocusRank Productivity Tracker",
    "files": [
      "dist/**/*",
      "public/main.js",
      "public/preload.js",
      "public/icon.png",
      "node_modules/**/*"
    ],
    "directories": {
      "buildResources": "public"
    },
    "win": {
      "target": ["nsis", "portable"]
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    },
    "mac": {
      "target": ["dmg", "zip"]
    },
    "linux": {
      "target": ["AppImage", "deb"]
    }
  }
}
```

### Step 4: Build & Package

```bash
# Build for current platform
npm run dist

# Build for Windows
npm run dist -- -w

# Build for Mac
npm run dist -- -m

# Build for Linux
npm run dist -- -l

# All platforms
npm run dist -- -wml
```

**Output:** `frontend/dist_electron/` folder with `.exe`, `.dmg`, `.AppImage` files

---

## 🌐 Option 2: WEBSITE DEPLOYMENT (Easy, Free Tier Available)

### Backend Deployment (Render/Railway)

**Using Render (easiest):**

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: productivity-tracker-backend
    runtime: python
    startCommand: "python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
```

2. Push to GitHub: `git push`
3. Connect GitHub repo to Render dashboard
4. Deploy

**Backend will be at:** `https://yourapp-backend.onrender.com`

### Frontend Deployment (Vercel/Netlify)

**Using Vercel (simplest for React):**

1. Install Vercel CLI: `npm install -g vercel`
2. In frontend directory: `vercel`
3. Follow prompts
4. Add environment variable:
   - `REACT_APP_API_URL=https://yourapp-backend.onrender.com`

**Frontend will be at:** `https://yourapp.vercel.app`

### Update Frontend API Endpoint

In `frontend/src/services/api.js`:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

---

## 📦 Option 3: SINGLE EXECUTABLE (.exe)

### Use PyInstaller to Bundle Everything

```bash
pip install pyinstaller

# Create single executable with embedded backend
pyinstaller --onefile \
  --windowed \
  --add-data "backend:backend" \
  --add-data "frontend/dist:frontend/dist" \
  --collect-all fastapi \
  --collect-all uvicorn \
  launcher.py
```

**Output:** `dist/launcher.exe` (single file users can run!)

---

## 🚀 RECOMMENDED DEPLOYMENT PATH

### For Most Users:
1. **Start with Electron** - Ship desktop app via GitHub releases
2. **Add website** - Optional web access via Vercel + Render

### Step-by-Step:

```bash
# 1. Build Electron app
cd frontend
npm install electron electron-builder concurrently cross-env --save-dev
npm run dist

# 2. Upload to GitHub Releases
# - Commit code
# - Create release tag
# - Upload .exe file from dist_electron/

# 3. Users download .exe and run it
```

---

## 📱 Option 4: APK (Android)

Use **React Native** or **Expo** to rebuild for Android:

```bash
npx create-expo-app productivity-tracker-mobile
cd productivity-tracker-mobile
npm install
# Rebuild UI components for mobile
expo build:android
```

This requires significant UI rework (not recommended unless you want mobile-first experience).

---

## 💡 DEPLOYMENT COMPARISON

### Timeline to Market:
- **Electron**: 2-3 hours (fastest way to ship)
- **Website**: 30 minutes (if backend ready)
- **Installer**: 4-5 hours (professional setup)
- **APK**: 1-2 days (requires redesign)

### Cost to Users:
- **Electron**: $0 (download .exe once)
- **Website**: $0 (use free tiers: Vercel + Render)
- **Both**: Users have choice

---

## 🔧 QUICK START: ELECTRON IN 5 MINUTES

```bash
# From frontend folder
npm install electron electron-builder concurrently --save-dev

# Copy this main.js to frontend/public/main.js (see above)

# Build React first
npm run build

# Create dist folder for electron
npm run dist

# Gives you ready-to-ship .exe files!
```

---

## 📊 WHAT I RECOMMEND FOR YOU

**Best approach:** Electron app + Optional website

**Why:**
- ✅ Desktop users get native app experience
- ✅ Single .exe file download
- ✅ Auto-update capability
- ✅ Works offline (no wait for web load)
- ✅ Can later add web version for remote users

**Then after:** Add website deployment for users who prefer browser access

---

## NEXT STEPS

1. **Ready to build Electron version?** I can set it up for you
2. **Ready to deploy website?** I'll create GitHub Actions CI/CD
3. **Want both?** I'll do Electron + website in one go

Let me know which path you want! 🚀
