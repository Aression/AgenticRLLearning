---
id: root-cause-attribution-search
title: 根因归因即搜索：长程 Agent 失败的持续搜索
summary: 长时程AI智能体执行日志可达数百万token，失败根因证据稀疏、分散且可能远早于最终结果出现。现有基于LLM裁判的单轮rubric式根因归因方法在证据空间未充分探索前就锁定一个看似合理的失败原因，导致归因不可靠；而自一致性、异构裁判组等重采样策略无法恢复遗漏证据。
stage: FRONTIER
track: 评估与安全
kind: paper
depth: deep
evidenceGrade: C
order: 51
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.13463
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 5
full_text_url: https://arxiv.org/html/2609.13463
objectives: [理解为何长程 Agent 根因归因应被建模为证据空间上的迭代搜索问题, 掌握 Continual Search 与 Passive Continuation、自一致性、异构评审团等基线的差异与增益, 了解长轨迹基准（MegaRCA-Mix、TRAIL、TELBench）与短轨迹基准（AgentRx、Who&When）上的效果分化, 认识该方法的成本、可观测性限制与标签噪声等边界条件]
tags: [root-cause-analysis, agent-failure-attribution, long-horizon-agents, llm-as-judge, continual-search, evaluation]
sources: [root-cause-attribution-is-a-search-probl]
related: [evaluation, agent-loop, multi-turn-rl]
prerequisites: [evaluation, agent-loop]
---
## 问题与语境

长时程智能体（agent）的执行记录可达数百万 token，而解释一次失败的证据往往稀疏、分散，且首次偏离正确执行的位置可能远早于最终结果出现。论文给出的现实动机是 Hugging Face 安全事件：调查者需要恢复并分析超过 70,000 条 agent 消息与文件才能重建入侵时间线，且重建过程需要反复通读执行记录，每一遍都会浮现此前阅读遗漏的证据。这说明根因归因（RCA）在安全与生产场景中不只是评测指标问题，而是决定干预对象（模型、harness、环境还是评分器）的前置环节。

已有做法的核心是 LLM 裁判：以 rubric 引导的单轮（single-pass）检查产出归因，Agent-as-a-Judge 进一步允许裁判通过工具查看中间证据。为提升可靠性，常见策略是自一致性与异构裁判组等重采样。论文指出的失效点是：当执行日志变大且证据分散时，LLM 倾向于在充分探索证据空间之前就锁定一个"看起来合理"的失败原因；而重采样只是对同一份证据做多次独立评估，无法恢复被遗漏的证据。论文的定位因此不是提出更强的单轮裁判或更好的聚合策略，而是把 RCA 重新刻画为对执行记录的证据搜索问题，并给出迭代式 Continual Search 框架：每轮要求裁判挑战既有结论、检索未读工具输出或未探索区域。与之配套，论文提出长时程基准 MegaRCA-Mix（50 个人工标注失败试验，中位执行规模 286K token），用以在现有 RCA 基准普遍偏短的证据空间之外检验该假设。需要说明的是，上述因果叙事属作者主张，本文未独立复现。

## 核心主张

论文的核心主张可概括为：长时程 RCA 的瓶颈在证据搜索而非单轮推理能力，因此"跨轮持续搜索新证据"应优于"在同一证据上重复判断或增加推理算力"。作者用三类对照支撑这一主张：与 Passive Continuation 的指令对照（唯一变量是后续轮次是否要求检查新证据）、与自一致性/异构裁判组的重采样对照、以及与推理 effort 和模型规模的对照。需要区分的是，这些结论均为作者在自建与既有基准上的报告结果，本文未做独立复现；其中短轨迹上的负向结果作者自己也承认与既有关于 LLM 裁判认知不稳定的发现一致。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | 在长执行记录基准上，Continual Search 优于单轮归因与 Passive Continuation | §4.1 表 2：MegaRCA-Mix 上 GPT-5.5 F1 0.349→0.498（Passive 0.401）；TRAIL Weighted F1 0.426→0.500（Passive 0.451） | 作者主张 |
| C2 | Continual Search 优于自一致性与异构裁判组等独立重采样基线 | §5.1 表 4：TRAIL 上 Opus-4.8 Joint Acc 自一致性 0.138→0.205，Weighted F1 0.430→0.539；自一致性甚至低于单轮（0.153→0.138） | 作者主张 |
| C3 | 在短执行轨迹上增益消失甚至为负 | §4.3 表 3：GPT-5.5 在 AgentRx 0.345→0.241，Who&When 0.548→0.452 | 作者主张 |
| C4 | 增益来自跨轮获取新证据而非单纯增加算力 | §5.3 图 7 去重 13-gram 观测 token；§4.2 图 5：Opus-4.8 低 effort 在 turn 3 达 0.533，约 62% 累计 token | 作者主张 |
| C5 | 增益与证据覆盖扩张同步 | §A.1 图 9：覆盖率由 turn 1 的 70.8% 升至 turn 3 的 94.6%、turn 4 的 97.4%；Passive 自 turn 2 起停在 77.0% | 作者主张 |

