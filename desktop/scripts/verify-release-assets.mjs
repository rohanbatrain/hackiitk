import fs from "node:fs";
import path from "node:path";

const LIMIT_BYTES = 2 * 1024 * 1024 * 1024;

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, files);
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

for (const folder of ["dist", "renderer/dist", "release"]) {
  if (!fs.existsSync(folder)) {
    continue;
  }

  for (const file of walk(folder)) {
    const size = fs.statSync(file).size;
    if (size >= LIMIT_BYTES) {
      throw new Error(`Artifact exceeds 2 GiB limit: ${file}`);
    }
  }
}

console.log("Release artifact size verification completed.");
