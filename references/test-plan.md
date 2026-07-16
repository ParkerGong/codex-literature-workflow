# Test Plan

Do not rely on this skill for large literature expansion until it passes a small end-to-end test.

## Contents

- Environment and dependency smoke tests
- Startup, acquisition, Zotero, and Obsidian scenarios
- Optional Git and QMD scenarios
- Acceptance criteria

## Smoke Test 1: Environment Only

Prompt:

```text
Use $codex-literature-workflow to check whether this machine can extract PDF text and render selected pages. Do not search the web, do not use Zotero, and do not write Obsidian notes.
```

Expected:

- `scripts/env_check.py` result;
- one PDF probe if a sample PDF is provided;
- no Zotero or Obsidian writes.

## Smoke Test 1b: Companion Install Checklist

Prompt:

```text
Initialize $codex-literature-workflow setup for a mixed Zotero and Obsidian workflow. Do not search yet. Recommend external skill/plugin dependencies that should be installed or enabled.
```

Expected:

- `dependency_setup.md` recommends checking/installing or enabling `academic-research-suite`, auxiliary `research-lr-ra`, `zotero:Zotero`, `zotero-linked-attachments`, `sciencedirect-live-session-fetcher`, Browser/Chrome/Computer Use, `pdf`, and local wiki/Obsidian helpers when relevant;
- public origin/source URLs are recorded where known; maintainer-built vendored companions are labeled with their `companion-skills/` paths; OpenAI plugin-only dependencies are labeled honestly instead of invented;
- missing companions are recorded as pending/unavailable with explicit fallback behavior;
- ARS remains the default discovery/screening companion and RLR remains auxiliary only;
- no long literature work starts until dependency status and fallbacks are recorded.

## Smoke Test 2: Startup Scope Gate

Prompt:

```text
Use $codex-literature-workflow. I want papers.
```

Expected:

- no search, download, Zotero, Obsidian, or PDF-reading work starts;
- the Controller Console asks for paper direction, target paper count, source input mode, download/access permission, language scope, Zotero connection, Obsidian connection, local input paths, output/write paths, collection/vault/QMD mapping needs, and whether Git checkpoints are enabled;
- `project_profile.md` keeps `user_scope_confirmed=false` until answers are recorded;
- no specialist dispatch happens before scope confirmation.

## Smoke Test 3: Open-Only Literature Batch

Prompt:

```text
Use $codex-literature-workflow to find 2-3 open-access English papers about <topic>. Download only legal open PDFs, write a candidate table and manifest, but do not use Zotero or Obsidian.
```

Expected:

- dated queries and sources;
- candidate table with rejected/selected rows;
- verified local PDFs;
- no browser-auth access;
- no Zotero/Obsidian writes.

## Smoke Test 4: Full Optional Pipeline

Prompt:

```text
Use $codex-literature-workflow on 2 papers I already downloaded with source_input_mode=local-library and download_enabled=false. Ask whether Zotero and Obsidian should be enabled. If Zotero is enabled, prepare validated linked-file scripts for me to run, then create PDF-first Obsidian notes with selected visual pages. Do not prepare Markdown-note attachment yet.
```

Expected:

- environment check;
- local PDFs registered with `access_route=local-library`;
- download phase recorded as skipped;
- user-run Zotero script plus parent/attachment verification or honest pending status;
- notes with page evidence and visual status;
- controller and agent worklogs;
- batch report and controller acceptance checklist.

## Smoke Test 5: Strict Profile Records Only

Prompt:

```text
Use $codex-literature-workflow with project_profile=dissertation-strict on one already-downloaded PDF. Do not search the web. First ask whether there is a local direction/mapping document and whether Zotero/Obsidian should be enabled. Initialize controller records. If Zotero is disabled, keep Zotero fields empty/pending for later. If Zotero is enabled but unavailable, write pending statuses rather than launching apps.
```

Expected:

- `project_profile.md`, `quota_status.md`, and `temp_artifacts.md` exist;
- `controller_worklog.md` and fixed agent worklogs exist and include at least one entry or template;
- source manifest includes local PDF and `md_note_path`;
- Zotero link index includes `zotero_collection`, parent/PDF status, and MD status as `disabled` or `pending-md-attachment` unless the optional second pass is requested;
- Obsidian note frontmatter includes `zotero_collection` and `md_note_path`;
- sub-agent report stops at `Waiting review`, not accepted.

## Smoke Test 6: Chinese Database Route Logging

Prompt:

```text
Use $codex-literature-workflow to screen Chinese papers about <topic>. Do not download unless open or already authorized. Record CNKI/Wanfang/VIP route details and manual blockers.
```

Expected:

- candidate table includes Chinese database/source fields;
- access route distinguishes `cnki-authorized`, `wanfang-authorized`, `vip-authorized`, `manual-user`, and `unavailable`;
- no credentials or private account data are stored;
- LiteratureAgent worklog records queries, database routes, and blockers.

## Smoke Test 7: Closed-Source Download Fallback

Prompt:

```text
Use $codex-literature-workflow to acquire one authorized closed-source paper. Set download_enabled=true and closed_source_fallback=chrome-then-computer-use-once. Use my authenticated Chrome session if allowed. If Chrome gets stuck at verification, try Computer Use once, then stop and write the blocker if still unresolved.
```

