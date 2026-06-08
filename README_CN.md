# Codex Obsidian Read：面向 Zotero 与 Obsidian 的 Codex 文献工作流

[![Preview](https://img.shields.io/badge/status-early%20preview-orange)](#早期预览声明)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](environment.yml)
[![macOS](https://img.shields.io/badge/platform-macOS%20tested-lightgrey)](#早期预览声明)
[![License](https://img.shields.io/badge/license-not%20selected-red)](#license)

[English](README.md) | **简体中文**

Codex Obsidian Read 是一个早期阶段的 Codex skill，用来把一个小研究方向组织成可恢复、可审计的文献流程：找文献、筛选、合法或授权下载 PDF、本地登记、接入 Zotero、PDF-first 精读，并生成 Obsidian/RAG-ready 的本地知识库笔记。

这个项目的出发点很朴素：让 Codex 能围绕一个小方向构建起 Obsidian 文献库，并接入 Zotero，方便研究者继续自己阅读、校对和扩展。因为 Codex 做文献流程时很容易踩坑，比如来源记录丢失、浏览器摘要被误当成论文事实、PDF 下载错、Zotero 附件只写成 URL、Obsidian 笔记脱离页码证据、长对话状态丢失，所以这里把流程拆成“总控台 + 固定 specialist session + durable Markdown 记录”。

## 早期预览声明

这是一个 **early preview**，只为急需测试这套流程的开发者提供框架思路、记录模板、提示词、脚本和依赖建议。当前不做功能性保证。

- 主要基于 macOS 开发。
- Windows 环境尚未测试。
- Browser、Zotero、Obsidian 和外部 skill 的可用性取决于你的本地 Codex 环境。
- 闭源论文必须依赖合法或已授权访问。本项目不会绕过付费墙、登录、验证码或机构权限控制。
- 如遇问题，请在 GitHub Issues 中附上平台、Codex 使用界面、依赖状态和失败阶段。

## 核心思想

必须明确指定一个 session 作为 **总控台 Controller Console**。总控台负责 goal、范围、任务记录、依赖状态、session registry、派发任务和最终验收。

其他 session 只做边界清楚的专项工作：

| Session | 职责 | 主要输出 |
| --- | --- | --- |
| Controller Console | goal、范围、路由、验收、恢复 | `project_profile.md`、`dependency_setup.md`、kanban、dispatch log、最终决策 |
| LiteratureAgent | 文献来源登记、ARS 主导的检索筛选、合法/授权下载 | candidate table、source manifest、download log、质量报告 |
| ZoteroAgent | Zotero 条目、collection、linked-file 附件和验证 | Zotero link index、附件验证记录 |
| ObsidianAgent | PDF-first 精读、选页视觉检查、Obsidian/RAG 笔记 | 文献笔记、source registry、ingest report、页码证据 |

如果某个 specialist session 不存在，总控台需要创建它，或要求用户创建，然后把 session/thread ID 记录到 `00_controller/session_registry.md`。不要每篇论文新建一个 session。

## 快速开始

### 1. 准备永久 Python 环境

推荐使用一个长期存在的命名环境，而不是每个项目临时建 `venv`。这样浏览器下载、PDF 解析、页面渲染和 OCR 工具都能稳定复用。

```bash
micromamba env create -f environment.yml
micromamba activate codex-lit
python3 scripts/env_check.py --json
```

如果环境已经存在：

```bash
micromamba activate codex-lit
micromamba env update -f environment.yml
python3 -m pip install -r requirements.txt
python3 scripts/env_check.py --json
```

### 2. 指定总控台 session

长任务开始前，先明确告诉一个 Codex session：你是总控台。

推荐短提示词：

```text
你是 codex-obsidian-read 的 Controller Console。
不要自己吞掉所有工作。
先初始化 controller records，检查依赖，选择或创建固定 specialist sessions，然后派发小范围任务。
文献发现和筛选默认使用 academic-research-suite。
research-lr-ra 只作为辅助或兜底。
只有 Controller Console 可以标记输出 accepted。
```

长任务建议给总控台挂 goal。

推荐长任务 goal 提示词：

```text
Goal: Build a source-grounded Zotero and Obsidian-ready literature workspace for <TOPIC_OR_DIRECTION>.

You are the Controller Console for codex-obsidian-read.

Rules:
- Keep this session as the only controller and acceptance owner.
- Do not perform every phase yourself unless a phase is tiny.
- Create or reuse fixed specialist sessions:
  - LiteratureAgent for ARS-led search, screening, legal/authorized acquisition, and source manifests.
  - ZoteroAgent for Zotero parent items, collections, linked PDF/MD attachments, and verification.
  - ObsidianAgent for PDF-first reading, selected visual checks, and Obsidian/RAG-ready notes.
- If a specialist session does not exist, create it or ask the user to create it, then record the thread/session ID.
- Before any long batch, initialize controller records and dependency_setup.md.
- Use academic-research-suite as the default research companion for literature discovery and screening.
- Use research-lr-ra only as auxiliary/fallback when ARS is unavailable or a narrow LR task fits it better.
- Do not bypass paywalls, logins, CAPTCHAs, or institutional access controls.
- Do not write zotero.sqlite directly.
- Do not claim paper facts from snippets or model memory.
- Every phase must write a durable handoff and update its worklog.
- Stop at Waiting review for specialist outputs; controller acceptance is separate.

Start by creating or updating the controller workspace records, dependency setup record, session registry, and first small dispatch plan.
```

### 3. 初始化目标项目的 controller records

在本 skill 仓库中运行：

```bash
python3 scripts/init_workspace.py --root /path/to/literature/project
```

它会创建：

- `00_controller/project_profile.md`
- `00_controller/initialization.md`
- `00_controller/dependency_setup.md`
- `00_controller/session_registry.md`
- controller 与 specialist worklogs
- source/download/Zotero/ingest manifests
- handoff 和状态文件

### 4. 长任务前填写依赖状态

打开生成的 `00_controller/dependency_setup.md`，记录这些依赖是否可用：

- `academic-research-suite`：文献发现与筛选默认主力。
- `research-lr-ra`：仅辅助或兜底。
- `sciencedirect-live-session-fetcher`：授权浏览器 session PDF 下载优先后端。
- `zotero:Zotero`：本地 Zotero 查询、导出、导入、验证。
- `zotero-linked-attachments`：把 PDF/MD 作为 linked-file 挂到 Zotero。
- `wiki-query`、`wiki-ingest`、`obsidian-wiki-ingest`：已有知识库查询和 Obsidian/RAG 写入。
- Browser、Chrome、Computer Use：浏览和授权下载机制。
- `codex-lit` Python 环境和 `env_check.py` 输出。

### 5. 小批量派发

总控台应该派发小批量任务，等待 durable handoff，审查后再进入下一阶段。第一批建议是 3-5 篇短论文，或 1-2 篇长报告/学位论文。

## 这个 skill 处理什么

| 阶段 | 默认路线 |
| --- | --- |
| 研究问题或方向收敛 | `academic-research-suite` |
| 外部论文发现与筛选 | `academic-research-suite` + LiteratureAgent |
| 本地 PDF 库登记 | LiteratureAgent，默认不下载 |
| 授权出版社下载 | `sciencedirect-live-session-fetcher`，再到 Chrome/Computer Use/manual |
| Zotero 条目和附件 | `zotero:Zotero` 与 `zotero-linked-attachments` |
| PDF 文本/渲染检查 | 内置脚本，必要时配合 `pdf` skill |
| Obsidian/RAG 笔记 | ObsidianAgent 与本地 wiki/Obsidian helper |
| 最终验收 | 仅 Controller Console |

## Zotero 连接

Zotero 用于本地文献库状态、citation keys、BibTeX/RIS 导出、父条目查找/导入、collection 和 linked-file 验证。

推荐做法：

1. 保持 Zotero Desktop 可用。
2. 在你的 Codex 环境里启用 Zotero plugin 或 Zotero MCP/connector。
3. 用 `zotero:Zotero` 查询本地库、导出、查找/导入条目和验证。
4. 用 `zotero-linked-attachments` 把 PDF 以及后续 Markdown 笔记作为 linked file 挂到 Zotero。
5. 不要直接写 `zotero.sqlite`。

## Obsidian 连接

Obsidian 集成采用 file-first 方式。总控台应先确定 vault 或项目目录，然后允许 ObsidianAgent 在批准路径内写 source registry、literature notes、concept links 和 ingest reports。

推荐做法：

1. 派发前确定 vault/project root。
2. 在 `project_profile.md` 中记录允许写入路径。
3. 如果本地安装了 `wiki-query`、`wiki-ingest`、`obsidian-wiki-ingest`，用它们做已有知识库查询和写入。
4. 笔记必须保持来源依据：实质性判断要指向论文、页码、表格、图、或明确 TODO。

## 仓库结构

```text
.
|-- SKILL.md
|-- README.md
|-- README_CN.md
|-- agents/
|   `-- openai.yaml
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
|   |-- pdf_probe.py
|   `-- setup_env.py
|-- environment.yml
`-- requirements.txt
```

## 验证

提交前可以跑：

```bash
python3 -m py_compile scripts/*.py
python3 -m json.tool evals/evals.json >/dev/null
python3 scripts/env_check.py --json
python3 scripts/init_workspace.py --root /private/tmp/codex_obsidian_read_smoke --force
```

## Roadmap

- 更可靠的 companion skill 安装/探测。
- 更清晰的 Codex thread/session 创建与交接模板。
- 更完整的 Zotero 与 Obsidian 验证流程。
- 使用 fake/demo PDF 的公开小样例。
- macOS 流程稳定后再测试 Windows/WSL。

## 贡献

当前项目还在确定流程契约。最有帮助的 issue 是包含失败阶段、依赖状态、平台和生成的 controller 文件。

请不要提交私人 PDF、凭据、Zotero 数据库、浏览器 cookies 或专有 Obsidian vault 内容。

## License

尚未选择许可证。正式开源前请补充许可证，否则其他人没有明确复用授权。
