# Workflow Walkthrough

This document walks through the whole skill as an auditable runbook. Use it when reviewing whether the implementation matches an existing project workflow.

## Contents

- Controller initialization and environment readiness
- Local intake, discovery, and legal acquisition
- Zotero linking and PDF-first Obsidian ingest
- Optional QMD refresh, acceptance, and recovery

## 0. Controller Opens The Run

The controller starts by creating or reusing one task ID. It does not immediately search the web, read PDFs, write Zotero, or write Obsidian notes.

Controller decisions:

1. Select `project_profile`.
2. Ask required startup questions and set `user_scope_confirmed=true` only after answers are recorded.
3. Ask for the paper direction or research boundary.
4. Ask for the expected paper count for the first batch.
5. Ask whether the user has local direction documents, literature-review indexes, PDF folders, manifests, or collection mappings. If yes, read those paths. If no, ask for the research direction or have LiteratureAgent draft a direction map after scope confirmation.
6. Set `language_scope`: English, Chinese, or both.
7. Ask whether sources are already downloaded: `local-library`, `search-and-download`, or `mixed`.
8. Ask whether new downloads are enabled. If a local library is enough, set `download_enabled=false`.
9. Ask whether Zotero and Obsidian should be enabled. Zotero remains optional; if enabled, strict verification applies. Obsidian requires a vault/project root and allowed write paths.
10. Set access mode: open-only first, authorized browser/manual only with user permission.
11. Set authorized download backend. When installed, use `sciencedirect-live-session-fetcher` as the preferred backend for authenticated publisher downloads before generic Chrome or Computer Use.
12. Set closed-source fallback policy, batch size, render cap, and visual-check mode.
13. Ask whether QMD refresh is enabled, which collection should be reused/created, and whether embeddings are approved.
14. Ask whether local Git checkpoints are enabled; only then set the target root, interval, and manual-only push policy.
15. Record allowed reads, allowed writes, forbidden paths, quota policy, process-check policy, temp cleanup policy, and worklog paths.

Durable outputs:

- `project_profile.md`
- `initialization.md`
- `controller_worklog.md`
- `agent_worklogs/<Agent>.md`
- `controller_kanban.md`
- `session_registry.md`
- `dispatch_log.md`
- `git_checkpoints.md`
- per-task handoff file

The optional controller goal prompt is in `architecture.md`. Use persistent goal mode only when the user explicitly requests it; controller records remain the durable default.

## 1. Controller Initializes Records

Before long work starts, the controller runs or manually follows:

```bash
python scripts/init_workspace.py --root <project-root>
```

This creates controller records for:

- fixed sessions;
- controller and per-agent worklogs;
- source manifest;
- download log;
- Zotero link index;
- Git checkpoint ledger;
- quota status;
- temp artifact ledger;
- ingest queue/status;
- per-task handoff folder.

These records prevent long tasks from drifting after context compaction, browser failure, quota limits, or user interruption. After compaction, an agent reads `project_profile.md`, `session_registry.md`, its own worklog, the active handoff, and the relevant manifest/index before continuing.

If local Git checkpoints are enabled, the controller verifies the target root is a Git repository. If it is not, ask the user to initialize Git, designate the correct repo root, or disable checkpoints.

First checkpoint trigger when enabled:

```bash
git status --short
```

When enabled, the controller inspects changed paths, runs the configured privacy scan on intended text files, stages explicit safe paths only, commits a local checkpoint, and records the commit hash in `00_controller/git_checkpoints.md`. It does not push. Otherwise record `disabled`.

## 2. Environment Is Checked

The controller checks companion skill/plugin readiness and the local Python environment before search/download/PDF-reading batches.

Companion setup is recorded in `dependency_setup.md`: `academic-research-suite`, auxiliary `research-lr-ra`, Zotero plugin/connector, `zotero-linked-attachments`, `sciencedirect-live-session-fetcher`, Browser/Chrome/Computer Use, `pdf`, and local wiki/Obsidian helpers are marked ready, pending, unavailable, or not needed with explicit fallback behavior. Public companions use GitHub install paths when known; vendored maintainer-built companions use `scripts/install_companion_skills.py`.

