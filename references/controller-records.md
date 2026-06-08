# Controller Records And Anti-Drift Markdown

Long literature workflows drift when state lives only in chat. Before dispatching a long task, the controller should create or update a small set of Markdown records. These records are portable and can live in any project; adjust paths to the host repo.

## Minimal File Set

| File | Purpose | Owner |
| --- | --- | --- |
| `00_controller/initialization.md` | Controller Console designation, goal status, and specialist session creation plan | Controller |
| `00_controller/project_profile.md` | selected profile, options, host-project policy overrides | Controller |
| `00_controller/controller_worklog.md` | chronological controller decisions, dispatches, acceptance, and recovery notes | Controller |
| `00_controller/agent_worklogs/<Agent>.md` | per-agent read/write/action ledger for context recovery | each fixed specialist |
| `00_controller/controller_kanban.md` | active task board and acceptance state | Controller |
| `00_controller/session_registry.md` | fixed specialist sessions and their current role/status | Controller |
| `00_controller/dispatch_log.md` | sent/recovered/accepted/blocker history | Controller |
| `00_controller/source_manifest.md` | canonical source IDs, metadata, local paths, DOI/URL, access status | LiteratureAgent, Controller accepts |
| `00_controller/download_log.md` | attempted URLs, used URLs, browser/manual access notes, file sizes | LiteratureAgent |
| `00_controller/quota_status.md` | reliable quota reading, `quota unknown`, or pause decision when applicable | Controller |
| `00_controller/temp_artifacts.md` | temp paths, file counts, byte sizes, soft-move/delete/preserve state | current phase owner |
| `00_controller/zotero_link_index.md` | optional Zotero keys and linked-file status | ZoteroAgent |
| `00_controller/ingest_queue.md` | optional Obsidian batch queue | Controller |
| `00_controller/ingest_status.md` | optional Obsidian per-source status | ObsidianAgent, Controller accepts |
| `00_controller/handoff/<TASK_ID>.md` | latest durable handoff for one task | current phase owner |

Run `scripts/init_workspace.py --root <project-root>` to generate these placeholders.

## Worklog Requirement

The controller and every fixed specialist agent must write a Markdown worklog. This is separate from chat and separate from final batch reports.

Use worklogs to answer three recovery questions after context compaction:

1. What did this agent read?
2. What did this agent write or change?
3. What is the exact next action or blocker?

Required worklogs:

| Worklog | Writer | When to update |
| --- | --- | --- |
| `controller_worklog.md` | Controller | start/end of each controller turn, before dispatch, after receiving outputs, before acceptance |
| `agent_worklogs/LiteratureAgent.md` | LiteratureAgent | before search, after candidate screening, after each download batch, before handoff |
| `agent_worklogs/ZoteroAgent.md` | ZoteroAgent | before Zotero actions, after verification, after blockers, before handoff |
| `agent_worklogs/ObsidianAgent.md` | ObsidianAgent | before PDF reading, after note writes, after visual checks, before handoff |

If a project uses more agents, add one worklog per fixed agent. Do not create a separate worklog per paper.

## Worklog Entry Template

```markdown
## <ISO_DATETIME> - <TASK_ID> - <PHASE>

- Status: Working | Waiting review | Blocked | Done | Superseded
- Trigger:
- Files read:
- Files written:
- Sources touched:
- Actions completed:
- Decisions made:
- Evidence basis:
- Temp artifacts:
- TODO:
- RISK:
- Next action:
```

Recovery rule: after context compaction, an agent first reads `project_profile.md`, `session_registry.md`, its own worklog, the current task handoff, and the relevant manifest/index before doing new work.

## Status Vocabulary

Use a small vocabulary consistently:

- `candidate`: found but not selected;
- `selected`: selected for acquisition;
- `local-existing`: existing local PDF registered without downloading;
- `download-skipped`: download phase intentionally disabled;
- `downloaded`: local PDF present and basic checks passed;
- `manual-check`: user/manual repair needed;
- `captcha-blocked`: browser flow reached human verification that requires user action;
- `pending-import`: Zotero parent item not verified;
- `pdf-linked`: Zotero PDF linked-file verified;
- `md-linked`: Zotero MD linked-file verified;
- `waiting-review`: sub-agent output ready for controller review;
- `controller-accepted`: controller accepted into the project record;
- `blocked`: cannot progress without user/external action;
- `superseded`: replaced by a later dispatch or corrected source.
- `paused-quota`: controller paused because a reliable quota reading reached the host project's threshold.
- `quota-unknown`: quota could not be read reliably; record the uncertainty and avoid inventing a number.

