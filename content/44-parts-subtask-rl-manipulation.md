---
id: parts-subtask-rl-manipulation
title: PARTS：瓶颈子任务残差RL适配长程操作
summary: 预训练VLA策略在长程操作任务中，失败集中在少数瓶颈子任务（如高精度插入、影响后续执行的准备动作）。全任务RL因稀疏终端奖励和有限真实机器人时间而低效，SFT重复采集完整演示代价高。
stage: SYSTEMS
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 44
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.21788
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 5
full_text_url: https://arxiv.org/html/2609.21788
objectives: [理解PARTS如何冻结预训练VLA、仅在瓶颈子任务上训练有界残差策略, 掌握策略选择器、成功验证器与自动重置策略三个可执行程序的分工, 了解成功重加权再训练机制及其消融证据, 评估真实世界RL微调在长程操作任务中的样本效率与人工成本权衡]
tags: [residual-rl, vla-finetuning, long-horizon-manipulation, real-world-rl, bottleneck-subtask, td3-bc]
sources: [from-pretraining-to-proficiency-real-wor]
related: [lab-agent-rl, mintrl-off-policy-intervention, evolvetrade-policy-refinement]
prerequisites: []
---
## 问题与语境

预训练 VLA 策略（如 π0.5）已能执行大量操作行为，但迁移到新的长程任务时，目标场景往往要求改变抓取策略、接触行为、空间布局或相邻动作间的协调。SFT 是直接解法，但对长程任务反复采集完整演示代价高昂——即使其中大部分子任务已经可靠工作，人类仍要为整条轨迹付出标注与遥操作成本。

论文的起点观察是：失败并非均匀分布，而是集中在少数「瓶颈子任务」上。这类瓶颈既包括高精度操作（如耳塞插入），也包括其终态决定后续难度的准备动作（如把耳塞盒握成便于插入的朝向）。作者用 $R=\prod_{i=1}^{N}\phi_i$ 刻画这一结构：若基础策略在子任务 $i$ 上的成功率 $p_i$ 偏低，则 $\Pr[R=1]\approx\prod_i p_i$，少数低 $p_i$ 的子任务就封顶了整任务成功率。

已有做法在此失效的方式有两种。其一是全任务真实世界 RL 微调（DSRL、EXPO-FT、RLT）：它们追求全局策略改进，但奖励是 20–120 s episode 末端的稀疏二值信号，基础成功率低时回放缓冲区里几乎没有成功轨迹，critic 学习困难、信用分配跨度长；同时预算被均匀摊到基础策略本已可靠的子任务上，留给瓶颈的尝试次数很少。其二是 SFT 重复采集完整演示，成本随任务长度线性增长。

论文的定位因此不是「更好的 RL 算法」，而是对真实世界 RL 练习位置的重新组织：冻结 VLA，只在人类指定的瓶颈处训练有界残差策略，用 3–15 s 子任务窗口的局部结果奖励 $r_k=\phi_k$ 替代整任务稀疏奖励，并用可执行程序（策略选择器、成功验证器、自动重置策略）把结果标注与场景重置局部化，使训练 rollout 无需人工纠正或切换决策。它属于「失败局部化的策略修复」，而非全局策略改进。

## 核心主张

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | PARTS 把全任务成功率从 32% 提升到 61%（YAM 耳塞），从 50% 提升到 95%（Franka 线缆），平均每任务仅需数十分钟真实世界 RL rollout | §I INTRODUCTION 贡献段；§IV-C Q1 | 作者主张 |
| C2 | 在匹配机器人 rollout 预算下，PARTS 比现有真实世界 RL 微调方法（DSRL、EXPO-FT、RLT）全任务成功率高 25% 以上，且所需人工介入更少 | §I INTRODUCTION；§IV-C Q2；表 I | 作者主张 |
| C3 | 成功重加权再训练是性能关键机制：移除后子任务与全任务成功率均下降 | §IV-C Q3；图 4 斜线柱 | 作者主张 |
| C4 | 仅修正夹爪闭合即可把 LEGO 分拣进度从 54% 提升到 82%，仅用 17 min RL rollout | §IV-C Q1 | 作者主张 |
| C5 | 局部奖励窗口（3–15 s，初始成功率高于 25%）比整任务稀疏奖励提供更频繁正反馈并缩短信用分配跨度 | §IV-C Q2；§IV-A | 作者主张 |

最强的是 C1 与 C4 这类「单任务、单指标、有明确数值」的结果：它们直接对应 §IV-C Q1 的逐任务报告，且评估协议明确（每任务 20 条完整 episode，从全任务初始状态出发，§IV-A），读者可以据此判断效应量级。C4 尤其干净——LEGO 只报告进度分数，因为二值结果会退化为「是否放好一块砖」，作者对此给出了理由。

