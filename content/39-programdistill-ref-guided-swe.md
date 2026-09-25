---
id: programdistill-ref-guided-swe
title: ProgramDistill：从交互式网页应用生成可验证 SWE 任务
summary: 现有编码智能体评测通常假设目标行为已被显式指定（issue、测试或指令）。但在实际网页开发中，开发者常需从一个可运行的参考应用（旧版本、原型、同类产品）中推断意图行为，再在当前不完整实现中复现。
stage: FRONTIER
track: 评估与安全
kind: paper
depth: deep
evidenceGrade: C
order: 39
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.18805
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 5
full_text_url: https://arxiv.org/html/2609.18805
objectives: [理解 application-to-task factorization：如何从交互式网页应用挖掘可重放行为并构造可验证 SWE 任务, 掌握 restoration depth 与 prerequisite lineage 作为可控难度轴的设计与评测含义, 读懂 logic-only 与 logic-and-UI 任务差距、深度效应及其对长上下文假设的反驳, 评估该基准在行为覆盖、应用规模与运行成本上的局限]
tags: [swe-agents, benchmark, task-generation, web-applications, long-context, evaluation]
sources: [programdistill-from-interactive-web-apps]
related: [harness-design-coding-agents, evaluation, environments]
prerequisites: []
---
## 问题与语境

现有编码智能体评测（SWE-bench 类 issue/测试驱动设置）普遍假设目标行为已被显式指定：issue 描述、自然语言指令或测试用例已经把「要做什么」交代清楚，agent 的任务只是定位并修改代码。论文指出这一假设在真实网页开发中经常不成立——开发者往往手上只有一个可运行的参考实现（旧版本、交互原型、同类产品、演示视频），需要先从参考中推断意图行为，再在不完整的当前实现里复现。这类「参考到当前」的行为蒸馏既要求交互式信息获取（观察参考应用的状态与反馈），又要求源码级实现能力，而现有基准把程序当作整体重建目标（如 ProgramBench 的 behavior-to-code），忽略了交互式 Web 应用特有的结构：功能通过 UI 动作与应用状态展开，并带有显式前置依赖（先登录才能建对象，先建对象才能改对象），这些依赖天然把行为组织成前置依赖链。

论文的定位不是再做一个「更难的重建基准」，而是提出一种把可运行应用转化为可验证 SWE 任务的变换：application-to-task factorization 把应用拆成带前置依赖的可重放行为与任务，reference-to-current distillation 则规定 agent 只能观察参考、不能读其源码，成功与否由挖掘阶段记录的可重放轨迹重放判定。由此得到的 restoration depth 成为一个可控难度轴，从原子修复延伸到全应用重建。其价值在于：任务与验证器同源（同一轨迹在完整应用上通过、掩蔽后失败、修复后重放通过），无需人工 issue、测试或行为标注，且深度轴可直接用作训练课程。

## 核心主张

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | mine–craft–patch 流水线可从 26 个应用自动挖掘 1,975 个可重放行为并构造 4,063 个任务，无需人工干预 | §1 贡献列表；§3.1 图 5；附录 A 表 3（Total 行 2862 / 1201 / 4063） | 作者主张 |
| C2 | 全应用重建中 GPT-6 Astra 与 Claude Opus 5 分别恢复 49.2% 与 28.8% 的工作流 | §1 摘要段；§3.3（12 个有状态 Web 应用，max reasoning effort） | 作者主张 |
| C3 | 部分重建成功率随恢复深度从 1 增至 8 而下降，Astra 由 100% 降至 64.0%，Opus 5 由 96% 降至 32% | §1 摘要段；§3.2 | 作者主张 |
| C4 | 深度导致的性能下降不能仅由上下文变长解释：同上下文长度档内 depth 1→8 二值分仍下降 31.5–58.4 点，同深度内 prompt 大小与得分相关性仅 −0.20 至 −0.05 | 附录 H.3 表 12 | 作者主张 |
| C5 | 掩蔽范围影响显著：Astra 在 logic-only 上二值分 92.9、logic-and-UI 上 76.9（差 16.0 点），链式分 96.2 vs 84.9（差 11.3 点）；所有模型在 logic-and-UI 上均下降，差距 15.4–33.1 点 | 附录 H.1 表 9（140 logic-only / 160 logic-and-UI） | 作者主张 |

