const { app, BrowserWindow, dialog } = require("electron");
const path = require("path");
const { createServer } = require("./backend/dist/backend/src/server");

const isDev = process.env.NODE_ENV === "development";

function pickDatabaseFile() {
  try {
    console.log("Opening file dialog...");
    const filePaths = dialog.showOpenDialogSync({
      properties: ["openFile"],
      title: "Select a Database File",
    });

    if (filePaths.length === 0) {
      console.log("No file selected. Exiting...");
      app.quit();
      return null;
    }

    console.log("Selected file path:", filePaths[0]);
    return filePaths[0];
  } catch (err) {
    console.error("Error during file selection:", err);
    app.quit();
    return null;
  }
}

function startBackendServer(filePath) {
  process.env.DB_PATH = filePath;

  const { start } = createServer();

  const port = 5000;
  start(port);
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
    },
  });

  const startURL = isDev
    ? "http://localhost:3000" // React development server
    : `file://${path.join(__dirname, "frontend/build/index.html")}`;

  mainWindow.loadURL(startURL).then(() => "Window loaded.");
}

app.whenReady().then(() => {
  const selectedFilePath = pickDatabaseFile();
  if (!selectedFilePath) return;

  startBackendServer(selectedFilePath);

  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
