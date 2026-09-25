---
id: modularrsi-harness
title: ModularRSI：模块化可泛化的 Harness 自进化
summary: CLI agent 的效能日益依赖 harness（执行、工具交互、上下文管理、环境反馈），但 harness 的递归自改进（RSI）难以泛化：任务级结果只提供粗粒度监督，存在数据级（缺乏高质量可执行长程任务）、轨迹级（单侧轨迹混淆系统性缺陷与任务细节）、机制级（难以定位应修改哪
stage: FRONTIER
track: Agent 系统
kind: paper
depth: deep
evidenceGrade: C
order: 25
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.14857
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.14857
objectives: [理解 ModularRSI 如何将 harness 拆分为可独立进化的模块并整合, 掌握模块化进化相比联合/非模块化进化的优势与消融证据, 了解进化数据难度分布与对比样本对 harness 自进化的影响, 评估 harness 进化在跨模型与跨域上的泛化能力]
tags: [harness-evolution, modular-rsi, agent-harness, self-improvement, terminal-bench, swe-bench]
sources: [modularrsi-modular-and-generalizable-rec]
related: [rrsi-regularized-harness-rsi, harness-design-coding-agents, sol-pi-auto-research-harness]
prerequisites: []
---
## 问题与语境

CLI agent 的能力越来越不只取决于基础模型，还取决于 harness——即支配执行流程、工具交互、上下文管理与环境反馈的那层框架。因此一个自然的想法是让 harness 自身做递归自改进（RSI）：从执行经验中迭代修正自己的机制。问题在于，这类改进很难证明是「可迁移的」，因为任务级成败只提供粗粒度监督。

论文把失效点拆成三重耦合的挑战。数据级：harness RSI 需要可靠环境与正确性反馈的长程可执行任务，规模化构造代价高，于是现有方法（如 AHE、Meta-Harness）常直接使用下游基准数据做进化，导致无法区分「可迁移改进」与「基准特定适配」。轨迹级：单条或单侧轨迹把系统性 harness 缺陷与任务特定的推理、解法细节纠缠在一起，直接据此优化会引入迁移性差的局部行为。机制级：即便识别出反复出现的缺陷，也不清楚该改哪个 harness 组件；不少方法仍整体重写 harness，修改空间过大，使不相关机制互相纠缠。

论文的定位不是提出又一个整体式 harness 进化器，而是把信用分配问题显式化：用同任务成败轨迹对比 + 跨任务证据聚合，把粗粒度任务结果转成局部化的函数级信号；再把 harness 行为机制分解为五个可独立进化的模块（Agent Loop、Tool Use、Observation Management、Context Management、Task Completion Detection），在受限修改范围内分别进化后集成。配套地，论文建立 benchmark-disjoint 进化协议：独立构造 2,000 个可执行进化任务，与下游基准隔离，并在评估前冻结 harness。其可检验的核心问题是——排除基准数据后，进化出的 harness 是否仍在未见任务、跨域与跨模型上稳定增益。

## 核心主张

论文的四条主张均以「冻结 harness + 基准不相交」为前提，因此其证据强度取决于协议本身是否可信，而非单点涨分。下表按证据表与全文摘录整理。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | 冻结的进化 harness 在未见任务上一致提升，且跨域迁移 | §6.1 表2：TerminalBench 2.0 47.57 → 52.43（in-domain）、SWE-Bench-Verified 73.40 → 76.45（in-domain）；跨域 TB→SWE 75.80、SWE→TB 49.40 | 作者主张 |
| C2 | 进化 harness 可跨基础模型迁移，提升 GLM-5.2 与 MiniMax-2.5 | §6.2 表3：GLM-5.2 59.55 → 61.80；MiniMax-2.5 41.57 → 44.94（harness 用 DeepSeek-V4-Flash Preview 在 TB 相关集进化后冻结） | 作者主张 |
| C3 | 独立进化各模块再集成优于联合或非模块化进化 | §6.3 表4：ModularRSI 52.43，Non-modular 46.44，Joint All-Module 44.19，Baseline 47.57 | 作者主张 |
| C4 | 基准不相交协议下 ModularRSI 增益远超 AHE 与 Meta-Harness | §6.4 表6：ModularRSI 61.79 → 67.42；AHE 62.54、Meta-Harness 62.92，相对 Terminus-2 基线 61.79 仅约一个百分点变化 | 作者主张 |

