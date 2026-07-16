#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

function usage() {
  console.error("Usage: node build_zotero_linked_attachment_js.mjs <mapping.json> <output.js>");
  process.exit(2);
}

function defaultContentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".pdf") return "application/pdf";
  if (ext === ".md" || ext === ".markdown") return "text/markdown";
  if (ext === ".txt") return "text/plain";
  return "application/octet-stream";
}

function normalizeRows(rawRows) {
  if (!Array.isArray(rawRows) || rawRows.length === 0) {
    throw new Error("Mapping JSON must be a nonempty array");
  }

  const byIdentity = new Map();
  let duplicateCount = 0;
  for (let index = 0; index < rawRows.length; index++) {
    const input = rawRows[index];
    if (!input || typeof input !== "object" || Array.isArray(input)) {
      throw new Error(`Row ${index} must be an object`);
    }
    if (typeof input.parentKey !== "string" || !input.parentKey.trim()) {
      throw new Error(`Row ${index} has an invalid parentKey`);
    }
    if (typeof input.path !== "string" || !path.isAbsolute(input.path)) {
      throw new Error(`Row ${index} path must be absolute`);
    }

    let canonicalPath;
    try {
      canonicalPath = fs.realpathSync.native(input.path);
    } catch {
      throw new Error(`Row ${index} file is unavailable: ${input.path}`);
    }
    if (!fs.statSync(canonicalPath).isFile()) {
      throw new Error(`Row ${index} path is not a regular file: ${input.path}`);
    }
    if (input.tags !== undefined && !Array.isArray(input.tags)) {
      throw new Error(`Row ${index} tags must be an array`);
    }
    const tags = [...new Set((input.tags || []).map((tag) => {
      if (typeof tag !== "string" || !tag.trim()) {
        throw new Error(`Row ${index} contains an invalid tag`);
      }
      return tag.trim();
    }))].sort();

    const row = {
      parentKey: input.parentKey.trim(),
      path: canonicalPath,
      title: input.title === undefined
        ? path.basename(canonicalPath)
        : String(input.title).trim(),
      contentType: input.contentType === undefined
        ? defaultContentType(canonicalPath)
        : String(input.contentType).trim(),
      tags,
    };
    if (!row.title || !row.contentType) {
      throw new Error(`Row ${index} has an empty title or contentType`);
    }

    const identity = `${row.parentKey}\u0000${row.path}`;
    const previous = byIdentity.get(identity);
    if (previous) {
      const sameMetadata = previous.title === row.title
        && previous.contentType === row.contentType
        && JSON.stringify(previous.tags) === JSON.stringify(row.tags);
      if (!sameMetadata) {
        throw new Error(`Conflicting duplicate mapping for ${row.parentKey}: ${row.path}`);
      }
      duplicateCount++;
      continue;
    }
    byIdentity.set(identity, row);
  }

  return {
    rows: [...byIdentity.values()],
    mappingRowCount: rawRows.length,
    duplicateCount,
  };
}

const argv = process.argv.slice(2);
if (argv.length !== 2) usage();
const [mappingPath, outputPath] = argv;

let mappingIdentity;
let outputIdentity;
let outputStat = null;
let pathsShareFile = false;
try {
  mappingIdentity = fs.realpathSync.native(mappingPath);
  const absoluteOutput = path.resolve(outputPath);
  let outputEntry = null;
  try {
    outputEntry = fs.lstatSync(absoluteOutput);
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }
  if (outputEntry?.isSymbolicLink()) {
    throw new Error(`Refusing to overwrite symlink output: ${absoluteOutput}`);
  }
  if (outputEntry && !outputEntry.isFile()) {
    throw new Error(`Output path is not a regular file: ${absoluteOutput}`);
  }
  if (outputEntry && outputEntry.nlink > 1) {
    throw new Error(`Refusing to overwrite hard-linked output: ${absoluteOutput}`);
  }
  const outputParent = fs.realpathSync.native(path.dirname(absoluteOutput));
  const outputExists = outputEntry !== null;
  outputIdentity = outputExists
    ? fs.realpathSync.native(absoluteOutput)
    : path.join(outputParent, path.basename(absoluteOutput));
  if (outputExists) {
    const mappingStat = fs.statSync(mappingIdentity);
    outputStat = fs.statSync(outputIdentity);
    pathsShareFile = mappingStat.dev === outputStat.dev && mappingStat.ino === outputStat.ino;
  }
} catch (error) {
  console.error(String(error?.message || error));
  process.exit(2);
}
if (mappingIdentity === outputIdentity || pathsShareFile) {
  console.error("Mapping and output paths must differ");
  process.exit(2);
}

let normalized;
try {
  normalized = normalizeRows(JSON.parse(fs.readFileSync(mappingIdentity, "utf8")));
} catch (error) {
  console.error(String(error?.message || error));
  process.exit(2);
}

try {
  for (const row of normalized.rows) {
    const sourceStat = fs.statSync(row.path);
    const sourceAliasesOutput = row.path === outputIdentity
      || (outputStat !== null
        && sourceStat.dev === outputStat.dev
        && sourceStat.ino === outputStat.ino);
    if (sourceAliasesOutput) {
      throw new Error(`Attachment source and generated-script output paths must differ: ${row.path}`);
    }
  }
} catch (error) {
  console.error(String(error?.message || error));
  process.exit(2);
}

