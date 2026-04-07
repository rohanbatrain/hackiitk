import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const INPUT_DIR = path.resolve("release-chunks");
const OUTPUT_DIR = path.resolve("release-assembled");
const manifestPath = path.join(INPUT_DIR, "manifest.json");

if (!fs.existsSync(manifestPath)) {
  throw new Error("Chunk manifest not found. Run release:chunk-assets first.");
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

for (const entry of manifest) {
  const target = path.join(OUTPUT_DIR, entry.source);
  const writeStream = fs.createWriteStream(target);

  for (const chunkFile of entry.chunks) {
    const chunkPath = path.join(INPUT_DIR, chunkFile);
    writeStream.write(fs.readFileSync(chunkPath));
  }

  writeStream.end();
  await new Promise((resolve) => writeStream.on("finish", resolve));

  if (entry.sha256) {
    const digest = crypto.createHash("sha256").update(fs.readFileSync(target)).digest("hex");
    if (digest !== entry.sha256) {
      throw new Error(`Checksum mismatch for ${entry.source}`);
    }
  }
}

console.log("Chunked release assets assembled successfully.");
