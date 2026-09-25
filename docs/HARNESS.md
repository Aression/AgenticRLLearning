# Maintenance Harness

`scripts/harness.py` 是知识库的统一维护入口。它默认离线运行，不调用模型，不自动编辑正文，也不会把论文摘要升级为已审核知识。

## Commands

```bash
python scripts/harness.py check --json
python scripts/harness.py report --json
python scripts/harness.py refresh
python scripts/harness.py all --refresh
```

`check` 检查 Markdown frontmatter、唯一 ID、来源引用、内部 `/notes/...` 链接、日期、来源审计覆盖率，以及每篇笔记的 `kind` / `depth` / `evidenceGrade` 与其章节契约（见 [`CONTENT_MODEL.md`](CONTENT_MODEL.md)）。输出同时包含 `depth` 统计（`byDepth`、`byKind`、`deep`、`deepShare`），用于跟踪深度架构的迁移进度；仍未深化的 LLM 草稿列为 warning 而非 error。`refresh` 才会访问来源和 HuggingFace Daily Papers，并更新 `research/source-audit.json` 与 `research/discovery.json`。`report` 写入带时间戳的 JSON 报告和 `research/reports/latest.json`。

## 内容数据库与知识图谱

`content/*.md` 是人工编辑格式；`scripts/atlas_db.py` 把它和 `data/sources.json` 导入 SQLite 数据库 `data/atlas.db`，再导出站点使用的拆分数据：

- `data/generated/notes.index.json`：笔记元数据（不含正文），含 `kind`/`depth`/`evidenceGrade`/`claims`/`sectionSizes` 以及证据分级与类型标签表，供列表与客户端搜索
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

知识库结构（`kind`、`depth`、章节契约、证据分级）定义在 [`CONTENT_MODEL.md`](CONTENT_MODEL.md)，代码级事实来源是 `scripts/content_model.py`。审计 workflow 在 DeepSeek 分流后运行 `scripts/cards.py`，分三轮生成 `kind: paper, depth: deep` 的深读档案：

1. 汇总 `research/agent-audits/audit-*.json` 的历史候选与当天 `data/generated/radar.json`，按每篇论文最近一次审计决定选择尚未入库的 `review`；旧候选先处理，避免每日雷达覆盖后丢失待办；
2. 抓取 arXiv HTML 全文（失败时回退 ar5iv），保留章节结构、表格行与公式 alttext，按相关性分配全文预算；
3. **证据抽取**：产出结构化证据表（主张 + 定位、机制与记号、实验与数值、消融、局限、可引用片段）；
4. **分节写作**：按小节分组写作，每节的长度与必备内容由 `SECTION_BRIEFS` 约束，输入为证据表 + 与该节最相关的全文切片；
5. **校验与修复**：契约校验（章节/字数/主张表/相关笔记）与落地校验（正文数字必须出现在原文摘录中、不得引入原文没有的 URL）；违反时触发一次定向重写，仍不通过则跳过并记录原因，不写入仓库；
6. 写入 `content/<order>-<id>.md` 与 `data/sources.json`，随后重建数据库与图谱。

生成的卡片带 `kind: paper`、`depth: deep`、`evidenceGrade: C`、`review: LLM 全文精读草稿 · 待人工复核`、`paper_id`、`claim_count`、`full_text_url`，只会进入审计 PR，合并前必须人工复核；论文全文不会写入仓库。每轮最多成功生成 2 篇（`harness.config.json` 的 `cardGeneration.maxCards`），抓取全文或制卡失败会记录在 `research/cards/latest.json` 的 `skipped` 中；历史审计缺失作者与日期时尝试从 HuggingFace 论文 API 补取。审计记录保存后续制卡所需的论文元数据，并复用 `agent-audit/latest` 分支累积未合并的草稿。`pendingReviews` 与 `deepenBacklog` 分别记录待制卡新论文与待深化薄卡数量；`status` 命令可列出两者。审计意见仅表示需要人工阅读，并不自动保证每篇候选都适合写卡。

存量薄卡用 `deepen` 原地升级为深读档案，保留 id、order 与来源引用；默认只重写仍是 LLM 草稿状态的卡片，已人工复核的卡片需要 `--force`：

```bash
python scripts/cards.py run --limit 2
python scripts/cards.py deepen --limit 1
python scripts/cards.py run --paper 2609.12419   # 单篇调试
python scripts/cards.py status                    # 待处理队列 + 待深化存量 + 深读占比
python scripts/cards.py check                     # 深读卡片契约 + 薄卡积压清单
python scripts/harness.py cards                   # 等价于 cards.py run
```

`scripts/search-papers.py` 从 HuggingFace Daily Papers（`https://huggingface.co/api/daily_papers`）拉取当日论文，用 `STRONG_KEYWORDS` / `BROAD_KEYWORDS` 对标题与摘要做 grep，只保留与知识库主题相关的条目（上限取 `harness.config.json` 的 `refresh.maxDiscoveryResults`）。网络失败时保留上一次的 `research/discovery.json`，不会让维护任务失败。

## Agent 审核 workflow

`.github/workflows/agent-audit.yml` 在采集 workflow 成功后运行。它把 `research/discovery.json` 和 `data/sources.json` 交给 DeepSeek `deepseek-v4-flash` 做候选分流，结果写入 `research/agent-audits/`，并创建独立分支和 Pull Request。采集 workflow 会把含最新 `research/discovery.json` 的 `atlas-maintenance-report` artifact 上传，审核 workflow 通过 `github.event.workflow_run.id` 下载该 artifact 后再运行，因此审计用的是当天刷新的结果，而不是仓库里上一次提交的旧文件。模型只生成审计意见，结果带有 `human_review_required=true` 和 `publish_directly=false`，不会直接修改 `content/` 或 `data/sources.json`。

