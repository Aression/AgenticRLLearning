# Agentic RL Atlas

可持续维护的 Agentic RL 个人知识库与研究导航站点。

## 内容模型

- `content/*.md` 是人工编辑的原子笔记（frontmatter + 正文），一篇一个文件。
- 每篇笔记由 `kind`（是什么）与 `depth`（概览/工作级/深读）共同定义，并声明 `evidenceGrade`（A–D 证据分级）。深读论文档案必须包含主张表、机制、实验设置、证据强度评估、边界与反例、与知识库的关系、复现计划、术语表与自测；完整契约见 [`docs/CONTENT_MODEL.md`](docs/CONTENT_MODEL.md)。
- `data/atlas.db`（SQLite）是内容数据库：导入笔记与来源，保存标签/概念、先修、共享来源等关系。
- `data/generated/` 是数据库导出给站点的拆分数据：`notes.index.json`（元数据，含类型/深度/证据分级/主张）、`notes/<id>.json`（单篇正文）、`graph.json`（知识图谱）、`sources.json`。
- 改动 Markdown 或来源后运行 `npm run content:build` 重新生成数据库与导出，用 `npm run content:check` 校验同步。
- 来源优先级：原始论文 > 官方课程/文档 > 作者博客 > 可复现实验仓库。
- 每条来源必须有稳定 URL、机构/作者、年份和一句“为什么读”。每季度复核链接与结论。

## 知识图谱

站点内置“知识图谱”视图：节点是知识笔记与概念标签，边来自先修顺序、显式相关、共享来源与共享概念。图谱由 `scripts/atlas_db.py` 从内容数据库生成，可开关关系类型并聚焦邻居。

## 研究雷达

“研究雷达”视图展示 HuggingFace Daily Papers 抓取、按知识库关键词过滤、再由 DeepSeek 分流的候选论文（review / archive / skip），附匹配关键词、热度、链接、审计理由与风险。数据写入 `data/generated/radar.json`，随每日审计 PR 更新；证据仅到摘要级，入库前需人工精读。

## 自动知识卡

> 当前暂停生成，见上文[维护状态](#维护状态)。以下描述的是恢复后的正常流程。

维护流水线从历史审计和当天 HuggingFace Daily Papers 雷达中选择仍为 `review` 且尚未入库的论文，每轮最多生成 2 张**深度档案**（`kind: paper`、`depth: deep`），历史待办先处理。生成分三轮：先抽取结构化证据表，再分节深读写作，最后用内容契约与“数字必须出现在原文摘录中”的落地校验把关，不通过则跳过而不写入。存量薄卡由 `python scripts/cards.py deepen` 原地升级为深读档案。写入 `content/` 与 `data/sources.json` 后重建数据库与图谱，随审计 PR 提交。卡片标记 `origin: llm-fulltext`、`depth: deep`、`evidenceGrade: C` 与 `review: LLM 全文精读草稿 · 待人工复核`，合并前必须人工复核；论文全文不写入仓库。未合并的草稿会在 `agent-audit/latest` 分支上累积。用 `python scripts/cards.py status` 查看待制卡与待深化队列。

## 维护状态

> **模型调用暂停中（自 2026-09-25）**：`harness.config.json` 的 `llm.enabled` 为 `false`，GitHub Actions 的 **Knowledge maintenance** 与 **Agent audit and archive** 已手动停用。`cards.py run/deepen` 与 `agent_audit.py` 会在发出首个请求前以退出码 `3` 退出，不消耗 token、不写入内容；离线校验、构建与部署不受影响。
>
> 恢复步骤、以及恢复前必须先处理的遗留审计分支（`agent-audit/latest` 上 3 篇卡片的 order 与 master 冲突），见 [`docs/HARNESS.md`](docs/HARNESS.md)。

## 本地运行

```bash
npm install
npm run dev
```

## Vercel 自动部署

在 Vercel 导入此 Git 仓库，Framework 选择 Next.js，Build Command 使用 `npm run build`。推送到默认分支会自动部署。若使用 GitHub Actions，可在仓库 Secrets 配置 `VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`，并将 `VERCEL_KEY` 保存在本地 `.env`（不要提交）。

## 维护 Harness

> 定时任务当前已停用（见[维护状态](#维护状态)）；`harness.py` 的离线命令仍可正常使用。

统一入口为 `python scripts/harness.py`，详见 [`docs/HARNESS.md`](docs/HARNESS.md)。每天 UTC 00:00（北京时间 08:00）的 GitHub Actions 会从 HuggingFace Daily Papers 抓取当日论文、按知识库关键词过滤，刷新来源元数据、运行内容契约、构建站点并上传报告。定时任务只创建维护 issue，不自动提交或发布正文；来源和新主张必须人工审阅后再合并。

## 研究路线

基础层覆盖 MDP、Bellman、Policy Gradient 和 ReAct；系统层覆盖工具环境、RLHF/RLAIF、GRPO、长时程信用分配、评估与安全；前沿层覆盖多智能体协作与在线自我改进。每篇笔记另带两个维度：`kind`（概念/系统/论文精读/综述/实验/索引）与 `depth`（概览/工作级/深读），深读档案要求可定位的主张表与证据分级，详见 [`docs/CONTENT_MODEL.md`](docs/CONTENT_MODEL.md)。
