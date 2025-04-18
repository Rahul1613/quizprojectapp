const { app, BrowserWindow, Menu, Tray, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = require('electron-is-dev');
const log = require('electron-log');
const { autoUpdater } = require('electron-updater');
const io = require('socket.io-client');
const fs = require('fs');

// Configure logging
log.transports.file.level = 'info';
autoUpdater.logger = log;
autoUpdater.autoDownload = true;

// Global references
let mainWindow;
let tray;
let djangoProcess;
let serverRunning = false;
let socket;

// Server URL
const serverUrl = 'http://localhost:8000';

// Path to Python executable and Django script
const pythonPath = isDev 
  ? path.join(__dirname, '.venv', 'Scripts', 'python.exe')
  : path.join(process.resourcesPath, 'python_dist', 'python.exe');

const djangoScript = isDev
  ? path.join(__dirname, 'manage.py')
  : path.join(process.resourcesPath, 'python_dist', 'manage.py');

// Database paths
const appDataPath = path.join(app.getPath('userData'), 'QuizAppData');
const dbPath = path.join(appDataPath, 'db.sqlite3');

// Ensure app data directory exists
if (!isDev && !fs.existsSync(appDataPath)) {
  fs.mkdirSync(appDataPath, { recursive: true });
  
  // Copy database if it doesn't exist in app data
  if (!fs.existsSync(dbPath)) {
    const sourceDbPath = path.join(process.resourcesPath, 'db', 'db.sqlite3');
    if (fs.existsSync(sourceDbPath)) {
      fs.copyFileSync(sourceDbPath, dbPath);
      log.info(`Database copied to: ${dbPath}`);
    }
  }
}

// Start Django server
function startDjangoServer() {
  log.info('Starting Django server...');
  
  try {
    // Set environment variables for the Django process
    const env = Object.assign({}, process.env, {
      PYTHONUNBUFFERED: '1',
      DJANGO_SETTINGS_MODULE: 'onlinequiz.settings',
      DATABASE_PATH: dbPath,
      PYTHONIOENCODING: 'utf-8'
    });

    // Start Django server
    log.info(`Starting Django with: ${pythonPath} ${djangoScript}`);
    log.info(`Database path: ${dbPath}`);
    
    djangoProcess = spawn(pythonPath, [djangoScript, 'runserver', '--noreload'], { env });
    
    // Log Django output
    djangoProcess.stdout.on('data', (data) => {
      const output = data.toString();
      log.info(`Django: ${output}`);
      if (output.includes('Starting development server at')) {
        serverRunning = true;
        mainWindow.loadURL(serverUrl);
        setupSocketConnection();
      }
    });
    
    djangoProcess.stderr.on('data', (data) => {
      const error = data.toString();
      log.error(`Django Error: ${error}`);
      
      // Show error dialog for critical errors
      if (error.includes('Error:') || error.includes('Exception:')) {
        dialog.showErrorBox('Server Error', 
          'There was a problem starting the quiz server. Please restart the application.');
      }
    });
    
    djangoProcess.on('close', (code) => {
      log.info(`Django server process exited with code ${code}`);
      serverRunning = false;
      
      if (code !== 0 && mainWindow) {
        mainWindow.loadFile(path.join(__dirname, 'error.html'));
      }
    });
  } catch (error) {
    log.error('Failed to start Django server:', error);
    dialog.showErrorBox('Server Error', 
      'Failed to start the quiz server. Please check if antivirus is blocking the application.');
  }
}

// Setup socket connection for real-time updates
function setupSocketConnection() {
  socket = io(serverUrl);
  
  socket.on('connect', () => {
    log.info('Connected to WebSocket server');
  });
  
  socket.on('notification', (data) => {
    log.info('Received notification:', data);
    if (mainWindow) {
      mainWindow.webContents.send('new-notification', data);
    }
  });
  
  socket.on('disconnect', () => {
    log.info('Disconnected from WebSocket server');
  });
}

// Create main application window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'build', 'icon.ico'),
    show: false // Don't show until ready
  });
  
  // Show loading screen while server starts
  mainWindow.loadFile(path.join(__dirname, 'loading.html'));
  
  // Show window when ready to avoid white flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
  
  // Start Django server
  startDjangoServer();
  
  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  // Create application menu
  createMenu();
  
  // Create system tray
  createTray();
  
  // Check for updates
  if (!isDev) {
    setTimeout(() => {
      autoUpdater.checkForUpdatesAndNotify();
    }, 10000); // Check after 10 seconds to avoid startup issues
  }
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Refresh',
          click: () => {
            if (mainWindow) mainWindow.reload();
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          click: () => {
            app.quit();
          }
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
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            // Show about dialog
            const aboutWindow = new BrowserWindow({
              width: 400,
              height: 300,
              resizable: false,
              minimizable: false,
              maximizable: false,
              parent: mainWindow,
              modal: true
            });
            aboutWindow.loadFile(path.join(__dirname, 'about.html'));
          }
        }
      ]
    }
  ];
  
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Create system tray
function createTray() {
  tray = new Tray(path.join(__dirname, 'build', 'icon.ico'));
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open Quiz App',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
        } else {
          createWindow();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Exit',
      click: () => {
        app.quit();
      }
    }
  ]);
  
  tray.setToolTip('Quiz App');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    } else {
      createWindow();
    }
  });
}

// App events
app.on('ready', createWindow);

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

// Clean up before quitting
app.on('before-quit', () => {
  if (djangoProcess) {
    log.info('Killing Django server process...');
    djangoProcess.kill();
  }
  
  if (socket) {
    socket.disconnect();
  }
});

// Auto-updater events
autoUpdater.on('checking-for-update', () => {
  log.info('Checking for update...');
});

autoUpdater.on('update-available', (info) => {
  log.info('Update available:', info);
  // Notify user about update
  if (mainWindow) {
    mainWindow.webContents.send('update-available', info);
  }
});

autoUpdater.on('update-not-available', (info) => {
  log.info('Update not available:', info);
});

autoUpdater.on('error', (err) => {
  log.error('Error in auto-updater:', err);
  // Don't show errors to user to avoid confusion
});

autoUpdater.on('download-progress', (progressObj) => {
  let logMessage = `Download speed: ${progressObj.bytesPerSecond}`;
  logMessage = `${logMessage} - Downloaded ${progressObj.percent}%`;
  logMessage = `${logMessage} (${progressObj.transferred}/${progressObj.total})`;
  log.info(logMessage);
});

autoUpdater.on('update-downloaded', (info) => {
  log.info('Update downloaded:', info);
  // Notify user that update is ready
  if (mainWindow) {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: 'A new version has been downloaded. Restart the application to apply the updates.',
      buttons: ['Restart', 'Later'],
      defaultId: 0
    }).then(result => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall(false, true);
      }
    });
  }
});

// Handle IPC messages from renderer
ipcMain.on('restart-app', () => {
  autoUpdater.quitAndInstall(false, true);
});

ipcMain.on('check-for-updates', () => {
  autoUpdater.checkForUpdates();
});
