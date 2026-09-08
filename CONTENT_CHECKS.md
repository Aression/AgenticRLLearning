# 内容检查

在提交前运行：

```bash
npm run build
python -m json.tool data/sources.json > $null
python experiments/replay.py
python scripts/harness.py check --json
```

维护者还应检查每篇笔记的 frontmatter：`id` 唯一、`order` 数字、`sources` 全部存在、`updated` 为 ISO 日期、预印本标注 `待精读`。统一入口见 [`docs/HARNESS.md`](docs/HARNESS.md)：`check` 离线阻断错误，`refresh` 才联网写入核验记录，`report` 生成带时间戳的维护报告。`scripts/research.py` 只负责保存 HTTP 元数据，不自动把摘要变为结论。
