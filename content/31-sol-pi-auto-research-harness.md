---
id: sol-pi-auto-research-harness
title: SoL-Pi：递归扩展自动研究循环优化 Agent Harness
summary: 长时程智能体任务中，token 开销随交互历史与环境观察累积而成为系统级瓶颈。现有提效工作多聚焦更快注意力、量化或更便宜模型，而连接模型与环境的 agent harness 层优化虽无需额外训练，却因工具使用、上下文管理、验证、委派、恢复与终止高度耦合而难以人工迭代；
stage: FRONTIER
track: Agent 系统
kind: paper
depth: deep
evidenceGrade: C
order: 31
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.20519
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 5
full_text_url: https://arxiv.org/html/2609.20519
objectives: [理解 SoL-Pi 如何用递归自我改进式搜索在 harness 层自动发现可复用效率机制, 掌握 Action Fusion、Online Context Compact、ObservationPack、Evidence-Preserving Reducer 四类机制的作用与组合效果, 了解 held-out 验证与搜索反馈隔离的设计动机及其对跨模型迁移的意义, 能解读 EdgeBench、Terminal-Bench 4、IMO 2026 与 kernel-optimization 上的性能—成本权衡结果]
tags: [agent-harness, recursive-self-improvement, token-efficiency, context-management, automated-search, cross-model-transfer]
sources: [sol-pi-recursively-scaling-auto-research]
related: [modularrsi-harness, rrsi-regularized-harness-rsi, harness-design-coding-agents]
prerequisites: []
---
## 问题与语境

长时程智能体把 token 开销从「单次推理成本」变成了系统级瓶颈：交互历史与环境观察随步数累积，上下文规模与执行开销同步膨胀。论文把这一现象定位在 agent harness 层——即在模型与环境之间呈现状态、暴露动作、处理反馈的系统层。这一层的优化不需要额外训练，因而与更快注意力核、量化压缩、换用更便宜模型等基础设施与模型层路线正交，可叠加使用。

失效点在于 harness 的耦合性。工具使用、上下文管理、验证、委派、恢复与终止彼此纠缠，局部有利的改动可能把成本转移到执行后段，或引发下游失败。因此 harness 开发长期依赖人工检查长轨迹、归纳反复出现的失败模式、再翻译成代码改动，成本高且难以跨任务与环境扩展。

已有的自动化 harness 改进工作提供了可行性证据：Meta-Harness 搜索可执行 harness 程序并评估其向留出数据集与模型的迁移；Recursive Harness Self-Improvement 针对单个任务精炼 agent loop 的 prompt 级规范。但论文引用的 Wang et al. 研究指出，演化出的 harness 可能过拟合搜索期任务，在未见任务上增益有限。这构成本文的直接动机：把搜索反馈与最终评估严格隔离。

论文的定位不是「再提一个 harness 技巧」，而是把 harness 效率机制的发现建模为受能力约束的 RSI 式自动研究搜索，并用宽到深漏斗在约 150 个方向与约 500 个可执行环境上扩展搜索规模。需要说明的是，作者明确声明这些计数只描述搜索范围，不构成 scaling law。

## 核心主张

论文的核心主张可归纳为：在保持底层模型固定的前提下，对 harness 机制层做 RSI 式自动搜索，能发现可跨任务、跨模型迁移的效率机制，且这些机制在留出评估上不牺牲（或仅小幅牺牲）任务表现。搜索最终保留四个机制：Action Fusion、Online Context Compact、ObservationPack、Evidence-Preserving Reducer，分别作用于动作执行、上下文管理、观察存储与委派阅读。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | 完整栈在 EdgeBench 上比 Pi 减少 49.0% token 流量，保留 93.7% 平均分（1.10 B vs 2.15 B；42.0 vs 44.8），token 成本低 33.2% | §3.1 表 1；§3.1 正文 | 作者主张 |
| C2 | 在未参与搜索的 Opus 5 上，完整栈减少 44.7% token 流量、33.5% API 成本，保留 94.3% 平均分 | §3.1 表 2 Opus 5 区块 | 作者主张 |
| C3 | Terminal-Bench 4 上 SoL-Pi 解出 15/63 题，总成本比 Pi 低 26.3%（$211.12 vs $286.45），单题成本低 11.6%（$14.07 vs $15.91） | §3.2 表 3 | 作者主张 |
| C4 | 四个机制各自单独加入 Pi 后，在 GPT-5.6 Sol 与 Opus 5 两种后端下均降低总 token 数 | §3.4 表 4 单组件评估 | 作者主张 |
| C5 | 完整栈在 EdgeBench 上减少 44.7–49.0% token 流量、约三分之一 token 成本，性能可比；最佳候选提升模型表现 5.3–12.8%、token 效率 9.8–18.2% | §5 结论；§1 引言 | 作者主张 |