最强的是 C2。它同时具备机制对照与成本对照：自一致性消耗的推理预算高于 Continual Search（表 4：Opus-4.8 为 $6.52 对 $2.58；GPT-5.5 为 $8.66 对 $6.24），却低于其所聚合的单轮归因，这直接削弱了"增益只是更多 test-time compute"的替代解释。C1 与 C5 相互印证，但 C5 的覆盖率指标定义依赖作者自建的工件划分，外部可比性较弱。最弱的是 C4 的"search-limited rather than reasoning-bound"表述：它由低 effort 匹配高 effort 的少数配置推出（Opus-4.8 与 Sonnet-5 各一例），且 §A.2 显示单轮基线本身在多次运行间波动于 0.129–0.153，因此该结论更宜视为方向性证据而非已确立的机制结论。C3 的负向结果样本量小（AgentRx n=29、Who&When n=126），且 Opus-4.8 在 AgentRx 上仍为正增益，说明"短轨迹必退化"并非普适规律。

## 机制与方法

论文把根因归因（Root-Cause Attribution, RCA）重新表述为**对执行记录中证据的搜索问题**：给定一条失败的智能体执行记录 $E$（可能达数百万 token），目标是定位「首次偏离正确执行的根因」$r^\*$ 并归责到模型、harness、环境或评分器等组件。作者的核心论点是：单轮 rubric 式 LLM 裁判会在证据空间被充分探索之前就锁定一个「看起来合理」的失败原因，而重采样（自一致性、异构裁判组）只是在同一证据子集上重复采样，无法恢复被遗漏的证据。

**机制。** 对每个样本，先运行基准原生的单轮 RCA，由具备工具调用能力的 agentic judge（只读访问评估记录）产生 turn 1 归因 $a_1$。随后把**同一会话**分支为两个续接条件，二者共享裁判配置、评估记录、任务指令与 $a_1$，唯一变量是后续轮次的指令：

- **Passive Continuation（对照）**：要求裁判重新考虑并确认现有结论，不要求检查新证据；
- **Continual Search（本文方法）**：要求裁判**挑战**当前结论，检查未解决或此前未检查的证据——未读工具输出、执行记录中未探索的区域、或未考虑过的候选失败步骤。

裁判通过 Bash、Grep、Glob 等工具按需检索，而非把海量轨迹直接内联进上下文（避免信息饱和与上下文耗尽）。每轮保留基准原生输出 schema，最多续接至 turn 4，按各基准原生指标评分。形式化地，第 $t$ 轮可写为

$$a_t = \mathrm{Judge}\big(a_{t-1},\ \mathrm{Read}_t(E)\big),\quad t = 1,\dots,4,$$

其中 $\mathrm{Read}_t(E)$ 是裁判在第 $t$ 轮通过工具实际读取的证据子集，$a_0$ 为空。关键设计取舍在于：**把「是否继续搜索」与「是否改变结论」解耦**——Passive Continuation 只施加确认压力，Continual Search 施加的是探索压力。作者用「去重观测 token」（移除重复 13-gram 片段后累计的裁判读取 token）来度量 $\mathrm{Read}_t(E)$ 中真正新增的证据量，从而把「搜索到新证据」与「单纯多花算力」区分开。

**适用前提。** 方法有效的前提是**证据空间中仍存在未被初始归因覆盖的材料**。作者明确指出：在短轨迹基准（AgentRx 中位 7.2K token、Who&When 中位 2.4K token）上，turn 1 已基本读完整个日志，后续轮次的提示退化为「对话压力」，可能迫使裁判翻转到错误标签（GPT-5.5 在 AgentRx 从 0.345 降至 0.241，Who&When 从 0.548 降至 0.452）。因此 Continual Search 的收益随执行记录规模增长，而非普适增益。此外，方法假设失败根因在**可观测记录**内可被定位；作者在局限性中承认，许多被评估轨迹由不暴露 thinking token 的专有模型生成，真实因果失败可能发生在未观测步骤中，结果应解释为「对可观测记录的根因归因」。

