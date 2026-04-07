import type { AppSettings, AppState, ModelInfo, RuntimeStatus } from "./types";

interface DesktopApi {
  getSettings: () => Promise<AppSettings>;
  updateSettings: (payload: AppSettings) => Promise<AppSettings>;
  getAppState: () => Promise<AppState>;
  updateAppState: (payload: AppState) => Promise<AppState>;
  healthCheck: () => Promise<{ ok: boolean; status: RuntimeStatus; diagnosticsPath: string }>;
  getRuntimeStatus: () => Promise<RuntimeStatus>;
  startOllama: () => Promise<boolean>;
  stopOllama: () => Promise<boolean>;
  listModels: () => Promise<ModelInfo[]>;
  installModel: (name: string) => Promise<boolean>;
  removeModel: (name: string) => Promise<boolean>;
  generateText: (payload: { model: string; prompt: string; stream?: boolean }) => Promise<{
    model: string;
    response: string;
    done: boolean;
  }>;
  checkForUpdates: () => Promise<string>;
}

declare global {
  interface Window {
    desktopApi?: DesktopApi;
  }
}

const fallbackSettings: AppSettings = {
  updateChannel: "stable",
  ollamaHost: "http://127.0.0.1:11434",
  ollamaCommand: "ollama",
  modelStoragePath: "models",
  logsLevel: "info",
  autoStartOllama: true,
  telemetryEnabled: false,
  allowOnlineModelCatalog: true
};

const fallbackState: AppState = {
  onboardingCompleted: false,
  recentPrompts: []
};

const unavailable = <T>(value: T): Promise<T> => Promise.resolve(value);

export const desktopApi: DesktopApi =
  window.desktopApi ?? {
    getSettings: () => unavailable(fallbackSettings),
    updateSettings: () => unavailable(fallbackSettings),
    getAppState: () => unavailable(fallbackState),
    updateAppState: () => unavailable(fallbackState),
    healthCheck: () => unavailable({
      ok: false,
      status: {
        ollamaInstalled: false,
        ollamaRunning: false,
        host: fallbackSettings.ollamaHost,
        uptimeSeconds: 0,
        memoryMB: 0,
        cpuCount: 0,
        freeMemoryGB: 0,
        errors: ["Desktop API unavailable outside Electron runtime."]
      },
      diagnosticsPath: ""
    }),
    getRuntimeStatus: () =>
      unavailable({
        ollamaInstalled: false,
        ollamaRunning: false,
        host: fallbackSettings.ollamaHost,
        uptimeSeconds: 0,
        memoryMB: 0,
        cpuCount: 0,
        freeMemoryGB: 0,
        errors: ["Desktop API unavailable outside Electron runtime."]
      }),
    startOllama: () => unavailable(false),
    stopOllama: () => unavailable(false),
    listModels: () => unavailable([]),
    installModel: () => unavailable(false),
    removeModel: () => unavailable(false),
    generateText: () => unavailable({ model: "", response: "Desktop API unavailable.", done: true }),
    checkForUpdates: () => unavailable("Desktop API unavailable.")
  };
