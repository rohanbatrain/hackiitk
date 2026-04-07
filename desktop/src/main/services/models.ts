import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type { AppSettings, ModelInfo } from "../../shared/contracts";

const execFileAsync = promisify(execFile);

export class ModelService {
  public async list(host: string): Promise<ModelInfo[]> {
    const response = await fetch(`${host}/api/tags`, { method: "GET" });
    if (!response.ok) {
      return [];
    }

    const payload = (await response.json()) as {
      models?: Array<{ name: string; size?: number; modified_at?: string; digest?: string }>;
    };

    return (payload.models ?? []).map((model) => ({
      name: model.name,
      size: model.size ?? 0,
      modifiedAt: model.modified_at,
      digest: model.digest
    }));
  }

  public async install(settings: AppSettings, model: string): Promise<void> {
    await execFileAsync(settings.ollamaCommand, ["pull", model]);
  }

  public async remove(settings: AppSettings, model: string): Promise<void> {
    await execFileAsync(settings.ollamaCommand, ["rm", model]);
  }
}
