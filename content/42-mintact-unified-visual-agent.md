---
id: mintact-unified-visual-agent
title: MintAct：统一数字环境的视觉智能体
summary: 视觉语言智能体在真实数字设备上需要同时具备界面元素定位、跨移动/桌面/网页的多步导航以及调用外部工具的能力，但这些能力目前分散在各自独立构建、训练和评测的专用模型中。为每个领域维护专用模型在服务与扩展上成本高昂，尤其不适合端侧小尺寸部署。
stage: FRONTIER
track: Agent 系统
kind: paper
depth: deep
evidenceGrade: C
order: 42
minutes: 55
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.22083
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.22083
objectives: [理解单一视觉智能体如何统一 UI 定位、移动/桌面/网页导航与工具调用, 掌握 MintAct 的多阶段训练配方：高分辨率单步 SFT、低分辨率多步 SFT、RFT 与联合智能体 RL, 了解异步 RL 框架如何通过参数同步间隔、消息队列容量与截断重要性采样稳定异构环境训练, 对比 MintAct 2B/4B/8B 在 AndroidWorld、OSWorld-Verified、Weblica 等基准上的表现]
tags: [visual-agent, gui-grounding, asynchronous-rl, unified-model, agent-training]
sources: [mintact-a-unified-visual-agent-for-digit]
related: [evoskill-gui-training-free, recreationworld-hybrid-cua, multi-turn-rl]
prerequisites: []
---
## 问题与语境

视觉语言智能体要在真实数字设备上可用，必须同时具备三类能力：把自然语言指令定位到屏幕可交互元素（UI grounding）、在移动/桌面/网页界面上完成多步导航、以及调用外部工具与 API 以触达界面操作难以完成的任务。论文指出，这三类能力目前分散在各自独立构建、训练与评测的专用模型中：grounding（Xie et al., 2026; Feizi et al., 2026）、移动导航（Zhang et al., 2025a; Wang et al., 2024a）、桌面控制（ByteDance Seed, 2025; Wang et al., 2026）、网页导航（Kar et al., 2026; Gupta et al., 2026）与视觉工具使用（Yang et al., 2025b; Zheng et al., 2026）各自为政。为每个领域维护一个专用模型在服务与扩展上成本高昂，在适合端侧部署的小尺寸上尤其不现实。

失效点不止于建模。论文强调，这些领域在观测空间、动作空间、原生交互方式、数据来源与可执行环境上都不同；朴素地合并各领域动作集或混合其数据会让领域互相干扰、侵蚀单领域质量。更棘手的是，可靠交互行为越来越依赖针对异构环境后端的在线 RL，而这些后端慢、不可靠、产生长多模态轨迹：同步 RL 会因等待最慢环境而严重浪费 GPU；朴素异步流水线虽提升吞吐，却让最快环境主导数据生成，破坏跨域采样比例的可控性，使实际训练分布向"跑得快的领域"漂移。

因此论文的定位不是再提出一个更强的单领域专家，而是把统一本身当作待解问题：统一是数据、环境与训练三方面的联合问题，而非单纯的建模问题。MintAct 以 2B/4B/8B 三个尺寸给出统一模型族，并配套异步 RL 基础设施与多阶段训练配方，试图回答"单一模型能否在不牺牲各领域性能的前提下统一这些能力"。

## 核心主张

论文的核心主张可归纳为四条，均出自 §1、§4.2 与 §5，证据定位如下表。表中"状态"一列依据本档案可核验的范围标注：所有数字均来自论文自报的 Table 3，档案中不存在第三方复现记录，故一律标为"作者主张"。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | 单一 MintAct 模型可同时覆盖定位、移动/桌面/网页导航与工具调用，且不牺牲各领域性能 | §1；§4.2 表 3；§5 | 作者主张 |
| C2 | MintAct-8B 在 OSWorld-Verified 达 48.9、Online-Mind2Web 达 39.1、AndroidWorld 达 67.0 | §1；§4.2 表 3 | 作者主张 |
| C3 | 相对 Qwen3-VL-8B 初始化，MintAct-8B 在 AndroidWorld 由 47.6 提升至 67.0，OSWorld-Verified 由 33.9 提升至 48.9，Weblica 由 55.5 提升至 74.7，MM-ToolSandBox 由 3.1 提升至 24.5 | §4.2 表 3 | 作者主张 |
| C4 | 多阶段训练配方中每个阶段都对最终能力有贡献 | §1；§4 消融 | 作者主张 |

