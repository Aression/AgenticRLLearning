---
id: evoskill-gui-training-free
title: EvoSkill-GUI：免训练的技能自演化
summary: 长时程 GUI 任务在非平稳界面（弹窗、延迟加载、控件移位）下，执行前固定的计划常失效。现有技能框架把技能当作部署前生成的静态单文件产物，存在四类障碍：技能非结构化难编辑、界面非平稳导致幂等失败循环、外部反思模型引入额外成本且耦合弱、程序性知识无法跨任务累积。
stage: FRONTIER
track: Agent 系统
kind: paper
depth: deep
evidenceGrade: C
order: 34
minutes: 59
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.17653
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.17653
objectives: [理解技能包 S=(D，A，P，B，C，F) 的结构化表示与各文件职责, 掌握 reflect-revise-reuse 循环中即时修订、隔离批评与受限编辑三阶段, 了解 OSWorld/AndroidWorld/MobileWorld 上的增益与 token 成本证据, 认识无形式化验证器带来的技能回归风险与部署局限]
tags: [gui-agent, skill-evolution, training-free, agent-skills, reflection, benchmark]
sources: [reflect-revise-reuse-training-free-skill]
related: [agent-loop, harness-design-coding-agents, recreationworld-hybrid-cua]
prerequisites: []
---
## 问题与语境

长时程 GUI 任务与单步执行任务的关键差别在于环境是非平稳的：弹窗、延迟加载、控件移位会随时使执行前固定的计划失效。论文把这一现象与「幂等失败循环」联系起来，指出智能体重复无效动作导致的超时是真实 GUI 部署中超时的重要来源。因此问题不在于单次规划能力，而在于**执行反馈能否被写回可复用的程序性知识**。

已有 agent-skill 框架（Anthropic 2025；CUA-Skill；WebXSkill；MMSkills；XSkill）把技能当作部署前生成的静态产物，论文认为它们未能同时处理四类障碍：(1) 技能常以单文件长文档存储，计划步骤、定位提示与恢复规则纠缠在一起，难以做定向修订；(2) 界面非平稳，一个在某个界面状态下有效的技能在弹窗出现或无障碍树过期后会失败；(3) 依赖外部反思模型引入额外延迟，且反思与技能执行、修订之间耦合松散，系统并非完全自演化；(4) 关于不可靠选择器、缺失分支与必要回退的经验被锁在单条轨迹里，无法成为邻近任务的可复用资产。

与本文最接近的两条线是自演化智能体（UI-Evol、UI-Mem、Mobile-Agent-E、SEAgent、EvoCUA、UI-Voyager、MobileUse、GUI-Reflection）与结构化记忆系统（HyMem 等）。论文的定位差异是：前者更新的是记忆、策略或模型权重，后者聚焦记忆构建而非技能级修订；并发的 CoEvoSkills 虽协同演化多文件技能包，但面向代码中心环境且侧重技能构建。EvoSkill-GUI 的定位是**在推理时直接修订已部署的技能工件本身**，不更新权重、不训练、不依赖外部反思模型，从而把技能从静态产物变成可修订的程序性知识。这一区分是理解其贡献边界的前提：它主张的是技能级自演化的可行性，而非更强的基座能力。

## 核心主张

论文的核心主张可归纳为四条，覆盖有效性、表示设计、复用性与成本四个维度。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | 免训练框架在 MobileWorld、AndroidWorld、OSWorld 上一致提升成功率，最大增益分别为 +16.2%、+6.0%、+10.5% | §1 贡献列表与摘要；§4.2 表 1、表 2 | 作者主张 |
| C2 | 结构化多文件技能包优于单文件技能，MobileWorld 成功率 69.52% 对 66.67%，提升 +2.85 | §4.3 表 3 | 作者主张 |
| C3 | 演化后的技能库可被后续相关任务复用，AndroidWorld 复用率 P1 为 37.9%、P2 为 100.0%，成功率分别提升 +2.6 与 +6.0 | §4.2 表 2 | 作者主张 |
| C4 | EvoSkill-GUI 三轮演化总 token 消耗 94.75M，处于 pass@3 基线 103.00M 预算范围内，此前 168M 为记账错误 | 附录 A.5 表 13 | 存疑 |

