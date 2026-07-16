---
name: codex-literature-workflow
description: "Controller-led, end-to-end literature operations that coordinate source intake or discovery, lawful PDF acquisition, Zotero linked attachments, PDF-first reading, manifest-backed Obsidian notes, and optional QMD refresh with durable handoffs. Use when a request spans multiple phases, asks to build, repair, test, or audit a Zotero-Obsidian literature pipeline, migrates a local PDF library through the workflow, or needs fixed specialist sessions. Route isolated paper search, single-PDF reading, and one-off Zotero attachment to phase-specific skills."
---

# Codex Literature Workflow

Use this skill to coordinate a multi-phase literature workflow. Keep one controller responsible for scope, durable state, routing, and acceptance. Give bounded phases to fixed specialist sessions when the runtime supports them.

## Release Scope

Treat deterministic setup, environment reporting, PDF probing, controller-record initialization, companion installation, and Zotero mapping verification as the supported core. Treat live publisher access, Zotero Desktop writes, production-vault writes, and optional QMD as environment-dependent integrations that require their own readiness checks.

Use a dedicated test workspace for first runs. Back up existing controller records, Zotero libraries, and Obsidian vaults before enabling writes. Never convert an external integration failure into a false success.

## First Decision

Identify the requested shape:

| User asks for | Read |
| --- | --- |
| New project initialization, Controller Console, session topology, goal prompt | `references/initialization.md` |
| Full pipeline, agent roles, fixed sessions, goal mode | `references/architecture.md` |
| Project profile, strict Zotero/Obsidian defaults, host-project policy overrides | `references/project-profiles.md` |
| Controller kanban, durable Markdown task records, anti-drift status files | `references/controller-records.md` |
| Dependency setup, companion skill hierarchy, permanent Python environment | `references/dependencies.md` |
| Environment setup, Python, PDF text/render tooling | `references/environment.md` |
| Topic/direction discovery, local PDF library intake, web search, open/closed PDF acquisition | `references/literature-acquisition.md` |
| Zotero parent-item preparation or linked-file attachment | `references/zotero-optional.md` |
| Obsidian/RAG-ready notes, visual page checks | `references/obsidian-optional.md` |
| Obsidian Wiki / LLM Wiki manifest-backed ingest | `references/obsidian-wiki-ingest.md` |
| QMD or fallback local RAG refresh | `references/qmd-rag.md` |
| Prompts to send to sub-sessions | `references/dispatch-templates.md` |
| End-to-end flow walkthrough for audit or onboarding | `references/workflow-walkthrough.md` |
| Where this workflow borrows ideas from | `references/provenance-and-companion-skills.md` |
| Testing the skill on a small batch | `references/test-plan.md` |

If the user only wants one phase, route to the phase-specific skill and load only the relevant reference. For a full workflow, load `initialization.md`, `architecture.md`, `dependencies.md`, and `environment.md`; load Zotero, Obsidian, and QMD references only after those modules are enabled.

## Skill Routing Defaults

- For a long multi-phase workflow, explicitly name the current session as the Controller Console unless the user already designated another session. Record the controller identity before dispatch.
- Create or reuse fixed specialist sessions when multi-agent/thread tools are available. If they are unavailable, execute bounded phases sequentially and preserve the same handoff/status contract.
- Create a persistent product goal only when the user explicitly requests goal tracking. Otherwise record `long_task_goal: not-needed` and continue.
- For external paper discovery, literature review planning, query expansion, citation/integrity checks, and research-question convergence, use `academic-research-suite` as the default research companion.
- Use `research-lr-ra` only as an auxiliary or legacy literature-review assistant when ARS is unavailable, explicitly requested, or a narrow LR subtask is better served by its local workflow.
- During setup, recommend installing or enabling missing companions that match the requested workflow: install open-source companions from their GitHub repositories when available, install the vendored maintainer-built companions `research-lr-ra` and `zotero-linked-attachments` with `scripts/install_companion_skills.py`, and enable plugin-only companions such as `zotero:Zotero`, Browser/Chrome/Computer Use, and `pdf` through the Codex/plugin environment.
- Use this skill as the controller for end-to-end work that continues from discovery into screening, authorized download, local registration, Zotero linked-file attachment, PDF-first reading, and Obsidian/RAG-ready notes.
- Treat Obsidian Wiki / LLM Wiki style manifest-backed ingestion as the formal knowledge-base phase when Obsidian is enabled: one canonical source gets one formal literature note plus manifest/source-registry/Zotero-index updates.
- Treat QMD as optional search/index infrastructure, not as the source of truth. Vault Markdown, `.manifest.json`, source registry, Zotero link index, and controller records remain authoritative.
- Use Zotero, Zotero linked-file, Obsidian/wiki, Browser, Chrome, Computer Use, and `sciencedirect-live-session-fetcher` for their integration phases; do not treat them as the default paper-discovery authority.

