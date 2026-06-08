#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

function usage() {
  console.error("Usage: node verify_zotero_linked_attachments.mjs <mapping.json> [--expect-pdf] [--api http://127.0.0.1:23119/api/users/0]");
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
  const args = { mappingPath: null, api: "http://127.0.0.1:23119/api/users/0", expectPdf: false };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--api") {
      args.api = argv[++i];
    } else if (arg === "--expect-pdf") {
      args.expectPdf = true;
    } else if (!args.mappingPath) {
      args.mappingPath = arg;
    } else {
      usage();
    }
  }
  if (!args.mappingPath) usage();
  return args;
}

function normalizeRows(rawRows) {
  if (!Array.isArray(rawRows)) {
    throw new Error("Mapping JSON must be an array");
  }
  return rawRows.map((row, index) => {
    if (!row?.parentKey || !row?.path) {
      throw new Error(`Row ${index} must include parentKey and path`);
    }
    return {
      parentKey: String(row.parentKey),
      path: String(row.path),
      contentType: row.contentType ? String(row.contentType) : defaultContentType(String(row.path)),
    };
  });
}

async function fetchChildren(api, parentKey) {
  const url = `${api.replace(/\/$/, "")}/items/${encodeURIComponent(parentKey)}/children`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText} for ${url}`);
  }
  return response.json();
}

const args = parseArgs(process.argv.slice(2));
const rows = normalizeRows(JSON.parse(fs.readFileSync(args.mappingPath, "utf8")));
const items = [];

for (const row of rows) {
  try {
    const children = await fetchChildren(args.api, row.parentKey);
    const expected = children.find((item) =>
      item?.data?.linkMode === "linked_file"
      && item?.data?.contentType === row.contentType
      && item?.data?.path === row.path
    );
    const pdfCount = children.filter((item) =>
      item?.data?.linkMode === "linked_file"
      && item?.data?.contentType === "application/pdf"
    ).length;
    const ok = Boolean(expected) && (!args.expectPdf || pdfCount >= 1);
    items.push({
      parentKey: row.parentKey,
      expectedContentType: row.contentType,
      attachmentKey: expected?.key || null,
      pdfCount,
      ok,
    });
  } catch (error) {
    items.push({
      parentKey: row.parentKey,
      expectedContentType: row.contentType,
      attachmentKey: null,
      pdfCount: 0,
      ok: false,
      error: String(error && error.message ? error.message : error),
    });
  }
}

const failures = items.filter((item) => !item.ok);
const result = {
  count: items.length,
  okCount: items.length - failures.length,
  failures,
  items,
};

console.log(JSON.stringify(result, null, 2));
process.exit(failures.length ? 1 : 0);
