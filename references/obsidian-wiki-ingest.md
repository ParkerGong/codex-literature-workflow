# Obsidian Wiki Ingest And Manifest Backfill

Use this reference when `obsidian_enabled=true`, the user asks for an Obsidian/LLM Wiki style knowledge base, or the controller needs to backfill manifest/source-registry/Zotero-index state after PDF-first reading.

This phase is file-first. Obsidian Desktop automation is not required. The controller owns scope and acceptance; the fixed ObsidianAgent writes bounded vault files and stops at `Waiting review`.

## Source Of Truth

The source of truth is the vault Markdown plus durable controller records:

- `.manifest.json`
- `index.md`
- `hot.md`
- `log.md`
- `01_sources/source_registry.md`
- `01_sources/zotero_link_index.md`
- `02_literature_notes/`
- optional `03_concepts/`
- optional `04_claims/`
- optional `_staging/`

QMD or any other index is search infrastructure only. It is not the authority for source facts, Zotero status, or note acceptance.

## Required Literature Note Fields

Every formal literature note should include:

- `source_id`
- title
- authors/year if known
- source type
- canonical PDF/source path
- duplicate aliases
- Zotero key/status
- local summary path if any
- text evidence pages
- visual verification pages
- `CONFIRMED` / `INFERRED` / `TODO` / `RISK`
- RAG/query keywords
- dissertation/project-use boundary
- avoid-overclaim notes
- Obsidian Wiki ingest metadata

## Required Manifest Fields

Every canonical source manifest entry should include:

| Field | Requirement |
| --- | --- |
| source key / canonical path | stable source pointer |
| `source_id` | stable workflow ID |
| `zotero_key` | Zotero parent key or empty/pending |
| `zotero_status` | verified, pending, disabled, or manual-check state |
| `ingested_at` | timestamp for ingest/write |
| `size_bytes` | canonical source size when local |
| `modified_at` | source mtime when local |
| `content_hash` | hash of canonical source when available |
| `hash_algorithm` | `sha256` |
| `source_type` | usually `document` |
| `pages_created` | written page paths |
| `pages_updated` | updated page paths |
| `note_path` | formal literature note path |
| `controller_task` | task ID or dispatch ID |
| `ingest_mode` | append, full, raw, staged, or repair |
| `status` | waiting-review, controller-accepted, manual-check, duplicate-alias, etc. |
| `qmd_status` | refreshed, skipped, failed, vectors-pending, etc. |
| `qmd_reason` | short reason when skipped or failed |

## Dedup Policy

- One canonical source gets one formal note.
- Duplicate aliases are report-only unless the controller explicitly decides otherwise.
- Duplicate metadata may be recorded in the manifest, source registry, note aliases, or batch report.
- Wrong, incomplete, encrypted, scan-only, or mismatched PDFs become `manual-check`, not formal notes.

## Minimal Batch Flow

1. Confirm vault root, allowed write paths, source registry path, Zotero link index path, and staging policy.
2. Read source/download manifest rows, Zotero link index rows, existing source registry rows, and any existing `.manifest.json`.
3. Assign or reuse stable `source_id` values.
4. Detect canonical sources and duplicate aliases.
5. For each valid canonical source, create or update one formal note in `02_literature_notes/`.
6. Update `.manifest.json`, `01_sources/source_registry.md`, and `01_sources/zotero_link_index.md` when Zotero is enabled or pending.
7. Update `index.md`, `hot.md`, and `log.md` only with source-grounded status.
8. Write a batch report with `Waiting review`.
9. Hand off to the controller for acceptance, then optional QMD/local RAG refresh.

## Waiting Review Gate

ObsidianAgent output is not accepted evidence until the Controller checks:

- note exists for each canonical source and no duplicate alias became a separate formal note;
- `.manifest.json`, source registry, Zotero link index, and note frontmatter agree;
- text/page evidence is present or TODO/RISK is explicit;
- bad/wrong/incomplete PDFs are `manual-check`;
- QMD/local RAG status is recorded but not treated as source authority;
- no forbidden path, original PDF, Zotero database, browser cookie, or private vault file was modified outside allowed writes.