## Non-Negotiables

- For a full multi-phase run, confirm research direction, target count, source mode, download/access permission, language, enabled modules, local inputs, allowed outputs, mappings, and checkpoint policy. Reuse answers already present in the user's request.
- For a single read-only check or one bounded phase, ask only for missing inputs, write permission, and integration permission relevant to that phase. Do not block an environment check on unrelated Zotero, Obsidian, or Git questions.
- Do not write directly to `zotero.sqlite`.
- Do not bypass paywalls, logins, CAPTCHA, or institutional access controls.
- Do not claim paper facts from model memory or web snippets.
- Do not create a fresh session per paper. Reuse fixed specialist sessions when available.
- Do not assume papers must be downloaded. If the user already has a local PDF library, register and verify those files, then continue to optional Zotero/Obsidian stages.
- Do not render whole PDFs by default. Use text-first reading and selected pages.
- Do not make QMD mandatory. If QMD is unavailable, skip the refresh, record `qmd_status`, and continue with the manifest-backed vault as the source of truth.
- Do not run `qmd embed`, `qmd query`, or `qmd vsearch` unless the user explicitly approves model downloads/embedding compute or the selected project profile says embeddings are allowed.
- Keep temporary text dumps and page images outside the project repo unless the user explicitly wants them preserved.
- Every accepted item needs provenance: query/source date, URL/DOI when available, local PDF path, Zotero key or pending status, page evidence, and unresolved TODO/RISK.
- The controller and every fixed specialist agent must write a Markdown worklog before and after meaningful work. Context recovery starts by reading these worklogs and the current handoff.
- Create local Git checkpoints only when the user or selected host profile has enabled them. When enabled, inspect explicit paths, scan for private data, commit at the configured interval, and never auto-push.
- Do not invent quota or environment status. If a host project has a quota pause rule, record `quota unknown` when unreadable and pause long work at the configured threshold.
- Do not run routine process-residue sweeps unless the host project asks for them or there are real symptoms of stuck processes.
- Do not delete temporary artifacts by default in strict projects. Prefer a recorded soft move to a configured temp trash folder.

## Options

Before dispatching, set these options explicitly in the controller note:

| Option | Values | Default |
| --- | --- | --- |
| `project_profile` | `generic`, `dissertation-strict`, custom profile name | `generic` |
| `controller_console` | current session ID or `pending` | current session for long workflows unless another is designated |
| `long_task_goal` | active goal text or `not-needed` | `not-needed` unless explicitly requested |
| `user_scope_confirmed` | `true`, `false` | `false` until required startup questions are answered |
| `git_checkpoint_required` | `true`, `false` | `false` for `generic`; ask or follow an enabled strict profile |
| `git_checkpoint_interval` | integer meaningful file-writing steps or accepted handoffs | `3` |
| `git_push_policy` | `manual-only`, `disabled`, `explicit-user-request` | `manual-only`; never push automatically |
| `target_direction` | user-provided direction, local-doc direction, or pending | ask before work |
| `target_count` | integer or `scope-map-only` | ask before work |
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
| `qmd_enabled` | `true`, `false`, `auto` | `false` unless local vault indexing is requested or an existing host profile sets `auto` |
| `qmd_collection` | collection name or `pending` | ask or infer from project/vault slug |
| `qmd_embed_allowed` | `true`, `false` | `false` unless explicitly approved |
| `visual_check` | `off`, `selected-pages`, `vision-model` | `selected-pages` for figure/table/curve-heavy papers |
| `batch_size` | integer | `3-5` short papers, `1-2` theses or long reports |
| `access_mode` | `open-only`, `authorized-browser`, `manual-user` | `open-only` unless the user authorizes browser/session access |
| `authorized_download_backend` | `sciencedirect-live-session-fetcher`, `chrome-control`, `computer-use`, `manual` | `sciencedirect-live-session-fetcher` when installed and `access_mode=authorized-browser` |
| `python_environment` | named permanent env path or `pending` | `codex-literature` permanent non-venv environment |

Read `references/project-profiles.md` before using a non-generic profile. A strict host profile may add required records and gates, while Zotero and Obsidian can still remain user-selected modules.

## Phase Map