**最强的一条是 C1 中的 OSWorld 结果**，因为它是唯一给出逐域分解、且同时覆盖通用模型与 GUI 专用模型的主表证据：GUI-Owl-1.5-8B 从 46.7 提升到 54.8（Δ +8.1），Qwen3-VL-8B-Instruct 从 23.8 提升到 34.3（Δ +10.5），且表 1 中同表列出了 Claude-Sonnet-4.5（58.1）、EvoCUA-32B（56.7）、GUI-Owl-1.5-32B（55.4）等参照点，读者可自行判断提升后的绝对水平处于什么位置。需要同时注意该表包含负向域级条目：GUI-Owl-1.5-8B 在 Thunderbird 上为 -4.1，Qwen3-VL-8B-Instruct 在 VS Code 上为 -13.3，论文在附录 A.4 中承认这是「rare regressions」并给出两个可能因素，但未给出机制性解释。

**最弱的一条是 C4**。它依赖附录 A.5 表 13，而该表本身是对先前数字的更正（原文称 168M 源于把中间累积快照计入最终累积记录造成重复计数）。这意味着该数字经历过一次口径修正，且论文未提供独立复算路径；同时「处于 pass@3 基线预算范围内」的对比是跨方法、跨评测协议（三次独立 rollout 对三轮演化）的，可比性由作者自行设定。C2 与 C3 的强度居中：C2 的 +2.85 是单基准单次消融，C3 的复用率在论文 Limitations 中被明确限定为「parameterized variants of the same task family」，作者自己提示向真正未见应用类别的迁移可能比该数字所暗示的更差。所有四条均标注为作者主张，证据表中没有出现已复现或与共识一致的条目。

## 机制与方法

EvoSkill-GUI 的核心主张是：把「技能」从部署前生成的静态单文件产物，改造成推理时可被执行反馈直接改写的结构化多文件包，从而在不更新模型权重、不引入外部反思模型的前提下实现技能级自演化。

问题被建模为部分可观测 MDP $\mathcal{M}=\langle\mathcal{X},\mathcal{A},T,\mathcal{O},\Omega,R\rangle$，其中 $\mathcal{X}$ 为底层屏幕状态，$\mathcal{A}$ 为 GUI 动作与工具调用，$T$ 为转移函数，$R(x_{T})\in\{0,1\}$ 为终止任务完成奖励。每步观测 $o_{t}=(\varphi_{t},\zeta_{t})$，即截图 $\varphi_{t}$ 与无障碍树 $\zeta_{t}$；部分可观测历史为 $h_{t}=(o_{1},a_{1},\ldots,a_{t-1},o_{t})$。技能包 $S$ 作为条件化策略的持久程序性知识对象：

$$a_{t}\sim\pi_{\theta}(a_{t}\mid h_{t},S)$$

给定指令 $I$，技能包的期望回报为 $J(S,I)=\mathbb{E}_{\tau\sim P(\tau\mid\pi_{\theta},S,\mathcal{M},I)}[R(x_{T})]$，其中 $\tau$ 为执行轨迹。目标是求在任务分布 $\mathcal{D}$ 上最大化期望回报的可复用技能包：

$$S^{*}=\arg\max_{S}\;\mathbb{E}_{I\sim\mathcal{D}}[J(S,I)]$$

表示层面，技能包定义为 $S=(D,A,P,B,C,F)$：$D$ 为检索元数据，$A$ 为无障碍树相关工具，$P$ 为可执行计划知识，$B$ 为备用定位与识别策略，$C$ 为失败恢复规则，$F=\{f^{(1)},\ldots,f^{(n)}\}$ 为失败案例集合。这一分解对应 GUI 智能体的三类常见错误来源：$P$ 规定做什么步骤，$B$ 规定如何识别与定位界面元素，$C$ 规定期望状态被违反时如何恢复。相较单块技能文件，该结构使修订更具针对性——定位失败改 $B$，缺失分支改 $C$，高层流程错误改 $P$。

