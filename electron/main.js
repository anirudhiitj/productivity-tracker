/**
 * Electron Main Process
 * Manages the application lifecycle, creates windows, and handles Python backend
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const http = require('http');
const { spawn, execSync } = require('child_process');

let mainWindow;
let pythonProcess = null;
const isDev = process.env.NODE_ENV === 'development';
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

// Determine paths for production vs development
const RESOURCES_PATH = isDev ? path.join(__dirname, '..') : process.resourcesPath;
const BACKEND_EXE_PATH = path.join(RESOURCES_PATH, 'python-backend', 'tracker-backend.exe');

function waitForBackend(retries = 40) {
  return new Promise((resolve, reject) => {
    const attempt = (remaining) => {
      const req = http.get(`${BACKEND_URL}/api/health`, (res) => {
        res.resume();
        resolve();
      });
      req.on('error', () => {
        if (remaining <= 0) {
          reject(new Error('Backend did not become ready in time'));
          return;
        }
        setTimeout(() => attempt(remaining - 1), 500);
      });
      req.setTimeout(1000, () => req.destroy());
    };
    attempt(retries);
  });
}

/**
 * Start the FastAPI backend server
 */
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    console.log('[Backend] Starting Python backend...');
    console.log('[Backend] Dev mode:', isDev);

    try {
      if (isDev) {
        pythonProcess = spawn('python', [
          'server.py'
        ], {
          cwd: RESOURCES_PATH,
          stdio: ['ignore', 'pipe', 'pipe'],
          env: {
            ...process.env,
            TRACKER_BACKEND_PORT: String(BACKEND_PORT)
          }
        });
      } else {
        pythonProcess = spawn(BACKEND_EXE_PATH, [], {
          stdio: ['ignore', 'pipe', 'pipe'],
          windowsHide: true,
          env: {
            ...process.env,
            TRACKER_BACKEND_PORT: String(BACKEND_PORT)
          }
        });
      }

      pythonProcess.stdout.on('data', (data) => {
        console.log(`[Backend] ${data.toString()}`);
      });

      pythonProcess.stderr.on('data', (data) => {
        console.error(`[Backend Error] ${data.toString()}`);
      });

      pythonProcess.on('error', (error) => {
        console.error('[Backend] Failed to start:', error);
        reject(error);
      });

      pythonProcess.on('close', (code) => {
        console.log(`[Backend] Process exited with code ${code}`);
        pythonProcess = null;
      });

      waitForBackend().then(() => {
        console.log('[Backend] Backend is ready');
        resolve();
      }).catch((error) => {
        reject(error);
      });

    } catch (error) {
      console.error('[Backend] Error starting backend:', error);
      reject(error);
    }
  });
}

/**
 * Stop the Python backend
 */
function stopPythonBackend() {
  if (pythonProcess) {
    console.log('[Backend] Stopping Python backend...');
    if (process.platform === 'win32') {
      try {
        execSync(`taskkill /pid ${pythonProcess.pid} /t /f`);
      } catch (_error) {
        pythonProcess.kill();
      }
    } else {
      pythonProcess.kill();
    }
    pythonProcess = null;
  }
}

/**
 * Create the main application window
 */
async function createWindow() {
  console.log('[App] Creating main window...');

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    },
    icon: path.join(__dirname, 'icon.png'), // Add your icon
    title: 'Productivity Tracker',
    backgroundColor: '#1a1a1a',
    show: false // Don't show until ready
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    console.log('[App] Window ready to show');
    mainWindow.show();
  });

  // Load the app
  if (isDev) {
    // Development: Load from Vite dev server
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    // Production: Load from built files
    mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * Initialize the application
 */
async function initializeApp() {
  try {
    console.log('[App] Initializing application...');
    
    // Start Python backend first
    await startPythonBackend();
    
    // Then create window
    await createWindow();
    
    console.log('[App] Application initialized successfully');
  } catch (error) {
    console.error('[App] Failed to initialize:', error);
    app.quit();
  }
}

/**
 * App Events
 */

app.whenReady().then(initializeApp);

app.on('window-all-closed', () => {
  stopPythonBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  stopPythonBackend();
});

/**
 * IPC Handlers
 */

ipcMain.handle('get-backend-status', async () => {
  return {
    running: pythonProcess !== null,
    port: BACKEND_PORT,
    url: BACKEND_URL
  };
});

ipcMain.handle('restart-backend', async () => {
  stopPythonBackend();
  await new Promise(resolve => setTimeout(resolve, 1000));
  await startPythonBackend();
  return { success: true };
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('[App] Uncaught exception:', error);
});

process.on('unhandledRejection', (error) => {
  console.error('[App] Unhandled rejection:', error);
});