Commands:

```bash
micromamba activate codex-literature
python scripts/env_check.py --json --strict
```

If `micromamba` is unavailable, use the equivalent installed `mamba` or `conda` commands.

If the permanent environment has not been created yet, initialize it from the skill repository:

```bash
micromamba env create -f environment.yml
micromamba activate codex-literature
python -m pip install -r requirements.txt
```

Use a temporary venv only as an explicit disposable fallback:

```bash
python scripts/setup_env.py --venv /private/tmp/codex_literature_workflow_venv_<task-id> --install
```

The fallback target must be a new, non-symlink path outside the skill repository; `--install` creates the venv and installs packages in this one call. Do not pre-create the directory or invoke the helper again for an existing venv. To add packages to an existing venv, call that venv's own `python -m pip` directly.

PDF probing is text-first and selected-page only:

```bash
python scripts/pdf_probe.py <paper.pdf> --pages 1,3,9 --out /private/tmp/codex_literature_workflow_probe
```

The run records whether Python packages, Poppler tools, OCR tools, browser tools, and temp paths are available. If quota is unknown, write `quota unknown` rather than a guessed number.

When checkpoints are enabled, the controller creates another local checkpoint after dependency records are updated and before broad search or file-writing work.

## 3. LiteratureAgent Registers Existing Local PDFs When Provided

If `source_input_mode=local-library` or `mixed`, LiteratureAgent starts from approved local folders, files, or manifests.

Local intake outputs:

- enumerated local PDF list;
- source IDs;
- PDF size/page/text status;
- title/author hints;
- duplicate aliases;
- source manifest rows with `access_route=local-library`;
- `download-skipped` state when no new download is enabled;
- LiteratureAgent worklog update.

No web search or download happens in pure `local-library` mode unless the controller explicitly changes scope.

When checkpoints are enabled, the controller checkpoints local intake manifests or quality reports before moving to Zotero, Obsidian, or additional search.

## 4. LiteratureAgent Screens Sources When Needed

The controller dispatches the fixed LiteratureAgent with a small batch.

LiteratureAgent uses a literature-review companion skill when available:

- `academic-research-suite` by default for discovery, deep/systematic review planning, query expansion, and source verification;
- `research-lr-ra` only as an auxiliary/fallback for legacy LR assistant work, research-gap mapping, or representative-work selection.

If no companion exists, LiteratureAgent still uses the screening rubric in `literature-acquisition.md`.

Screening outputs:

- search queries and dates;
- database/site names;
- candidate table;
- screening score;
- inclusion/exclusion reason;
- access route;
- duplicate risk.

The candidate table is not a final source list. The controller can audit why each item was selected, deferred, rejected, or marked manual-check.

When checkpoints are enabled, the controller checkpoints the screening table and manifest changes before acquisition or other risky follow-up writes.

## 5. LiteratureAgent Optionally Downloads Legal Or Authorized PDFs

This step runs only when `download_enabled=true`. Open materials are downloaded directly when the source is legitimate. Closed or authenticated materials are one-item-at-a-time and require user permission.

Access route order:

1. `open-direct`
2. `publisher-open`
3. `authorized-browser`
4. Chinese authorized routes when applicable: `cnki-authorized`, `wanfang-authorized`, `vip-authorized`
5. `manual-user`
6. `unavailable`

Authorized-browser mode should use `sciencedirect-live-session-fetcher` first when it is installed and the publisher route fits. It reuses one live DevTools browser session and serially fetches PDFs from the authorized page context. Use generic Chrome control or Computer Use only when the fetcher is unavailable, attached to the wrong session, or blocked by a visible browser interaction. Stop at login, CAPTCHA, payment, or license uncertainty.

Closed-source fallback:

1. Try legal/open direct or publisher PDF links.
2. Use `sciencedirect-live-session-fetcher` with the same browser/profile/window where lawful access is active.
3. If the fetcher cannot attach to the correct authorized session, use Codex Chrome control with the user's existing authenticated Chrome profile.
4. If Chrome control gets stuck in a visible UI or verification flow, make at most one Computer Use fallback attempt.
5. If human verification, CAPTCHA, payment, login, or license uncertainty remains, stop and mark `captcha-blocked`, `manual-user`, or `manual-check`.

