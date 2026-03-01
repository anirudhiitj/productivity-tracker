import { app, BrowserWindow, Menu, ipcMain, dialog } from 'electron';
import path from 'path';
import { spawn, execSync } from 'child_process';
import net from 'net';
import http from 'http';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow;
let backendProcess;
const isDev = !app.isPackaged;
let BACKEND_PORT = 8000;
let BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

// ─────────────────────────────────────────────
// Utility: find an available TCP port
// ─────────────────────────────────────────────
function findFreePort(startPort = 8000, maxAttempts = 20) {
  return new Promise((resolve, reject) => {
    const attempt = (portToTry, remaining) => {
      if (remaining <= 0) {
        reject(new Error(`No free port found starting from ${startPort}`));
        return;
      }
      const server = net.createServer();
      server.once('error', () => {
        setImmediate(() => attempt(portToTry + 1, remaining - 1));
      });
      server.once('listening', () => {
        server.close(() => resolve(portToTry));
      });
      server.listen(portToTry, '127.0.0.1');
    };
    attempt(startPort, maxAttempts);
  });
}

// ─────────────────────────────────────────────
// Wait for backend /api/health to respond
// ─────────────────────────────────────────────
function waitForBackend(retries = 60) {
  return new Promise((resolve, reject) => {
    const attempt = (remaining) => {
      if (backendProcess && backendProcess.exitCode !== null) {
        reject(new Error(`Backend exited with code ${backendProcess.exitCode}`));
        return;
      }
      const req = http.get(`${BACKEND_URL}/api/health`, (res) => {
        res.resume();
        if (res.statusCode === 200) {
          resolve();
        } else if (remaining > 0) {
          setTimeout(() => attempt(remaining - 1), 500);
        } else {
          reject(new Error('Backend health check returned non-200'));
        }
      });
      req.on('error', () => {
        if (remaining <= 0) {
          reject(new Error('Backend did not become ready'));
          return;
        }
        setTimeout(() => attempt(remaining - 1), 500);
      });
      req.setTimeout(2000, () => req.destroy());
    };
    attempt(retries);
  });
}

// ─────────────────────────────────────────────
// Start the Python / PyInstaller backend
// ─────────────────────────────────────────────
async function startBackend() {
  try {
    BACKEND_PORT = await findFreePort(8000);
    BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
    console.log(`[ELECTRON] Using port ${BACKEND_PORT}`);

    if (isDev) {
      // In dev assume backend is started separately or start it
      console.log('[ELECTRON] Dev mode – spawning python server.py');
      const projectRoot = path.join(__dirname, '..');
      backendProcess = spawn('python', ['server.py'], {
        cwd: projectRoot,
        stdio: ['ignore', 'pipe', 'pipe'],
        env: { ...process.env, TRACKER_BACKEND_PORT: String(BACKEND_PORT) }
      });
    } else {
      // Production: find the bundled backend exe
      const resourcesPath = process.resourcesPath;
      const exeName = process.platform === 'win32' ? 'tracker-backend.exe' : 'tracker-backend';
      const possiblePaths = [
        path.join(resourcesPath, 'python-backend', exeName),
        path.join(resourcesPath, 'tracker-backend', exeName),
        path.join(path.dirname(process.execPath), 'resources', 'python-backend', exeName)
      ];

      let exePath = null;
      for (const p of possiblePaths) {
        console.log(`[ELECTRON] Checking: ${p}`);
        if (fs.existsSync(p)) { exePath = p; break; }
      }

      if (!exePath) {
        const msg = `Backend not found.\nSearched:\n${possiblePaths.join('\n')}`;
        console.error('[ELECTRON]', msg);
        dialog.showErrorBox('Backend Missing', msg);
        return;
      }

      console.log(`[ELECTRON] Launching ${exePath}`);
      backendProcess = spawn(exePath, [], {
        cwd: path.dirname(exePath),
        stdio: ['ignore', 'pipe', 'pipe'],
        windowsHide: true,
        env: { ...process.env, TRACKER_BACKEND_PORT: String(BACKEND_PORT) }
      });
    }

    // Pipe backend output to Electron console
    if (backendProcess.stdout) backendProcess.stdout.on('data', d => console.log(`[BACKEND] ${d}`));
    if (backendProcess.stderr) backendProcess.stderr.on('data', d => console.error(`[BACKEND] ${d}`));
    backendProcess.on('error', e => console.error('[BACKEND] spawn error', e));
    backendProcess.on('exit', c => { console.log(`[BACKEND] exited ${c}`); backendProcess = null; });

    console.log(`[ELECTRON] Waiting for backend on ${BACKEND_URL} ...`);
    await waitForBackend();
    console.log('[ELECTRON] Backend is ready');
  } catch (err) {
    console.error('[ELECTRON] startBackend failed:', err);
    throw err;
  }
}

