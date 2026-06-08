# Literature Source Intake, Search, And Optional Acquisition

This phase turns a topic, direction, existing PDF library, or mixed source set into registered local sources. Download is optional. If the user already has local PDFs, register and verify the library first, then continue to Zotero/Obsidian stages without searching or downloading unless the controller asks for gap filling.

## Direction Intake

The controller should ask or infer:

- topic/direction and research boundary;
- language scope: English, Chinese, or both;
- publication types: papers, surveys, theses, standards, reports;
- time window and venues/databases;
- must-have and exclusion keywords;
- desired batch size;
- source input mode: local library, search/download, or mixed;
- local PDF folder or manifest path when available;
- whether new downloads are enabled;
- whether Zotero/Obsidian outputs are enabled.

If the user gives a broad direction, LiteratureAgent first writes a direction map before downloading.

## Source Input Modes

The controller chooses one source input mode before dispatch:

| Mode | Use when | Download behavior |
| --- | --- | --- |
| `local-library` | user already has PDFs, a literature folder, or a manifest | `download_enabled=false`; register and verify local files only |
| `search-and-download` | user wants new literature discovery and PDF acquisition | `download_enabled=true` only after access rules are set |
| `mixed` | user has some PDFs but wants gap filling | register local files first, then search/download only missing items |

For `local-library`, LiteratureAgent does not search the web unless the controller explicitly asks for metadata repair or gap filling.

## Local Library Intake

Use this path when the user provides existing PDFs or a local source manifest.

Required inputs:

- local folder(s), file list, or manifest path;
- optional existing metadata: BibTeX/RIS/CSV/Zotero export/source registry;
- target direction or inclusion rule;
- allowed write paths for source manifest, quality report, and worklog.

Runbook:

1. Enumerate only approved local PDF paths.
2. Reserve stable `source_id` values.
3. Probe each PDF for file size, page count, title/author hints, text layer, and encryption/scanned status.
4. Use existing metadata files when available; do not invent missing DOI/title/author fields.
5. Detect duplicates by DOI, title, file hash if available, Zotero key, and obvious filename aliases.
6. Write `source_manifest.md` rows with `access_route=local-library` and status `local-existing`, `scan-or-ocr-needed`, `bad-pdf`, or `manual-check`.
7. Leave `download_log.md` empty or write `download-skipped` rows that point to the original local path, depending on the host project's convention.
8. Stop at `Waiting review` before Zotero or Obsidian work.

Suggested local library manifest fields:

| Field | Meaning |
| --- | --- |
| `source_id` | stable local ID |
| `local_pdf` | existing PDF path |
| `original_filename` | filename before any canonical copy/rename |
| `metadata_source` | PDF metadata, BibTeX/RIS/CSV/Zotero export, filename, manual |
| `doi_url` | DOI/URL if known |
| `title_status` | verified, inferred, missing, conflict |
| `text_status` | text-ok, scan-or-ocr-needed, encrypted, bad-pdf |
| `duplicate_of` | canonical `source_id` if this is an alias/duplicate |
| `intake_status` | local-existing, manual-check, bad-pdf |

Do not rename, move, or overwrite the user's original PDFs unless the controller explicitly allows canonical copying.

## Screening Skill Choice

When available, use a literature-review skill for search and screening rather than improvising:

- Use `academic-research-suite` for deep research, systematic literature review planning, query expansion, and evidence-maturity decisions.
- Use `research-lr-ra` for literature review assistant work, search strategy, research-gap mapping, and representative-work selection.
- Use browser/chrome/computer-use only for source discovery and authorized download mechanics; do not let browser snippets become paper facts.

If no companion skill is available, LiteratureAgent still follows the screening rubric below.

## Controller Record Integration

LiteratureAgent writes progress to durable records after each small batch:

| Moment | Record update |
| --- | --- |
| direction clarified | kanban row moves to search/screening; direction map path recorded |
| local PDFs registered | source manifest status becomes `local-existing` or an honest problem status |
| download disabled | kanban/handoff records `download-skipped` and why |
| candidates found | candidate table saved; source IDs reserved |
| candidates rejected | exclusion reasons written, not just omitted |
| PDF selected for acquisition | source manifest status becomes `selected` |
| PDF accepted | source manifest status becomes `downloaded`; download log quality is `ok` |
| PDF bad or unavailable | status becomes `manual-check`, `wrong-pdf`, `scan-or-ocr-needed`, or `unavailable` |
| batch complete | handoff status is `Waiting review` |