在 GitHub repository settings 的 Actions secrets 中配置 `DEEPSEEK_V4_FLASH_API_KEY`。脚本只从环境变量读取 key，不读取仓库中的 `.env`，不打印请求、响应或 token。API 失败、返回非法 JSON 或 harness 失败时，workflow 失败且不会创建 PR。API key 不应写入 issue、artifact、PR 描述或提交。

## 暂停模型调用

`harness.config.json` 的顶层 `llm` 是模型调用的总开关：

```json
"llm": { "enabled": false, "disabledReason": "..." }
```

当它为 `false` 时，所有会调用模型的脚本（`scripts/cards.py run/deepen`、`scripts/agent_audit.py`）在发出第一个请求前就以退出码 `3` 终止，不会消耗 token、也不会写入内容。离线命令不受影响：`cards.py check/status/fetch`、`harness.py check`、`atlas_db.py build/check` 仍可正常使用，因此暂停期间仍可校验与查阅仓库。

单次覆盖（不修改文件）：

```bash
ATLAS_LLM_ENABLED=1 python scripts/cards.py deepen --limit 1
```

退出码约定：`0` 成功，`1` 内容契约失败，`2` 脚本或输入错误，`3` 模型调用被暂停。

## 当前维护状态（模型调用已暂停）

**状态：暂停中**——自 2026-09-25 起人工暂停，恢复前不会有任何自动制卡或审计提交。

| 对象 | 位置 | 状态 |
| --- | --- | --- |
| 模型调用总开关 | `harness.config.json` → `llm.enabled` | `false` |
| Knowledge maintenance | Actions workflow `353304335` | `disabled_manually` |
| Agent audit and archive | Actions workflow `353313263` | `disabled_manually` |
| Content check（离线校验） | Actions workflow `353295278` | active |
| Deploy to Vercel | Actions workflow `353295279` | active |

暂停期间：`cards.py run/deepen` 与 `agent_audit.py` 在**发出第一个请求之前**就以退出码 `3` 终止，不消耗 token，也不写入内容。离线命令照常可用：`harness.py check`、`cards.py check/status/fetch`、`atlas_db.py build/check`、`npm test`、`npm run build`。向 master 推送或开 PR 只会触发 Content check 与 Vercel 部署，两者都不调用模型。

### 恢复清单

1. 打开代码开关：`harness.config.json` → `"llm": { "enabled": true }`；或单次覆盖 `ATLAS_LLM_ENABLED=1 python scripts/cards.py deepen --limit 1`。
2. 恢复定时任务：

   ```bash
   gh workflow enable 353304335   # Knowledge maintenance
   gh workflow enable 353313263   # Agent audit and archive
   ```

3. **先处理暂停前遗留的审计分支**（重要，见下）。
4. 补齐深读积压：`python scripts/cards.py deepen --limit N`（用 `status` 查看队列）。

### 遗留分支：恢复前必须处理

暂停时 `agent-audit/latest` 上仍有 1 个未合并提交（2026-09-25 那次审计），包含 3 篇旧流水线薄卡，其 `order` 与 master 上现有笔记**直接冲突**：

| 分支上的卡片 | order | master 上同号笔记 |
| --- | --- | --- |
| `rewardverse-rubric-video-rm` | 55 | `agora-git` |
| `aewm-agent-editing-world-model` | 56 | `hypoevolve` |
| `spatial-interactor-opd` | 57 | `riskchainbench` |

审核 workflow 恢复后会执行 `git merge -X theirs FETCH_HEAD` 合并该分支，因此会带出重复 `order`，使 `harness.py check` 失败、从而**不会创建 PR**。恢复到步骤 3 时请二选一：

```bash
# 方案 A：丢弃分支上的旧草稿，让下次运行从干净的 master 开新分支
git push origin --delete agent-audit/latest

# 方案 B：保留草稿——先把 3 篇卡片迁入内容模型并移到 73 起的新序号，再重建数据库
```

对应的 PR #20 已于 2026-09-25 关闭（其内容与 master 的深度架构不一致，其中 9 篇卡片已随 PR #17 进入 master 并重新编号为 64–72）。

### 暂停时的内容快照

| 指标 | 数值 |
| --- | --- |
| 笔记 | 72（其中 `depth: deep` 40） |
| 深读占比 | 55.6% |
| 结构化主张 | 180 |
| 来源 | 83 |
| 图谱边 | 867（笔记间关系 513 + 概念边 354） |
| 待深化薄卡 | 9（`cards.py status` 可查） |
| 待制卡新论文 | 9（均为无条件全文而跳过） |

## 更新原则

定时任务只负责发现和报告。来源、主张、前沿状态和正文变化必须通过人工审阅的 Git commit 进入生产站点。预印本默认为 `摘要核验 · 待精读`，代码仓库的页面可访问不代表实验已复现。

## 失败处理

命令退出码 `0` 表示通过，`1` 表示内容契约失败，`2` 表示 harness 本身或输入文件错误。CI 使用 `check` 阻断构建；定时刷新产生报告后创建 issue，维护者审阅后再提交内容变更。
