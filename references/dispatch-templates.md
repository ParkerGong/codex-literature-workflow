# Dispatch Templates

These templates are intentionally explicit. The controller should fill placeholders and send them to fixed specialist sessions.

Every dispatch has a Markdown recording rule:

- Controller updates `controller_worklog.md` before sending and after reviewing the result.
- The target agent reads its own `agent_worklogs/<Agent>.md` before starting.
- The target agent updates its worklog before writing `Waiting review`.
- Context recovery begins from worklogs, handoff, and manifests, not from chat memory.

## Controller Pre-Dispatch Checklist

```markdown
# Controller Pre-Dispatch: <TASK_ID>

- project_profile: <generic|dissertation-strict|custom>
- controller_console: <thread/session id>
- controller_goal_status: <active|not-needed|pending>
- direction_source:
- direction_docs:
- collection_mapping_source:
- source_input_mode: <local-library|search-and-download|mixed>
- research_companion_default: academic-research-suite
- research_companion_auxiliary: research-lr-ra
- download_enabled: <true|false>
- local_library_paths:
- fixed target session:
- target session status: <idle|recovering|blocked>
- quota status: <reliable value|quota unknown|not applicable>
- quota decision:
- process check policy: <skip routine sweeps|enabled by project|symptom-driven>
- temp cleanup policy:
- allowed reads:
- allowed writes:
- forbidden paths:
- batch size:
- controller worklog:
- dependency setup record:
- target agent worklog:
- acceptance owner: Controller only
- previous batch status:
- reason this dispatch is safe to start:
```

Do not dispatch a new long batch when the previous batch is still `Working` or `Waiting review`.
Do not dispatch any long batch until one session is explicitly designated as the Controller Console and the required specialist session is created or recorded.

## LiteratureAgent Dispatch

```markdown
# Controller Dispatch: <TASK_ID> Literature Source Intake And Optional Acquisition

You are the fixed LiteratureAgent for this workflow. Do not create a new session and do not expand scope.

## Objective

Register, screen, or acquire literature for: <TOPIC_OR_DIRECTION>.

## Options

- source_input_mode: <local-library|search-and-download|mixed>
- research_companion_default: academic-research-suite
- research_companion_auxiliary: research-lr-ra
- download_enabled: <true|false>
- local_library_paths: <paths or none>
- language_scope: <english|chinese|both>
- access_mode: <open-only|authorized-browser|manual-user>
- closed_source_fallback: <none|chrome-then-computer-use-once>
- target_count: <N>
- zotero_enabled: <true|false>
- obsidian_enabled: <true|false>
- project_profile: <generic|dissertation-strict|custom>
- quota status: <value|quota unknown|not applicable>
- temp cleanup policy:

## Inputs

- Existing direction notes/manifests: <paths or none>
- Existing local PDFs/manifests: <paths or none>
- Dependency setup record: <00_controller/dependency_setup.md>
- Inclusion rules:
- Exclusion rules:
- Worklog path: <00_controller/agent_worklogs/LiteratureAgent.md>

## Allowed Writes

- Candidate table: <path>
- Source/download manifest: <path>
- Local library quality report: <path or none>
- Downloaded PDFs under: <path>
- LiteratureAgent worklog: <path>
- Handoff report: <path>

## Forbidden

- Do not bypass access controls.
- Use `academic-research-suite` as the default research companion for search strategy, query expansion, source verification, and screening logic when searching is enabled.
- Use `research-lr-ra` only as an auxiliary/fallback for legacy LR assistant work, research-gap mapping, representative-work selection, or a narrow subtask where the controller explicitly allows it.
- Do not search or download when `source_input_mode=local-library` unless the controller explicitly changes scope.
- Do not write Zotero sqlite.
- Do not create Obsidian notes.
- Do not process outside this topic.
- Do not run routine process-residue sweeps unless the controller explicitly enables them.

## Required Output

If `source_input_mode=local-library`, enumerate approved local PDFs, write source manifest rows with `access_route=local-library`, verify file size/page count/text status/title hints, detect duplicates, and mark download as `download-skipped`.
If searching is enabled, write a candidate table with query/date/source/URL/DOI/access route/relevance/status.
If `download_enabled=true`, download only legal/authorized PDFs and verify title, authors, body, page count, and file size.
For closed-source items, try Codex Chrome control first; if blocked by a UI/verification flow, make at most one Computer Use fallback attempt, then mark `captcha-blocked`, `manual-user`, or `downloaded`.
Write temp artifact path/size/count and any soft-move result.
Update the LiteratureAgent worklog with files read, files written, search/download actions, blockers, and next owner.
Stop at Waiting review and hand off to ZoteroAgent or Controller.
```

## ZoteroAgent Dispatch

