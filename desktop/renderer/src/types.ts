export type UpdateChannel = "stable" | "beta";

export interface AppSettings {
  updateChannel: UpdateChannel;
  ollamaHost: string;
  ollamaCommand: string;
  modelStoragePath: string;
  logsLevel: "error" | "warn" | "info" | "debug";
  autoStartOllama: boolean;
  telemetryEnabled: boolean;
  allowOnlineModelCatalog: boolean;
}

export interface RuntimeStatus {
  ollamaInstalled: boolean;
  ollamaRunning: boolean;
  ollamaVersion?: string;
  host: string;
  uptimeSeconds: number;
  memoryMB: number;
  cpuCount: number;
  freeDiskGB: number;
  errors: string[];
}

export interface ModelInfo {
  name: string;
  size: number;
  modifiedAt?: string;
  digest?: string;
}

export interface AppState {
  onboardingCompleted: boolean;
  lastSelectedModel?: string;
  recentPrompts: string[];
  lastHealthCheckAt?: string;
}
