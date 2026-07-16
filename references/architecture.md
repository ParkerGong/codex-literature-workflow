# Architecture And Controller Pattern

This workflow is controller-mediated. The controller keeps the global state small and reliable; specialist sessions keep domain context clean.

## Contents

- Roles and controller state
- Optional persistent-goal prompt
- Strict pipeline gates
- Companion routing and batch sizing

## Roles

| Role | Owns | Does not own |
| --- | --- | --- |
| Controller | task ID, scope, session routing, option flags, acceptance, status files, optional Git checkpoints, risk judgment | detailed reading of every paper unless doing a small recovery |
| LiteratureAgent | search strategy, screening, access route, legal PDF acquisition, local manifest | Zotero sqlite writes, final KB acceptance |
| ZoteroAgent | read-only parent/collection lookup, linked-file script preparation, verification | Zotero Desktop execution, search decisions, paper interpretation |
| ObsidianAgent | PDF-first reading, selective visual checks, Obsidian Wiki / LLM Wiki notes, manifest/source registry/Zotero index backfill, optional QMD/local RAG refresh handoff | web discovery, Zotero database writes, controller acceptance |
| User | research direction, login/CAPTCHA/payment/institutional consent, final approval | none |

Before using these roles for a long task, record the current session as the Controller Console unless the user already chose another controller. Create a persistent long-task goal only when the user explicitly requests one. Read `initialization.md` for the exact setup sequence.

Use existing long-running sessions when possible. Do not create a new session per paper or per small batch.

## Controller State Files

A portable project should maintain these files or equivalents:

- `controller_kanban.md`: active tasks and acceptance state.
- `project_profile.md`: profile choice, options, quota/process/temp policies.
- `controller_worklog.md`: controller decisions, dispatches, acceptance, and recovery notes.
- `agent_worklogs/<Agent>.md`: per-agent read/write/action logs for context recovery.
- `session_registry.md`: fixed specialist sessions and current status.
- `dispatch_log.md`: sent/recovered/accepted tasks.
- `git_checkpoints.md`: optional local checkpoint commits, privacy scan notes, and disabled/blocker status.
- `source_manifest.md`: local files, URLs, DOI, access route, status.
- `zotero_link_index.md`: optional Zotero keys and attachment status.
- `quota_status.md` and `temp_artifacts.md`: strict-project safeguards.
- `ingest_queue.md` / `ingest_status.md`: optional Obsidian batch tracking.
- `.manifest.json` in the target vault: optional Obsidian Wiki / LLM Wiki source manifest when Obsidian ingest is enabled.

Read `controller-records.md` for templates. These Markdown records are part of the workflow, not optional paperwork: they let another Codex session recover after long runs, context compaction, tool failures, or user interruption.

## Goal Mode Prompt

Use this prompt only when the user explicitly asks for a persistent goal:

```text
Goal: Build a source-grounded literature pipeline for <TOPIC_OR_DIRECTION>.

You are the Controller. Do not perform all phases yourself unless a phase is tiny.
Coordinate fixed specialist sessions:
- LiteratureAgent for search, screening, legal/authorized PDF acquisition, and source manifest.
- ZoteroAgent for optional parent/collection lookup, linked-file script preparation, and verification; the user runs Desktop writes.
- ObsidianAgent for optional PDF-first notes, Obsidian Wiki / LLM Wiki manifest-backed ingest, and QMD/local RAG refresh status.

Options:
- project_profile: <generic|dissertation-strict|custom>
- direction_source: <local-docs|user-prompt|agent-generated>
- direction_docs: <paths or none>
- collection_mapping_source: <local-docs|user-prompt|agent-proposed|none>
- source_input_mode: <local-library|search-and-download|mixed>
- download_enabled: <true|false>
- local_library_paths: <paths or none>
- language_scope: <english|chinese|both>
- zotero_enabled: <true|false>
- obsidian_enabled: <true|false>
- visual_check: <off|selected-pages|vision-model>
- batch_size: <N>
- access_mode: <open-only|authorized-browser|manual-user>
- closed_source_fallback: <none|chrome-then-computer-use-once>
- git_checkpoint_required: <true|false>
- git_checkpoint_interval: <3 meaningful file-writing steps or custom>
- git_checkpoint_root: <repo root>
- git_push_policy: <manual-only>
- quota_policy: <not-applicable|quota unknown|pause at <=N%>
- process_check_policy: <symptom-driven|project-enabled>
- temp_cleanup_policy: <preserve|soft-move to PATH|delete only when approved>

Rules:
- Use fixed sessions where available; do not create one session per paper.
- Every phase must write a durable handoff and update the controller or agent worklog.
- If the user enables local Git checkpoints, create them after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, after phase acceptance, and before pause/handoff. Do not auto-push.
- When checkpoints are enabled, if the target root is not a Git repository or safe staged paths are unclear, ask the user to designate another root, initialize Git, or disable checkpoints.
- Do not bypass access controls or write zotero.sqlite.
- Stop at Waiting review for sub-agent outputs; controller acceptance is separate.
- If blocked, write the blocker and next manual action rather than guessing.
- Zotero is optional. If enabled, resolve or record Zotero parent/collection/PDF attachment status before accepting linked Zotero outputs. Markdown note attachment is a later optional pass after note paths are stable.
- Download is optional. If local PDFs already exist, register and verify them before optional Zotero/Obsidian work.
- QMD is optional. If enabled, refresh and verify the local index after vault writes; if unavailable, skip and record `qmd_status`. Do not run embeddings unless approved.
- For closed-source downloads, prefer authenticated Chrome control; use Computer Use at most once as a fallback, then stop for user action if verification/login/payment remains.
- Do not invent quota. If quota is unknown, write `quota unknown`.

Start by reading/creating controller state files and asking for local direction/mapping docs when needed, then dispatch the first small batch only.
```