Expected:

- controller records browser/session access permission;
- LiteratureAgent tries Chrome before Computer Use;
- at most one Computer Use fallback attempt is recorded;
- unresolved verification is marked `captcha-blocked` or `manual-user`;
- no credentials, cookies, or private account details are stored;
- accepted PDF, if any, passes PDF quality checks before `downloaded`.

## Smoke Test 8: Enabled Git Checkpoint Gate

Prompt:

```text
Use $codex-literature-workflow to initialize a long mixed literature workflow. Do not search yet. Explicitly enable Git checkpoints and ask the Controller Console to create the first local checkpoint after initialization/scope records.
```

Expected:

- `project_profile.md` includes `git_checkpoint_required`, `git_checkpoint_interval`, `git_checkpoint_root`, `git_push_policy`, and latest checkpoint status;
- `git_checkpoints.md` exists;
- the controller verifies whether the target root is a Git repository before long work;
- if the target root is not a Git repository, the controller stops and asks the user to initialize Git or designate the correct root;
- if Git is available, the controller inspects changed paths, runs a privacy scan on intended text files, stages explicit safe paths only, creates a local checkpoint commit, and records the hash or blocker;
- no automatic push happens.

## Smoke Test 9: Obsidian Wiki Ingest + QMD Update Only

Prompt:

```text
Use $codex-literature-workflow to test Obsidian Wiki ingest in an isolated temp vault. Create a few demo Markdown notes, initialize QMD if available, reuse or add a collection, run qmd update, and search for a known title or keyword. Do not run qmd embed and do not touch real PDFs, Zotero sqlite, or production vaults.
```

Expected:

- temp/test vault contains `.manifest.json`, `index.md`, `hot.md`, `log.md`, `01_sources/source_registry.md`, `01_sources/zotero_link_index.md`, and `02_literature_notes/`;
- each canonical demo source has one formal note and manifest row;
- duplicate aliases are recorded only in manifest/report/source registry, not as separate formal notes;
- wrong/incomplete demo sources are marked `manual-check`;
- `qmd init`, `qmd collection list`, idempotent collection reuse/add, `qmd update`, `qmd status`, and `qmd search` are attempted only when QMD is available;
- QMD search returns a known title/keyword when available;
- vectors remain pending or 0 embedded when `qmd embed` was not approved;
- `.qmd/` and `10_knowledge_base/.rag/` are ignored by Git;
- no original PDFs, Zotero sqlite files, browser cookies, credentials, or production vaults are modified.

## Acceptance Criteria

- Fixed-session pattern is used; no session-per-paper behavior.
- Required startup scope is confirmed before specialist work.
- Setup recommends installing/enabling the external companion skills/plugins needed by the requested workflow and records missing-dependency fallbacks.
- Optional Zotero/Obsidian switches are respected.
- Download is optional and skipped for `local-library` mode.
- Search and access provenance is dated.
- Bad PDFs are not treated as valid sources.
- Visual claims are either checked or marked TODO.
- No direct Zotero sqlite writes.
- All outputs are durable files, not chat-only.
- Controller and fixed specialist agents update Markdown worklogs.
- When Git checkpoints are enabled, the Controller creates them after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, and before pause/handoff; otherwise the records say `disabled`.
- When used, Git checkpoints inspect `git status`, run privacy scans, avoid `git add .`, exclude private PDFs/Zotero databases/cookies/credentials unless explicitly approved, and never auto-push.
- Strict profile outputs include quota/process/temp policy state.
- When Zotero is enabled or pending, Zotero and Obsidian records agree on `source_id`, `zotero_key`, `zotero_collection`, `local_pdf`, and `md_note_path`.
- Obsidian Wiki / LLM Wiki ingest writes one formal note per canonical source and records duplicate aliases without duplicate formal notes.
- `.manifest.json`, source registry, Zotero link index, and note frontmatter agree before controller acceptance.
- QMD is optional, update-only by default, and never treated as the source of truth.
- `qmd embed`, `qmd query`, and `qmd vsearch` are not run without explicit approval.

## Automated Release Checks

Run from the repository root:

```bash
python3 -m pip install -r requirements.txt -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 -m py_compile scripts/*.py
python3 -m json.tool evals/evals.json
node --check companion-skills/zotero-linked-attachments/scripts/build_zotero_linked_attachment_js.mjs
node --check companion-skills/zotero-linked-attachments/scripts/verify_zotero_linked_attachments.mjs
python3 -m unittest discover -s tests -v
python3 scripts/env_check.py --json --strict
```

The offline suite must cover YAML metadata validation, input validation, safe backup/install behavior, installer source/destination overlap, disposable-environment target safety, complete PDF report/text/render alias preflight, blank/scan-only/encrypted PDF semantics, relative Zotero base-path resolution, parent/link-mode checks, pagination, conflicting mappings, and mapping/attachment-source/output hard-link or symlink protection. Live Zotero writes, authenticated publisher access, and production-vault writes remain manual opt-in integration tests against disposable or backed-up targets.
