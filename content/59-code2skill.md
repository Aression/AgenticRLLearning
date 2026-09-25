---
id: code2skill
title: Code2Skill：从代码规模化合成接地技能库
summary: 现有技能合成方法受限于其来源：基于轨迹的方法依赖产生它的模型、任务分布与工具，质量受生成智能体能力上限约束且易过时；基于文档的方法缺乏可执行证据来验证技能。论文提出以大规模代码库作为接地来源，解决如何从真实代码中抽象出可复用、可验证、可维护的程序性技能并规模化构建技能库的问题。
stage: SYSTEMS
track: Agent 系统
kind: paper
depth: deep
evidenceGrade: C
order: 59
minutes: 52
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.05571
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 5
full_text_url: https://arxiv.org/html/2609.05571
objectives: [理解以源代码而非执行轨迹或文档作为技能合成基底的核心动机与优势, 掌握 Code2Skill 四阶段流水线：源单元筛选、技能抽象、源体盲重建验证、溯源与索引组织, 了解 CodeSkillBank 的规模、记录构成与在 SWE-bench 等基准上的增益证据, 认识技能在 RL 训练中的接入位置效应与紧凑渲染、purpose indexing 的检索权衡]
tags: [skill-synthesis, code-grounded, agent-harness, skill-bank, retrieval, rl-integration]
sources: [grounded-skill-synthesis-from-code-at-sc]
related: [modularrsi-harness, harness-design-coding-agents, codemidas-code-rl-envs]
prerequisites: [agent-loop, harness-design-coding-agents]
---
## 问题与语境

Agentic 系统的能力上限并不只由模型参数决定：长程任务要求智能体在推理时检索并执行可复用的程序性知识，而这类知识通常被封装在 skill / harness 组件中。由于 skill 可以独立更新、版本化与部署，它构成了一条独立于参数规模与推理时算力的扩展维度。问题在于，现有技能合成范式的**基底（substrate）**限制了这条维度能走多远。

论文把已有做法归为两类。其一是轨迹派生方法（Trace2Skill、ExpeL、SkillRL-Bank 等），从执行轨迹中蒸馏成功片段、失败与反复出现的 workaround。其失效点在于耦合性：技能质量受生成智能体的能力与经验上界约束，且与产生它的模型、任务分布、工具与 harness 绑定，这些组件一旦变化，已蒸馏的技能可能过时或不兼容。其二是文档派生方法，从静态人类可读文本合成技能，虽不依赖智能体轨迹，但缺乏具体执行作为接地与验证的依据。

论文的定位不是"再做一个技能库"，而是提出一个互补的合成范式：以**源代码**作为接地基底。代码天然支持执行、评测、验证、维护与版本化，GitHub 上已积累大量被实现、调试并反复精炼的仓库，为抽象与验证可复用过程提供了具体操作证据。真正的困难在于抽象与证据之间的张力——真实代码把可泛化过程与框架胶水、项目局部标识符、重复实现、隐式依赖和未解决的边界情况交织在一起；一条"golden skill"不仅要说明实现做了什么，还要说明何时适用、哪些步骤本质、哪些不变量必须成立、哪些失败会改变执行路径、哪些泛化超出其范围。因此核心挑战是：在超越具体实现的同时，保留足以接地与验证该技能的实现证据。Code2Skill 即针对这一张力设计的全自动流水线。

## 核心主张

论文的核心主张可归纳为四点：代码派生技能库在推理侧带来可测量的整体增益；在统一下游接口下优于轨迹派生技能库；技能的有效性取决于接入位置而非仅取决于"有没有技能"；紧凑渲染比更深检索更划算。下表给出主张、证据定位与状态判定。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | CodeSkillBank 在 72 次协议匹配评测中提升 57 次，宏平均从 42.90 升至 47.90（相对 +11.7%）；每个模型与推理模式的八基准均值上升 2.26–7.39 点（相对 6.0%–20.7%），九个 SWE-bench Verified 配对全部提升 | §1 Introduction；§5.2 表 1；§6 Conclusions | 作者主张 |
| C2 | 在共享 agent loop 下，Code2Skill 在全部七个共享基准上排名第一，平均 49.5；即使按基准逐项取三个轨迹派生基线的最优（oracle）也仅 40.1，低 9.5 点；单项上超出最强轨迹基线 6.6–13.3 点 | §1 Introduction；§5.3 表 2 | 作者主张 |
| C3 | k=3 时摘要渲染把平均技能上下文减少 88.9%（6,352→707 字符）而性能保持或提升；k 从 1 增到 10 使平均渲染上下文从 2.1K 扩到 17.8K 字符但收益甚微 | §5.5 图 6 | 作者主张 |
| C4 | 编码 RL 中四种接入均优于无技能对照（24%）：full prompt 32%、summary prompt 31%、reward reference 31%、post-generation review 38% | §5.6 表 3 | 存疑 |
| C5 | 从测试通过的 AI 生成实现中提取的技能库与人类代码技能库在 LiveCodeBench 400 题子集上 pass rate 为 93.50% 与 93.00%，但两者在 16 题上不一致（人类独解 7 题，AI 独解 9 题） | §5.7 图 7 | 作者主张 |