IEEE example:

- Put the IEEE article detail URL in the CSV `note`, for example `https://ieeexplore.ieee.org/document/<arnumber>`.
- Include the IEEE DOI when known, especially `10.1109/...`, so the fetcher uses its IEEE branch.
- If the live IEEE page says `Access provided by: <institution>` and shows the red `PDF` button, use that route directly. Do not click `Personal Sign In` as a default step.
- If a DevTools run fails while the visible user Chrome succeeds, suspect a session mismatch before suspecting lack of access.

For each accepted PDF, LiteratureAgent verifies:

- plausible file size;
- page count;
- title/authors match;
- body text exists;
- language/publication metadata match;
- the PDF is not a landing-page print or incomplete front matter.

Outputs:

- source manifest row;
- download log row;
- local PDF path;
- quality status;
- fetcher output paths such as `devtools_results.csv` and `summary.txt` when `sciencedirect-live-session-fetcher` was used;
- handoff with `Waiting review`.

Bad PDFs are recorded honestly as `wrong-pdf`, `incomplete-pdf`, `scan-or-ocr-needed`, or `manual-check`.

For Chinese databases, LiteratureAgent records database-specific fields such as `cn_database`, `cn_record_url`, `cn_access_route`, Chinese/English title, journal/source name, year/issue/pages, database ID, download method, and manual blocker.

When checkpoints are enabled, the controller checkpoints reviewed download logs and source manifest updates before Zotero linking or Obsidian ingest.

## 6. ZoteroAgent Links Bibliography And Files

This phase runs only when Zotero is enabled by the user or host project.

ZoteroAgent never writes `zotero.sqlite` directly. It uses the read-only local API, generated user-run Zotero Desktop JavaScript, connector/manual results, or manual confirmation.

For the formal release, API access is read-only and Zotero Desktop writes are user-run: ZoteroAgent validates the mapping and generates JavaScript, the user executes it, and ZoteroAgent verifies the resulting state. The agent does not launch or control Zotero Desktop.

Strict Zotero gate when enabled records:

- parent item key or pending-import status;
- target collection or collection-missing/manual-check status;
- linked local PDF or pending-attachment status;
- Markdown note link status, usually `disabled` until the Obsidian note has a stable path.

Zotero outputs:

- Zotero link index row;
- verification record;
- parent key/status;
- collection status;
- PDF linked-file status;
- MD linked-file status only if the optional second pass is requested;
- exact blocker if manual action is needed.

Default MD note behavior: do not link Markdown notes to Zotero in the first Zotero pass. After Obsidian notes are complete and stable, the controller may dispatch ZoteroAgent to prepare an optional second pass with `attach_md_note=true` for the user to run.

When checkpoints are enabled, the controller checkpoints Zotero link-index or verification record changes before PDF-first reading or Obsidian writes.

## 7. ObsidianAgent Performs PDF-First Reading

This phase runs only when Obsidian/RAG ingest is enabled.

The controller dispatch includes exact source rows, allowed write paths, render cap, temp policy, and duplicate/canonical status.

ObsidianAgent rules:

- use the PDF as primary evidence;
- treat existing summaries as secondary clues;
- do not modify original PDFs or previous summaries unless explicitly allowed;
- do not create independent notes for duplicate aliases;
- stop at `Waiting review`, not accepted.

Reading levels:

- `text-ok`
- `selected-visual`
- `vision-model`
- `scan-or-ocr`
- `bad-pdf`

Visual work is optional and evidence-driven. Render only selected pages when claims depend on figures, tables, formulas, curves, screenshots, or diagrams. If the render cap is not enough, record TODO/RISK instead of rendering everything.

When checkpoints are enabled, the controller checkpoints note drafts, rendered-page ledgers, or reading-level records before accepting or dispatching the next note batch.

## 8. Obsidian Wiki Ingest And Manifest Backfill

