import { ipcMain } from "electron";
import {
  IPCChannels,
  appSettingsSchema,
  appStateSchema,
  modelInstallRequestSchema,
  textGenerationRequestSchema
} from "../../shared/contracts";
import type { JsonStore } from "../services/jsonStore";
import type { AppSettings, AppState } from "../../shared/contracts";
import type { OllamaRuntimeService } from "../services/runtime";
import type { ModelService } from "../services/models";
import type { UpdaterService } from "../services/updater";

export interface HandlerDeps {
  settingsStore: JsonStore<AppSettings>;
  appStateStore: JsonStore<AppState>;
  runtimeService: OllamaRuntimeService;
  modelService: ModelService;
  updaterService: UpdaterService;
}

export const registerHandlers = (deps: HandlerDeps): void => {
  const fallbackSettings = appSettingsSchema.parse({});
  const fallbackState = appStateSchema.parse({});

  ipcMain.handle(IPCChannels.GET_SETTINGS, () => deps.settingsStore.load(fallbackSettings));
  ipcMain.handle(IPCChannels.UPDATE_SETTINGS, (_event, payload) => deps.settingsStore.save(appSettingsSchema.parse(payload)));

  ipcMain.handle(IPCChannels.GET_APP_STATE, () => deps.appStateStore.load(fallbackState));
  ipcMain.handle(IPCChannels.UPDATE_APP_STATE, (_event, payload) => deps.appStateStore.save(appStateSchema.parse(payload)));

  ipcMain.handle(IPCChannels.GET_RUNTIME_STATUS, async () => {
    const settings = deps.settingsStore.load(fallbackSettings);
    return deps.runtimeService.getStatus(settings);
  });

  ipcMain.handle(IPCChannels.HEALTH_CHECK, async () => {
    const settings = deps.settingsStore.load(fallbackSettings);
    const status = await deps.runtimeService.getStatus(settings);
    return {
      ok: status.ollamaInstalled,
      status,
      diagnosticsPath: OllamaRuntimeService.diagnosticsBundlePath()
    };
  });

  ipcMain.handle(IPCChannels.START_OLLAMA, async () => {
    const settings = deps.settingsStore.load(fallbackSettings);
    return deps.runtimeService.start(settings);
  });

  ipcMain.handle(IPCChannels.STOP_OLLAMA, async () => {
    await deps.runtimeService.stop();
    return true;
  });

  ipcMain.handle(IPCChannels.LIST_MODELS, async () => {
    const settings = deps.settingsStore.load(fallbackSettings);
    return deps.modelService.list(settings.ollamaHost);
  });

  ipcMain.handle(IPCChannels.INSTALL_MODEL, async (_event, payload) => {
    const request = modelInstallRequestSchema.parse(payload);
    const settings = deps.settingsStore.load(fallbackSettings);
    await deps.modelService.install(settings, request.name);
    return true;
  });

  ipcMain.handle(IPCChannels.REMOVE_MODEL, async (_event, payload) => {
    const request = modelInstallRequestSchema.parse(payload);
    const settings = deps.settingsStore.load(fallbackSettings);
    await deps.modelService.remove(settings, request.name);
    return true;
  });

  ipcMain.handle(IPCChannels.GENERATE_TEXT, async (_event, payload) => {
    const request = textGenerationRequestSchema.parse(payload);
    const settings = deps.settingsStore.load(fallbackSettings);
    return deps.runtimeService.generateText(settings.ollamaHost, request.model, request.prompt);
  });

  ipcMain.handle(IPCChannels.CHECK_FOR_UPDATES, async () => deps.updaterService.checkForUpdates());
};
