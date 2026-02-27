# Productivity Tracker - Deployment Guide

## 🚀 Building the Desktop Application

This guide will help you build a fully deployable Windows desktop application.

---

## Prerequisites

### 1. Install Node.js Dependencies

```bash
# Install root dependencies (Electron)
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Install Python Dependencies

```bash
# Make sure you're in your conda environment
conda activate base  # or your environment name

# Install PyInstaller for bundling
pip install pyinstaller

# Verify all dependencies
pip install -r requirements.txt
```

---

## 🔧 Development Mode

Run the app in development mode (for testing):

```bash
# Terminal 1: Start backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Start Electron
npm run dev:electron
```

Or use the combined command:
```bash
npm run dev
```

---

## 📦 Building for Production

### Step 1: Build Frontend

```bash
cd frontend
npm run build
cd ..
```

This creates optimized production files in `frontend/dist/`

### Step 2: Build Python Backend

```bash
python build_backend.py
```

This:
- Bundles Python + all dependencies into `backend.exe`
- Creates a standalone executable (~50-80 MB)
- Includes all required data files
- Output: `backend/dist/backend.exe`

### Step 3: Build Electron App

```bash
npm run build:electron
```

This creates:
- **Installer**: `dist/Productivity Tracker-Setup-1.0.0.exe` (~150 MB)
- **Portable**: `dist/Productivity Tracker-Portable-1.0.0.exe` (~150 MB)

---

## 📂 Build Output

After successful build:

```
dist/
├── Productivity Tracker-Setup-1.0.0.exe      # Installer (users run this)
├── Productivity Tracker-Portable-1.0.0.exe   # Portable version (no install needed)
└── win-unpacked/                              # Unpacked version for testing
```

---

## 🎯 Quick Build (All Steps)

```bash
npm run build
```

This runs all build steps automatically:
1. Builds frontend (React + Vite)
2. Bundles backend (Python + PyInstaller)
3. Packages everything with Electron

---

## 📱 Distribution Methods

### Method 1: Direct Download
- Upload `.exe` file to your website
- Users download and run

### Method 2: GitHub Releases
```bash
# Tag and push release
git tag v1.0.0
git push origin v1.0.0

# Upload dist/*.exe to GitHub Releases
```

### Method 3: Auto-Updates (Future)
- Implement electron-updater
- Host update files on server
- App auto-checks for updates

---

## 🧪 Testing the Built App

### Test Portable Version
```bash
cd dist
.\Productivity\ Tracker-Portable-1.0.0.exe
```

### Test Installer
1. Double-click `Productivity Tracker-Setup-1.0.0.exe`
2. Follow installation wizard
3. Check Start Menu for shortcut

---

## 🐛 Troubleshooting

### Backend doesn't start
**Issue**: `backend.exe` not found

**Solution**:
1. Run `python build_backend.py` manually
2. Check `backend/dist/backend.exe` exists
3. Rebuild Electron: `npm run build:electron`

### Frontend not loading
**Issue**: Blank screen in Electron

**Solution**:
1. Check `frontend/dist/` exists and has files
2. Rebuild frontend: `cd frontend && npm run build`
3. Check Electron DevTools (F12) for errors

### Python dependencies missing
**Issue**: Module not found errors

**Solution**:
1. Install missing package: `pip install <package>`
2. Rebuild backend: `python build_backend.py`
3. Rebuild app: `npm run build`

### Electron build fails
**Issue**: electron-builder errors

**Solution**:
1. Clear cache: `rm -rf node_modules dist`
2. Reinstall: `npm install`
3. Rebuild: `npm run build`

---

## 📊 Build Sizes

| Component | Size | Description |
|-----------|------|-------------|
| Frontend (built) | ~2 MB | React + Vite optimized |
| Backend (exe) | ~50-80 MB | Python + FastAPI + dependencies |
| Electron Runtime | ~150 MB | Chromium + Node.js |
| **Total App Size** | **~200-250 MB** | Complete installer |

---

## 🔐 Code Signing (Optional)

For production releases, sign your executable:

```bash
# Install Windows SDK for signtool.exe
# Get a code signing certificate

# Sign the executable
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com "dist/Productivity Tracker-Setup-1.0.0.exe"
```

---

## 📝 Version Management

Update version in 3 places:
1. `package.json` → `"version": "1.0.0"`
2. `frontend/package.json` → `"version": "1.0.0"`
3. `backend/main.py` → `__version__ = "1.0.0"`

---

## 🚢 Release Checklist

- [ ] Update version numbers
- [ ] Test in development mode
- [ ] Build frontend: `cd frontend && npm run build`
- [ ] Build backend: `python build_backend.py`
- [ ] Build Electron: `npm run build:electron`
- [ ] Test portable exe manually
- [ ] Test installer on clean system
- [ ] Create GitHub Release
- [ ] Upload installers
- [ ] Write release notes
- [ ] Update documentation

---

## 🎉 Success!

Your app is now ready for distribution! Users can:
1. Download the installer
2. Double-click to install
3. Run from Start Menu
4. Track their productivity!

---

## 📞 Support

For issues, check:
- Console logs in DevTools (F12)
- Electron main process logs
- Backend logs (if running separately)

---

**Built with**: Electron + React + FastAPI + Python
**Platform**: Windows 10/11 (x64)
**License**: MIT
