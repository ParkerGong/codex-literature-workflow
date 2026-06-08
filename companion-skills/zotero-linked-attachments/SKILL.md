---
name: zotero-linked-attachments
description: Attach local PDF, Markdown, and other source files to existing Zotero parent items as linked_file attachments. Use when the user asks to put PDFs into Zotero, connect Markdown notes to Zotero items, fix Zotero items that open URL fields instead of file attachments, batch attach local literature files, generate Zotero Run JavaScript scripts, or verify Zotero PDF/MD attachment status through the local API.
---

# Zotero Linked Attachments

Use this skill to connect local research files to Zotero items without copying files into scattered Zotero storage folders. Prefer Zotero Desktop internal JavaScript for writes and Zotero local API for reads.

## Core Rule

- Treat Zotero as the authoritative reference manager.
- Attach PDF and Markdown notes as child `linked_file` attachments under the Zotero parent item.
- Do not use the parent item `url` field as a substitute for local files.
- Do not write `zotero.sqlite` directly unless the user explicitly approves a database-level recovery operation.

## Workflow

1. Build or confirm a mapping file with one row per attachment.
2. Generate a Zotero Run JavaScript script from the mapping.
3. Open Zotero Desktop internal `Run JavaScript`.
4. Enable async execution.
5. Paste and run the generated script.
6. Verify every parent item through the Zotero local API.
7. Update project indexes, logs, or note frontmatter with attachment status.

## Mapping Format

Use JSON when possible:

```json
[
  {
    "parentKey": "374X93AF",
    "path": "/absolute/path/to/note.md",
    "title": "literature-note-example.md",
    "contentType": "text/markdown",
    "tags": ["literature-note", "markdown-note"]
  }
]
```

Use `application/pdf` for PDFs and `text/markdown` for Markdown notes. Always use absolute paths.

## Scripts

- `scripts/build_zotero_linked_attachment_js.mjs`: generate Zotero Desktop JavaScript from a JSON mapping file.
- `scripts/verify_zotero_linked_attachments.mjs`: verify expected linked-file attachments through `http://127.0.0.1:23119/api/users/0`.

## Zotero Desktop Execution

Open the internal JavaScript window by menu when available:

```text
Tools -> Developer -> Run JavaScript
```

If the menu is not exposed on macOS, the internal page can be opened with:

```bash
/Applications/Zotero.app/Contents/MacOS/zotero -chrome chrome://zotero/content/runJS.html
```

In the window, check `Run as async function`, paste the generated script, and execute it. The generated script skips existing same-path child attachments and returns JSON with `createdCount`, `skippedCount`, `missingParents`, `errors`, and attachment keys.

## Verification Standard

After execution, verify each parent item has the expected child attachment:

- `linkMode` is `linked_file`.
- `contentType` matches the mapping.
- `path` matches the expected absolute local path.
- For literature items with both source and note files, verify at least one PDF and one Markdown attachment when applicable.

If verification fails, inspect the returned child items before re-running. Re-running the generated script is safe for same-path duplicates because it skips existing attachments.
