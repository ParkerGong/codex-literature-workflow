# Dependency Setup

Use this reference during project initialization, before long source discovery, download, Zotero, or Obsidian/RAG batches. The controller should record dependency status in `00_controller/dependency_setup.md`.

Read `initialization.md` first so the current or user-selected session is recorded as the Controller Console before dependency checks and specialist dispatches.

## Contents

- Skill and plugin routing
- Install/enable checklist
- Permanent Python environment
- Package coverage and initialization record

## Skill Routing Dependencies

For paper discovery and screening, the default hierarchy is:

| Capability | Default | Fallback or auxiliary use |
| --- | --- | --- |
| Literature discovery, deep research, systematic review planning, query expansion, citation/integrity checks | `academic-research-suite` | none; use generic rubric only if unavailable |
| Legacy LR assistant work, research-gap mapping, representative-work selection | `research-lr-ra` | auxiliary only when ARS is unavailable, explicitly requested, or better suited to a narrow LR subtask |
| End-to-end orchestration from discovery to Zotero/Obsidian | this skill, `codex-literature-workflow` | do not collapse all phases into one unsupervised agent |
| Local Zotero search/export/read-only verification | `zotero:Zotero` | user-mediated import or Desktop write when needed |
| User-run PDF/MD linked-file script preparation and read-only verification | `zotero-linked-attachments` | manual pending status if Zotero is unavailable |
| Existing Obsidian/RAG knowledge lookup | `wiki-query`, `wiki-ingest`, or `obsidian-wiki-ingest` when installed | use only for local KB gap/context, not external paper discovery |
| Obsidian Wiki / LLM Wiki index refresh | QMD (`qmd`) when configured | skip and report, or use lexical/sparse fallback |
| Authorized publisher download from a live browser session | `sciencedirect-live-session-fetcher` | Chrome control, Computer Use once, then manual-user if blocked |

`research-paper-writing` and `dissertation-spine` are writing, argument, chapter, and evidence-maturity skills. Do not use them as default paper-discovery tools.

## Recommended Install Or Enable Checklist

During setup, the Controller Console should explicitly recommend installing or enabling the companions that match the user's requested workflow. Record the status in `00_controller/dependency_setup.md`.

| Companion | Setup recommendation | Origin/source URL | Required when | Fallback if missing |
| --- | --- | --- | --- | --- |
| `academic-research-suite` | install/enable first | Codex adapter: <https://github.com/Imbad0202/academic-research-skills-codex>; upstream suite: <https://github.com/Imbad0202/academic-research-skills> | any external literature discovery or screening | generic screening rubric, but mark ARS unavailable |
| `research-lr-ra` | install vendored copy as auxiliary only | vendored in this repo at `companion-skills/research-lr-ra` | legacy LR workflow or narrow research-gap mapping | skip unless the controller explicitly needs it |
| `zotero:Zotero` plugin/connector | enable before Zotero phases | OpenAI/Codex plugin capability: <https://help.openai.com/en/articles/20001256> | read-only Zotero lookup/export/verification requested | mark Zotero pending/manual; ask the user to perform imports or writes |
| `zotero-linked-attachments` | install vendored copy before linked-file phases | vendored in this repo at `companion-skills/zotero-linked-attachments` | user-run PDF/MD linked-file attachment requested | record pending/manual attachment |
| `sciencedirect-live-session-fetcher` from `Given-Dream/sciencedirect-live-session-fetcher` | install before authorized-browser publisher download tests | <https://github.com/Given-Dream/sciencedirect-live-session-fetcher> | `access_mode=authorized-browser` and publisher route fits | Chrome control, Computer Use once, then manual-user |
| Browser / Chrome / Computer Use plugins | enable when browser/session access is needed | OpenAI/Codex plugin capabilities: <https://help.openai.com/en/articles/20001256> | authenticated browsing, visible UI fallback, or manual verification | stop for user/manual action |
| `pdf` skill | enable when selected visual checks or PDF QA matter | bundled/local Codex skill; no separate public upstream URL confirmed | figure/table/page-render evidence needed | text-only reading plus TODO for visual evidence |
| `wiki-query`, `wiki-ingest`, or `obsidian-wiki-ingest` | install/enable only when local KB/Obsidian integration is requested | public examples to verify before install: <https://github.com/Ar9av/obsidian-wiki>, <https://github.com/AgriciDaniel/claude-obsidian> | existing KB lookup or Obsidian/RAG note output | file-first Markdown notes with pending KB integration |
| QMD (`@tobilu/qmd`) | optional local search/index backend after Obsidian vault writes | npm package: <https://www.npmjs.com/package/@tobilu/qmd> | local BM25/search index over the vault is requested | skip and record `qmd_status`, or use lexical/sparse fallback |

