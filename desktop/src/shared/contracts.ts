import { z } from "zod";

export const updateChannelSchema = z.enum(["stable", "beta"]);

export const appSettingsSchema = z.object({
  updateChannel: updateChannelSchema.default("stable"),
  ollamaHost: z.string().default("http://127.0.0.1:11434"),
  ollamaCommand: z.string().default("ollama"),
  modelStoragePath: z.string().default("models"),
  logsLevel: z.enum(["error", "warn", "info", "debug"]).default("info"),
  autoStartOllama: z.boolean().default(true),
  telemetryEnabled: z.boolean().default(false),
  allowOnlineModelCatalog: z.boolean().default(true)
});

export const modelInfoSchema = z.object({
  name: z.string(),
  size: z.number().nonnegative().default(0),
  modifiedAt: z.string().optional(),
  digest: z.string().optional()
});

export const runtimeStatusSchema = z.object({
  ollamaInstalled: z.boolean(),
  ollamaRunning: z.boolean(),
  ollamaVersion: z.string().optional(),
  host: z.string(),
  uptimeSeconds: z.number().nonnegative(),
  memoryMB: z.number().nonnegative(),
  cpuCount: z.number().int().positive(),
  freeDiskGB: z.number().nonnegative(),
  errors: z.array(z.string()).default([])
});

export const modelInstallRequestSchema = z.object({
  name: z.string().min(1)
});

export const textGenerationRequestSchema = z.object({
  model: z.string().min(1),
  prompt: z.string().min(1),
  stream: z.boolean().default(false)
});

export const textGenerationResultSchema = z.object({
  model: z.string(),
  response: z.string(),
  done: z.boolean().default(true)
});

export const appStateSchema = z.object({
  onboardingCompleted: z.boolean().default(false),
  lastSelectedModel: z.string().optional(),
  recentPrompts: z.array(z.string()).default([]),
  lastHealthCheckAt: z.string().optional()
});

export type AppSettings = z.infer<typeof appSettingsSchema>;
export type ModelInfo = z.infer<typeof modelInfoSchema>;
export type RuntimeStatus = z.infer<typeof runtimeStatusSchema>;
export type ModelInstallRequest = z.infer<typeof modelInstallRequestSchema>;
export type TextGenerationRequest = z.infer<typeof textGenerationRequestSchema>;
export type TextGenerationResult = z.infer<typeof textGenerationResultSchema>;
export type AppState = z.infer<typeof appStateSchema>;

export const IPCChannels = {
  GET_SETTINGS: "settings:get",
  UPDATE_SETTINGS: "settings:update",
  GET_APP_STATE: "appState:get",
  UPDATE_APP_STATE: "appState:update",
  HEALTH_CHECK: "runtime:healthCheck",
  GET_RUNTIME_STATUS: "runtime:getStatus",
  START_OLLAMA: "runtime:startOllama",
  STOP_OLLAMA: "runtime:stopOllama",
  LIST_MODELS: "models:list",
  INSTALL_MODEL: "models:install",
  REMOVE_MODEL: "models:remove",
  GENERATE_TEXT: "task:generateText",
  CHECK_FOR_UPDATES: "updates:check"
} as const;

export type IPCChannel = (typeof IPCChannels)[keyof typeof IPCChannels];
