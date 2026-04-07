import path from "node:path";
import { app } from "electron";
import pino from "pino";

export const createLogger = () => {
  const logsPath = path.join(app.getPath("userData"), "logs", "desktop.log");

  return pino({
    level: process.env.NODE_ENV === "development" ? "debug" : "info"
  }, pino.destination({
    mkdir: true,
    dest: logsPath,
    sync: false
  }));
};

export type Logger = ReturnType<typeof createLogger>;