最弱的是 C2。它依赖跨方法比较，而比较的可控性有限：作者自述「比较控制的是机器人数据采集时间，wall-clock 与算力成本可能不同」（limits），且 RLT 在 LEGO 上无法表达该任务（抓取瓶颈每块砖复发、需反复切换），只能退化为全任务 RL 运行，这使「同一预算下的一致优势」在不同任务上的含义并不齐整。此外 C2 的「25% 以上」是相对提升还是绝对百分点，摘录中未明确，读者不应自行换算。

C3 的强度居中：消融只在耳塞任务上做，且只对 RL1、RL2 施加再训练（RL0 因基础成功率高、重置即任务初始条件而未再训练），因此它是机制性证据而非跨任务普适结论。所有五条均为作者主张，本档案未发现独立复现记录。

## 机制与方法

PARTS 的核心主张是：长程任务的失败集中在少数瓶颈子任务上，因此真实世界 RL 的机器人交互时间应只花在这些瓶颈处，其余阶段保留预训练策略的可靠性。方法把「在哪里学、学什么、何时交还控制权」拆成可执行契约与轻量残差策略两部分。

问题设定：一个 episode 被建模为 $N$ 个子任务 $\sigma_1,\dots,\sigma_N$，子任务 $i$ 从入口状态集 $\mathcal{E}_i\subset\mathcal{S}$ 进入，在其结果判据 $\phi_i:\mathcal{S}\to\{0,1\}$ 于出口被评估或超时后结束。完整任务只有稀疏二值奖励 $R\in\{0,1\}$，且因所有子任务都成功才算成功，可分解为

$$R=\prod_{i=1}^{N}\phi_i .$$

若基础策略从典型入口完成子任务 $i$ 的概率为 $p_i$，则 $\Pr[R=1]\approx\prod_i p_i$，少数低 $p_i$ 的子任务即瓶颈，其索引集记为 $\mathcal{K}\subseteq\{1,\dots,N\}$，$K=|\mathcal{K}|$。瓶颈可能早于可见失败出现：当 $\sigma_{i-1}$ 的终态决定 $\sigma_i$ 的难度时，瓶颈向前延伸，其成功判据要求一个适合执行 $\sigma_i$ 的构型。瓶颈可成有序链、可互为备选，也可在同一 episode 内重复（如每个物体都要抓一次）。子任务 $i$ 的入口分布 $\mu_i$ 由从任务初始条件执行 $\sigma_1,\dots,\sigma_{i-1}$ 诱导；也可从重置程序准备的 restaged 分布 $\hat{\mu}_i$ 进入，二者不必相等。目标是最大化全任务成功率。

方法流程：先在专家演示 $\mathcal{D}_{\text{exp}}$ 上 SFT 得到任务基础策略 $\pi_0$（由预训练 VLA $\pi_{\text{VLA}}$，本文为 $\pi_{0.5}$ 得到），通过真实机器人评估识别瓶颈 $\mathcal{K}$。人类为每个瓶颈编写契约：入口集 $\mathcal{E}_k$、可修正动作坐标及其边界、结果判据 $\phi_k$、运动预算，并附少量子任务演示。编码智能体据此生成三个可执行程序：策略选择器（由图像、本体感受与运动谓词输出 $g_t$，仅在观测满足入口条件时激活残差 $k$，否则由基础策略控制；支持有序序列或入口条件成立者之间的选择，并允许入口重现时重复激活）、成功验证器（在人类定义的事件门满足后检验契约后置条件，必要时要求跨观测持续，返回 1/0；不确定时请求人工标注，人工可覆盖自动标签）、自动重置策略（在每次终止标签后决定重试还是重置：失败且起始条件仍成立则直接重试，成功且改变了起始条件则需重置，机器人可行时自行恢复，否则由人完成）。

学习部分：VLA 保持冻结，提供参考动作块与视觉特征，并界定残差可作用的邻域。每个瓶颈训练一个轻量、有界的残差 actor-critic，用在线 TD3+BC 更新，只修正少数动作维度，奖励为该子任务自身的局部结果 $r_k=\phi_k$；完整任务结果 $R$ 仅用于评估。这一设计把 20–120 s episode 的稀疏终端奖励替换为 3–15 s 子任务窗口的局部奖励，缩短信用分配 horizon 并提供更频繁的正反馈。

