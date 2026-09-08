# Agentic RL Atlas

可持续维护的 Agentic RL 个人知识库与研究导航站点。

## 内容模型

- `data/knowledge.ts` 是唯一内容源，节点包含阶段、主题、难度、状态、标签和来源。
- 来源优先级：原始论文 > 官方课程/文档 > 作者博客 > 可复现实验仓库。
- 每条来源必须有稳定 URL、机构/作者、年份和一句“为什么读”。每季度复核链接与结论。

## 本地运行

```bash
npm install
npm run dev
```

## Vercel 自动部署

在 Vercel 导入此 Git 仓库，Framework 选择 Next.js，Build Command 使用 `npm run build`。推送到默认分支会自动部署。若使用 GitHub Actions，可在仓库 Secrets 配置 `VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`，并将 `VERCEL_KEY` 保存在本地 `.env`（不要提交）。

## 维护 Harness

统一入口为 `python scripts/harness.py`，详见 [`docs/HARNESS.md`](docs/HARNESS.md)。每周一 UTC 01:17 的 GitHub Actions 会刷新来源元数据、运行内容契约、构建站点并上传报告。定时任务只创建维护 issue，不自动提交或发布正文；来源和新主张必须人工审阅后再合并。

## 研究路线

基础层覆盖 MDP、Bellman、Policy Gradient 和 ReAct；系统层覆盖工具环境、RLHF/RLAIF、GRPO、长时程信用分配、评估与安全；前沿层覆盖多智能体协作与在线自我改进。
