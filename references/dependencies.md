# Dependency Setup

Use this reference during project initialization, before long source discovery, download, Zotero, or Obsidian/RAG batches. The controller should record dependency status in `00_controller/dependency_setup.md`.

Read `initialization.md` first so one session is designated as the Controller Console before dependency checks and specialist dispatches.

## Skill Routing Dependencies

For paper discovery and screening, the default hierarchy is:

| Capability | Default | Fallback or auxiliary use |
| --- | --- | --- |
| Literature discovery, deep research, systematic review planning, query expansion, citation/integrity checks | `academic-research-suite` | none; use generic rubric only if unavailable |
| Legacy LR assistant work, research-gap mapping, representative-work selection | `research-lr-ra` | auxiliary only when ARS is unavailable, explicitly requested, or better suited to a narrow LR subtask |
| End-to-end orchestration from discovery to Zotero/Obsidian | this skill, `codex-obsidian-read` | do not collapse all phases into one unsupervised agent |
| Local Zotero search/export/import | `zotero:Zotero` | Zotero Desktop/API only when enabled |
| PDF/MD linked-file attachment to Zotero | `zotero-linked-attachments` | manual pending status if Zotero is unavailable |
| Existing Obsidian/RAG knowledge lookup | `wiki-query`, `wiki-ingest`, or `obsidian-wiki-ingest` when installed | use only for local KB gap/context, not external paper discovery |
| Authorized publisher download from a live browser session | `sciencedirect-live-session-fetcher` | Chrome control, Computer Use once, then manual-user if blocked |

`research-paper-writing` and `dissertation-spine` are writing, argument, chapter, and evidence-maturity skills. Do not use them as default paper-discovery tools.

## Python Environment

Recommended permanent non-venv environment:

```bash
micromamba env create -f environment.yml
micromamba activate codex-lit
python3 scripts/env_check.py --json
```

If the environment already exists:

```bash
micromamba activate codex-lit
micromamba env update -f environment.yml
python3 -m pip install -r requirements.txt
python3 scripts/env_check.py --json
```

When this checklist is generated inside another project by `scripts/init_workspace.py`, use the absolute `environment.yml`, `requirements.txt`, and `env_check.py` paths written in that generated file.

This installs or verifies:

- Python 3.12;
- `poppler` command-line tools: `pdftoppm`, `pdftotext`;
- `tesseract`;
- Python packages from `requirements.txt`.

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
- Python interpreter path for the permanent environment;
- output of `python3 scripts/env_check.py --json`;
- missing CLI tools or packages and the next install action.

Do not start a long search/download/read batch until dependency status is either ready or explicitly recorded as a conscious fallback.