成功重加权再训练与再部署：在线更新对基础成功率低的瓶颈信号很弱（多数尝试失败，replay 中受奖励转移稀少）；同时为省重置时间，尝试常被 restaged 到子任务起始条件而非任务初始状态，连续尝试看到近乎相同的场景，在线更新会过拟合该构型。因此 PARTS 周期性在成功重加权的 replay 副本上重训残差并再部署：

$$\widetilde{\mathcal{D}}_{k}=\mathcal{D}_{k}^{+}\cup\operatorname{Sample}_{\rho}(\mathcal{D}_{k}^{-}),$$

即保留全部成功 episode，并均匀采样比例 $\rho$ 的失败 episode，从而在所有 restaging 上提高受奖励经验占比，同时保留部分失败作为负样本。新 actor 与 critic 在该固定数据集上训练，由操作者选择候选 checkpoint；选中的 checkpoint 与 curated replay buffer 初始化新一轮在线运行，随新 rollout 继续更新。重训练因此改变后续数据收集所用的策略，而非仅作为最终策略抽取步骤。

推理时，固定残差在其入口被激活，在其出口把控制权交还基础策略，使完整任务继续执行并按需激活后续残差。

适用前提与取舍：方法假设存在少量可识别的瓶颈子任务、每个瓶颈有可判定的结果判据、且基础策略在瓶颈处有足够高的初始成功率以支撑有效局部探索（论文报告局部奖励窗口初始成功率高于 25%）。它依赖人类指定瓶颈、协助 setup 并在必要时物理重置；训练 rollout 本身无需人工动作纠正、切换决策或结果标注。与全任务 RL 微调相比，PARTS 不更新 backbone，因而无法修正非瓶颈阶段的系统性缺陷；与单阶段 RLT 式 handoff 相比，它需要协调基础策略与多个专用残差之间的反复切换。

## 实验设置

论文在三个长程真实机器人任务上评估 PARTS，覆盖双臂 YAM 与单臂 Franka FR3 两个平台。任务时长 20–120 s（约 600–3,600 控制步，30 Hz），瓶颈子任务通常持续 3–15 s（90–450 控制步）。评估为每个任务 20 个完整 episode，从全任务初始状态开始；除二值全任务成功率外，还报告归一化 progress score（earbud 每完成一阶段记 1/3，成功需三阶段全成；cable 拔出与插入各记 1/2，成功需两者皆成；LEGO 因是十块积木的重复 pick-and-place，只报告 progress，即截止时间前分拣的积木比例），并在同一批 episode 内报告各阶段成功率。所有 RL 方法从同一 $\pi_{0.5}$-SFT 基础策略出发，训练使用相同的机器人 rollout 时间（按 RL rollout 期间机器人实际耗时计，不含物理重置与 RL 更新暂停），且 RL rollout 期间不使用纠正性遥操作或 DAgger 式人工干预；所有基线使用人工重置与人工奖励标注（LEGO 上标签为 episode 内分拣积木比例）。比较控制的是机器人数据采集时间，wall-clock 与计算成本可能不同。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
| --- | --- | --- | --- | --- |
| Earbud insertion（双臂 YAM） | PARTS（π0.5 backbone） | SFT base policy | 平均每任务数十（tens of minutes）真实世界 RL rollout | full-task success rate |
| Cable unplug-and-plug（单臂 Franka FR3） | PARTS（π0.5 backbone） | SFT base policy | 29 min RL rollouts | insertion success |
| LEGO sorting（双臂 YAM） | PARTS（π0.5 backbone） | SFT base policy | 17 min RL rollouts | progress score（十块积木中已分拣比例） |
| YAM 任务（earbud、LEGO） | PARTS（π0.5 backbone） | DSRL、EXPO-FT、RLT | 匹配的机器人 rollout 预算 | full-task success |
| Franka 任务（cable） | PARTS（π0.5 backbone） | SFT base policy | 未说明 | full-task success rate |
| 全部三个任务 | PARTS（π0.5 backbone） | DSRL、EXPO-FT、RLT | 相同机器人 rollout 时间 | full-task success |
| Earbud insertion（双臂 YAM） | PARTS 去掉 success-reweighted retraining | PARTS（含 retraining） | 未说明 | subtask 与 full-task success |