1. **Controller gate**: designate the Controller Console for long multi-phase work; record a goal only when the user requested one; create or reuse fixed specialist sessions when supported.
2. **User scope intake gate**: for full runs, record direction, target count, source mode, download/access permission, language, enabled modules, local inputs, output paths, mappings, and checkpoint policy. For a bounded phase, collect only relevant missing fields.
3. **Profile and scope gate**: create or reuse a controller task ID; choose `project_profile`; define topic/direction, source input mode, whether downloads are enabled, language, inclusion/exclusion rules, optional or required Zotero/Obsidian outputs, allowed writes, forbidden paths, quota/process/temp policies, and acceptance criteria.
4. **Controller and agent records**: initialize or update Markdown state files before any long work: controller worklog, per-agent worklogs, kanban, session registry, dispatch log, dependency setup, source manifest, download log, ingest queue/status, and per-task handoff.
5. **Optional Git checkpoint gate**: when checkpointing is enabled, read `references/controller-records.md`, verify the Git root, scan explicit intended files for private data, and commit at the configured interval. Never auto-push. Otherwise record `git checkpoint: disabled` and continue.
6. **Dependency and environment check**: read `references/dependencies.md`; recommend installing or enabling missing companion skills/plugins that match the requested workflow; use GitHub install paths for public companions and `scripts/install_companion_skills.py` for vendored maintainer-built companions; recommend the permanent `codex-literature` environment from `environment.yml`; run `scripts/env_check.py --json --strict`; record companion-skill and Python/CLI readiness before long batches.
7. **Source intake**: if `source_input_mode=local-library`, register existing PDFs and skip download; if `mixed`, register local PDFs first, then search only for gaps.
8. **Search and screening when needed**: use `academic-research-suite` by default for literature discovery, query expansion, and screening strategy; use `research-lr-ra` only as an auxiliary/fallback; produce a dated candidate table with query strings, sources, URLs/DOIs, access route, relevance score, and exclusion reasons.
9. **Optional acquisition and local registration**: only when `download_enabled=true`, download legal/authorized PDFs. For authenticated publisher pages, prefer `sciencedirect-live-session-fetcher` with one live authorized browser session before generic Chrome/Computer Use fallback; verify title/body/pages; write a manifest row and mark bad PDFs honestly.
10. **Optional Zotero**: locate parent items through read-only tooling, generate validated linked-file JavaScript, ask the user to run it in Zotero Desktop, and verify via the local API or returned structured result.
11. **PDF-first reading**: extract text; classify reading level; render only selected claim-bearing pages; record visual evidence or TODO.
12. **Obsidian Wiki Ingest And Manifest Backfill**: when Obsidian/RAG is enabled, write or update the manifest-backed vault contract: `.manifest.json`, `index.md`, `hot.md`, `log.md`, `01_sources/source_registry.md`, `01_sources/zotero_link_index.md`, one formal note per canonical source under `02_literature_notes/`, optional concept/claim pages, and a batch report. Duplicate aliases are report/manifest entries, not independent formal notes. Wrong or incomplete PDFs become `manual-check`.
13. **QMD / Local RAG Refresh**: if QMD is configured, run update-only refresh and verify status/search. If QMD is missing or collection settings are unavailable, skip and report. Use project-local lexical/sparse fallback only as fallback retrieval, not dense semantic RAG. Run `qmd embed` only with explicit approval.
14. **Controller acceptance**: check files, provenance, duplicate handling, temp cleanup, status consistency, QMD/fallback status, and Git checkpoint state when enabled; only the controller marks output accepted.

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
- Git checkpoint:
- Evidence basis:
- TODO:
- RISK:
- Suggested next owner:
```

## Stop Conditions

Stop and ask the controller or user when:

- no Controller Console has been recorded for long multi-phase work;
- a required specialist phase has no executable route and sequential fallback is unsafe;
- fields required for the requested phases are unanswered or `user_scope_confirmed=false` for a full run;
- `git_checkpoint_required=true` but the target project root is not a Git repository, safe files to commit are unclear, or the privacy scan finds secrets/private local paths that cannot be excluded;
- no legal/authorized PDF is available;
- the PDF is wrong, incomplete, encrypted, scan-only without OCR, or mostly unreadable;
- browser access requires login, CAPTCHA, payment, or institutional consent not yet granted; for IEEE/ScienceDirect-style authorized routes, first verify whether the live browser already shows institutional access and a PDF button before treating personal sign-in as required;
- the host project's reliable quota reading is at or below its pause threshold;
- Zotero is unavailable and the task requires verified attachments;
- visual interpretation is required but page rendering/vision is unavailable;
- the task would write outside the allowed paths;
- fixed specialist session ownership is unclear.
