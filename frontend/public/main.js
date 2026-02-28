const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;
const isDev = !app.isPackaged;

// Utility to find free port
async function findFreePort(startPort = 8000) {
  const net = require('net');
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(startPort, () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
    server.on('error', () => {
      resolve(findFreePort(startPort + 1));
    });
  });
}

// Start backend server
async function startBackend() {
  try {
    const backendPort = await findFreePort(8000);
    
    if (isDev) {
      console.log('Development mode: assuming backend is already running on 8000');
      return 8000;
    }

    // In production, start backend from bundled Python
    const resourcesPath = process.resourcesPath;
    const backendScriptPath = path.join(resourcesPath, 'backend', 'launcher.py');
    
    console.log(`Starting backend on port ${backendPort}...`);
    
    backendProcess = spawn('python', [backendScriptPath], {
      cwd: resourcesPath,
      stdio: 'ignore'
    });

    return backendPort;
  } catch (error) {
    console.error('Failed to start backend:', error);
    return 8000;
  }
}

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png')
  });

  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../dist/index.html')}`;

  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webDevTools.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        isDev && { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ].filter(Boolean)
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About FocusRank',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'FocusRank Productivity Tracker',
              message: 'FocusRank',
              detail: 'Track your focus. Compete. Climb the ranks.\n\nVersion 1.0.0'
            });
          }
        }
      ]
    }
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// App event handlers
app.on('ready', async () => {
  await startBackend();
  
  // Wait for backend to start
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  createWindow();
  createMenu();
});

app.on('window-all-closed', () => {
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
  if (backendProcess) {
    try {
      backendProcess.kill();
    } catch (e) {
      console.error('Failed to kill backend process:', e);
    }
  }
});

// IPC handlers for frontend communication
ipcMain.handle('get-app-version', () => app.getVersion());
ipcMain.handle('get-app-name', () => app.name);