任务细节：earbud 任务中机器人打开充电盒、左手持盒、右臂插入两只耳机并合盒，瓶颈为 case preparation（RL0）、first insertion（RL1）、second insertion（RL2）；LEGO 任务需在 150 s 内把十块积木分入三个颜色箱，SFT 演示来自公开 ABC-130k 数据集，其积木比本文所用更大，故标称夹爪常闭合不足，瓶颈为任一臂的抓取；cable 任务中机器人从源路由器拔出线缆并插入目标路由器，瓶颈为对齐与插入。奖励与重置协议按结果识别难度与场景恢复难度而定：LEGO 与 cable 由自动成功验证器提供全部奖励；earbud 因 VLM 难以区分已就位耳机与搁在盒上的耳机，由人工检查验证器标签，且当重置超出机器人硬件能力（如取出已就位耳机）或场景无法自主恢复（如耳机落地）时需人工介入。RLT 无法表达 LEGO sorting（抓取瓶颈每块积木都重现、需在 VLA 与残差间反复切换），故 LEGO 上以全任务 RL 运行 RLT。

## 证据与结果

下表汇总全文摘录中可确认的数字。凡摘录未给出者，一律标注「摘录未给出」，不做推断。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| 全任务成功率 | 32% → 61% | YAM（earbud insertion），PARTS vs base policy | §I INTRODUCTION |
| 全任务成功率 | 50% → 95% | Franka（cable unplug-and-plug），PARTS vs base policy | §I INTRODUCTION |
| 全任务成功率提升 | more than 25% | PARTS vs 现有真实世界 RL 微调方法 | §I INTRODUCTION |
| 插入成功率 | nearly doubles | cable 任务，仅 29 min RL rollouts 后 | §IV-C Experimental Results |
| 全任务成功率 | four times the base policy's | earbud 任务，PARTS | §IV-C Experimental Results |
| 每阶段成功率（两次插入） | 提升 20-35 percentage points | earbud 任务，相对 base policy | §IV-C Experimental Results |
| 进度分数 | 54% → 82% | LEGO sorting，仅修正夹爪闭合，17 min RL rollouts | §IV-C Experimental Results |
| 每任务评测回合数 | 20 | 从全任务初始状态开始的完整回合 | §IV-A Tasks and Setup |
| LEGO 分拣砖块数 | ten | 三个颜色箱，150 s 内 | §IV-A Tasks and Setup |
| 任务时长 | 20–120 s（约 600–3,600 control steps @ 30 Hz） | 三个长程任务 | §IV-A Tasks and Setup |
| 瓶颈子任务时长 | 3–15 s（90–450 control steps） | 瓶颈子任务 | §IV-A Tasks and Setup |
| 瓶颈子任务初始成功率 | above 25% | PARTS 局部奖励窗口 | §IV-C Experimental Results |
| LEGO 时限 | 150 s | LEGO sorting 任务 | §IV-A Tasks and Setup |
| 平均 RL rollout 预算 | tens of minutes per task | YAM 与 Franka 任务平均 | §I INTRODUCTION |
| cable 任务 RL rollout 预算 | 29 min | cable 任务 | §IV-C Experimental Results |
| LEGO 任务 RL rollout 预算 | 17 min | LEGO 任务 | §IV-C Experimental Results |

对照与消融。Q2 的对照为 DSRL、EXPO-FT、RLT，均在相同机器人 rollout 时间下训练，且不使用纠正性遥操作或 DAgger 式人工干预；摘录称 PARTS 在难度不同的任务上一致优于全部基线，并指出 EXPO-FT 最终低于 base policy，RLT 与 DSRL 在有限真实世界预算下平均未显著超过 SFT 策略。Q3 的消融在 earbud 任务上仅对 RL1 与 RL2 移除成功重加权再训练（RL0 未重训练，因其 base 成功率已高且重置即任务初始条件），结果为子任务与全任务成功率均下降（Fig. 4 斜线柱）。摘录未给出该消融的具体数值，也未给出各基线的逐任务数值表。

需注意的口径问题：YAM 的 32%→61% 与「four times the base policy's」在摘录中同时出现，前者约为 1.9 倍，二者是否对应同一评测口径（全任务二值成功 vs 其他统计）摘录未明确说明，本档案不做调和。

## 证据强度评估

证据分级：B（单一来源、真实机器人实验、有匹配预算对照与消融，但缺统计显著性与独立复现）。

理由：结论建立在两个真实平台、三个长程任务上，每任务 20 个完整回合，且与三个已发表 RL 微调基线在「相同机器人 rollout 时间」下对照，并配有成功重加权再训练的消融，这超出纯演示型工作的证据水平。但全部数字来自作者自建任务与自建评测流程，无第三方复现，无置信区间或显著性检验，故不足以评为 A。

主要威胁：

1. 统计显著性未报告。每任务仅 20 个完整回合，32%→61% 对应约 6/20 与 12/20，50%→95% 对应约 10/20 与 19/20；摘录未给出方差、置信区间或检验，小样本下「more than 25%」的基线差距可能落在噪声范围内。

