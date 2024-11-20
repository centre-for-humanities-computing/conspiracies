const { app, BrowserWindow } = require("electron");
const path = require("path");


function createWindow() {
  const mainWindow = new BrowserWindow();

  // Directly load index.html from the build folder
  mainWindow.loadFile(path.join(__dirname, "build", "index.html"));
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