**最强的是 C2。** 它把比较放在同一 agent loop、同一评测模型（DS4-Flash reasoning）、同一批七个基准上，并报告五次运行的 mean ± std（如 Code2Skill 在 SWE 上 44.7±1.6，最强轨迹基线 SkillRL-Bank 为 36.8±1.9），且额外给出 oracle 上界 40.1 这一保守对照——即便允许基线逐基准挑最优仍低于 Code2Skill，这排除了"收益仅来自 agent loop"的替代解释。相对地，C1 覆盖面更广（9 个模型设置 × 8 个基准），但 Avg 是展示分数的未加权宏平均，混合了不同评测器与任务数，作者自己也声明它只是描述性汇总而非任务级合并成功率。

**最弱的是 C4。** 它只有单一 checkpoint（step 150）、无重复种子、无学习曲线，因此无法区分学习速度、收敛性与最终策略性能的差异；作者在限制中明确承认这一点。此外该实验使用模拟 test-pass 奖励，与真实 RL 训练条件的距离未被量化。C3 与 C5 同属单点证据：C3 只在 BigCodeBench Instruct-Hard 上验证，且 purpose indexing 对 pass rate 影响混合；C5 的 0.50 个百分点总差不足以确立等价性，作者亦如此声明。

## 机制与方法

Code2Skill 的目标是把「源代码仓库」而非「执行轨迹」或「文档」作为技能合成的接地基底。其问题形式化（§3.1）为：构造映射把函数、方法、命令行入口或文件级组件连同其仓库上下文，映射为候选技能记录；一条被接受的记录必须说明该过程何时适用、要复现什么行为、哪些前置条件与不变量约束执行、失败如何处理、以及哪些源码跨度支撑这些主张。由此导出三项要求：**接地性**（procedural claims 须由可恢复的实现跨度支撑，并通过 source-body-blind reconstruction 挑战）、**可迁移性**（剥离项目局部标识与集成细节，保留可复用的前置条件、步骤、不变量与失败处理）、**可维护性**（保留溯源、支撑源码跨度、记录类型与构建状态，以便随代码演化被审查、作废或再生成）。

流水线为四阶段全自动流程（Figure 1）：(1) **源单元选择**——扫描 GitHub 仓库（保留 >500 星项目），解析候选函数、方法、命令行入口与文件级组件，排除不安全文件、测试文件、二进制与过短单元；再由 LLM 标注器按六项可复用性信号（可复用意图、有序步骤、控制流/状态转移、边界与失败处理、接口充分性、非平凡性）打分，经选择门限并受每仓库上限约束保留源单元。(2) **类型化技能生成**——把选中实现抽象为原子操作、复合工作流或重复模式三类记录，含适用条件、执行步骤、不变量、失败情形、反目标与支撑证据。(3) **接地验证**——源体盲重建：仅凭技能记录让 LLM 重建实现；再由源感知评判器与原始代码比对，过滤无支撑或不完整记录。(4) **检索视图构建**——接受记录进入带溯源的证据档案，并构建特征标签视图与用途索引（purpose indexing）视图。

下游使用接口（§4.2）形式化为：给定任务 $x$ 与决策步 $t$ 前的智能体/模型状态 $h_t$，若接口以查询 $q_t$ 访问检索面向的技能库 $\mathcal{B}$，则渲染技能上下文