2. 构造效度与评测口径。全任务成功、progress score、per-stage success 三种口径混用，且 LEGO 只报 progress（因二值结果会退化为「是否放好一块砖」）。YAM 的 32%→61% 与「four times」并存，口径关系摘录未澄清，读者难以判断哪一数字对应部署时的真实可靠性。

3. 外部效度与人工依赖。任务仅覆盖 YAM 双臂与 Franka FR3 单臂、三类操作；瓶颈由人类从真实机器人评测中识别并编写契约，earbud 任务还需人工检查验证器标签并在机器人无法恢复场景时人工重置。因此「less human involvement」是相对基线而言，并非零人工，迁移到新任务时的人工成本未被量化。

4. 基线选择与公平性边界。对照仅控制机器人数据采集时间，摘录明确承认 wall-clock 与 compute 成本可以不同；RLT 在 LEGO 上被迫退化为全任务 RL（因其无法表达每块砖重复出现的抓取瓶颈），EXPO-FT 未使用其发表设定中的人工干预与自动奖励检测器。这些改动方向对基线不利，削弱了「一致优于全部基线」的强度。

## 边界与反例

**什么观察会推翻结论。** 论文的核心因果链是「失败集中在少数瓶颈子任务 → 只在瓶颈处做残差 RL → 全任务成功率大幅提升」。若出现以下观察，该结论即被削弱或推翻：

- 瓶颈不可由人类事先稳定识别。PARTS 的入口集 $\mathcal{E}_k$、判据 $\phi_k$、可修正动作坐标与边界全部由人类从真实机器人评估中写出契约（§III-C）。若在同类任务上，不同标注者给出的瓶颈集合差异很大，或瓶颈随训练进程漂移（例如 RL0 修好后 RL1 的失败模式改变），则「一次性指定瓶颈」的前提失效。
- 瓶颈之间强耦合，局部奖励无法分解。论文假设 $R=\prod_i \phi_i$，且每个瓶颈有独立局部奖励 $r_k=\phi_k$。earbud 任务中作者自己承认「a poor holding pose propagates to both insertions」，即 $\sigma_{i-1}$ 的终态决定 $\sigma_i$ 的难度，瓶颈会向前延伸。若耦合强到局部判据 $\phi_k$ 在瓶颈外被满足却在全任务中无用，局部奖励就会奖励错误行为。
- 基线在同等预算下被公平调优后追平。论文称 PARTS 比现有真实世界 RL 微调方法全任务成功率高「more than 25%」，但该数字来自作者自述的匹配 rollout 预算比较，且 RLT 无官方代码、为「reproduced from the paper」，DSRL/EXPO-FT 在 YAM 上是作者重实现（仅改机器人接口）。若独立复现中基线调参后差距消失，结论不成立。

**最可能失效的条件。** 论文明确列出初始成功率门槛：局部奖励窗口的初始成功率需「above 25%」（§IV-C）。若某瓶颈的 base 成功率远低于此，局部奖励同样稀疏，PARTS 退化为全任务稀疏奖励的困境。此外，任务时长 20–120 s、瓶颈 3–15 s 是本文的适用范围；瓶颈占比更高（接近全任务）时，「只练瓶颈」相对全任务 RL 的预算优势消失。人类介入也是硬约束：earbud 上需人工核对验证器标签、人工重置（如从盒中取出已就位的耳机、耳机落地后恢复场景），LEGO 与 cable 才全自动。

**作者未验证、读者可能误推的方向。**
1. 误推「PARTS 可零人工」。作者在结论中把「自动识别瓶颈、生成稠密子任务奖励、构造恢复阶段」列为 future work，说明当前仍需人类指定瓶颈与契约。
2. 误推「残差维度越少越好」。论文只报告了「仅修正夹爪闭合」使 LEGO 进度 54%→82%，未做可修正动作维度数量的系统消融。
3. 误推「成功重加权再训练在任何任务上都关键」。该消融仅在 earbud 的 RL1/RL2 上做（RL0 因 base 成功率已高、重置即任务初始条件而未重训练），不能外推到 base 成功率高的瓶颈。
4. 误推「wall-clock 与算力也更省」。作者明确说明比较只控制机器人数据采集时间，「wall-clock and compute costs can differ」。
5. 误推「RLT 在 LEGO 上被公平击败」。作者说明 RLT 无法表达 LEGO 分拣（抓取瓶颈每块砖复发、需反复切换），因此在 LEGO 上把 RLT 当作全任务 RL 运行——这是能力不匹配，而非同等条件下的性能对比。

## 与知识库的关系

以下按相关笔记逐条对照，标注「新增 / 印证 / 张力」。笔记 id 为建议链接名。