最强的是 C3。它是同初始化、同尺寸的受控对比，四个领域方向一致且幅度大（如 MM-ToolSandBox 3.1→24.5），且论文称 2B、4B 有"similar gains"，与表 3 中 MintAct-2B/4B 相对 Qwen3-VL-2B/4B 的全面提升一致；这类"相对自身初始化"的增益比跨模型横比更不易被评测口径差异解释。

最弱的是 C1 与 C4。C1 的"不牺牲"依赖跨模型横比，而表 3 中 MintAct-8B 在 AndroidWorld 为 67.0，低于 MAI-UI-8B 的 70.7；在 ScreenSpot-V2 为 93.7，低于 WEBLICA-8B 的 94.5；Om2W 为 39.1，与 WEBLICA-8B 的 39.2 基本持平。论文自己的措辞也只是"competitive with or outperforms"与"remaining competitive on the others"，因此"不牺牲"应理解为"同尺寸下具竞争力"，而非逐项最优。C4 的消融证据在给定摘录中仅有 §1 的一句概括性陈述，缺少可核验的逐阶段数字，属于证据最薄的一条。

## 机制与方法

MintAct 以 Qwen3-VL-Instruct 为初始化，通过多阶段配方把定位（grounding）、移动/桌面/网页导航与视觉工具调用统一进单一模型。所有阶段优化同一自回归目标：

$$\max_{\theta}\ \log \pi_{\theta}(a \mid s)$$

其中 $s$ 是策略的条件上下文（系统提示、指令与历史），$a$ 是目标推理轨迹与动作，$\pi_\theta$ 为参数 $\theta$ 的策略模型。三个 SFT 阶段（高分辨率单步 SFT、低分辨率多步 SFT、RFT）均做全参数微调，但冻结视觉编码器与多模态投影器（作者主张，见附录 B 表 A）。

阶段设计体现明确的取舍：第一阶段用公开静态定位与单步数据，最大图像像素 $2{,}116{,}800$、序列长度 $16{,}384$、全局批大小 $128$、学习率 $1\times10^{-5}$，目标是高保真单步定位；第二阶段转向自建环境生成的多步轨迹，把分辨率降到 $921{,}600$、序列长度扩到 $60{,}000$、最多 30 轮（视觉工具使用 100 轮），领域混合比 $25{:}25{:}25{:}25$，学习率仍为 $1\times10^{-5}$，全局批大小 $64$；第三阶段 RFT 用拒绝采样蒸馏精炼，学习率降为 $3\times10^{-6}$，其余与第二阶段一致。分辨率与序列长度的此消彼长，是「单步精度」与「长程多模态上下文」之间的直接权衡。

核心训练机制是异步 RL 框架，用于解决三类问题：慢环境交互导致的 GPU 空转、长多模态轨迹的内存瓶颈、以及混合域训练分布漂移。其设计要点为：分离 trainer 与 rollouter 节点（4 个 trainer、12 个 rollouter），每 $K=5$ 次更新同步一次参数，并限制消息队列容量为 $448$ 以约束样本陈旧度；同时显式控制跨域采样比例（移动 25% / 桌面 75%，最大轮数均为 30）。联合 RL 配置为：组大小 $N=8$、mini-batch $48$、训练 250 步、学习率 $4\times10^{-6}$、KL 系数 $\beta=0.0$、截断重要性采样阈值 $C=2.0$、最大响应长度 $53248$、采样温度 $1.0$、最大训练图像像素 $921600$。作者明确关闭 KL 惩罚（$\beta=0$），改用 TIS 缓解 rollout 与训练策略的不匹配（作者主张，见附录 C）。

适用前提：需要可执行、可并发、可给奖励的异构环境后端（AndroidWorld、OSWorld、Weblica、MM-ToolSandBox），以及为稀缺域补充的低成本合成环境（HTML/CSS/JavaScript + 无头浏览器，无需模拟器或虚拟机）。作者指出真实交互环境「对评测不可或缺，但训练扩展成本高」，合成环境是互补数据来源（作者主张，见附录 A 与限制节）。此外，跨域采样比例与队列容量等超参需按域调优，方法本身未给出自动化的比例调度方案。

## 实验设置