$$z_t = \begin{cases}\mathrm{Render}_r\!\left(\mathrm{TopK}_k(q_t;\mathcal{B})\right), & \text{若发出查询},\\ \varnothing, & \text{否则}.\end{cases}$$

随后 $a_t \sim \pi_{\theta^{(s)}}(\cdot\mid x, h_t, z_t)$。其中 $k$ 为检索深度，$r$ 为渲染方式（完整记录或摘要），$\theta^{(s)}$ 为被评测的模型或策略检查点。无技能对照即同一协议下 $z_t=\varnothing$。该接口统一覆盖 prompt 级检索、规划期检索、生成后审查、验证器/奖励侧使用与训练期技能条件化；学习场景下接口还决定技能对哪个检查点可见（例如对 verifier 或 reward model 可见而对被评判的策略轨迹隐藏）。推理类协议在测试时保持模型或策略参数固定。

**设计取舍与适用前提**：以代码为基底换取可执行、可验证、可版本化的证据，代价是必须处理真实代码中通用过程与框架胶水、项目局部标识、重复实现、隐式依赖与未决边界情形交织的问题；接地验证依赖「重建—比对」这一代理信号，而非直接执行。用途索引以每簇一个代表记录降低语料冗余，但可能挤掉局部相关的候选。方法前提是：存在大规模、活跃维护且带采用信号的公开仓库（本文候选池中位 3,133 星、82 个已合并 PR，78.3% 至少 1,000 星，66.0% 在近一年内有推送），且技能库可离线构建、独立于模型权重维护。

## 实验设置

实验围绕六个研究问题组织（§5）：RQ1 代码派生技能库是否提升智能体表现；RQ2 与轨迹派生技能库在共享接口下的比较；RQ3 技能应插入工作流的哪个位置；RQ4 技能能否紧凑表示而不损失效用；RQ5 在强化学习中接入位置是否仍然重要；RQ6 AI 生成代码能否成为持续扩展的技能来源。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
| --- | --- | --- | --- | --- |
| SWE-bench Verified、BigCodeBench、AIME、HMMT、GPQA、TerminalBench、LongCLI、AgentBench（八个基准） | DS4-Flash、Qwen3.5 27b、Qwen3.6 27b、Gemini 2.5 Pro、GPT 5.2（含推理模式开关） | No CodeSkill（协议匹配对照，同一 review 步骤但不提供技能） | 未说明 | Avg（所展示基准分数的未加权均值） |
| SWE、BigCode、AIME、HMMT、Terminal、LongCLI、AgentBench（七个共享基准） | DS4-Flash reasoning | Trace2Skill、ExpeL、SkillRL-Bank | 五次运行 | mean ± std |
| BigCodeBench Instruct-Hard | DS4-Flash、Qwen3.5 | no-skill 基线；full-record 渲染 | $k \in \{1,3,10\}$ | 渲染上下文字符数、pass rate |
| SWE-World coding RL | Qwen3-32B SWE-World checkpoint | No CodeSkill（24%） | 共享训练步 150 | resolve rate |
| LiveCodeBench 子集（400 任务） | DS4-Flash（high reasoning effort，temperature 0） | human-code bank（93.00%） | top-k=4 检索 | pass rate |

协议细节（Appendix D.2）：SWE-bench 全程使用同一固定 475 实例子集；TerminalBench 与 LongCLI 的超时保留在分母中；每个 LongCLI 任务重复三次，报告多次尝试的平均解决率。聚合口径（Appendix D.1）：基准内技能效应为固定任务集上协议匹配的技能与无技能条件之差，百分点差基于基准报告的 0–100 分制；Avg 列与 RQ2 的七基准汇总均为所展示基准分数的未加权宏平均，因混合了不同评测器与任务数，属描述性汇总而非任务级合并成功率；仅当两条件在相同任务 ID 上保留条目级结果时才使用任务配对统计检验。上下文成本定义为模型可见的渲染技能记录的平均字符数，检索管线自身产生的文本（含 reranker 解释与任务查询字段）不计入。技能库构建侧：Code2Skill 扫描截至 2026 年 4 月 14 日可用的 GitHub 仓库，保留超过 500 星的项目；RQ2 的三个轨迹派生基线由 Qwen3.5-397B-A17B 在与评测不重叠的留出任务划分上构建，CodeSkillBank 不使用这些基准的智能体轨迹。