最强的是 C4：它是表 4 中逐组件、双后端的加一评估，方向一致（每个组件都降低总 token 数），且不依赖跨模型迁移这一更弱的环节。C1 与 C2 的机制相同但后端不同，C2 是迁移证据，作者自己限定为「preliminary evidence of transfer to an unseen LLM backend」。

最弱的是 C3 所代表的性能类主张：SoL-Pi 在 Terminal-Bench 4 上只解出 15 题，低于 Codex 与 Pi 的 18 题，成本优势部分来自解得更少；IMO 2026 上 SoL-Pi 与 Pi 同为 3/6，低于 Codex 的 5/6。因此「效率提升」在这些基准上伴随任务完成量的下降，不能读作全面占优。此外，作者声明搜索规模计数不构成 scaling law，机制交互效应也未被隔离（各配置在自身触发子集上比较），这两点限制了主张的可迁移强度。

## 机制与方法

SoL-Pi 把 harness 改进建模为**受能力约束的 RSI 式自动研究搜索**：研究智能体读取基础 harness（Pi）的执行轨迹，定位可避免的开销，生成候选机制假设，在开发环境中实现并测试，最终只保留能跨环境迁移的效率机制。底层模型固定不变，搜索对象是模型与环境之间的系统层。

**搜索结构（broad-to-deep funnel）。** 外层在六个提案族（context、progress、tools、delegation、prompt and policy、improvement and evaluation）中展开 152 个方向；每个方向必须指出具体开销来源并提出 harness 改动。内层把每个方向实现为一个**可丢弃的隔离谱系**：复制共享技能模板、设定参数、跑完固定实验后保留候选与证据、丢弃编排代码。谱系之间不耦合失败，因此搜索宽度来自并行启动更多隔离循环，深度来自单循环内的反复精化（Ralph Loop：实现者按显式完成标准迭代，独立评审者检查，评审失败触发修订）。独立分析器各查一条轨迹（重复动作、上下文增长、大观察、稀疏诊断信号），reducer 汇总为候选级摘要指导下一轮提案。

**双门控选择。** 在实验开始前固定能力指标、容差与效率指标，且这些量对优化智能体不可控，以防其博弈接受准则。候选须顺序通过两道门：

$$
\text{accept}(c) \iff \bigl(\forall m \in \mathcal{C}:\ |m(c)-m(\text{Pi})| \le \tau_m\bigr) \ \wedge\ \bigl(\exists e \in \mathcal{E}:\ e(c) \succ e(\text{Pi})\bigr)
$$

其中 $\mathcal{C}$ 为能力指标集、$\tau_m$ 为预先声明的容差、$\mathcal{E}$ 为声明的效率指标集。通过者之间保留帕累托非支配结果。符号上，token traffic（B）为记录的总 token 流量（十亿），token efficiency（$/score）为每单位聚合任务得分对应的 API 成本，trigger rate 为机制被激活的任务比例，trigger intensity 为每个被触发任务的平均激活次数。

**保留的四个机制**分别作用于 agent–环境循环的不同位置：Action Fusion 把一次文件变更与其后续命令合并为一个请求，API 调用从三次降到两次；Online Context Compact 在子任务完成时评估压缩，仅当预计节省超过重写成本时执行；ObservationPack 对大结果前两次请求完整发送，之后替换为稳定句柄与 1 KB 摘录，原始分块可按需精确取回；Evidence-Preserving Reducer 用低成本模型压缩结果，经确定性验证，失败则回退原始内容。

**设计取舍与适用前提。** 关键取舍是**搜索反馈与最终评估严格隔离**：机制冻结后才在留出的 EdgeBench 上做单向验证，验证失败即拒绝且不触发进一步优化——这是针对「演化 harness 在留出任务上过拟合」风险的直接设计回应。适用前提包括：需要可自动评估的执行环境（本文为 535 个：495 个 GitHub issue–PR 任务 + 40 个合成任务）；能力容差与效率指标须在搜索前声明；机制以 Pi 扩展形式实现，迁移到其他 harness 需重新验证。作者明确说明，方向数、环境数、运行数等计数只描述搜索规模，**不构成 scaling law**（作者主张）。

## 实验设置