评测覆盖定位、移动导航、桌面导航、网页导航与工具调用五类能力，主结果见 Table 3。基线为各规模的 Qwen3-VL-Instruct 初始化模型，并对比同尺寸公开专用模型。所有数字为作者报告值，未在本文档范围内独立复现。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| AndroidWorld | MintAct-8B-Final | Qwen3-VL-8B (47.6) | 未说明 | success rate |
| OSWorld-Verified | MintAct-8B-Final | Qwen3-VL-8B (33.9) | 未说明 | success rate |
| Weblica | MintAct-8B-Final | Qwen3-VL-8B (55.5) | 未说明 | success rate |
| MM-ToolSandBox | MintAct-8B-Final | Qwen3-VL-8B (3.1) | 未说明 | success rate |
| Online-Mind2Web (Om2W) | MintAct-8B-Final | Qwen3-VL-8B (26.5) | 未说明 | success rate |
| UI-Vision | MintAct-8B-Final | 未说明 | 未说明 | score |
| OS-World-G | MintAct-8B-Final | 未说明 | 未说明 | score |
| AndroidWorld | MintAct-4B-Final | Qwen3-VL-4B (45.3) | 未说明 | success rate |
| OSWorld-Verified | MintAct-4B-Final | Qwen3-VL-4B (26.2) | 未说明 | success rate |
| Weblica | MintAct-4B-Final | Qwen3-VL-4B (47.6) | 未说明 | success rate |
| MM-ToolSandBox | MintAct-4B-Final | Qwen3-VL-4B (0.8) | 未说明 | success rate |
| AndroidWorld | MintAct-2B-Final | Qwen3-VL-2B (36.4) | 未说明 | success rate |
| OSWorld-Verified | MintAct-2B-Final | Qwen3-VL-2B (17.0) | 未说明 | success rate |
| Weblica | MintAct-2B-Final | Qwen3-VL-2B (27.7) | 未说明 | success rate |
| MM-ToolSandBox | MintAct-2B-Final | Qwen3-VL-2B (0.0) | 未说明 | success rate |

Table 3 另报告 MintAct-8B-Final 在 MMBench-GUI 80.8、ScreenSpot-V2 93.7、AndroidControl 71.0，以及 MintAct-2B/4B 在 UI-Vision、OS-World-G、AndroidControl、Om2W 上的分数（证据表未逐项列出，故不在此展开）。训练侧配置：SFT 三阶段超参见 Table A，联合 RL 超参见 Table B（组大小 8、mini-batch 48、250 步、学习率 4e-6、$\beta=0.0$、TIS 阈值 2.0、4 trainer / 12 rollouter 节点、$K=5$、队列容量 448、最大响应长度 53248、温度 1.0、最大训练图像像素 921600、移动/桌面采样比 25%/75%、最大轮数 30）。评测预算（如每任务尝试次数、交互轮数上限）在给定摘录中未说明。

## 证据与结果

以下数字全部来自全文摘录（Table 3、Table A、Table B），未做任何换算或推断。

主结果（Table 3，success rate / score）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| AndroidWorld | 67.0 | MintAct-8B-Final | Table 3 |
| OSWorld-Verified | 48.9 | MintAct-8B-Final | Table 3 |
| Weblica | 74.7 | MintAct-8B-Final | Table 3 |
| MM-ToolSandBox | 24.5 | MintAct-8B-Final | Table 3 |
| Om2W | 39.1 | MintAct-8B-Final | Table 3 |
| UI-Vision | 56.6 | MintAct-8B-Final | Table 3 |
| OS-World-G | 64.5 | MintAct-8B-Final | Table 3 |
| MMBench-GUI | 80.8 | MintAct-8B-Final | Table 3 |
| ScreenSpot-V2 | 93.7 | MintAct-8B-Final | Table 3 |
| AndroidControl | 71.0 | MintAct-8B-Final | Table 3 |
| AndroidWorld | 59.8 | MintAct-2B-Final | Table 3 |
| OSWorld-Verified | 36.1 | MintAct-2B-Final | Table 3 |
| Weblica | 56.3 | MintAct-2B-Final | Table 3 |
| MM-ToolSandBox | 7.8 | MintAct-2B-Final | Table 3 |
| AndroidWorld | 62.6 | MintAct-4B-Final | Table 3 |
| OSWorld-Verified | 44.8 | MintAct-4B-Final | Table 3 |
| Weblica | 64.9 | MintAct-4B-Final | Table 3 |
| MM-ToolSandBox | 18.9 | MintAct-4B-Final | Table 3 |

