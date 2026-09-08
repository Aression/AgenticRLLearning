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

## 更新原则

定时任务只负责发现和报告。来源、主张、前沿状态和正文变化必须通过人工审阅的 Git commit 进入生产站点。预印本默认为 `摘要核验 · 待精读`，代码仓库的页面可访问不代表实验已复现。

## 失败处理

命令退出码 `0` 表示通过，`1` 表示内容契约失败，`2` 表示 harness 本身或输入文件错误。CI 使用 `check` 阻断构建；定时刷新产生报告后创建 issue，维护者审阅后再提交内容变更。