最强的是 C3。它不依赖跨域或跨模型的外推，而是在同一基准、同一骨干上做受控对比，且方向性明确：两种「大范围改动」策略（非模块化、联合全模块）都掉到基线以下（46.44、44.19），只有模块受限 + 独立进化 + 集成超过基线（52.43）。这与论文的机制假设（限制修改范围可减少干扰）自洽，也与表5的单模块结果形成梯度证据：五个单模块变体均高于基线 47.57（Context Management 49.44、Tool Use 50.19、Agent Loop 50.56、Observation Management 49.81、Task Completion Detection 49.44），集成后进一步升到 52.43。

最弱的是 C4。它把「增益远超已有 RSI 方法」作为结论，但该对比只在 TerminalBench 2.0 单一基准、单一骨干（DeepSeek-V4-Flash-0731）上给出，且 AHE 与 Meta-Harness 的复现条件（是否同样 16 epochs、是否同样 120 实例）在给定摘录中未完整交代；同时论文自述未做隔离对比轨迹分析贡献的专门消融，因此「增益来自对比 + 模块化」这一归因仍属作者主张而非已复现结论。C1、C2 的数值一致且跨域、跨模型方向一致，但均为作者自报，尚无第三方复现，故仍标为作者主张。

## 机制与方法

ModularRSI 的核心主张是：harness 自进化的瓶颈不是「能不能改」，而是「改哪里」——即信用分配（credit assignment）。任务级二值奖励只说明成败，不说明哪个机制该负责。方法据此把问题拆成三步：对比轨迹采样与分析、模块受限的 harness 修改、验证门过滤。

**符号与分组。** 对第 $i$ 个进化实例 $x_i$ 做 $K$ 次 rollout，得到轨迹 $(tra_i^1,\dots,tra_i^K)$，每条由任务专属评估器赋二值奖励 $r_i^k\in\{0,1\}$。按奖励和把任务分为三组：

$$\mathcal{G}_i=\begin{cases}\mathrm{Positive},&\sum_k r_i^k=K\\ \mathrm{Contrastive},&0<\sum_k r_i^k<K\\ \mathrm{Negative},&\sum_k r_i^k=0\end{cases}$$

三组走不同分析路径：Contrastive 组配对同任务的成败轨迹做对比，定位与结果相关的函数级因素；Negative 组先查 Trajectory Memory（跨 epoch 存储的历史轨迹与奖励）找同任务的历史成功轨迹配对，找不到才做单侧诊断（重复循环、工具误用、恢复失效、过早终止）；Positive 组分析冗余动作与低效探索。分析结果被汇总为 JSON 结构化 findings，每条标注所属模块、支撑证据、修改理由与建议改动。

**模块化与修改范围限制。** harness 被分解为五个功能模块：Agent Loop、Tool Use、Observation Management、Context Management、Task Completion Detection。基础设施类组件（沙箱初始化、并行执行、LLM 通信）被排除在进化范围外。各模块独立进化、不共享中间更新，可并行处理。修改目标的选择依据是跨任务支持票数：语义相近、指向同一函数的诊断先被合并为候选修改，再按提供支撑证据的不同任务数投票排序，优先修改多任务共同支持的候选，以压低实例特异的失败影响。此外每个被修改函数维护 Evolution History，记录历史代码变更与各版本引入的功能，用于抑制重复/冲突修改与进化震荡。

**验证门。** 每次函数更新后依次通过三道门：Program Check（AST 校验、导入检查、协议合规、discovery-contract 验证、静态自属性审计）；Diff Review（由 Code-Modify Agent 审查 diff 是否编码了任务特定解、启发式或难以泛化的条件）；Execution Validation（从当前 batch 随机抽两个任务实跑）。任一环节失败即按记录的 diff 回滚。

**集成与函数库管理。** 五模块独立进化后做 Cross-Module Integration：在进化集上跑一个额外 epoch，识别跨模块冲突，去重、澄清职责、调整协调逻辑。为控制函数库膨胀，Function Merge 合并功能高度重叠的函数，Task-Aware Function Composer 依据任务描述与各函数自然语言描述，用 LLM 选出任务相关子集，仅激活这些函数。最终函数库冻结，评估期不再修改。