对照（同尺寸 Qwen3-VL 初始化，Table 3）：8B 由 47.6→67.0（AndroidWorld）、33.9→48.9（OSWorld-Verified）、55.5→74.7（Weblica）、3.1→24.5（MM-ToolSandBox）；4B 由 45.3→62.6、26.2→44.8、47.6→64.9、0.8→18.9；2B 由 36.4→59.8、17.0→36.1、27.7→56.3、0.0→7.8。摘录中 2B 的 Om2W 基线为 10.8、MintAct-2B 为 25.3，4B 为 22.0→31.1，但证据表未收录这三项，故仅在此处按摘录列出。

消融：摘录仅称「our ablations (Section 4) show that every stage contributes」，并说明两个 warm-up 阶段在输入分辨率、任务跨度与数据混合上不同；未给出任何消融数值，具体逐阶段增益「摘录未给出」。

训练配置（Table A / Table B）：高分辨率单步 SFT 学习率 $1\times10^{-5}$、global batch 128、max image pixels 2,116,800、max sequence length 16,384；低分辨率多步 SFT 与 RFT 分别为 $1\times10^{-5}$、$3\times10^{-6}$，batch 64，max image pixels 921,600，max sequence length 60,000，domain mixing 25:25:25:25，max turns 30（VTU 为 100）。联合 RL：group size 8、mini-batch 48、250 步、学习率 4e-6、$\beta=0.0$、TIS 阈值 $C=2.0$；异步侧 4 trainer / 12 rollouter 节点、$K=5$、消息队列容量 448；生成侧最大响应长度 53248、温度 1.0；域配置 mobile 25%/30、desktop 75%/30。

## 证据强度评估

证据分级：B（单篇论文自报结果，配置披露充分但无第三方复现）。

理由：正面因素是训练配方与超参披露到可复现粒度（Table A/B 给出学习率、batch、分辨率、序列长度、域混合比、异步同步间隔与队列容量），且改进方向一致——三个尺寸、四个域相对同一初始化（Qwen3-VL-Instruct）全部提升，这种「同源对照 + 跨规模一致」比跨论文比数字更可信。但所有数字均为作者自报，摘录中没有任何复现实验、随机种子数、方差或置信区间，也没有说明评测协议（尝试次数、是否取多次最优）。

主要威胁：

1. 构造效度：核心主张 C1 是「统一不牺牲各域性能」，但摘录只给出各域分数，未给出任何「统一 vs 专用」的受控对照（例如同一数据预算下分别训练专用模型）。跨论文比较（如与 MAI-UI-8B 70.7、WEBLICA-8B 70.6）混入了数据、环境与评测差异，不能直接支撑「统一无代价」。
2. 统计显著性：所有报告为单点数值，无方差、无种子、无显著性检验。8B 在 Om2W 为 39.1，而摘录中 WEBLICA-8B 为 39.2，此类 0.1 量级差距在无方差信息时不可解释；AndroidWorld 67.0 与 MAI-UI-8B 70.7 的差距同样无法判断是否显著。
3. 基线选择与外部效度：主对照是自家初始化 Qwen3-VL，提升幅度大（如 MM-ToolSandBox 3.1→24.5）可能部分来自基线本身在该域近乎失效（2B 基线为 0.0），属于「低基线放大相对增益」。同时 2B/4B 在 Om2W、UI-Vision、OS-World-G 上的对照数字在证据表中缺失，跨规模结论的完整性受限。
4. 评测污染与数据来源：训练环境包含 AndroidWorld、OSWorld、Weblica、MM-ToolSandBox，而这些同时是评测基准；摘录未说明训练与评测任务/实例的隔离方式，也未说明合成环境是否与评测集重叠。这是本档案中最需要外部信息才能排除的风险。

可迁移性判断：训练配方（多阶段 SFT→RFT→联合异步 RL、TIS、$\beta=0$、显式域采样比）与超参可直接借鉴，属于较可信的工程证据；「统一不牺牲性能」这一科学结论目前只应视为作者主张，需等待独立复现或受控消融。

## 边界与反例

**什么观察会推翻结论。** 核心主张 C1（单一模型统一能力且不牺牲各领域性能）依赖「同尺寸对比」这一前提。若出现以下任一观察，结论即被削弱或推翻：

