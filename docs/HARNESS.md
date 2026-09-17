# Maintenance Harness

`scripts/harness.py` 是知识库的统一维护入口。它默认离线运行，不调用模型，不自动编辑正文，也不会把论文摘要升级为已审核知识。

## Commands

```bash
python scripts/harness.py check --json
python scripts/harness.py report --json
python scripts/harness.py refresh
python scripts/harness.py all --refresh
```

`check` 检查 Markdown frontmatter、唯一 ID、来源引用、内部 `/notes/...` 链接、日期和来源审计覆盖率。`refresh` 才会访问来源和 HuggingFace Daily Papers，并更新 `research/source-audit.json` 与 `research/discovery.json`。`report` 写入带时间戳的 JSON 报告和 `research/reports/latest.json`。

## 内容数据库与知识图谱

`content/*.md` 是人工编辑格式；`scripts/atlas_db.py` 把它和 `data/sources.json` 导入 SQLite 数据库 `data/atlas.db`，再导出站点使用的拆分数据：

- `data/generated/notes.index.json`：笔记元数据（不含正文），供列表与客户端搜索
- `data/generated/notes/<id>.json`：单篇笔记（含正文），只在服务端按需读取
- `data/generated/graph.json`：知识图谱节点与边
- `data/generated/sources.json`：来源目录
- `data/generated/radar.json`：最近一次 HuggingFace Daily Papers 抓取与 DeepSeek 审计的合并结果，由 `scripts/agent_audit.py` 写入并随审计 PR 提交

```bash
python scripts/atlas_db.py build   # 重新导入并导出
python scripts/atlas_db.py check   # 校验导出与数据库、正文同步
python scripts/atlas_db.py graph   # 打印图谱统计
```

图谱边来自先修关系、显式 `related`、共享来源与共享概念；概念标签从笔记 `tags` 归一化并单独建表。`npm run content:build` 与 `npm run content:check` 是同一入口；维护 workflow 在构建前运行 `atlas_db.py check`。

## 知识卡生成

审计 workflow 在 DeepSeek 分流后运行 `scripts/cards.py`：

1. 从 `data/generated/radar.json` 选择 `decision=review` 且尚未入库的论文；
2. 抓取 arXiv HTML 全文（失败时回退 ar5iv），抽取摘要与方法、实验、结论等章节；
3. 让 DeepSeek 依据全文写一张克制的中文知识卡；
4. 写入 `content/<order>-<id>.md` 与 `data/sources.json`，随后重建数据库与图谱。

生成的卡片带 `origin: llm-fulltext`、`review: LLM 全文精读草稿 · 待人工复核`、`paper_id`、`full_text_url`，只会进入审计 PR，合并前必须人工复核；论文全文不会写入仓库。每轮最多 3 篇（`harness.config.json` 的 `cardGeneration.maxCards`），并复用 `agent-audit/latest` 分支累积未合并的草稿。

```bash
python scripts/cards.py run --limit 3
python scripts/cards.py run --paper 2609.12419   # 单篇调试
python scripts/cards.py check
python scripts/harness.py cards                  # 等价于 cards.py run
```

`scripts/search-papers.py` 从 HuggingFace Daily Papers（`https://huggingface.co/api/daily_papers`）拉取当日论文，用 `STRONG_KEYWORDS` / `BROAD_KEYWORDS` 对标题与摘要做 grep，只保留与知识库主题相关的条目（上限取 `harness.config.json` 的 `refresh.maxDiscoveryResults`）。网络失败时保留上一次的 `research/discovery.json`，不会让维护任务失败。

## Agent 审核 workflow

`.github/workflows/agent-audit.yml` 在采集 workflow 成功后运行。它把 `research/discovery.json` 和 `data/sources.json` 交给 DeepSeek `deepseek-v4-flash` 做候选分流，结果写入 `research/agent-audits/`，并创建独立分支和 Pull Request。采集 workflow 会把含最新 `research/discovery.json` 的 `atlas-maintenance-report` artifact 上传，审核 workflow 通过 `github.event.workflow_run.id` 下载该 artifact 后再运行，因此审计用的是当天刷新的结果，而不是仓库里上一次提交的旧文件。模型只生成审计意见，结果带有 `human_review_required=true` 和 `publish_directly=false`，不会直接修改 `content/` 或 `data/sources.json`。

在 GitHub repository settings 的 Actions secrets 中配置 `DEEPSEEK_V4_FLASH_API_KEY`。脚本只从环境变量读取 key，不读取仓库中的 `.env`，不打印请求、响应或 token。API 失败、返回非法 JSON 或 harness 失败时，workflow 失败且不会创建 PR。API key 不应写入 issue、artifact、PR 描述或提交。

## 更新原则

定时任务只负责发现和报告。来源、主张、前沿状态和正文变化必须通过人工审阅的 Git commit 进入生产站点。预印本默认为 `摘要核验 · 待精读`，代码仓库的页面可访问不代表实验已复现。

## 失败处理

命令退出码 `0` 表示通过，`1` 表示内容契约失败，`2` 表示 harness 本身或输入文件错误。CI 使用 `check` 阻断构建；定时刷新产生报告后创建 issue，维护者审阅后再提交内容变更。
