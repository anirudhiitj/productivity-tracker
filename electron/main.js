/**
 * Electron Main Process
 * Manages the application lifecycle, creates windows, and handles Python backend
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let pythonProcess = null;
const isDev = process.env.NODE_ENV === 'development';
const BACKEND_PORT = 8000;

// Determine paths for production vs development
const RESOURCES_PATH = isDev
  ? path.join(__dirname, '..')
  : process.resourcesPath;

const BACKEND_PATH = isDev
  ? path.join(RESOURCES_PATH, 'backend')
  : path.join(RESOURCES_PATH, 'backend', 'backend.exe');

const PYTHON_PATH = isDev
  ? 'python'  // Use system Python in dev
  : BACKEND_PATH;  // Use bundled exe in production

/**
 * Start the FastAPI backend server
 */
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    console.log('[Backend] Starting Python backend...');
    console.log('[Backend] Path:', PYTHON_PATH);
    console.log('[Backend] Dev mode:', isDev);

    try {
      if (isDev) {
        // Development: Run Python directly
        pythonProcess = spawn('python', [
          '-m', 'uvicorn',
          'backend.main:app',
          '--host', '127.0.0.1',
          '--port', BACKEND_PORT.toString(),
          '--log-level', 'info'
        ], {
          cwd: RESOURCES_PATH,
          stdio: ['ignore', 'pipe', 'pipe']
        });
      } else {
        // Production: Run bundled executable
        pythonProcess = spawn(BACKEND_PATH, [], {
          stdio: ['ignore', 'pipe', 'pipe']
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

      // Wait for backend to be ready
      setTimeout(() => {
        console.log('[Backend] Backend should be ready');
        resolve();
      }, 3000);

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
    pythonProcess.kill();
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
    url: `http://localhost:${BACKEND_PORT}`
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