- 同尺寸专用模型在某一领域显著超过 MintAct 且差距超出评测噪声。证据表中已存在一处张力：AndroidWorld 上 MintAct-8B 为 67.0，低于 MAI-UI-8B 的 70.7（摘录 Table 3）。作者用「competitive」而非「best」表述该列，说明移动导航并非全面领先。若后续在更多移动基准上复现该差距，则「不牺牲性能」在移动域不成立。
- 提升主要来自 Qwen3-VL 初始化与数据规模，而非统一训练本身。证据表只给出 Final 模型与初始化的对比（如 8B：47.6→67.0），未给出「同等数据量下各领域独立训练」的对照。缺少这一对照时，读者无法区分「统一带来的增益」与「更多数据/更长训练带来的增益」。
- 消融不完整。作者称「每个阶段都有贡献」（C4），但证据表只给出该主张的定性表述，未列出逐阶段移除后的具体数值。若某阶段移除后指标不降，C4 即被推翻。

**最可能失效的条件。** 论文自述的边界是环境成本：交互式环境「每次 rollout 占用一个实时页面、模拟器或虚拟机」，难以规模化训练（Appendix A）。因此结论最可能在以下条件失效：(1) 目标领域缺乏可合成的低成本环境，只能依赖真实设备，异步 RL 的吞吐优势被环境瓶颈吃掉；(2) 领域间观测/动作空间差异远大于本文覆盖的移动/桌面/网页/工具四类，朴素合并动作集导致干扰（§1 明确警告此风险）；(3) 端侧部署对 8B 仍过大，而 2B 在 MM-ToolSandBox 仅 7.8，工具调用能力接近失效。

**读者可能误推的方向。** 其一，把 48.9/39.1/67.0 当作跨论文可比的绝对水平——不同论文的 OSWorld-Verified 与 Om2W 评测协议、步数预算、环境版本可能不同，证据表未给出 budget 字段。其二，把「异步 RL 框架」当作通用即插即用方案——其稳定性依赖显式控制跨域采样比、队列容量 448、同步间隔 K=5 等具体配置，换环境后需重新调参。其三，把合成环境当作真实环境的替代品——作者定位其为「补充性」低成本来源，而非等价替代。

## 与知识库的关系

**新增内容。** 本文为知识库补入一条「统一视觉智能体 + 异步智能体 RL」的完整配方笔记，此前知识库中的 GUI 智能体条目多为单领域专用模型（grounding、移动、桌面、网页各自独立）。新增的可复用要素有三：(1) 多阶段配方（高分辨单步 SFT → 低分辨多步 SFT → RFT → 各域 RL 专家 → 联合 RL）的完整超参表（Table A / Table B）；(2) 异步 RL 的三个工程手段——分离 trainer/rollouter 节点、按 K 同步参数、限制消息队列容量以控制样本陈旧度；(3) 用编码智能体合成移动/桌面 OS 界面作为训练环境，扩展自 Weblica 的合成网站生成。

**印证内容。** 与知识库中「异步 RL 用于长程智能体后训练」的既有结论一致：本文印证了 rollout 延迟高度可变、环境交互昂贵时同步 RL 会导致 GPU 利用率低（§3.4 三条挑战），并印证 TIS 可缓解 rollout-training 不匹配（β=0 + TIS 阈值 2.0）。同时印证「合成环境可作为低成本训练数据补充」这一方向。

**存在张力的结论。** 其一，知识库若已有「专用模型优于统一模型」的条目，本文构成反例，但需注意 AndroidWorld 上 MAI-UI-8B 70.7 > MintAct-8B 67.0，说明「统一不牺牲性能」在移动域并非无条件成立。其二，本文的 Om2W 39.1 与 WEBLICA-8B 39.2 基本持平（证据表 relations 中作者表述为「超过……附近水平」，措辞含混），不宜作为「超越专用模型」的证据。其三，KL 系数设为 0.0 与部分 RLHF 笔记中「KL 正则防止策略漂移」的常规做法相悖，本文以 TIS 替代该作用，值得单独建条对比。

**可链接笔记 id 建议：** `gui-agent-grounding-specialists`、`mobile-nav-agents`、`desktop-control-agents`、`web-nav-agents`、`visual-tool-use`、`async-rl-for-agents`、`synthetic-env-generation`、`rft-rejection-sampling`、`tis-off-policy-correction`、`kl-penalty-in-rl`。

## 复现与验证计划

目标：在最小成本下验证「统一模型不牺牲单域性能」这一核心主张（C1/C3），而非复现全部 2B/4B/8B 家族。