**适用前提与取舍。** 该方法要求：(1) 存在可执行、有可靠评估器的长程任务，且能对同一实例多次 rollout 以获得成败配对；(2) 任务可按模块归属做局部化诊断，即缺陷能被映射到五个模块之一；(3) 有足够算力支撑每实例 $K$ 次 rollout 加多轮验证执行。取舍上，模块化以「限制修改范围」换取低干扰，代价是跨模块的耦合缺陷可能被单模块视角漏掉，需靠集成阶段补偿；对比分析依赖成败配对的存在，当全部 rollout 失败且无历史成功轨迹时退化为单侧诊断，信号质量下降（作者在 Table 9 中量化了该比例，但未做隔离对比分析的专门消融，见「局限」）。

## 实验设置

评估在 TerminalBench 2.0（89 个长程终端任务）与 SWE-Bench-Verified（500 个人工验证的仓库级软件工程任务）上进行，全部在 Harbor 框架下运行，使用原始发布的基准版本。进化数据为独立构建的 2,000 个可执行任务（TB-related 与 SWE-related 两个子集），经 LLM 过滤（环境完整性、实用性/非平凡性、评估器有效性）、可执行验证（reference solution.sh 须通过全部测试且 no-op 提交不得获正奖励）、人工复核与语义相似度筛查，以最小化与下游基准的重叠。由于算力与时间限制，实际进化从每个子集各取 120 个实例，进化 3 个 epoch，batch size 10，TPM 限制 2M tokens/min。指标为 Acc、Pass@3、Pass^3，部分表格另报 StepNum（平均交互步数）。所有方法均禁用 web search。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| TerminalBench 2.0（in-domain） | DeepSeek-V4-Flash-Preview | No Evolution (Terminus-2) | 120 TB-related 进化实例，3 epochs | Acc 47.57 → 52.43；Pass@3 58.43 → 65.17；Pass^3 30.34 → 35.96 |
| SWE-Bench-Verified（in-domain） | DeepSeek-V4-Flash-Preview | No Evolution (Terminus-2) | 120 SWE-related 进化实例，3 epochs | Acc 73.40 → 76.45；Pass@3 83.20 → 85.30；Pass^3 62.80 → 66.80 |
| SWE-Bench-Verified（out-of-domain） | DeepSeek-V4-Flash-Preview | No Evolution (Terminus-2) | 120 TB-related 进化实例 | Acc 73.40 → 75.80；Pass@3 83.20 → 84.67；Pass^3 62.80 → 66.20 |
| TerminalBench 2.0（out-of-domain） | DeepSeek-V4-Flash-Preview | No Evolution (Terminus-2) | 120 SWE-related 进化实例 | Acc 47.57 → 49.40；Pass@3 58.43 → 60.67；Pass^3 30.34 → 30.34 |
| TerminalBench 2.0 | GLM-5.2 | Baseline | 冻结 harness，由 DeepSeek-V4-Flash Preview 在 TB-related 集上进化 | Acc 59.55 → 61.80；Pass@3 70.79 → 74.16；Pass^3 46.07 → 49.44 |
| TerminalBench 2.0 | MiniMax-2.5 | Baseline | 冻结 harness，由 DeepSeek-V4-Flash Preview 在 TB-related 集上进化 | Acc 41.57 → 44.94；Pass@3 56.18 → 57.30；Pass^3 24.72 → 30.34 |
| TerminalBench 2.0 | DeepSeek-V4-Flash-0731 | Baseline (Terminus-2) | 120 进化实例；基线 16 epochs | Acc 61.79 → 67.42；Pass@3 73.03 → 78.65；Pass^3 50.56 → 56.18 |
| SWE-Bench Verified | DeepSeek-V4-Flash-Preview | Hard & Easy 难度分布 | Medium-centered vs Hard & Easy 进化集 | Acc 76.45（Medium-centered）vs 74.25（Hard & Easy） |