**note: real-world-rl-finetune-vla（DSRL / EXPO-FT / RLT 一类真实世界 RL 微调）**
- 新增：PARTS 把 RL 练习范围从「全任务」改为「瓶颈子任务」，并用可执行契约（策略选择器、成功验证器、自动重置策略）替代人工纠正与人工切换。这是对「全局策略改进」范式的一次范围收缩。
- 印证：该笔记中「真实机器人 rollout 时间是最稀缺资源」的判断——PARTS 在匹配 rollout 预算下报告全任务成功率提升「more than 25%」，且训练 rollout 无需人工纠正或切换决策。
- 张力：论文报告 EXPO-FT「ultimately underperforms the base policy」，并推测稀疏全任务奖励驱动的 backbone 更新会破坏非瓶颈子任务中原本可靠的行为。这与「继续更新 VLA backbone 有益」的直觉相冲突，值得在该笔记中标注为待复核的反例。

**note: sparse-reward-credit-assignment（长程稀疏奖励与信用分配）**
- 新增：用 3–15 s 子任务窗口的局部结果奖励替代 20–120 s episode 的终端奖励，把信用分配 horizon 从约 600–3,600 控制步（30 Hz）缩短到 90–450 步，并要求局部初始成功率「above 25%」。
- 印证：稀疏终端奖励下 replay buffer 中成功轨迹稀少、critic 学习困难，是长程任务 RL 的公认瓶颈。
- 张力：PARTS 并未解决稀疏奖励本身，只是把稀疏性局部化；当瓶颈 base 成功率低于 25% 时该机制失效，这与「分层/子目标分解可普遍缓解稀疏性」的乐观表述存在张力。

**note: residual-rl-frozen-policy（残差 RL 与冻结基座）**
- 新增：残差被限制在「有界动作维度」上，且推理时在瓶颈入口激活、出口交还控制权，形成可重复的多次切换；这与 RLT 的「单次人工 handoff、之后 RL 全程接管、不交还」形成明确对照。
- 印证：冻结 VLA + 轻量残差 actor-critic（在线 TD3+BC）是稳定且样本高效的适配方式。
- 张力：RLT 无法表达「同一瓶颈在 episode 内反复出现」的任务（LEGO 每块砖都要抓），说明「单次切换」式残差设计在重复瓶颈场景下不适用——这是对残差 RL 适用范围的一条边界。

**note: human-in-the-loop-cost（人类监督成本）**
- 新增：把结果标注与重置「局部化」为可执行程序，使 RL rollout 阶段无需人工纠正或切换决策；论文用 Table I 逐方法对比 Rollout / Reward / Reset 三项人工介入。
- 印证：人工介入是真实世界策略学习可扩展性的主要瓶颈。
- 张力：earbud 任务仍需人工核对验证器标签（就位耳机与搁在盒上的耳机对未做任务特定后训练的 VLM 难以区分）与部分物理重置，因此「无需人工」只成立于 LEGO 与 cable。

**note: success-reweighted-retraining（成功重加权重训练与再部署）**
- 新增：curated 数据集 $\widetilde{\mathcal{D}}_k=\mathcal{D}_k^{+}\cup\operatorname{Sample}_{\rho}(\mathcal{D}_k^{-})$ 保留全部成功回合与均匀采样的 $\rho$ 比例失败回合；重训练后的 checkpoint 与 curated replay 初始化新一轮在线训练，即重训练改变的是后续数据采集所用的策略，而非仅作最终策略抽取。
- 印证：重放缓冲中成功样本占比过低会阻碍学习。
- 张力：消融仅在 earbud 的 RL1/RL2 上完成（RL0 未重训练，因其 base 成功率已高且重置即任务初始条件），因此「重训练普遍关键」这一推广缺乏证据，应标注为不确定。

## 复现与验证计划

目标：在自有平台上验证「把真实世界 RL 限制在瓶颈子任务」是否比全任务 RL 微调更省机器人时间。以下为最小可执行方案，所有数字均取自原文，未标注处为不确定。

**环境与任务**：选一个长程任务（20–120 s，约 600–3,600 控制步 @30 Hz），瓶颈子任务时长 3–15 s（90–450 控制步）。原文三任务为 bimanual YAM 的 earbud insertion、LEGO sorting（十块积木分三色箱，限时 150 s）与单臂 Franka FR3 的 cable unplug-and-plug。建议先复现 LEGO：瓶颈单一（夹爪闭合），且原文称仅修正夹爪闭合即把进度从 54% 提到 82%，只用 17 min RL rollout。

