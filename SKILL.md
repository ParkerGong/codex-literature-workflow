---
name: codex-obsidian-read
description: "End-to-end literature workflow for Codex: turn a topic, direction, or existing local PDF library into screened sources, optional legal/authorized PDF acquisition, optional Zotero linked-file attachment, PDF-first reading with optional visual page checks, and optional Obsidian/RAG-ready notes. Use this skill whenever the user asks to find, download, organize, read, summarize, attach to Zotero, or convert papers into an Obsidian knowledge base, especially when multiple fixed Codex sessions should cooperate under a controller."
---

# Codex Obsidian Read

Use this skill to coordinate a literature workflow without turning one agent into an uncontrolled mega-agent. A controller owns scope, fixed-session routing, status, and acceptance. Specialist sessions do the phase work.

## First Decision

Identify the requested shape:

| User asks for | Read |
| --- | --- |
| Full pipeline, agent roles, fixed sessions, goal mode | `references/architecture.md` |
| Project profile, strict Zotero/Obsidian defaults, host-project policy overrides | `references/project-profiles.md` |
| Controller kanban, durable Markdown task records, anti-drift status files | `references/controller-records.md` |
| Dependency setup, companion skill hierarchy, permanent Python environment | `references/dependencies.md` |
| Environment setup, Python, PDF text/render tooling | `references/environment.md` |
| Topic/direction discovery, local PDF library intake, web search, open/closed PDF acquisition | `references/literature-acquisition.md` |
| Zotero import or linked-file attachment | `references/zotero-optional.md` |
| Obsidian/RAG-ready notes, visual page checks | `references/obsidian-optional.md` |
| Prompts to send to sub-sessions | `references/dispatch-templates.md` |
| End-to-end flow walkthrough for audit or onboarding | `references/workflow-walkthrough.md` |
| Where this workflow borrows ideas from | `references/provenance-and-companion-skills.md` |
| Testing the skill on a small batch | `references/test-plan.md` |

If the user only wants one phase, load only the relevant reference. If the user wants the full workflow, load `architecture.md`, `dependencies.md`, `environment.md`, and the relevant optional references.

## Skill Routing Defaults

- For external paper discovery, literature review planning, query expansion, citation/integrity checks, and research-question convergence, use `academic-research-suite` as the default research companion.
- Use `research-lr-ra` only as an auxiliary or legacy literature-review assistant when ARS is unavailable, explicitly requested, or a narrow LR subtask is better served by its local workflow.
- Use this skill as the controller for end-to-end work that continues from discovery into screening, authorized download, local registration, Zotero linked-file attachment, PDF-first reading, and Obsidian/RAG-ready notes.
- Use Zotero, Zotero linked-file, Obsidian/wiki, Browser, Chrome, Computer Use, and `sciencedirect-live-session-fetcher` for their integration phases; do not treat them as the default paper-discovery authority.

## Non-Negotiables

- Do not write directly to `zotero.sqlite`.
- Do not bypass paywalls, logins, CAPTCHA, or institutional access controls.
- Do not claim paper facts from model memory or web snippets.
- Do not create a fresh session per paper. Reuse fixed specialist sessions when available.
- Do not assume papers must be downloaded. If the user already has a local PDF library, register and verify those files, then continue to optional Zotero/Obsidian stages.
- Do not render whole PDFs by default. Use text-first reading and selected pages.
- Keep temporary text dumps and page images outside the project repo unless the user explicitly wants them preserved.
- Every accepted item needs provenance: query/source date, URL/DOI when available, local PDF path, Zotero key or pending status, page evidence, and unresolved TODO/RISK.
- The controller and every fixed specialist agent must write a Markdown worklog before and after meaningful work. Context recovery starts by reading these worklogs and the current handoff.
- Do not invent quota or environment status. If a host project has a quota pause rule, record `quota unknown` when unreadable and pause long work at the configured threshold.
- Do not run routine process-residue sweeps unless the host project asks for them or there are real symptoms of stuck processes.
- Do not delete temporary artifacts by default in strict projects. Prefer a recorded soft move to a configured temp trash folder.

## Options

Before dispatching, set these options explicitly in the controller note:

