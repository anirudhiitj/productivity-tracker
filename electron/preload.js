/**
 * Electron Preload Script
 * Exposes safe APIs to the renderer process
 */

import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  // Backend status
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  
  // Restart backend
  restartBackend: () => ipcRenderer.invoke('restart-backend'),
  
  // Platform info
  platform: process.platform,
  
  // App info
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron
  }
});

// Log that preload is loaded
console.log('[Preload] Preload script loaded');
console.log('[Preload] Platform:', process.platform);
console.log('[Preload] Electron version:', process.versions.electron);
