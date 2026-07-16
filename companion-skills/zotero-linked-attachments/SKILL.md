---
name: zotero-linked-attachments
description: Prepare validated, user-run Zotero Desktop scripts that attach local PDF, Markdown, and other source files to existing parent items as linked_file attachments, then verify the resulting state read-only. Use when the user asks to put PDFs into Zotero, connect Markdown notes to Zotero items, fix items that open URL fields instead of file attachments, prepare a batch of local literature links, generate Zotero Run JavaScript, or verify PDF/MD attachment status through the local API.
---

# Zotero Linked Attachments

Use this skill to prepare user-run connections between local research files and Zotero items without copying files into scattered Zotero storage folders. The user performs writes through Zotero Desktop internal JavaScript; the agent uses the Zotero local API only for reads.

## Core Rule

- Treat Zotero as the authoritative reference manager.
- Attach PDF and Markdown notes as child `linked_file` attachments under the Zotero parent item.
- Do not use the parent item `url` field as a substitute for local files.
- Never write `zotero.sqlite` directly. Database-level recovery is outside this skill's scope.
- In the formal workflow, do not launch, control, paste into, or execute Zotero Desktop on the user's behalf. If the local API or Desktop is unavailable, report the live-integration blocker and keep generated files for a later user-run step.

## Workflow

1. Build or confirm a mapping file with one row per attachment.
2. Generate a Zotero Run JavaScript script from the mapping.
3. Ask the user to open Zotero Desktop internal `Run JavaScript`.
4. Ask the user to enable async execution, paste the generated script, run it, and return the structured result.
5. Verify every parent item through the read-only Zotero local API.
6. Update project indexes, logs, or note frontmatter with attachment status.

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

The mapping must be a nonempty array. Each source path must resolve to a regular file. Duplicate rows with the same parent and canonical path must agree on title, content type, and tags; conflicts fail before any Zotero action.

## Scripts

- `scripts/build_zotero_linked_attachment_js.mjs`: generate Zotero Desktop JavaScript from a JSON mapping file.
- `scripts/verify_zotero_linked_attachments.mjs`: verify expected linked-file attachments through `http://127.0.0.1:23119/api/users/0`.

Both scripts use exit `0` for success, `1` for a completed verification with missing/mismatched attachments, and `2` for invalid input or CLI usage where applicable. Read [`references/zotero-linked-file-notes.md`](references/zotero-linked-file-notes.md) for the relative-base-path and verification contract.
The builder refuses direct, symlink, and hard-link aliases between its mapping and output and never follows an output-file symlink.

## Zotero Desktop Execution

Open the internal JavaScript window by menu when available:

```text
Tools -> Developer -> Run JavaScript
```

If the menu is not exposed, stop and ask the user to open Zotero's Developer Run JavaScript window manually; do not launch an internal page on their behalf.

Ask the user to check `Run as async function`, paste the generated script, execute it, and return the JSON result. The generated script skips already-correct same-path children, updates safe metadata differences, refuses ambiguous/unavailable same-path conflicts, and returns `createdCount`, `updatedCount`, `skippedCount`, `missingParentsCount`, `conflictsCount`, `errorsCount`, attachment keys, and partial-create details.

## Verification Standard

After execution, verify each parent item has the expected child attachment:

- `linkMode` is `linked_file`.
- `contentType` matches the mapping.
- the resolved file URL matches the expected canonical local path. Zotero may store a linked attachment as `attachments:<relative-path>` when Linked Attachment Base Directory is configured, so the raw `path` field need not be absolute.
- For literature items with both source and note files, verify at least one PDF and one Markdown attachment when applicable.

If verification fails, inspect the returned child items before re-running. Re-running is idempotent for one unambiguous same-path attachment; multiple matches or an unavailable existing file are explicit conflicts, not silent duplicates.
