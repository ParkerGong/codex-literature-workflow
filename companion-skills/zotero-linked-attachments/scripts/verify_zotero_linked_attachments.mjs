#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

function usage() {
  console.error("Usage: node verify_zotero_linked_attachments.mjs <mapping.json> [--expect-pdf] [--api http://127.0.0.1:23119/api/users/0] [--timeout-ms 5000]");
  process.exit(2);
}

function defaultContentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".pdf") return "application/pdf";
  if (ext === ".md" || ext === ".markdown") return "text/markdown";
  if (ext === ".txt") return "text/plain";
  return "application/octet-stream";
}

function parseArgs(argv) {
  const args = {
    mappingPath: null,
    api: "http://127.0.0.1:23119/api/users/0",
    expectPdf: false,
    timeoutMs: 5000,
  };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--api") {
      if (i + 1 >= argv.length) usage();
      args.api = argv[++i];
    } else if (arg === "--timeout-ms") {
      if (i + 1 >= argv.length) usage();
      args.timeoutMs = Number(argv[++i]);
    } else if (arg === "--expect-pdf") {
      args.expectPdf = true;
    } else if (!args.mappingPath && !arg.startsWith("--")) {
      args.mappingPath = arg;
    } else {
      usage();
    }
  }
  if (!args.mappingPath) usage();
  if (!Number.isInteger(args.timeoutMs) || args.timeoutMs < 100 || args.timeoutMs > 120000) {
    console.error("--timeout-ms must be an integer from 100 to 120000");
    process.exit(2);
  }
  let apiURL;
  try {
    apiURL = new URL(args.api);
  } catch {
    console.error(`Invalid --api URL: ${args.api}`);
    process.exit(2);
  }
  if (!['http:', 'https:'].includes(apiURL.protocol)) {
    console.error("--api must use http or https");
    process.exit(2);
  }
  return args;
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
    const row = {
      parentKey: input.parentKey.trim(),
      path: canonicalPath,
      contentType: input.contentType === undefined
        ? defaultContentType(canonicalPath)
        : String(input.contentType).trim(),
    };
    if (!row.contentType) throw new Error(`Row ${index} has an empty contentType`);
    const identity = `${row.parentKey}\u0000${row.path}`;
    const previous = byIdentity.get(identity);
    if (previous) {
      if (previous.contentType !== row.contentType) {
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

function apiItemURL(api, itemKey, suffix) {
  const base = new URL(api.endsWith("/") ? api : `${api}/`);
  return new URL(`items/${encodeURIComponent(itemKey)}/${suffix}`, base);
}

function errorMessage(error) {
  const message = String(error?.message || error);
  const cause = error?.cause;
  if (!cause) return message;
  const causeMessage = String(cause?.message || cause);
  const code = cause?.code ? `${cause.code} ` : "";
  return `${message}: ${code}${causeMessage}`;
}

async function fetchResponse(url, timeoutMs) {
  let response;
  try {
    response = await fetch(url, {
      headers: { "Zotero-API-Version": "3" },
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch (error) {
    throw new Error(`Request failed for ${url}: ${errorMessage(error)}`);
  }
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText} for ${url}`);
  }
  return response;
}

async function fetchChildren(api, parentKey, timeoutMs) {
  const items = [];
  const seenItemIdentities = new Set();
  const limit = 100;
  let start = 0;
  while (true) {
    const url = apiItemURL(api, parentKey, "children");
    url.searchParams.set("limit", String(limit));
    url.searchParams.set("start", String(start));
    const response = await fetchResponse(url, timeoutMs);
    const batch = await response.json();
    if (!Array.isArray(batch)) {
      throw new Error(`Unexpected children response for ${parentKey}`);
    }
    let newItemCount = 0;
    for (const item of batch) {
      const itemKey = item?.key || item?.data?.key;
      const identity = typeof itemKey === "string" && itemKey
        ? `key:${itemKey}`
        : `json:${JSON.stringify(item)}`;
      if (!seenItemIdentities.has(identity)) {
        seenItemIdentities.add(identity);
        newItemCount++;
      }
    }
    if (batch.length > 0 && newItemCount === 0) {
      throw new Error(
        `Children pagination made no progress for ${parentKey}: page at start ${start} repeated previously seen items`,
      );
    }
    items.push(...batch);
    const totalHeader = response.headers.get("Total-Results");
    const total = totalHeader === null ? null : Number(totalHeader);
    if ((total !== null && Number.isFinite(total) && items.length >= total) || batch.length < limit) break;
    if (batch.length === 0) break;
    start += batch.length;
  }
  return items;
}

const args = parseArgs(process.argv.slice(2));
let normalized;
try {
  const mappingPath = fs.realpathSync.native(args.mappingPath);
  normalized = normalizeRows(JSON.parse(fs.readFileSync(mappingPath, "utf8")));
} catch (error) {
  console.error(String(error?.message || error));
  process.exit(2);
}

const childCache = new Map();
const resolvedPathCache = new Map();
async function childrenFor(parentKey) {
  if (!childCache.has(parentKey)) {
    childCache.set(parentKey, fetchChildren(args.api, parentKey, args.timeoutMs));
  }
  return childCache.get(parentKey);
}

async function resolveAttachmentPath(item) {
  const itemKey = item?.key || item?.data?.key;
  if (!itemKey) throw new Error("Attachment response is missing an item key");
  if (!resolvedPathCache.has(itemKey)) {
    resolvedPathCache.set(itemKey, (async () => {
      const url = apiItemURL(args.api, itemKey, "file/view/url");
      const response = await fetchResponse(url, args.timeoutMs);
      const value = (await response.text()).trim();
      let fileURL;
      try {
        fileURL = new URL(value);
      } catch {
        throw new Error(`Attachment ${itemKey} did not return a file URL: ${value}`);
      }
      if (fileURL.protocol !== "file:") {
        throw new Error(`Attachment ${itemKey} returned a non-file URL: ${value}`);
      }
      const localPath = fileURLToPath(fileURL);
      try {
        return fs.realpathSync.native(localPath);
      } catch {
        throw new Error(`Attachment ${itemKey} points to an unavailable file: ${localPath}`);
      }
    })());
  }
  return resolvedPathCache.get(itemKey);
}

const items = [];
for (const row of normalized.rows) {
  try {
    const children = await childrenFor(row.parentKey);
    const linkedChildren = children.filter((item) =>
      item?.data?.itemType === "attachment"
      && item?.data?.parentItem === row.parentKey
      && item?.data?.linkMode === "linked_file"
    );
    const resolvedChildren = [];
    for (const item of linkedChildren) {
      try {
        resolvedChildren.push({
          item,
          resolvedPath: await resolveAttachmentPath(item),
          resolveError: null,
        });
      } catch (error) {
        resolvedChildren.push({
          item,
          resolvedPath: null,
          resolveError: errorMessage(error),
        });
      }
    }

    const samePath = resolvedChildren.filter(({ resolvedPath }) => resolvedPath === row.path);
    const expected = samePath.find(({ item }) => item.data.contentType === row.contentType);
    const pdfCount = resolvedChildren.filter(({ item, resolvedPath }) =>
      Boolean(resolvedPath) && item.data.contentType === "application/pdf"
    ).length;
    let reason = null;
    if (samePath.length > 1) reason = "multiple-same-path-linked-files";
    else if (samePath.length === 0) reason = "resolved-path-not-found";
    else if (!expected) reason = "content-type-mismatch";
    else if (args.expectPdf && pdfCount < 1) reason = "expected-pdf-sibling-missing";

    items.push({
      parentKey: row.parentKey,
      expectedPath: row.path,
      expectedContentType: row.contentType,
      attachmentKey: expected?.item?.key || expected?.item?.data?.key || null,
      resolvedPath: expected?.resolvedPath || samePath[0]?.resolvedPath || null,
      pdfCount,
      ok: reason === null,
      reason,
      resolutionErrors: resolvedChildren
        .filter(({ resolveError }) => resolveError)
        .map(({ item, resolveError }) => ({
          attachmentKey: item?.key || item?.data?.key || null,
          error: resolveError,
        })),
    });
  } catch (error) {
    items.push({
      parentKey: row.parentKey,
      expectedPath: row.path,
      expectedContentType: row.contentType,
      attachmentKey: null,
      resolvedPath: null,
      pdfCount: 0,
      ok: false,
      reason: "api-or-verification-error",
      error: errorMessage(error),
    });
  }
}

const failures = items.filter((item) => !item.ok);
const result = {
  ok: failures.length === 0,
  mappingRows: normalized.mappingRowCount,
  verifiedRows: normalized.rows.length,
  duplicateRows: normalized.duplicateCount,
  okCount: items.length - failures.length,
  failureCount: failures.length,
  failures,
  items,
};

console.log(JSON.stringify(result, null, 2));
process.exit(result.ok ? 0 : 1);