## 证据与结果

**主结果（RQ1，表 1）**：CodeSkillBank 在 72 次协议匹配评测中提升 57 次；八个基准的宏平均在每个模型与推理模式下上升 2.26–7.39 分，相对提升 6.0%–20.7%；SWE-bench Verified 的九对比较全部提升。宏平均从 42.90（无技能）升至 47.90（有技能），相对增益 11.7%。注意 Avg 为各基准显示分数的未加权宏平均，作者自述其为描述性汇总而非任务级合并成功率（附录 D.1）。

**与轨迹派生技能库对比（RQ2，表 2）**：统一下游接口、DS4-Flash reasoning、五次运行、七个共享基准。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Code2Skill 七基准平均 | 49.5 | 统一 agent loop | §1、§5.3 |
| Trace2Skill 平均 | 31.0 | 同上 | §1 |
| ExpeL 平均 | 27.9 | 同上 | §1 |
| SkillRL-Bank 平均 | 32.8 | 同上 | §1 |
| oracle best-of-baselines 平均 | 40.1（低于 Code2Skill 9.5 分） | 逐基准取最优基线 | §5.3 |
| Code2Skill 相对最强轨迹基线 | 超出 6.6–13.3 分 | 单基准 | §1、§5.3 |

**上下文效率（RQ4，图 6）**：k 从 1 增至 10，平均渲染上下文由 2.1K 扩至 17.8K 字符，收益甚微；Qwen 仅增 1.40 分（33.10→34.50），DS4-Flash 处于或低于其无技能基线。k=3 时摘要渲染将平均技能上下文减少 88.9%（6,352→707 字符）；Qwen 保持全记录分数，DS4-Flash 由 28.40 升至 31.80。用途索引将全记录上下文从约 6.4K 降至 5.0K 字符，但对 pass rate 影响混合。

**RL 集成（RQ5，表 3）**：Qwen3-32B SWE-World 检查点、共享训练步 150、resolve rate——无技能 24%，full prompt 32%，summary prompt 31%，reward reference 31%，post-generation review 38%。

**AI 代码来源（RQ6，图 7）**：LiveCodeBench 400 题子集、DS4-Flash、top-k=4，人类代码库 93.00%、AI 代码库 93.50%，两者在 16 题上不一致（人类独解 7 题、AI 独解 9 题）。

**消融与对照**：RQ3 比较生成时提示、规划时引导与生成后批评三种接入点——规划时引导在全部八项共享评测上提升；生成时提示对 DS4-Flash 四项全升，Qwen3.5 收益不一致；生成后批评在 72 项中提升 57 项。RQ4 消融检索深度、渲染方式与用途索引。RQ5 消融技能接入位置。RQ6 消融技能来源（人类 vs AI 代码）。所有对照均为协议匹配的无技能条件（$z_t=\varnothing$）。技能库规模：19,769 个 GitHub 仓库、1,006,822 条接受记录；仓库中位星数 3,133、中位合并 PR 82，78.3% 仓库 ≥1,000 星，46.9% ≥100 合并 PR，66.0% 近一年内有推送。

## 证据强度评估

**分级：B（中等偏强，方向可信、幅度需谨慎）**。理由：证据覆盖八个基准、五个模型家族、推理与非推理模式、推理与 RL 两类设置，且 RQ2 在统一接口下与三种轨迹派生基线做五次运行对比，RQ4/RQ5/RQ6 均有针对性消融，内部一致性较好（SWE-bench Verified 九对全升、RL 四种接入全部优于对照）。但所有数字均为作者自报，档案中未见第三方复现、未见任务级配对显著性检验的完整结果，且核心汇总量为未加权宏平均，故不足以支撑 A 级。

**主要威胁**：

1. **构造效度**：宏平均（Avg）是不同评测器、不同题量的基准分数的未加权平均，作者自己在附录 D.1 承认这是描述性汇总而非任务级合并成功率。因此「+5.0 分 / 11.7%」不能解释为任务成功率提升；RQ2 的 49.5 与 40.1 同样受此限制。

2. **统计显著性**：RQ2 报告五次运行的 mean±std，但档案未给出逐基准的显著性检验结果；RQ5 仅报告单一检查点（步 150），作者明确承认「无重复种子或学习曲线，不能确立学习速度、收敛或最终策略性能的差异」。因此 24%→38% 的 14 点差距应视为单点观测，C4 标注为「存疑」是恰当的。