## Strict Pipeline Gate

For `project_profile=dissertation-strict`, the controller moves a source through these gates:

| Gate | Owner | Required durable output |
| --- | --- | --- |
| Direction and inclusion rules | Controller | project profile, kanban task, acceptance criteria |
| Local library intake when provided | LiteratureAgent | source manifest, local quality report, duplicate/problem statuses |
| Candidate search and screening when needed | LiteratureAgent | candidate table with queries, sources, scores, exclusion reasons |
| Optional Git checkpoint before acquisition | Controller | local commit recorded in `git_checkpoints.md` when checkpoints are enabled; otherwise `disabled` |
| Optional legal or authorized acquisition | LiteratureAgent | source manifest and download log with quality/fallback status |
| Optional Zotero parent and PDF linked file | ZoteroAgent | Zotero link index and verification record when Zotero is enabled |
| PDF-first reading | ObsidianAgent | note with page evidence and reading level |
| Selected visual checks | ObsidianAgent | rendered page evidence or explicit TODO/RISK |
| Obsidian Wiki ingest and manifest backfill | ObsidianAgent | `.manifest.json`, source registry, Zotero link index, one formal note per canonical source, optional concept/claim updates, batch report |
| QMD / local RAG refresh | ObsidianAgent or Controller-approved environment step | QMD status/search verification or fallback retrieval status |
| Optional MD note link to Zotero | ZoteroAgent | second-pass `md-linked` verification after note path is stable |
| Acceptance | Controller | checklist, checkpoint status when enabled, and status transition to accepted or blocked |

## Which Skills To Use

When installed, prefer these companion skills for each phase:

| Phase | Preferred companion |
| --- | --- |
| Broad literature planning, search strings, inclusion/exclusion logic | `academic-research-suite` by default; `research-lr-ra` auxiliary/fallback only |
| Browser search/download with current user session | `chrome:control-chrome`, then `computer-use` fallback |
| Zotero linked-file script preparation and read-only verification | `zotero-linked-attachments`; the user runs Desktop writes |
| Obsidian/wiki note conventions | `wiki-ingest` or `obsidian-wiki-ingest` |
| QMD/local RAG index refresh | optional `qmd`; lexical/sparse fallback when unavailable |
| Skill editing/testing | `skill-creator` |

If these are not installed, follow this skill's generic Markdown runbooks and record the missing dependency in `dependency_setup.md`.

## Batch Sizing

| Material | Recommended batch |
| --- | --- |
| Short papers with clean PDFs | 3-5 |
| Long surveys | 2-3 |
| Theses/books/reports | 1-2 |
| First test of a new environment | 1 |
| Paywalled/manual-access items | 1 at a time |

## Recovery Pattern

If a specialist session stops after receiving a dispatch but writes no durable output:

1. Keep the same fixed session if it is not corrupted.
2. Read `project_profile.md`, `session_registry.md`, controller worklog, target agent worklog, current handoff, and relevant manifests.
3. Send a recovery prompt that points to durable state files instead of repeating a long prior prompt.
4. Do not expand scope during recovery.
5. If content is written but report/temp cleanup is missing, send a closure-only follow-up.
6. Only create a new session after repeated system failure, severe context pollution, true isolation need, or explicit user approval.