最强的是 C4。它不是单点分数，而是一个针对替代解释的排除性检验：作者按每步平均 prompt 大小分 40–80k、80–120k、120–200k 三档，在各档内仍观察到 depth 1→8 的二值分下降（58.4、54.5、31.5 点），且同深度内 prompt 大小与得分的 Pearson 相关仅 −0.20 至 −0.05，任务内中心化后合并相关为 +0.11。这直接反驳了「深度效应只是长上下文所致」这一最自然的质疑，也是该结论最可能迁移到其他长程 agent 场景的部分。需注意作者自己限定：该结果「与组合多个依赖修复的难度增加一致」，但未给出因果证明（§H.3），因此是排除性证据而非机制性解释。

最弱的是 C2。全应用重建只在 12 个有状态 Web 应用上评估，且只用了 GPT-6 Astra、Claude Opus 5、GPT-5.6 Sol 三个模型（§3.3），样本面窄、无基线对照，49.2% / 28.8% 这两个数字的可外推性有限。C1 的规模数字（1,975 / 4,063）本身可核验，但「无需人工干预」的覆盖完整性存疑：图 5(a) 显示仍有目标行为未被收集或重放验证失败，且各应用任务数极不均衡（ExpenseFlow 仅 2 个任务，Reactive Resume 372 个），说明产出规模受各应用状态与交互动态限制，而非均匀覆盖。C3 与 C5 均为作者自建基准上的自报结果，尚无第三方复现，状态应保守视为作者主张。

## 机制与方法

ProgramDistill 把「可运行的交互式网页应用」转化为可验证的软件工程任务，方法由两条正交轴构成：**application-to-task factorization**（应用→任务分解）与 **reference-to-current distillation**（参考→当前蒸馏）。前者由 mine–craft–patch 流水线实现，后者由 patching 阶段的智能体行为实现。流水线本身与模型无关，论文实验中所有阶段统一使用 GPT-5.6 Sol 作为 construction model。

**符号与对象。** 挖掘阶段产出一个已验证轨迹库 $\mathcal{B}$，其中每条元素 $\tau$ 是一条可重放的浏览器交互轨迹，包含浏览器动作、期望结果信号，以及可选的父轨迹（parent trace）。父链接保留复现依赖行为所需的前置上下文，使后续阶段能沿同一 lineage 掩蔽与评测。掩蔽任务记为 $m_2$、$m_3$（原子掩蔽），沿依赖链组合后得到累积掩蔽任务 $m_2 \oplus m_3$；恢复深度 $r_L$ 表示累积任务中需同时恢复的依赖行为数量。

**Mining。** 由四个子智能体分工：Planner 基于应用证据提出行为目标与可选父轨迹；Collector 在真实浏览器中执行目标并记录动作，从环境给出的候选成功信号中挑选最能证明行为达成的信号；候选轨迹经干净重采集与重放验证后，由 Relabeler 仅依据实际达成的行为（隐藏原始目标以避免标签偏向 Planner 意图）命名与描述；Reflector 在每轮结束后汇总覆盖与失败情况以指导下一轮。通过验证的轨迹进入 $\mathcal{B}^{(r+1)}$。

**Crafting。** 由轨迹生成掩蔽源码的 diff，Mask-Depth Critic 判断是否删除了实质逻辑。原子验证的判据是：所有前置轨迹仍通过，而目标轨迹失败——即失败被限制在预期目标而非其前置条件上。通过验证的原子掩蔽再沿 lineage 组合为累积任务，未掩蔽的轨迹充当 replay bridge。任务沿两个维度受控：mask scope（logic-only 保留 UI 只移除使其工作的实现；logic-and-UI 同时移除行为与 UI）与 task composition（单行为 vs 沿前置链的多个依赖行为）。

**Patching 与验证。** 智能体获得掩蔽后的当前应用与问题陈述，可观察参考应用但不可访问其源码，通过编辑当前实现恢复行为。评测分两种设定：partial-application reconstruction 从 crafting 产出的掩蔽仓库出发；full-application reconstruction 从最小可执行脚手架出发。验证方式是重放挖掘阶段记录的轨迹，比较应用行为是否与参考一致，得到二元分数（所有目标均通过才计分）与链式分数（按首次失败前已恢复的行为比例给部分分）。