与已有 RSI 方法的对比（Table 6）在统一协议下复现 AHE 与 Meta-Harness：均适配到 Harbor、从同一 Terminus-2 harness 出发、使用相同 120 个进化实例；ModularRSI 每模块独立进化 3 epochs 后合并，为对齐总进化轮数，AHE 与 Meta-Harness 进化 16 epochs；三者均用 DeepSeek-V4-Flash-0731 做进化与评估，TPM 同为 2M。结果：Baseline 61.79、Meta-Harness 62.92、AHE 62.54、ModularRSI 67.42（Acc）。消融方面，Table 4 比较非模块化进化（Acc 46.44）、全模块联合进化（44.19）与 ModularRSI（52.43）；Table 5 报告五个单模块进化变体（Context Management 49.44、Tool Use 50.19、Agent Loop 50.56、Observation Management 49.81、Task Completion Detection 49.44，基线 47.57）。难度分布设置见 Table 11：Medium-centered 在 40–60% 区间占 50%，Hard & Easy 在 0–20% 与 80–100% 各占 35%。需注意，作者未做隔离对比轨迹分析贡献的专门消融，且主实验仅使用 2,000 个进化实例中的子集。

## 证据与结果

以下数字均照抄自证据表与全文摘录，未做换算或推断。

主结果（冻结 harness，跨基准迁移，Table 2）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Acc | 47.57 → 52.43 | TerminalBench 2.0，TB-related 进化，In-Domain | Table 2 |
| Pass@3 | 58.43 → 65.17 | 同上 | Table 2 |
| Pass^3 | 30.34 → 35.96 | 同上 | Table 2 |
| Acc | 73.40 → 76.45 | SWE-Bench-Verified，SWE-related 进化，In-Domain | Table 2 |
| Pass@3 | 83.20 → 85.30 | 同上 | Table 2 |
| Pass^3 | 62.80 → 66.80 | 同上 | Table 2 |
| Acc | 73.40 → 75.80 | SWE-Bench-Verified，TB-related 进化，Out-of-Domain | Table 2 |
| Pass@3 | 83.20 → 84.67 | 同上 | Table 2 |
| Pass^3 | 62.80 → 66.20 | 同上 | Table 2 |
| Acc | 47.57 → 49.40 | TerminalBench 2.0，SWE-related 进化，Out-of-Domain | Table 2 |
| Pass@3 | 58.43 → 60.67 | 同上 | Table 2 |
| Pass^3 | 30.34 → 30.34 | 同上 | Table 2 |

跨基础模型迁移（冻结 harness，Table 3）：GLM-5.2 Acc 59.55 → 61.80（Pass@3 70.79 → 74.16，Pass^3 46.07 → 49.44）；MiniMax-2.5 Acc 41.57 → 44.94（Pass@3 56.18 → 57.30，Pass^3 24.72 → 30.34）。

消融与对照：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Acc | 47.57 / 46.44 / 44.19 / 52.43 | Baseline / Non-modular / Joint All-Module / ModularRSI | Table 4 |
| StepNum | 34.70 / 29.03 / 44.34 / 35.57 | 同上 | Table 4 |
| Acc | 49.44 / 50.19 / 50.56 / 49.81 / 49.44 | 单模块：Context Mgmt / Tool Use / Agent Loop / Observation Mgmt / Task Completion Detection | Table 5 |
| StepNum | 35.10 / 41.28 / 40.40 / 22.50 / 31.06 | 同上 | Table 5 |
| Acc | 61.79 / 62.92 / 62.54 / 67.42 | Baseline / Meta-Harness / AHE / ModularRSI（benchmark-disjoint） | Table 6 |
| Acc | 76.45 vs 74.25 | Medium-centered vs Hard & Easy 难度分布 | Table 7 |

对比对比例（Table 9）：当前 rollout 提供成败对 40.67%（732）；全失败组经 replay 配对历史成功 8.33%（150）；全失败且无历史成功 14.56%（262）；全成功 36.00%（648）。难度分布（Table 11）：Medium-centered 为 10%/15%/50%/15%/10%，Hard & Easy 为 35%/10%/10%/10%/35%（0–20% 至 80–100% 五档）。

摘录未给出：Table 2 中 Out-of-Domain 的 Pass@3/Pass^3 之外的分项置信区间、方差或显著性检验；Table 6 中 AHE 与 Meta-Harness 的 Pass@3/Pass^3 数值；Table 7 的 Pass@3/Pass^3；各表的 rollout 次数与随机种子。作者自述「未做隔离对比轨迹分析贡献的专门消融」，且主实验仅用 2,000 条中的 120 条子集。