评估覆盖四个基准：EdgeBench、Terminal-Bench 4、IMO 2026 与一个 kernel-optimization 基准。EdgeBench 公开 51 题，其中 11 题用于冻结候选的单向接受，其余 40 题留作泛化性最终评估；官方 GPT-5.5 @2h 的 31.2 分为不计排名的纯分数参考。所有 token 成本使用 2026 年 8 月 17 日的 API 价格。Terminal-Bench 4 因基础设施限制排除了依赖 GPU 的任务；IMO 2026 每题设 150 分钟上限以限制无产出的循环，成本包含该预算内的全部模型活动。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| EdgeBench（51 公开题；11 接受 / 40 留出） | GPT-5.6 Sol（搜索后端） | Pi；另列 Codex、OpenSquilla、Oh-My-Pi、OpenCode、Oh-My-Opencode | 未说明 | Recorded Token Traffic (B)、Token Cost ($)、Avg. Score、Token Eff. ($/score) |
| EdgeBench（同上） | Opus 5（留出后端，不再搜索或适配） | Pi；另列 Claude Code | 未说明 | 同上 |
| Terminal-Bench 4 | GPT-5.6 Sol | Codex、Pi | 63 个 CPU-only 任务 | Solved Tasks (out of 63)、Total Model Cost ($)、Cost / Solved Task ($) |
| IMO 2026 | GPT-5.6 Sol (xhigh)，Lean 4 形式化验证 | Codex、Pi | 6 题，每题 150 分钟上限 | Pass (out of 6)、Total Model Cost ($)、Cost / Passed Problem ($) |
| kernel-optimization | 协调者 GPT-5.6 Sol (xhigh)，worker GPT-5.6 Luna (xhigh) | 单 Codex agent；Codex 协调者 + 20 个 Pi baseline worker | 每次两小时，同一冻结 starter（需 147,734 cycles） | cycles、API cost |

SoL-Pi 报告两个操作点：**[Efficiency]** 为固定的四机制完整栈，**[Performance]** 为各后端在单机制评估中平均分最高的配置（GPT-5.6 Sol 下为 ObservationPack，Opus 5 下为 Action Fusion）。单机制贡献通过 add-one 评估（Table 4）给出，机制组合效应见 Figure 7；作者指出，在各配置自身的触发任务子集上比较**不能隔离交互效应**（作者主张）。搜索规模为 152 个提案方向、535 个可执行环境、超过 3,000 次运行与超过 60,000 次 agent–环境交互，作者声明这些计数只描述搜索范围，不建立 scaling law。

## 证据与结果