循环由三阶段交替构成：(1) rollout 期间，当执行反馈与当前计划矛盾时触发即时 in-rollout 修订；(2) rollout 失败后，同一骨干模型在严格信息隔离下充当独立批评者诊断轨迹；(3) 同一骨干模型再以执行者身份，通过受限工具接口只编辑包内特定文件，修订顺序为 $P\rightarrow B\rightarrow C$，失败示例最多保留 3 条。验证通过的技能包按结构化元数据 $D=(\mathrm{id},\mathrm{intent},\mathrm{app},\mathrm{platform},\mathrm{kw},\mathrm{args},\mathrm{hist},\mathrm{status})$ 建库，用 BM25 加关键词阈值、分歧阈值、领域与关键词加权的打分检索复用；未命中则生成新技能。按元数据而非完整程序体索引，是为了避免长程序文件中表面 token 重叠导致的跨任务误匹配。

设计取舍上，作者选择「单骨干自演化」而非外部反思模型，理由是外部反思引入额外延迟且与技能执行、修订耦合弱；选择工具受限编辑与信息隔离，是为了让修订局部化、可审计，并降低批评者窥见执行者内部信息带来的偏差。适用前提需明确：该框架依赖骨干模型对截图、无障碍树与执行轨迹的解读能力，以及通过工具调用产出结构化修订的能力；当骨干感知或轨迹诊断不可靠时，技能编辑可能未命中真实失败原因，原则上可向已验证的技能包引入回归。作者亦声明当前不含形式化验证器来否决有害编辑，且技能演化循环每次失败 rollout 会额外产生一次批评调用加一次修订调用。

## 实验设置

评估覆盖 MobileWorld、AndroidWorld、OSWorld 三个 GUI 基准，横跨移动与桌面环境，并在通用模型与 GUI 专用模型上验证。OSWorld-Verified 上的对比在最大 50 步预算下进行，指标为成功率（%）；AndroidWorld 报告复用率与成功率；MobileWorld 报告技能组织消融与 pass@1/pass@3 下的 token 成本与准确率。实现细节方面，执行阶段温度 0.0、最大输出 8192 token、历史截图 3 张、坐标缩放因子 1000、每步最多 4 次技能工具调用；技能生成温度 0.3、最大输出 4096；批评者温度 0.0、最大输出 4096、最多 8 张截图、截图最大边长 1280；检索 BM25 参数 $k_{1}=1.5$、$b=0.75$，关键词阈值 0.6，分歧阈值 0.65，分歧权重 0.3，领域加成 0.15，关键词加成 $\leq 0.2$；修订顺序 $P\rightarrow B\rightarrow C$，失败示例最多 3 条。API 模型使用官方端点与确定性解码，本地开源权重模型使用单张 RTX PRO 6000 96GB 上的 vLLM。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
| --- | --- | --- | --- | --- |
| OSWorld-Verified | GUI-Owl-1.5-8B | GUI-Owl-1.5-8B (no skill) | 最大 50 步 | 成功率 (%) |
| OSWorld-Verified | Qwen3-VL-8B-Instruct | Qwen3-VL-8B-Instruct (no skill) | 最大 50 步 | 成功率 (%) |
| AndroidWorld | EvoSkill-GUI | Base SR | 未说明 | 成功率 (SR) |
| MobileWorld | EvoSkill-GUI | Single-file Skill | 未说明 | 成功率 (%) |
| MobileWorld | EvoSkill-GUI (3 rounds) | Baseline pass@1 / pass@3 | pass@1 与 pass@3 | token 成本 (M) 与准确率 (%) |

OSWorld-Verified 上另列出若干参照模型作为上下文：Claude-Sonnet-4.5 58.1、Qwen3-VL-Flash 41.6、UI-TARS-72B-DPO 25.9、Computer-Use-Preview 31.2、OpenCUA-32B 35.1、EvoCUA-8B 46.1、EvoCUA-32B 56.7、GUI-Owl-1.5-32B 55.4、MMSkills 25.4（均来自 Table 1）。需注意，Table 1 中 GUI-Owl-1.5-8B 与 Qwen3-VL-8B-Instruct 的逐域结果存在个别负向条目（OS 域 $-4.1$、Thunderbird 域 $-13.3$），作者在附录 A.4 中将其归为罕见回归并给出两个可能因素，但未给出定量归因。上述实验设置与结果均为作者报告，除 token 记账更正（附录 A.5）外，本档案未记录独立复现。

