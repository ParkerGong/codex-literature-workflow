# Project Profiles

Use a project profile to adapt the generic open-source workflow to a host project's stricter rules. The controller should record the selected profile before any long task starts.

## Contents

- Generic and dissertation-strict profiles
- Direction, collection, and local-input intake
- Host protocol loading and profile record
- Override rules

## Generic Profile

Use `project_profile=generic` when the user has not provided a project-specific protocol.

Defaults:

- `user_scope_confirmed=false` until startup questions are answered.
- `zotero_enabled=false` unless requested.
- `obsidian_enabled=false` unless requested.
- `qmd_enabled=false` unless local vault search/index refresh is requested; embeddings remain separately opt-in.
- `git_checkpoint_required=false` unless the user or host profile enables it.
- `visual_check=selected-pages` only when figures, tables, curves, formulas, or screenshots matter.
- `access_mode=open-only` until the user authorizes browser, login, institutional, or manual access.
- temporary artifacts stay outside the repository and are reported before deletion or reuse.

Required records:

- controller kanban;
- session registry;
- dispatch log;
- source manifest;
- download log;
- phase handoff.

## Dissertation Strict Profile

Use `project_profile=dissertation-strict` when the workflow is part of a dissertation or research project where local provenance, durable records, and controller acceptance are mandatory. Zotero and Obsidian remain user-selected modules, but if they are enabled they follow strict verification rules.

Strict overrides:

| Setting | Value |
| --- | --- |
| `user_scope_confirmed` | ask first and require `true` before dispatch |
| `direction_source` | ask first: local direction docs/mapping, or user-provided direction |
| `target_count` | ask first; do not assume a paper count |
| `source_input_mode` | ask first: existing local library, search/download, or mixed |
| `download_enabled` | ask first; `false` when using only existing local PDFs |
| `zotero_enabled` | ask at start; optional, but strict verification applies if enabled |
| `obsidian_enabled` | ask at start; usually `true` when the user wants a knowledge base |
| `qmd_enabled` | ask only when local vault search/index refresh is in scope; `qmd_embed_allowed=false` by default |
| `git_checkpoint_required` | `false` unless the user or host protocol explicitly enables local recovery commits |
| `visual_check` | `selected-pages` by default; `vision-model` only when requested or essential |
| `batch_size` | first test: `1`; normal papers: `3-5`; long reports/theses: `1-2` |
| `access_mode` | `open-only` first; `authorized-browser` or `manual-user` only after user consent |
| `status_gate` | sub-agents stop at `Waiting review`; only the controller accepts |
| `temp_cleanup_mode` | soft-move and report, not default deletion |

Strict records:

- all generic records;
- `project_profile.md`;
- `controller_worklog.md`;
- `agent_worklogs/<Agent>.md`;
- `quota_status.md`;
- `temp_artifacts.md`;
- Zotero link index with collection and attachment state when Zotero is enabled or pending;
- Obsidian ingest queue/status/report when Obsidian is enabled.

## Direction And Collection Intake

Do not hard-code a private dissertation direction map or Zotero collection mapping into the open-source skill. At the start of a strict run, the controller asks:

1. Do you already have a local direction document, literature-review index, or Zotero/Obsidian collection mapping?
2. If yes, what local path(s) should be read?
3. Do you already have downloaded PDFs or a source manifest to ingest?
4. If yes, what local PDF/library/manifest path(s) should be used?
5. If no, should LiteratureAgent search/download new sources, or only make a candidate list?
6. If no direction mapping exists, what research direction should LiteratureAgent use to create a direction map and proposed collection buckets?
7. How many papers should the first batch target?
8. Should Zotero be enabled?
9. Should Obsidian/RAG-ready notes be enabled, and where may they be written?
10. If QMD refresh is wanted, which collection should be reused/created, and are embeddings approved?
11. Should local Git checkpoints be enabled and, if so, which repository root is safe?

Record the answer in `project_profile.md`:

```markdown
- direction_source: local-docs | user-prompt | agent-generated
- direction_docs:
- collection_mapping_source:
- user_scope_confirmed:
- source_input_mode: local-library | search-and-download | mixed
- download_enabled:
- local_library_paths:
- target_direction:
- target_count:
- zotero_enabled:
- obsidian_enabled:
- qmd_enabled:
- qmd_collection:
- qmd_embed_allowed:
- git_checkpoint_required:
- git_checkpoint_root:
- zotero_collection_or_mapping:
- obsidian_vault_or_output_root:
- allowed_obsidian_write_paths:
- proposed_collection_bucket:
```

When no mapping exists, LiteratureAgent should propose collection buckets and the controller should review them before dispatching ZoteroAgent or ObsidianAgent. Zotero collection mapping remains a runtime project configuration, not a bundled private table.

Strict source identity:

- every source has a stable `source_id`;
- duplicate titles, translated titles, and alias filenames point to one canonical note;
- no evidence-backed claim is accepted without a local PDF, DOI/URL, or an explicit manual-source note.

Strict Zotero Gate When Enabled:

1. LiteratureAgent selects and registers the source.
2. If Zotero is enabled, ZoteroAgent verifies or honestly marks the Zotero parent item, collection, and PDF linked-file attachment.
3. ObsidianAgent can write notes before Markdown note attachment to Zotero; note files often need a stable final path first.
4. After Obsidian notes are stable, ZoteroAgent may prepare a second linked-file mapping/script if the user/project wants it; the user runs the Zotero Desktop write and ZoteroAgent verifies it read-only.
5. Controller checks enabled records before marking accepted.

When Zotero is disabled, keep DOI/URL/local PDF and optional empty Zotero fields so Zotero can be added later. When Zotero is temporarily unavailable but enabled, Obsidian can proceed only if the controller records an explicit temporary status such as `pending-import`, `pending-attachment`, or `pending-md-attachment`.

## Host Project Protocol Loading

If the host project has its own Markdown protocol, the controller reads it before dispatch. Common documents include:

- project rules or `AGENTS.md`;
- agent task protocol;
- session dispatch protocol;
- Zotero workflow;
- Obsidian or knowledge-base README;
- literature-review direction notes;
- project-local version of this skill, if present.

The controller should translate host-specific paths into this skill's generic records. Do not copy private project names, paths, or research claims into an open-source release unless the maintainer wants that profile included.

## Profile Record Template

```markdown
# Project Profile

- project_profile:
- task_id:
- selected_at:
- controller:
- language_scope:
- direction_source:
- direction_docs:
- collection_mapping_source:
- source_input_mode:
- download_enabled:
- local_library_paths:
- target_direction:
- proposed_collection_bucket:
- zotero_enabled:
- obsidian_enabled:
- qmd_enabled:
- qmd_collection:
- qmd_embed_allowed:
- git_checkpoint_required:
- git_checkpoint_root:
- visual_check:
- access_mode:
- batch_size:
- allowed_read_paths:
- allowed_write_paths:
- forbidden_paths:
- quota_policy:
- process_check_policy:
- temp_cleanup_policy:
- acceptance_owner:
- notes:
```

## Override Rules

- The user's latest instruction can narrow scope or disable optional outputs.
- A strict profile can make a generic optional step required.
- A host project rule can forbid an action even if this skill allows it generically.
- If profile rules conflict and the controller cannot resolve them from local documents, stop before dispatch and ask the user.