## 实验设置

论文在五个 RCA 设定上评估 Continual Search，均保留各基准原生的任务形式与评分逻辑，以独立于任何特定 RCA schema。裁判实现基于 Claude Agent SDK，具备对评估记录的只读访问与工具检索能力。两个续接条件共享裁判配置、评估记录、任务指令与 turn 1 预测，唯一变量是后续轮次指令；最多续接 4 轮。下表按实验块汇总设置（未在证据中写明的字段标为「未说明」）。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| MegaRCA-Mix | GPT-5.5 | Single-turn / Passive Continuation | 4 continuation turns | F1 |
| MegaRCA-Mix | Opus-4.8 | Single-turn / Passive Continuation | 4 continuation turns | F1 |
| TRAIL | GPT-5.5 | Single-turn / Passive Continuation | 4 continuation turns | Joint Accuracy、Weighted F1 |
| TRAIL | Opus-4.8 | Single-turn / Passive Continuation | 4 continuation turns | Joint Accuracy、Weighted F1 |
| TELBench | GPT-5.5 | Single-turn / Passive Continuation | 4 continuation turns | native metric |
| TELBench | Opus-4.8 | Single-turn / Passive Continuation | 4 continuation turns | native metric |
| AgentRx | GPT-5.5 | Single-turn / Passive Continuation | 4 continuation turns | native metric |
| AgentRx | Opus-4.8 | Single-turn / Passive Continuation | 4 continuation turns | native metric |
| Who&When | GPT-5.5 | Single-turn / Passive Continuation | 4 continuation turns | native metric |
| Who&When | Opus-4.8 | Single-turn / Passive Continuation | 4 continuation turns | native metric |
| TRAIL | Opus-4.8 | Self-consistency（4 samples，多数投票） | 4 samples | Joint Accuracy、Weighted F1 |
| TRAIL | GPT-5.5 | Self-consistency（4 samples，多数投票） | 4 samples | Joint Accuracy、Weighted F1 |
| TRAIL | Judge panel（GPT-5.5, Opus-4.7, Opus-4.8, Grok-4.6） | Single-turn | 4 models | Joint Accuracy、Weighted F1 |
| TRAIL | GLM-4.7 | Turn 1 | 4 turns | Weighted F1 |
| TRAIL | Sonnet-5 | Turn 4 | 4 turns | Weighted F1 |
| TRAIL | Opus-4.8（low effort） | high effort | turn 3 | Weighted F1 |
| TRAIL | Sonnet-5（low effort） | high/max effort | turn 4 | Weighted F1 |
| MegaRCA-Mix | Opus-4.8 taxonomy classifier | ABA（Automated Benchmark Analysis） | Turns 1–4 | F1、Precision、Recall |

**基准规模。** MegaRCA-Mix 为本文提出，$n=50$，中位 286K token / 1.05 MiB，取自 Harbor Index 执行记录，覆盖 GAIA、SWE-Bench、HLE、OpenRCA 及 15 个额外基准，共 29 个基准、7 个领域；TRAIL $n=148$，中位 100K token / 430 KiB；TELBench $n=33$，中位 39K token / 144 KiB；AgentRx $n=29$，中位 7.2K token / 23.9 KiB；Who&When $n=126$，中位 2.4K token / 8.9 KiB。TRAIL 与 TELBench 的指标定义、以及各基准原生指标的精确公式见原文附录 B.3（本次摘录未给出公式细节，标注为不确定）。成本对比（Table 4）以发布 API 费率下的每轨迹平均价格计。

## 证据与结果

