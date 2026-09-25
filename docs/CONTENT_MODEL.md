# 内容模型与深度架构

本页定义知识库的结构契约。结构本身写在 [`scripts/content_model.py`](../scripts/content_model.py)，是**唯一事实来源**：校验（`scripts/harness.py`）、导出（`scripts/atlas_db.py`）、生成（`scripts/cards.py`）三者都从这里读取，避免契约漂移。

## 两条轴

每篇笔记由 `kind`（是什么）和 `depth`（投入多深）共同定义，而不是只靠 `stage` 分层。

| `kind` | 含义 | 典型内容 |
| --- | --- | --- |
| `orientation` | 导航 | 全库入口、范围与阅读顺序 |
| `concept` | 概念 | 算法与术语的定义、形式化、边界 |
| `system` | 系统 | 训练/推理系统的组成、数据流、失效模式 |
| `paper` | 论文精读 | 单篇论文的深度档案（主张、证据、边界） |
| `synthesis` | 专题综述 | 跨论文的证据地图、共识与分歧 |
| `lab` | 实验 | 可复现实验的假设、协议、结果与成本 |
| `reference` | 索引 | 术语表、路线图、维护约定 |

| `depth` | 含义 | 契约强度 |
| --- | --- | --- |
| `overview` | 概览，只保证可读与可检索 | 最少 3 节、500 字（兼容存量笔记） |
| `working` | 工作级，结构完整但未做证据分级 | 最少 4 节、1200–1800 字，需相关笔记 |
| `deep` | 深读档案，结论可用于研究决策 | 按 `kind` 强制章节、字数、主张表与证据分级 |

`depth: overview` 是**过渡态**：存量笔记先落在这里，`scripts/cards.py deepen` 与人工编辑逐步把它们升级为 `deep`。

## 证据分级（`evidenceGrade`）

每篇笔记必须声明其主张的最强支撑等级：

| 等级 | 含义 |
| --- | --- |
| `A` | 有多处独立证据或本地复现支撑；结论已交叉验证 |
| `B` | 全文精读且方法、实验设置、代码或数据可核验；未复现 |
| `C` | 全文级阅读，但结论依赖单一来源的作者自述，未经人工复核 |
| `D` | 仅摘要、元数据或未运行的计划；不得当作已确证结论 |

LLM 生成的全部卡片为 `C`，并且必须带 `review: LLM 全文精读草稿 · 待人工复核`。人工复核并交叉验证后，才可以升级为 `A`/`B`。

## 深度论文档案契约（`kind: paper`, `depth: deep`）

深读档案必须包含以下小节，且每节不少于 150 字，正文合计不少于 4500 字：

| 小节 | 必须回答的问题 |
| --- | --- |
| 问题与语境 | 问题为何重要，已有做法的失效点，本文的定位 |
| 核心主张 | 主张表（见下），并指出哪条最强、哪条最弱 |
| 机制与方法 | 机制、公式、符号含义、适用前提与设计取舍 |
| 实验设置 | 基准、模型/规模、基线、预算、指标（表格） |
| 证据与结果 | 具体数值与出处、消融与对照（表格） |
| 证据强度评估 | 本档案的 A–D 分级理由，以及对该结论的主要威胁 |
| 边界与反例 | 什么观察会推翻结论，何时最可能失效 |
| 与知识库的关系 | 相对已有笔记新增/印证/冲突了什么 |
| 复现与验证计划 | 可执行的最小验证：环境、数据、基线、预算、判据 |
| 术语与记号 | 关键符号与缩写表 |
| 自测 | 5 个问题，含折叠答案，至少 2 题需跨小节推理 |

其余 `kind` 的 `deep` 契约（`concept` / `system` / `synthesis` / `lab` / `orientation` / `reference`）同样定义在 `scripts/content_model.py` 的 `CONTRACTS` 中。

### 主张表格式

`核心主张`（论文）与 `证据地图`（综述）必须包含 Markdown 表格，至少 3 行，状态只能取固定枚举：

```markdown
| # | 主张 | 证据 | 状态 |
| --- | --- | --- | --- |
| C1 | 类别感知专家训练缓解跷跷板效应 | §4.2 表 2 | 作者主张 |
| C2 | 标签路由蒸馏提升长尾类别 | §5.1 图 3 | 作者主张 |
| C3 | 增益可迁移到未见语言 | 附录 B 表 7 | 存疑 |
```

状态枚举为 `作者主张 / 与共识一致 / 已复现 / 存疑`。这张表会被导出为结构化数据（`claimCount`、`claims`），供站点展示与检索；因此它既是写作要求，也是数据契约。

## 生成流水线

`scripts/cards.py` 生成 `kind: paper, depth: deep` 的档案，分三轮，避免把深度压在单次补全上：

1. **证据抽取**（`plan_evidence`）：读全文，产出结构化证据表——主张与定位、机制与记号、实验与数值、消融、局限、可引用片段。
2. **分节写作**（`draft_sections`）：按小节分组写作，每组的输入是证据表 + 与该节最相关的全文切片；小节长度与必备内容由 `SECTION_BRIEFS` 约束。
3. **契约与落地校验**：`check_structure` 校验章节/字数/主张表/相关笔记，`grounding_violations` 校验正文数字必须出现在原文摘录中、且不得引入原文没有的 URL。违反时触发一次定向修复重写；仍不通过就跳过并记录原因，不写入仓库。

两个入口：

```bash
python scripts/cards.py run --limit 2      # 处理审计队列中新论文
python scripts/cards.py deepen --limit 1   # 把存量薄卡改写为深读档案
python scripts/cards.py status             # 待处理队列 + 待深化存量 + 深读占比
```

`deepen` 会原地重写同一篇笔记（保留 id、order 与来源引用），并且默认只处理仍是 LLM 草稿状态的卡片；已人工复核的卡片需要显式 `--force`。

## 校验与门槛

```bash
python -m unittest discover -s tests    # 契约、装配、修复、取材的回归测试
python scripts/harness.py check --json  # 所有笔记的 kind/depth/证据分级与契约
python scripts/cards.py check           # 深读卡片契约 + 薄卡积压清单
python scripts/atlas_db.py check        # 数据库与导出是否同步
```

`harness.py check` 会在输出中给出 `depth` 统计：`byDepth`、`byKind`、`deep`、`deepShare`，用于跟踪向深度架构迁移的进度。仍未深化的 LLM 草稿会被列为 warning（而非 error），因此积压可见但不阻断 CI；真正的契约违反是 error。

## 手工写一篇深读笔记

1. 复制对应 `kind` 的模板（`templates/`），或从 `python scripts/cards.py run` 生成的草稿起步。
2. 填全 frontmatter：`kind`、`depth: deep`、`evidenceGrade`，以及 `related`（至少 2 篇，用于接入知识图谱）。
3. 按契约补齐小节，并写主张表；每个数字都要能在来源中定位。
4. 运行 `python scripts/atlas_db.py build && python scripts/harness.py check`，直到无 error。