**设计取舍与适用前提。** 重放稳定性优先于覆盖面：元素定位使用浏览器可观察属性（accessibility role/name、label、placeholder、可见文本、链接、test ID）而非前端生成的 DOM id；若可观察属性无法唯一标识元素，则不生成 selector 且针对该元素的动作被拒绝。观测在「稳定」后记录：默认无在途请求且 DOM 400 ms 未变化即视为 settled，上限 10 s，超时轨迹视为不可复现并排除出验证轨迹库。验证依赖记录动作与期望信号断言，而非 LLM 视觉判断；截图仅用于分析，不作为修复与全应用重建智能体的输入。方法前提是应用自包含、可确定性重放（每次采集与重放前重置到同一 seeded 状态，并用 libfaketime 对服务端、解释器、数据库与前端 Date 施加同一常量时间偏移），且行为可通过浏览器动作与可观察信号刻画。

## 实验设置

评测在 ProgramDistill-300 上进行（300 个任务，含 140 个 logic-only 与 160 个 logic-and-UI），九个前沿模型统一以 reasoning effort high 运行；每个模型收到掩蔽应用与问题陈述，需通过观察参考、编辑当前实现并在实时应用上验证来恢复缺失行为。depth-1 为原子修复，depth 2–8 沿前置链组合多个修复目标。全应用重建在 12 个有状态 Web 应用上评估，使用 GPT-6 Astra、Claude Opus 5、GPT-5.6 Sol，max reasoning effort，从最小可执行脚手架出发。运行成本方面，GPT-6 Astra 以 high reasoning effort 完成全部 300 个任务约需 557 分钟墙钟时间（9 小时 17 分钟），使用四台 CPU 服务器；单次试验平均 48.2 分钟，中位数 43.1 分钟。价格取自 LiteLLM model_cost 表（如 GPT-6 Astra 输入 10.00 / 输出 50.00 美元每 1M tokens）。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| ProgramDistill-300 | GPT-6 Astra | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300 | Claude Opus 5 | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300 | GPT-5.6 Sol | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300 | Grok 4.6 | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300 | Claude Sonnet 5 | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300 | GPT-5.3 Codex | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300 | Gemini 3.7 Flash | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300 | Gemini 3.6 Flash | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300 | Gemini 3.1 Pro Preview | 未说明 | reasoning effort high | binary score / chain score |
| ProgramDistill-300（logic-only，140 任务） | GPT-6 Astra 等九模型 | 未说明 | 未说明 | binary score |
| ProgramDistill-300（logic-and-UI，160 任务） | GPT-6 Astra 等九模型 | 未说明 | 未说明 | binary score |
| full-application reconstruction（12 个有状态 Web 应用） | GPT-6 Astra / Claude Opus 5 / GPT-5.6 Sol | 未说明 | max reasoning effort | workflow recovery |
| partial-application reconstruction | GPT-6 Astra / Claude Opus 5 | 未说明 | 未说明 | success rate at restoration depth 1 vs 8 |

需注意：证据表中所有实验块均未给出显式基线（baseline 字段为空），因此上表统一填「未说明」；mask scope 与 restoration depth 的对比属于同一模型内部的消融条件，而非与外部基线的比较。

## 证据与结果

本节汇总摘录中可核对的全部数字。所有数值均照抄原文，未做换算或推断。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| 挖掘到的可重放行为 | 1,975 | 26 个应用，构造模型 GPT-5.6 Sol | §1 / Figure 5(a) |
| 构造任务数 | 4,063 | 26 个应用，无人工干预 | §1 / Figure 5(b) |
| 语料应用数 | 26 | 18 个 OSWorld 派生 + 8 个开源/SaaS 克隆 | Appendix A |
| 原子任务总数 | 2862 | Table 3 合计行 | Table 3 |
| 累积任务总数 | 1201 | Table 3 合计行 | Table 3 |
| 任务总数 | 4063 | Table 3 合计行 | Table 3 |
| ProgramDistill-300 任务数 | 300 | 评测套件 | §3.2 / Figure 19 |
| logic-only 任务数 | 140 | ProgramDistill-300 | Table 9 |
| logic-and-UI 任务数 | 160 | ProgramDistill-300 | Table 9 |

主结果（ProgramDistill-300，reasoning effort high，二值分 / 链式分）：