下表汇总摘录中可核对的数字。所有数值均照抄原文，未在摘录中出现的量一律标注「摘录未给出」。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| F1 | 0.349 → 0.498（Continual Search）；Passive 0.401 | MegaRCA-Mix, GPT-5.5, 4 turns | §1 / §4.1 表2 |
| F1 | 0.478 → 0.620（Continual Search）；Passive 0.559 | MegaRCA-Mix, Opus-4.8 | §4.1 表2 |
| Joint Accuracy | 0.156 → 0.257；Passive 0.189 | TRAIL, GPT-5.5 | §4.1 表2 |
| Weighted F1 | 0.426 → 0.500；Passive 0.451 | TRAIL, GPT-5.5 | §1 / §4.1 表2 |
| Joint Accuracy | 0.153 → 0.205；Passive 0.155 | TRAIL, Opus-4.8 | §4.1 表2 |
| Weighted F1 | 0.486 → 0.539；Passive 0.502 | TRAIL, Opus-4.8 | §4.1 表2 |
| native metric | 0.121 → 0.212；Passive 0.152 | TELBench, GPT-5.5 | §4.1 表2 |
| native metric | 0.121 → 0.182；Passive 0.061 | TELBench, Opus-4.8 | §4.1 表2 |
| native metric | 0.345 → 0.241；Passive 0.310 | AgentRx, GPT-5.5 | §4.3 表3 |
| native metric | 0.345 → 0.414；Passive 0.345 | AgentRx, Opus-4.8 | §4.3 表3 |
| native metric | 0.548 → 0.452；Passive 0.508 | Who&When, GPT-5.5 | §4.3 表3 |
| native metric | 0.373 → 0.325；Passive 0.373 | Who&When, Opus-4.8 | §4.3 表3 |
| Joint Acc. / Weighted F1 | 0.138 / 0.430 | TRAIL, Opus-4.8, Self-consistency (4 samples) | §5.1 表4 |
| Joint Acc. / Weighted F1 | 0.135 / 0.386 | TRAIL, GPT-5.5, Self-consistency | §5.1 表4 |
| Joint Acc. / Weighted F1 | 0.173 / 0.431（Opus-4.8）；0.175 / 0.435（GPT-5.5） | TRAIL, Judge panel（GPT-5.5, Opus-4.7, Opus-4.8, Grok-4.6） | §5.1 表4 |
| Cost $ | 1.21 / 2.11（Single-turn）；6.52 / 8.66（Self-consistency）；4.73 / 4.72（Judge panel）；2.58 / 6.24（Continual Search） | TRAIL, Opus-4.8 / GPT-5.5 | §5.1 表4 |
| Weighted F1 | 0.268（T1）→ 0.473（T4） | TRAIL, GLM-4.7 | §4.2 |
| Weighted F1 | 0.518（T4） | TRAIL, Sonnet-5 | §4.2 |
| Weighted F1 | 0.533（T3，约 62% 累计 token） | TRAIL, Opus-4.8 low effort | §4.2 |
| Weighted F1 | 0.521（T4） | TRAIL, Sonnet-5 low effort | §4.2 |
| 去重证据 token | 42K → 58K（Continual Search）；48K（Passive） | 四轮 | §1 / §5.3 图7 |
| 工件覆盖率 | 70.8%（T1）→ 94.6%（T3）→ 97.4%（T4）；Passive 自 T2 起 77.0% | §A.1 图9 | §A.1 |
| F1 / Precision / Recall | T1 0.16/1.00/0.09；T2 0.67/0.92/0.52；T3 0.74/0.93/0.61；T4 0.74/0.93/0.61；ABA 0.63/0.51/0.83 | MegaRCA-Mix, Opus-4.8 分类器 vs ABA | §6 图8 |
| 中位执行规模 | MegaRCA-Mix 286K token / 1.05 MiB / n=50；TRAIL 100K / 430 KiB / n=148；TELBench 39K / 144 KiB / n=33；AgentRx 7.2K / 23.9 KiB / n=29；Who&When 2.4K / 8.9 KiB / n=126 | 表1 | §3.2 表1 |
| 最高三分位中位日志 | 3.40 MB（MegaRCA-Mix）；2.46 MB（TRAIL）；19–34 KB（AgentRx）；5–16 KB（Who&When） | §5.2 | §5.2 |
| 跨运行增益 | Joint Acc. 0.037–0.055；Weighted F1 0.021–0.064；单轮基线波动 0.129–0.153 | TRAIL, Opus-4.8, 四次运行 | §A.2 表5 |

