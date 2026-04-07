import fs from "node:fs";
import path from "node:path";
import { app } from "electron";
import type { ZodSchema } from "zod";

export class JsonStore<T> {
  private readonly filePath: string;

  public constructor(private readonly name: string, private readonly schema: ZodSchema<T>) {
    this.filePath = path.join(app.getPath("userData"), `${name}.json`);
  }

  public load(fallback: T): T {
    try {
      if (!fs.existsSync(this.filePath)) {
        this.save(fallback);
        return fallback;
      }
      const parsed = JSON.parse(fs.readFileSync(this.filePath, "utf8"));
      return this.schema.parse(parsed);
    } catch {
      this.save(fallback);
      return fallback;
    }
  }

  public save(value: T): T {
    const parsed = this.schema.parse(value);
    fs.mkdirSync(path.dirname(this.filePath), { recursive: true });
    fs.writeFileSync(this.filePath, JSON.stringify(parsed, null, 2), "utf8");
    return parsed;
  }
}