## 证据与结果

以下数字均直接取自全文摘录与证据表，未做任何换算或补全。

OSWorld-Verified 主结果（Table 1，统一 maximum of 50 steps，指标为 success rate %）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Overall SR | 58.1 | Claude-Sonnet-4.5 | Table 1 |
| Overall SR | 41.6 | Qwen3-VL-Flash | Table 1 |
| Overall SR | 25.9 | UI-TARS-72B-DPO | Table 1 |
| Overall SR | 31.2 | Computer-Use-Preview | Table 1 |
| Overall SR | 35.1 | OpenCUA-32B | Table 1 |
| Overall SR | 46.1 | EvoCUA-8B | Table 1 |
| Overall SR | 56.7 | EvoCUA-32B | Table 1 |
| Overall SR | 55.4 | GUI-Owl-1.5-32B | Table 1 |
| Overall SR | 25.4 | MMSkills | Table 1 |
| Overall SR | 46.7 → 54.8（Δ +8.1） | GUI-Owl-1.5-8B，无技能 → +EvoSkill-GUI | Table 1 |
| Overall SR | 23.8 → 34.3（Δ +10.5） | Qwen3-VL-8B-Instruct，无技能 → +EvoSkill-GUI | Table 1 |

分域结果（摘录给出逐列数值）：GUI-Owl-1.5-8B 的 Δ 为 +5.7 / +7.7 / +8.0 / +8.3 / +0.0 / +9.0 / −4.1 / +20.0 / +42.7 / +5.2；Qwen3-VL-8B-Instruct 的 Δ 为 +15.3 / +19.3 / +10.7 / +2.6 / +4.4 / +7.5 / +25.0 / −13.3 / +15.3 / +21.7。摘录中两处负向域级条目被作者归因于「two plausible factors」，但未给出具体因子名称。

AndroidWorld（Table 2）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Reuse Rate / Base SR / Ours SR / Δ | 37.9 / 68.1 / 70.7 / +2.6 | P1 (seed 30) | Table 2 |
| Reuse Rate / Base SR / Ours SR / Δ | 100.0 / 55.2 / 61.2 / +6.0 | P2 (seed 42) | Table 2 |

MobileWorld 消融（Table 3）：Single-file Skill 66.67% 对 Skill Package (Ours) 69.52%，Δ +2.85。摘录仅称「Ablations confirm the importance of structured packages, instant revision, and reflection-driven edits」，instant revision 与 reflection-driven edits 的具体数值摘录未给出。

Token 成本（Table 13，MobileWorld）：Baseline pass@1 33.20M / 0.284M / 0.284M / 53.3%；Baseline pass@3 103.00M / 0.880M / 0.293M / 62.8%；Single-file skill pass@3 84.54M / 0.723M / 0.372M / 66.7%；EvoSkill-GUI (3 rounds) 94.75M / 0.810M / 0.439M / 69.5%。作者称此前 168M 系「accounting error」导致的重复计数，并已在修订表中更正。

对照关系上，Table 1 同时包含闭源通用模型、专用开源模型与技能类方法（MMSkills），EvoSkill-GUI 的增益是在同一 50 步预算下相对各自无技能基线的差值，而非与最强基线（Claude-Sonnet-4.5 的 58.1）比较。

## 证据强度评估

证据分级：B（中等偏弱）。理由：结论方向（免训练技能级自演化可提升 GUI 成功率）在三个基准、多个骨干上一致为正，且给出了逐域数值与 token 账目更正，具备可核查性；但全部证据来自单一论文自报，无第三方复现，且关键机制消融不完整。

主要威胁：

1. 构造效度（机制归因不足）。Table 3 只隔离了「结构化包 vs 单文件」一个变量（+2.85），而 instant revision 与 reflection-driven edits 的贡献「摘录未给出」具体数值。因此「reflect-revise-reuse 循环本身有效」这一核心机制主张，目前只有作者的文字断言支撑，无法排除增益主要来自检索复用或额外推理预算。

