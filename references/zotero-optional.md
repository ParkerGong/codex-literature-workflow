# Optional Zotero Workflow

Use this only when `zotero_enabled=true` or the user explicitly asks for Zotero.

## Principles

- Never write `zotero.sqlite` directly.
- Prefer Zotero Desktop linked-file attachments so project-local PDFs stay in place.
- Do not put a local PDF path only in the parent item's URL field.
- Verify parent item, collection, PDF attachment, and optional note attachment when that optional stage is enabled.
- If verification is unavailable, record `pending-*` status honestly.

## Connection Modes

| Mode | When to use | Notes |
| --- | --- | --- |
| `local-api` | Zotero Desktop local API is enabled and reachable | best for read/verify |
| `desktop-run-js` | attachments must be created as linked files | use Zotero Developer Run JavaScript or approved wrapper |
| `connector/manual` | user imports through browser connector | record parent key/status after user action |
| `disabled` | user does not want Zotero | keep DOI/URL/local PDF in source manifest |

The controller should state which mode is allowed before dispatching ZoteroAgent.

## Status Values

| Status | Meaning |
| --- | --- |
| `pending-import` | no verified parent item yet |
| `parent-created` | Zotero parent exists, attachment not verified |
| `pdf-linked` | PDF linked-file attachment verified |
| `md-linked` | Markdown note linked-file attachment verified |
| `pending-attachment` | parent exists, attachment not complete |
| `pending-md-attachment` | parent/PDF state is known, but Markdown note linked-file attachment is not complete |
| `collection-missing` | parent exists but target collection membership is not verified |
| `verification-failed` | expected state could not be verified by API, Desktop JS output, or manual confirmation |
| `manual-check` | user/Zotero action required |

## Recommended Flow

1. Locate existing parent item by DOI, title, or known key.
2. If absent, import from DOI/BibTeX/RIS or create via approved Zotero tooling.
3. Ensure item is in the requested collection.
4. Attach local PDF as linked file.
5. Do not attach an Obsidian Markdown note by default. Only attach the MD note after the note path is stable and the user or project explicitly asks for Zotero to link notes.
6. Verify through local Zotero API if available.
7. If local API is unavailable but Zotero Desktop Run JavaScript returns structured output, save that output as the verification record.

## Strict Zotero Gate When Enabled

Use this mode when Zotero is enabled in a host project. Zotero itself remains optional for the overall skill.

Recommended before ObsidianAgent starts when Zotero is enabled:

- source row exists in `source_manifest.md`;
- target Zotero collection is known or explicitly pending;
- Zotero parent item status is one of: verified, `pending-import`, or `manual-check`;
- PDF linked-file status is one of: `pdf-linked`, `pending-attachment`, or `manual-check`;
- MD linked-file status is usually `disabled` or `pending-md-attachment` until Obsidian has produced a final stable note path.

The controller may allow Obsidian to proceed with pending Zotero fields only when the pending state is written into both the Zotero link index and the note frontmatter.

## Two-Stage Markdown Note Linking

Default: `attach_md_note=false`.

Recommended sequence:

1. ZoteroAgent links or records the PDF and parent/collection status.
2. ObsidianAgent creates or promotes the final Markdown note.
3. Controller confirms the final `md_note_path`.
4. ZoteroAgent runs a second optional pass with `attach_md_note=true`.
5. ZoteroAgent updates `md_status` from `pending-md-attachment` or `disabled` to `md-linked`.

Use `pending-md-attachment` only when the user/project wants the note linked but the path is not stable yet. Use `disabled` when Markdown note linking is not requested.

## Zotero Link Index Template

```markdown
# Zotero Link Index

| source_id | zotero_key | zotero_collection | parent_status | pdf_status | md_status | local_pdf | md_note_path | verification | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Recommended status combinations:

| Situation | parent_status | pdf_status | md_status |
| --- | --- | --- | --- |
| fully linked PDF, no MD requested | `parent-created` or `verified` | `pdf-linked` | `disabled` |
| PDF linked, MD note exists but not attached | `verified` | `pdf-linked` | `pending-md-attachment` |
| parent exists but PDF missing | `verified` | `pending-attachment` | `pending-md-attachment` or `disabled` |
| user must act in Zotero | `manual-check` | `manual-check` | `manual-check` |

## Local API Probe

When available, verify Zotero through `http://127.0.0.1:23119/` or the host's Zotero plugin/tooling:

- search parent by title/DOI;
- verify collection membership;
- list child attachments;
- compare attachment paths with the project-local PDF/MD paths.

If the API fails because Zotero is closed, ask before launching GUI apps in environments that require approval. If the API fails while Zotero is open, record the failure and use Desktop JS/manual verification instead of guessing.

## Zotero Desktop Run JavaScript Pattern

Use this pattern only inside Zotero Desktop Developer tools or an approved automation wrapper:

```javascript
const attachment = await Zotero.Attachments.linkFromFile({
  file: row.path,
  parentItemID: parent.id,
  contentType: row.contentType || "application/pdf",
});
attachment.setField("title", row.title);
await attachment.saveTx();
```

The result must include:

- parent key;
- attachment key;
- path;
- content type;
- created/skipped/error counts.

## Verification Record

Write a JSON or Markdown record with:

- checked time;
- method: local API, Zotero Desktop JS result, manual user confirmation;
- parent collection;
- parent keys;
- expected and actual PDF/MD attachments;
- source manifest row and note frontmatter fields checked;
- missing attachments;
- errors;
- next action.

If Zotero is optional and disabled, source records should still include DOI/URL/local PDF path so Zotero can be added later.

## Optional Markdown Note Attachment

Only attach Markdown notes to Zotero when the user or project profile wants Zotero to open the project note from the parent item.

Rules:

- attach the Markdown file as a linked file, not a copied attachment, unless the user requests copied storage;
- set content type to `text/markdown` when the automation supports it;
- verify that `md_note_path` in the note frontmatter matches the linked attachment path;
- if the note is staged and may move later, record `pending-md-attachment` until the final path is stable.
