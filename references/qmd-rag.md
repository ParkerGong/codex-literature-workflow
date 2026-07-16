# QMD / Local RAG Refresh

Use this reference after Obsidian Wiki / LLM Wiki style vault writes when the user or project profile wants a local search/index refresh.

QMD is optional search/index infrastructure. It is not the source of truth. Vault Markdown, `.manifest.json`, source registry, Zotero link index, and controller records remain authoritative.

## Contents

- Idempotent setup and refresh
- Embedding approval boundary
- Status labels and fallback retrieval
- Node/ABI troubleshooting

## Optional QMD Setup

Tested package and command shape:

```bash
npm install -g @tobilu/qmd
qmd --version
qmd init
qmd collection list
qmd collection add <VAULT_PATH> --name <COLLECTION_NAME>
qmd context add qmd://<COLLECTION_NAME> "<short project/vault description>"
qmd status
qmd update
qmd search "<query>" -c <COLLECTION_NAME> -n 5
```

Run `qmd collection list` before `collection add`. Reuse an existing collection when its name and canonical vault path match. `qmd collection add` returns nonzero when that collection already exists; treat that as an idempotent reuse only after verifying the existing path, not as a failed index.

Useful environment variables:

```bash
QMD_WIKI_COLLECTION="<COLLECTION_NAME>"
QMD_CLI="qmd"
```

Gitignore local runtime state:

```gitignore
.qmd/
10_knowledge_base/.rag/
```

## Refresh Policy After Vault Writes

Run update after ObsidianAgent writes or rewrites vault Markdown and the controller has approved an index refresh:

```bash
${QMD_CLI:-qmd} update
```

Then verify:

```bash
${QMD_CLI:-qmd} status
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
${QMD_CLI:-qmd} search "<known query>" -c "$QMD_WIKI_COLLECTION" -n 5
```

If `$QMD_WIKI_COLLECTION` is unset, skip QMD and record the skip. If `qmd` is unavailable, skip QMD and record the missing CLI.

## Embeddings Are Explicit Approval Only

Do not run by default:

```bash
qmd embed
qmd query
qmd vsearch
```

Run these only when the user explicitly approves model downloads/embedding compute or the project profile says embeddings are allowed. Explain that `qmd embed` may download GGUF models from Hugging Face and can consume disk, CPU, and GPU resources.

## Status Labels

Record one of these in the manifest, ingest status, or batch report:

- `QMD refreshed: update only + verified`
- `QMD refreshed: update + embed + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <short error>`
- `QMD BM25 ready; vectors pending`
- `QMD vectors pending: qmd embed not approved`

## Local Fallback Retrieval

If QMD is absent or embeddings are not approved, use a project-local lexical/sparse retrieval fallback when needed.

- Keep fallback state under a local ignored runtime directory, such as `10_knowledge_base/.rag/`.
- Use source-grounded Markdown and manifest rows as the indexed material.
- Do not present sparse/lexical fallback retrieval as dense semantic RAG.
- Record fallback status separately from QMD status.

## Troubleshooting

QMD may print a version successfully but fail during `qmd init`, `qmd update`, or `qmd search` if a native dependency was compiled for a different Node.js version. A common symptom mentions `better-sqlite3` and `NODE_MODULE_VERSION`.

When this happens:

- record `QMD failed: Node native module ABI mismatch`;
- do not run embeddings or retry in a loop;
- ask the user's Codex session to adapt the fix to the local environment;
- possible local fixes include `npm rebuild -g @tobilu/qmd`, reinstalling `@tobilu/qmd` under the active Node version, or using the Node version that originally installed QMD;
- keep vault Markdown and manifest writes intact; QMD failure does not roll them back.

If the machine has multiple Node installations, the failure may happen even when `qmd --version` works. Check both the shell Node and the Node used by QMD's second-stage launcher:

```bash
which qmd
type -a node
node --version
node -p process.versions.modules
qmd doctor
```

Run `qmd init` from the intended project/vault before relying on `qmd doctor`; a global doctor check can fail simply because no index/cache has been initialized for that context.

If `qmd doctor` reports a different Node version than `node --version`, pin QMD commands to the Node prefix that installed QMD, for example:

```bash
QMD_BIN="$(command -v qmd)"
QMD_NODE_BIN="$(dirname "$QMD_BIN")"
QMD_PATH="$QMD_NODE_BIN:/usr/bin:/bin:/usr/sbin:/sbin"
env PATH="$QMD_PATH" "$QMD_BIN" doctor
env PATH="$QMD_PATH" "$QMD_BIN" init
env PATH="$QMD_PATH" "$QMD_BIN" update
```

Record the pinned invocation in the controller notes. Do not hide this as a normal success; it is an environment repair.
