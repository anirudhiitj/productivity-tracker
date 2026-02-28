/**
 * Electron Main Process
 * Manages the application lifecycle, creates windows, and handles Python backend
 */

import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import path from 'path';
import http from 'http';
import fs from 'fs';
import { spawn, execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow;
let pythonProcess = null;
const isDev = process.env.NODE_ENV === 'development';
let BACKEND_PORT = 8000;  // Will be updated after finding free port
let BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
let appLogFile = null;
let backendLogFile = null;

// Determine paths for production vs development
const RESOURCES_PATH = isDev ? path.join(__dirname, '..') : process.resourcesPath;
const BACKEND_EXE_PATH = path.join(RESOURCES_PATH, 'python-backend', 'tracker-backend.exe');

function safeString(value) {
  if (value === undefined || value === null) return '';
  return String(value);
}

/**
 * Find an available port by attempting to bind to ports starting from basePort
 * Returns a promise that resolves with the free port number
 */
function findAvailablePort(basePort = 8000, maxAttempts = 10) {
  return new Promise((resolve, reject) => {
    const attempt = (portToTry, attemptsRemaining) => {
      if (attemptsRemaining <= 0) {
        reject(new Error(`Could not find available port after trying ports ${basePort}-${basePort + maxAttempts - 1}`));
        return;
      }

      const server = http.createServer();
      server.once('error', (err) => {
        if (err.code === 'EADDRINUSE') {
          // Port is in use, try next
          setImmediate(() => attempt(portToTry + 1, attemptsRemaining - 1));
        } else {
          reject(err);
        }
      });
      server.once('listening', () => {
        server.close(() => {
          resolve(portToTry);
        });
      });
      server.listen(portToTry, '127.0.0.1');
    };

    attempt(basePort, maxAttempts);
  });
}

function writeLog(level, message, details = '') {
  const timestamp = new Date().toISOString();
  const line = `[${timestamp}] [${level}] ${message}${details ? `\n${details}` : ''}\n`;
  const printer = level === 'ERROR' ? console.error : console.log;
  printer(line.trim());
  if (!appLogFile) return;
  try {
    fs.appendFileSync(appLogFile, line, 'utf8');
  } catch (_error) {
    // Ignore log write failures
  }
}

function setupLogging() {
  try {
    const userDataPath = app.getPath('userData');
    const logDir = path.join(userDataPath, 'logs');
    fs.mkdirSync(logDir, { recursive: true });
    appLogFile = path.join(logDir, 'electron-main.log');
    backendLogFile = path.join(logDir, 'backend.log');
    writeLog('INFO', 'Logging initialized', `appLogFile=${appLogFile}\nbackendLogFile=${backendLogFile}`);
  } catch (error) {
    console.error('[App] Failed to initialize logging', error);
  }
}

function waitForBackend(retries = 40) {
  return new Promise((resolve, reject) => {
    const attempt = (remaining) => {
      if (!pythonProcess) {
        reject(new Error('Backend process is not running'));
        return;
      }

      if (pythonProcess.exitCode !== null) {
        reject(new Error(`Backend process exited early with code ${pythonProcess.exitCode}`));
        return;
      }

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
  return findAvailablePort(8000, 10).then((availablePort) => {
    return new Promise((resolve, reject) => {
      // Update global port variables
      BACKEND_PORT = availablePort;
      BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
      
      writeLog('INFO', 'Starting Python backend', `isDev=${isDev}, port=${BACKEND_PORT}`);

      try {
        if (!isDev && !fs.existsSync(BACKEND_EXE_PATH)) {
          const error = new Error(`Backend executable not found at: ${BACKEND_EXE_PATH}`);
          writeLog('ERROR', 'Missing backend executable', safeString(error.stack || error.message));
          reject(error);
          return;
        }

        if (isDev) {
          pythonProcess = spawn('python', [
            'server.py'
          ], {
            cwd: RESOURCES_PATH,
            stdio: ['ignore', 'pipe', 'pipe'],
            env: {
              ...process.env,
              TRACKER_BACKEND_PORT: String(BACKEND_PORT),
              TRACKER_LOG_FILE: backendLogFile || ''
            }
          });
        } else {
          pythonProcess = spawn(BACKEND_EXE_PATH, [], {
            stdio: ['ignore', 'pipe', 'pipe'],
            windowsHide: true,
            env: {
              ...process.env,
              TRACKER_BACKEND_PORT: String(BACKEND_PORT),
              TRACKER_LOG_FILE: backendLogFile || ''
            }
          });
        }

        writeLog('INFO', 'Backend process spawned', `pid=${pythonProcess.pid || 'unknown'}`);

        pythonProcess.stdout.on('data', (data) => {
          writeLog('INFO', '[Backend stdout]', safeString(data));
        });

        pythonProcess.stderr.on('data', (data) => {
          writeLog('ERROR', '[Backend stderr]', safeString(data));
        });

        pythonProcess.on('error', (error) => {
          writeLog('ERROR', 'Backend failed to start', safeString(error.stack || error.message));
          reject(error);
        });

        pythonProcess.on('close', (code) => {
          writeLog('ERROR', 'Backend process exited', `code=${code}`);
          pythonProcess = null;
        });

        waitForBackend().then(() => {
          writeLog('INFO', 'Backend is ready', BACKEND_URL);
          resolve();
        }).catch((error) => {
          writeLog('ERROR', 'Backend healthcheck failed', safeString(error.stack || error.message));
          reject(error);
        });
      } catch (error) {
        writeLog('ERROR', 'Failed to spawn backend', safeString(error.stack || error.message));
        reject(error);
      }
    });
  }).catch((error) => {
    writeLog('ERROR', 'Failed to find available port', safeString(error.stack || error.message));
    return Promise.reject(error);
  });
}

/**
 * Stop the Python backend
 */
function stopPythonBackend() {
  if (pythonProcess) {
    writeLog('INFO', 'Stopping Python backend', `pid=${pythonProcess.pid}`);
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
  writeLog('INFO', 'Creating main window');

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
    writeLog('INFO', 'Window ready to show');
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
    setupLogging();
    writeLog('INFO', 'Initializing application', `resourcesPath=${RESOURCES_PATH}\nbackendExePath=${BACKEND_EXE_PATH}`);
    
    // Start Python backend first
    await startPythonBackend();
    
    // Then create window
    await createWindow();
    
    writeLog('INFO', 'Application initialized successfully');
  } catch (error) {
    const message = safeString(error && (error.stack || error.message || error));
    writeLog('ERROR', 'Application failed to initialize', message);
    await dialog.showErrorBox(
      'Productivity Tracker failed to start',
      `The app could not start correctly.\n\nCheck logs:\n${appLogFile || 'electron-main.log'}\n${backendLogFile || 'backend.log'}\n\nError:\n${message}`
    );
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
  writeLog('ERROR', 'Uncaught exception', safeString(error && (error.stack || error.message || error)));
});

process.on('unhandledRejection', (error) => {
  writeLog('ERROR', 'Unhandled rejection', safeString(error && (error.stack || error.message || error)));
});
