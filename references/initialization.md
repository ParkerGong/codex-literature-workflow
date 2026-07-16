# Initialization And Controller Console Protocol

Use this reference whenever a user starts a new long literature workflow or asks to initialize a target project.

## Contents

- Controller ownership and startup questions
- Session topology and setup sequence
- Recommended prompts and durable records
- Initialization stop conditions

## Non-Negotiable Initialization Rule

For a long multi-phase run, the active Codex session becomes the **Controller Console** unless the user has already selected another controller. Record that choice in the workspace; do not block merely to ask the user to rename the current session.

The Controller Console:

- owns the in-session plan and, only when the user explicitly requested persistent goal tracking, the active goal;
- initializes or updates all `00_controller/` records;
- owns local Git checkpoint commits when the user enables them for the target project root;
- verifies dependency status before long batches;
- creates or reuses fixed specialist sessions;
- dispatches bounded work to specialists;
- reviews durable handoff output;
- is the only session allowed to mark outputs accepted.

Specialist sessions do not accept final output and do not expand scope.

## Required User Questions Before Work

Before a full multi-phase search/download/Zotero/Obsidian run, the Controller Console must confirm the startup scope. If the latest user message or existing project records already answer a field, record that answer and ask only for missing fields. For a bounded, read-only, or single-phase task, ask only the fields that can materially change that task; do not impose the full questionnaire.

Required questions:

1. What is the paper direction or research boundary?
2. How many papers should the first batch target?
3. Are sources already local PDFs, new search/download, or mixed?
4. Should new PDF download/acquisition be enabled? If yes, is only open access allowed, or may authorized browser/manual access be used?
5. What language scope should be used: English, Chinese, or both?
6. Should Zotero be connected for parent items, collections, and linked PDF attachments?
7. Should Obsidian/RAG-ready notes be created?
8. If Zotero is enabled, what collection, collection mapping, or mapping document should be used?
9. If Obsidian is enabled, what vault/project root and allowed write paths should be used?
10. Are there existing local direction documents, literature indexes, PDF folders, manifests, or Zotero/Obsidian mapping files?
11. If QMD retrieval is enabled, which collection name should be reused or created, and has embedding/network use been approved?
12. Should local Git checkpoints be enabled? If yes, which target project root should receive them?

Record answers in `project_profile.md`. Set `user_scope_confirmed: true` only after required answers are present. Do not dispatch long specialist work while `user_scope_confirmed=false`.

## Required Session Topology

| Session | Required before phase | If missing |
| --- | --- | --- |
| Controller Console | all phases | use the current session unless the user already chose another controller |
| LiteratureAgent | search, screening, local library intake, download | create/reuse one fixed session when multi-agent execution is available; otherwise run the phase sequentially and record that fallback |
| ZoteroAgent | read-only lookup, linked-file script preparation, verification | create/reuse only when Zotero is enabled and multi-agent execution is available; otherwise run sequentially |
| ObsidianAgent | PDF-first reading and Obsidian/RAG ingest | create/reuse only when Obsidian/RAG output is enabled and multi-agent execution is available; otherwise run sequentially |

Do not create one session per paper. Reuse fixed specialist sessions for batches.

## Controller Setup Sequence

1. Record the current session as the Controller Console unless the user already selected another controller.
2. If the user explicitly requested persistent goal tracking, create or attach a goal using the recommended goal prompt; otherwise keep the plan in the controller records.
3. Run `scripts/init_workspace.py --root <target-project>` if controller records do not exist.
4. Ask the required user startup questions above and record answers in `00_controller/project_profile.md`.
5. Read and fill `00_controller/project_profile.md`; do not continue until `user_scope_confirmed=true`.
6. If local Git checkpoints are enabled, verify the target root is a Git repository. If not, ask the user to initialize Git, designate another root, or continue without checkpoints.
7. If checkpoints are enabled, create the first local checkpoint after initialization and scope records are written. Record it in `00_controller/git_checkpoints.md`.
8. Read `references/dependencies.md`, recommend installing or enabling missing companion skills/plugins that match the requested workflow, and fill `00_controller/dependency_setup.md`.
9. Run or request the permanent environment check:

```bash
micromamba activate codex-literature  # or: mamba/conda activate codex-literature
python3 <skill-root>/scripts/env_check.py --json --strict
```

