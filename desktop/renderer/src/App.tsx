import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { desktopApi } from "./api";
import type { AppSettings, AppState, ModelInfo, RuntimeStatus } from "./types";

type Screen = "onboarding" | "runtime" | "models" | "tasks" | "settings";

const formatBytes = (value: number): string => {
  if (!value) {
    return "0 B";
  }
  const units = ["B", "KB", "MB", "GB", "TB"];
  let unitIndex = 0;
  let current = value;
  while (current >= 1024 && unitIndex < units.length - 1) {
    current /= 1024;
    unitIndex += 1;
  }
  return `${current.toFixed(1)} ${units[unitIndex]}`;
};

const defaultSettings: AppSettings = {
  updateChannel: "stable",
  ollamaHost: "http://127.0.0.1:11434",
  ollamaCommand: "ollama",
  modelStoragePath: "models",
  logsLevel: "info",
  autoStartOllama: true,
  telemetryEnabled: false,
  allowOnlineModelCatalog: true
};

const defaultState: AppState = {
  onboardingCompleted: false,
  recentPrompts: []
};

const defaultRuntime: RuntimeStatus = {
  ollamaInstalled: false,
  ollamaRunning: false,
  host: defaultSettings.ollamaHost,
  uptimeSeconds: 0,
  memoryMB: 0,
  cpuCount: 0,
  freeMemoryGB: 0,
  errors: []
};