消融与对照。唯一变量是续接指令：两分支共享裁判配置、评估记录、任务指令与 T1 预测，Passive 仅要求复核确认，Continual Search 要求挑战结论并检索未检查证据（§3.1）。对照基线包括自一致性（4 样本多数投票）与异构裁判组；自一致性在 Joint Accuracy 上相对单轮反而回退（Opus-4.8 0.153→0.138，GPT-5.5 0.156→0.135），且成本高于 Continual Search（§5.1）。模型规模消融显示 GLM-4.7、Sonnet-5、Opus-4.8、Fable-5 均逐轮单调提升（§4.2）；推理努力消融显示低 effort 可匹配或超过高 effort（§4.2）。短轨迹上增益消失甚至为负（§4.3）。四次独立运行的绝对增益区间与单轮基线波动区间重叠（§A.2），逐运行数值见证据表 Table 5；显著性检验、置信区间与效应量在摘录中均未给出。

## 证据强度评估

证据分级：B（内部一致、方向可复现，但缺统计显著性与独立复现）。

理由。其一，实验设计具备较强的内部对照：Passive Continuation 与 Continual Search 共享裁判配置、评估记录、任务指令与 T1 预测，唯一变量是续接指令（§3.1），这排除了「多轮本身带来增益」的混淆，也解释了为何自一致性在更大预算下仍不涨（§5.1）。其二，方向性证据跨基准、跨模型、跨运行一致：MegaRCA-Mix、TRAIL、TELBench 上两个裁判模型均提升，Opus-4.8 在 TRAIL 上四次独立运行全部保持正增益（§A.2）。其三，机制侧有可观测的中间量支撑——去重 13-gram 观测 token 从 42K 增至 58K（Passive 仅 48K）、工件覆盖率 70.8%→97.4%（Passive 停在 77.0%），说明增益伴随新证据进入而非单纯上下文堆积（§5.3、§A.1）。其四，短轨迹上的负结果（AgentRx 0.345→0.241）与「证据已耗尽」的解释自洽，构成对机制的证伪性检验，而非选择性报告。未达 A 的关键缺口：摘录未给出任何显著性检验、置信区间或多次采样的方差估计，而 §A.2 显示单轮基线本身在 0.129–0.153 间波动，增益区间 0.037–0.055 与之同量级，无法从摘录判断是否超出噪声。

主要威胁。

构造效度。评测依赖人工标注的根因真值，作者自承「在超大规模执行日志上建立可靠人工真值本身困难，会引入标签噪声」，且「当前失败分类法可能存在重叠类别，人为压低分类分数」（§7）。若标签本身有噪声，则所有方法的绝对分数与相对排序都可能被压缩或扭曲。

外部效度。MegaRCA-Mix 仅 50 条、TELBench 33 条、AgentRx 29 条，样本量小；且轨迹多由不暴露 thinking token 的专有模型生成，真实因果失败可能发生在不可观测步骤（§7）。因此结论应限定为「对可观测记录的归因」，迁移到自建 agent 栈时需重新验证证据空间是否足够大。

统计显著性与基线选择。缺显著性检验是最大短板；同时自一致性基线在 Joint Accuracy 上低于单轮，这一反常结果提示基线实现（4 样本多数投票、聚合方式）可能未调优，若基线偏弱则 Continual Search 的相对优势被高估。裁判组基线成本受四家 API 价格混淆，作者亦承认（§5.1）。

成本与评测污染。Continual Search 成本高于单轮（TRAIL 上 Opus-4.8 \$2.58 vs \$1.21，GPT-5.5 \$6.24 vs \$2.11），部署时需权衡；此外五个基准中 TRAIL、TELBench、AgentRx、Who&When 均为已发表基准，若裁判模型训练数据覆盖其公开标注，存在潜在污染，摘录未讨论此点。

## 边界与反例

**什么观察会推翻结论。** 论文的核心主张是「长时程 RCA 是搜索受限而非推理受限」（C4）。若在控制「新增去重证据量」后，Continual Search 相对 Passive Continuation 的增益消失，则该主张被推翻——即增益只是多轮提示带来的额外算力，而非新证据。作者用去重 13-gram 观测 token 作为代理（§5.3），但这是间接证据：它只证明「读到了新内容」，未证明「新内容因果性地改变了判定」。一个直接的证伪实验是：把 Passive Continuation 的预算提到与 Continual Search 相同的观测 token 量，若差距收敛，则「搜索」解释不成立。

