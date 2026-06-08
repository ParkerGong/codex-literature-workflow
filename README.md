# codex-literature-workflow

Agent-native literature workflow for Codex, Zotero, and Obsidian.

[![Preview](https://img.shields.io/badge/status-early%20preview-orange)](#early-preview-notice)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](environment.yml)
[![macOS](https://img.shields.io/badge/platform-macOS%20tested-lightgrey)](#early-preview-notice)
[![License](https://img.shields.io/badge/license-not%20selected-red)](#license)

**English** | [简体中文](README_CN.md)

`codex-literature-workflow` is an early-stage Codex skill for turning a small research direction into a supervised literature workflow: discover papers, screen sources, legally or manually acquire PDFs, register local files, connect them to Zotero, perform PDF-first reading, and build Obsidian/RAG-ready local knowledge notes.

The project exists because agent-led literature work has many sharp edges: source provenance gets lost, browser snippets become false evidence, PDFs are misidentified, Zotero attachments silently become URL fields, Obsidian notes drift away from page evidence, and long Codex conversations lose state. This skill packages a controller-led process to make those failure modes visible and recoverable.

## Critical Disclaimer

This project is a temporary early-preview skill that was summarized by Codex from our own previous small internal tests. It is provided only for developers who urgently need to test this workflow idea. It provides no functional guarantee, no safety guarantee, and no promise that it will behave correctly in your Codex, Zotero, browser, filesystem, or Obsidian environment.

Test this skill only in an **INDEPENDENT, NON-IMPACTING, DEDICATED TEST SPACE**. Do not run it directly against existing production vaults, important Zotero libraries, private PDF collections, browser profiles, or research repositories unless you have backups and understand the risks. This warning exists to avoid catastrophic data loss, accidental overwrites, or accidental publication of private files.

The only workflow currently tested by the maintainer is: follow a research direction, find relevant literature, download **open-access** papers, connect records to Zotero, and create an Obsidian-style local knowledge base. Other workflows are unverified preview paths.

If you hit a bug, first discuss the failure with your own Codex session and inspect the generated controller records before opening an issue. This project currently provides no functional guarantee.

## Early Preview Notice

This repository is an **early preview** for developers who urgently need to test this workflow idea. It provides a framework, records, prompts, scripts, and dependency recommendations. It does **not** provide functional guarantees.

- Project statement: this project is meant to offer the most basic starting solution for users who are not yet sure how to use Codex for literature assistance and local literature management. Many intermediate layers in this repository may be redundant, over-specific, or close to reinventing existing tools. Please do **not** treat this repository as a model of excellent open-source project design.
- Developed primarily on macOS.
- Windows has not been tested.
- Browser, Zotero, Obsidian, and external skill integrations depend on your local Codex setup.
- Legal or authorized access is required for closed-source PDFs. This project does not bypass paywalls, CAPTCHAs, logins, or institutional access controls.
- If something breaks, please open a GitHub issue with your platform, Codex surface, dependency status, and the failing phase.

## The Core Idea

One session must be explicitly chosen as the **Controller Console**. The controller owns the goal, scope, task records, dependency state, session registry, dispatches, and final acceptance.

Specialist sessions do bounded work:

| Session | Role | Main outputs |
| --- | --- | --- |
| Controller Console | Goal, scope, routing, acceptance, recovery | `project_profile.md`, `dependency_setup.md`, kanban, dispatch log, final decisions |
| LiteratureAgent | Source intake, ARS-led discovery, screening, legal/authorized acquisition | candidate tables, source manifest, download log, quality reports |
| ZoteroAgent | Zotero lookup/import and linked-file attachment | Zotero link index, attachment verification |
| ObsidianAgent | PDF-first reading and Obsidian/RAG notes | literature notes, source registry, ingest reports, visual-page evidence |

If a specialist session does not exist, the Controller Console should create one or ask the user to create one, then record it in `00_controller/session_registry.md`. Do not create a fresh session per paper.

## Quick Start

### 1. Prepare the permanent Python environment

Use a named non-`venv` environment so browser fetching, PDF parsing, rendering, and OCR utilities remain available across literature projects.

```bash
micromamba env create -f environment.yml
micromamba activate codex-literature
python3 scripts/env_check.py --json
```

If the environment already exists:

```bash
micromamba activate codex-literature
micromamba env update -f environment.yml
python3 -m pip install -r requirements.txt
python3 scripts/env_check.py --json
```

### 2. Choose the Controller Console

Before starting a long workflow, explicitly tell one Codex session that it is the Controller Console.

Recommended short prompt:

```text
You are the Controller Console for codex-literature-workflow.
Do not do all work yourself.
Initialize controller records, verify dependencies, choose or create fixed specialist sessions, then dispatch small bounded tasks.
Use academic-research-suite as the default literature discovery/screening companion.
Use research-lr-ra only as auxiliary/fallback.
Force local Git checkpoint commits after initialization/scope/dependency/session records, after every 3 meaningful file-writing steps or accepted handoffs, before risky bulk writes, and before pausing or handoff. Do not auto-push.
Only the Controller Console may mark outputs accepted.
```

For long tasks, attach a goal to the controller session.

Recommended long-task goal prompt:

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
- Verify the target root is a Git repository before long work. If it is not, stop and ask the user to initialize Git or designate the correct repo root.
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

### 3. Initialize controller records in the target literature project

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

### 4. Answer the startup scope questions

Before any search, download, Zotero, Obsidian, or PDF-reading work, the Controller Console must ask the user to confirm:

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
11. Target project root for local Git checkpoint commits.

Record these answers in `00_controller/project_profile.md` and set `user_scope_confirmed: true` before dispatching specialist work.

### 5. Keep forced local Git checkpoints

For long workflows, Git checkpointing is mandatory. The Controller Console must create a local commit:

- after initialization, startup-scope, dependency, and session records are written;
- after every 3 meaningful file-writing steps or accepted handoffs;
- before risky bulk writes, Zotero attachment batches, Obsidian note batches, pauses, or handoffs.

Checkpoint commits are local recovery points. The controller must inspect `git status`, run a privacy scan over intended text files, stage explicit safe paths only, and record the result in `00_controller/git_checkpoints.md`. It must not use `git add .`, and it must never push to GitHub unless the user separately asks for that.

### 6. Fill in dependency status before long work

Open the generated `00_controller/dependency_setup.md` and record what is available:

- `academic-research-suite`: default for paper discovery and screening.
- `research-lr-ra`: auxiliary/fallback only.
- `sciencedirect-live-session-fetcher`: preferred authorized browser-session PDF backend.
- `zotero:Zotero`: local Zotero lookup/export/import and verification.
- `zotero-linked-attachments`: attach PDF/MD files to Zotero as linked files.
- Obsidian helpers such as `wiki-query`, `wiki-ingest`, or `obsidian-wiki-ingest`: local KB lookup and note/registry integration.
- Browser, Chrome, and Computer Use tools: source navigation and authorized download mechanics.
- `codex-literature` Python environment and `env_check.py` output.

### 7. Dispatch small batches

The controller should dispatch bounded tasks, wait for durable handoff output, review, checkpoint, then route the next phase. A typical first batch is 3-5 short papers or 1-2 long reports/theses.

## What This Skill Handles

| Phase | Default route |
| --- | --- |
| Research question or direction scoping | `academic-research-suite` |
| External paper discovery and screening | `academic-research-suite` + LiteratureAgent |
| Local PDF library intake | LiteratureAgent, no download by default |
| Authorized publisher download | `sciencedirect-live-session-fetcher`, then Chrome/Computer Use/manual fallback |
| Zotero item and attachment work | `zotero:Zotero` and `zotero-linked-attachments` |
| PDF text/render checks | bundled scripts plus `pdf` skill when available |
| Obsidian/RAG note output | ObsidianAgent plus local wiki/Obsidian helpers |
| Git checkpoints | Controller Console only; local commits, no automatic push |
| Final acceptance | Controller Console only |

## Zotero Connection

Use Zotero for local library state, citation keys, BibTeX/RIS export, parent item lookup/import, collections, and linked-file verification.

Recommended setup:

1. Keep Zotero Desktop available.
2. Enable the Codex Zotero plugin or Zotero MCP/connector in your environment.
3. Use `zotero:Zotero` for library search, exports, item lookup/import, and verification.
4. Use `zotero-linked-attachments` to attach PDFs and later Markdown notes as linked files.
5. Never write directly to `zotero.sqlite`.

## Obsidian Connection

Obsidian integration is intentionally file-first. The controller should choose a vault or project folder, then allow ObsidianAgent to write source registries, literature notes, concept links, and ingest reports inside approved paths.

Recommended setup:

1. Decide the vault/project root before dispatch.
2. Record allowed write paths in `project_profile.md`.
3. Use local helpers such as `wiki-query`, `wiki-ingest`, or `obsidian-wiki-ingest` when available.
4. Keep notes source-grounded: every substantive claim should point back to a paper, page, table, figure, or explicit TODO.

## Repository Layout

```text
.
|-- SKILL.md
|-- README.md
|-- README_CN.md
|-- agents/
|   `-- openai.yaml
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
|   |-- pdf_probe.py
|   `-- setup_env.py
|-- environment.yml
`-- requirements.txt
```

## Validation

Run lightweight checks before committing changes:

```bash
python3 -m py_compile scripts/*.py
python3 -m json.tool evals/evals.json >/dev/null
python3 scripts/env_check.py --json
python3 scripts/init_workspace.py --root /private/tmp/codex_literature_workflow_smoke --force
```

## Roadmap

- More robust install probes for companion skills.
- Cleaner session creation handoff templates for Codex thread tools.
- More complete Zotero and Obsidian verification recipes.
- Small public sample workflow with fake/demo PDFs.
- Windows/WSL testing after the macOS workflow stabilizes.

## Contributing

This project is still shaping its workflow contract. Issues that include exact phase, dependency status, platform, and generated controller files are the most useful.

Please do not submit private PDFs, credentials, Zotero databases, browser cookies, or proprietary Obsidian vault content.

## License

No license has been selected yet. Add one before publishing if you want others to have explicit reuse rights.