本节汇总摘录中可核对的数字。所有数值均照抄原文，未在摘录中出现的量一律标注「摘录未给出」。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Recorded Token Traffic (B) total | 1.0990 | SoL-Pi [Efficiency], GPT-5.6 Sol, EdgeBench | Table 1 |
| Token Cost ($) | 894 | SoL-Pi [Efficiency], GPT-5.6 Sol, EdgeBench | Table 1 |
| Avg. Score | 42.003 | SoL-Pi [Efficiency], GPT-5.6 Sol, EdgeBench | Table 1 |
| Token Eff. ($/score) | 0.4174 | SoL-Pi [Efficiency], GPT-5.6 Sol, EdgeBench | Table 1 |
| Recorded Token Traffic (B) total | 2.1538 | Pi, GPT-5.6 Sol, EdgeBench | Table 1 |
| Token Cost ($) | 1,339 | Pi, GPT-5.6 Sol, EdgeBench | Table 1 |
| Avg. Score | 44.833 | Pi, GPT-5.6 Sol, EdgeBench | Table 1 |
| Token Eff. ($/score) | 0.5855 | Pi, GPT-5.6 Sol, EdgeBench | Table 1 |
| Recorded Token Traffic (B) total | 2.0224 | SoL-Pi [Performance], GPT-5.6 Sol, EdgeBench | Table 1 |
| Token Cost ($) | 1,271 | SoL-Pi [Performance], GPT-5.6 Sol, EdgeBench | Table 1 |
| Avg. Score | 47.208 | SoL-Pi [Performance], GPT-5.6 Sol, EdgeBench | Table 1 |
| Token Eff. ($/score) | 0.5280 | SoL-Pi [Performance], GPT-5.6 Sol, EdgeBench | Table 1 |
| Recorded Token Traffic (B) total | 1.3101 | SoL-Pi [Efficiency], Opus 5, EdgeBench | Table 2 |
| Token Cost ($) | 1,158 | SoL-Pi [Efficiency], Opus 5, EdgeBench | Table 2 |
| Avg. Score | 42.224 | SoL-Pi [Efficiency], Opus 5, EdgeBench | Table 2 |
| Token Eff. ($/score) | 0.5376 | SoL-Pi [Efficiency], Opus 5, EdgeBench | Table 2 |
| Recorded Token Traffic (B) total | 2.3697 | Pi, Opus 5, EdgeBench | Table 2 |
| Token Cost ($) | 1,741 | Pi, Opus 5, EdgeBench | Table 2 |
| Avg. Score | 44.756 | Pi, Opus 5, EdgeBench | Table 2 |
| Token Eff. ($/score) | 0.7625 | Pi, Opus 5, EdgeBench | Table 2 |
| Recorded Token Traffic (B) total | 2.1016 | SoL-Pi [Performance], Opus 5, EdgeBench | Table 2 |
| Token Cost ($) | 1,605 | SoL-Pi [Performance], Opus 5, EdgeBench | Table 2 |
| Avg. Score | 50.482 | SoL-Pi [Performance], Opus 5, EdgeBench | Table 2 |
| Token Eff. ($/score) | 0.6235 | SoL-Pi [Performance], Opus 5, EdgeBench | Table 2 |
| Solved Tasks (out of 63) | 15 | SoL-Pi, Terminal-Bench 4 | Table 3 |
| Total Model Cost ($) | 211.12 | SoL-Pi, Terminal-Bench 4 | Table 3 |
| Cost / Solved Task ($) | 14.07 | SoL-Pi, Terminal-Bench 4 | Table 3 |
| Solved Tasks (out of 63) | 18 | Pi, Terminal-Bench 4 | Table 3 |
| Total Model Cost ($) | 286.45 | Pi, Terminal-Bench 4 | Table 3 |
| Cost / Solved Task ($) | 15.91 | Pi, Terminal-Bench 4 | Table 3 |
| Solved Tasks (out of 63) | 18 | Codex, Terminal-Bench 4 | Table 3 |
| Total Model Cost ($) | 272.35 | Codex, Terminal-Bench 4 | Table 3 |
| Cost / Solved Task ($) | 15.13 | Codex, Terminal-Bench 4 | Table 3 |
| Pass (out of 6) | 3 | SoL-Pi, IMO 2026 | Table 3 |
| Total Model Cost ($) | 62.69 | SoL-Pi, IMO 2026 | Table 3 |
| Cost / Passed Problem ($) | 20.90 | SoL-Pi, IMO 2026 | Table 3 |
| Pass (out of 6) | 5 | Codex, IMO 2026 | Table 3 |
| Total Model Cost ($) | 114.47 | Codex, IMO 2026 | Table 3 |
| Cost / Passed Problem ($) | 22.89 | Codex, IMO 2026 | Table 3 |
| Pass (out of 6) | 3 | Pi, IMO 2026 | Table 3 |
| Total Model Cost ($) | 75.95 | Pi, IMO 2026 | Table 3 |
| Cost / Passed Problem ($) | 25.32 | Pi, IMO 2026 | Table 3 |
| cycles | 1,127 | SoL-Pi swarm, kernel-optimization, two-hour run | Figure 5(b) |
| API cost ($) | 60.11 | SoL-Pi swarm, kernel-optimization, two-hour run | Figure 5(b) |
| cycles | 1,333 | single agent, kernel-optimization, two-hour run | Figure 5(b) |
| API cost ($) | 39.20 | single agent, kernel-optimization, two-hour run | Figure 5(b) |
| cycles | 1,366 | Pi baseline swarm, kernel-optimization, two-hour run | Figure 5(b) |
| API cost ($) | 82.12 | Pi baseline swarm, kernel-optimization, two-hour run | Figure 5(b) |
| starter cycles | 147,734 | kernel-optimization frozen starter | §3.3 |
| proposed directions | 152 | outer search proposal families | §2.2 |
| executable environments | 535 | search set (495 repository tasks + 40 synthetic tasks) | §2.3 |
| runs | more than 3,000 | overall search scale | §1 |
| agent–environment interactions | more than 60,000 | overall search scale | §1 |
| EdgeBench public tasks | 51 | 11 for one-way acceptance, 40 reserved for final evaluation | §2.5 |
| projected token reduction under full triggering | 11.5% | Action Fusion oracle analysis | §3.5 |
| recorded iterations | 27 | Action Fusion lineage across four stages | §3.5 |
| prompt-optimization explorations | 18 | Action Fusion Stage 03 | Figure 8 |
| retained steps | ten | Action Fusion panels (b)–(c) | Figure 8 |
| API calls reduced | from three to two | Action Fusion | Figure 4(a) |
| ObservationPack excerpt size | 1 KB | after first two provider requests | Figure 4(c) |
| model performance improvement | 5.3–12.8% | best-performing candidates on EdgeBench | §5 |
| token efficiency improvement | 9.8–18.2% | best-performing candidates on EdgeBench | §5 |
| token traffic reduction | 44.7–49.0% | complete stack on EdgeBench | §5 |
| token cost reduction | about one third | complete stack on EdgeBench | §5 |
| EdgeBench official GPT-5.5 @2h score | 31.2 | unranked score-only reference | Table 1 |

