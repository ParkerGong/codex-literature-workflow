# codex-literature-workflow

Agent-native literature workflow for Codex, Zotero, and Obsidian.

[![Stable](https://img.shields.io/badge/status-formal%20release-brightgreen)](#release-scope)
[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](VERSION)
[![Validate](https://github.com/ParkerGong/codex-literature-workflow/actions/workflows/validate.yml/badge.svg)](https://github.com/ParkerGong/codex-literature-workflow/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/python-3.12%20tested-blue)](environment.yml)
[![macOS](https://img.shields.io/badge/platform-macOS%20tested-lightgrey)](#release-scope)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**English** | [简体中文](README_CN.md)

Release evidence: [1.0.0 audit](RELEASE_AUDIT.md)

## Public Interest Statement

This is a public-interest project for people who want to use Codex for literature management, connect Zotero for easier reading, and build a private Obsidian knowledge base, but do not know where to start. It provides only the most basic workflow idea. Many steps in this workflow are still token-expensive and need optimization, so please do **not** treat this project as the definitive or authoritative way to use Codex for literature workflows.

`codex-literature-workflow` is a controller-led Codex skill for turning a research direction or local PDF library into a supervised literature workflow: discover and screen sources, legally or manually acquire PDFs, register local files, connect them to Zotero, perform PDF-first reading, and build manifest-backed Obsidian notes with optional QMD refresh.

The project exists because agent-led literature work has many sharp edges: source provenance gets lost, browser snippets become false evidence, PDFs are misidentified, Zotero attachments silently become URL fields, Obsidian notes drift away from page evidence, and long Codex conversations lose state. This skill packages a controller-led process to make those failure modes visible and recoverable.

## Release Scope

Version 1.0.0 is the formal release of the workflow contract and its deterministic helpers. Offline regression tests cover skill metadata, safe installation, controller-workspace initialization and backup, environment reporting, PDF probe success/failure semantics, and Zotero linked-file mapping/verification with mocked Local API responses.

The 1.0.0 release gate passes 40/40 offline regression tests and validates all three skill trees: the main skill and both vendored companions. See the [release audit](RELEASE_AUDIT.md) for the tested core, integration evidence, and deliberate manual boundaries.

Live integrations remain conditional on the user's machine:

- Zotero Desktop writes require the user to run the generated JavaScript and then verify through the Local API. This release never writes `zotero.sqlite`.
- Obsidian integration is file-first and must stay inside explicitly allowed vault paths.
- QMD is optional. Update/search may require pinning QMD to the Node prefix that installed its native modules; embeddings are never run without explicit approval.
- Authenticated publisher access depends on lawful user or institutional access. The workflow does not bypass paywalls, CAPTCHAs, logins, or license controls.
- macOS is the maintained test platform. Windows remains unverified.

Use an isolated workspace for the first run and keep backups of important Zotero libraries and Obsidian vaults. Report failures with the phase, platform, dependency state, command output, and generated controller records; never include private PDFs, credentials, cookies, or database files.

## The Core Idea

For a long multi-phase run, the current task becomes the **Controller Console** unless the user already selected another controller. It owns scope, task records, dependency state, session registry, dispatches, and final acceptance; it owns a persistent goal only when the user explicitly requests goal tracking.

Specialist sessions do bounded work:

| Session | Role | Main outputs |
| --- | --- | --- |
| Controller Console | Scope, optional goal, routing, acceptance, recovery | `project_profile.md`, `dependency_setup.md`, kanban, dispatch log, final decisions |
| LiteratureAgent | Source intake, ARS-led discovery, screening, legal/authorized acquisition | candidate tables, source manifest, download log, quality reports |
| ZoteroAgent | Read-only lookup, linked-file mapping/script preparation, verification | Zotero link index, generated script, attachment verification |
| ObsidianAgent | PDF-first reading, Obsidian Wiki ingest, optional QMD/RAG refresh status | literature notes, `.manifest.json`, source registry, ingest reports, visual-page evidence |

If multi-agent tools are available, create or reuse fixed specialist sessions and record them in `00_controller/session_registry.md`. Otherwise execute the same bounded phases sequentially and preserve the handoff/status contract. Do not create a fresh session per paper.

## Quick Start

### 1. Install the main skill

From a clone of this repository, dry-run the install and then create the installable skill package in the canonical skill directory:

```bash
python3 scripts/install_skill.py --dry-run
python3 scripts/install_skill.py
```

Use `--force` only for an intentional backed-up replacement. Start a new Codex task and invoke `$codex-literature-workflow` to verify discovery.

#### Upgrade from a preview install

Preview installs are never overwritten silently. Review the backed-up replacement first, then run it explicitly:

```bash
python3 scripts/install_skill.py --dry-run --force
python3 scripts/install_skill.py --force
```

Before replacement, the installer moves the existing skill directory into a timestamped backup under the configured Codex home.

### 2. Prepare the permanent Python environment

Use a named non-`venv` environment so browser fetching, PDF parsing, rendering, and OCR utilities remain available across literature projects.

```bash
micromamba env create -f environment.yml
micromamba activate codex-literature
python3 scripts/env_check.py --json --strict
```

If `micromamba` is unavailable, use the equivalent `mamba env create -f environment.yml` or `conda env create -f environment.yml`, then activate `codex-literature`.

If the environment already exists:

```bash
micromamba activate codex-literature
micromamba env update -f environment.yml
python3 -m pip install -r requirements.txt
python3 scripts/env_check.py --json --strict
```

### 3. Install or enable companion skills/plugins

Before a real test run, ask Codex to install or enable the companion skills/plugins that match the workflow you want to test:

Public/open-source companion skills should be installed from their GitHub repositories when a public upstream is known. This repository only vendors the maintainer-built companion skills listed below.

| Companion | Recommended status | Origin/source URL | Used for |
| --- | --- | --- | --- |
| `academic-research-suite` | strongly recommended | Codex adapter: <https://github.com/Imbad0202/academic-research-skills-codex>; upstream suite: <https://github.com/Imbad0202/academic-research-skills> | default literature discovery, screening strategy, query expansion, citation/integrity checks |
| `research-lr-ra` | optional auxiliary | vendored in this repo at `companion-skills/research-lr-ra` | legacy LR support and narrow research-gap mapping when ARS is unavailable or explicitly better |
| `zotero:Zotero` plugin/connector | optional unless Zotero output is requested | OpenAI/Codex plugin capability; see <https://help.openai.com/en/articles/20001256> | read-only Zotero lookup, export, collections, and verification; user-mediated imports |
| `zotero-linked-attachments` | optional unless Zotero linked files are requested | vendored in this repo at `companion-skills/zotero-linked-attachments` | prepare user-run PDF/MD linked-file scripts and verify the result read-only |
| `sciencedirect-live-session-fetcher` from `Given-Dream/sciencedirect-live-session-fetcher` | optional; recommended for authorized-browser publisher download tests | <https://github.com/Given-Dream/sciencedirect-live-session-fetcher> | reuse a live authorized browser session for publisher PDF routes |
| Browser / Chrome / Computer Use plugins | optional but useful | OpenAI/Codex plugin capabilities; see <https://help.openai.com/en/articles/20001256> | browser navigation, authenticated sessions, UI fallback |
| `wiki-query`, `wiki-ingest`, or `obsidian-wiki-ingest` | optional unless local KB integration is requested | examples to verify before install: <https://github.com/Ar9av/obsidian-wiki>, <https://github.com/AgriciDaniel/claude-obsidian> | existing knowledge-base lookup and Obsidian/RAG-style note integration |
| QMD (`@tobilu/qmd`) | optional unless local vault search/index refresh is requested | npm package: <https://www.npmjs.com/package/@tobilu/qmd> | update and query a local vault index; embeddings require explicit approval |

If a companion is unavailable, record it in `00_controller/dependency_setup.md` and use the documented fallback path. Do not silently pretend that an unavailable companion was used.

To install the vendored maintainer-built companion skills into the current Codex skills directory:

```bash
python3 scripts/install_companion_skills.py
```

Use `--force` only when you intentionally want to overwrite an existing local copy.

### 4. Record the Controller Console

Before starting a long workflow, record the current task as Controller Console unless another controller has already been selected.

Recommended short prompt:

```text
You are the Controller Console for codex-literature-workflow.
Do not do all work yourself.
Initialize controller records, verify dependencies, choose or create fixed specialist sessions, then dispatch small bounded tasks.
Use academic-research-suite as the default literature discovery/screening companion.
Use research-lr-ra only as auxiliary/fallback.
Create local Git checkpoints only when I or the host project explicitly enable them. Never auto-push.
Only the Controller Console may mark outputs accepted.
```

Attach a persistent product goal only when the user explicitly requests goal tracking. Otherwise record `long_task_goal: not-needed`.

Recommended long-task goal prompt:

```text
Goal: Build a source-grounded Zotero and Obsidian-ready literature workspace for <TOPIC_OR_DIRECTION>.

You are the Controller Console for codex-literature-workflow.

Rules:
- Keep this session as the only controller and acceptance owner.
- Do not perform every phase yourself unless a phase is tiny.
- Create or reuse fixed specialist sessions:
  - LiteratureAgent for ARS-led search, screening, legal/authorized acquisition, and source manifests.
  - ZoteroAgent for Zotero parent/collection lookup, linked PDF/MD script preparation, and verification; the user runs Desktop writes.
  - ObsidianAgent for PDF-first reading, selected visual checks, Obsidian Wiki manifest-backed notes, and optional QMD/local RAG refresh status.
- Create or reuse fixed specialist sessions when supported; otherwise record and use sequential phase execution.
- Before any long batch, initialize controller records and dependency_setup.md.
- Before a full multi-phase run, ask for paper direction, expected paper count, source input mode, download/access permission, language scope, Zotero connection, Obsidian connection, local input paths, output paths, collection/vault mapping needs, and checkpoint policy.
- Record those answers in project_profile.md and set user_scope_confirmed=true before dispatch.
- If Git checkpoints are enabled, verify the target root before committing. If disabled, record that state and continue.
- When enabled, checkpoint only explicit privacy-reviewed files at the configured interval.
- Run privacy scans before staging files. Do not commit private PDFs, Zotero databases, browser cookies, credentials, or closed vault content unless explicitly approved. Never push automatically.
- Use academic-research-suite as the default research companion for literature discovery and screening.
- Use research-lr-ra only as auxiliary/fallback when ARS is unavailable or a narrow LR task fits it better.
- Do not bypass paywalls, logins, CAPTCHAs, or institutional access controls.
- Do not write zotero.sqlite directly.
- Do not treat QMD as the source of truth. QMD is optional index/search infrastructure; run qmd embed only with explicit approval.
- Do not claim paper facts from snippets or model memory.
- Every phase must write a durable handoff and update its worklog.
- Stop at Waiting review for specialist outputs; controller acceptance is separate.

Start by creating or updating the controller workspace records, dependency setup record, session registry, and first small dispatch plan.
```

### 5. Initialize controller records in the target literature project

Run this from the skill repository:

```bash
python3 scripts/init_workspace.py --root /path/to/literature/project
```

This creates:

- `00_controller/project_profile.md`
- `00_controller/initialization.md`
- `00_controller/dependency_setup.md`
- `00_controller/session_registry.md`
- `00_controller/git_checkpoints.md`
- controller and specialist worklogs
- source/download/Zotero/ingest manifests
- handoff and status files

### 6. Answer the startup scope questions

Before a full multi-phase search/download/Zotero/Obsidian run, the Controller Console confirms missing material scope fields. A bounded single-phase request asks only relevant fields.

1. Paper direction or research boundary.
2. Target number of papers for the first batch.
3. Source mode: local PDFs, new search/download, or mixed.
4. Whether new PDF download/acquisition is enabled, and whether access is open-only or authorized browser/manual.
5. Language scope: English, Chinese, or both.
6. Whether Zotero should be connected.
7. Whether Obsidian/RAG-ready notes should be created.
8. Zotero collection or mapping document, if Zotero is enabled.
9. Obsidian vault/project root and allowed write paths, if Obsidian is enabled.
10. Existing direction documents, literature indexes, PDF folders, manifests, or mapping files.
11. Whether QMD refresh is enabled, which collection to reuse/create, and whether embeddings are approved.
12. Whether local Git checkpoints are enabled and, if so, the target Git root.

Record these answers in `00_controller/project_profile.md` and set `user_scope_confirmed: true` before dispatching specialist work.

### 7. Configure optional local Git checkpoints

Git checkpointing is disabled by default in the generic profile. Enable it only when the user or host-project protocol requests local recovery commits. When enabled, create a local commit:

- after initialization, startup-scope, dependency, and session records are written;
- after every 3 meaningful file-writing steps or accepted handoffs;
- before risky bulk writes, Zotero attachment batches, Obsidian note batches, pauses, or handoffs.

Checkpoint commits are local recovery points. The controller must inspect `git status`, run a privacy scan over intended text files, stage explicit safe paths only, and record the result in `00_controller/git_checkpoints.md`. It must not use `git add .`, and it must never push to GitHub unless the user separately asks for that.

### 8. Fill in dependency status before long work

Open the generated `00_controller/dependency_setup.md` and record what is available:

- `academic-research-suite`: default for paper discovery and screening.
- `research-lr-ra`: auxiliary/fallback only.
- `sciencedirect-live-session-fetcher`: preferred authorized browser-session PDF backend.
- `zotero:Zotero`: read-only Zotero lookup/export/verification; imports remain user-mediated.
- `zotero-linked-attachments`: prepare user-run PDF/MD linked-file scripts and verify the result read-only.
- Obsidian helpers such as `wiki-query`, `wiki-ingest`, or `obsidian-wiki-ingest`: local KB lookup and note/registry integration.
- QMD: optional local search/index backend after vault writes; not required for basic notes.
- Browser, Chrome, and Computer Use tools: source navigation and authorized download mechanics.
- `codex-literature` Python environment and `env_check.py` output.

### 9. Dispatch small batches

The controller should dispatch bounded tasks, wait for durable handoff output, review, checkpoint when enabled, then route the next phase. A typical first batch is 3-5 short papers or 1-2 long reports/theses.

## What This Skill Handles

| Phase | Default route |
| --- | --- |
| Research question or direction scoping | `academic-research-suite` |
| External paper discovery and screening | `academic-research-suite` + LiteratureAgent |
| Local PDF library intake | LiteratureAgent, no download by default |
| Authorized publisher download | `sciencedirect-live-session-fetcher`, then Chrome/Computer Use/manual fallback |
| Zotero item and attachment work | `zotero:Zotero` and `zotero-linked-attachments` |
| PDF text/render checks | bundled scripts and the configured Python environment |
| Obsidian Wiki / manifest-backed note output | ObsidianAgent plus local wiki/Obsidian helpers |
| QMD/local RAG refresh | optional `qmd update` + status/search verification, or lexical/sparse fallback |
| Git checkpoints | Controller Console only; local commits, no automatic push |
| Final acceptance | Controller Console only |

## Zotero Connection

Use Zotero for local library state, citation keys, BibTeX/RIS export, parent-item lookup, user-mediated import, collections, and linked-file verification.

Recommended setup:

1. Ask the user to open Zotero Desktop when a live step is needed.
2. Enable the Codex Zotero plugin or Zotero MCP/connector in your environment.
3. Use `zotero:Zotero` for read-only library search, exports, item lookup, and verification; keep imports user-confirmed.
4. Use `zotero-linked-attachments` to prepare validated linked-file mappings/scripts, ask the user to run them, then verify the PDF or Markdown child attachments.
5. Never write directly to `zotero.sqlite`.

## Obsidian Connection

Obsidian integration is intentionally file-first. The controller should choose a vault or project folder, then allow ObsidianAgent to write source registries, literature notes, concept links, and ingest reports inside approved paths.

Recommended setup:

1. Decide the vault/project root before dispatch.
2. Record allowed write paths in `project_profile.md`.
3. Use local helpers such as `wiki-query`, `wiki-ingest`, or `obsidian-wiki-ingest` when available.
4. Use manifest-backed Obsidian Wiki / LLM Wiki style ingestion when the project needs durable RAG-ready state: `.manifest.json`, `01_sources/source_registry.md`, `01_sources/zotero_link_index.md`, and one formal note per canonical source.
5. Keep notes source-grounded: every substantive claim should point back to a paper, page, table, figure, or explicit TODO.

## QMD / Local RAG

QMD is optional. It can refresh a local search/index layer after vault writes:

```bash
npm install -g @tobilu/qmd
qmd init
qmd collection list
qmd collection add <VAULT_PATH> --name <COLLECTION_NAME>  # only when absent; otherwise reuse the verified path
qmd update
qmd search "<known query>" -c <COLLECTION_NAME> -n 5
```

QMD is not the source of truth. Do not run `qmd embed`, `qmd query`, or `qmd vsearch` unless the user approves model downloads and embedding compute. If multiple Node installations cause a native-module ABI error, use the pinned-PATH recovery in `references/qmd-rag.md`.

## Repository Layout

```text
.
|-- SKILL.md
|-- README.md
|-- README_CN.md
|-- RELEASE_AUDIT.md
|-- LICENSE
|-- VERSION
|-- agents/
|   `-- openai.yaml
|-- companion-skills/
|   |-- research-lr-ra/
|   `-- zotero-linked-attachments/
|-- evals/
|   `-- evals.json
|-- references/
|   |-- initialization.md
|   |-- dependencies.md
|   |-- architecture.md
|   |-- controller-records.md
|   |-- environment.md
|   `-- ...
|-- scripts/
|   |-- env_check.py
|   |-- init_workspace.py
|   |-- install_skill.py
|   |-- install_companion_skills.py
|   |-- pdf_probe.py
|   |-- setup_env.py
|   `-- validate_skills.py
|-- tests/
|   `-- test_*.py
|-- environment.yml
|-- requirements.txt
`-- requirements-dev.txt
```

## Validation

Run these checks from the activated `codex-literature` environment created from `environment.yml`. If using another environment, install the declared Python dependencies and the required system PDF/OCR tools, including Poppler and Tesseract, first.

```bash
python3 -m pip install -r requirements.txt -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 -m py_compile scripts/*.py
python3 -m json.tool evals/evals.json >/dev/null
node --check companion-skills/zotero-linked-attachments/scripts/build_zotero_linked_attachment_js.mjs
node --check companion-skills/zotero-linked-attachments/scripts/verify_zotero_linked_attachments.mjs
python3 -m unittest discover -s tests -v
python3 scripts/env_check.py --json --strict
python3 scripts/init_workspace.py --root /private/tmp/codex_literature_workflow_smoke --dry-run
```

## Roadmap

- Opt-in live Zotero integration tests against a disposable test library.
- Reproducible public sample workflow with non-proprietary demo PDFs.
- Add Windows/WSL validation and platform-specific setup guidance.

## Contributing

Issues that include the exact phase, dependency status, platform, generated controller files, and sanitized failure output are the most useful.

Please do not submit private PDFs, credentials, Zotero databases, browser cookies, or proprietary Obsidian vault content.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
