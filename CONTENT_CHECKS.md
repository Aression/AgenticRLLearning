# 内容检查

在提交前运行：

```bash
python -m unittest discover -s tests
python scripts/harness.py check --json
python scripts/cards.py check
python -m json.tool data/sources.json > $null
python experiments/replay.py
python scripts/atlas_db.py build   # 仅在编辑 content/ 或 data/sources.json 后
python scripts/atlas_db.py check   # 校验 data/atlas.db 与 data/generated/ 是否同步
npm run build
```

维护者还应检查每篇笔记的 frontmatter：`id` 唯一、`order` 数字、`sources` 全部存在、`updated` 为 ISO 日期、预印本标注 `待精读`。

内容模型决定每篇笔记还必须满足什么：`kind`（概念/系统/论文精读/综述/实验/索引）、`depth`（概览/工作级/深读）与 `evidenceGrade`（A–D）。`harness.py check` 会校验对应章节契约并输出 `depth` 统计；深读论文档案必须包含主张表、机制、实验设置、证据强度评估、边界与反例、与知识库的关系、复现计划、术语表与自测。完整契约与写作要求见 [`docs/CONTENT_MODEL.md`](docs/CONTENT_MODEL.md)，代码级事实来源是 `scripts/content_model.py`。

LLM 生成的卡片用 `python scripts/cards.py check` 校验深读契约，并用 `python scripts/cards.py status` 查看待制卡与待深化队列；存量薄卡用 `python scripts/cards.py deepen` 升级为深读档案。统一入口见 [`docs/HARNESS.md`](docs/HARNESS.md)：`check` 离线阻断错误，`refresh` 才联网写入核验记录，`report` 生成带时间戳的维护报告。`scripts/research.py` 只负责保存 HTTP 元数据，不自动把摘要变为结论。