消融与对照。Table 4 为 add-one 评估：把四个机制各自单独加入 Pi，在 GPT-5.6 Sol 与 Opus 5 两种后端下均降低总 token 数。GPT-5.6 Sol 下 ObservationPack 取得单机制最高平均分（47.208），Opus 5 下为 Action Fusion（50.482）。完整栈（SoL-Pi [Efficiency]）在两个后端区块中总 token 数与 token 成本最低（GPT-5.6 Sol：1.0990 B / $894；Opus 5：1.3101 B / $1,158）。机制激活随后端变化：Opus 5 下 trigger rate 与 trigger intensity 均更低，作者推测与「harness 仅在 GPT-5.6 Sol 轨迹上优化」有关。Figure 7 显示 ObservationPack 在完整栈中变得更选择性，可能与 Evidence-Preserving Reducer 在观察密集轨迹上的重叠有关；每个机制在完整栈中的 token 效率增益大于其单独配置，作者称这与互补性一致，但明确说明「在各配置自身触发任务子集上的比较不能隔离交互效应」。对照基线包括 Codex、Pi、Claude Code、OpenSquilla、Oh-My-Pi、OpenCode、Oh-My-Opencode；EdgeBench 官方 GPT-5.5 @2h（31.2）为不计排名的仅分数参考。Terminal-Bench 4 与 IMO 2026 的样本量、方差、重复次数与显著性检验：摘录未给出。kernel-optimization 的重复运行次数与随机种子：摘录未给出。

## 证据强度评估

证据分级：B（中等偏弱）。理由：结论有明确的对照基线（Pi、Codex、Claude Code 等）、两个后端区块、add-one 消融与留出验证流程，且数字可逐项核对；但缺少统计显著性检验、重复次数与方差报告，主要证据来自作者自建/自选的评测点，且部分关键结论（跨后端迁移）作者自述仅为「preliminary evidence」。因此不足以支撑 A 级，也不宜降为 C——消融与留出设计本身具备可检验结构。

主要威胁：

1. 构造效度（指标定义与成本口径）。Token efficiency 定义为「每单位聚合任务得分对应的 API 成本」，其分母是聚合分数，聚合方式摘录未给出。Online Context Compact 的门控「从上下文大小与 cache-write/read 价格比估计 cache-rewrite 开销；它不单独为 summarization call 计价」——这意味着该机制的成本被系统性低估，可能夸大其净收益。此外所有 token 成本使用「截至 2026 年 8 月 17 日的 API 价格」，价格变动会使 $/score 类结论不可直接迁移。

2. 外部效度（迁移与任务覆盖）。跨后端迁移只在 Opus 5 上验证一次，作者自述为「preliminary evidence of transfer to an unseen LLM backend」，并强调「仅在所评估设定内展示强跨模型泛化」。Terminal-Bench 4 排除了依赖 GPU 的任务（基础设施限制），因此结论不覆盖 GPU 相关任务。IMO 2026 仅 6 题、每题 150 分钟上限，样本极小。kernel-optimization 为单次两小时运行，无重复。

3. 统计显著性与基线选择。所有报告为点估计，摘录未给出置信区间、方差或显著性检验；EdgeBench 上 SoL-Pi [Efficiency] 的平均分低于 Pi（42.003 vs 44.833；Opus 5 上 42.224 vs 44.756），即效率点以分数下降换取 token 下降，二者权衡的稳健性无法从点估计判断。Terminal-Bench 4 上 SoL-Pi 解出 15/63，低于 Pi 与 Codex 的 18/63，作者以成本更低作为解释，但解题数下降本身是能力代价。基线 Pi 为作者自建/自选 harness，其调优程度未在摘录中说明。

4. 评测污染与搜索规模解释。搜索使用 535 个可执行环境（495 仓库任务 + 40 合成任务），EdgeBench 51 个公开任务中 11 个用于单向接受、40 个留出；留出结果不回流搜索，这一隔离设计降低了污染风险，但作者同时声明「这些计数描述搜索范围，不构成 scaling law」。此外，各配置在自身触发任务子集上的比较「不能隔离交互效应」，因此四机制的互补性主张属于作者主张而非已确立结论。作者亦承认「完整栈在 GPT-5.6 Sol 与 Opus 5 上的一致结果仅在所评估设定内展示强跨模型泛化」。

## 边界与反例

**什么观察会推翻结论。** 核心结论是「harness 层机制可跨任务与跨模型迁移地降低 token 流量」。若在留出任务上复现时出现以下任一情况，结论即被推翻或大幅削弱：(1) 在未参与搜索的第三方 benchmark 上，token 流量下降幅度显著小于 44.7–49.0%，或平均分跌破能力容差；(2) 换一个未参与搜索的 LLM 后端后，机制触发率与触发强度进一步下降至接近零，使「效率增益」退化为「机制不激活」；(3) 增益主要来自 API 价格结构（cache 读/写价差）而非交互结构本身——注意 Table 1/2 中 SoL-Pi [Efficiency] 的 Cache W. 从 Pi 的 0.0141 B 升到 0.0316 B（GPT-5.6 Sol），说明压缩本身引入了额外写入成本，若价格比变化，净收益可能反转。

