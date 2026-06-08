# Provenance And Companion Skills

This skill packages a workflow pattern that Codex temporarily summarized from small maintainer-side local tests. It does not vendor third-party or private skill code unless a repository maintainer explicitly adds that code with license review.

## Observed Companion Skills

These skills or plugins informed the workflow design and can be called when installed:

| Companion | Public/source status | Used for |
| --- | --- | --- |
| `skill-creator` | optional Codex/system skill; do not vendor without license review | skill structure, progressive disclosure, test planning |
| `zotero-linked-attachments` | optional local/public skill when available | Zotero linked-file attachment pattern and verification |
| `wiki-ingest` / `obsidian-wiki-ingest` | optional local/public skill when available | Obsidian-style source registry, notes, manifests, staged writes |
| `pdf` | optional Codex/local skill when available | PDF text extraction, rendering, visual QA pattern |
| `browser:control-in-app-browser` | optional OpenAI bundled Browser plugin | local/web navigation when browser connector is available |
| `chrome:control-chrome` | optional OpenAI bundled Chrome plugin | authenticated browser sessions and existing Chrome tabs |
| `computer-use:computer-use` | optional OpenAI bundled Computer Use plugin | GUI fallback for downloads or Zotero Desktop when connectors fail |
| `academic-research-suite` | default optional research workflow skill | external paper discovery, deep/systematic review planning, query expansion, source verification, citation/integrity checks |
| `research-lr-ra` | auxiliary optional research workflow skill | legacy LR assistant work, research-gap mapping, representative-work selection when ARS is unavailable or a narrow subtask fits better |
| `sciencedirect-live-session-fetcher` | optional public skill from `Given-Dream/sciencedirect-live-session-fetcher` | preferred authorized-browser backend for ScienceDirect/Elsevier, IEEE Xplore, and publisher PDF routes exposed inside a live browser session |

## Packaging Policy

- Keep this repository usable without private paths.
- Treat companion skills as optional accelerators.
- For literature discovery and search strategy, default to `academic-research-suite`; keep `research-lr-ra` as auxiliary/fallback rather than an equal default.
- For authorized publisher downloads, prefer `sciencedirect-live-session-fetcher` when installed, but keep the generic Chrome/Computer Use/manual fallback path documented for environments where it is unavailable.
- If a companion skill is unavailable, follow the generic instructions in this package.
- If vendoring code from another skill or repository, preserve its license, attribution, and upstream URL.
- For Zotero, prefer API/Desktop automation; never vendor or manipulate Zotero's private database format.

## Attribution In Open Source Releases

Release notes or project documentation should state:

```text
This skill combines controller-mediated literature workflow patterns, authorized browser-based publisher PDF acquisition, Zotero linked-file attachment practices, PDF-first selected-page reading, and Obsidian/RAG-ready note conventions. It was derived from locally tested Codex workflows and is designed to interoperate with optional sciencedirect-live-session-fetcher, Browser, Chrome, Computer Use, Zotero, PDF, and wiki-ingest skills when available.
```

Also state that the maintainer-tested path is currently limited to following a research direction, finding relevant literature, downloading open-access papers, connecting records to Zotero, and creating an Obsidian-style local knowledge base.

Before publishing, replace local filesystem origins with public repository URLs for any bundled dependency that is actually included.

## Recommended Public Attribution Fields

Before open-source release, add public URLs or package names for any companion actually bundled or documented. If a companion is only an optional Codex skill in the user's local environment, list it as "optional integration" rather than a dependency.

## Maintainer Checklist Before Release

- Remove private filesystem paths from package metadata, README-equivalent release notes, and examples.
- Keep optional integrations optional unless their code is bundled with license review.
- Link to upstream public repositories or package pages for bundled code.
- If a host-project strict profile is included, remove private project paths and replace them with generic placeholders.
- State that authorized browser access requires user permission and does not bypass paywalls.