Do not dispatch ZoteroAgent from memory. The controller should pass rows from the source manifest and download log.

## Screening Rubric

Score candidates before downloading. Keep the score in the candidate table so the controller can audit why a paper entered the batch.

| Criterion | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Topical fit | unrelated | adjacent background | directly answers direction |
| Source authority | unknown/weak | workshop/preprint or secondary | peer-reviewed/standard/thesis/publisher record |
| Method relevance | no method overlap | partial method overlap | central method or benchmark |
| Scenario relevance | generic | adjacent domain | target domain or strong transfer bridge |
| Evidence value | low citation/unclear | useful background | core/high-impact/representative |
| Access feasibility | unavailable | manual/auth required | open or already authorized |

Recommended interpretation:

- `9-12`: select unless duplicate or out of scope;
- `6-8`: keep as candidate or background;
- `<6`: reject or defer.

Always add an exclusion reason for rejected candidates.

## Candidate Table

Every search batch should produce:

| Field | Meaning |
| --- | --- |
| `source_id` | stable project-local ID |
| `title` | title from authoritative source |
| `authors_year` | authors and year |
| `venue` | journal/conference/thesis source |
| `doi_url` | DOI, publisher URL, arXiv/CNKI/Wanfang/etc. |
| `source_input_mode` | local-library, search-and-download, or mixed |
| `query` | query string and database/site |
| `access_route` | open, publisher, institutional, manual, unavailable |
| `relevance` | why selected |
| `status` | candidate, selected, downloaded, manual-check, rejected |
| `notes` | metadata uncertainty, duplicate, risk |
| `screening_score` | rubric total and short rationale |

Record search date and source site. Do not use snippets as paper facts.

## Access Routes

| Route | Examples | Rule |
| --- | --- | --- |
| `local-library` | user-provided PDF folder, file list, or manifest | no download; register and verify existing local files |
| `open-direct` | arXiv, open journal PDF, institutional repository | direct download is acceptable; record URL and date |
| `publisher-open` | MDPI, Frontiers, Springer Open, PLOS | use publisher PDF; verify body and title |
| `authorized-browser` | IEEE, ScienceDirect, SAGE, CNKI, Wanfang, VIP/CQVIP through user/institution | use the user's authenticated browser session only with permission |
| `cnki-authorized` | CNKI through institution or user account | record CNKI metadata and stop at login/CAPTCHA/payment |
| `wanfang-authorized` | Wanfang through institution or user account | record Wanfang metadata and stop at login/CAPTCHA/payment |
| `vip-authorized` | VIP/CQVIP through institution or user account | record VIP metadata and stop at login/CAPTCHA/payment |
| `manual-user` | CAPTCHA, payment, login, library proxy, uncertain license | stop and give user exact next action |
| `unavailable` | no legal route found | mark manual-check; do not fabricate |

## Preferred Authorized Download Backend

When `download_enabled=true`, `access_mode=authorized-browser`, and `sciencedirect-live-session-fetcher` is installed, use it as the first-choice backend for authenticated publisher downloads.

Use it for:

- ScienceDirect/Elsevier pages with signed PDF URLs;
- IEEE Xplore article pages such as `https://ieeexplore.ieee.org/document/<arnumber>`;
- DOI or publisher landing pages that expose a normal PDF route inside an authorized Chrome/Edge/Firefox session.

Preferred run pattern:

1. Prepare a CSV with `number`, `doi`, `title`, and `note`. Put the publisher article URL in `note` when available.
2. For IEEE, include the real IEEE DOI when known, for example `10.1109/...`, so the fetcher triggers its IEEE route. Use the article detail URL, not only a `stamp.jsp` URL.
3. Launch or attach to one live browser session with DevTools enabled.
4. Confirm the same browser session has lawful access. For IEEE, if the page shows `Access provided by: <institution>` and the red `PDF` button is visible, treat institutional access as active; do not click `Personal Sign In`.
5. Run the fetcher serially with conservative sleeps and a small batch.
6. Accept only files whose bytes start as a real PDF and pass the PDF acceptance checks below.

