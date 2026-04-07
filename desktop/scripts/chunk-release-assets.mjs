import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const CHUNK_SIZE = 1900 * 1024 * 1024;
const RELEASE_DIR = path.resolve("release");
const OUTPUT_DIR = path.resolve("release-chunks");

if (!fs.existsSync(RELEASE_DIR)) {
  console.log("No release directory found; skipping chunking.");
  process.exit(0);
}

fs.mkdirSync(OUTPUT_DIR, { recursive: true });

const manifest = [];

for (const file of fs.readdirSync(RELEASE_DIR)) {
  const fullPath = path.join(RELEASE_DIR, file);
  if (!fs.statSync(fullPath).isFile()) {
    continue;
  }

  const fileSize = fs.statSync(fullPath).size;

  if (fileSize < CHUNK_SIZE) {
    const destination = path.join(OUTPUT_DIR, file);
    fs.copyFileSync(fullPath, destination);
    manifest.push({ source: file, chunks: [file], size: fileSize });
    continue;
  }

  const fd = fs.openSync(fullPath, "r");
  let offset = 0;
  let index = 0;
  const parts = [];

  while (offset < fileSize) {
    const partName = `${file}.part${String(index).padStart(4, "0")}`;
    const partPath = path.join(OUTPUT_DIR, partName);
    const chunk = Buffer.alloc(Math.min(CHUNK_SIZE, fileSize - offset));
    fs.readSync(fd, chunk, 0, chunk.length, offset);
    fs.writeFileSync(partPath, chunk);
    parts.push(partName);
    offset += chunk.length;
    index += 1;
  }

  fs.closeSync(fd);

  const sha256 = crypto.createHash("sha256").update(fs.readFileSync(fullPath)).digest("hex");
  manifest.push({ source: file, chunks: parts, size: fileSize, sha256 });
}

fs.writeFileSync(path.join(OUTPUT_DIR, "manifest.json"), JSON.stringify(manifest, null, 2));
console.log(`Chunk manifest written to ${path.join(OUTPUT_DIR, "manifest.json")}`);
