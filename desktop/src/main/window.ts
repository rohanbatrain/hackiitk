import path from "node:path";
import { BrowserWindow, shell } from "electron";

export const createMainWindow = (): BrowserWindow => {
  const preloadPath = path.join(__dirname, "../preload/index.js");
  const isDev = process.env.NODE_ENV === "development";
  const devUrl = process.env.VITE_DEV_SERVER_URL;

  const window = new BrowserWindow({
    width: 1320,
    height: 900,
    minWidth: 1120,
    minHeight: 760,
    show: false,
    backgroundColor: "#0f172a",
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      devTools: isDev
    }
  });

  window.once("ready-to-show", () => window.show());

  window.webContents.setWindowOpenHandler(({ url }) => {
    void shell.openExternal(url);
    return { action: "deny" };
  });

  if (isDev && devUrl) {
    void window.loadURL(devUrl);
  } else {
    const rendererIndex = path.join(__dirname, "../../renderer/dist/index.html");
    void window.loadFile(rendererIndex);
  }

  return window;
};