const zoteroScript = `// Generated by zotero-linked-attachments.
// Run inside Zotero Desktop: Tools -> Developer -> Run JavaScript.
// Check "Run as async function" before executing.

const rows = ${JSON.stringify(normalized.rows, null, 2)};
const libraryID = Zotero.Libraries.userLibraryID;
const result = {
  created: [],
  updated: [],
  skipped: [],
  missingParents: [],
  conflicts: [],
  errors: [],
};

async function inspectLinkedChildren(parent, expectedPath) {
  const matches = [];
  for (const childID of parent.getAttachments()) {
    const item = Zotero.Items.get(childID);
    if (!item || !item.isLinkedFileAttachment()) continue;

    let availablePath = null;
    try {
      availablePath = await item.getFilePathAsync();
    } catch (_error) {
      availablePath = null;
    }
    let configuredPath = availablePath;
    if (!configuredPath) {
      const storedPath = item.attachmentPath;
      configuredPath = storedPath?.startsWith(Zotero.Attachments.BASE_PATH_PLACEHOLDER)
        ? Zotero.Attachments.resolveRelativePath(storedPath)
        : storedPath;
    }
    if (!configuredPath) continue;
    if (PathUtils.normalize(configuredPath) === PathUtils.normalize(expectedPath)) {
      matches.push({
        item,
        fileAvailable: Boolean(availablePath),
        storedPath: item.attachmentPath,
      });
    }
  }
  return matches;
}

for (const row of rows) {
  let phase = "lookup-parent";
  let attachmentKey = null;
  let createdBeforeError = false;
  try {
    const parent = Zotero.Items.getByLibraryAndKey(libraryID, row.parentKey);
    if (!parent) {
      result.missingParents.push({ parentKey: row.parentKey, path: row.path });
      continue;
    }
    if (!parent.isRegularItem()) {
      result.conflicts.push({
        parentKey: row.parentKey,
        path: row.path,
        reason: "parent-is-not-a-regular-item",
      });
      continue;
    }

    phase = "inspect-existing";
    const matches = await inspectLinkedChildren(parent, row.path);
    if (matches.length > 1) {
      result.conflicts.push({
        parentKey: row.parentKey,
        path: row.path,
        attachmentKeys: matches.map(({ item }) => item.key),
        reason: "multiple-same-path-linked-files",
      });
      continue;
    }
    if (matches.length === 1) {
      const { item: existing, fileAvailable, storedPath } = matches[0];
      attachmentKey = existing.key;
      if (!fileAvailable) {
        result.conflicts.push({
          parentKey: row.parentKey,
          path: row.path,
          attachmentKey,
          storedPath,
          reason: "existing-file-unavailable",
        });
        continue;
      }

      const changes = [];
      if (existing.attachmentContentType !== row.contentType) {
        changes.push({
          field: "contentType",
          from: existing.attachmentContentType,
          to: row.contentType,
        });
        existing.attachmentContentType = row.contentType;
      }
      const existingTitle = existing.getField("title");
      if (existingTitle !== row.title) {
        changes.push({ field: "title", from: existingTitle, to: row.title });
        existing.setField("title", row.title);
      }
      const existingTags = new Set(existing.getTags().map(({ tag }) => tag));
      const addedTags = row.tags.filter((tag) => !existingTags.has(tag));
      for (const tag of addedTags) existing.addTag(tag);
      if (addedTags.length) changes.push({ field: "tags", added: addedTags });

      if (changes.length) {
        phase = "update-existing";
        await existing.saveTx();
        result.updated.push({
          parentKey: row.parentKey,
          path: row.path,
          attachmentKey,
          changes,
        });
      } else {
        result.skipped.push({
          parentKey: row.parentKey,
          path: row.path,
          attachmentKey,
          reason: "already-correct",
        });
      }
      continue;
    }

    phase = "create";
    const attachment = await Zotero.Attachments.linkFromFile({
      file: row.path,
      parentItemID: parent.id,
      title: row.title,
      contentType: row.contentType,
    });
    attachmentKey = attachment.key;
    createdBeforeError = true;
    const createdRecord = {
      parentKey: row.parentKey,
      path: row.path,
      contentType: row.contentType,
      attachmentKey,
      metadataComplete: row.tags.length === 0,
    };
    result.created.push(createdRecord);

    if (row.tags.length) {
      phase = "save-created-tags";
      for (const tag of row.tags) attachment.addTag(tag);
      await attachment.saveTx();
      createdRecord.metadataComplete = true;
    }
  } catch (error) {
    result.errors.push({
      parentKey: row.parentKey,
      path: row.path,
      attachmentKey,
      phase,
      createdBeforeError,
      message: String(error && error.message ? error.message : error),
    });
  }
}

for (const name of ["created", "updated", "skipped", "missingParents", "conflicts", "errors"]) {
  result[name + "Count"] = result[name].length;
}
result.ok = result.missingParentsCount === 0
  && result.conflictsCount === 0
  && result.errorsCount === 0
  && result.created.every((item) => item.metadataComplete);

return JSON.stringify(result, null, 2);
`;

fs.writeFileSync(outputIdentity, zoteroScript, "utf8");
console.log(JSON.stringify({
  mappingRows: normalized.mappingRowCount,
  generatedRows: normalized.rows.length,
  duplicateRows: normalized.duplicateCount,
  outputPath: outputIdentity,
}, null, 2));
