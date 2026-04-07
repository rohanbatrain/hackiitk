import { app, BrowserWindow } from "electron";
import { registerHandlers } from "./ipc/registerHandlers";
import { createLogger } from "./services/logger";
import { JsonStore } from "./services/jsonStore";
import { appSettingsSchema, appStateSchema, type AppSettings, type AppState } from "../shared/contracts";
import { OllamaRuntimeService } from "./services/runtime";
import { ModelService } from "./services/models";
import { UpdaterService } from "./services/updater";
import { createMainWindow } from "./window";

const bootstrap = async (): Promise<void> => {
  await app.whenReady();

  app.setAppUserModelId("com.hackiitk.policyanalyzer.desktop");

  const logger = createLogger();
  const settingsStore = new JsonStore<AppSettings>("settings", appSettingsSchema);
  const appStateStore = new JsonStore<AppState>("appState", appStateSchema);

  const runtimeService = new OllamaRuntimeService(logger);
  const modelService = new ModelService();
  const updaterService = new UpdaterService(logger);

  registerHandlers({
    settingsStore,
    appStateStore,
    runtimeService,
    modelService,
    updaterService
  });

  const settings = settingsStore.load(appSettingsSchema.parse({}));
  if (settings.autoStartOllama) {
    void runtimeService.start(settings);
  }

  createMainWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
      app.quit();
    }
  });

  app.on("before-quit", () => {
    void runtimeService.stop();
  });
};

void bootstrap();
