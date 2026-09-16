# Agentic RL Atlas

可持续维护的 Agentic RL 个人知识库与研究导航站点。

## 内容模型

- `content/*.md` 是人工编辑的原子笔记（frontmatter + 正文），一篇一个文件。
- `data/atlas.db`（SQLite）是内容数据库：导入笔记与来源，保存标签/概念、先修、共享来源等关系。
- `data/generated/` 是数据库导出给站点的拆分数据：`notes.index.json`（元数据）、`notes/<id>.json`（单篇正文）、`graph.json`（知识图谱）、`sources.json`。
- 改动 Markdown 或来源后运行 `npm run content:build` 重新生成数据库与导出，用 `npm run content:check` 校验同步。
- 来源优先级：原始论文 > 官方课程/文档 > 作者博客 > 可复现实验仓库。
- 每条来源必须有稳定 URL、机构/作者、年份和一句“为什么读”。每季度复核链接与结论。

## 知识图谱

站点内置“知识图谱”视图：节点是知识笔记与概念标签，边来自先修顺序、显式相关、共享来源与共享概念。图谱由 `scripts/atlas_db.py` 从内容数据库生成，可开关关系类型并聚焦邻居。

## 研究雷达

“研究雷达”视图展示 HuggingFace Daily Papers 抓取、按知识库关键词过滤、再由 DeepSeek 分流的候选论文（review / archive / skip），附匹配关键词、热度、链接、审计理由与风险。数据写入 `data/generated/radar.json`，随每日审计 PR 更新；证据仅到摘要级，入库前需人工精读。

## 本地运行

```bash
npm install
npm run dev
```

## Vercel 自动部署

在 Vercel 导入此 Git 仓库，Framework 选择 Next.js，Build Command 使用 `npm run build`。推送到默认分支会自动部署。若使用 GitHub Actions，可在仓库 Secrets 配置 `VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`，并将 `VERCEL_KEY` 保存在本地 `.env`（不要提交）。

## 维护 Harness

统一入口为 `python scripts/harness.py`，详见 [`docs/HARNESS.md`](docs/HARNESS.md)。每天 UTC 00:00（北京时间 08:00）的 GitHub Actions 会从 HuggingFace Daily Papers 抓取当日论文、按知识库关键词过滤，刷新来源元数据、运行内容契约、构建站点并上传报告。定时任务只创建维护 issue，不自动提交或发布正文；来源和新主张必须人工审阅后再合并。

## 研究路线

基础层覆盖 MDP、Bellman、Policy Gradient 和 ReAct；系统层覆盖工具环境、RLHF/RLAIF、GRPO、长时程信用分配、评估与安全；前沿层覆盖多智能体协作与在线自我改进。