| 模型 | 总体二值 | logic-only 二值 | logic-and-UI 二值 | Δ二值 | 总体链式 | logic-only 链式 | logic-and-UI 链式 | Δ链式 |
|---|---|---|---|---|---|---|---|---|
| GPT-6 Astra | 84.3 | 92.9 | 76.9 | 16.0 | 90.2 | 96.2 | 84.9 | 11.3 |
| Claude Opus 5 | 68.7 | 80.0 | 58.8 | 21.2 | 75.2 | 85.7 | 66.0 | 19.7 |
| GPT-5.6 Sol | 60.7 | 76.4 | 46.9 | 29.6 | 68.2 | 81.5 | 56.5 | 25.0 |
| Grok 4.6 | 48.3 | 64.3 | 34.4 | 29.9 | 57.1 | 72.7 | 43.5 | 29.2 |
| Claude Sonnet 5 | 47.3 | 65.0 | 31.9 | 33.1 | 57.5 | 73.9 | 43.1 | 30.8 |
| GPT-5.3 Codex | 45.7 | 59.6 | 33.4 | 26.2 | 53.7 | 67.4 | 41.7 | 25.7 |
| Gemini 3.7 Flash | 45.3 | 61.4 | 31.2 | 30.2 | 53.2 | 69.5 | 38.9 | 30.6 |
| Gemini 3.6 Flash | 29.7 | 37.9 | 22.5 | 15.4 | 39.6 | 49.6 | 30.9 | 18.7 |
| Gemini 3.1 Pro Preview | 22.3 | 31.1 | 14.7 | 16.4 | 30.5 | 41.6 | 20.8 | 20.8 |

重建与深度效应：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| 全应用重建 workflow recovery | 49.2% / 28.8% | GPT-6 Astra / Claude Opus 5，12 个有状态应用，max reasoning effort | §1 / §3.3 |
| 部分重建成功率 depth 1→8 | 100% → 64.0% | GPT-6 Astra | §1 / §3.2 |
| 部分重建成功率 depth 1→8 | 96% → 32% | Claude Opus 5 | §1 / §3.2 |
| 每步 prompt 中位数 depth 1 / depth 8 | 47.5k / 107.5k tokens（×2.3） | 九个模型 | §H.3 |
| 平均二值分 depth 1 / depth 8 | 83.4% / 23.1% | 九个模型 | §H.3 |
| depth 1→8 二值分降幅（40–80k / 80–120k / 120–200k） | 58.4 / 54.5 / 31.5 点 | 同上下文长度档内 | Table 12 |
| prompt 大小与二值分 Pearson 相关（深度内） | −0.20 至 −0.05 | 九个模型 | §H.3 |
| 任务内中心化后合并相关 | +0.11 | 九个模型 | §H.3 |

成本与运行时：GPT-6 Astra 完成 300 任务约 557 分钟墙钟（9 小时 17 分钟），四台 CPU 服务器，最多 32 并发；单次试验均值 48.2 分钟、中位数 43.1 分钟（§G.2）。价格表（Table 8，$/1M tokens，输入/输出）：GPT-6 Astra 10.00/50.00，Claude Opus 5 5.00/25.00，GPT-5.6 Sol 4.00/20.00，GPT-5.3 Codex 1.75/14.00，Gemini 3.1 Pro Preview 2.00/12.00，Claude Sonnet 5 2.00/10.00，Grok 4.6 2.00/6.00，Gemini 3.6/3.7 Flash 均 0.75/3.75。

消融与对照有三条主线。其一，mask scope 消融：所有模型在 logic-and-UI 上均下降，二值分差距 15.4–33.1 点，链式分差距 11.3–30.8 点，说明 UI 重建是独立于逻辑恢复的额外负担。其二，任务组合消融（atomic vs cumulative）：深度 1→8 成功率单调下降，且链式分下降比二值分更平缓（Figure 19），表明部分恢复仍能得分但深度效应未消失。其三，上下文长度替代解释检验：同上下文长度档内深度效应仍为 31.5–58.4 点，深度内相关性仅 −0.20 至 −0.05，中心化后 +0.11，作者据此主张深度效应不能仅由更长上下文解释（C4）。需注意：摘录未给出任何基线方法的对照数字，也未给出统计显著性检验（如置信区间、p 值、多次运行方差），因此上述差距均为单次报告的点估计。

## 证据强度评估

证据分级：B（中等偏强，但存在结构性缺口）。

理由：正面看，评测对象是九个前沿模型在统一套件（ProgramDistill-300，300 任务）上的同预算对比（reasoning effort high），指标定义明确（二值分要求全部目标通过，链式分给首次失败前的部分分），验证方式是确定性轨迹重放而非 LLM 视觉判断（Appendix B.3），且元素定位使用可观察属性而非前端生成 DOM id（Appendix B.2），时间通过 libfaketime 对齐（Appendix A.1）。这些设计显著降低了评测噪声，使模型间排序具备可解释性。此外，作者主动做了针对「长上下文解释」的替代假设检验（§H.3 / Table 12），这是较强的自我反驳式证据。扣分项在于：全部数字来自单一论文、单一构造模型（GPT-5.6 Sol）、无独立复现，且缺少基线方法与统计检验，因此不能升到 A。

