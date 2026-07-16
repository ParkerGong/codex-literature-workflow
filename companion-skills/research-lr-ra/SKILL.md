---
name: research-lr-ra
description: Literature review research assistant workflow for Codex. Use when the user asks Codex to do LR, literature review, literature mapping, paper discovery, research gap finding, Zotero-backed reading, Google Scholar/gs skill searching, Chrome MCP browsing, user-mediated Zotero intake, OneFind local-library synthesis, or to turn a topic, research question, course assignment, advisor suggestion, or rough idea into a structured review plan and reading map.
---

# Research LR RA

## Core Principle

Connect the whole literature-review chain: search, save, read, organize, and synthesize. Do not treat search results as the final answer. Aim to turn a rough topic into a managed local literature base plus a research map the user can act on.

## Workflow

1. Clarify the topic lightly.
   - Accept rough inputs such as an advisor's phrase, assignment prompt, early research interest, or formal research question.
   - Identify likely disciplines, keywords, synonyms, core constructs, methods, populations, and time range.
   - Avoid over-asking. If the user has not specified scope, choose a reasonable initial scope and state it.

2. Search the literature.
   - Prefer the user's available scholar-search tools, especially gs skill with Chrome MCP for Google Scholar.
   - Search for seminal papers, recent papers, review papers, high-citation papers, methods papers, and papers frequently co-cited with core works.
   - Iterate keywords across theory terms, empirical setting terms, method terms, and adjacent literatures.
   - Track search terms and why each query was used.

3. Prepare promising papers for saving.
   - Use Zotero MCP or the local API only for read-only lookup, export, and verification. Prepare DOI/BibTeX/RIS or an import queue and ask the user to perform Zotero imports or Desktop writes.
   - Preserve metadata: title, authors, year, venue, DOI/URL, abstract, tags, and notes when available.
   - Prefer a durable pending-import record before deep synthesis so the user does not lose useful findings.

4. Read and synthesize the local library.
   - Use OneFind or equivalent local-library search once papers are in Zotero.
   - Treat Zotero as the user's research knowledge base, not just citation storage.
   - Compare papers by question, theory/mechanism, data, method, identification, findings, limitations, and relation to the user's topic.

5. Produce actionable LR outputs.
   - Literature map: 3-6 main streams with concise descriptions.
   - Priority reading list: which papers to read first and why.
   - Classification table: seminal/recent/review/theory/method/empirical/mechanism papers.
   - Research gap memo: crowded areas, open spaces, plausible contribution angles.
   - Next-search plan: missing keywords, venues, authors, datasets, or adjacent fields to search next.

## Quality Checks

- Distinguish what was found in sources from inference.
- Do not overstate novelty from a shallow search.
- Prefer papers with stable bibliographic metadata over vague web snippets.
- Flag access gaps, missing PDFs, uncertain metadata, and likely duplicate records.
- Do not launch, control, or write through Zotero Desktop; keep every Zotero mutation user-mediated.
- When tools are unavailable, still run the same conceptual workflow manually and clearly say which tool-backed steps could not be executed.

## Output Shape

For exploratory LR, default to:

```text
Topic scope
Search strategy
Core papers
Literature streams
Priority reading order
Potential gaps
Next actions
```

For a more mature project, default to:

```text
Research question
Position in literature
Mechanisms and methods
What is already crowded
What remains open
Candidate contribution
Reading and evidence plan
```
