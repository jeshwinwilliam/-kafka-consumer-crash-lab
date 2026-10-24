import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";

const [archiveArgument, checksumArgument] = process.argv.slice(2);

if (!archiveArgument) {
  console.error("Usage: node scripts/create-archive-checksum.mjs <archive-path> [checksum-path]");
  process.exit(1);
}

const archivePath = resolve(archiveArgument);
const checksumPath = resolve(checksumArgument ?? `${archivePath}.sha256`);
const archive = await readFile(archivePath);
const checksum = createHash("sha256").update(archive).digest("hex");

await writeFile(checksumPath, `${checksum}  ${basename(archivePath)}\n`);
console.log(`Wrote SHA-256 checksum to ${checksumPath}`);