主要威胁：

1. 构造效度。任务由「掩蔽源码」生成，其难度由掩蔽范围与依赖链长度定义，而非由真实开发者意图定义。作者也承认挖掘阶段存在未收集或重放失败的目标行为（Figure 5(a)），且无法在时限内达到 settled observation 的 trace 被直接排除（Appendix B.3），元素无法唯一标识时动作被拒绝（Appendix B.2）。这意味着任务集偏向「可被结构化观测与重放」的行为，可能系统性低估真实网页开发中视觉、动画、时序类需求。

2. 外部效度。语料仅 26 个自包含 Web 应用（18 OSWorld 派生 + 8 开源/SaaS 克隆），且任务数在应用间极不均衡（ExpenseFlow 2 个，Reactive Resume 372 个），说明「可发现行为数」受应用状态与交互动态强烈影响。全应用重建更只在 12 个应用、3 个模型上评估（§3.3）。结论能否迁移到非 Web 领域、大型多服务系统或私有代码库，摘录未给出证据。

3. 统计显著性与基线选择。摘录未给出任何置信区间、方差、多次采样或显著性检验；模型间差距（如 47.3 vs 45.7 vs 45.3）是否稳定不可判断。同时缺少非 agent 基线（如直接复制参考实现、无参考消融、随机补丁）作为下界，也缺少「有参考源码」的上界对照，因此无法量化「参考不可读源码」这一约束本身贡献了多少难度。

4. 评测污染与成本约束。任务由 LLM 流水线自动生成，构造模型为 GPT-5.6 Sol，而被评测模型包含同族模型（GPT-5.6 Sol、GPT-5.3 Codex、GPT-6 Astra），存在生成器与被测者同源的风险；摘录未说明是否做了去污染检查。此外单次 300 任务评测需约 557 分钟与四台 CPU 服务器（§G.2），高成本会抑制第三方复现与多 seed 验证，进一步削弱结论的稳健性。

综上，该结论适合作为「参考引导式软件工程」这一新评测形式的可行性证据与难度轴存在的证据，但不宜直接引用为模型能力的精确排序或绝对水平。

## 边界与反例

**会推翻结论的观察。** 若在控制 prompt 大小后深度效应消失，则 C4 被推翻。作者已做部分控制：按每步平均 prompt 大小分 40–80k、80–120k、120–200k 三档，档内 depth 1→8 二值分仍分别下降 58.4、54.5、31.5 点；同深度内 prompt 大小与二值分相关性仅 $-0.20$ 至 $-0.05$，任务内中心化后合并相关性为 $+0.11$。因此「纯长上下文解释」已被数据削弱，但作者明确未给出因果证明，仅称与「组合多个依赖修复的难度增加一致」。要真正推翻，需要的是干预实验：固定任务、固定上下文长度、只改变依赖修复数量，若成功率不随依赖数下降，则深度轴不是独立难度维度。

**最可能失效的条件。**
- 语料仅 26 个自包含 Web 应用（18 个 OSWorld 派生 + 8 个开源/SaaS 克隆），且任务数在应用间极不均衡（ExpenseFlow 仅 2 个任务，Reactive Resume 372 个）。迁移到非 Web、非状态化、或依赖外部服务的系统时，prerequisite lineage 可能不存在或不可重放。
- 挖掘阶段存在未收集或重放验证失败的目标行为，行为覆盖不完整；无法在时限内达到 settled observation 的 trace 被排除。这意味着「深度 8」的样本是经过可重放性筛选的子集，难度分布可能被截断。
- 元素可观察属性无法唯一标识时不生成 selector、动作被拒绝，限制了可记录动作范围，可能系统性排除某些 UI 模式（如纯 canvas 渲染）。
- 全应用重建仅在 12 个应用、3 个模型上评估，样本量小，49.2% / 28.8% 不宜外推为「模型能力上限」。

