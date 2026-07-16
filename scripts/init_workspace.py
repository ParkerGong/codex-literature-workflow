#!/usr/bin/env python3
import argparse
import datetime as dt
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


FILES = {
    "00_controller/project_profile.md": """# Project Profile

- project_profile: generic
- task_id: TBD
- selected_at: TBD
- controller_console: TBD
- controller_thread_id: TBD
- long_task_goal: not-needed
- user_scope_confirmed: false
- startup_questions_missing: direction, target_count, source_input_mode, download_enabled/access_mode, language_scope, zotero_enabled, obsidian_enabled, qmd_enabled/embed approval, local inputs, output paths, collection/vault mapping, checkpoint policy/root when enabled
- git_checkpoint_required: false
- git_checkpoint_interval: 3 meaningful file-writing steps or accepted handoffs
- git_checkpoint_root: disabled
- git_push_policy: manual-only; never push automatically
- latest_git_checkpoint: disabled
- git_privacy_scan_status: disabled
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
- qmd_enabled: false
- qmd_collection: pending
- qmd_embed_allowed: false
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
- controller_goal_status: not-needed
- controller_goal_text:
- initialized_at:
- initialized_by:

## Required Rule

Record the current session as the Controller Console before long multi-phase work unless the user already designated another session. The Controller Console owns scope, records, dependency setup, specialist-session routing, optional checkpoint policy, and final acceptance. Create a persistent product goal only when the user explicitly requests one.

## Required User Questions Before Work

Before a full multi-phase search/download/Zotero/Obsidian run, confirm the following. For a bounded, read-only, or single-phase task, ask only fields that can materially change that task:

1. What is the paper direction or research boundary?
2. How many papers should the first batch target?
3. Are sources already local PDFs, new search/download, or mixed?
4. Should new PDF download/acquisition be enabled? If yes, is only open access allowed, or may authorized browser/manual access be used?
5. What language scope should be used: English, Chinese, or both?
6. Should Zotero be connected for parent items, collections, and linked PDF attachments?
7. Should Obsidian/RAG-ready notes be created?
8. If Zotero is enabled, what collection, collection mapping, or mapping document should be used?
9. If Obsidian is enabled, what vault/project root and allowed write paths should be used?
10. If Obsidian/RAG is enabled, should optional QMD refresh be attempted? What collection name should be used? Is `qmd embed` explicitly approved?
11. Are there existing local direction documents, literature indexes, PDF folders, manifests, or Zotero/Obsidian mapping files?
12. Should local Git checkpoints be enabled? If yes, which target project root should receive them?

Record answers in `project_profile.md`. Set `user_scope_confirmed: true` only after required answers are present. Do not dispatch long specialist work while `user_scope_confirmed=false`.

## Git Checkpoint Rule

Git checkpointing is disabled by default in the generic profile. When the user or host profile enables it, verify the target Git root, run privacy scans, stage explicit safe paths, commit at the configured interval, and never push automatically. Record `disabled` when checkpoints are not enabled.

## Specialist Session Plan

| Session | Needed | Thread ID | Status | Creation action | Notes |
| --- | --- | --- | --- | --- | --- |
| LiteratureAgent | yes | TBD | missing | create or reuse before search/intake | default research companion: academic-research-suite |
| ZoteroAgent | when zotero_enabled=true | TBD | missing | create/reuse only if Zotero enabled | read-only lookup, script preparation, user-run Desktop write, verification |
| ObsidianAgent | when obsidian_enabled=true | TBD | missing | create/reuse only if Obsidian/RAG enabled | write approved vault paths; record manifest and QMD/local RAG status |

## Recommended Controller Prompt

```text
You are the Controller Console for codex-literature-workflow.
Do not do all work yourself.
Initialize controller records, verify dependencies, choose or create fixed specialist sessions, then dispatch small bounded tasks.
Before a full multi-phase dispatch, confirm paper direction, target count, source mode, download/access permission, Zotero connection, Obsidian connection, local inputs, output paths, mapping needs, optional QMD settings, and whether Git checkpoints are enabled.
Use academic-research-suite as the default literature discovery/screening companion.
Use research-lr-ra only as auxiliary/fallback.
Create local Git checkpoints only when the user or host profile enables them. Do not auto-push.
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
  - ObsidianAgent for PDF-first reading, selected visual checks, Obsidian Wiki manifest-backed notes, and optional QMD/local RAG refresh status.
- If a specialist session does not exist, create it or ask the user to create it, then record the thread/session ID.
- Before any long batch, initialize controller records and dependency_setup.md.
- Before a full multi-phase run, ask for paper direction, expected paper count, source input mode, download/access permission, language scope, Zotero connection, Obsidian connection, local input paths, output paths, collection/vault mapping needs, and checkpoint policy.
- Record those answers in project_profile.md and set user_scope_confirmed=true before dispatch.
- When Git checkpoints are enabled, verify the target root is a Git repository before committing. If checkpoints are disabled, record that state and continue.
- When enabled, create local Git checkpoints at the configured interval and before risky bulk writes or handoff.
- Run privacy scans before staging files. Do not commit private PDFs, Zotero databases, browser cookies, credentials, or closed vault content unless explicitly approved. Never push automatically.
- Use academic-research-suite as the default research companion for literature discovery and screening.
- Use research-lr-ra only as auxiliary/fallback when ARS is unavailable or a narrow LR task fits it better.
- Do not bypass paywalls, logins, CAPTCHAs, or institutional access controls.
- Do not write zotero.sqlite directly.
- Do not treat QMD as source of truth. QMD is optional index/search infrastructure; run qmd embed only with explicit approval.
- Do not claim paper facts from snippets or model memory.
- Every phase must write a durable handoff and update its worklog.
- Stop at Waiting review for specialist outputs; controller acceptance is separate.

Start by creating or updating the controller workspace records, dependency setup record, session registry, and first small dispatch plan.
```
""",
    "00_controller/session_registry.md": """# Session Registry

| Session name | Thread ID | Role | Status | Main artifacts | Next use |
| --- | --- | --- | --- | --- | --- |
| Controller Console | TBD | Controller | active after recording the current or user-selected session | controller files, optional goal, dispatch log | route and accept tasks |
| LiteratureAgent | TBD | Literature | missing until created/reused | candidate/source/download manifests | search and acquisition; default research companion is academic-research-suite; research-lr-ra is auxiliary/fallback |
| ZoteroAgent | TBD | Zotero | optional missing | zotero_link_index, generated script, verification | read-only lookup and user-run attachment workflow |
| ObsidianAgent | TBD | Obsidian | optional missing | notes, ingest reports, QMD/local RAG status | PDF-first notes and manifest-backed ingest |
""",
    "00_controller/dependency_setup.md": """# Dependency Setup

## Recommended Routing

| Dependency | Role | Status | Notes |
| --- | --- | --- | --- |
| academic-research-suite | default paper discovery, deep/systematic review planning, query expansion, source verification, citation/integrity checks | pending | use before research-lr-ra for literature discovery |
| research-lr-ra | auxiliary/fallback LR assistant, research-gap mapping, representative-work selection | pending | not the default when ARS is available |
| codex-literature-workflow | controller for discovery -> screening -> download -> local registration -> Zotero -> PDF-first reading -> Obsidian/RAG | active | this initialized workspace |
| sciencedirect-live-session-fetcher | preferred authorized-browser PDF backend | pending | only when access_mode=authorized-browser and user has authorized access |
| zotero:Zotero | read-only Zotero lookup/export and verification | pending | imports and Desktop writes remain user-mediated |
| zotero-linked-attachments | user-run PDF/MD linked-file script preparation and read-only verification | pending | do not write zotero.sqlite directly |
| wiki-query / wiki-ingest / obsidian-wiki-ingest | existing KB lookup and Obsidian/RAG writes | pending | not external paper discovery authority |
| QMD | optional local vault search/index refresh | pending | not source of truth; skip if unavailable |
| browser / chrome / computer-use | browsing and authorized download mechanics | pending | snippets are not paper facts |

## Recommended Install Or Enable Checklist

Before long work, recommend installing or enabling companions that match the requested workflow:

| Companion | Setup recommendation | Origin/source URL | Required when | Fallback if missing |
| --- | --- | --- | --- | --- |
| academic-research-suite | install/enable first | Codex adapter: https://github.com/Imbad0202/academic-research-skills-codex ; upstream suite: https://github.com/Imbad0202/academic-research-skills | external literature discovery or screening | generic screening rubric; mark ARS unavailable |
| research-lr-ra | install vendored copy as auxiliary only | vendored in this repo at {{SKILL_ROOT}}/companion-skills/research-lr-ra | legacy LR workflow or narrow research-gap mapping | skip unless explicitly needed |
| zotero:Zotero plugin/connector | enable before Zotero phases | OpenAI/Codex plugin capability: https://help.openai.com/en/articles/20001256 | read-only Zotero lookup/export/verification requested | mark Zotero pending/manual; ask the user to perform imports or writes |
| zotero-linked-attachments | install vendored copy before linked-file phases | vendored in this repo at {{SKILL_ROOT}}/companion-skills/zotero-linked-attachments | PDF/MD linked-file attachments requested | record pending/manual attachment |
| sciencedirect-live-session-fetcher | install before authorized-browser publisher download tests | https://github.com/Given-Dream/sciencedirect-live-session-fetcher | access_mode=authorized-browser and publisher route fits | Chrome control, Computer Use once, then manual-user |
| Browser / Chrome / Computer Use plugins | enable when browser/session access is needed | OpenAI/Codex plugin capabilities: https://help.openai.com/en/articles/20001256 | authenticated browsing, visible UI fallback, or manual verification | stop for user/manual action |
| pdf skill | enable when selected visual checks or PDF QA matter | bundled/local Codex skill; no separate public upstream URL confirmed | figure/table/page-render evidence needed | text-only reading plus TODO for visual evidence |
| wiki-query / wiki-ingest / obsidian-wiki-ingest | install/enable only when local KB/Obsidian integration is requested | examples to verify before install: https://github.com/Ar9av/obsidian-wiki ; https://github.com/AgriciDaniel/claude-obsidian | existing KB lookup or Obsidian/RAG output | file-first Markdown notes with pending KB integration |
| QMD (@tobilu/qmd) | optional install only when vault search/index refresh is requested | https://www.npmjs.com/package/@tobilu/qmd | update/search local vault index after Obsidian writes | skip and record qmd_status; use lexical/sparse fallback if needed |

Open-source companions should be installed from GitHub when a public upstream is known. This project vendors maintainer-built companion skills only.

Vendored maintainer companion install:

```bash
python3 {{SKILL_ROOT}}/scripts/install_companion_skills.py
```

Use `--force` only when intentionally replacing an existing local skill copy.

Record:

- academic_research_suite_install_action:
- research_lr_ra_install_action:
- vendored_companion_install_time:
- vendored_companion_install_dest:
- vendored_companion_install_status:
- sciencedirect_fetcher_install_action:
- zotero_plugin_enablement:
- zotero_linked_attachments_install_action:
- browser_chrome_computer_use_enablement:
- pdf_skill_enablement:
- wiki_obsidian_helper_install_action:
- qmd_install_action:
- qmd_collection:
- qmd_embed_approval:

## Python Environment

Recommended permanent non-venv environment:

```bash
micromamba env create -f {{SKILL_ROOT}}/environment.yml  # or: mamba/conda env create
micromamba activate codex-literature  # or: mamba/conda activate codex-literature
python3 {{SKILL_ROOT}}/scripts/env_check.py --json --strict
```

If already created:

```bash
micromamba activate codex-literature  # or: mamba/conda activate codex-literature
micromamba env update -f {{SKILL_ROOT}}/environment.yml  # or: mamba/conda env update
python3 -m pip install -r {{SKILL_ROOT}}/requirements.txt
python3 {{SKILL_ROOT}}/scripts/env_check.py --json --strict
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

- Required for long workflows: false by default; enable only by user or host profile
- Interval: after every 3 meaningful file-writing steps or accepted handoffs
- When enabled, also checkpoint: after initialization/scope/dependency/session records, before risky bulk writes, after each phase acceptance, and before pause/handoff
- Push policy: manual-only; never push automatically

| Time | Task ID | Trigger | Files intended | Privacy scan | Commit hash | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | setup | default policy | none | not-run: disabled | none | disabled | enable only by user or host profile |
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

| source_id | batch | local_pdf | zotero_key | zotero_collection | zotero_status | md_note_path | reading_level | visual_pages | qmd_status | qmd_reason | status | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
""",
    "00_controller/handoff/.gitkeep": "",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="project root where controller files are created")
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing files after copying them to a timestamped backup",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and print actions without writing files",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if root.exists() and not root.is_dir():
        parser.error(f"--root is not a directory: {root}")
    created = []
    skipped = []
    backed_up = []
    planned = []
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_container = root / ".codex-literature-backups"
    backup_root = backup_container / timestamp
    backup_ignore = backup_container / ".gitignore"
    operations = []

    if backup_container.is_symlink():
        raise SystemExit(f"Refusing to use symlink backup directory: {backup_container}")
    if backup_container.exists() and not backup_container.is_dir():
        raise SystemExit(f"Backup path is not a directory: {backup_container}")
    if backup_container.resolve(strict=False).parent != root:
        raise SystemExit(f"Backup directory escaped the project root: {backup_container}")
    if backup_ignore.is_symlink():
        raise SystemExit(f"Refusing to overwrite symlink backup ignore file: {backup_ignore}")
    if backup_ignore.exists() and not backup_ignore.is_file():
        raise SystemExit(f"Backup ignore path is not a regular file: {backup_ignore}")

    # Complete the safety preflight before the first write so a bad late path
    # cannot leave a partially overwritten controller workspace.
    for rel, content in FILES.items():
        path = root / rel
        resolved_parent = path.parent.resolve()
        if resolved_parent != root and root not in resolved_parent.parents:
            raise SystemExit(f"Refusing to write through a path outside the project root: {path}")
        if path.is_symlink():
            raise SystemExit(f"Refusing to overwrite symlink: {path}")
        if path.exists() and not path.is_file():
            raise SystemExit(f"Expected a file path but found another object: {path}")
        if args.force and path.exists() and path.stat().st_nlink > 1:
            raise SystemExit(f"Refusing to overwrite hard-linked file: {path}")
        if path.exists() and not args.force:
            skipped.append(str(path))
            continue
        action = "overwrite" if path.exists() else "create"
        planned.append(f"{action} {path}")
        operations.append((rel, content, path, path.exists()))

    if args.dry_run:
        operations = []

    if any(existed for _, _, _, existed in operations):
        backup_container.mkdir(parents=True, exist_ok=True)
        if not backup_ignore.exists():
            backup_ignore.write_text("*\n", encoding="utf-8")

    for rel, content, path, existed in operations:
        path.parent.mkdir(parents=True, exist_ok=True)
        if existed:
            backup_path = backup_root / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_path)
            backed_up.append(str(backup_path))
        content = content.replace("{{SKILL_ROOT}}", str(SKILL_ROOT))
        path.write_text(content, encoding="utf-8")
        created.append(str(path))

    if args.dry_run:
        print("planned:")
        for action in planned:
            print(f"- {action}")
        print("skipped:")
        for path in skipped:
            print(f"- {path}")
    else:
        print("created:")
        for path in created:
            print(f"- {path}")
        print("skipped:")
        for path in skipped:
            print(f"- {path}")
        print("backed_up:")
        for path in backed_up:
            print(f"- {path}")


if __name__ == "__main__":
    main()
