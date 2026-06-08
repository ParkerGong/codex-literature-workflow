# Initialization And Controller Console Protocol

Use this reference whenever a user starts a new long literature workflow or asks to initialize a target project.

## Non-Negotiable Initialization Rule

One Codex session must be explicitly named the **Controller Console** before long work begins.

The Controller Console:

- owns the active goal for long-running workflows;
- initializes or updates all `00_controller/` records;
- verifies dependency status before long batches;
- creates or reuses fixed specialist sessions;
- dispatches bounded work to specialists;
- reviews durable handoff output;
- is the only session allowed to mark outputs accepted.

Specialist sessions do not accept final output and do not expand scope.

## Required User Questions Before Work

Before any search, download, Zotero, Obsidian, or PDF-reading phase, the Controller Console must ask the user to confirm the startup scope. If the latest user message already answers a field, record that answer and ask only for the missing fields.

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

Record answers in `project_profile.md`. Set `user_scope_confirmed: true` only after required answers are present. Do not dispatch long specialist work while `user_scope_confirmed=false`.

## Required Session Topology

| Session | Required before phase | If missing |
| --- | --- | --- |
| Controller Console | all phases | ask the user to designate this session or create a new controller thread |
| LiteratureAgent | search, screening, local library intake, download | create/reuse one fixed session and record its thread/session ID |
| ZoteroAgent | Zotero lookup/import/linked-file attachment | create/reuse only when Zotero is enabled |
| ObsidianAgent | PDF-first reading and Obsidian/RAG ingest | create/reuse only when Obsidian/RAG output is enabled |

Do not create one session per paper. Reuse fixed specialist sessions for batches.

## Controller Setup Sequence

1. Confirm that the current session is the Controller Console.
2. For long work, create or attach a goal using the recommended goal prompt.
3. Run `scripts/init_workspace.py --root <target-project>` if controller records do not exist.
4. Ask the required user startup questions above and record answers in `00_controller/project_profile.md`.
5. Read and fill `00_controller/project_profile.md`; do not continue until `user_scope_confirmed=true`.
6. Read and fill `00_controller/dependency_setup.md`.
7. Run or request the permanent environment check:

```bash
micromamba activate codex-lit
python3 <skill-root>/scripts/env_check.py --json
```

8. Read `00_controller/session_registry.md`.
9. Reuse fixed specialist sessions when listed and active.
10. If a required specialist session is missing, create it or ask the user to create it, then record its ID.
11. Write the first dispatch to `00_controller/dispatch_log.md`.
12. Send the bounded dispatch prompt from `references/dispatch-templates.md`.
13. Wait for a durable handoff before dispatching the next phase.

## Recommended Controller Prompt

```text
You are the Controller Console for codex-obsidian-read.
Do not do all work yourself.
Initialize controller records, verify dependencies, choose or create fixed specialist sessions, then dispatch small bounded tasks.
Before dispatch, ask the user to confirm paper direction, target count, source mode, download/access permission, Zotero connection, Obsidian connection, local inputs, output paths, and mapping needs.
Use academic-research-suite as the default literature discovery/screening companion.
Use research-lr-ra only as auxiliary/fallback.
Only the Controller Console may mark outputs accepted.
```

## Recommended Long-Task Goal Prompt

```text
Goal: Build a source-grounded Zotero and Obsidian-ready literature workspace for <TOPIC_OR_DIRECTION>.

You are the Controller Console for codex-obsidian-read.

Rules:
- Keep this session as the only controller and acceptance owner.
- Do not perform every phase yourself unless a phase is tiny.
- Create or reuse fixed specialist sessions:
  - LiteratureAgent for ARS-led search, screening, legal/authorized acquisition, and source manifests.
  - ZoteroAgent for Zotero parent items, collections, linked PDF/MD attachments, and verification.
  - ObsidianAgent for PDF-first reading, selected visual checks, and Obsidian/RAG-ready notes.
- If a specialist session does not exist, create it or ask the user to create it, then record the thread/session ID.
- Before any long batch, initialize controller records and dependency_setup.md.
- Before any search/download/Zotero/Obsidian/PDF-reading work, ask the user for paper direction, expected paper count, source input mode, download/access permission, language scope, Zotero connection, Obsidian connection, local input paths, output paths, and collection/vault mapping needs.
- Record those answers in project_profile.md and set user_scope_confirmed=true before dispatch.
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

- no Controller Console has been designated;
- the controller cannot create or record required specialist sessions;
- the required user startup questions have not been answered;
- dependency status is unknown and the host project requires strict readiness;
- the Python environment cannot run `env_check.py`;
- Zotero is required but unavailable;
- Obsidian output is required but allowed write paths are not defined;
- the task would require unauthorized access or private credentials.