## 证据强度评估

证据分级：B（中等偏强，方向可信但幅度需打折）。

理由：正向证据结构较完整——同一冻结 harness 在 in-domain 与 out-of-domain 两个方向上都为正增益（Table 2），跨三个基础模型（DeepSeek-V4-Flash-Preview、GLM-5.2、MiniMax-2.5）方向一致（Table 3），且模块化 vs 非模块化 vs 联合进化的对照呈现单调排序（Table 4），与「限制修改范围降低干扰」的机制解释自洽。但所有数字均为作者单方报告，无第三方复现，无显著性检验，且关键消融缺失，故不足以给 A。

主要威胁：

1. 构造效度（信用分配机制未被隔离）。作者明确承认「We do not conduct a dedicated ablation that isolates the contribution of contrastive trajectory analysis」。因此 47.57 → 52.43 的增益无法归因于对比轨迹分析本身，可能来自验证门、Evolution History、Function Merge 等任一组件。Fig. 3 中对比对比例随进化下降只是相关性证据，作者也仅表述为「suggests」。

2. 外部效度（数据规模与任务域受限）。主实验仅从 2,000 条中取 120 条 TB-related 与 120 条 SWE-related，3 epochs；作者自述受算力限制。评测仅覆盖 TerminalBench 2.0（89 任务）与 SWE-Bench-Verified（500 任务），两者同属终端/仓库级软件工程，向非软件域（如网页、科学计算）的可迁移性无证据。

3. 统计显著性缺失。TerminalBench 2.0 仅 89 任务，out-of-domain 的 Pass^3 为 30.34 → 30.34（零变化），而 Acc 增益 1.83 点；在如此小的任务集上，单任务翻转即可造成约 1.1 点的 Acc 波动，故 49.40 这类小幅增益可能落在噪声范围内。摘录未给出方差、置信区间或多种子结果。

4. 基线选择与评测污染。Table 6 的 benchmark-disjoint 对照中，AHE 与 Meta-Harness 仅变动约一个百分点，而 ModularRSI 提升超五点（61.79 → 67.42）；但该表使用 DeepSeek-V4-Flash-0731，与 Table 2/3 的 Preview 版本不同，跨表比较需谨慎。此外，进化数据虽经相似度过滤与人工审查以「minimize overlap」，但任务类别标签取自 TerminalBench 与 SWE-Bench 家族，仍存在通过类别先验间接适配下游分布的可能，作者未报告重叠度的量化上界。

## 边界与反例

**会推翻结论的观察**

- 若在 benchmark-disjoint 协议下，AHE / Meta-Harness 的增益被复现为与 ModularRSI 同量级（而非摘录所述「approximately one percentage point」），则 C4 的核心对比失效，模块化与对比分析的必要性随之被削弱。
- 若把「独立进化 + 集成」换成任意随机模块划分（而非五个功能模块），仍能取得 52.43 的 Acc，则增益来源是「限制修改范围」而非「功能模块化」，C3 的机制解释被替代。
- 若 Medium-centered 与 Hard & Easy 的 2.20 个百分点差距在多次随机种子下不显著（论文未报告方差或置信区间），则难度分布结论退化为噪声。

**最可能失效的条件**

1. **规模外推**：作者自陈「Due to computational and time constraints, we select 120 instances from each of the TB-related and SWE-related subsets of the 2,000-instance evolution dataset」。120 条、3 epochs 的进化预算下，函数库规模与模块间冲突量都远小于全量 2,000 条场景；Cross-Module Integration 与 Function Merge 的收益可能随规模非线性变化。
2. **模型能力区间**：跨模型证据只覆盖 GLM-5.2（59.55 → 61.80）、MiniMax-2.5（41.57 → 44.94）与 DeepSeek-V4-Flash 系列。对显著更强或更弱的基座，harness 修改的可迁移性未验证。
3. **基准同质性**：两个下游基准（TerminalBench 2.0、SWE-Bench-Verified）与进化数据同属「终端 / 仓库级」任务族，跨域仅在此二者间往返，真正的远域迁移（如非代码 agent 任务）无证据。

