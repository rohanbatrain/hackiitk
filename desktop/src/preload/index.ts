import { contextBridge, ipcRenderer } from "electron";
import type {
  AppSettings,
  AppState,
  ModelInfo,
  RuntimeStatus,
  TextGenerationRequest,
  TextGenerationResult
} from "../shared/contracts";
import { IPCChannels } from "../shared/contracts";

const api = {
  getSettings: (): Promise<AppSettings> => ipcRenderer.invoke(IPCChannels.GET_SETTINGS),
  updateSettings: (payload: AppSettings): Promise<AppSettings> => ipcRenderer.invoke(IPCChannels.UPDATE_SETTINGS, payload),
  getAppState: (): Promise<AppState> => ipcRenderer.invoke(IPCChannels.GET_APP_STATE),
  updateAppState: (payload: AppState): Promise<AppState> => ipcRenderer.invoke(IPCChannels.UPDATE_APP_STATE, payload),
  healthCheck: (): Promise<{ ok: boolean; status: RuntimeStatus; diagnosticsPath: string }> =>
    ipcRenderer.invoke(IPCChannels.HEALTH_CHECK),
  getRuntimeStatus: (): Promise<RuntimeStatus> => ipcRenderer.invoke(IPCChannels.GET_RUNTIME_STATUS),
  startOllama: (): Promise<boolean> => ipcRenderer.invoke(IPCChannels.START_OLLAMA),
  stopOllama: (): Promise<boolean> => ipcRenderer.invoke(IPCChannels.STOP_OLLAMA),
  listModels: (): Promise<ModelInfo[]> => ipcRenderer.invoke(IPCChannels.LIST_MODELS),
  installModel: (name: string): Promise<boolean> => ipcRenderer.invoke(IPCChannels.INSTALL_MODEL, { name }),
  removeModel: (name: string): Promise<boolean> => ipcRenderer.invoke(IPCChannels.REMOVE_MODEL, { name }),
  generateText: (payload: TextGenerationRequest): Promise<TextGenerationResult> =>
    ipcRenderer.invoke(IPCChannels.GENERATE_TEXT, payload),
  checkForUpdates: (): Promise<string> => ipcRenderer.invoke(IPCChannels.CHECK_FOR_UPDATES)
};

contextBridge.exposeInMainWorld("desktopApi", api);
