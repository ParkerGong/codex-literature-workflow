#!/usr/bin/env python3
import argparse
from pathlib import Path


FILES = {
    "00_controller/project_profile.md": """# Project Profile

- project_profile: generic
- task_id: TBD
- selected_at: TBD
- controller: TBD
- language_scope: both
- direction_source: TBD
- direction_docs: TBD
- collection_mapping_source: TBD
- source_input_mode: TBD
- download_enabled: TBD
- local_library_paths: TBD
- target_direction: TBD
- proposed_collection_bucket: TBD
- zotero_enabled: false
- obsidian_enabled: false
- visual_check: selected-pages
- access_mode: open-only
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
    "00_controller/session_registry.md": """# Session Registry

| Session name | Thread ID | Role | Status | Main artifacts | Next use |
| --- | --- | --- | --- | --- | --- |
| Controller | TBD | Controller | active | controller files | route and accept tasks |
| LiteratureAgent | TBD | Literature | idle | candidate/source/download manifests | search and acquisition |
| ZoteroAgent | TBD | Zotero | idle | zotero_link_index, verification | parent items and attachments |
| ObsidianAgent | TBD | Obsidian | idle | notes, ingest reports | PDF-first notes |
""",
    "00_controller/dispatch_log.md": """# Dispatch Log

| Time | Task ID | Target session | Action | Status | Notes |
| --- | --- | --- | --- | --- | --- |
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