**数据与基座**：SFT 基座用 π0.5（原文 backbone），LEGO 演示来自公开 ABC-130k（注意原文指出其积木比自研的大，导致标称夹爪闭合不足——这是可预期的初始失败来源）。冻结 VLA，仅训练有界残差 actor-critic（在线 TD3+BC），局部奖励 $r_k=\phi_k$。

**基线**：SFT 基座、DSRL、EXPO-FT、RLT。注意 RLT 无法表达 LEGO（抓取瓶颈每块积木复现、需反复切换），原文在 LEGO 上把 RLT 当全任务 RL 跑；若照此复现需在报告中注明该不对等。

**预算与判据**：匹配机器人 rollout 时间（原文按 RL rollout 的机器人耗时计，排除物理重置与更新暂停；wall-clock 与算力成本可不同）。评测 20 个完整 episode，从全任务初始状态起；主判据为二值全任务成功率，辅以归一化进度分（LEGO 为限时内分拣比例）与 per-stage 成功率。

**预期失败模式**：(1) 基座成功率过低（原文要求瓶颈初始成功率高于 25%）时局部奖励过稀，残差学不动；(2) 重置被 restage 到子任务起点而非任务初始态，连续尝试场景近乎相同，在线更新过拟合该配置，评测时因前序标称行为带来的状态变化而失效——这正是原文引入成功重加权再训练的理由，消融显示移除后子任务与全任务成功率均下降；(3) 若瓶颈判定错误或验证器标签不可靠（earbud 上需人工核对），奖励信号被污染。建议先做移除再训练的消融以确认该机制在自有场景是否同样关键。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| VLA | 视觉-语言-动作模型，输入图像与语言指令、输出机器人动作 |
| $\pi_{\mathrm{VLA}}$ | 预训练通用 VLA 基座（本文为 π0.5） |
| $\pi_0$ | 在专家演示 $\mathcal{D}_{\text{exp}}$ 上 SFT 后的任务基座策略，所有 RL 方法的起点 |
| SFT | 监督微调，在专家演示上对预训练模型做有监督训练 |
| Action Chunking | 动作分块：每次重规划预测 $C$ 个未来动作 $\bar{A}_t=(\bar{a}_t,\dots,\bar{a}_{t+C-1})$，执行其中 $E\le C$ 个前缀后再预测 |
| $o_t,\ p_t$ | 观测（多视角 RGB）与本体感受状态 |
| $\sigma_i$ | 第 $i$ 个子任务；episode 由 $N$ 个子任务 $\sigma_1,\dots,\sigma_N$ 组成 |
| $\phi_i$ | 子任务 $i$ 的结果判据，$\phi_i:\mathcal{S}\to\{0,1\}$ |
| $R$ | 完整任务的稀疏二值奖励，$R=\prod_{i=1}^{N}\phi_i$ |
| Bottleneck Subtask | 瓶颈子任务：基座成功率 $p_i$ 低、从而限制全任务成功的子任务 |
| $\mathcal{K},\ K$ | 瓶颈子任务索引集及其大小 $K=|\mathcal{K}|$ |
| $\mathcal{E}_i,\ \mu_i$ | 子任务 $i$ 的入口状态集与入口分布；$\hat{\mu}_i$ 为重置程序准备的 restaged 分布 |
| Residual Policy | 残差策略：在基座参考动作块上施加有界修正的轻量策略 |
| TD3+BC | 双延迟 DDPG 与行为克隆结合的在线 RL 算法，用于更新残差 |
| $r_k=\phi_k$ | 瓶颈 $k$ 的局部奖励，即该子任务自身的结果判据 |
| Contract | 契约：人类为瓶颈定义的入口集、可修正动作坐标及边界、结果判据与运动预算 |
| Policy Selector | 策略选择器：依据观测判断是否激活某残差策略的可执行程序 |
| Success Verifier | 成功验证器：检验子任务后置条件并输出局部奖励的程序 |
| Auto-Reset Policy | 自动重置策略：决定失败重试还是场景恢复的程序 |
| Success-Reweighted Retraining | 成功重加权再训练：在保留全部成功回合与均匀采样比例 $\rho$ 的失败回合的数据集 $\widetilde{\mathcal{D}}_k=\mathcal{D}_k^{+}\cup\operatorname{Sample}_{\rho}(\mathcal{D}_k^{-})$ 上重训残差并再部署 |
| $\rho$ | 再训练时保留失败回合的采样比例 |

## 自测

以下问题用于检验读者是否真正掌握了 PARTS 的证据边界，而非仅记住数字。答案中标注了「作者主张」与「已复现/共识」的区分。