**最可能失效的条件。** 作者自述机制「exclusively on GPT-5.6 Sol trajectories」上优化，Opus 5 上触发率与触发强度均更低，因此跨模型迁移目前只是初步证据（作者标注为 preliminary evidence）。此外，Online Context Compact 的门控只按上下文大小与 cache 写/读价格比估算重写开销，**不单独计价摘要调用**，在摘要成本高或上下文短的任务上该门控会系统性高估收益。Terminal-Bench 4 排除了 GPU 依赖任务，IMO 2026 每题 150 分钟上限，二者都改变了任务分布。

**读者可能误推的方向。** 第一，把「3,000+ runs、60,000+ 交互、152 方向、535 环境」当作 scaling law 证据——作者明确声明这些计数只描述搜索规模，不构成 scaling law（作者主张）。第二，把 Terminal-Bench 4 的 15/63 解出率读成能力提升：SoL-Pi 解出 15 题，少于 Pi 与 Codex 的 18 题，其优势仅在成本（$211.12 vs $286.45，单题 $14.07 vs $15.91），是效率—能力权衡而非全面胜出。第三，把 kernel-optimization 的 1,127 cycles 读成最优：单 agent 为 1,333 cycles 但成本仅 $39.20，是三者中最便宜，SoL-Pi swarm 的 26.8% 成本降幅只相对于 Pi baseline swarm。第四，把 add-one 结果当作机制可加性证明——作者指出各配置在各自触发子集上的比较无法隔离交互效应。

## 与知识库的关系

**新增。** 相对 Meta-Harness（可执行 harness 程序搜索，维护任务性能—上下文成本 Pareto 前沿），SoL-Pi 新增的是「搜索反馈与留出验证的严格隔离」这一协议，以及在此协议下报告的可迁移效率数字（token traffic 降 44.7–49.0%，跨 GPT-5.6 Sol → Opus 5）。相对 RHI（针对单任务精炼 prompt 级 agent loop 规范），新增的是跨约 150 方向、约 500 环境的可复用机制搜索，而非单任务规范精炼。相对 Darwin Gödel Machine / Hyperagents（修改 agent 代码或元级改进过程），SoL-Pi 在固定底层模型前提下把 RSI 式搜索限制在 harness 机制层。相对 SWE-agent 的 agent–computer 接口结论，本文把该观点扩展到 token 效率维度，并给出四个具体机制（Action Fusion、Online Context Compact、ObservationPack、Evidence-Preserving Reducer）。相对 AgentDiet、ACON、Context-Folding、AgentFold、Context as a Tool、ACE 等上下文控制工作，新增的是跨多个 harness 组件的自动发现与选择，而非单一上下文压缩机制。

**印证。** 与 Wang et al. 关于演化 harness 在留出任务上过拟合、增益有限的研究一致：本文据此把搜索反馈与最终评估分离，并以 Opus 5 上「保留 94.3% 平均分、降 44.7% token traffic」作为可迁移性的初步证据（作者主张，非已复现）。与 AHE 的迁移关切一致，但选择规则不同：SoL-Pi 用 capability-constrained 双门控（能力指标须在预设容差内且至少改善一项效率指标）并保留非支配结果。

**张力。** 与 Meta-Harness 的 Pareto 前沿目标存在张力：SoL-Pi 的完整栈在 EdgeBench 上平均分低于 Pi（42.003 vs 44.833），即效率点并非性能点，其「性能点」是单机制配置（GPT-5.6 Sol 下为 ObservationPack，47.208；Opus 5 下为 Action Fusion，50.482），二者不可同时取得。与「更多机制组合必然更好」的直觉也存在张力：ObservationPack 在完整栈中变得更选择性，作者推测是与 Evidence-Preserving Reducer 在观察密集轨迹上重叠所致，但未隔离交互效应。

**可链接笔记 id。** `meta-harness`、`rhi-recursive-harness-self-improvement`、`wang-et-al-harness-overfitting`、`swe-agent-aci`、`context-efficient-agents`（AgentDiet / ACON / Context-Folding / AgentFold / Context-as-a-Tool / ACE）、`darwin-godel-machine`、`hyperagents`、`ahe-modular-harness-evolution`。

## 复现与验证计划

最小可执行验证的目标不是复现全部搜索（约 150 个方向、约 500 个环境、超过 3,000 次运行、超过 60,000 次 agent–environment 交互），而是验证「四个机制冻结后是否在留出任务上同时保分与省 token」这一可迁移性主张。