2. 统计显著性与方差。AndroidWorld 的 P1 增益仅 +2.6（68.1→70.7），且 P1 复用率 37.9% 与 P2 的 100.0% 差异极大，说明结果对任务族与种子高度敏感；摘录未给出置信区间、重复次数或显著性检验。OSWorld 上还存在 −4.1 与 −13.3 的域级回退，与「一致提升」的表述存在张力。

3. 外部效度与复用率解释。作者自述 AndroidWorld 的复用率是在「parameterized variants of the same task family」上取得，并承认迁移到真正未见应用类别时「may degrade more gracefully than this number suggests」——即 100.0% 复用率不能外推为通用复用能力。评测仅覆盖三个基准，真实部署的界面更新频率、网络延迟与隐私状态均未被反映。

4. 基线选择与评测污染。OSWorld 对照中 EvoSkill-GUI 的 54.8 仍低于 Claude-Sonnet-4.5 的 58.1 与 EvoCUA-32B 的 56.7，增益是相对弱基线（8B 无技能）的差值，容易被读作绝对性能提升。此外 Table 13 存在已承认的记账错误（168M→94.75M），虽已更正，但提示成本类数字的可靠性需打折；同时框架缺少「formal verifier that vetoes harmful skill edits」，错误修订可能静默污染已验证技能包，构成对结论稳健性的实质威胁。

## 边界与反例

**什么观察会推翻结论。** 核心主张 C1（免训练一致提升）建立在三个基准的总体成功率上，但表 1 的分领域数据已包含反例：GUI-Owl-1.5-8B 在 Thunderbird 上 $-4.1$，Qwen3-VL-8B-Instruct 在 VS Code 上 $-13.3$。作者在 A.4 承认存在「两个负向领域级条目」，并称识别出「两个可能因素」，但摘录未给出这两个因素的具体内容——此处不确定。因此，若在更多领域或更多随机种子上出现负向条目比例上升，或负向幅度与正向幅度同量级，则「一致提升」的表述应被削弱为「平均提升、方差未充分刻画」。

**最可能失效的条件。** 作者自陈的边界最值得重视：框架依赖骨干模型解读截图、无障碍树与轨迹并产出结构化修订；当骨干感知或轨迹诊断不可靠时，修订可能未命中真实失败原因，并「原则上可能向已验证的技能包引入回归」。更关键的是，作者明确承认「目前不包含否决有害技能编辑的形式化验证器」。这意味着技能库的单调改进性没有保证——已通过验证的包可能在后续轮次被改坏。此外，AndroidWorld 的复用率（P1 37.9%、P2 100.0%）是在「同一任务族的参数化变体」上取得的，作者自己提示迁移到真正未见过的应用类别时表现可能下降。

**读者可能误推的方向。** 其一，把 +16.2%/+6.0%/+10.5% 当作跨基准可比的统一增益：这三个数字分别对应 MobileWorld、AndroidWorld、OSWorld 的最大增益，且 OSWorld 上实际报告的是 +8.1（GUI-Owl-1.5-8B）与 +10.5（Qwen3-VL-8B-Instruct），不能混用。其二，把 token 成本结论当作已定论：C4 被标注为「存疑」，作者自述此前 168M 系「记账错误」（中间累积快照被重复计入），修正后为 94.75M；这是作者单方面更正，缺乏第三方复核。其三，把「免训练」等同于「零额外成本」：作者指出每次失败 rollout 需额外一次 critic 调用加一次 revision 调用，在延迟敏感部署中需靠复用摊销。其四，把 MobileWorld 上 69.52% vs 66.67%（$\Delta +2.85$）视为强证据：该差距未报告方差或显著性检验，摘录中亦无多次种子结果。

## 与知识库的关系