**Q1.** 论文报告 YAM 上全任务成功率从 32% 提升到 61%，Franka 上从 50% 提升到 95%。这两个数字的评测协议是什么？为什么 LEGO 任务不报告二值全任务成功率？

<details><summary>答案</summary>
评测协议为每个任务 20 个完整 episode，从全任务初始状态出发（§IV-A）。LEGO 是十块积木的重复 pick-and-place，二值结果会退化为「是否放置了单块积木」，因此只报告进度分数（截止时间前分拣的积木比例），LEGO 时限 150 s。注意 32%→61% 与 50%→95% 均为作者主张（§I INTRODUCTION），非第三方复现。
</details>

**Q2.** PARTS 声称「训练 rollout 无需人工纠正、切换决策或结果标注」。这是否意味着整个流程完全无需人类？请结合 Table I 与 §IV-A 说明。

<details><summary>答案</summary>
不是。Table I 中 PARTS 的 Rollout 与 Reward 列标为 ✓（自主），但 Reset 列标为 ✓‡，脚注说明：LEGO 与 cable 上自动，earbud 上需人工检查验证器标签，且当机器人无法恢复场景时由人工重置。§IV-A 进一步给出原因：对 VLM 而言，已就位的耳塞与搁在盒上的耳塞外观相似，故需人工核对标签；取出已就位的耳塞超出硬件能力、耳塞落地后场景无法自主恢复，均需人工。人类仍需指定瓶颈、协助 setup 与执行物理重置。
</details>

**Q3.** 为什么 PARTS 用 3–15 s 子任务窗口的局部奖励，而不是 20–120 s episode 的终端奖励？请从信用分配与正反馈频率两个角度解释，并说明这一设计对基线对比的含义。

<details><summary>答案</summary>
全任务奖励是稀疏二值 $R=\prod_i \phi_i$，只有所有子任务成功才为 1；当基座成功率低时，replay buffer 中几乎没有成功轨迹，critic 学习困难，且信用分配 horizon 长达 20–120 s。PARTS 的局部奖励 $r_k=\phi_k$ 作用在 3–15 s 窗口上，初始成功率高于 25%，正反馈更频繁、horizon 更短。对基线对比的含义：在匹配机器人 rollout 预算下，DSRL、EXPO-FT、RLT 把预算花在基座已能可靠完成的子任务上，且受稀疏终端奖励困扰；PARTS 把交互集中在瓶颈处，因此作者主张其全任务成功率高出 25% 以上（作者主张，非独立复现）。
</details>

**Q4.**（跨小节）成功重加权再训练在消融中被移除后子任务与全任务成功率均下降。请结合 §III-D 的 restaging 问题与 §IV-C Q3 的消融设置，解释为什么 RL0 没有被重训练，而 RL1、RL2 需要。

<details><summary>答案</summary>
§III-D 指出：为节省重置时间，尝试常被 restage 到子任务起始条件而非任务初始状态，连续尝试看到几乎相同的场景配置，在线更新会过拟合该配置，在评测时由前序 nominal 行为产生的状态变化下失效。§IV-C Q3 说明消融在 earbud 任务上仅对 RL1 和 RL2 施加再训练：二者基座成功率低、局部奖励稀疏，且都被 restage 到 RL0 的成功状态，因此需要成功重加权再训练（保留全部成功 episode 加均匀采样比例 $\rho$ 的失败 episode）来跳出局部最优。RL0 未重训练，因为其基座成功率已高，且其 reset 就是任务初始条件，尝试已覆盖评测分布。该结论为作者主张（图 4 斜线柱）。
</details>

**Q5.**（跨小节）论文称 PARTS 在匹配机器人 rollout 预算下优于 DSRL、EXPO-FT、RLT。这个「匹配」控制了哪些成本、没有控制哪些成本？为什么 RLT 在 LEGO 上被改为全任务 RL？

<details><summary>答案</summary>
匹配的是机器人数据采集时间，即 RL rollout 期间的机器人运行时间，排除物理重置与 RL 更新暂停；wall-clock 与计算成本可以不同（§IV-B）。因此「更优」不能直接推广为计算效率更优。RLT 在 LEGO 上被改为全任务 RL，是因为 RLT 无法表达 LEGO 分拣：其抓取瓶颈对每块积木反复出现，需要在 VLA 与残差之间反复切换，而 RLT 只有单次由人工选择的 VLA-to-RL handoff，之后 RL 策略控制剩余 episode 且不交还 VLA（§IV-B）。此外 EXPO-FT 在实验中最终低于基座策略，作者推测稀疏全任务奖励驱动的 backbone 更新会破坏非瓶颈子任务的可靠行为——此为作者解释，非独立验证。
</details>