环境与数据：以 Pi 为基线 harness，在其上分别实现 Action Fusion、Online Context Compact、ObservationPack、Evidence-Preserving Reducer 四个机制（实现细节见 §2.5）。评测集用 EdgeBench 公开的 51 个任务，其中 11 个用于单向接受、40 个留出做最终泛化评估（§2.5）。若无法获得 EdgeBench，退而用 Terminal-Bench 4 的 63 个 CPU-only 任务做方向性检查，但注意该基准上 SoL-Pi 解出 15/63，低于 Pi 与 Codex 的 18/63，因此它只能验证成本侧、不能验证保分侧。

基线与预算：基线为 Pi；两个操作点分别为 SoL-Pi [Efficiency]（四机制完整栈）与 SoL-Pi [Performance]（各后端平均分最高的单机制配置，GPT-5.6 Sol 下为 ObservationPack，Opus 5 下为 Action Fusion）。成本口径统一为 API 成本，并注明价格时点（论文使用 2026 年 8 月 17 日价格）。

判据：完整栈在留出任务上应满足 (i) 平均分不低于 Pi 的约 93.7%（GPT-5.6 Sol）或 94.3%（Opus 5）；(ii) 记录 token 流量下降 44.7–49.0%；(iii) token 成本下降约三分之一。单机制层面应复现「每个组件在两种后端下都降低总 token 数」。

预期失败模式：一是机制触发率与触发强度在非搜索后端上偏低（论文观察到 Opus 5 上两者均更低，可能因 harness 仅在 GPT-5.6 Sol 轨迹上优化），导致省 token 效果缩水；二是 ObservationPack 与 Evidence-Preserving Reducer 在观察密集轨迹上重叠，使完整栈中 ObservationPack 变得更选择性，单机制增益不可线性相加；三是 Online Context Compact 的门控只按上下文规模与 cache 写读价格比估算重写开销，未单独计价摘要调用，实际节省可能被高估。需注意：论文自身的 add-one 与组合比较均在各自触发任务子集上进行，不能隔离交互效应，因此复现时应把「机制互补」视为待检验假设而非既定结论。

## 术语与记号

本节的记号沿用论文口径：token 流量以十亿（B）为单位，成本以美元计，token 效率定义为每单位聚合任务得分对应的 API 成本（$ / score），数值越低越好。需要区分两类「效率」表述：论文正文的 token 效率改进百分比（9.8–18.2%）与表中 Token Eff. 列的绝对数值（如 0.4174），二者不可混用。

| 术语 | 含义 |
| --- | --- |
| agent harness | 智能体框架：在模型与环境之间呈现状态、暴露动作并处理反馈的系统层 |
| recursive self-improvement (RSI) | 递归自我改进：系统迭代改进自身组件或流程的能力 |
| Action Fusion | 动作融合：把一次文件变更与其后续命令合并为一个请求，减少 API 调用（由三次降为两次） |
| Online Context Compact | 在线上下文压缩：在子任务完成时评估压缩，仅当预计节省超过重写成本时执行 |
| ObservationPack | 观察打包：大结果前两次请求完整发送，之后替换为稳定句柄与 1 KB 摘录，原始分块可按需精确取回 |
| Evidence-Preserving Reducer | 证据保留归约器：用低成本模型压缩结果，经确定性验证，失败则回退到原始内容 |
| held-out validation | 留出验证：候选冻结后才在未参与搜索的任务上评估，结果不回流搜索 |
| broad-to-deep funnel | 宽到深漏斗：外层广探索假设、内层对候选反复实现与加固的搜索结构 |
| Oracle Analysis | 预言机分析：在分配 rollout 预算前检查已有轨迹以定位可避免开销的步骤 |
| Ralph Loop | Ralph 循环：实现者按明确完成标准迭代精化候选、由独立评审者检查的迭代实现循环 |
| token traffic (B) | 记录的总 token 流量，单位十亿 |
| token efficiency ($/score) | 每单位聚合任务得分对应的 API 成本 |
| trigger rate | 机制在任务上被激活的任务比例 |
| trigger intensity | 每个被触发任务的平均激活次数 |
| Pi | 本文的基线 harness，四个机制均作为其扩展实现 |
| SoL-Pi [Efficiency] | 固定四机制完整栈，面向 token 效率的操作点 |
| SoL-Pi [Performance] | 各后端平均分最高的单机制配置（GPT-5.6 Sol 为 ObservationPack，Opus 5 为 Action Fusion） |

需注意，论文中「约 150 个方向」「约 500 个环境」「超过 3,000 次运行」「超过 60,000 次交互」等计数仅描述搜索规模，作者明确说明这些计数不构成 scaling law。