3. **基线选择**：RQ2 的轨迹派生基线由 Qwen3.5-397B-A17B 在留出划分上构建，而 CodeSkillBank 由 19,769 个仓库离线构建，两者在构建预算、数据量与工程投入上并不对等；「代码基底优于轨迹基底」的结论可能部分来自规模而非来源。此外 oracle best-of-baselines 是逐基准取最优，属事后上界，与单一 Code2Skill 库的比较并非同预算对照。

4. **外部效度与评测污染**：技能库扫描截止 2026 年 4 月 14 日、保留 >500 星项目，而 SWE-bench、BigCodeBench、LiveCodeBench 等基准的题目多源自公开仓库，存在技能库与评测集同源（训练/评测重叠）的风险，档案未提供去污染分析。RQ6 中人类与 AI 代码库仅差 0.50 个百分点、却在 16 题上分歧，作者亦承认「小的总体差异不能确立等价性」，故「AI 代码可作持续扩展来源」应读作可行性提示而非等价性结论。

## 边界与反例

**什么观察会推翻结论。** 核心结论「代码基底技能库优于轨迹派生技能库」建立在 RQ2 的七基准对比上（Code2Skill 平均 49.5，oracle best-of-baselines 仅 40.1）。若在**同一 agent loop、同一检索接口**下，把轨迹基线换成更强的生成模型或更大的轨迹预算后差距收敛到噪声范围内，则该结论退化为「检索技能有用」而非「代码基底有额外优势」。作者自己也承认 RQ2 的 Avg 是不同评测器与任务数的**未加权宏平均**，是描述性汇总而非任务级成功率，因此 9.5 分的差距不能直接读作任务级胜率差。

**最可能失效的条件。**
- **短题与强模型**：作者明确指出 BigCodeBench 在 reasoning mode 下结果混合，技能对「强模型已能直接解决的短问题」收益更小。把结论外推到竞赛级短代码题需谨慎。
- **上下文预算充足时**：RQ4 显示 k 从 1 增到 10 只把渲染上下文从 2.1K 扩到 17.8K 字符却「little additional utility」，说明收益主要来自少量高价值记录；若读者误推「检索越深越好」，与原文相反。
- **RL 场景**：RQ5 仅报告 step 150 的**单一 checkpoint**，无重复种子、无学习曲线，作者明言这**不能**确立学习速度、收敛性或最终策略性能的差异。因此「post-generation review 最优（38% vs 24%）」应视为单点观察，而非稳定的接口排序。
- **来源等价性**：RQ6 中人类代码库 93.00% 与 AI 代码库 93.50% 仅差 0.50 个百分点，但两者在 16 个任务上不一致（人类独解 7 个、AI 独解 9 个）。作者明确表示小聚合差异**不足以确立等价**，读者不应据此推断 AI 代码可替代人类代码。

**未验证但易被误推的方向。** 论文未给出技能库随源仓库演化的**失效/再生成率**，也未验证跨语言、跨生态迁移；「可维护、可版本化」目前是设计主张而非实测结论。此外，purpose indexing 降低语料冗余却对 pass rate 效果混合，说明「去冗余」不等于「提性能」。

## 与知识库的关系

**新增维度（此前笔记未覆盖）。** 本文把技能来源从「执行轨迹」和「静态文档」扩展到**源代码**，并给出可执行、可验证的接地机制（source-body-blind reconstruction + source-aware comparison）。这为 `coskill`、`modularrsi` 中「技能/harness 作为可插拔组件」的主题补上了「代码作为可执行基底」这一来源轴，且技能库被定位为可独立更新、版本化、部署的 plug-and-play 组件（1,006,822 条记录，源自 19,769 个仓库）。

**印证。** 与 `modularrsi` 关于「harness 层可独立于模型权重扩展能力」的判断一致：CodeSkillBank 离线构建、跨模型家族与推理模式复用同一检索索引，且推理期协议保持参数固定。

