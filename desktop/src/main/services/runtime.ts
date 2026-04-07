import os from "node:os";
import { spawn } from "node:child_process";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { app } from "electron";
import type { AppSettings, RuntimeStatus } from "../../shared/contracts";
import type { Logger } from "./logger";

const execFileAsync = promisify(execFile);

export class OllamaRuntimeService {
  private processHandle: ReturnType<typeof spawn> | null = null;
  private bootTimestamp = Date.now();

  public constructor(private readonly logger: Logger) {}

  private async commandExists(command: string): Promise<boolean> {
    try {
      await execFileAsync(command, ["--version"]);
      return true;
    } catch {
      return false;
    }
  }

  public async getVersion(command: string): Promise<string | undefined> {
    try {
      const { stdout, stderr } = await execFileAsync(command, ["--version"]);
      return (stdout || stderr).trim();
    } catch {
      return undefined;
    }
  }

  public async isRunning(host: string): Promise<boolean> {
    try {
      const response = await fetch(`${host}/api/tags`, { method: "GET" });
      return response.ok;
    } catch {
      return false;
    }
  }

  public async start(settings: AppSettings): Promise<boolean> {
    if (await this.isRunning(settings.ollamaHost)) {
      this.logger.info("Ollama already running.");
      return true;
    }

    if (!(await this.commandExists(settings.ollamaCommand))) {
      this.logger.warn("Ollama command unavailable.");
      return false;
    }

    this.logger.info("Starting Ollama background process.");
    this.processHandle = spawn(settings.ollamaCommand, ["serve"], {
      detached: false,
      stdio: "ignore"
    });
    this.processHandle.unref();
    this.bootTimestamp = Date.now();

    for (let i = 0; i < 30; i += 1) {
      if (await this.isRunning(settings.ollamaHost)) {
        return true;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    return false;
  }

  public async stop(): Promise<void> {
    if (!this.processHandle) {
      return;
    }

    this.processHandle.kill("SIGTERM");
    this.processHandle = null;
  }

  public async getStatus(settings: AppSettings): Promise<RuntimeStatus> {
    const ollamaInstalled = await this.commandExists(settings.ollamaCommand);
    const ollamaRunning = await this.isRunning(settings.ollamaHost);
    const version = ollamaInstalled ? await this.getVersion(settings.ollamaCommand) : undefined;

    const freeMemoryGB = Math.max(0, os.freemem() / (1024 ** 3));

    return {
      ollamaInstalled,
      ollamaRunning,
      ollamaVersion: version,
      host: settings.ollamaHost,
      uptimeSeconds: Math.floor((Date.now() - this.bootTimestamp) / 1000),
      memoryMB: Math.round(process.memoryUsage().rss / (1024 ** 2)),
      cpuCount: os.cpus().length,
      freeMemoryGB,
      errors: []
    };
  }

  public async generateText(
    host: string,
    model: string,
    prompt: string
  ): Promise<{ model: string; response: string; done: boolean }> {
    const response = await fetch(`${host}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, prompt, stream: false })
    });

    if (!response.ok) {
      throw new Error(`Generation failed: ${response.status}`);
    }

    const payload = (await response.json()) as { model?: string; response?: string; done?: boolean };

    return {
      model: payload.model ?? model,
      response: payload.response ?? "",
      done: payload.done ?? true
    };
  }

  public static diagnosticsBundlePath(): string {
    return `${app.getPath("userData")}/logs`;
  }
}
