import fs from "fs";
import path from "path";

const LOG_DIR = path.resolve(process.cwd(), "logs");
const LOG_FILE = path.join(LOG_DIR, "debug.log");

function ensureLogDir() {
  if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  }
}

function truncate(value, maxLength = 4000) {
  if (value === undefined || value === null) {
    return value;
  }

  const text = typeof value === "string" ? value : JSON.stringify(value);
  if (!text) {
    return text;
  }

  return text.length > maxLength ? `${text.slice(0, maxLength)}...<truncated>` : text;
}

export function logEvent(scope, message, details) {
  ensureLogDir();

  const entry = {
    ts: new Date().toISOString(),
    scope,
    message,
    details: details === undefined ? undefined : truncate(details)
  };

  fs.appendFileSync(LOG_FILE, `${JSON.stringify(entry)}\n`, "utf8");

  if (details === undefined) {
    console.log(`[${entry.ts}] [${scope}] ${message}`);
  } else {
    console.log(`[${entry.ts}] [${scope}] ${message}`, entry.details);
  }
}

export function logError(scope, message, error) {
  logEvent(scope, message, {
    name: error?.name,
    message: error?.message,
    stack: error?.stack
  });
}

export function getLogFilePath() {
  return LOG_FILE;
}