**环境与数据**：优先选择可离线、确定性高的合成环境（附录 A：HTML/CSS/JavaScript + 无头浏览器，无需模拟器或虚拟机，可单机托管大量实例），避免 AndroidWorld/OSWorld 这类每次 rollout 占用真实模拟器或 VM 的高成本后端（附录 A 明确指出其「costly to scale for training」）。若必须验证真实域，建议只取 OSWorld-Verified 与 Weblica 的小规模子集。

**基线**：Qwen3-VL-Instruct 同尺寸初始化模型，这是论文所有增益的参照点（表 3）。注意 2B/4B/8B 的基线数值不同（如 AndroidWorld 上 36.4 / 45.3 / 47.6），不可跨尺寸比较。

**预算与配置**：按表 A/表 B 复现单阶段即可。最小可行路径是跳过 RL，只做两阶段 SFT（高分辨率单步：lr $1\times10^{-5}$、global batch 128、max image pixels 2,116,800、max seq 16,384；低分辨率多步：lr $1\times10^{-5}$、global batch 64、max image pixels 921,600、max seq 60,000、max turns 30（VTU 100）、domain mixing 25:25:25:25）。若加联合 RL，需 4 trainer + 12 rollouter 节点、250 步、group size 8、mini-batch 48、lr 4e-6、$\beta=0$、TIS 阈值 $C=2.0$、$K=5$、队列容量 448——这是本复现的主要成本瓶颈。

**判据**：以「相对同尺寸 Qwen3-VL 基线的提升方向与幅度」为准，而非绝对分数。论文报告 8B 从 47.6→67.0（AndroidWorld）、33.9→48.9（OSWorld-Verified）、55.5→74.7（Weblica）、3.1→24.5（MM-ToolSandBox）。若复现中某域提升接近 0 或为负，即证伪 C1 的「不牺牲」表述。

**预期失败模式**：(1) 域间干扰——朴素混合数据导致单域退化，论文称需显式控制跨域采样比（mobile 25% / desktop 75%）与异步队列容量；(2) 异步 off-policy 漂移——若去掉 TIS 或放大 $K$，训练可能不稳定；(3) 工具调用域极低基线（2B 为 0.0）使相对增益对噪声极敏感，小样本评测不可靠。

**不确定处**：证据表未给出各基准的评测轮数、随机种子与置信区间，因此单次复现的分数波动无法与论文数值做严格统计比较；上述判据应视为方向性检验。

## 术语与记号

本节汇总正文与附录中出现的关键符号与缩写。符号定义取自方法节的记号表与附录 B 的超参表；未在证据中出现的符号不予列出。

| 术语 | 含义 |
| --- | --- |
| Visual agent | 视觉智能体，直接以像素为输入操作数字设备并完成任务的模型 |
| UI grounding | 界面元素定位，将自然语言指令映射到屏幕上的可交互目标位置 |
| Asynchronous RL | 异步强化学习，rollout 生成与策略训练解耦、参数按间隔同步的训练范式 |
| Off-policy drift | 离策略漂移，异步训练中生成样本的策略与当前训练策略不一致导致的分布偏移 |
| RFT | 拒绝采样微调，用拒绝采样筛选高质量轨迹后做监督微调 |
| TIS | 截断重要性采样，用于缓解 rollout 与训练之间的不匹配 |
| Synthetic environments | 合成环境，用 HTML/CSS/JavaScript 构建并在无头浏览器中渲染的轻量确定性训练环境 |
| AndroidWorld / OSWorld / Weblica / MM-ToolSandBox | 分别为移动端、桌面端、网页导航、视觉工具调用的评测（及训练）环境 |
| $s$ | 策略的条件上下文，包括系统提示、指令与历史 |
| $a$ | 目标推理轨迹与动作 |
| $\pi_\theta$ | 参数为 $\theta$ 的策略模型；SFT 阶段最大化 $\log\pi_\theta(a\mid s)$ |
| $N$ | RL 组大小，表 B 中为 8 |
| $\beta$ | KL 惩罚系数，表 B 中为 0.0（即禁用 KL 惩罚） |
| $C$ | 截断重要性采样阈值，表 B 中为 2.0 |
| $K$ | 异步训练中参数同步间隔，表 B 中为 5 |

