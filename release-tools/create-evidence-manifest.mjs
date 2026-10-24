import { createHash } from "node:crypto";
import { mkdir, readdir, readFile, stat, writeFile } from "node:fs/promises";
import { dirname, relative, resolve, sep } from "node:path";

const [sourceArgument, outputArgument] = process.argv.slice(2);

if (!sourceArgument || !outputArgument) {
  console.error("Usage: node scripts/create-evidence-manifest.mjs <evidence-directory> <manifest-path>");
  process.exit(1);
}

const sourceDirectory = resolve(sourceArgument);
const outputPath = resolve(outputArgument);

async function filesWithin(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const results = [];

  for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
    const fullPath = resolve(directory, entry.name);
    if (fullPath === outputPath) continue;
    if (entry.isDirectory()) results.push(...await filesWithin(fullPath));
    if (entry.isFile()) results.push(fullPath);
  }

  return results;
}

const sourceStats = await stat(sourceDirectory);
if (!sourceStats.isDirectory()) {
  throw new Error(`Evidence directory is not a directory: ${sourceDirectory}`);
}

const entries = await Promise.all((await filesWithin(sourceDirectory)).map(async (filePath) => {
  const content = await readFile(filePath);
  return {
    path: relative(sourceDirectory, filePath).split(sep).join("/"),
    bytes: content.byteLength,
    sha256: createHash("sha256").update(content).digest("hex")
  };
}));

const manifest = {
  schemaVersion: 1,
  generatedAt: new Date().toISOString(),
  algorithm: "sha256",
  fileCount: entries.length,
  files: entries
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`Wrote ${entries.length} file checksums to ${outputPath}`);
