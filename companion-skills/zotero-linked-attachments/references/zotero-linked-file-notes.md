# Zotero Linked File Notes

## Preferred Attachment API

Use Zotero Desktop internal JavaScript for creating local linked-file attachments:

```javascript
const attachment = await Zotero.Attachments.linkFromFile({
  file: "/absolute/path/to/file.pdf",
  parentItemID: parent.id,
  contentType: "application/pdf",
});
```

This works for PDFs, Markdown notes, text files, and other local source files when Zotero can access the path.

## Why Not The Local HTTP API For Writes

The Zotero local API at `http://127.0.0.1:23119/api/users/0` is useful for reading items and child attachments. In tested desktop setups, `POST /api/users/0/items` may return `Endpoint does not support method`, so do not rely on it for creating attachments.

## Safe Verification

Verify through child items:

```text
GET http://127.0.0.1:23119/api/users/0/items/<PARENT_KEY>/children
```

The expected child attachment should include:

- `itemType: attachment`
- `linkMode: linked_file`
- expected `contentType`
- a resolvable linked-file path
- `parentItem` equal to the Zotero parent key

Do not compare the raw child `path` field to an absolute path. With Zotero's Linked Attachment Base Directory enabled, the API can return `attachments:<relative-path>`. Resolve the attachment by requesting:

```text
GET http://127.0.0.1:23119/api/users/0/items/<ATTACHMENT_KEY>/file/view/url
```

Require a `file:` URL, convert it to a local path, canonicalize it, and compare that result with the canonical expected mapping path. Paginate child lists in batches of 100; when `Total-Results` is absent, continue until a short or empty page.

## Operational Safety

- Prefer linked files over imported copies when a project needs one canonical local file path.
- Keep source PDFs and Markdown notes inside the project or another backed-up source directory.
- Never write Zotero SQLite directly; database-level recovery is outside this skill.
- Ask the user to launch and operate Zotero Desktop. An unavailable local API is a live-integration blocker, not permission for the agent to open the app or mutate the library.
- Record attachment status in the project log or source index after verification.