10. Read `00_controller/session_registry.md`.
11. Reuse fixed specialist sessions when listed and active.
12. If a required specialist session is missing, create it or ask the user to create it, then record its ID.
13. If checkpoints are enabled, create another local checkpoint after dependency and session records are updated.
14. Write the first dispatch to `00_controller/dispatch_log.md`.
15. Send the bounded dispatch prompt from `references/dispatch-templates.md`.
16. Wait for a durable handoff before dispatching the next phase.
17. When checkpoints are enabled, create one after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, and before pausing or handing off.

## Recommended Controller Prompt

```text
You are the Controller Console for codex-literature-workflow.
Do not do all work yourself.
Initialize controller records, verify dependencies, choose or create fixed specialist sessions, then dispatch small bounded tasks.
Before a full multi-phase dispatch, confirm paper direction, target count, source mode, download/access permission, Zotero connection, Obsidian connection, local inputs, output paths, mapping needs, optional QMD settings, and whether Git checkpoints are enabled.
Use academic-research-suite as the default literature discovery/screening companion.
Use research-lr-ra only as auxiliary/fallback.
If the user enables local Git checkpoints, create them after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, and before pausing or handoff. Do not auto-push.
Only the Controller Console may mark outputs accepted.
```

## Recommended Long-Task Goal Prompt

```text
Goal: Build a source-grounded Zotero and Obsidian-ready literature workspace for <TOPIC_OR_DIRECTION>.

You are the Controller Console for codex-literature-workflow.

Rules:
- Keep this session as the only controller and acceptance owner.
- Do not perform every phase yourself unless a phase is tiny.
- Create or reuse fixed specialist sessions:
  - LiteratureAgent for ARS-led search, screening, legal/authorized acquisition, and source manifests.
  - ZoteroAgent for parent/collection lookup, linked PDF/MD script preparation, and verification; the user runs Desktop writes.
  - ObsidianAgent for PDF-first reading, selected visual checks, and Obsidian/RAG-ready notes.
- If a specialist session does not exist, create it or ask the user to create it, then record the thread/session ID.
- Before any long batch, initialize controller records and dependency_setup.md.
- Before a full multi-phase search/download/Zotero/Obsidian/PDF-reading run, ask only for missing material scope fields: paper direction, expected paper count, source input mode, download/access permission, language scope, Zotero connection, Obsidian connection, local input paths, output paths, collection/vault/QMD mapping needs, and whether Git checkpoints are enabled.
- Record those answers in project_profile.md and set user_scope_confirmed=true before dispatch.
- If Git checkpoints are enabled, verify the target root is a Git repository before committing. If it is not, ask the user to initialize Git, designate another repo root, or disable checkpoints.
- When enabled, create local Git checkpoint commits after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, and before pausing or handoff.
- Run privacy scans before staging files. Do not commit private PDFs, Zotero databases, browser cookies, credentials, or closed vault content unless explicitly approved. Never push automatically.
- Use academic-research-suite as the default research companion for literature discovery and screening.
- Use research-lr-ra only as auxiliary/fallback when ARS is unavailable or a narrow LR task fits it better.
- Do not bypass paywalls, logins, CAPTCHAs, or institutional access controls.
- Do not write zotero.sqlite directly.
- Do not claim paper facts from snippets or model memory.
- Every phase must write a durable handoff and update its worklog.
- Stop at Waiting review for specialist outputs; controller acceptance is separate.

Start by creating or updating the controller workspace records, dependency setup record, session registry, and first small dispatch plan.
```

## Session Creation Record

When the Controller Console creates or requests a specialist session, update `session_registry.md`:

| Session name | Thread ID | Role | Status | Main artifacts | Next use |
| --- | --- | --- | --- | --- | --- |
| LiteratureAgent | `<id>` | Literature | idle | candidate/source/download manifests | search and acquisition |

Also append to `dispatch_log.md`:

| Time | Task ID | Target session | Action | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `<time>` | `<task>` | LiteratureAgent | session-created | active | ready for first bounded dispatch |

## Stop Conditions During Initialization

Stop before long work when:

- the controller session cannot be recorded;
- a required phase cannot run sequentially and the controller cannot create or record the needed specialist session;
- the required user startup questions have not been answered;
- Git checkpoints are enabled but the target root is unclear, is not a Git repository, or cannot pass a safe privacy scan;
- dependency status is unknown and the host project requires strict readiness;
- the Python environment cannot run `env_check.py`;
- Zotero is required but unavailable;
- Obsidian output is required but allowed write paths are not defined;
- the task would require unauthorized access or private credentials.