export default function App() {
  const [screen, setScreen] = useState<Screen>("onboarding");
  const [settings, setSettings] = useState<AppSettings>(defaultSettings);
  const [appState, setAppState] = useState<AppState>(defaultState);
  const [runtimeStatus, setRuntimeStatus] = useState<RuntimeStatus>(defaultRuntime);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [newModel, setNewModel] = useState("qwen2.5:3b-instruct");
  const [prompt, setPrompt] = useState("Summarize key policy gaps in plain language.");
  const [result, setResult] = useState("");

  const canRunTask = useMemo(() => runtimeStatus.ollamaRunning && models.length > 0, [runtimeStatus.ollamaRunning, models.length]);

  const refreshStatus = async (): Promise<void> => {
    const [status, list] = await Promise.all([desktopApi.getRuntimeStatus(), desktopApi.listModels()]);
    setRuntimeStatus(status);
    setModels(list);
  };

  useEffect(() => {
    (async () => {
      try {
        const [storedSettings, storedState] = await Promise.all([desktopApi.getSettings(), desktopApi.getAppState()]);
        setSettings(storedSettings);
        setAppState(storedState);
        setScreen(storedState.onboardingCompleted ? "runtime" : "onboarding");
        await refreshStatus();
      } catch (caughtError) {
        setError((caughtError as Error).message);
      }
    })();

    const timer = setInterval(() => {
      void refreshStatus();
    }, 10000);

    return () => clearInterval(timer);
  }, []);

  const run = async (label: string, action: () => Promise<void>): Promise<void> => {
    setBusy(label);
    setError(null);
    try {
      await action();
    } catch (caughtError) {
      setError((caughtError as Error).message);
    } finally {
      setBusy(null);
    }
  };

  const completeOnboarding = async (): Promise<void> => {
    await run("onboarding", async () => {
      const health = await desktopApi.healthCheck();
      setRuntimeStatus(health.status);
      const nextState = {
        ...appState,
        onboardingCompleted: true,
        lastHealthCheckAt: new Date().toISOString()
      };
      await desktopApi.updateAppState(nextState);
      setAppState(nextState);
      setScreen("runtime");
    });
  };

  const saveSettings = async (): Promise<void> => {
    await run("settings", async () => {
      const updated = await desktopApi.updateSettings(settings);
      setSettings(updated);
      await refreshStatus();
    });
  };

  const startRuntime = async (): Promise<void> => {
    await run("start-ollama", async () => {
      await desktopApi.startOllama();
      await refreshStatus();
    });
  };

  const stopRuntime = async (): Promise<void> => {
    await run("stop-ollama", async () => {
      await desktopApi.stopOllama();
      await refreshStatus();
    });
  };

  const installModel = async (): Promise<void> => {
    await run("install-model", async () => {
      await desktopApi.installModel(newModel);
      await refreshStatus();
    });
  };

  const removeModel = async (name: string): Promise<void> => {
    await run("remove-model", async () => {
      await desktopApi.removeModel(name);
      await refreshStatus();
    });
  };

  const generate = async (): Promise<void> => {
    if (!models[0]) {
      return;
    }

    await run("generate", async () => {
      const selectedModel = appState.lastSelectedModel ?? models[0].name;
      const response = await desktopApi.generateText({ model: selectedModel, prompt, stream: false });
      setResult(response.response);
      const nextState = {
        ...appState,
        lastSelectedModel: selectedModel,
        recentPrompts: [prompt, ...appState.recentPrompts.filter((value) => value !== prompt)].slice(0, 10)
      };
      await desktopApi.updateAppState(nextState);
      setAppState(nextState);
    });
  };

  const checkUpdates = async (): Promise<void> => {
    await run("updates", async () => {
      const message = await desktopApi.checkForUpdates();
      setResult((previous) => `${previous}\n\n[Updater]\n${message}`.trim());
    });
  };

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <h1>Offline Policy Gap Analyzer</h1>
        <p className="subtitle">Production desktop runtime</p>
        {(["onboarding", "runtime", "models", "tasks", "settings"] as Screen[]).map((value) => (
          <button
            key={value}
            className={screen === value ? "nav active" : "nav"}
            type="button"
            onClick={() => setScreen(value)}
          >
            {value.toUpperCase()}
          </button>
        ))}
        <div className="status-pill">
          {runtimeStatus.ollamaRunning ? "Ollama Online" : "Ollama Offline"}
        </div>
      </aside>

      <section className="content">
        {error ? <div className="error">{error}</div> : null}
        {busy ? <div className="busy">Working: {busy}</div> : null}

        {screen === "onboarding" ? (
          <article className="panel">
            <h2>Onboarding & Diagnostics</h2>
            <p>Validate local dependencies, startup behavior, and offline readiness before first use.</p>
            <ul>
              <li>Ollama installed: {runtimeStatus.ollamaInstalled ? "Yes" : "No"}</li>
              <li>Ollama running: {runtimeStatus.ollamaRunning ? "Yes" : "No"}</li>
              <li>Host: {runtimeStatus.host}</li>
              <li>CPU cores: {runtimeStatus.cpuCount}</li>
            </ul>
            <button type="button" onClick={completeOnboarding}>Complete onboarding</button>
          </article>
        ) : null}

        {screen === "runtime" ? (
          <article className="panel">
            <h2>Runtime Status</h2>
            <div className="grid">
              <div className="card"><strong>Version</strong><span>{runtimeStatus.ollamaVersion ?? "unknown"}</span></div>
              <div className="card"><strong>Uptime</strong><span>{runtimeStatus.uptimeSeconds}s</span></div>
              <div className="card"><strong>App Memory</strong><span>{runtimeStatus.memoryMB} MB</span></div>
              <div className="card"><strong>Free RAM</strong><span>{runtimeStatus.freeMemoryGB.toFixed(2)} GB</span></div>
            </div>
            <div className="actions">
              <button type="button" onClick={startRuntime}>Start Ollama</button>
              <button type="button" onClick={stopRuntime}>Stop Ollama</button>
              <button type="button" onClick={() => void refreshStatus()}>Refresh</button>
            </div>
          </article>
        ) : null}

        {screen === "models" ? (
          <article className="panel">
            <h2>Model Management</h2>
            <div className="actions">
              <input value={newModel} onChange={(event) => setNewModel(event.target.value)} />
              <button type="button" onClick={installModel}>Install / Pull</button>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Size</th>
                  <th>Modified</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {models.map((model) => (
                  <tr key={model.name}>
                    <td>{model.name}</td>
                    <td>{formatBytes(model.size)}</td>
                    <td>{model.modifiedAt ?? "-"}</td>
                    <td>
                      <button type="button" onClick={() => void removeModel(model.name)}>Remove</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>
        ) : null}

        {screen === "tasks" ? (
          <article className="panel">
            <h2>Task Execution</h2>
            <p>Run prompts against your local model pipeline with no cloud dependency.</p>
            <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={6} />
            <div className="actions">
              <button type="button" disabled={!canRunTask} onClick={generate}>Run local inference</button>
              <button type="button" onClick={checkUpdates}>Check updates</button>
            </div>
            <pre>{result || "Results will appear here."}</pre>
          </article>
        ) : null}

        {screen === "settings" ? (
          <article className="panel">
            <h2>Settings</h2>
            <label>
              Ollama Host
              <input value={settings.ollamaHost} onChange={(event) => setSettings({ ...settings, ollamaHost: event.target.value })} />
            </label>
            <label>
              Ollama Command
              <input value={settings.ollamaCommand} onChange={(event) => setSettings({ ...settings, ollamaCommand: event.target.value })} />
            </label>
            <label>
              Model Storage Path
              <input value={settings.modelStoragePath} onChange={(event) => setSettings({ ...settings, modelStoragePath: event.target.value })} />
            </label>
            <label>
              Update Channel
              <select
                value={settings.updateChannel}
                onChange={(event) => setSettings({ ...settings, updateChannel: event.target.value as AppSettings["updateChannel"] })}
              >
                <option value="stable">Stable</option>
                <option value="beta">Beta</option>
              </select>
            </label>
            <label>
              <input
                type="checkbox"
                checked={settings.autoStartOllama}
                onChange={(event) => setSettings({ ...settings, autoStartOllama: event.target.checked })}
              />
              Auto-start Ollama on app launch
            </label>
            <label>
              <input
                type="checkbox"
                checked={settings.telemetryEnabled}
                onChange={(event) => setSettings({ ...settings, telemetryEnabled: event.target.checked })}
              />
              Enable local telemetry files
            </label>
            <button type="button" onClick={saveSettings}>Save settings</button>
          </article>
        ) : null}
      </section>
    </main>
  );
}