**与既有结论的张力。**
- 与轨迹派生技能库笔记（Trace2Skill / ExpeL / SkillRL-Bank）存在**直接张力**：在统一下游接口下，代码派生平均 49.5 对 31.0 / 27.9 / 32.8，作者据此主张收益不能仅归因于 agent loop。但该对比的 Avg 为未加权宏平均，且基线由 Qwen3.5-397B-A17B 在留出划分上构建，**构建模型不同**可能混淆来源效应——这是需要标记的不确定处。
- 与「技能检索与上下文效率」笔记**部分印证、部分修正**：印证「紧凑表示优于堆叠上下文」；修正之处在于 purpose indexing 并非单调有益，作者观察到它可能「displace a locally relevant candidate」。
- 与「技能在 RL 中的集成位置」笔记**新增证据但存疑**：post-generation review 24%→38%，高于 policy 侧（32%/31%）与 reward 侧（31%），提示集成位置效应在 RL 中同样存在；但单 checkpoint、无种子重复，属**存疑**级证据（对应 claims 中 C4 的 status）。
- 与「AI 生成代码作为技能来源」笔记**新增证据**：AI 代码库可作持续扩展来源，但**非等价替代**。

**可链接笔记 id**：`coskill`、`modularrsi`、`trajectory-skill-banks`、`skill-retrieval-context-efficiency`、`skill-rl-integration`、`ai-code-as-skill-source`。

## 复现与验证计划

目标：在自有场景下判断「代码派生技能库」是否可迁移，而非复现 1,006,822 条记录的完整 CodeSkillBank。建议按三级最小验证推进。

**第一级（接口验证，成本最低）**。环境：任一可跑 agent loop 的模型 + 检索后端。任务：BigCodeBench Instruct-Hard 与 SWE-bench Verified 固定 475 实例子集（附录 D.2 明确「SWE-bench uses the same fixed 475-instance subset throughout」）。基线：协议匹配的 no-skill 对照（同一 review 步骤但不注入技能）。预算：检索深度 $k \in \{1,3,10\}$，全记录渲染 vs 摘要渲染。判据：$k=3$ 摘要渲染应把平均技能上下文从 6,352 字符压到 707 字符（−88.9%）而性能不降；若你的场景中压缩即掉点，说明该结论依赖其记录写法，不可直接迁移。

**第二级（来源对照）**。用同一 agent loop、同一模型（DS4-Flash reasoning 或你的等价模型），对比代码派生库与轨迹派生库（Trace2Skill / ExpeL / SkillRL-Bank 的公开实现），五次运行报 mean ± std。判据：代码派生库是否在全部基准上领先；注意作者报告的 oracle best-of-baselines 平均仅 40.1，低于 Code2Skill 的 49.5。

**第三级（RL 接入位置）**。在 SWE-World 类编码 RL 中，于共享训练步 150 比较 no-skill（24%）、full prompt（32%）、summary prompt（31%）、reward reference（31%）、post-generation review（38%）。

**预期失败模式**：(1) 短题上技能无收益甚至负收益（作者自述 BigCodeBench 推理模式下结果混合）；(2) purpose indexing 可能挤掉局部相关候选，pass rate 效果混合；(3) 单一 checkpoint 无重复种子，无法区分学习速度与最终策略差异——若你要下「RL 中位置效应」的结论，必须自行补种子与学习曲线。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| Grounded Skill Synthesis | 以可执行实现为证据来源、可被重建验证的技能合成范式 |
| Code2Skill | 从源代码仓库规模自动合成可复用程序性技能的四阶段流水线 |
| CodeSkillBank | 由 Code2Skill 构建的技能库，含 1,006,822 条接受记录，源自 19,769 个精选 GitHub 仓库 |
| Source-Body-Blind Reconstruction | 仅给技能记录、不给源代码体，让 LLM 重建实现以检验接地性 |
| Source-Aware Comparison | 源感知评判器将重建结果与原始代码比对，判定技能是否有支撑 |
| Atomic / Composite / Recurring-Pattern Skill | 原子操作、复合工作流、重复模式三类技能记录粒度 |
| Purpose Indexing | 按「任务族 + 意图动作 + 意图目标」归一化键聚类，选代表记录以减少冗余候选 |
| Provenance | 记录保留的来源、支撑代码跨度、记录类型与构建状态，支持审计与再生成 |
| Trajectory-Derived Skill Bank | 从智能体执行轨迹蒸馏技能的技能库，如 Trace2Skill、ExpeL、SkillRL-Bank |
| Post-Generation Review | 在候选解生成后引入技能进行审查与修订的接入方式 |

