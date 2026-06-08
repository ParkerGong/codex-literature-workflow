# Codex Obsidian Read

Codex Obsidian Read is a controller-led Codex skill for literature workflows. It helps route a topic, research direction, or local PDF library through source intake, optional legal or authorized acquisition, optional Zotero linked-file attachment, PDF-first reading, selected visual checks, and optional Obsidian/RAG-ready notes.

The skill is designed for long-running work where durable state matters: a controller keeps the scope, task records, manifests, and acceptance checks, while specialist sessions handle literature search, Zotero work, and note creation.

## What It Provides

- A skill entry point in `SKILL.md`.
- Workflow runbooks in `references/`.
- Python helper scripts in `scripts/` for environment checks, workspace scaffolding, dependency setup, and PDF probing.
- Example eval prompts in `evals/evals.json`.
- Agent metadata in `agents/openai.yaml`.

## Repository Layout

```text
.
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- evals/
|   `-- evals.json
|-- references/
|   |-- architecture.md
|   |-- controller-records.md
|   |-- environment.md
|   `-- ...
|-- scripts/
|   |-- env_check.py
|   |-- init_workspace.py
|   |-- pdf_probe.py
|   `-- setup_env.py
`-- requirements.txt
```

## Quick Start

Check the local environment:

```bash
python3 scripts/env_check.py
```

Install the combined runtime requirements in a dedicated permanent Python interpreter:

```bash
python3 -m pip install -r requirements.txt
```

For a permanent non-`venv` environment with PDF command-line tools included, use `micromamba` or Miniforge:

```bash
micromamba env create -f environment.yml
micromamba activate codex-lit
python scripts/env_check.py
```

Create a dedicated temporary Python environment only when a host project wants isolation:

```bash
python3 scripts/setup_env.py --venv /private/tmp/codex_obsidian_read_venv
```

Install recommended packages when dependency downloads are allowed:

```bash
python3 scripts/setup_env.py --venv /private/tmp/codex_obsidian_read_venv --install
```

Initialize controller workspace records in a target project:

```bash
python3 scripts/init_workspace.py --root /path/to/literature/project
```

Probe selected pages from a PDF:

```bash
python3 scripts/pdf_probe.py paper.pdf --pages 1,3,9 --out /private/tmp/codex_obsidian_read_probe
```

## Safety Notes

- Do not write directly to `zotero.sqlite`.
- Do not bypass paywalls, logins, CAPTCHA, or institutional access controls.
- Keep PDFs, rendered pages, text dumps, and temporary environments outside this repository unless intentionally preserving test fixtures.
- Record provenance for accepted sources: query/source date, URL/DOI when available, local PDF path, Zotero key or pending status, page evidence, and unresolved risks.

## Validation

Run these checks before committing:

```bash
python3 -m py_compile scripts/*.py
python3 -m json.tool evals/evals.json >/dev/null
python3 scripts/env_check.py --json
```

## License

No license has been selected yet. Add one before publishing if you want others to have explicit reuse rights.