**最可能失效的条件。** 作者自己给出了清晰的边界：证据空间已被首轮覆盖时，续接提示退化为「对话压力」，会把裁判推向错误标签（§4.3）。GPT-5.5 在 AgentRx 从 0.345 降至 0.241、Who&When 从 0.548 降至 0.452，即为反例。因此失效条件可操作化为：首轮证据覆盖率接近饱和（短轨迹，中位 7.2K / 2.4K token），或分类法类别重叠导致「换标签」成本低。此外，作者未验证但读者可能误推的方向有三：其一，把「低 effort 匹配高 effort」（Opus-4.8 在 turn 3 达 0.533、约 62% 累计 token）误推为「推理 effort 无用」——该结论仅在 TRAIL 单一基准、且裁判已具备基线能力时成立；其二，把「低阶模型可追平前沿模型」误推为「模型规模不重要」——论文只测了 GLM-4.7、Sonnet-5、Opus-4.8、Fable-5 四档，且未报告低于某能力阈值时的崩溃点；其三，把 MegaRCA-Mix 上的分类器结果（F1 0.16→0.74，召回 0.09→0.61，精度保持 >0.90）误推为「通用基准审计可替代专用流水线」——该对比仅 50 条试验、单一裁判模型，且作者承认推理成本更高。

**未验证的迁移风险。** 所有结果都建立在「可观测记录」之上；作者明确限制：私有模型的思考 token 不可见，真实根因可能发生在未观测步骤。因此任何把该框架用于「需要归因到模型内部推理」的场景，都超出了论文的证据范围。

## 与知识库的关系

**新增。** 相对 `agentic-survey`，本文新增的不是又一个 LLM-judge RCA 变体，而是把归因形式化为「对证据空间的搜索」，并给出可对照的续接条件设计（Passive Continuation vs. Continual Search，唯一变量是后续轮次指令）。相对 `long-horizon agent reliability and evaluation`，新增 MegaRCA-Mix（50 条人工标注、中位 286K token、覆盖 29 个基准 7 个领域）这一长时程基准，以及「搜索收益随证据空间增大而出现、随其饱和而反转」的边界刻画。

**印证。** 与 `swe-agent` 相关：TRAIL 与 MegaRCA-Mix 含 SWE-Bench 轨迹，Continual Search 在其上提升归因，印证「长时程软件工程失败需要多轮取证」。与 `gaia` 相关：MegaRCA-Mix、TRAIL、TELBench 均含 GAIA 派生执行，结论方向一致。与 `tau-bench` 相关：AgentRx 使用 retail τ-bench 轨迹（中位 7.2K token），本文在此**未**获得一致增益，这恰好印证了「短轨迹上首轮即覆盖大部分证据」的假设，而非与之冲突。

**张力。** 与「更多测试时算力即更好」的通用直觉存在张力：自一致性用 4 个独立样本、成本更高（TRAIL 上 Opus-4.8 \$6.52 vs Continual Search \$2.58；GPT-5.5 \$8.66 vs \$6.24），却在 Joint Accuracy 上回退（Opus-4.8 0.153→0.138，GPT-5.5 0.156→0.135）。异构裁判组（0.173 / 0.175）也显著低于 Continual Search（0.205 / 0.257）。这提示「独立重采样」与「顺序搜索」不是同一类算力，前者无法恢复遗漏证据。另一处张力在推理 effort：低 effort 在 TRAIL 上匹配甚至超过高/最高 effort，与「effort 越高越好」的常见默认相悖，但作者仅将其作为「搜索受限」的旁证，未做跨基准验证。

**可链接笔记 id**：`agentic-survey`、`swe-agent`、`tau-bench`、`gaia`、`long-horizon agent reliability and evaluation`。

## 复现与验证计划

目标：以最小成本验证核心主张 C1（长执行记录上 Continual Search 优于单轮与 Passive Continuation）与 C3（短轨迹上无一致增益甚至退化）。

环境与数据。使用工具型 agentic judge（论文用 Claude Agent SDK，只读访问评估记录，通过 Bash/Grep/Glob 按需检索，避免内联海量轨迹）。优先选 TRAIL（n=148，中位 100K token，430 KiB）与 AgentRx（n=29，中位 7.2K token，23.9 KiB）构成「长 vs 短」对照；若算力允许再加 TELBench（n=33，39K token）。MegaRCA-Mix（n=50，286K token，1.05 MiB）需自建标注，成本最高，建议后置。