Each literature note becomes RAG-ready when it is part of a manifest-backed Obsidian Wiki / LLM Wiki style vault. QMD or any other index is only search infrastructure; the vault Markdown, `.manifest.json`, source registry, Zotero link index, and controller records remain the source of truth.

Each formal literature note should contain:

- `source_id`
- title and authors/year;
- local PDF path;
- `zotero_key`
- `zotero_collection`
- `zotero_status`
- `md_note_path`
- duplicate aliases;
- reading level;
- visual verification pages;
- page-level evidence;
- TL;DR;
- method/mechanism;
- limitations/risks;
- project use boundary;
- RAG keywords;
- Obsidian Wiki ingest metadata.

Optional project metadata fields may be added only when useful:

- `lr_direction`: literature-review direction or topic bucket;
- `chapter_target`: likely dissertation/report chapter or section;
- `claim_type`: background, method, benchmark, limitation, gap, or similar claim class.

These are not hard requirements. Use controlled values from local direction documents when available.

Optional outputs:

- `.manifest.json`;
- source registry row;
- Zotero link index update when Zotero is enabled or pending;
- concept pages;
- claim cards;
- batch report;
- ingest queue/status updates.

Canonical source rule:

- one canonical source gets one formal literature note;
- duplicate aliases are report/manifest/source-registry entries, not separate formal notes;
- wrong, incomplete, encrypted, or mismatched PDFs become `manual-check`.

Unverified visual claims are marked `TODO: visual verification` or `INFERRED`, not fact.

When checkpoints are enabled, the controller checkpoints Obsidian/RAG notes, manifest, ingest status records, and QMD/fallback status before final acceptance.

## 9. QMD / Local RAG Refresh Is Optional

After vault writes, the controller may refresh local search/index infrastructure.

QMD update-only path:

```bash
${QMD_CLI:-qmd} update
${QMD_CLI:-qmd} status
${QMD_CLI:-qmd} search "<known query>" -c "$QMD_WIKI_COLLECTION" -n 5
```

Skip QMD when `qmd` is unavailable or `QMD_WIKI_COLLECTION` is unset. Record `qmd_status` and `qmd_reason`.

Do not run `qmd embed`, `qmd query`, or `qmd vsearch` unless the user explicitly approves model downloads/embedding compute or the project profile allows embeddings. If QMD is absent or embeddings are not approved, a project-local lexical/sparse fallback can be used, but it must not be described as dense semantic RAG.

## 10. Controller Accepts Or Blocks

The controller reviews files, not chat memory.

Acceptance checks:

- output files exist and are inside allowed paths;
- source provenance is present;
- source input mode was respected, including `download-skipped` when applicable;
- PDF quality checks passed or bad state is honest;
- Zotero parent, collection, PDF attachment, and MD attachment status are honest;
- Obsidian frontmatter matches Zotero/source records;
- page evidence exists;
- visual claims have checked/TODO status;
- QMD or fallback retrieval status is recorded without being treated as source truth;
- duplicates are canonicalized;
- temp artifacts are recorded and moved/preserved according to policy;
- controller and target agent worklogs were updated;
- sub-agent status is `Waiting review`.
- when Git checkpoints are enabled, the latest checkpoint includes the accepted record changes or its blocker is recorded; otherwise `git_checkpoints.md` records `disabled`.

Only then does the controller mark a source or batch accepted. Otherwise it writes an exact blocker and next owner.

When checkpoints are enabled, the controller checkpoints acceptance or blocker decisions before pause, handoff, or the next batch.

## 11. Recovery And Long-Run Control

If a fixed specialist session stops or context compacts:

1. Reuse the same fixed session when possible.
2. Send a recovery dispatch that points to durable records.
3. Do not expand scope during recovery.
4. Ask only for missing closeout if files exist but report/temp cleanup is missing.
5. Create a new session only after repeated system failure, severe context pollution, true isolation need, or explicit user approval.

The workflow remains recoverable because state is stored in Markdown files, manifests, logs, verification records, and handoff reports.

When checkpoints are enabled, if the latest checkpoint is older than 3 meaningful file-writing steps or accepted handoffs, recovery starts by creating or repairing it before new broad writes.
