# Environment Setup

Always check the environment before search/download batches or PDF reading batches. Keep project repositories clean: put temporary environments, rendered pages, and text dumps outside the repo unless the user asks otherwise.

Read `dependencies.md` first during new project initialization so companion skills, permanent Python environment paths, and missing install actions are recorded together.

## Permanent Non-Venv Python Environment

For repeated Codex literature work, prefer one dedicated, permanent named environment instead of creating a fresh project venv for every batch. This keeps browser-session fetching, PDF reading, rendering, Poppler/Tesseract command-line tools, and Zotero/Obsidian-adjacent helpers available from a stable path.

Recommended pattern on macOS with `micromamba` or Miniforge:

```bash
micromamba create -n codex-literature -c conda-forge python=3.12 pip poppler tesseract
micromamba activate codex-literature
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
```

Record the resulting interpreter path in host-project controller notes:

```text
python: ~/.local/share/mamba/envs/codex-literature/bin/python
requirements: codex-literature-workflow/requirements.txt
```

If `micromamba` is not available and you want a strict non-`venv` layout, use a dedicated pyenv Python interpreter and install into that interpreter's own site-packages:

```bash
pyenv install 3.12.8
pyenv shell 3.12.8
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
pyenv prefix
```

Record that interpreter path explicitly:

```text
python: /Users/<user>/.pyenv/versions/3.12.8/bin/python
requirements: codex-literature-workflow/requirements.txt
```

Avoid installing into macOS system Python. Homebrew Python may also reject global pip installs through externally managed environment protections; a dedicated pyenv interpreter is cleaner and easier to repair.

## Requirements

The combined Python requirements cover:

- `sciencedirect-live-session-fetcher`: `selenium`, `websocket-client`.
- PDF text and rendering: `pypdf`, `pdfplumber`, `pymupdf`, `pillow`.
- Web metadata and parsing helpers: `requests`, `beautifulsoup4`.

Install from the repository root:

```bash
python3 -m pip install -r requirements.txt
```

## Temporary Venv Fallback

Recommended location:

```bash
/private/tmp/codex_literature_workflow_venv
```

Recommended packages:

- `pypdf`: quick text and metadata extraction.
- `pdfplumber`: layout/table-oriented text fallback.
- `pymupdf`: selected-page rendering and robust PDF probing.
- `pillow`: image verification and compression.
- `requests`: optional metadata/API calls.
- `beautifulsoup4`: optional HTML metadata extraction.
- `selenium`: visible browser automation for mixed-publisher routes.
- `websocket-client`: Chrome/Edge DevTools remote-debugging attachment.

Use this fallback when a host project explicitly wants an isolated disposable environment. If dependency download is blocked by sandbox/network policy, ask for approval.

Create a temporary environment with:

```bash
python3 scripts/setup_env.py --venv /private/tmp/codex_literature_workflow_venv
```

Install recommended packages only when network/dependency installation is allowed:

```bash
python3 scripts/setup_env.py --venv /private/tmp/codex_literature_workflow_venv --install
```

The setup script prints the Python and pip paths to use for later `env_check.py` and `pdf_probe.py` runs.

## Environment Check

Run:

```bash
python3 scripts/env_check.py --json
```

Expected checks:

- Python version.
- Import availability and versions for `pypdf`, `pdfplumber`, `fitz`, `PIL`, `requests`, `bs4`, `selenium`, and `websocket`.
- CLI availability for `pdftoppm`, `pdftotext`, `tesseract`.
- Writable temp directory.
- Browser tools or GUI automation availability, if relevant in the host environment.

## PDF Probe

Use this for a single PDF or a small test batch:

```bash
python3 scripts/pdf_probe.py paper.pdf --pages 1,3,9 --out /private/tmp/codex_literature_workflow_probe
```

It should:

- extract page text into `texts/`;
- render only selected pages into `renders/` when PyMuPDF is available;
- write `probe_report.json`;
- fail honestly if rendering is unavailable.

## Reading Levels

Classify each PDF before note writing:

| Level | Meaning | Action |
| --- | --- | --- |
| `text-ok` | clean text; claims do not depend on figures/tables/curves | no rendering required |
| `selected-visual` | diagrams, tables, formulas, screenshots, or curves matter | render selected pages |
| `vision-model` | image semantics are central and local visual inspection is not enough | ask user before using a vision-capable model |
| `scan-or-ocr` | text layer missing or garbled | OCR path required; do not claim full reading |
| `bad-pdf` | wrong, incomplete, encrypted, or non-article PDF | mark manual-check |

## Temporary Artifacts

Keep temporary paths explicit in reports:

- original temp path;
- moved or deleted path;
- size and file count;
- whether the reusable Python environment was preserved.

For shared projects, prefer soft-moving disposable artifacts to a trash-like temp folder instead of deleting them immediately.

Strict temp cleanup policy:

```text
/private/tmp/codex_agent_trash/<date>_<task-id>_<slug>/
```

Use this style when the host project asks for recoverable cleanup:

1. Count files and bytes before moving.
2. Move disposable temp outputs to the trash folder.
3. Record original path, moved path, bytes, file count, and cleanup owner.
4. Preserve venvs unless the controller explicitly asks to rebuild or remove them.
5. Avoid default destructive cleanup commands for project artifacts.

## Browser And GUI Access Check

Only use Chrome, Computer Use, or Zotero Desktop automation when the user or project profile allows it.

Record:

- browser/tool used;
- whether the access was open, authorized institutional, connector/manual, or unavailable;
- login/CAPTCHA/payment blockers;
- downloaded file path and verification status.