基线与预算。三条件共享同一 turn 1 归因：Single-turn、Passive Continuation、Continual Search，最多 4 轮，保留各基准原生 schema 与原生指标（TRAIL 报 Joint Accuracy 与 Weighted F1）。可选加 Self-consistency（4 样本多数投票）作为「多算力是否等价」的对照。成本参照 Table 4：TRAIL 上 Opus-4.8 单轮 $1.21、Continual Search $2.58；GPT-5.5 单轮 $2.11、Continual Search $6.24。

判据。长轨迹上要求 Continual Search 在 Joint Accuracy 与 Weighted F1 上均高于 Passive 与 Single-turn；短轨迹上不要求增益，若出现下降即与 C3 一致。稳定性参照 Table 5：Opus-4.8 在 TRAIL 上四次独立运行，Continual Search 对 Passive 的绝对增益为 Joint Accuracy 0.037–0.055、Weighted F1 0.021–0.064，而单轮基线本身在 0.129–0.153 间波动——因此必须报告多次运行，单次差异小于该波动区间时不可下结论。

预期失败模式。其一，短轨迹上持续提示压力使裁判翻转向错误标签（GPT-5.5 在 AgentRx 0.345→0.241、Who&When 0.548→0.452）。其二，若裁判未真正读取新证据，去重 13-gram 观测 token 不增长，则增益可能只是上下文累积而非搜索。其三，标签噪声与分类法类别重叠会压低绝对分数，需与人工标注一致性一并报告。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| Root-Cause Attribution (RCA) | 根因归因：把结果级失败信号转为可操作诊断，定位首次偏离正确执行的根因，并归责到模型、harness、环境或评分器等组件 |
| Continual Search | 持续搜索：迭代多轮框架，每轮要求裁判挑战现有归因并检索此前未检查的证据 |
| Passive Continuation | 被动续接：对照条件，仅要求裁判重新考虑并确认现有结论，不要求检查新证据 |
| Agentic Judge | 智能体式裁判：具备工具调用能力、只读访问评估记录、按需检索证据的 LLM 裁判 |
| MegaRCA-Mix | 本文提出的长时程 RCA 基准，$n=50$，中位 286K token / 1.05 MiB，覆盖 29 个基准、7 个领域 |
| Interaction-Centric Taxonomy | 交互中心失败分类法，含 Instruction-Grader Mismatch、Service Failure、Stale State Delivery、Mistranslation 等基准侧缺陷类别 |
| Self-Consistency | 自一致性：同一模型独立采样多个归因并多数投票的基线（本文用 4 样本） |
| Heterogeneous Judge Panel | 异构裁判组：跨多个不同模型聚合预测的基线（GPT-5.5、Opus-4.7、Opus-4.8、Grok-4.6） |
| Deduplicated Observation Tokens | 去重观测 token：移除重复 13-gram 片段后累计的裁判读取 token，用于衡量新证据获取量 |
| Artifact Coverage | 工件覆盖率：裁判检查过的诊断证据（轨迹、环境配置、验证器输出、系统日志等）占全部工件的比例 |
| ABA (Automated Benchmark Analysis) | 专用基准审计基线，用严重度评分 rubric 评估任务 |

记号：$T1$–$T4$ 表示第 1 至第 4 轮续接归因；$n$ 为各基准人工标注的失败试验数；F1 为 MegaRCA-Mix 等基准的原生指标；Weighted F1 为 TRAIL 的加权 F1，惩罚未落地的错误类别预测；Joint Accuracy 为 TRAIL 的联合准确率，同时评估错误位置与类别。注意 TELBench、AgentRx、Who&When 使用各自原生指标，跨基准数值不可直接比较。

## 自测

以下问题用于检验你是否真正掌握了本文的论证结构，而非仅记住数字。答案中标注了「作者主张」与「已复现/共识」的区分。

**Q1.** 论文把 RCA 重新定义为「搜索问题」。若把 Continual Search 的增益简单归因于「多花了 4 倍推理算力」，你会用哪一组对照实验反驳？请给出具体数字。

<details><summary>答案</summary>
用自一致性基线反驳。TRAIL 上 Opus-4.8 自一致性（4 样本）Joint Accuracy 为 0.138、Weighted F1 为 0.430，均低于单轮基线（0.153 / 0.486），而成本为 $6.52，高于 Continual Search 的 $2.58。GPT-5.5 同样：自一致性 0.135 / 0.386，成本 $8.66，Continual Search 为 0.257 / 0.500，成本 $6.24。即「更多独立采样」既更贵又更差，说明增益来自跨轮的新证据获取而非算力堆叠（作者主张，§5.1 表 4）。辅助证据是去重 13-gram 观测 token：Continual Search 从 42K 增至 58K，Passive 仅到 48K。
</details>

