#!/usr/bin/env python3
import argparse
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


FILES = {
    "00_controller/project_profile.md": """# Project Profile

- project_profile: generic
- task_id: TBD
- selected_at: TBD
- controller_console: TBD
- controller_thread_id: TBD
- long_task_goal: pending for long workflows
- user_scope_confirmed: false
- startup_questions_missing: direction, target_count, source_input_mode, download_enabled/access_mode, language_scope, zotero_enabled, obsidian_enabled, local inputs, output paths, collection/vault mapping, git checkpoint root
- git_checkpoint_required: true
- git_checkpoint_interval: 3 meaningful file-writing steps or accepted handoffs
- git_checkpoint_root: TBD
- git_push_policy: manual-only; never push automatically
- latest_git_checkpoint: pending
- git_privacy_scan_status: pending
- language_scope: both
- direction_source: TBD
- direction_docs: TBD
- collection_mapping_source: TBD
- research_companion_default: academic-research-suite
- research_companion_auxiliary: research-lr-ra
- source_input_mode: TBD
- download_enabled: TBD
- local_library_paths: TBD
- target_direction: TBD
- target_count: TBD
- inclusion_rules: TBD
- exclusion_rules: TBD
- proposed_collection_bucket: TBD
- zotero_collection_or_mapping: TBD
- obsidian_vault_or_output_root: TBD
- allowed_obsidian_write_paths: TBD
- zotero_enabled: false
- obsidian_enabled: false
- visual_check: selected-pages
- access_mode: open-only
- authorized_download_backend: sciencedirect-live-session-fetcher when installed
- python_environment: codex-literature permanent non-venv environment
- dependency_setup_status: pending
- batch_size: TBD
- allowed_read_paths: TBD
- allowed_write_paths: TBD
- forbidden_paths: TBD
- quota_policy: quota unknown
- process_check_policy: symptom-driven; no routine sweeps
- temp_cleanup_policy: soft-move preferred
- acceptance_owner: Controller
- notes:
""",
    "00_controller/controller_worklog.md": """# Controller Worklog

## Template

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
- Git checkpoint:
- TODO:
- RISK:
- Next action:
```
""",
    "00_controller/agent_worklogs/LiteratureAgent.md": """# LiteratureAgent Worklog

## Template

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
- Git checkpoint:
- TODO:
- RISK:
- Next action:
```
""",
    "00_controller/agent_worklogs/ZoteroAgent.md": """# ZoteroAgent Worklog

## Template

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
- Git checkpoint:
- TODO:
- RISK:
- Next action:
```
""",
    "00_controller/agent_worklogs/ObsidianAgent.md": """# ObsidianAgent Worklog

## Template

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
- Git checkpoint:
- TODO:
- RISK:
- Next action:
```
""",
    "00_controller/controller_kanban.md": """# Controller Kanban

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
""",
    "00_controller/initialization.md": """# Initialization

## Controller Console

- controller_console:
- controller_thread_id:
- controller_goal_status: pending | active | not-needed
- controller_goal_text:
- initialized_at:
- initialized_by:

## Required Rule

One session must be explicitly designated as the Controller Console before long work starts. The Controller Console owns goal, scope, records, dependency setup, specialist-session routing, forced local Git checkpoints, and final acceptance.

## Required User Questions Before Work

Before any search, download, Zotero, Obsidian, or PDF-reading phase, ask the user to confirm:

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
11. Which target project root should receive local Git checkpoint commits, or should the initialized root be used?

Record answers in `project_profile.md`. Set `user_scope_confirmed: true` only after required answers are present. Do not dispatch long specialist work while `user_scope_confirmed=false`.

## Git Checkpoint Rule

The Controller Console must force local Git checkpoint commits after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, and before pausing or handoff. If the target root is not a Git repository, stop and ask the user to initialize Git or designate the correct repo root before long work. Run privacy scans before staging files. Never push automatically.

## Specialist Session Plan

| Session | Needed | Thread ID | Status | Creation action | Notes |
| --- | --- | --- | --- | --- | --- |
| LiteratureAgent | yes | TBD | missing | create or reuse before search/intake | default research companion: academic-research-suite |
| ZoteroAgent | when zotero_enabled=true | TBD | missing | create/reuse only if Zotero enabled | use Zotero plugin/MCP and linked attachments |
| ObsidianAgent | when obsidian_enabled=true | TBD | missing | create/reuse only if Obsidian/RAG enabled | write only approved vault/project paths |

## Recommended Controller Prompt

```text
You are the Controller Console for codex-literature-workflow.
Do not do all work yourself.
Initialize controller records, verify dependencies, choose or create fixed specialist sessions, then dispatch small bounded tasks.
Before dispatch, ask the user to confirm paper direction, target count, source mode, download/access permission, Zotero connection, Obsidian connection, local inputs, output paths, mapping needs, and target Git checkpoint root.
Use academic-research-suite as the default literature discovery/screening companion.
Use research-lr-ra only as auxiliary/fallback.
Force a local Git checkpoint after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, and before pausing or handoff. Do not auto-push.
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
  - ZoteroAgent for Zotero parent items, collections, linked PDF/MD attachments, and verification.
  - ObsidianAgent for PDF-first reading, selected visual checks, and Obsidian/RAG-ready notes.
- If a specialist session does not exist, create it or ask the user to create it, then record the thread/session ID.
- Before any long batch, initialize controller records and dependency_setup.md.
- Before any search/download/Zotero/Obsidian/PDF-reading work, ask the user for paper direction, expected paper count, source input mode, download/access permission, language scope, Zotero connection, Obsidian connection, local input paths, output paths, collection/vault mapping needs, and the target Git checkpoint root.
- Record those answers in project_profile.md and set user_scope_confirmed=true before dispatch.
- Verify the target root is a Git repository before long work. If not, stop and ask the user to initialize Git or designate the correct repo root.
- Force local Git checkpoint commits after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, and before pausing or handoff.
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
""",
    "00_controller/session_registry.md": """# Session Registry

| Session name | Thread ID | Role | Status | Main artifacts | Next use |
| --- | --- | --- | --- | --- | --- |
| Controller Console | TBD | Controller | active after explicit designation | controller files, goal, dispatch log | route and accept tasks |
| LiteratureAgent | TBD | Literature | missing until created/reused | candidate/source/download manifests | search and acquisition; default research companion is academic-research-suite; research-lr-ra is auxiliary/fallback |
| ZoteroAgent | TBD | Zotero | optional missing | zotero_link_index, verification | parent items and attachments |
| ObsidianAgent | TBD | Obsidian | optional missing | notes, ingest reports | PDF-first notes |
""",
    "00_controller/dependency_setup.md": """# Dependency Setup

## Recommended Routing

| Dependency | Role | Status | Notes |
| --- | --- | --- | --- |
| academic-research-suite | default paper discovery, deep/systematic review planning, query expansion, source verification, citation/integrity checks | pending | use before research-lr-ra for literature discovery |
| research-lr-ra | auxiliary/fallback LR assistant, research-gap mapping, representative-work selection | pending | not the default when ARS is available |
| codex-literature-workflow | controller for discovery -> screening -> download -> local registration -> Zotero -> PDF-first reading -> Obsidian/RAG | active | this initialized workspace |
| sciencedirect-live-session-fetcher | preferred authorized-browser PDF backend | pending | only when access_mode=authorized-browser and user has authorized access |
| zotero:Zotero | local Zotero lookup/export/import and verification | pending | enable only when Zotero outputs are requested |
| zotero-linked-attachments | linked-file PDF/MD attachment to Zotero | pending | do not write zotero.sqlite directly |
| wiki-query / wiki-ingest / obsidian-wiki-ingest | existing KB lookup and Obsidian/RAG writes | pending | not external paper discovery authority |
| browser / chrome / computer-use | browsing and authorized download mechanics | pending | snippets are not paper facts |

## Python Environment

Recommended permanent non-venv environment:

```bash
micromamba env create -f {{SKILL_ROOT}}/environment.yml
micromamba activate codex-literature
python3 {{SKILL_ROOT}}/scripts/env_check.py --json
```

If already created:

```bash
micromamba activate codex-literature
micromamba env update -f {{SKILL_ROOT}}/environment.yml
python3 -m pip install -r {{SKILL_ROOT}}/requirements.txt
python3 {{SKILL_ROOT}}/scripts/env_check.py --json
```

Record:

- python_interpreter:
- requirements_path: {{SKILL_ROOT}}/requirements.txt
- environment_yml_path: {{SKILL_ROOT}}/environment.yml
- env_check_time:
- env_check_summary:
- missing_packages:
- missing_cli_tools:
- next_install_action:
""",
    "00_controller/dispatch_log.md": """# Dispatch Log

| Time | Task ID | Target session | Action | Status | Notes |
| --- | --- | --- | --- | --- | --- |
""",
    "00_controller/git_checkpoints.md": """# Git Checkpoints

Policy:

- Required for long workflows: true
- Interval: after every 3 meaningful file-writing steps or accepted handoffs
- Also required: after initialization/scope/dependency/session records, before risky bulk writes, after each phase acceptance, and before pause/handoff
- Push policy: manual-only; never push automatically

| Time | Task ID | Trigger | Files intended | Privacy scan | Commit hash | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
""",
    "00_controller/source_manifest.md": """# Source Manifest

| source_id | title | authors_year | venue | doi_url | local_pdf | md_note_path | source_input_mode | access_route | status | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
""",
    "00_controller/download_log.md": """# Download Log

| source_id | attempted_urls | used_url | access_date | access_route | fallback_attempted | fallback_outcome | local_pdf | bytes | page_count | quality_status | message |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
""",
    "00_controller/zotero_link_index.md": """# Zotero Link Index

| source_id | zotero_key | zotero_collection | parent_status | pdf_status | md_status | local_pdf | md_note_path | verification | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
""",
    "00_controller/quota_status.md": """# Quota Status

| Time | Reading | Reliability | Decision | Notes |
| --- | --- | --- | --- | --- |
| TBD | quota unknown | unknown | avoid new long batches until clarified if host policy requires | initialized placeholder |
""",
    "00_controller/temp_artifacts.md": """# Temp Artifacts

| Task ID | Original path | Moved/preserved path | Files | Bytes | Cleanup mode | Owner | Notes |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
""",
    "00_controller/ingest_queue.md": """# Ingest Queue

| batch | task_id | source_ids | owner | status | report |
| --- | --- | --- | --- | --- | --- |
""",
    "00_controller/ingest_status.md": """# Ingest Status

| source_id | batch | local_pdf | zotero_key | zotero_collection | zotero_status | md_note_path | reading_level | visual_pages | status | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
""",
    "00_controller/handoff/.gitkeep": "",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="project root where controller files are created")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    created = []
    skipped = []
    for rel, content in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not args.force:
            skipped.append(str(path))
            continue
        content = content.replace("{{SKILL_ROOT}}", str(SKILL_ROOT))
        path.write_text(content, encoding="utf-8")
        created.append(str(path))

    print("created:")
    for path in created:
        print(f"- {path}")
    print("skipped:")
    for path in skipped:
        print(f"- {path}")


if __name__ == "__main__":
    main()