## Controller Preflight Template

```markdown
# Controller Preflight

- Task ID:
- Project profile:
- Goal/mode:
- Quota status: reliable <value> | quota unknown | not applicable
- Quota decision:
- Process check policy:
- Temp cleanup policy:
- Fixed sessions:
- Allowed reads:
- Allowed writes:
- Forbidden paths:
- Acceptance owner:
- Notes:
```

## Kanban Template

```markdown
# Controller Kanban

## Active

| Task ID | Phase | Owner | Scope | Status | Expected output | Last durable update |
| --- | --- | --- | --- | --- | --- | --- |

## Backlog

| Task ID | Task | Priority | Inputs | Outputs | Suggested owner |
| --- | --- | --- | --- | --- | --- |

## Blocked

| Task ID | Blocker | Needed user/controller action |
| --- | --- | --- |

## Accepted

| Task ID | Accepted outputs | Evidence notes |
| --- | --- | --- |
```

## Session Registry Template

```markdown
# Session Registry

| Session name | Thread ID | Role | Status | Main artifacts | Next use |
| --- | --- | --- | --- | --- | --- |
| Controller | <id> | Controller | active | controller files | route and accept tasks |
| LiteratureAgent | <id> | Literature | idle | candidate/source/download manifests | search and acquisition |
| ZoteroAgent | <id> | Zotero | idle | zotero_link_index, verification | parent items and attachments |
| ObsidianAgent | <id> | Obsidian | idle | notes, ingest reports | PDF-first notes |
```

## Dispatch Log Template

```markdown
# Dispatch Log

| Time | Task ID | Target session | Action | Status | Notes |
| --- | --- | --- | --- | --- | --- |
```

## Per-Task Handoff Template

```markdown
# Handoff: <TASK_ID>

- Status:
- Owner this round:
- Started:
- Last updated:
- Scope:
- Options:
- Quota status:
- Process check:
- Worklog updated:
- Files read:
- Files written:
- Sources processed:
- Zotero status:
- Obsidian/RAG status:
- Temp artifacts:
- Evidence basis:
- TODO:
- RISK:
- Suggested next owner:
```

## Anti-Drift Rules

- Update the kanban before sending a long dispatch and after receiving outputs.
- Update the relevant worklog before and after meaningful work; do not rely on chat memory.
- A sub-agent must write `Waiting review` before the controller can accept.
- Do not mark a task `Done` from chat alone.
- If context compacts or a session recovers, read the records above before continuing.
- If a task runs for a long time, require batch reports after every small batch.
- If a phase is blocked, write the exact manual action needed and stop.
- Do not start the next batch while the previous batch is still `Working` or `Waiting review`.

## Quota Policy

Use a quota policy only when the host environment exposes a reliable quota reading.

- If reliable remaining quota is at or below the host project's pause threshold, do not start a new long search, PDF render batch, browser-download batch, or wide file modification. Write `Paused: quota <= <threshold>` in the kanban or handoff.
- If quota cannot be read reliably, write `quota unknown`; do not invent a percentage.
- If the user asks for a short inspection or report while quota is low, keep it bounded and do not start new worker sessions.
- A strict host project can set the threshold, for example `<=2%`.

## Process Check Policy

Do not run routine `ps`, `grep`, or process-residue sweeps as a default part of the workflow. Use process inspection only when:

- the user explicitly asks for it;
- the host project protocol enables it;
- there are real symptoms of a stuck browser, Zotero, renderer, or long-running process.

If a check is skipped because the project policy disables routine sweeps, record `process check skipped by policy`.

## Temporary Artifact Policy

The controller chooses a temp cleanup policy before dispatch. Recommended strict policy:

```text
temp_cleanup_mode=soft-move
temp_trash_root=/private/tmp/codex_agent_trash/<date>_<task-id>_<slug>/
```

Rules:

- Keep temp text dumps, selected-page renders, browser downloads in progress, and probe outputs outside the repository unless explicitly requested.
- Do not default to `rm -rf` for cleanup in strict projects.
- Soft-move disposable artifacts to the configured trash root, then report the moved path, file count, and total bytes.
- Preserve reusable virtual environments unless the controller explicitly decides to rebuild or remove them.
- If a temp artifact is intentionally preserved for debugging, record why and who should clean it later.