// ─────────────────────────────────────────────
// Stop the backend process tree
// ─────────────────────────────────────────────
function stopBackend() {
  if (!backendProcess) return;
  console.log(`[ELECTRON] Stopping backend pid=${backendProcess.pid}`);
  try {
    if (process.platform === 'win32') {
      execSync(`taskkill /pid ${backendProcess.pid} /t /f`, { stdio: 'ignore' });
    } else {
      backendProcess.kill();
    }
  } catch (_) { /* ignore */ }
  backendProcess = null;
}

// ─────────────────────────────────────────────
// Create the BrowserWindow
// ─────────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'),
    title: 'FocusRank',
    backgroundColor: '#1a1a1a',
    show: false
  });

  mainWindow.once('ready-to-show', () => mainWindow.show());

  // Inject the dynamic backend URL into the renderer BEFORE any fetch runs
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.executeJavaScript(`
      window.__BACKEND_URL__ = '${BACKEND_URL}';
      console.log('[INJECT] Backend URL set to', window.__BACKEND_URL__);
    `);
  });

  let startUrl;
  if (isDev) {
    startUrl = 'http://localhost:3000';
    mainWindow.webContents.openDevTools();
  } else {
    const appPath = app.getAppPath();
    const distPath = path.join(appPath, 'dist', 'index.html');
    console.log(`[ELECTRON] Loading ${distPath}`);
    startUrl = `file://${distPath}`;
  }

  mainWindow.loadURL(startUrl);
  mainWindow.on('closed', () => { mainWindow = null; });
}

// ─────────────────────────────────────────────
// Application menu
// ─────────────────────────────────────────────
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        { label: 'Exit', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' }, { role: 'redo' }, { type: 'separator' },
        { role: 'cut' }, { role: 'copy' }, { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' }, { role: 'forceReload' },
        isDev && { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' },
        { type: 'separator' }, { role: 'togglefullscreen' }
      ].filter(Boolean)
    },
    {
      label: 'Help',
      submenu: [{
        label: 'About FocusRank',
        click: () => dialog.showMessageBox(mainWindow, {
          type: 'info', title: 'FocusRank', message: 'FocusRank Productivity Tracker',
          detail: 'Track your focus. Compete. Climb.\n\nVersion 1.0.0'
        })
      }]
    }
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// ─────────────────────────────────────────────
// App lifecycle
// ─────────────────────────────────────────────
app.on('ready', async () => {
  try {
    await startBackend();
    createWindow();
    createMenu();
  } catch (err) {
    console.error('[ELECTRON] Fatal init error:', err);
    dialog.showErrorBox('FocusRank failed to start',
      `Could not start the backend.\n\n${err.message || err}`);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (mainWindow === null) createWindow();
});

app.on('before-quit', () => stopBackend());

// IPC
ipcMain.handle('get-app-version', () => app.getVersion());
ipcMain.handle('get-app-name', () => app.name);
ipcMain.handle('get-backend-status', () => ({
  running: backendProcess !== null,
  port: BACKEND_PORT,
  url: BACKEND_URL
}));

// Crash safety
process.on('uncaughtException', e => console.error('[UNCAUGHT]', e));
process.on('unhandledRejection', e => console.error('[UNHANDLED]', e));