Same-session rule:

- The DevTools browser used by `sciencedirect-live-session-fetcher` must be the same session/profile/window where access is active.
- Do not mix a foreground user Chrome tab that has institutional access with a separate temporary DevTools Chrome profile that does not.
- If a probe says "challenge" but the visible publisher page shows institutional access and an exposed PDF button, prefer the visible page evidence and rerun with the correct same-session browser before asking for personal sign-in.

Recommended command shape when the companion skill is installed:

```bash
bash ~/.codex/skills/sciencedirect-live-session-fetcher/scripts/run_devtools_sciencedirect_fetch_macos.sh \
  --input-csv <input.csv> \
  --out-dir <download-run-dir> \
  --python-exe <venv-python> \
  --debug-port <port> \
  --page-wait-seconds 8 \
  --inter-item-sleep-seconds 6 \
  --limit <small-batch-size>
```

Record `authorized_download_backend=sciencedirect-live-session-fetcher`, the DevTools port or browser route, the visible access signal, the source URL, and the fetcher output files (`devtools_results.csv`, `summary.txt`, and accepted PDF path).

## Browser And Computer Use

Prefer programmatic direct download only for open URLs. For closed or authenticated resources:

1. Ask/confirm that authorized browser access may be used.
2. Prefer `sciencedirect-live-session-fetcher` for ScienceDirect/Elsevier, IEEE Xplore, and other publisher pages where a live authorized browser session exposes the PDF route.
3. If the fetcher is unavailable or cannot attach to the correct authorized browser session, use Codex Chrome control for the user's existing authenticated Chrome profile.
4. If Chrome control cannot complete the UI flow, record the blocker and make at most one Computer Use fallback attempt on the existing user-authenticated browser.
5. Handle one paywalled/manual item at a time.
6. If human verification, CAPTCHA, payment, login, or license uncertainty remains after the single fallback attempt, stop and mark `manual-user` or `captcha-blocked`.
7. After download, copy or move only the downloaded PDF into the approved local literature folder.

Do not bypass access controls. This skill manages authorized access; it is not a paywall circumvention workflow.

## Closed-Source Download Fallback Ladder

Use this ladder only when `download_enabled=true` and the controller has authorized browser/session access.

| Step | Tool/route | Rule | Failure status |
| --- | --- | --- | --- |
| 1 | open URL/direct publisher PDF | only for legal/open URLs | `unavailable` or next step |
| 2 | `sciencedirect-live-session-fetcher` | preferred for authorized ScienceDirect/Elsevier, IEEE Xplore, and publisher PDF routes; use the same live authorized DevTools browser session | `fetcher-session-mismatch`, `fetcher-blocked`, or next step |
| 3 | Codex Chrome control | use the user's existing Chrome login/session/profile when the fetcher is unavailable or attached to the wrong session | `chrome-blocked` or next step |
| 4 | Computer Use, one attempt | operate the visible local browser UI once for a stuck click/download/verification screen | `captcha-blocked`, `manual-user`, or `downloaded` |
| 5 | manual user | user completes login/CAPTCHA/payment/library action | `manual-check` until user returns |

Computer Use fallback rules:

- Use at most one fallback attempt per source unless the controller explicitly approves another.
- Do not solve or bypass CAPTCHA; if verification requires proving humanity or private credentials, stop and ask the user.
- Do not store screenshots, cookies, credentials, or private account details.
- Record `fallback_attempted=computer-use-once`, outcome, blocker, and next manual action.
- If the fallback succeeds, still run PDF acceptance checks before marking `downloaded`.

IEEE institutional-access rule:

- If IEEE Xplore shows `Access provided by: <institution>` and the article detail page has a visible red `PDF` button, click/use that PDF route directly.
- Do not click `Personal Sign In` unless the user explicitly wants IEEE personal-account login or the institutional route is absent.
- Prefer article URLs like `https://ieeexplore.ieee.org/document/<arnumber>` in the CSV `note`; let the fetcher normalize `stamp.jsp`/`stampPDF` details from the article page.

For institutional or user-authenticated downloads, record enough for reproducibility without exposing private credentials:

- access route, such as `authorized-browser`;
- landing URL and accepted PDF URL when visible;
- date accessed;
- browser/tool used;
- manual blocker, if any;
- final local PDF path and quality status.

## Download Runbook

For each selected source:

1. Try DOI/publisher landing page and open PDF links.
2. Try open repositories only when legally appropriate: arXiv, institutional repository, PubMed Central, publisher open access, conference proceedings.
3. For Chinese sources, record whether the route is journal site, CNKI, Wanfang, VIP/CQVIP, university repository, or manual user download.
4. For closed sources, switch `access_route` to `authorized-browser` and process one item at a time.
5. After download, rename or copy to the canonical local path chosen by the controller.
6. Run PDF acceptance checks before updating the manifest.
7. Record attempted URLs, used URL, access date, bytes, page count, and verification result in `download_log.md` or a JSON manifest.

Suggested download log row:

| Field | Meaning |
| --- | --- |
| `source_id` | stable local ID |
| `attempted_urls` | all attempted PDF/landing URLs |
| `used_url` | URL that produced the accepted PDF |
| `access_date` | date of access |
| `access_route` | local-library, open-direct, publisher-open, authorized-browser, cnki-authorized, wanfang-authorized, vip-authorized, manual-user, unavailable |
| `fallback_attempted` | none, chrome, computer-use-once |
| `fallback_outcome` | downloaded, captcha-blocked, login-blocked, payment-blocked, manual-user, unavailable |
| `local_pdf` | accepted local path |
| `bytes` | file size |
| `page_count` | page count |
| `quality_status` | ok, wrong-pdf, incomplete-pdf, scan-or-ocr-needed, manual-check |
| `message` | human explanation |

## Chinese Database Route Details

Chinese literature often needs more precise route records than a generic publisher URL. Use these fields in the candidate table, download log, or an adjacent JSON record when relevant.

| Field | Meaning |
| --- | --- |
| `cn_database` | `CNKI`, `Wanfang`, `VIP/CQVIP`, journal site, university repository, or other |
| `cn_record_url` | stable record/detail page URL when available |
| `cn_download_url_visible` | visible PDF/download URL if exposed; leave blank if hidden behind UI |
| `cn_access_route` | `cnki-authorized`, `wanfang-authorized`, `vip-authorized`, `open-direct`, `manual-user`, or `unavailable` |
| `institution_route` | institution/proxy/library route, without credentials |
| `title_zh` | Chinese title from database record |
| `title_en` | English title if present |
| `authors_zh` | Chinese author names if present |
| `journal_zh` | Chinese journal/source name |
| `year_issue_pages` | year, issue, pages, or thesis metadata |
| `doi_or_cn_id` | DOI, CNKI file name/id, Wanfang id, VIP id, or other database identifier |
| `download_method` | direct PDF, browser click, manual user, unavailable |
| `manual_blocker` | login, CAPTCHA, payment, institutional permission, no PDF, metadata-only |
| `pdf_quality_status` | ok, wrong-pdf, incomplete-pdf, scan-or-ocr-needed, manual-check |

Database-specific notes:

- CNKI: record whether the source is journal, thesis, conference, standard, or newspaper; CNKI download buttons and file IDs may differ by material type.
- Wanfang: record Wanfang item id or detail URL when visible; verify that the PDF title matches the Wanfang metadata.
- VIP/CQVIP: record the detail page and journal metadata; many pages require browser/manual access even when metadata is visible.
- Journal or university repositories: prefer legal open PDF links when they clearly belong to the journal/institution.
- Do not store credentials, cookies, screenshots with private account data, or library proxy tokens in logs.

## PDF Acceptance Checks

Before marking `downloaded`, verify:

- file exists and size is plausible;
- page count is plausible;
- title and author line match the candidate;
- body text exists;
- PDF is not only front matter, table of contents, or a landing-page print;
- language and publication metadata match expectations.

If a file fails checks, keep it only if useful for audit and mark:

- `wrong-pdf`;
- `incomplete-pdf`;
- `scan-or-ocr-needed`;
- `manual-check`.

Never overwrite a bad PDF with a corrected one without explicit controller approval. Prefer adding a corrected candidate path and preserving the old file as an alias or bad source.