补充说明：训练配方分三阶段 SFT/RFT（表 A）与联合 RL（表 B）。表 A 中三阶段均冻结视觉编码器与多模态投影器，仅做全参数微调；三阶段学习率分别为 $1\times10^{-5}$、$1\times10^{-5}$、$3\times10^{-6}$，global batch size 分别为 128、64、64。表 B 中域配置为 mobile 目标比 25% / 最大 30 轮，desktop 目标比 75% / 最大 30 轮；最大响应长度 53248，采样温度 1.0，最大训练图像像素 921600。上述数值均照抄自附录表格，未做换算。

## 自测

以下问题用于检验读者是否真正掌握了本档案中「作者主张」与「可迁移结论」的边界。建议先自行作答，再展开答案核对。

**Q1（基础核对）** MintAct-8B-Final 在 AndroidWorld 与 OSWorld-Verified 上的成功率分别是多少？其相对 Qwen3-VL-8B 初始化的提升幅度各为多少？

<details><summary>答案</summary>
AndroidWorld 为 67.0，OSWorld-Verified 为 48.9（Table 3）。相对 Qwen3-VL-8B 初始化，AndroidWorld 由 47.6 提升至 67.0，OSWorld-Verified 由 33.9 提升至 48.9（§4.2 摘录原文）。注意这两个数字均为作者主张，档案中未见第三方复现记录。
</details>

**Q2（跨小节推理：规模 vs 收益）** 结合 2B/4B/8B 三档在 AndroidWorld 与 MM-ToolSandBox 上的表现，说明「统一训练带来的增益」是否随模型规模单调变化。请用具体数字支撑。

<details><summary>答案</summary>
AndroidWorld：2B 由 36.4→59.8（+23.4），4B 由 45.3→62.6（+17.3），8B 由 47.6→67.0（+19.4）。MM-ToolSandBox：2B 由 0.0→7.8，4B 由 0.8→18.9，8B 由 3.1→24.5。可见增益并非随规模单调递增（AndroidWorld 上 4B 增益最小），但绝对分数随规模上升；工具调用上 8B 绝对分数最高。因此「统一训练有效」在三个规模上都成立，但「规模越大增益越大」这一更强命题不被数据支持。
</details>

**Q3（跨小节推理：训练配方与结果）** 联合 RL 阶段将 KL 系数设为 0.0 并使用 TIS 阈值 2.0，同时采用 4 trainer / 12 rollouter 节点、K=5 同步、消息队列容量 448。这些设置分别针对方法描述中的哪一类问题？若把 K 调大，可能引入什么风险？

<details><summary>答案</summary>
β=0 与 TIS 针对「rollout 与训练策略不匹配 / off-policy drift」；分离 trainer 与 rollouter 节点、按 K 同步参数针对「慢环境交互导致 GPU 利用率低」；消息队列容量上限针对「样本陈旧度」。若把 K 调大，参数同步间隔变长，rollout 样本相对当前策略更陈旧，off-policy 漂移加剧，TIS 截断可能不足以完全缓解——此为基于机制推理，论文未给出 K 的消融数据，属不确定推断。
</details>

**Q4（证据强度）** 档案中 C1–C4 四条 claim 的状态均为「作者主张」。请指出其中哪一条的证据最薄弱，并说明理由。

<details><summary>答案</summary>
C4「多阶段训练配方中每个阶段都对最终能力有贡献」证据最薄弱。其证据为 §1 与 §4 消融，但档案的 ablations 字段仅给出「our ablations (Section 4) show that every stage contributes」这类概括性表述，未提供逐阶段移除后的具体数字。相比之下 C2/C3 至少有 Table 3 的具体数值支撑（虽仍为作者主张）。
</details>

**Q5（可迁移性）** 若你想把 MintAct 的异步 RL 框架迁移到自己的 GUI 智能体训练中，档案中哪些设计是可直接借鉴的、哪些依赖论文未公开的细节？

<details><summary>答案</summary>
可直接借鉴的：trainer/rollouter 节点分离、按固定间隔 K 同步参数、消息队列容量上限控制样本陈旧度、对跨域采样比例做显式控制（Table B 给出 K=5、队列 448、mobile:desktop = 25%:75% 等具体值）。依赖未公开细节的：合成环境的具体构建方式（仅说明用 HTML/CSS/JavaScript 在无头浏览器渲染、由编码智能体生成，未给生成流程细节）、各领域 RL 专家的训练配置、奖励信号定义。此外，论文自述交互式环境「costly to scale for training」，迁移时需评估自身环境吞吐是否构成瓶颈。
</details>