记号（对应 §4.2 式 (1)）：$\mathcal{B}$ 为当前评测可访问的检索面向技能库；$q_t$ 为决策步 $t$ 前的检索查询；$z_t$ 为渲染后的技能上下文，无查询时 $z_t=\varnothing$；$k$ 为检索深度（返回记录数）；$h_t$ 为决策步 $t$ 前的智能体或模型状态；$\theta^{(s)}$ 为被评测的模型或策略检查点。渲染与采样写作

$$z_t=\mathrm{Render}_r\!\left(\mathrm{TopK}_k(q_t;\mathcal{B})\right),\qquad a_t\sim\pi_{\theta^{(s)}}(\cdot\mid x,h_t,z_t).$$

无技能对照即同一协议下 $z_t=\varnothing$。注意 $\theta^{(s)}$ 在训练期设置中决定技能对谁可见（如对 verifier 或 reward model 可见而对被评判的策略轨迹隐藏）。缩写：SWE 指 SWE-bench Verified，BigCode 指 BigCodeBench，Terminal 指 TerminalBench，Avg 为所展示基准分数的未加权宏平均。

## 自测

以下问题用于检验你是否真正掌握了本文证据的边界，而非仅记住结论。

**Q1（跨小节）** 论文同时报告了「宏平均 42.90→47.90」与「Code2Skill 平均 49.5」。这两个数字能否直接比较？为什么？

<details><summary>答案</summary>
不能。42.90/47.90 来自 §5.2 表1 的八基准协议匹配对照（No/Yes CodeSkill），而 49.5 来自 §5.3 表2 的七基准技能来源比较（DS4-Flash reasoning，五轮均值）。两者基准集合、对照条件与聚合口径不同。论文自身也提示：Avg 列与七基准汇总都是「displayed benchmark scores 的未加权宏平均」，混合了不同评测器与任务数，属描述性汇总而非任务级合并成功率。
</details>

**Q2** 表1 中「57 of 72 提升」是否意味着技能在所有任务族上都稳定有效？

<details><summary>答案</summary>
不是。作者明确指出 BigCodeBench 在 reasoning mode 下结果混合，并解释为「短问题、强模型已能直接解决时技能收益较小」。此外表1 中确有下降项（如 Qwen3.5 27b 的 AgentBench 55.56→50.69、Qwen3.6 的 AgentBench 55.56→52.78）。因此 57/72 是总体计数，不构成逐族一致性。
</details>

**Q3（跨小节）** RQ4 的「摘要渲染减少 88.9% 上下文」与 RQ5 的「summary prompt 31% vs full prompt 32%」是否互相支持？

<details><summary>答案</summary>
方向一致但强度不同，且不可互相替代。RQ4 在 BigCodeBench Instruct-Hard 上显示 k=3 摘要渲染把平均技能上下文从 6,352 降到 707 字符，Qwen 保持全记录分数、DS4-Flash 从 28.40 升到 31.80。RQ5 在 SWE-World 编码 RL 中显示 summary prompt 31% 略低于 full prompt 32%，但两者都高于无技能 24%。前者是推理期上下文效率证据，后者是训练期单检查点证据，不能合并推断。
</details>

**Q4** 关于「生成后审查最优」这一结论，证据强度如何？

<details><summary>答案</summary>
属初步证据。RQ5 在共享训练步 150 上报告：无技能 24%、full prompt 32%、summary prompt 31%、reward reference 31%、post-generation review 38%。作者自述该实验「只报告单一检查点，没有重复种子或学习曲线」，因此不能确立学习速度、收敛性或最终策略性能上的差异。证据表中该主张亦被标注为「存疑」。
</details>

**Q5** RQ6 能否支持「AI 生成代码可等价替代人类代码作为技能来源」？

<details><summary>答案</summary>
不能。LiveCodeBench 400 题子集上人类代码库 93.00%、AI 代码库 93.50%，总体仅差 0.50 个百分点，但两者在 16 个任务上不一致（人类独解 7 个，AI 独解 9 个）。作者明确表示这一微小总体差异「不足以确立等价性」，结论只支持 AI 代码可作为持续扩展技能库的来源。
</details>