**读者可能误推的方向。**
1. 把二值分与链式分之差当作「部分正确也算成功」——链式分只是给首个失败前的部分恢复计分，两者不可互换比较。
2. 把 logic-only 与 logic-and-UI 的差距（15.4–33.1 点）直接读作「UI 能力不足」；掩蔽范围同时改变了任务的信息量与验证面，差距是复合效应。
3. 把 restoration depth 当作可直接用于 RL 课程的现成难度标尺——作者仅提出这是「自然课程」的可能性，未做训练实验验证。
4. 把 557 分钟 / 300 任务（四台 CPU 服务器、最大 32 并发）当作可忽略的评测成本；单次 trial 均值 48.2 分钟、中位 43.1 分钟，复现门槛不低。

## 与知识库的关系

**新增（此前笔记未覆盖）。**
- 评测范式的转向：现有 SWE-bench 类笔记假设目标行为已被 issue/测试/指令显式指定；本文提出 reference-to-current distillation，要求 agent 从可运行参考中推断意图行为。可链接笔记：`swe-bench-issue-driven-eval`、`coding-agent-task-specification`。
- 可控难度轴：prerequisite lineage 与 restoration depth（1→8）提供了从原子修复到全应用重建的连续难度，且深度由依赖结构而非人为扰动定义。可链接笔记：`benchmark-difficulty-axes`、`synthetic-task-generation`。
- 自动任务生成流水线：mine–craft–patch 无需人工 issue、测试或行为标注，产出 1,975 个可重放行为与 4,063 个任务。可链接笔记：`data-distillation-for-training`、`auto-verifiable-task-construction`。

**印证。**
- 印证「可验证性优先于规模」：每个行为同时是任务单元与验证器（同一 trace 在完整应用上通过、掩蔽后失败、修复后重放通过）。可链接笔记：`verifier-design-for-agent-eval`。
- 印证「agent 的观察/验证/编辑投入分配是独立能力维度」：GPT-6 Astra 修复最强、观察活动最高、edit/write 步数最少。可链接笔记：`agent-effort-allocation`、`interactive-information-seeking`。

**张力。**
- 与「长上下文导致性能下降」这一常见结论存在张力：本文数据显示同上下文长度档内 depth 1→8 二值分仍下降 31.5–58.4 点，同深度内 prompt 大小与得分相关性仅 $-0.20$ 至 $-0.05$。可链接笔记：`long-context-degradation-hypothesis`。注意作者未给因果证明，此处应记为「削弱而非否定」。
- 与 ProgramBench 类 behavior-to-code 笔记的差异：后者把程序当作整体重建目标，本文改为应用→任务分解并引入依赖链。可链接笔记：`programbench-behavior-to-code`、`whole-program-reconstruction`。

**不确定处。** 上述「新增/印证/张力」的归类基于本文自述的定位与证据表，未做跨论文的独立复核；若知识库中已有针对 restoration depth 或 reference-guided 设定的笔记，需重新核对是否真为新增。

## 复现与验证计划

目标：在自有环境上最小化复现「恢复深度 → 性能下降」这一核心结论，并检验其是否由上下文长度解释。

环境。需要真实 Chromium 实例 + 浏览器 helper（动作词表见 Table 4：observe / click / type / drag / upload 等；repair 额外有 observe-both、reset-reference）。确定性依赖两点：每次采集与重放前重置应用到同一 seeded state；用 libfaketime 对应用服务器、解释器、数据库施加恒定时间偏移，浏览器侧对 `Date` 施加同一偏移（Appendix A.1）。观测需等待 settled：无在途请求且 DOM 400 ms 未变，上限 10 s（Appendix B.3）。元素定位必须用可观察属性（role/name/label/placeholder/可见文本/test id）而非前端生成的 DOM id；无法唯一标识则不生成 selector，该动作被拒绝（Appendix B.2）。

数据/任务。若无法获取 26 个应用，可自建 2–3 个有状态 Web 应用，按 mine–craft–patch 自采轨迹：原子掩蔽需满足「前置轨迹通过、目标轨迹失败」，再沿前置依赖链组合成 depth 2–8 的累积任务。评测集规模可远小于 ProgramDistill-300（300 题，其中 140 logic-only、160 logic-and-UI）。

基线。至少两个能力档位的模型，reasoning effort 设为 high 以对齐原文设置；同时报告 binary score（全通过才计分）与 chain score（首次失败前部分分）。

预算。注意成本量级：GPT-6 Astra 完成 300 题约 557 分钟墙钟（9 小时 17 分钟），需四台 CPU 服务器，单次 trial 均值 48.2 分钟、中位 43.1 分钟（§G.2）。建议先跑 depth 1 与 depth 8 两端各 30–50 题。