```markdown
# Controller Dispatch: <TASK_ID> Zotero Linking

You are the fixed ZoteroAgent. Work only on the listed sources.

## Scope

Sources:
<table with source_id, title, DOI/URL, local_pdf, target collection, md_note_path if any>

## Options

- project_profile: <generic|dissertation-strict|custom>
- zotero_mode: <local-api|desktop-run-js|connector/manual>
- attach_pdf: <true|false>
- attach_md_note: <false by default; true only after note path is stable and user/project asks for it>
- strict_zotero_before_kb: <true|false>
- Worklog path: <00_controller/agent_worklogs/ZoteroAgent.md>

## Allowed Writes

- Zotero verification record: <path>
- Zotero link index or manifest updates: <path>
- ZoteroAgent worklog: <path>
- Updated note frontmatter if explicitly allowed: <paths or none>

## Forbidden

- Do not write zotero.sqlite directly.
- Do not change literature screening decisions.
- Do not create Obsidian notes unless explicitly asked.
- Do not store the local PDF path only in a parent URL field.

## Required Output

For each source, report:
- parent key/status;
- target collection/status;
- PDF linked-file status;
- optional MD linked-file status (`md-linked`, `pending-md-attachment`, `disabled`, or `manual-check`);
- verification method;
- exact pending/manual action if incomplete.

Update the ZoteroAgent worklog with API/Desktop/manual actions, verification evidence, skipped optional MD note link, blockers, and next owner.
Use pending/manual-check statuses honestly. Stop at Waiting review.
```

## ObsidianAgent Dispatch

```markdown
# Controller Dispatch: <TASK_ID> PDF-First Obsidian Ingest

You are the fixed ObsidianAgent. Do not create a new session, do not expand scope, and do not mark controller accepted.

## Preflight

- fixed session status: <idle|recovering>
- project_profile: <generic|dissertation-strict|custom>
- quota status:
- process check policy:
- temp cleanup policy:
- previous batch status:
- Worklog path: <00_controller/agent_worklogs/ObsidianAgent.md>

## Batch

- batch_size: <N>
- visual_check: <off|selected-pages|vision-model>
- render_cap: <N pages total>
- staging mode: <direct|staged-writes>

## Sources

<table with source_id, title, local_pdf, zotero_key, zotero_collection, zotero_status, existing_summary_path as secondary clue, md_note_path, duplicate/canonical status, boundary>

## Allowed Writes

- Literature notes:
  - <paths>
- Source registry:
- Zotero link index:
- Queue/status/log:
- ObsidianAgent worklog:
- Batch report:

## Forbidden

- Do not modify original PDFs or prior summaries.
- Do not write Zotero sqlite.
- Do not touch files outside allowed paths.
- Do not process sources outside this batch.
- Do not create an independent note for a duplicate alias.
- Do not treat existing summaries as primary evidence.
- Do not mark any output `controller-accepted`.

## PDF Reading

Use PDF-first reading. Existing summaries are secondary clues only.
Extract text, classify reading level, render only selected claim-bearing pages, and record TODO for unverified figures.
Respect `render_cap`. If the cap is insufficient, stop with TODO/RISK rather than rendering the whole PDF.

## Required Note Fields

Each literature note frontmatter must include:

- `source_id`
- `local_pdf`
- `zotero_key`
- `zotero_collection`
- `zotero_status`
- `md_note_path`
- `duplicate_aliases`
- `visual_verification_pages`
- `reading_level`
- `status: waiting-review`

## Required Output

Each note must include source_id, local PDF, Zotero status, page evidence, visual pages if any, RAG keywords, TODO/RISK, and use boundary.
Update the ObsidianAgent worklog with PDFs read, pages rendered, notes written, claims deferred, temp artifacts, and next owner.
Write a batch report with temp artifact size/path and status `Waiting review`.
```

## Controller Acceptance Checklist

```markdown
# Controller Acceptance: <TASK_ID>

- Output files exist:
- Paths are inside allowed writes:
- No forbidden paths touched:
- Source provenance present:
- Source input mode respected:
- Downloads were skipped when disabled:
- Local PDF quality verified:
- Zotero collection and attachment statuses checked:
- Zotero status honest:
- MD-Zotero note path/frontmatter checked:
- Obsidian notes include page evidence:
- Visual claims have visual status or TODO:
- Duplicate aliases handled:
- Quota/process/temp policies followed:
- Temp artifacts recorded:
- Controller and target agent worklogs updated:
- Sub-agent status was Waiting review:
- Accepted / blocked decision:
```

## Recovery Prompt

Use this only for the same fixed session after interruption, context compaction, or a partial run.

```markdown
# Controller Recovery Dispatch: <TASK_ID>

Continue only the previous assigned phase. Do not expand scope.

Read these durable records first:
- kanban:
- dispatch log:
- controller worklog:
- your agent worklog:
- source/download manifest:
- Zotero index:
- ingest status:
- previous handoff:

Current blocker or missing closeout:

Required action:

Write only the missing output/report and stop at `Waiting review`.
```
