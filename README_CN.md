# codex-literature-workflow

面向 Codex、Zotero 与 Obsidian 的 agent-native 文献工作流。

[![Stable](https://img.shields.io/badge/status-formal%20release-brightgreen)](#正式版支持范围)
[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](VERSION)
[![Validate](https://github.com/ParkerGong/codex-literature-workflow/actions/workflows/validate.yml/badge.svg)](https://github.com/ParkerGong/codex-literature-workflow/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/python-3.12%20tested-blue)](environment.yml)
[![macOS](https://img.shields.io/badge/platform-macOS%20tested-lightgrey)](#正式版支持范围)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) | **简体中文**

发布证据：[1.0.0 审计报告](RELEASE_AUDIT.md)

## 公益声明

本项目是公益性质的，旨在为想用 Codex 进行文献管理、连接 Zotero 方便阅读、制作 Obsidian 私人知识库，但不知道如何开始的朋友，提供一个最最基础的工作流。此工作流只是提供思路，项目里面存在很多十分消耗 token 的环节都需优化，因此请不要把这个项目“奉为圣旨”。

`codex-literature-workflow` 是一个由总控台协调的 Codex skill，用来把研究方向或本地 PDF 库组织成可恢复、可审计的文献流程：找文献、筛选、合法或授权获取 PDF、本地登记、接入 Zotero、PDF-first 精读，并生成 manifest-backed Obsidian 笔记，必要时再做可选 QMD 刷新。

这个项目的出发点很朴素：让 Codex 能围绕一个小方向构建起 Obsidian 文献库，并接入 Zotero，方便研究者继续自己阅读、校对和扩展。因为 Codex 做文献流程时很容易踩坑，比如来源记录丢失、浏览器摘要被误当成论文事实、PDF 下载错、Zotero 附件只写成 URL、Obsidian 笔记脱离页码证据、长对话状态丢失，所以这里把流程拆成“总控台 + 固定 specialist session + durable Markdown 记录”。

## 正式版支持范围

1.0.0 是工作流契约和确定性辅助脚本的正式版。离线回归测试覆盖：skill 元数据、安全安装、controller workspace 初始化与备份、环境报告、PDF 探针的成功/失败语义，以及基于 mock Local API 的 Zotero linked-file mapping 与验证。

1.0.0 发布门已通过 40/40 项离线回归测试，并验证了主 skill 与两个 vendored companion 共 3 个 skill tree。测试核心、集成证据和有意保留的人工边界见[发布审计](RELEASE_AUDIT.md)。

真实集成仍取决于本机环境：

- Zotero Desktop 写入需要用户运行生成的 JavaScript，再通过 Local API 验证；本项目绝不写 `zotero.sqlite`。
- Obsidian 采用 file-first 集成，只能写入用户明确允许的 vault 路径。
- QMD 是可选项。update/search 可能需要固定到安装 QMD 的 Node 前缀；未经明确授权绝不运行 embedding。
- 出版社授权访问依赖用户或机构的合法权限；本工作流不绕过付费墙、CAPTCHA、登录或许可限制。
- macOS 是当前维护测试平台；Windows 仍未验证。

首次运行仍应使用隔离 workspace，并为重要 Zotero 库和 Obsidian vault 做好备份。报告问题时请提供失败阶段、平台、依赖状态、命令输出和 controller records，不要提交私人 PDF、凭据、cookie 或数据库文件。

## 核心思想

长的多阶段流程默认把当前 task 记录为 **总控台 Controller Console**；如果用户已指定其他总控台，则沿用用户选择。总控台负责范围、任务记录、依赖状态、session registry、派发和最终验收；只有用户明确要求 goal tracking 时才负责持久 goal。

其他 session 只做边界清楚的专项工作：

| Session | 职责 | 主要输出 |
| --- | --- | --- |
| Controller Console | 范围、可选 goal、路由、验收、恢复 | `project_profile.md`、`dependency_setup.md`、kanban、dispatch log、最终决策 |
| LiteratureAgent | 文献来源登记、ARS 主导的检索筛选、合法/授权下载 | candidate table、source manifest、download log、质量报告 |
| ZoteroAgent | 只读查询、linked-file mapping/script 准备和验证 | Zotero link index、生成脚本、附件验证记录 |
| ObsidianAgent | PDF-first 精读、Obsidian Wiki ingest、可选 QMD/RAG 刷新状态 | 文献笔记、`.manifest.json`、source registry、ingest report、页码证据 |

有 multi-agent 工具时，总控台创建或复用固定 specialist session，并记录到 `00_controller/session_registry.md`；没有时就按同一 handoff/status 契约顺序执行各阶段。不要每篇论文新建一个 session。

## 快速开始

### 1. 安装主 skill

在本仓库 clone 中先做 dry-run，再在规范目录中创建可安装 skill 包：

```bash
python3 scripts/install_skill.py --dry-run
python3 scripts/install_skill.py
```

只有明确要做带备份的覆盖安装时才使用 `--force`。随后新建一个 Codex task，用 `$codex-literature-workflow` 验证 skill 能被发现。

#### 从预览版升级

安装器不会静默覆盖预览版。先检查带备份的替换计划，再明确执行：

```bash
python3 scripts/install_skill.py --dry-run --force
python3 scripts/install_skill.py --force
```

替换前，安装器会把现有 skill 目录移动到 Codex home 下带时间戳的备份目录。

### 2. 准备永久 Python 环境

推荐使用一个长期存在的命名环境，而不是每个项目临时建 `venv`。这样浏览器下载、PDF 解析、页面渲染和 OCR 工具都能稳定复用。

```bash
micromamba env create -f environment.yml
micromamba activate codex-literature
python3 scripts/env_check.py --json --strict
```

如果没有 `micromamba`，可等价使用 `mamba env create -f environment.yml` 或 `conda env create -f environment.yml`，再激活 `codex-literature`。

如果环境已经存在：

```bash
micromamba activate codex-literature
micromamba env update -f environment.yml
python3 -m pip install -r requirements.txt
python3 scripts/env_check.py --json --strict
```

### 3. 安装或启用 companion skills/plugins

正式测试前，先让 Codex 安装或启用与你要测试的流程匹配的外部 skills/plugins：

公开/开源 companion skills 有明确上游时，建议直接从 GitHub 安装。本仓库只打包下表中标注为 vendored 的维护者自建 companion skills。

| Companion | 推荐状态 | 原始/来源 URL | 用途 |
| --- | --- | --- | --- |
| `academic-research-suite` | 强烈推荐 | Codex adapter: <https://github.com/Imbad0202/academic-research-skills-codex>；upstream suite: <https://github.com/Imbad0202/academic-research-skills> | 默认文献发现、筛选策略、query expansion、引用/完整性检查 |
| `research-lr-ra` | 可选辅助 | 已 vendored 到本仓库 `companion-skills/research-lr-ra` | ARS 不可用或某个窄 LR 子任务更适合时，用于旧 LR 支持和 research-gap mapping |
| `zotero:Zotero` plugin/connector | 需要 Zotero 输出时启用 | OpenAI/Codex plugin capability；见 <https://help.openai.com/en/articles/20001256> | 只读 Zotero 查询、导出、collection 和验证；导入由用户执行 |
| `zotero-linked-attachments` | 需要 Zotero linked files 时启用 | 已 vendored 到本仓库 `companion-skills/zotero-linked-attachments` | 准备由用户运行的 PDF/MD linked-file 脚本，并只读验证结果 |
| 来自 `Given-Dream/sciencedirect-live-session-fetcher` 的 `sciencedirect-live-session-fetcher` | 可选；授权浏览器下载测试时推荐 | <https://github.com/Given-Dream/sciencedirect-live-session-fetcher> | 复用 live authorized browser session 获取出版社 PDF |
| Browser / Chrome / Computer Use plugins | 可选但很有用 | OpenAI/Codex plugin capabilities；见 <https://help.openai.com/en/articles/20001256> | 浏览器导航、认证 session、UI fallback |
| `wiki-query`、`wiki-ingest` 或 `obsidian-wiki-ingest` | 需要本地 KB 集成时启用 | 安装前需核验的公开示例：<https://github.com/Ar9av/obsidian-wiki>、<https://github.com/AgriciDaniel/claude-obsidian> | 已有知识库查询与 Obsidian/RAG 风格笔记接入 |
| QMD (`@tobilu/qmd`) | 需要本地 vault search/index 刷新时启用 | npm package: <https://www.npmjs.com/package/@tobilu/qmd> | 更新并查询本地 vault 索引；embedding 必须明确批准 |

如果某个 companion 不可用，把状态记录到 `00_controller/dependency_setup.md`，并走文档中的 fallback 路径。不要假装已经使用了不可用的 companion。

把这些 vendored 的维护者自建 companion skills 安装到当前 Codex skills 目录：

```bash
python3 scripts/install_companion_skills.py
```

只有在你明确要覆盖本地已有副本时，才加 `--force`。

### 4. 记录总控台 session

长任务开始前，把当前 task 记录为总控台；如果用户已经选择了另一个总控台，则沿用该选择。

推荐短提示词：

```text
你是 codex-literature-workflow 的 Controller Console。
不要自己吞掉所有工作。
先初始化 controller records，检查依赖，选择或创建固定 specialist sessions，然后派发小范围任务。
文献发现和筛选默认使用 academic-research-suite。
research-lr-ra 只作为辅助或兜底。
只有我或 host project 明确启用时才创建本地 Git checkpoint；绝不自动 push。
只有 Controller Console 可以标记输出 accepted。
```

只有用户明确要求 goal tracking 时才创建持久 goal；否则记录 `long_task_goal: not-needed`。

推荐长任务 goal 提示词：

```text
Goal: Build a source-grounded Zotero and Obsidian-ready literature workspace for <TOPIC_OR_DIRECTION>.

You are the Controller Console for codex-literature-workflow.

Rules:
- Keep this session as the only controller and acceptance owner.
- Do not perform every phase yourself unless a phase is tiny.
- Create or reuse fixed specialist sessions:
  - LiteratureAgent for ARS-led search, screening, legal/authorized acquisition, and source manifests.
  - ZoteroAgent for Zotero parent/collection lookup, linked PDF/MD script preparation, and verification; the user runs Desktop writes.
  - ObsidianAgent for PDF-first reading, selected visual checks, Obsidian Wiki manifest-backed notes, and optional QMD/local RAG refresh status.
- Create or reuse fixed specialist sessions when supported; otherwise record and use sequential phase execution.
- Before any long batch, initialize controller records and dependency_setup.md.
- Before a full multi-phase run, ask for paper direction, expected paper count, source input mode, download/access permission, language scope, Zotero connection, Obsidian connection, local input paths, output paths, collection/vault mapping needs, and checkpoint policy.
- Record those answers in project_profile.md and set user_scope_confirmed=true before dispatch.
- If Git checkpoints are enabled, verify the target root before committing. If disabled, record that state and continue.
- When enabled, checkpoint only explicit privacy-reviewed files at the configured interval.
- Run privacy scans before staging files. Do not commit private PDFs, Zotero databases, browser cookies, credentials, or closed vault content unless explicitly approved. Never push automatically.
- Use academic-research-suite as the default research companion for literature discovery and screening.
- Use research-lr-ra only as auxiliary/fallback when ARS is unavailable or a narrow LR task fits it better.
- Do not bypass paywalls, logins, CAPTCHAs, or institutional access controls.
- Do not write zotero.sqlite directly.
- Do not treat QMD as the source of truth. QMD is optional index/search infrastructure; run qmd embed only with explicit approval.
- Do not claim paper facts from snippets or model memory.
- Every phase must write a durable handoff and update its worklog.
- Stop at Waiting review for specialist outputs; controller acceptance is separate.

Start by creating or updating the controller workspace records, dependency setup record, session registry, and first small dispatch plan.
```

### 5. 初始化目标项目的 controller records

在本 skill 仓库中运行：

```bash
python3 scripts/init_workspace.py --root /path/to/literature/project
```

它会创建：

- `00_controller/project_profile.md`
- `00_controller/initialization.md`
- `00_controller/dependency_setup.md`
- `00_controller/session_registry.md`
- `00_controller/git_checkpoints.md`
- controller 与 specialist worklogs
- source/download/Zotero/ingest manifests
- handoff 和状态文件

### 6. 回答启动前 scope 问题

完整的多阶段检索/下载/Zotero/Obsidian 流程开始前，总控台确认缺失且会影响结果的 scope 字段；单一阶段只询问相关字段。

1. 论文方向或研究边界。
2. 第一批期望找多少篇。
3. 来源模式：已有本地 PDF、新检索/下载、或混合。
4. 是否启用新 PDF 下载/获取；若启用，是仅开放获取，还是允许授权浏览器/manual 访问。
5. 语言范围：英文、中文、或中英都要。
6. 是否接入 Zotero。
7. 是否创建 Obsidian/RAG-ready 笔记。
8. 如果启用 Zotero，使用哪个 collection 或 mapping 文档。
9. 如果启用 Obsidian，vault/project root 和允许写入路径是什么。
10. 是否已有方向文档、文献索引、本地 PDF 文件夹、manifest、或 Zotero/Obsidian mapping 文件。
11. 是否启用 QMD 刷新、复用/创建哪个 collection、是否批准 embedding。
12. 是否启用本地 Git checkpoint；如果启用，目标 Git root 是什么。

把这些答案记录到 `00_controller/project_profile.md`，并在派发 specialist 工作前设置 `user_scope_confirmed: true`。

### 7. 配置可选的本地 Git checkpoint

generic profile 默认不启用 Git checkpoint。只有用户或 host project protocol 要求本地恢复 commit 时才启用；启用后创建本地 commit：

- 初始化、启动 scope、依赖和 session 记录写完后；
- 每 3 个有文件写入的 meaningful steps 或 accepted handoffs 后；
- 危险批量写入、Zotero 附件批处理、Obsidian 笔记批处理、暂停或交接前。

checkpoint commit 是本地恢复点，不等于 push 到 GitHub。总控台必须检查 `git status`，对准备提交的文本文件做隐私扫描，只 stage 明确安全的路径，并把结果记录到 `00_controller/git_checkpoints.md`。不要使用 `git add .`，除非用户另行明确要求，否则绝不自动 push。

### 8. 长任务前填写依赖状态

打开生成的 `00_controller/dependency_setup.md`，记录这些依赖是否可用：

- `academic-research-suite`：文献发现与筛选默认主力。
- `research-lr-ra`：仅辅助或兜底。
- `sciencedirect-live-session-fetcher`：授权浏览器 session PDF 下载优先后端。
- `zotero:Zotero`：只读 Zotero 查询、导出和验证；导入由用户执行。
- `zotero-linked-attachments`：准备由用户运行的 PDF/MD linked-file 脚本，并只读验证结果。
- `wiki-query`、`wiki-ingest`、`obsidian-wiki-ingest`：已有知识库查询和 Obsidian/RAG 写入。
- QMD：vault 写入后的可选本地 search/index 后端；不是基础笔记生成的必要条件。
- Browser、Chrome、Computer Use：浏览和授权下载机制。
- `codex-literature` Python 环境和 `env_check.py` 输出。

### 9. 小批量派发

总控台应该派发小批量任务，等待 durable handoff，审查，并在启用 checkpoint 时提交恢复点，再进入下一阶段。第一批建议是 3-5 篇短论文，或 1-2 篇长报告/学位论文。

## 这个 skill 处理什么

| 阶段 | 默认路线 |
| --- | --- |
| 研究问题或方向收敛 | `academic-research-suite` |
| 外部论文发现与筛选 | `academic-research-suite` + LiteratureAgent |
| 本地 PDF 库登记 | LiteratureAgent，默认不下载 |
| 授权出版社下载 | `sciencedirect-live-session-fetcher`，再到 Chrome/Computer Use/manual |
| Zotero 条目和附件 | `zotero:Zotero` 与 `zotero-linked-attachments` |
| PDF 文本/渲染检查 | 内置脚本和配置好的 Python 环境 |
| Obsidian Wiki / manifest-backed 笔记 | ObsidianAgent 与本地 wiki/Obsidian helper |
| QMD/local RAG 刷新 | 可选 `qmd update` + status/search 验证，或 lexical/sparse fallback |
| Git checkpoints | 仅 Controller Console；本地 commit，不自动 push |
| 最终验收 | 仅 Controller Console |

## Zotero 连接

Zotero 用于本地文献库状态、citation keys、BibTeX/RIS 导出、父条目查找、由用户执行的导入、collection 和 linked-file 验证。

推荐做法：

1. 需要 live 步骤时，请用户打开 Zotero Desktop。
2. 在你的 Codex 环境里启用 Zotero plugin 或 Zotero MCP/connector。
3. 用 `zotero:Zotero` 只读查询本地库、导出、查找条目和验证；导入保持用户确认。
4. 用 `zotero-linked-attachments` 准备已校验的 mapping/script，请用户运行，再验证 PDF 或 Markdown child attachment。
5. 不要直接写 `zotero.sqlite`。

## Obsidian 连接

Obsidian 集成采用 file-first 方式。总控台应先确定 vault 或项目目录，然后允许 ObsidianAgent 在批准路径内写 source registry、literature notes、concept links 和 ingest reports。

推荐做法：

1. 派发前确定 vault/project root。
2. 在 `project_profile.md` 中记录允许写入路径。
3. 如果本地安装了 `wiki-query`、`wiki-ingest`、`obsidian-wiki-ingest`，用它们做已有知识库查询和写入。
4. 如果项目需要 durable RAG-ready 状态，使用 manifest-backed Obsidian Wiki / LLM Wiki 风格 ingest：`.manifest.json`、`01_sources/source_registry.md`、`01_sources/zotero_link_index.md`，并且每个 canonical source 只生成一篇 formal note。
5. 笔记必须保持来源依据：实质性判断要指向论文、页码、表格、图、或明确 TODO。

## QMD / Local RAG

QMD 是可选的。它可以在 vault 写入后刷新本地 search/index 层：

```bash
npm install -g @tobilu/qmd
qmd init
qmd collection list
qmd collection add <VAULT_PATH> --name <COLLECTION_NAME>  # 仅在不存在时添加；否则复用已核验路径
qmd update
qmd search "<known query>" -c <COLLECTION_NAME> -n 5
```

QMD 不是 source of truth。除非用户明确批准模型下载和 embedding 计算，否则不要运行 `qmd embed`、`qmd query` 或 `qmd vsearch`。多套 Node 导致原生模块 ABI 错误时，使用 `references/qmd-rag.md` 中的固定 PATH 恢复方法。

## 仓库结构

```text
.
|-- SKILL.md
|-- README.md
|-- README_CN.md
|-- RELEASE_AUDIT.md
|-- LICENSE
|-- VERSION
|-- agents/
|   `-- openai.yaml
|-- companion-skills/
|   |-- research-lr-ra/
|   `-- zotero-linked-attachments/
|-- evals/
|   `-- evals.json
|-- references/
|   |-- initialization.md
|   |-- dependencies.md
|   |-- architecture.md
|   |-- controller-records.md
|   |-- environment.md
|   `-- ...
|-- scripts/
|   |-- env_check.py
|   |-- init_workspace.py
|   |-- install_skill.py
|   |-- install_companion_skills.py
|   |-- pdf_probe.py
|   |-- setup_env.py
|   `-- validate_skills.py
|-- tests/
|   `-- test_*.py
|-- environment.yml
|-- requirements.txt
`-- requirements-dev.txt
```

## 验证

请在由 `environment.yml` 创建并已激活的 `codex-literature` 环境中运行这些检查。若使用其他环境，请先安装声明的 Python 依赖以及 Poppler、Tesseract 等系统 PDF/OCR 工具。

```bash
python3 -m pip install -r requirements.txt -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 -m py_compile scripts/*.py
python3 -m json.tool evals/evals.json >/dev/null
node --check companion-skills/zotero-linked-attachments/scripts/build_zotero_linked_attachment_js.mjs
node --check companion-skills/zotero-linked-attachments/scripts/verify_zotero_linked_attachments.mjs
python3 -m unittest discover -s tests -v
python3 scripts/env_check.py --json --strict
python3 scripts/init_workspace.py --root /private/tmp/codex_literature_workflow_smoke --dry-run
```

## Roadmap

- 针对一次性测试库的 opt-in Zotero live integration tests。
- 使用非专有 demo PDF 的可复现公开样例。
- 补充 Windows/WSL 验证与平台专用安装说明。

## 贡献

最有帮助的 issue 应包含失败阶段、依赖状态、平台、生成的 controller 文件和脱敏后的错误输出。

请不要提交私人 PDF、凭据、Zotero 数据库、浏览器 cookies 或专有 Obsidian vault 内容。

## License

本项目使用 MIT License 开源。见 [LICENSE](LICENSE)。