判据。可复现的预期形态：depth 1 平均 binary 约 83.4%，depth 8 约 23.1%（§H.3，九模型均值）；logic-only 明显高于 logic-and-UI（GPT-6 Astra 92.9 vs 76.9）。关键对照：按每步 prompt 大小分档后，档内 depth 1→8 仍应下降（原文 40–80k 降 58.4 点、80–120k 降 54.5 点、120–200k 降 31.5 点）；同深度内 prompt 大小与得分相关性应很弱（$-0.20$ 至 $-0.05$，任务内中心化后 $+0.11$）。

预期失败模式。若你的应用状态依赖弱、轨迹不可重放，depth 效应会消失或反转；若 selector 不稳定，重放失败会被误记为模型失败；若任务间难度未控，深度效应可能与任务构成混淆。作者明确指出深度下降与「组合多个依赖修复的难度增加」一致，但未给出因果证明（§H.3）——复现时应把因果归因标为未决。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| application-to-task factorization | 应用到任务分解：把可运行应用拆解为带前置依赖的可验证 SWE 任务 |
| reference-to-current distillation | 参考到当前蒸馏：智能体从可运行参考推断行为并在当前实现中复现 |
| mine–craft–patch pipeline | 挖掘—构造—修补流水线：自动生成并验证任务的完整流程 |
| replayable trace | 可重放轨迹：记录浏览器动作与期望信号、可确定性重放的交互序列 |
| prerequisite lineage | 前置依赖链：行为之间按状态依赖形成的先后关系 |
| restoration depth | 恢复深度：累积任务中需要同时恢复的依赖行为数量 |
| mask scope | 掩蔽范围：仅移除逻辑（logic-only）或同时移除逻辑与 UI（logic-and-UI） |
| binary score | 二元分数：累积任务中所有目标均通过才计分 |
| chain score | 链式分数：按首次失败前已恢复的行为比例给部分分 |
| settled observation | 稳定观测：等待网络与 DOM 变化停止后记录的浏览器状态 |
| replay-stable element addressing | 重放稳定元素定位：用可观察属性而非前端生成的 DOM id 定位元素 |

符号。$\mathcal{B}$ 为已验证轨迹库（trace bank），第 $r$ 轮后记为 $\mathcal{B}^{(r)}$；$\tau$ 为一条可重放浏览器交互轨迹，可带可选父轨迹（parent trace）以保留前置上下文。$m_2$、$m_3$ 为原子掩蔽任务，$m_2 \oplus m_3$ 表示沿依赖链组合的累积掩蔽任务。$r_L$ 为恢复深度（restoration depth），depth 1 为原子修复，depth 2–8 为累积修复。

流程记号。Mining 由 Planner / Collector / Relabeler / Reflector 四类子智能体轮次推进；Crafting 由 Task Generator 生成掩蔽 diff、Mask-Depth Critic 判断是否删除实质逻辑；Patching 中智能体可观察参考应用但不可访问其源码，仅能编辑当前实现。评测通过重放挖掘阶段记录的轨迹，比较当前实现与参考行为是否一致。

规模记号。语料 26 个应用（18 个 OSWorld 派生 + 8 个开源/SaaS 克隆），共 1,975 个可重放行为、4,063 个任务（原子 2862 + 累积 1201）；评测套件 ProgramDistill-300 含 300 题（140 logic-only、160 logic-and-UI）。注意各应用任务数差异极大（ExpenseFlow 2 个，Reactive Resume 372 个），反映可可靠发现并重放验证的行为数量受应用状态与交互动态限制。

## 自测

以下 5 题用于检验你是否真正读懂了本档案的证据链，而非记住数字。建议先自行作答，再展开答案对照。

**Q1（基础）** ProgramDistill-300 中 logic-only 与 logic-and-UI 任务各有多少？GPT-6 Astra 在两类任务上的二值分差距是多少？该差距在九个模型上的取值范围如何？

<details><summary>答案</summary>
套件含 140 个 logic-only 与 160 个 logic-and-UI 任务。GPT-6 Astra 二值分为 92.9 vs 76.9，差 16.0 点；链式分 96.2 vs 84.9，差 11.3 点。九个模型的二值分差距为 15.4–33.1 点（如 Claude Opus 5 为 21.2、GPT-5.6 Sol 为 29.6、Grok 4.6 为 29.9、Claude Sonnet 5 为 33.1、GPT-5.3 Codex 为 26.2、Gemini 3.7 Flash 为 30.2、Gemini 3.6 Flash 为 15.4、Gemini 3.1 Pro Preview 为 16.4）。注意：这些均为作者主张，档案中未见独立复现。
</details>

