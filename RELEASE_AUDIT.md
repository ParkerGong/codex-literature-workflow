# Release Audit — 1.0.0

- Audit date: 2026-07-16
- Release decision: supported core accepted
- Integration decision: live writes remain explicit, environment-dependent opt-ins

## Supported Core

The 1.0.0 release supports deterministic skill installation, metadata validation, environment reporting, controller-workspace initialization, PDF text/render probing, vendored companion installation, Zotero linked-file mapping generation and read-only verification, manifest-backed Obsidian ingest, and optional QMD update-only indexing.

The source of truth remains the local PDF, controller records, vault Markdown, `.manifest.json`, source registry, and Zotero link index. QMD is search infrastructure only.

This audit, repository READMEs, tests, evals, and CI configuration are repository evidence. The installer builds the installable skill package and intentionally excludes repository-only READMEs, this audit, tests, evals, and CI configuration.

## Release Blockers Closed

| Area | Preview problem | 1.0.0 resolution |
| --- | --- | --- |
| PDF readiness | Blank, scan-only, or even empty-password encrypted PDFs could conflict with success expectations | Empty extracted text is a failure; every encrypted PDF stops for manual handling; readiness and encryption gates have separate regression tests |
| File safety | Symlink, broken-symlink, hard-link, source/output alias, and recursive source/destination overlap cases were incomplete | Install, initialization, environment setup, probe, attachment-source, mapping, and report paths now preflight unsafe aliases or overlaps before any write |
| Zotero contract | Documentation disagreed about agent-run Desktop actions and database recovery | The user runs generated Zotero Desktop JavaScript; the agent performs read-only verification; direct `zotero.sqlite` writes are always outside scope |
| Zotero verification | Relative base-directory paths, missing pagination headers, pagination progress, parent/link mode, and conflicting content types were not fully enforced | Builder and verifier now validate these cases, stop non-progressing pagination, and fail with explicit status |
| Controller defaults | Persistent goals and Git checkpoint state could appear pending when not requested | Both are opt-in; generated records use `not-needed` or `disabled` until explicitly enabled |
| QMD | PATH/collection assumptions made refresh fragile | The contract pins the QMD Node prefix when needed, reuses collections idempotently, defaults to update-only, and prohibits embeddings without approval |
| Privacy and CI | Scan examples covered too little output; CI did not protect the maintained macOS platform or fully parse metadata | Scan scope covers intended staged text outputs; CI now validates YAML/JSON, Python, Node, environment readiness, and tests on Ubuntu and macOS |
| Documentation | One companion reference link and several support-boundary statements were inconsistent | Links and English/Chinese release contracts were aligned for 1.0.0 |

## Verification Evidence

| Gate | Result |
| --- | --- |
| Official skill validator | 3/3 skills valid: main skill and both vendored companions |
| Repository YAML validator | 3/3 skill metadata trees valid |
| Offline regression suite | 40/40 tests passed |
| Syntax and data checks | Python compile, Node syntax, eval JSON, and `git diff --check` passed |
| Isolated installation | Main skill and standalone companions installed into a temporary Codex-style tree and revalidated |
| Environment gate | Core PDF text/render path ready under Python 3.12; strict environment check passed |
| PDF integration | Two-page text extraction and selected-page rendering passed; a blank PDF correctly failed text readiness; rendered pages were visually checked |
| Fresh Obsidian invocation | One canonical source produced one manifest-backed formal note; manifest, registries, statuses, and handoff agreed |
| QMD update-only integration | Workspace-local collection indexed 7 Markdown files; BM25 returned the formal note and ingest report; 0 vectors and no embedding/query/vsearch command |
| Fresh Zotero route invocation | Mapping assertions, user-run JavaScript generation, async compilation, duplicate checks, and deterministic rebuild hash passed |
| Live Zotero read-only check | An existing linked attachment's canonical path, expected content type, and parent were verified through the Local API, with its PDF sibling count checked; no Desktop write or database mutation occurred |
| Privacy scan | No repository-local credential, private Zotero key/path, or maintainer-home-path match was found |

## Deliberate Manual Boundaries

These are not represented as automated successes:

- A real Zotero Desktop attachment write still requires the user to review and run the generated JavaScript, then return the structured result for read-only verification.
- Authenticated publisher acquisition requires the user's lawful institutional or personal access and a separate disposable test.
- A production Obsidian vault write requires an explicit allowed path and backup; release testing used an isolated temporary vault.
- QMD embeddings remain disabled unless the user explicitly approves model downloads and compute.
- Windows and WSL remain unverified; macOS is the maintained platform and Ubuntu is covered by CI.
- Optional HTTP/browser Python packages may be absent from the host runtime until the declared environment or requirements are installed; this does not affect the verified local PDF core.

## Reproduce The Automated Gates

Run these gates from the activated `codex-literature` environment created from `environment.yml`, or install the declared Python dependencies and required system PDF/OCR tools such as Poppler and Tesseract first.

```bash
python3 -m pip install -r requirements.txt -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 -m py_compile scripts/*.py
python3 -m json.tool evals/evals.json
node --check companion-skills/zotero-linked-attachments/scripts/build_zotero_linked_attachment_js.mjs
node --check companion-skills/zotero-linked-attachments/scripts/verify_zotero_linked_attachments.mjs
python3 -m unittest discover -s tests -v
python3 scripts/env_check.py --json --strict
git diff --check
```

## Acceptance Statement

Version 1.0.0 is ready as a formal release for the supported deterministic core. Conditional integrations are safe to attempt only behind their documented permission, backup, and verification gates. No evidence in this audit should be read as approval to mutate a real Zotero library or production vault without the user's explicit action.
