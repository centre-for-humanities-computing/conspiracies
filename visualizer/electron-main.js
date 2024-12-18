const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const path = require("path");

let mainWindow;
let backendProcess;
let frontendProcess;

const isDev = process.env.NODE_ENV === "development";

function startBackendServer() {
  console.log("Starting Express backend...");
  backendProcess = spawn("npm", ["run", "start:backend"], {
    cwd: path.resolve(__dirname),
    shell: true,
  });

  backendProcess.stdout.on("data", (data) => {
    console.log(`[Backend]: ${data}`);
  });

  backendProcess.stderr.on("data", (data) => {
    console.error(`[Backend Error]: ${data}`);
  });

  backendProcess.on("close", (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

function startFrontendServer() {
  console.log("Starting React frontend...");
  frontendProcess = spawn("npm", ["run", "start:frontend"], {
    cwd: path.resolve(__dirname),
    shell: true,
  });

  frontendProcess.stdout.on("data", (data) => {
    console.log(`[Frontend]: ${data}`);
  });

  frontendProcess.stderr.on("data", (data) => {
    console.error(`[Frontend Error]: ${data}`);
  });

  frontendProcess.on("close", (code) => {
    console.log(`Frontend process exited with code ${code}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
    },
  });

  const startURL = isDev
    ? "http://localhost:3000" // React development server
    : `file://${path.join(__dirname, "frontend/build/index.html")}`;

  mainWindow.loadURL(startURL);

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startBackendServer();
  if (isDev) {
    startFrontendServer();
  }
  createWindow();
});

app.on("window-all-closed", () => {
  if (backendProcess) backendProcess.kill();
  if (frontendProcess) frontendProcess.kill();
  if (process.platform !== "darwin") app.quit();
});