**作者未验证、读者易误推的方向**

- 论文明确承认「We do not conduct a dedicated ablation that isolates the contribution of contrastive trajectory analysis」。因此不能把增益归因于对比轨迹分析本身；Fig. 3 中对比对比例随进化下降只是相关性证据，作者亦仅表述为 "suggests"。
- 不应把 ModularRSI 读作「harness 可无限自进化」：函数库在评估前被冻结，且 Task-Aware Function Composer 只激活子集，长期持续进化的稳定性（振荡、退化）未被检验。
- 不应把 out-of-domain 结果（73.40 → 75.80、47.57 → 49.40）等同于「通用能力提升」：两者仍共享同一 harness 与同一模型，且 out-of-domain 增益明显小于 in-domain。

## 与知识库的关系

**Harness RSI / 自进化 agent harness 笔记（`note-harness-rsi`）**
- 新增：把 harness 显式拆为五个功能模块（Agent Loop、Tool Use、Observation Management、Context Management、Task Completion Detection），并给出「独立进化 → Cross-Module Integration → Function Merge → Task-Aware Function Composer → 冻结」的完整流水线；此前笔记中的整体式进化方法（Meta-Harness、AHE）无此信用分配粒度。
- 新增：benchmark-disjoint 进化协议（2,000 条独立构建任务，含相似度过滤与领域分析）。这是该笔记此前缺失的评测基础设施。
- 张力：笔记若曾把「模块化」默认为天然更优，本文 Table 4 提供了反例边界——Joint All-Module Evolution 44.19、Non-modular Evolution 46.44 均低于 baseline 47.57，说明模块化本身不是充分条件，限制修改范围才是关键变量。

**自进化泛化性 / 基准数据泄漏笔记（`note-rsi-leakage`）**
- 印证：在排除基准数据后，AHE 与 Meta-Harness「remain close to the Terminus-2 baseline, with accuracy changes of approximately one percentage point」，而 ModularRSI「improves accuracy by more than five points」（61.79 → 67.42）。这为「用下游基准数据进化会高估泛化性」提供了直接对照。
- 注意：该对照仅在单一模型（DeepSeek-V4-Flash-0731）与单一基准（TerminalBench 2.0）上给出，不宜当作跨设置的普适结论。

**对比轨迹分析 / 信用分配笔记（`note-contrastive-credit`）**
- 新增：同任务成败配对 + 跨任务证据聚合（按支持任务数投票）+ 模块受限修改三者结合；并引入 Trajectory Memory 处理全失败组（Table 9：150 组由历史成功轨迹补配对，262 组无历史成功，8 组无有效分数）。
- 张力：该笔记若把对比分析视为已被验证的核心机制，需修正——作者明确未做隔离消融，Fig. 3 的对比对比例下降只是支持性证据。

**进化数据难度分布笔记（`note-evolution-data-quality`）**
- 印证并量化：Medium-centered（40–60% 占 50%）在 SWE-Bench Verified 上 76.45，Hard & Easy（两端各 35%）74.25，差 2.20 个百分点（Table 7、Table 11）。

**TerminalBench / SWE-Bench 评测笔记（`note-terminalbench-swebench`）**
- 新增：冻结 harness 的跨模型迁移证据（GLM-5.2、MiniMax-2.5、DeepSeek-V4-Flash 系列）与跨域往返证据；并补充 Pass@3 与 Pass^3 双指标（如 TB in-domain Pass^3 30.34 → 35.96）。

## 复现与验证计划

**最小可执行验证方案（基于证据表与摘录，未标注处为不确定）**

环境与初始 harness：以 Harbor 框架中的 Terminus-2 作为共享初始 harness，并将其行为机制重组为五个模块（Agent Loop、Tool Use、Observation Management、Context Management、Task Completion Detection）。所有方法统一适配到 Harbor，并禁用 web search，防止 harness 从外部检索任务解。

数据与任务：作者自建 2,000 个可执行进化任务，经环境完整性、实用性/非平凡性、评估器有效性三重 LLM 过滤，加可执行验证（reference solution.sh 须通过全部测试、no-op 提交不得获正奖励）与人工复核、语义相似度筛查。受算力限制，主实验仅从 TB-related 与 SWE-related 子集各取 120 个实例。复现时若无法重建该数据集，最小验证可退化为：自建小规模可执行任务集，并严格保证与下游基准不相交。

