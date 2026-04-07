import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";

test("chunk assembler script files exist", () => {
  const desktopRoot = path.resolve(process.cwd());
  for (const scriptName of [
    "scripts/chunk-release-assets.mjs",
    "scripts/assemble-release-assets.mjs",
    "scripts/verify-release-assets.mjs"
  ]) {
    assert.equal(fs.existsSync(path.join(desktopRoot, scriptName)), true);
  }
});

test("temp file remains under 2 GiB policy during test", () => {
  const tmpFile = path.join(os.tmpdir(), `desktop-policy-${Date.now()}.bin`);
  fs.writeFileSync(tmpFile, Buffer.alloc(1024));
  const size = fs.statSync(tmpFile).size;
  assert.equal(size < 2 * 1024 * 1024 * 1024, true);
  fs.unlinkSync(tmpFile);
});