**Q2.** 为什么 Continual Search 在 AgentRx 与 Who&When 上失效？请从证据空间规模与「认知不稳定」两个角度解释，并给出 GPT-5.5 的具体退化数字。

<details><summary>答案</summary>
两个基准的中位轨迹仅 7.2K 与 2.4K token（对比 MegaRCA-Mix 286K、TRAIL 100K、TELBench 39K），单轮归因已基本覆盖全部证据，后续轮次无新证据可搜。此时续接提示退化为纯对话压力，而既有文献表明持续施压会迫使裁判翻转判断、偏离真值。GPT-5.5 上 AgentRx 从 0.345 降至 0.241，Who&When 从 0.548 降至 0.452（作者主张，§4.3 表 3）。注意 Opus-4.8 在 AgentRx 上反而从 0.345 升至 0.414，但在 Who&When 上从 0.373 降至 0.325——即退化并非对所有模型一致，这一点在引用时需谨慎。
</details>

**Q3.（跨小节）** 论文声称「长时程 RCA 是搜索受限而非推理受限」。请用推理努力消融与证据覆盖率两条证据链支持该论断，并指出该论断的适用边界。

<details><summary>答案</summary>
证据链一（推理努力）：TRAIL 上 Opus-4.8 低 effort 在 turn 3 达到 0.533 Weighted F1，匹配 high effort，仅消耗约 62% 累计 token；Sonnet-5 低 effort 在 turn 4 取得最高 0.521，超过 high 与 max。即单轮内加大思考预算收益递减甚至反转。证据链二（证据覆盖）：工件级覆盖率从 turn 1 的 70.8% 升至 turn 3 的 94.6%、turn 4 的 97.4%，而 Passive Continuation 自 turn 2 起停在 77.0%。适用边界：该论断仅在证据空间足够大时成立；在 AgentRx / Who&When 上搜索已饱和，继续施压反而有害（§4.3）。此外作者承认轨迹部分不可见（专有模型不暴露 thinking token），结论应理解为「对可观测记录的归因」。
</details>

**Q4.（跨小节）** 表 2 与表 4 都报告 TRAIL 上 Opus-4.8 的 Weighted F1，但数值不同（0.539 vs 0.486 单轮）。这是矛盾吗？请说明应如何正确引用。

<details><summary>答案</summary>
不矛盾，但需注意口径。表 2 与表 4 的单轮 Opus-4.8 Weighted F1 均为 0.486、Continual Search 均为 0.539，二者一致；差异在于表 4 额外给出了 Joint Accuracy 与成本列，并引入了自一致性与裁判组基线。真正需要警惕的是跨运行波动：§A.2 报告四次独立运行中单轮基线在 0.129–0.153（Joint Accuracy）间浮动，Continual Search 相对 Passive 的绝对增益为 Joint Accuracy 0.037–0.055、Weighted F1 0.021–0.064，方向在四次运行中一致为正。因此引用时应给出区间而非单点，并说明增益幅度小于单轮基线自身的运行间波动范围。
</details>

**Q5.** 在基准诊断任务（§6）中，Continual Search 的增益「完全由 recall 驱动」。请给出 T1→T3 的 precision / recall / F1 变化，并解释为何这一分解对「分类器是否真的变强」这一判断很关键。

<details><summary>答案</summary>
Opus-4.8 分类器在 50 个 MegaRCA-Mix 试验上：T1 precision 1.00 / recall 0.09 / F1 0.16；T2 0.92 / 0.52 / 0.67；T3 0.93 / 0.61 / 0.74；T4 与 T3 持平。ABA 基线为 precision 0.51 / recall 0.83 / F1 0.63。关键在于：单轮时分类器 precision 极高但 recall 极低，说明它并非「判断不准」，而是「几乎不敢报」——漏掉了大量真实基准缺陷。Continual Search 通过逐轮检索被忽略的环境工件把 recall 拉起来，同时 precision 保持在 0.90 以上，因此 F1 的提升是真实的判别能力扩展，而非阈值移动带来的权衡。相较之下 ABA 靠高 recall、低 precision 换分，两者错误结构完全不同（作者主张，§6 图 8）。
</details>