**Q2（基础）** 二值分与链式分的定义差别是什么？为什么同一模型在链式分上普遍高于二值分，且随深度下降更平缓？

<details><summary>答案</summary>
二值分要求累积任务中所有目标均通过才计分；链式分按首次失败前已恢复的行为比例给部分分。因此链式分对「部分恢复」给予信用，数值更高、随深度下降更平缓（§H.2 / Figure 19）。但作者明确指出整体深度效应在链式分下依然存在，说明下降并非纯粹由「全或无」评分口径造成。
</details>

**Q3（跨小节推理）** 有人主张「深度效应只是上下文变长的副产品」。请用 §H.3 / Table 12 的证据评估这一主张，并说明该证据为何仍不足以给出因果结论。

<details><summary>答案</summary>
反驳证据有两层：(1) 按每步平均 prompt 大小分 40–80k、80–120k、120–200k 三档，各档内 depth 1→8 二值分仍分别下降 58.4、54.5、31.5 点——即在上下文长度相近的条件下深度效应依然存在；(2) 同一深度内 prompt 大小与二值分仅呈弱负相关（Pearson $-0.20$ 至 $-0.05$），任务内中心化后合并相关性为 $+0.11$（弱正）。同时中位 prompt 从 depth 1 的 47.5k tokens 增至 depth 8 的 107.5k（因子 2.3），均值二值分从 83.4% 降至 23.1%。因此「仅由更长上下文解释」不成立。但作者自己指出，深度相关下降与「组合多个依赖修复的难度增加」一致，并未给出因果证明——分档分析排除了单一替代解释，不等于确立了机制。
</details>

**Q4（跨小节推理）** 若你想把 ProgramDistill 用作训练课程（trajectory distillation 或 RL），restoration depth 提供了什么？结合语料统计与运行成本，说明这一课程在工程上的两个主要约束。

<details><summary>答案</summary>
restoration depth 沿 prerequisite lineage 提供从原子修复（depth 1）到全应用重建的可控难度轴，作者明确将其定位为「未来训练（轨迹蒸馏或强化学习）的自然课程」。工程约束：(1) 语料不均衡——26 个应用中任务数差异极大（ExpenseFlow 仅 2 个任务，Reactive Resume 372 个），且挖掘阶段存在未收集或重放验证失败的目标行为，行为覆盖不完整，课程在各应用上的可用深度分布不均；(2) 评测成本高——GPT-6 Astra 以 high reasoning effort 完成 300 个任务约需 557 分钟（9 小时 17 分钟）墙钟时间，需四台 CPU 服务器、最多 32 并发，单次试验平均 48.2 分钟、中位 43.1 分钟。此外全应用重建仅在 12 个有状态应用、3 个模型上评估，外推需谨慎。
</details>

**Q5（跨小节推理）** 论文的「可验证性」依赖哪些机制？请指出至少两处会系统性缩小可评测行为集合的设计选择，并说明它们对结论外推的影响。

<details><summary>答案</summary>
可验证性机制：挖掘阶段记录带 replay-stable selector 的动作序列与 observation-grounded 期望信号，经干净重采集与重放验证后存入轨迹库 $\mathcal{B}$；重放验证使用记录动作与期望信号断言，而非 LLM 视觉判断（截图仅用于分析，不作为修复与全应用重建 agent 的输入）；确定性执行通过每次重置到同一 seeded 状态、并用 libfaketime 对服务端、解释器、数据库与前端 Date 施加恒定时间偏移来保证。缩小可评测集合的设计：(1) 若元素的可观察属性无法唯一标识，则不生成 selector，针对该元素的动作被拒绝（Appendix B.2）；(2) 无法在配置时限内达到 settled observation 的 trace 被视为不可复现并排除出验证 trace bank（默认 DOM 400 ms 未变即视为 settled，过程上限 10 s，Appendix B.3）。影响：这些过滤使「可评测行为」偏向可稳定定位、可快速稳定的交互，对依赖连续更新、动画或非唯一可观察属性的行为存在系统性遗漏；因此 1,975 个行为与 4,063 个任务应理解为「可可靠发现并重放验证的行为」的下界，而非应用行为的全集，跨应用/跨框架外推时需重新评估覆盖率。
</details>