Open-source companions should be installed from their GitHub repositories when a public upstream is known. This repository vendors only the maintainer-built companion skills used by the supported workflow.

Vendored maintainer companion install:

```bash
python3 scripts/install_companion_skills.py
```

Use `--force` only when intentionally replacing an existing local skill copy.

Suggested setup prompt for a new Codex session:

```text
Before running $codex-literature-workflow, check whether these companions are installed or enabled: academic-research-suite, research-lr-ra, zotero:Zotero, zotero-linked-attachments, sciencedirect-live-session-fetcher, Browser/Chrome/Computer Use, pdf, local wiki/Obsidian helpers, and optional QMD when Obsidian/RAG indexing is requested. Recommend GitHub installation for public companions, use scripts/install_companion_skills.py for vendored maintainer-built companions, then record ready/pending/unavailable status in 00_controller/dependency_setup.md. Do not begin long literature work until the missing-dependency fallback is explicit.
```

## Python Environment

Recommended permanent non-venv environment:

```bash
micromamba env create -f environment.yml
micromamba activate codex-literature
python3 scripts/env_check.py --json --strict
```

If `micromamba` is unavailable, use the equivalent `mamba` or `conda` commands and record which manager supplied the environment.

If the environment already exists:

```bash
micromamba activate codex-literature
micromamba env update -f environment.yml
python3 -m pip install -r requirements.txt
python3 scripts/env_check.py --json --strict
```

When this checklist is generated inside another project by `scripts/init_workspace.py`, use the absolute `environment.yml`, `requirements.txt`, and `env_check.py` paths written in that generated file.

This installs or verifies:

- Python 3.12;
- `poppler` command-line tools: `pdftoppm`, `pdftotext`;
- `tesseract`;
- Python packages from `requirements.txt`.

QMD is optional and uses Node/npm rather than the Python environment. Do not require QMD for basic Obsidian note creation. Treat `.qmd/` as local runtime state, not source material.

Avoid macOS system Python. Use one dedicated named environment and record the interpreter path in controller notes.

## Python Package Coverage

`requirements.txt` combines this skill's runtime needs with the public `Given-Dream/sciencedirect-live-session-fetcher` requirements:

| Package | Used for |
| --- | --- |
| `pypdf` | PDF metadata and page text extraction |
| `pdfplumber` | layout/table-oriented PDF text fallback |
| `pymupdf` | selected-page rendering and robust PDF probing |
| `pillow` | render/image verification |
| `requests` | metadata/API calls when needed |
| `beautifulsoup4` | HTML metadata parsing |
| `selenium` | visible browser/session automation |
| `websocket-client` | Chrome/Edge DevTools remote-debugging attachment |

## Initialization Checklist

When `scripts/init_workspace.py` creates controller records, the controller should fill in:

- `academic-research-suite`: installed, unavailable, or pending install;
- `research-lr-ra`: auxiliary installed, unavailable, or not needed;
- `sciencedirect-live-session-fetcher`: installed, unavailable, or only needed for authorized-browser downloads;
- `zotero:Zotero` and `zotero-linked-attachments`: enabled, disabled, or pending;
- Obsidian/RAG helper skills: installed, disabled, or pending;
- QMD: installed, skipped, failed, or not needed; collection name when configured; embed approval status;
- Python interpreter path for the permanent environment;
- output of `python3 scripts/env_check.py --json --strict`;
- missing CLI tools or packages and the next install action.

Do not start a long search/download/read batch until dependency status is either ready or explicitly recorded as a conscious fallback.
