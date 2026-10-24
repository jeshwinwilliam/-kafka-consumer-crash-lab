import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const [manifestArgument] = process.argv.slice(2);

if (!manifestArgument) {
  console.error("Usage: node scripts/verify-evidence-manifest.mjs <manifest-path>");
  process.exit(1);
}

const manifestPath = resolve(manifestArgument);
const manifest = JSON.parse(await readFile(manifestPath, "utf8"));

if (manifest.schemaVersion !== 1 || manifest.algorithm !== "sha256" || !Array.isArray(manifest.files)) {
  throw new Error("Unsupported or malformed evidence manifest.");
}

const root = dirname(manifestPath);
const failures = [];

for (const entry of manifest.files) {
  const filePath = resolve(root, entry.path);
  if (!filePath.startsWith(`${root}/`)) {
    failures.push(`${entry.path}: escapes the manifest directory`);
    continue;
  }

  try {
    const content = await readFile(filePath);
    const hash = createHash("sha256").update(content).digest("hex");
    if (content.byteLength !== entry.bytes || hash !== entry.sha256) {
      failures.push(`${entry.path}: checksum or size mismatch`);
    }
  } catch {
    failures.push(`${entry.path}: missing or unreadable`);
  }
}

if (failures.length) {
  console.error(`Evidence manifest verification failed:\n${failures.join("\n")}`);
  process.exit(1);
}

console.log(`Verified ${manifest.files.length} evidence files from ${manifestPath}`);