基线与预算：基线为 No Evolution（Terminus-2）。ModularRSI 每模块独立进化 3 epochs 后做 merging；对照的 AHE 与 Meta-Harness 为匹配总进化轮数设为 16 epochs。所有方法使用同一基础模型（对比实验用 DeepSeek-V4-Flash-0731）与相同 TPM 上限 2M tokens/min。

判据：主指标 Acc，辅以 Pass@3 与 Pass^3。可复现的判据锚点为：TerminalBench 2.0 上 47.57 → 52.43（in-domain），SWE-Bench-Verified 上 73.40 → 76.45（in-domain）；跨域为 73.40 → 75.80 与 47.57 → 49.40。若复现结果仅提升约一个百分点（如 AHE 62.54、Meta-Harness 62.92 相对基线 61.79），应怀疑未真正实现模块化信用分配。

预期失败模式：非模块化或联合全模块进化可能低于基线（46.44、44.19）；任务特定 diff 未通过 Diff Review 会被回滚；Execution Validation 随机抽两任务实跑失败即回滚；对比样本不足时（全失败且无历史成功，占 14.56%）诊断退化为单侧。注意作者未做隔离对比轨迹分析的专门消融，该环节贡献属不确定。

## 术语与记号

ModularRSI 将 harness 行为机制分解为五个可独立进化的功能模块，并用对比轨迹分析把任务级结果转化为局部化进化信号。下表覆盖正文出现的关键术语、符号与缩写。

| 术语 | 含义 |
| --- | --- |
| Harness | 智能体执行框架，负责执行流程、工具交互、上下文管理与环境反馈 |
| Recursive Self-Improvement (RSI) | 递归自改进，智能体从执行经验中迭代优化自身机制 |
| Credit Assignment | 信用分配，将任务级成败归因到具体应修改的组件 |
| Contrastive Trajectory Analysis | 对比轨迹分析，配对同任务的成功与失败轨迹以定位行为差异 |
| Trajectory Memory | 轨迹记忆，跨进化轮次存储历史轨迹及奖励以补充对比证据 |
| Validation Gates | 验证门，含 Program Check、Diff Review、Execution Validation，过滤不合格修改 |
| Cross-Module Integration | 跨模块集成，将独立进化的模块合并并消解冲突 |
| Function Merge | 函数合并，合并功能高度重叠的进化函数以减少冗余 |
| Task-Aware Function Composer | 任务感知函数组合器，按任务描述动态激活相关函数 |
| Benchmark-Disjoint Evolution Protocol | 基准不相交进化协议，进化数据与下游评估基准完全隔离 |
| Pass@3 | 三次独立 rollout 中至少一次成功的任务比例 |
| Pass^3（正文亦写作 Pass3） | 三次独立 rollout 全部成功的任务比例，衡量执行可靠性 |
| $x_i$ | 第 $i$ 个进化实例（任务） |
| $K$ | 每个实例的 rollout 次数 |
| $tra_i^k$ | 实例 $i$ 的第 $k$ 条轨迹 |
| $r_i^k$ | 轨迹的二值奖励，$r_i^k=1$ 成功，$r_i^k=0$ 失败 |
| $\mathcal{G}_i$ | 任务按 rollout 奖励划分的组：Positive（$\sum_k r_i^k=K$）、Contrastive（$0<\sum_k r_i^k<K$）、Negative（$\sum_k r_i^k=0$） |

五个功能模块为：Agent Loop、Observation Management、Tool Use、Context Management、Task Completion Detection。实现层进一步把三组细化为路由桶：Positive 对应 all_pass_efficient / all_pass_wasteful，Contrastive 对应 mixed，Negative 对应 fixable_fail / stuck_fail / unreachable_fail，infra_only 被排除在 harness 诊断之外。

## 自测

以下问题用于检验你是否真正读懂了 ModularRSI 的证据链，而非只记住了几个提升数字。建议先不看答案自答，再展开核对。

**Q1（基础）** ModularRSI 把 harness 的行为机制拆成哪五个模块？在单模块进化消融（Table 5）中，哪个模块的 Acc 增益最大，哪个模块对 StepNum 的影响最显著？

