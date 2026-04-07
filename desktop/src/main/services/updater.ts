import { autoUpdater } from "electron-updater";
import type { Logger } from "./logger";

export class UpdaterService {
  public constructor(private readonly logger: Logger) {
    autoUpdater.autoDownload = false;

    autoUpdater.on("error", (error) => {
      this.logger.error({ error }, "Updater error");
    });
  }

  public async checkForUpdates(): Promise<string> {
    const result = await autoUpdater.checkForUpdates();
    if (!result?.updateInfo) {
      return "No updates available.";
    }
    return `Latest available: ${result.updateInfo.version}`;
  }
}
