# Optional Obsidian And RAG-Ready Notes

Use this only when `obsidian_enabled=true` or the user asks for a knowledge base.

For the manifest-backed Obsidian Wiki / LLM Wiki contract, read `obsidian-wiki-ingest.md`. For optional QMD or fallback local RAG refresh after vault writes, read `qmd-rag.md`.

## Contents

- Connection modes, output files, and vault layout
- Literature-note structure and source links
- Optional project metadata and Zotero-note linking
- Visual checks, RAG readiness, link rules, and batch reports

## Connection Modes

This skill does not require Obsidian Desktop automation. Prefer file-based vault writes because they are portable and versionable.

| Mode | When to use | How |
| --- | --- | --- |
| `file-vault` | local Obsidian vault is a directory | write Markdown files directly under the vault |
| `staged-writes` | user wants review before formal KB writes | write notes under `_staging/`, then controller promotes |
| `existing-wiki-skill` | a wiki/Obsidian ingest skill is installed | follow that skill for local conventions |
| `no-obsidian` | user only wants PDFs/Zotero | keep source manifest and skip notes |

Before writing, the controller should define:

- vault root;
- note folder;
- source registry path;
- Zotero link index path, if Zotero is enabled or pending;
- whether staged writes are enabled;
- naming convention for `source_id` and note files;
- allowed concept/claim folders, if any.
- whether this run uses a strict project profile.

## Output Files

A typical Obsidian-enabled project writes:

- source registry row;
- Zotero link index row if Zotero is enabled or pending;
- one literature note per canonical source;
- optional concept pages for reusable technical ideas;
- optional claim cards for dissertation/report-ready claims;
- batch report;
- ingest queue/status/log updates.
- `.manifest.json` updates when the project uses Obsidian Wiki / LLM Wiki style ingestion.

## Minimal Vault Layout

```text
knowledge_base/
├── index.md
├── log.md
├── hot.md
├── 00_index/
├── 01_sources/
│   ├── source_registry.md
│   └── zotero_link_index.md
├── 02_literature_notes/
├── 03_concepts/
├── 04_claims/
└── _staging/
```

Projects may use different names. Preserve local conventions. A manifest-backed vault should include `.manifest.json` at the vault root.

## Literature Note Template

```markdown
---
source_id:
title:
authors_year:
source_type: paper
local_pdf:
zotero_key:
zotero_collection:
zotero_status:
md_note_path:
duplicate_aliases: []
visual_verification_pages: []
reading_level: text-ok | selected-visual | vision-model | scan-or-ocr | bad-pdf
status: waiting-review
---

# <Title>

## Source Links

- Local PDF:
- DOI/URL:
- Zotero:
- Zotero collection:
- Search/acquisition route:
- Markdown note path:

## TL;DR

## Research Question

## Method / Mechanism

## Evidence By Page

| Page | Evidence | Status |
| --- | --- | --- |

## Visual Verification

| Page | Figure/Table | What was checked | Status |
| --- | --- | --- | --- |

## Reusable Claims

## Limitations / Risks

## Dissertation Or Project Use Boundary

## RAG Keywords

## TODO
```

## Optional Project Metadata Fields

Some dissertation or report projects need extra frontmatter fields to make notes sortable by the writing plan. These are optional project metadata, not universal requirements:

| Field | Meaning | Use when |
| --- | --- | --- |
| `lr_direction` | literature-review direction or topic bucket | the project has several LR directions and wants notes grouped by direction |
| `chapter_target` | likely chapter, section, or report part where this source may be used | the knowledge base feeds a dissertation/report outline |
| `claim_type` | kind of reusable evidence, such as background, method, benchmark, limitation, or gap | the project builds claim cards or writing-ready evidence banks |

If the user does not understand or need these fields, leave them out. If a local direction document defines them, copy the controlled values from that document rather than inventing labels.

## MD-Zotero Link Rule

When Zotero is enabled or pending, every literature note frontmatter should include:

| Field | Meaning |
| --- | --- |
| `source_id` | stable ID used across manifest, Zotero index, and note |
| `zotero_key` | Zotero parent item key, or empty while pending |
| `zotero_collection` | target or verified collection name/key |
| `zotero_status` | `pending-import`, `parent-created`, `pdf-linked`, `md-linked`, `pending-attachment`, `pending-md-attachment`, or `manual-check` |
| `local_pdf` | project-local PDF path |
| `md_note_path` | path of this Markdown note, used for optional Zotero linked-file attachment |

Do not treat a note as fully linked until the Zotero index and note frontmatter agree.

## Visual Checks

Visual checks are optional but should be selected by evidence need, not by habit.

Render selected pages when claims depend on:

- architecture diagrams;
- model/pipeline diagrams;
- formulas whose symbol layout matters;
- experiment tables;
- ablation plots;
- result curves;
- screenshots or qualitative outputs.

Keep these statuses distinct:

- `CONFIRMED: text`;
- `CONFIRMED: visual-checked`;
- `INFERRED`;
- `TODO: visual verification`;
- `RISK`.

## RAG Readiness

A note is RAG-ready when it has:

- stable `source_id`;
- clear title/authors/year;
- local source path or URL/DOI;
- page-level evidence;
- concise TL;DR;
- method and limitation sections;
- keywords and concept links;
- uncertainty tags.

Do not create a note for duplicate aliases. Register the alias and point it to the canonical note.

QMD or fallback retrieval can index a RAG-ready note, but it does not make the note true. The note, manifest, source registry, Zotero index, and controller acceptance records remain the source of truth.

Duplicate rule:

- same DOI, same Zotero key, or same canonical PDF hash/title match means one canonical note;
- translated titles and filename variants go into `duplicate_aliases`;
- if a duplicate has useful metadata, add it to source registry or note aliases, not a separate literature note.

## Obsidian Link Rules

- Use stable wikilinks or relative Markdown links consistently with the host vault.
- Link literature notes to concept pages only when directly supported.
- Link claim cards only when the claim is evidence-backed.
- Mark uncertain synthesis as `INFERRED`, not fact.
- Keep frontmatter machine-readable and avoid project-private secrets.
- Treat existing summaries as secondary clues only. The PDF and recorded page evidence are primary.
- Do not modify original PDFs, prior summaries, or source files unless the controller explicitly includes them in allowed writes.

## Strict Obsidian Dispatch Rules

For strict profiles, ObsidianAgent should not begin until the controller dispatch includes:

- fixed session name or thread ID and confirmation that the session is idle or ready for recovery;
- exact source table with `source_id`, title, local PDF, Zotero key/status, collection, existing summary path if any, and use boundary;
- allowed write paths for literature notes, source registry, Zotero link index, queue/status/log, and report;
- render cap, usually a small total page count for the batch;
- temp artifact policy;
- forbidden paths;
- required final status: `Waiting review`.

The ObsidianAgent should write no independent note for duplicate aliases and should not mark any output `controller-accepted`.

## Batch Report

Every Obsidian batch report should include:

- status: usually `Waiting review`;
- files read and written;
- sources processed;
- text evidence pages;
- visual verification pages;
- Zotero status;
- duplicate handling;
- temp artifact path, size, file count, cleanup/move state;
- forbidden paths not touched;
- TODO/RISK;
- suggested next owner.
