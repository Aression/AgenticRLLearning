# Maintenance Harness

`scripts/harness.py` 是知识库的统一维护入口。它默认离线运行，不调用模型，不自动编辑正文，也不会把论文摘要升级为已审核知识。

## Commands

```bash
python scripts/harness.py check --json
python scripts/harness.py report --json
python scripts/harness.py refresh
python scripts/harness.py all --refresh
```

`check` 检查 Markdown frontmatter、唯一 ID、来源引用、内部 `/notes/...` 链接、日期和来源审计覆盖率。`refresh` 才会访问来源和 arXiv，并更新 `research/source-audit.json` 与 `research/discovery.json`。`report` 写入带时间戳的 JSON 报告和 `research/reports/latest.json`。

## Agent 审核 workflow

`.github/workflows/agent-audit.yml` 在采集 workflow 成功后运行。它把 `research/discovery.json` 和 `data/sources.json` 交给 DeepSeek `deepseek-chat` 做候选分流，结果写入 `research/agent-audits/`，并创建独立分支和 Pull Request。模型只生成审计意见，结果带有 `human_review_required=true` 和 `publish_directly=false`，不会直接修改 `content/` 或 `data/sources.json`。

在 GitHub repository settings 的 Actions secrets 中配置 `DEEPSEEK_V4_FLASH_API_KEY`。脚本只从环境变量读取 key，不读取仓库中的 `.env`，不打印请求、响应或 token。API 失败、返回非法 JSON 或 harness 失败时，workflow 失败且不会创建 PR。API key 不应写入 issue、artifact、PR 描述或提交。

## 更新原则

定时任务只负责发现和报告。来源、主张、前沿状态和正文变化必须通过人工审阅的 Git commit 进入生产站点。预印本默认为 `摘要核验 · 待精读`，代码仓库的页面可访问不代表实验已复现。

## 失败处理

命令退出码 `0` 表示通过，`1` 表示内容契约失败，`2` 表示 harness 本身或输入文件错误。CI 使用 `check` 阻断构建；定时刷新产生报告后创建 issue，维护者审阅后再提交内容变更。