**新增（此前笔记未覆盖）。** 与 Agent Skills 一系（Anthropic 2025；CUA-Skill；WebXSkill；MMSkills；XSkill）相比，本文的新增点是把技能表示为结构化多文件包 $S=(D,A,P,B,C,F)$，并在推理时通过 reflect-revise-reuse 循环做技能级修订，而非离线构建或检索后保持不变。与 Self-evolving Agents 一系（UI-Evol；UI-Mem；Mobile-Agent-E；SEAgent；EvoCUA；UI-Voyager；MobileUse；GUI-Reflection）相比，新增点是不更新记忆、策略或模型权重，而是直接修订部署的技能工件本身。建议新建笔记 `skill-package-representation`（记录六元组分解与 P→B→C 修订顺序）与 `inference-time-skill-revision`（记录 in-rollout 修订 + 信息隔离批评 + 工具受限编辑三阶段）。

**印证。** 本文与 `agent-skills-static-artifact` 一脉的观察一致：现有技能框架把技能当作部署前生成的静态产物，导致程序性知识无法跨任务累积。本文的 MobileWorld 消融（单文件 66.67% vs 技能包 69.52%，$\Delta +2.85$）为「结构化优于单体」这一直觉提供了弱证据，可挂到 `structured-vs-monolithic-prompt` 下，但需标注为作者主张且无方差报告。

**张力。** 其一，与 CoEvoSkills（Zhang et al., 2026a）存在直接张力：两者都做多文件技能包共演化，但 CoEvoSkills 面向代码中心环境且带 surrogate verifier，本文面向已部署 GUI 技能修订且**明确没有形式化验证器**。这构成一条可链接的对比笔记 `verifier-vs-no-verifier`：验证器的有无直接决定技能库是否可能被改坏，是两条路线最实质的分歧。其二，与结构化记忆系统（HyMem；Zhu et al., 2026）存在边界张力：这些系统聚焦记忆构建而非技能级修订，本文主张技能级修订是不同层次的对象；但「记忆更新」与「技能修订」在工程上是否真能清晰二分，本文未给出判别实验，建议在 `memory-vs-skill-boundary` 中标注为待验证。其三，C4 的 token 记账更正（168M → 94.75M）提示：凡引用本文成本数字的笔记都应链接到 `token-accounting-correction`，并注明该更正为作者自述、未经独立复核。

## 复现与验证计划

目标：在最小成本下验证「免训练技能自演化带来成功率提升」这一核心主张，并优先检验其最脆弱环节——token 记账与复用率口径。

环境与数据。三个基准中，MobileWorld 与 AndroidWorld 为移动端，OSWorld-Verified 为桌面端。OSWorld-Verified 需注意统一评测预算：表 1 明确「all results are evaluated under a maximum of 50 steps」。本地开权重模型按附录 A.1 使用 vLLM 部署于单张 RTX PRO 6000 96GB；API 模型走官方端点并采用确定性解码（执行与批评者 temperature 均为 0.0，技能生成 0.3）。

最小实验配置。建议先做 MobileWorld 单点复现，因为该基准同时提供了准确率与 token 成本（表 13），可一次性检验 C2 与 C4。基线取 pass@3（103.00M total，0.880M per task，62.8%），对照 Single-file skill pass@3（84.54M，0.723M per task，66.7%）与 EvoSkill-GUI 三轮（94.75M，0.810M per task，0.439M per round，69.5%）。判据：EvoSkill-GUI 准确率应高于单文件技能，且总 token 不显著超出 pass@3 基线。

关键超参须照抄表 12：检索 BM25 $k_1=1.5$、$b=0.75$，关键词阈值 0.6，分歧阈值 0.65，分歧权重 0.3，领域加成 0.15，关键词加成 $\leq 0.2$；修订顺序 $P\rightarrow B\rightarrow C$，失败示例最多 3 条；批评者最多 8 张截图、单边最大 1280。

预期失败模式与不确定处。其一，C4 标注为「存疑」：论文自述此前 168M 系「accounting error」，即中间累积快照被重复计入最终累积记录。复现时必须独立记录每轮增量而非累积值，否则会重演同一错误。其二，AndroidWorld 复用率 P1 为 37.9%、P2 为 100.0%，但作者在 Limitations 中承认该复用率「achieved on parameterized variants of the same task family」，因此高复用率不能外推至全新应用类别。其三，表 1 存在域级负增益（GUI-Owl-1.5-8B 在 OS 为 $-4.1$，Qwen3-VL-8B-Instruct 在 Thunderbird 为 $-13.3$），复现应逐域报告而非只看 Overall。其四，框架无形式化验证器否决有害编辑，回归风险需通过技能包版本化与人工抽检监控。

