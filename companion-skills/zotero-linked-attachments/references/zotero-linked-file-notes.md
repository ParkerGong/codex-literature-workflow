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
- expected absolute `path`
- `parentItem` equal to the Zotero parent key

## Operational Safety

- Prefer linked files over imported copies when a project needs one canonical local file path.
- Keep source PDFs and Markdown notes inside the project or another backed-up source directory.
- Avoid direct SQLite writes while Zotero is running.
- Record attachment status in the project log or source index after verification.