## 自测

以下问题用于检验你是否真正读懂了本档案的证据边界，而非记住结论数字。答案折叠在每题下方。

**Q1（证据强度）** 论文报告搜索规模为「more than 3,000 runs」「more than 60,000 agent–environment interactions」「152 proposed directions」「535 executable environments」。这些数字能支持「搜索规模越大、机制质量越高」这一推论吗？

<details><summary>答案</summary>
不能。原文明确写道「These counts describe the scope of our search; they do not establish a scaling law.」档案 limits 亦收录该条。这些数字只描述搜索覆盖面，不构成规模—收益的因果或单调关系证据。任何把 152/535/3000 当作 scaling 论据的引用都是过度解读。
</details>

**Q2（跨小节推理：机制归因）** 表 4 显示，在 GPT-5.6 Sol 下单独加入 ObservationPack 得到平均分 47.208（高于完整栈的 42.003），而完整栈的 token 总量最低（1.0990 B）。若有人据此声称「完整栈的分数损失来自机制间负交互」，这个说法在本文证据下成立吗？

<details><summary>答案</summary>
不成立，至少是未证。档案 limits 明确：「Comparisons on each configuration's own triggered-task subset do not isolate interaction effects.」Figure 7 的对比是在各配置各自的 triggered-task 子集上做的，因此无法分离交互效应。此外 SoL-Pi [Efficiency] 与 SoL-Pi [Performance] 是两个不同的操作点（前者为固定四机制栈，后者为各后端平均分最高的单机制配置），二者分数差异不能直接读作机制冲突。作者仅提出 ObservationPack 在完整栈中「more selective」的推测性解释（可能与 Evidence-Preserving Reducer 在观察密集轨迹上重叠），用词为 potentially。
</details>

**Q3（跨小节推理：迁移证据的边界）** 论文在 Opus 5 上报告保留 94.3% 平均分、降低 44.7% token 流量。结合 §3.4 的激活模式，这条迁移证据的强度应如何定性？

<details><summary>答案</summary>
应定性为「初步证据」，且是作者主张而非已复现。理由有三：(1) 档案 limits 写明「Transfer results to Opus 5 provide only preliminary evidence of transfer to an unseen LLM backend.」；(2) 机制在 Opus 5 上的 trigger rate 与 trigger intensity 均低于 GPT-5.6 Sol，作者推测原因是 harness 仅在 GPT-5.6 Sol 轨迹上优化——即迁移后机制的实际工作方式已发生变化；(3) 完整栈在 Opus 5 上的平均分 42.224 低于 Pi 的 44.756，属「以分换效率」的权衡点，而非全面占优。因此可迁移性结论限于「在本文评估设定内」。
</details>

**Q4（指标口径）** 档案中 token efficiency 记为「$/score」，而表 1 中 SoL-Pi [Efficiency] 的 0.4174 低于 Pi 的 0.5855。这个指标下降是否等价于「每单位得分更便宜」？使用时需注意什么？

<details><summary>答案</summary>
按档案给出的定义，token efficiency 是「每单位聚合任务得分对应的 API 成本」，数值越低越好，因此 0.4174 相对 0.5855 表示单位得分的 API 成本更低。但需注意两点：(1) 该指标同时受分子（成本）与分母（分数）影响，SoL-Pi [Efficiency] 的分数本身低于 Pi（42.003 vs 44.833），因此效率改善部分来自分数下降而非纯成本节省；(2) 表注说明「API prices change over time; all token costs in this paper use the API prices as of August 17, 2026」，跨时间或跨供应商比价时该口径不可直接搬运。
</details>

**Q5（结论可迁移性）** 若你想把「Action Fusion 减少 API 调用」这一机制搬到自己的 agent 上，本文提供了哪些可直接复用的信息，哪些必须自行验证？

<details><summary>答案</summary>
可直接复用的：机制定义（把一次文件变更与其后续命令合并为一个请求，API 调用从三次降到两次，见 Figure 4(a)）；发现路径（oracle analysis 识别重复相邻动作，投影 full triggering 下 11.5% token 减少，随后经 27 次迭代、四阶段——oracle analysis、baseline construction、prompt 与 tool-schema 优化、final held-out validation）；以及一条工程教训：prompt-only triggering 不可靠，需扩展 tool schema 直接暴露融合动作，并引入 trigger rate 作为中间接受指标。必须自行验证的：该 11.5% 是 oracle 投影而非实测端到端收益；表 4 中 Action Fusion 单加在 GPT-5.6 Sol 下 token 总量 1.8968 B、平均分 46.664，在 Opus 5 下 2.1016 B、50.482，说明收益随后端变化；且你的工具 schema 与调用模式未必存在同样的相邻动作冗余。
</details>