## 术语与记号

本节汇总正文出现的关键符号与缩写。记号沿用 §3.1 的部分可观测马尔可夫决策过程建模：任务为 $\mathcal{M}=\langle\mathcal{X},\mathcal{A},T,\mathcal{O},\Omega,R\rangle$，其中 $\mathcal{X}$ 为底层屏幕状态，$\mathcal{A}$ 为 GUI 动作与工具调用，$T$ 为转移函数，$R(x_{T})\in\{0,1\}$ 为终止任务完成奖励。每步观测 $o_{t}=(\varphi_{t},\zeta_{t})$，由截图 $\varphi_{t}$ 与无障碍树 $\zeta_{t}$ 组成；部分可观测历史为 $h_{t}=(o_{1},a_{1},\ldots,a_{t-1},o_{t})$。策略以技能包为条件：$a_{t}\sim\pi_{\theta}(a_{t}\mid h_{t},S)$。

技能包定义为 $S=(D,A,P,B,C,F)$，其期望回报 $J(S,I)$ 与最优包 $S^{*}$ 见式 (2)(3)。注意符号 $A$ 在 MDP 中表示动作集合、在技能包分解中表示无障碍树工具，二者同名不同义，阅读时需按上下文区分。

| 术语 | 含义 |
| --- | --- |
| EvoSkill-GUI | 免训练的技能自演化 GUI 智能体框架，通过反思-修订-复用循环在推理时更新技能包 |
| Skill Package | 结构化多文件技能包，由检索元数据、无障碍工具、计划、备用定位、恢复规则、失败案例六部分组成 |
| $S=(D,A,P,B,C,F)$ | 技能包分解；$D$ 检索元数据，$A$ 无障碍树工具，$P$ 可执行计划，$B$ 备用定位与识别策略，$C$ 失败恢复规则，$F$ 失败案例集合 |
| $D$ | 检索元数据 $(\mathrm{id},\mathrm{intent},\mathrm{app},\mathrm{platform},\mathrm{kw},\mathrm{args},\mathrm{hist},\mathrm{status})$ |
| $h_t$ / $o_t$ | 部分可观测历史 / 观测（截图 $\varphi_t$ 与无障碍树 $\zeta_t$） |
| $J(S,I)$ / $S^{*}$ | 技能包 $S$ 在指令 $I$ 下的期望任务回报 / 在任务分布 $\mathcal{D}$ 上最大化期望回报的技能包 |
| Reflect-Revise-Reuse Loop | 反思-修订-复用循环：rollout 即时修订、隔离批评、技能文件修订、检索复用 |
| In-rollout Revision | 执行过程中当反馈与计划矛盾时立即对技能进行的修订 |
| Information Isolation | 批评者与执行者之间的严格信息隔离 |
| Tool-restricted Edit | 通过受限工具接口只允许编辑技能包内特定文件，保证修订局部可审计 |
| Single-backbone Self-evolution | 同一骨干模型既充当批评者又充当执行者完成技能自演化，无需外部反思模型 |
| Accessibility Tree | 无障碍树，GUI 界面元素的结构化表示，作为智能体观测的一部分 |
| BM25 | 用于技能元数据检索的排序函数，参数 $k_1=1.5$、$b=0.75$ |
| Reuse Rate | 后续相关任务成功检索并复用已有技能包的比例 |
| Pass@k | $k$ 次独立尝试中至少一次成功的评测指标 |
| Idempotent Failure Loop | 幂等失败循环，智能体重复无效动作导致超时，是真实 GUI 部署超时的重要来源 |

## 自测

以下问题用于检验读者是否真正掌握了本档案中「证据强度」与「可迁移性」的边界。答案基于给定证据表与全文摘录，凡涉及数字均照抄原文。

**Q1（证据强度）** 论文声称「免训练框架在 MobileWorld、AndroidWorld、OSWorld 上一致提升成功率，最大增益分别为 +16.2%、+6.0%、+10.5%」。但证据表中 AndroidWorld 的最大 Δ 只有 +6.0，MobileWorld 的 Δ 只有 +2.85。这个 +16.2% 从何而来？它是否被本档案的表格证据直接支持？