<details><summary>答案</summary>
五个模块为 Agent Loop、Observation Management、Tool Use、Context Management、Task Completion Detection。单模块进化中 Agent Loop 的 Acc 最高（50.56，基线 47.57），增益最大；Observation Management 把平均执行步数从基线 34.70 降到 22.50，对效率影响最显著。注意所有单模块变体都高于基线，但都低于五模块整合后的 52.43。
</details>

**Q2（基础）** 在 benchmark-disjoint 协议下，ModularRSI 与 AHE、Meta-Harness 的对比结果是什么？为什么作者认为这一对比比"在基准数据上进化"的结果更有说服力？

<details><summary>答案</summary>
Table 6 中，基线 61.79，Meta-Harness 62.92，AHE 62.54，ModularRSI 67.42。AHE 与 Meta-Harness 相对 Terminus-2 基线仅约一个百分点的变化，而 ModularRSI 提升超过五个百分点。作者主张：在排除基准数据后，已有方法在基准上表现出的强性能主要来自对下游基准的适配，因此 benchmark-disjoint 协议更能反映可迁移改进。这是作者主张，非独立复现结论。
</details>

**Q3（跨小节推理）** 结合 Table 4 与 Table 5，为什么"独立进化各模块再整合"优于"联合进化全部模块"？请用干扰（interference）与信用分配两个概念解释，并指出这一解释在证据上的薄弱处。

<details><summary>答案</summary>
Table 4 显示：非模块化进化 Acc 46.44、联合全模块进化 44.19，均低于基线 47.57；而独立进化后整合达 52.43。作者的解释是限制修改范围可减少无关机制间的干扰，并把粗粒度任务级结果局部化为模块级信号（信用分配）。薄弱处：论文未做隔离对比轨迹分析贡献的专门消融（Limitations 明确承认），因此"对比分析"与"模块化"各自的贡献无法从现有证据中分离；此外联合/非模块化变体低于基线这一反直觉现象也缺少机制层面的直接证据。
</details>

**Q4（跨小节推理）** 论文同时报告了 in-domain 与 out-of-domain 迁移（Table 2）以及跨基础模型迁移（Table 3）。这两类泛化证据在逻辑上各自排除了什么替代解释？又共同留下了什么未解问题？

<details><summary>答案</summary>
跨域迁移（TB 进化→SWE 75.80；SWE 进化→TB 49.40）排除了"仅适配进化任务表面分布"的解释；跨模型迁移（GLM-5.2 59.55→61.80，MiniMax-2.5 41.57→44.94，冻结 harness 由 DeepSeek-V4-Flash-Preview 进化）排除了"改进只与进化所用基础模型耦合"的解释。共同未解问题：进化数据仅从 2,000 实例中取 120 条（每子集），规模有限；且缺少隔离对比轨迹分析的消融，因此无法确认增益究竟来自哪一机制成分。此外 out-of-domain 增益明显小于 in-domain（如 TB 上 49.40 vs 52.43），迁移幅度有限。
</details>

**Q5（跨小节推理）** 若你要把 ModularRSI 迁移到自己的 agent 场景，根据 Table 7/Table 11 与 Table 9，你会如何设计进化数据的难度分布与对比样本来源？请说明依据与风险。

<details><summary>答案</summary>
难度分布：Table 11 显示 Medium-centered 在 40–60% 难度区间占 50%，两端各 10%；Hard & Easy 则在 0–20% 与 80–100% 各占 35%。Table 7 显示 Medium-centered 在 SWE-Bench Verified 上达 76.45，比 Hard & Easy 的 74.25 高 2.20 个百分点。依据是中等难度任务更可能产生成败混合的对比信号。对比样本来源：Table 9 显示当前 rollout 即提供成败对的占 40.67%（732 组），全失败但可借历史成功配对的占 8.33%（150 组），全失败且无历史成功的占 14.56%（262 组），全成功占 36.00%（648 组）——即约 14.56% 的组缺乏对比证据，需依赖单侧诊断。风险：论文承认未做隔离对比分析的消融，且进化仅用 120 条实例，迁移到你场景时难度分布的最优形状与对比样本稀缺下的退化行为均未被验证。
</details>
