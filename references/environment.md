# Environment Setup

Always check the environment before search/download batches or PDF reading batches. Keep project repositories clean: put temporary environments, rendered pages, and text dumps outside the repo unless the user asks otherwise.

Read `dependencies.md` first during new project initialization so companion skills, permanent Python environment paths, and missing install actions are recorded together.

## Contents

- Permanent Python environment and requirements
- Optional Node/QMD setup
- Disposable fallback and readiness checks
- PDF probing, reading levels, temporary files, and GUI boundaries

## Permanent Non-Venv Python Environment

For repeated Codex literature work, prefer one dedicated, permanent named environment instead of creating a fresh project venv for every batch. This keeps browser-session fetching, PDF reading, rendering, Poppler/Tesseract command-line tools, and Zotero/Obsidian-adjacent helpers available from a stable path.

Recommended pattern on macOS with `micromamba`, `mamba`, or `conda`:

```bash
micromamba create -n codex-literature -c conda-forge python=3.12 pip poppler tesseract
micromamba activate codex-literature
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
```

If `micromamba` is unavailable, substitute `mamba` or `conda` for the create/activate commands. This host fallback is supported; do not report the environment blocked merely because one manager name is absent.

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

## Optional Node / QMD Environment

QMD is optional. It is useful after Obsidian Wiki / LLM Wiki style vault writes when a project wants a local search/index backend. It is not required for basic Obsidian note creation.

Recommended checks:

```bash
node --version
npm --version
qmd --version
```

Install only when the user/project wants QMD:

```bash
npm install -g @tobilu/qmd
```

Record:

- `QMD_CLI`, usually `qmd`;
- `QMD_WIKI_COLLECTION`, when configured;
- whether `qmd init`, idempotent collection reuse/add, `qmd update`, and `qmd search` succeeded;
- whether embeddings are approved.

Do not run `qmd embed` by default. It may download GGUF models and consume local disk/CPU/GPU.

If `qmd --version` works but `qmd init` or `qmd update` fails with a `better-sqlite3` / `NODE_MODULE_VERSION` mismatch, record QMD as failed and let the user's Codex adapt the Node/npm repair to that machine. Do not make QMD a blocker for basic vault notes.

On machines with several Node installations, QMD can pass `qmd --version` but fail when its launcher starts a second Node process. Compare `node --version`, `node -p process.versions.modules`, `type -a node`, and `qmd doctor`. If the QMD error reports a different Node version, pin QMD commands to the Node prefix that installed QMD:

```bash
QMD_BIN="$(command -v qmd)"
QMD_NODE_BIN="$(dirname "$QMD_BIN")"
QMD_PATH="$QMD_NODE_BIN:/usr/bin:/bin:/usr/sbin:/sbin"
env PATH="$QMD_PATH" "$QMD_BIN" doctor
env PATH="$QMD_PATH" "$QMD_BIN" init
```

Record this as a local environment repair before continuing.

Keep local QMD/RAG runtime state out of Git:

```gitignore
.qmd/
10_knowledge_base/.rag/
```

## Temporary Venv Fallback

Recommended location:

```bash
/private/tmp/codex_literature_workflow_venv_<task-id>
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

The helper accepts only a brand-new target. The final path must not exist, no final or ancestor path component may be a symlink, and the target must not equal, contain, or sit inside this skill repository. Use a unique disposable path for every creation attempt.

Create a temporary environment without installing packages:

```bash
python3 scripts/setup_env.py --venv /private/tmp/codex_literature_workflow_venv_<task-id>
```

When network/dependency installation is allowed, create the new environment and install the recommended packages in the same invocation:

```bash
python3 scripts/setup_env.py --venv /private/tmp/codex_literature_workflow_venv_<task-id> --install
```

Do not pre-create the target and do not rerun the helper against an existing or partially created venv. For an existing venv, use that environment's own pip directly, for example `/path/to/existing-venv/bin/python -m pip install -r requirements.txt` (or `Scripts\\python.exe` on Windows). If a creation attempt is partial, inspect it and choose another new target; the helper will not rewrite it.

The setup script prints the Python and pip paths to use for later `env_check.py` and `pdf_probe.py` runs.

## Environment Check

Run:

```bash
python3 scripts/env_check.py --json --strict
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
- mark a blank/scan-only selected range as not text-ready even when parsing succeeds;
- refuse symlink output directories/files rather than following them;
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

Only use Chrome or Computer Use when the user or project profile allows it. Zotero Local API access is read-only; Zotero Desktop writes remain user-run in this release.

Record:

- browser/tool used;
- whether the access was open, authorized institutional, connector/manual, or unavailable;
- login/CAPTCHA/payment blockers;
- downloaded file path and verification status.