| Option | Values | Default |
| --- | --- | --- |
| `project_profile` | `generic`, `dissertation-strict`, custom profile name | `generic` |
| `direction_source` | `local-docs`, `user-prompt`, `agent-generated` | ask at start for full/strict runs |
| `collection_mapping_source` | `local-docs`, `user-prompt`, `agent-proposed`, `none` | ask at start when Zotero/Obsidian grouping matters |
| `research_companion_default` | `academic-research-suite` | `academic-research-suite` |
| `research_companion_auxiliary` | `research-lr-ra`, `none` | `research-lr-ra` |
| `source_input_mode` | `local-library`, `search-and-download`, `mixed` | ask at start |
| `download_enabled` | `true`, `false` | `false` for `local-library`, ask otherwise |
| `local_library_paths` | paths or manifest | required for `local-library` or `mixed` |
| `language_scope` | `english`, `chinese`, `both` | user request, otherwise `both` |
| `zotero_enabled` | `true`, `false` | ask at start for full/strict runs; otherwise `false` unless requested |
| `obsidian_enabled` | `true`, `false` | `false` unless a knowledge base is requested |
| `visual_check` | `off`, `selected-pages`, `vision-model` | `selected-pages` for figure/table/curve-heavy papers |
| `batch_size` | integer | `3-5` short papers, `1-2` theses or long reports |
| `access_mode` | `open-only`, `authorized-browser`, `manual-user` | `open-only` unless the user authorizes browser/session access |
| `authorized_download_backend` | `sciencedirect-live-session-fetcher`, `chrome-control`, `computer-use`, `manual` | `sciencedirect-live-session-fetcher` when installed and `access_mode=authorized-browser` |
| `python_environment` | named permanent env path or `pending` | `codex-lit` permanent non-venv environment |

Read `references/project-profiles.md` before using a non-generic profile. A strict host profile may add required records and gates, while Zotero and Obsidian can still remain user-selected modules.

## Phase Map

1. **Profile and scope gate**: create or reuse a controller task ID; choose `project_profile`; define topic/direction, source input mode, whether downloads are enabled, language, inclusion/exclusion rules, optional or required Zotero/Obsidian outputs, allowed writes, forbidden paths, quota/process/temp policies, and acceptance criteria.
2. **Controller and agent records**: initialize or update Markdown state files before any long work: controller worklog, per-agent worklogs, kanban, session registry, dispatch log, dependency setup, source manifest, download log, ingest queue/status, and per-task handoff.
3. **Dependency and environment check**: read `references/dependencies.md`; recommend the permanent `codex-lit` environment from `environment.yml`; run `scripts/env_check.py`; record companion-skill and Python/CLI readiness before long batches.
4. **Source intake**: if `source_input_mode=local-library`, register existing PDFs and skip download; if `mixed`, register local PDFs first, then search only for gaps.
5. **Search and screening when needed**: use `academic-research-suite` by default for literature discovery, query expansion, and screening strategy; use `research-lr-ra` only as an auxiliary/fallback; produce a dated candidate table with query strings, sources, URLs/DOIs, access route, relevance score, and exclusion reasons.
6. **Optional acquisition and local registration**: only when `download_enabled=true`, download legal/authorized PDFs. For authenticated publisher pages, prefer `sciencedirect-live-session-fetcher` with one live authorized browser session before generic Chrome/Computer Use fallback; verify title/body/pages; write a manifest row and mark bad PDFs honestly.
7. **Optional Zotero**: create or locate parent items, attach PDFs/MD notes as linked files, and verify via API or logged Zotero Desktop Run JavaScript results.
8. **PDF-first reading**: extract text; classify reading level; render only selected claim-bearing pages; record visual evidence or TODO.
9. **Optional Obsidian/RAG ingest**: create source records, literature notes, concept/claim updates if directly supported, and a batch report.
10. **Controller acceptance**: check files, provenance, duplicate handling, temp cleanup, and status consistency; only the controller marks output accepted.

## Required Handoff Shape

Every phase must leave a durable handoff:

```markdown
## Handoff

- Task ID:
- Status: Working | Waiting review | Blocked | Done
- Owner this round:
- Worklog updated:
- Files read:
- Files written:
- Sources processed:
- Zotero status:
- Obsidian/RAG status:
- Evidence basis:
- TODO:
- RISK:
- Suggested next owner:
```

## Stop Conditions

Stop and ask the controller or user when:

- no legal/authorized PDF is available;
- the PDF is wrong, incomplete, encrypted, scan-only without OCR, or mostly unreadable;
- browser access requires login, CAPTCHA, payment, or institutional consent not yet granted; for IEEE/ScienceDirect-style authorized routes, first verify whether the live browser already shows institutional access and a PDF button before treating personal sign-in as required;
- the host project's reliable quota reading is at or below its pause threshold;
- Zotero is unavailable and the task requires verified attachments;
- visual interpretation is required but page rendering/vision is unavailable;
- the task would write outside the allowed paths;
- fixed specialist session ownership is unclear.