<details><summary>答案</summary>
+16.2% 只出现在摘要与 §1 贡献列表的叙述性引文中（"maximum gains of $+16.2\%$, $+6.0\%$, and $+10.5\%$"），证据表 experiments 与 results 中没有任何一行给出 +16.2 的数值。AndroidWorld 表 2 的最大 Δ 为 +6.0（P2 seed 42），MobileWorld 表 3 的 Δ 为 +2.85。因此 +16.2% 属于**作者主张**，本档案未提供可核对的表格支撑，应标注为不确定，不能当作已复现结论使用。
</details>

**Q2（跨小节推理：成本 vs 收益）** 结合 Table 13 与 Limitations，说明「EvoSkill-GUI 比 pass@3 基线更省 token」这一说法是否成立，以及它在延迟敏感场景下的真实代价是什么。

<details><summary>答案</summary>
Table 13 显示 EvoSkill-GUI 总 token 94.75M，低于 pass@3 基线的 103.00M，但**高于** Single-file skill pass@3 的 84.54M；其 Avg./Round 为 0.439M，是三者中最高（基线 0.293M、单文件 0.372M）。所以「比 pass@3 基线省」成立，但「比所有对照省」不成立。Limitations 明确指出：每次失败 rollout 额外产生一次 critic 调用加一次 revision 调用，该开销相对重训练可忽略，但在延迟关键部署中需靠复用摊销。即 token 总量省不等于单次延迟低。
</details>

**Q3（跨小节推理：复用率与泛化）** Table 2 中 P2 复用率 100.0%、Δ +6.0，P1 复用率仅 37.9%、Δ +2.6。能否据此推断「复用率越高增益越大」？Limitations 对此有何限定？

<details><summary>答案</summary>
不能直接推断。两点数据不足以建立单调关系，且 P1/P2 是不同 seed 的不同任务集，Base SR 本身差异很大（68.1 vs 55.2），增益空间不同。Limitations 明确限定：AndroidWorld 上的复用率是在**同一任务族的参数化变体**上取得的，迁移到真正未见过的应用类别时可能比该数字所暗示的更差（"may degrade more gracefully than this number suggests"）。因此该复用率不可外推到开放域。
</details>

**Q4（机制理解）** 技能包 S=(D,A,P,B,C,F) 中，为什么把 P、B、C 分开存储对「可修订性」是关键？请对应到三类 GUI 错误来源。

<details><summary>答案</summary>
§3.2 说明该分解对齐三类常见错误：P 规定做什么步骤（高层程序性错误改 P），B 规定如何识别与定位界面元素（grounding 失败改 B），C 规定期望状态被违反时如何恢复（缺失 contingency 改 C）。若技能是单一长文档，计划、定位提示与恢复规则纠缠，无法做定向修订。分开存储使修订局部化、可审计，这也是 Table 3 中 Skill Package 69.52% 优于 Single-file 66.67%（Δ +2.85）的设计依据（该结论为作者主张）。
</details>

**Q5（可信度与风险）** 论文承认「没有形式化验证器否决有害的技能编辑」。结合 Table 1 中的负向条目，说明这一风险在数据上是否已经显现，以及它对迁移到高风险场景意味着什么。

<details><summary>答案</summary>
已显现。Table 1 中 GUI-Owl-1.5-8B 在 OS 域 Δ 为 -4.1，Qwen3-VL-8B-Instruct 在 Thunderbird 域 Δ 为 -13.3；§A.4 承认这是两处域级负向回归并给出两个可能因素。Limitations 指出当骨干模型的感知或轨迹诊断不可靠时，技能编辑可能未抓住真实失败原因，原则上可向已验证的技能包引入回归；工具受限接口与信息隔离批评只降低风险，不构成否决机制。迁移含义：在高风险或隐私敏感场景复用演化后的技能包前，需要技能级版本管理、人工在环验证与显式 fail-safe 规则（Ethics Statement 亦如此建议）。
</details>
