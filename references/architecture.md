# Architecture And Controller Pattern

This workflow is controller-mediated. The controller keeps the global state small and reliable; specialist sessions keep domain context clean.

## Roles

| Role | Owns | Does not own |
| --- | --- | --- |
| Controller | task ID, scope, session routing, option flags, acceptance, status files, Git checkpoints, risk judgment | detailed reading of every paper unless doing a small recovery |
| LiteratureAgent | search strategy, screening, access route, legal PDF acquisition, local manifest | Zotero sqlite writes, final KB acceptance |
| ZoteroAgent | parent item lookup/import, collection placement, linked-file attachments, verification | search decisions, paper interpretation |
| ObsidianAgent | PDF-first reading, selective visual checks, notes, concepts, source registry, batch report | web discovery, Zotero database writes, controller acceptance |
| User | research direction, login/CAPTCHA/payment/institutional consent, final approval | none |

Before using these roles for a long task, designate one session as the Controller Console and attach the long-task goal. Read `initialization.md` for the exact setup sequence.

Use existing long-running sessions when possible. Do not create a new session per paper or per small batch.

## Controller State Files

A portable project should maintain these files or equivalents:

- `controller_kanban.md`: active tasks and acceptance state.
- `project_profile.md`: profile choice, options, quota/process/temp policies.
- `controller_worklog.md`: controller decisions, dispatches, acceptance, and recovery notes.
- `agent_worklogs/<Agent>.md`: per-agent read/write/action logs for context recovery.
- `session_registry.md`: fixed specialist sessions and current status.
- `dispatch_log.md`: sent/recovered/accepted tasks.
- `git_checkpoints.md`: forced local checkpoint commits and privacy scan notes.
- `source_manifest.md`: local files, URLs, DOI, access route, status.
- `zotero_link_index.md`: optional Zotero keys and attachment status.
- `quota_status.md` and `temp_artifacts.md`: strict-project safeguards.
- `ingest_queue.md` / `ingest_status.md`: optional Obsidian batch tracking.

Read `controller-records.md` for templates. These Markdown records are part of the workflow, not optional paperwork: they let another Codex session recover after long runs, context compaction, tool failures, or user interruption.

## Goal Mode Prompt

Use a goal when the controller should persist across a long workflow:

```text
Goal: Build a source-grounded literature pipeline for <TOPIC_OR_DIRECTION>.

You are the Controller. Do not perform all phases yourself unless a phase is tiny.
Coordinate fixed specialist sessions:
- LiteratureAgent for search, screening, legal/authorized PDF acquisition, and source manifest.
- ZoteroAgent for optional Zotero parent items and linked-file attachments.
- ObsidianAgent for optional PDF-first notes and RAG-ready knowledge base ingest.

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
- Force local Git checkpoint commits after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, after phase acceptance, and before pause/handoff. Do not auto-push.
- If the target root is not a Git repository or safe staged paths are unclear, stop before long work and ask the user.
- Do not bypass access controls or write zotero.sqlite.
- Stop at Waiting review for sub-agent outputs; controller acceptance is separate.
- If blocked, write the blocker and next manual action rather than guessing.
- Zotero is optional. If enabled, resolve or record Zotero parent/collection/PDF attachment status before accepting linked Zotero outputs. Markdown note attachment is a later optional pass after note paths are stable.
- Download is optional. If local PDFs already exist, register and verify them before optional Zotero/Obsidian work.
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
| Git checkpoint before acquisition | Controller | local commit recorded in `git_checkpoints.md` |
| Optional legal or authorized acquisition | LiteratureAgent | source manifest and download log with quality/fallback status |
| Optional Zotero parent and PDF linked file | ZoteroAgent | Zotero link index and verification record when Zotero is enabled |
| PDF-first reading | ObsidianAgent | note with page evidence and reading level |
| Selected visual checks | ObsidianAgent | rendered page evidence or explicit TODO/RISK |
| KB/RAG ingest | ObsidianAgent | source registry, note, optional concept/claim updates, batch report |
| Optional MD note link to Zotero | ZoteroAgent | second-pass `md-linked` verification after note path is stable |
| Acceptance | Controller | checklist, latest checkpoint status, and status transition to accepted or blocked |

## Which Skills To Use

When installed, prefer these companion skills for each phase:

| Phase | Preferred companion |
| --- | --- |
| Broad literature planning, search strings, inclusion/exclusion logic | `academic-research-suite` by default; `research-lr-ra` auxiliary/fallback only |
| Browser search/download with current user session | `chrome:control-chrome`, then `computer-use` fallback |
| Zotero linked-file attachment | `zotero-linked-attachments` or the Zotero plugin |
| PDF rendering and selected-page QA | `pdf` |
| Obsidian/wiki note conventions | `wiki-ingest` or `obsidian-wiki-ingest` |
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
