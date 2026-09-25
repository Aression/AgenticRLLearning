---
id: exploration-guided-prompt-scaffolding
title: 探索引导的提示脚手架多模态强化后训练
summary: 在线强化学习后训练（如GRPO）中，训练提示被统一对待，隐含假设每个提示对当前策略同等有信息量。实际上提示效用差异很大：部分已饱和、部分过难，只有部分掌握者提供有效学习信号。
stage: FRONTIER
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 47
minutes: 54
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.15051
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.15051
objectives: [理解提示效用差异为何破坏 GRPO 等在线 RL 后训练的学习信号, 掌握 EPS（探索潜力分数）如何从已有 rollout 奖励统计中零成本估计, 了解教师模型如何将低效用提示改写为脚手架变体并形成数据飞轮, 评估该方法在域内与 OOD 多模态数学推理基准上的增益与适用边界]
tags: [prompt-scaffolding, multimodal-rl, grpo, curriculum-learning, prompt-selection, post-training]
sources: [not-all-prompts-are-equal-exploration-gu]
related: [grpo, multi-turn-rl, rewards]
prerequisites: [grpo, policy-gradient]
---
## 问题与语境

在线 RL 后训练（GRPO 一类无 critic 算法）已成为 LLM/MLLM 推理能力提升的主流范式，但流水线中存在一个被普遍忽略的隐含假设：训练提示被统一对待，即默认每个提示对当前策略同等有信息量。论文指出这一假设在实践中经常被违反：部分提示在当前策略下已饱和，几乎不产生额外梯度信息；部分提示过难，rollout 一致失败，只提供弱或噪声监督；只有处于「部分掌握」区间的提示才能同时产生成功与失败轨迹，从而支持更有信息量的信用分配。作者把这种提示依赖的有用性差异称为 exploration potential。

该问题在多模态场景更突出：提示同时包含语言与视觉信息，推理难度随语言复杂度与视觉内容在几何、空间、符号任务上联合变化。更关键的是，提示效用不是静态的——策略改进后，曾经有信息量的提示会饱和，另一些提示则可能变得可学。因此训练提示分布本身成为优化问题的一部分，而非固定的数据前提。

已有做法各有失效点。知识蒸馏与教师监督类方法在输出空间操作：教师提供目标生成，学生被优化去复现它；这与在线 RL 中学生从自身 rollout 学习的机制不对齐，token 级模仿并非学生最需要的信号。数据选择与课程/主动学习类方法（如 DAPO 式动态采样、基于不确定性的主动学习）主要做筛选、重加权或重采样，作用在既有提示集合上，不改变提示本身；且多以预测不确定性为采集信号，而非在线 RL 策略下的 rollout 奖励统计。

论文的定位因此是：把教师从「输出来源」重新定位为「自适应课程设计者」，用其改写低效用提示而非提供目标输出；并提出 EPS 作为可直接从 GRPO 已有 rollout 统计计算的提示效用代理，把自适应采样扩展为自适应提示精炼。它并不替代策略优化算法或奖励设计，而是主张提示策展是 RL 后训练中一条互补且欠探索的优化轴。

## 核心主张

论文的核心主张可归纳为四点，均以 GRPO 为唯一对照基线、在 Qwen3-VL-2B/4B 两个规模上验证。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | EPS 可从 GRPO 已有 rollout 统计直接计算，无需额外模型或额外 rollout | §1 贡献段；§2.2；附录 B.5 式(23) | 作者主张 |
| C2 | 在 Geo3K 与 MMK12 上，方法一致优于 GRPO 基线，含域内与 OOD | §4.2 表1、表2 | 作者主张 |
| C3 | MMK12 训练下 2B 模型 MathVision 从 28.62% 提升至 31.91% | §4.2 表2 | 作者主张 |
| C4 | 高 EPS 提示对应更好下游准确率，剔除近零 EPS 提示优于全池训练 | §4.3 图3 | 作者主张 |

C2 的证据面最宽：表1（Geo3K 训练）与表2（MMK12 训练）各覆盖 2B/4B 两个骨干、1 个域内指标与 4 个 OOD 基准，方向一致。例如 MMK12 训练下 OOD 平均从 39.50% 升至 42.83%（2B）、从 50.87% 升至 52.67%（4B）；Geo3K 训练下域内从 55.41% 升至 59.07%（2B）、从 60.57% 升至 65.39%（4B）。作者另在 §1 报告相对提升幅度：域内最高 9.7%、MathVision 11.5%、MMMU-Pro 11.1%。需注意这些均为作者自报数字，无第三方复现，且对照仅为 GRPO，未与 DAPO、GHPO 等提示筛选/提示注入类方法直接比较。

C1 属于机制性主张，理论上自洽（EPS 由 KL 正则化策略改进导出，用 N 个 rollout 奖励的 softmax 加权均值减样本均值估计），但「无需额外开销」的强度取决于重写环节的教师调用成本是否被计入，论文未给出该成本核算，故仍标为作者主张而非共识。

C4 最弱：其证据是图3 的训练曲线（仅 Qwen3-VL-2B、仅前 1,000 RL 步、仅 MMK12），作者自己也声明这些分析「intended as supporting evidence for the proposed design choices rather than a complete causal disentanglement of individual components」。同时作者在 Limitations 中承认 EPS 只是 rollout-based proxy，受有限样本噪声影响，可能无法完美排序所有提示。因此 C4 应视为设计选择的弱支持证据，而非已确立的因果结论。

另需标注两项影响可迁移性的边界：当前脚手架生成是 answer-aware 的（教师可见参考答案，但被指示不得直接泄露最终答案），结果应在教师辅助训练设定下解读；实验仅覆盖可验证奖励的多模态数学与视觉推理任务。

## 机制与方法

方法的核心是把「提示效用」显式建模为在线 RL 的可优化对象，而非把所有提示同等对待。整体是一个动态提示池上的三阶段循环：Score → Filter & Rewrite → Refresh。

**Score（EPS 估计）**。对提示 $x$ 采样 $N$ 个 rollout，得到回答 $y_i$ 与奖励 $r_i=R(x,y_i)$。作者从 KL 正则化策略改进理论出发，定义理想化探索潜力分数 $E(x)$ 为基策略 $\pi(y|x)$ 与 KL 正则化最优策略 $\pi^{*}(y|x)$ 的期望奖励差（$\beta>0$ 为正则系数）。该量不可精确计算，故用自归一化重要性采样近似：权重 $w_i\propto\exp(r_i/\beta)$，归一化后 $\sigma_i=\mathrm{softmax}(r_0/\beta,\ldots,r_{N-1}/\beta)_i$。最终估计量为

$$\hat{\mathcal{E}}(x)=\sum_{i=0}^{N-1} r_i \sigma_i-\bar{r},\qquad \bar{r}=\frac{1}{N}\sum_i r_i.$$

即「奖励加权（偏向高奖励样本）的均值」减去「样本均值」。作者主张 EPS 可直接复用 GRPO 已有的 rollout 统计，无需额外模型或额外 rollout（C1，作者主张）。

**Filter & Rewrite**。按阈值 $\tau$ 划分 $\mathcal{P}_{\text{keep}}=\{x:\hat{\mathcal{E}}(x)>\tau\}$ 与 $\mathcal{P}_{\text{rewrite}}=\{x:\hat{\mathcal{E}}(x)\le\tau\}$，默认 $\tau=0$——依据是理想化 EPS 非负（Prop. B.4），负值主要反映采样噪声或当前过难提示。保留集直接用于 GRPO 更新；重写集连同学生 rollout 与奖励交给教师 $\mathcal{T}$，生成脚手架变体 $x'=\mathcal{T}(x,\{y_i,r_i\},\hat{\mathcal{E}}(x))$，要求保留原任务意图、不直接泄露最终答案，手段包括补全缺失约束、分解子目标、纠正错误推理路径。

**Refresh**。脚手架变体进入刷新缓冲并周期性重新注入训练池；同时维护储备集，定期重估并重新激活效用回升的提示，形成随策略演化的数据飞轮。设计取舍上，教师被重新定位为「自适应课程设计者」而非输出模仿源，与输出级蒸馏区分开；框架对不完美重写有容忍度——若变体后续仍低 EPS，会被再次过滤、继续重写或降权。

**适用前提**：需要可验证奖励信号（本文用 MathRuler 构造奖励）；当前实现为答案感知脚手架（教师可见参考答案），故结果应在教师辅助训练设定下解读；EPS 是 rollout 代理而非未来可学习性的精确度量，受有限样本噪声影响。

## 实验设置

初始策略由 SFT 得到：在 OmniThoughtV（过滤后的 500K 多模态推理样本）上微调。随后在 Geometry3K 与 MMK12 两个数据集上分别做 GRPO 式 RL 训练，训练与评估按数据集独立进行。域内指标为各训练集测试划分的准确率；跨域迁移在 MathVerse、MathVision、MMMU-Val、MMMU-Pro 上评估，OOD Avg 为这四项均值。OOD 评估遵循 LMMs-Eval 框架，使用 Qwen3-VL-Plus 作为 API judge。教师模型为 Qwen-VL-Max，默认阈值 $\tau=0$。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| Geometry3K（域内）+ MathVerse / MathVision / MMMU-Val / MMMU-Pro（OOD） | Qwen3-VL-2B | GRPO | 3,000 RL steps，global batch size 16，8 GPUs FSDP，每提示 N=8 rollouts，最大响应长度 3,072 tokens，lr 1e-6，clip 0.2，KL 0.01 | accuracy (%) |
| Geometry3K（域内）+ MathVerse / MathVision / MMMU-Val / MMMU-Pro（OOD） | Qwen3-VL-4B | GRPO | 同上 | accuracy (%) |
| MMK12（域内）+ MathVerse / MathVision / MMMU-Val / MMMU-Pro（OOD） | Qwen3-VL-2B | GRPO | 同上 | accuracy (%) |
| MMK12（域内）+ MathVerse / MathVision / MMMU-Val / MMMU-Pro（OOD） | Qwen3-VL-4B | GRPO | 同上 | accuracy (%) |

对照条件包括：N/A（未后训练的零样本）、SFT、GRPO、Ours。检查点选择方式为取验证性能最佳者。需注意：所有对比数字均为作者报告值，本档案未记录独立复现；且脚手架生成是答案感知的，比较应理解为教师辅助设定下的结果。

## 证据与结果

本节的数字全部来自论文 Table 1、Table 2 与 §1 正文摘录，未做任何换算或推断。训练配置（两表共用）：3,000 RL steps，global batch size 16，8×GPU FSDP，每提示 $N=8$ 条 rollout，最大响应长度 3,072 tokens，lr $1\times10^{-6}$，PPO-style clip $\epsilon=0.2$，KL 系数 $0.01$；SFT 初始化自 OmniThoughtV 过滤后的 500K 多模态推理样本；教师模型为 Qwen-VL-Max，EPS 阈值 $\tau=0$。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Geo3K acc (%) | 18.97 / 38.69 / 55.41 / 59.07 | Qwen3-VL-2B：N/A / SFT / GRPO / Ours | Table 1 |
| Geo3K acc (%) | 47.08 / 55.07 / 60.57 / 65.39 | Qwen3-VL-4B：N/A / SFT / GRPO / Ours | Table 1 |
| OOD Avg (%) | 33.61 / 38.79 / 39.59 / 41.47 | Qwen3-VL-2B（Geo3K 训练） | Table 1 |
| OOD Avg (%) | 41.58 / 48.33 / 48.54 / 49.75 | Qwen3-VL-4B（Geo3K 训练） | Table 1 |
| MMK12 acc (%) | 37.45 / 36.35 / 51.40 / 56.40 | Qwen3-VL-2B：N/A / SFT / GRPO / Ours | Table 2 |
| MMK12 acc (%) | 46.45 / 56.48 / 68.05 / 71.15 | Qwen3-VL-4B：N/A / SFT / GRPO / Ours | Table 2 |
| OOD Avg (%) | 33.61 / 38.79 / 39.50 / 42.83 | Qwen3-VL-2B（MMK12 训练） | Table 2 |
| OOD Avg (%) | 41.58 / 48.33 / 50.87 / 52.67 | Qwen3-VL-4B（MMK12 训练） | Table 2 |
| MathVision (%) | 28.62 → 31.91 | 2B，MMK12 训练，GRPO → Ours | Table 2 / §4.2 |
| MathVision (%) | 41.78 → 44.41 | 4B，MMK12 训练，GRPO → Ours | Table 2 / §4.2 |
| MMMU-Pro (%) | 36.59 → 40.64 | 2B，MMK12 训练，GRPO → Ours | Table 2 / §4.2 |
| 域内相对提升 | up to 9.7% | Ours vs GRPO | §1 |
| MathVision 相对提升 | 11.5% | Ours vs GRPO | §1 |
| MMMU-Pro 相对提升 | 11.1% | Ours vs GRPO | §1 |

逐基准的 OOD 明细（MathVerse / MathVision / MMMU-Val / MMMU-Pro）在证据表中已逐项列出，此处不重复。注意 Table 1 与 Table 2 的 N/A、SFT 行数值相同（同一 SFT 初始化），仅 GRPO/Ours 行随训练集变化。

消融与对照：Figure 3 按估计 EPS 划分 MMK12 训练提示，比较 2B 模型前 1,000 RL 步，报告「更高 EPS 的提示对应更好的下游准确率，且排除近零 EPS 提示优于在完整提示池上训练」；Figure 4 报告使用提示脚手架训练相比原始提示池上的标准 GRPO 产生「更大且更一致为正」的优势估计。数据规模效应：2B 在 Geo3K 上后训练 OOD 平均 41.47%，在 MMK12 上 42.83%。模型规模效应：2B 与 4B 均提升，相对增益在较小模型上更大，4B 绝对性能最强。消融的具体数值（如各 EPS 分桶的准确率、优势估计的均值/方差）摘录未给出。

## 证据强度评估

证据分级：B（单一来源、内部一致但缺乏独立复现与统计检验）。

理由：结论（EPS 引导的提示脚手架在域内与 OOD 上一致优于 GRPO）由同一论文的 Table 1、Table 2 支持，覆盖 2 个训练集 × 2 个模型规模 × 5 个评测基准，方向一致、无反向结果，且给出了完整训练超参与评测框架（LMMs-Eval + Qwen3-VL-Plus 作 judge）。但所有数字均来自作者自报，无第三方复现、无多种子方差、无显著性检验，故不能升为 A。同时它也不是 C/D：实验设置披露充分（步数、batch、rollout 数、lr、clip、KL、教师模型、阈值 $\tau=0$），且消融（Figure 3/4）与主结果方向自洽。

主要威胁：

1. 构造效度（最关键）。EPS 被作者自己定位为「rollout-based proxy for prompt utility rather than an exact measure of future learnability」，其估计受有限样本噪声影响，「may not perfectly rank all prompts」。因此「EPS 有效」这一中间机制并未被独立验证；Figure 3 只报告相关性方向，未给出分桶数值，无法排除「高 EPS 提示本身就是简单提示」这一混淆解释。

2. 答案感知脚手架带来的归因模糊。作者明确说明当前实现是 answer-aware：教师可见参考答案以生成与答案一致的提示，只是被指示不直接泄露最终答案。这意味着增益可能部分来自教师注入的答案相关信息，而非「提示改写」这一机制本身；作者也要求结果「在教师辅助训练设定下解读」。对想迁移到无答案场景的读者，这是直接的外部效度限制。

3. 基线选择与对照缺失。主对照只有 GRPO 与 SFT，没有与「仅做提示筛选/重加权而不改写」（如动态采样类方法）、「教师直接生成 SFT 数据」等强对照比较，因此无法判断增益来自 EPS 评分、来自改写、还是来自额外的教师算力投入。教师模型 Qwen-VL-Max 的推理成本也未在摘录中量化。

4. 统计显著性与评测污染。所有提升均为单点数值（如 2B MMK12 OOD 39.50→42.83），未报告方差或置信区间；部分提升幅度较小（4B MMK12 的 MMMU-Val 60.67→60.89、MMMU-Pro 50.06→50.29），在无多种子重复的情况下难以判断是否超出噪声。此外 OOD 评测使用 API judge（Qwen3-VL-Plus），judge 版本与提示模板未在摘录中给出，存在评测侧不可复现的风险。

迁移建议：该结论可作为「提示分布自适应改写值得一试」的 B 级证据采纳，但复现时应自行加入多种子方差、无答案脚手架对照，以及「只筛选不改写」的消融，才能把增益归因到脚手架机制本身。

## 边界与反例

**什么观察会推翻结论。** 核心主张 C2（方法一致优于 GRPO）建立在「EPS 能正确排序提示效用」之上。若在相同 3,000 步预算下，把 EPS 替换为随机打分（随机选同样比例的提示送教师重写），仍能得到与表 1/表 2 相当的增益，则 EPS 作为效用信号的必要性被推翻，方法退化为「教师改写数据增强」。作者在 §4.3 明确承认这些分析「intended as supporting evidence for the proposed design choices rather than a complete causal disentanglement of individual components」——即缺少 EPS 与脚手架各自的消融，这是最直接的攻击面。

**最可能失效的条件。** 其一，奖励不可验证时。作者在 Limitations 中说明实验「focus on multimodal mathematical and visual reasoning, which are well-suited to verifiable reward signals」，EPS 的 softmax 重加权依赖 $r_i$ 的尺度与 $\beta$，在噪声大或主观奖励下 $\hat{\mathcal{E}}(x)$ 的排序可能被噪声主导。其二，答案感知脚手架（answer-aware）意味着教师可见参考答案；在无法提供参考答案的部署场景中，脚手架质量与增益均未验证。其三，作者自述 EPS「is a rollout-based proxy for prompt utility rather than an exact measure of future learnability」，且 $\tau=0$ 的合理性依赖「idealized EPS is non-negative (Proposition B.4)」，有限样本下负值被归因于采样噪声——若真实分布中大量提示的 EPS 接近零，阈值划分会退化为噪声驱动的随机路由。

**读者可能误推的方向。** 第一，把「OOD Avg 提升」误读为泛化能力提升：OOD 评测使用 Qwen3-VL-Plus 作为 API judge，与训练奖励函数 MathRuler 不同源，但评测协议差异未被消融。第二，把相对增益外推到更大模型：作者自己指出「relative gains tend to be larger for the smaller model」，4B 上 MMK12 的 OOD Avg 仅从 50.87 升至 52.67，MMMU-Val 从 60.67 到 60.89（+0.22），接近噪声量级，不应据此宣称方法在强模型上同样有效。第三，把「剔除近零 EPS 提示优于全池训练」（图 3）误推为「提示越多越差」——该结论仅在 MMK12、2B、前 1,000 步的设定下成立。

## 与知识库的关系

**新增维度：从「筛选」到「改写」。** 与 DAPO 动态采样 / RLVR 数据筛选类笔记（如 `note-dapo-dynamic-sampling`、`note-rlvr-prompt-filtering`）相比，本文的 delta 是明确的：既有方法在提示池上重加权或重采样，本文新增「教师改写低效用提示」这一维度，把自适应采样扩展为自适应提示精炼。可链接 `note-prompt-curriculum-rl`。

**印证：GRPO 作为 MLLM 多模态推理基线的有效性。** 表 1/表 2 中 GRPO 相对 SFT 与 zero-shot 的一致提升（如 2B/Geo3K：18.97 → 38.69 → 55.41）与 `note-grpo-mllm-baseline` 的结论方向一致，可作为该笔记的补充证据点。同时本文指出 GRPO「将所有提示视为同等信息量」的隐含假设在实践中常被违反，这是对 `note-grpo-assumption-uniform-prompts` 的直接印证。

**张力一：与输出级蒸馏笔记的定位冲突。** `note-teacher-output-distillation` 主张教师监督的核心是匹配输出分布；本文明确将教师重新定位为「adaptive curriculum designer」，用其改写提示而非提供目标输出。二者并非矛盾而是分工，但若读者把本文读成「蒸馏无效」，则与 `note-teacher-output-distillation` 的结论存在误读性张力——本文并未做与输出蒸馏的对照实验。

**张力二：与主动学习/不确定性采样笔记的度量分歧。** `note-active-learning-uncertainty` 用预测不确定性作为采集信号；本文用在线 RL 策略下的 rollout 奖励统计（EPS）。两者在「什么是有信息量的样本」上给出不同答案，且本文未与不确定性基线对比，因此无法判断 EPS 是否优于不确定性度量。这是可链接但尚未闭合的张力点，建议在 `note-active-learning-uncertainty` 中标注「与 EPS 的关系待验证」。

**待补笔记。** 建议新建 `note-eps-exploration-potential-score` 记录式 (23) 的估计形式与 $\tau=0$ 的设定，以及 `note-answer-aware-scaffolding` 记录答案感知这一限制条件。

## 复现与验证计划

目标：在最小成本下验证「EPS 筛选 + 教师脚手架重写」相对 GRPO 的增益是否真实存在，而非超参或数据泄漏所致。

环境与数据。骨干 Qwen3-VL-2B（先做 SFT 初始化，论文用 OmniThoughtV_Filter_0.5M 的 500K 多模态推理样本）。RL 训练集二选一：Geometry3K 或 MMK12；域内指标用各自 test split，OOD 用 MathVerse、MathVision、MMMU-Val、MMMU-Pro，OOD Avg 为四者均值。奖励用 MathRuler 构造可验证奖励；OOD 评测按 LMMs-Eval 框架，判分用 Qwen3-VL-Plus API。

预算与超参（照抄论文设置）。3,000 RL steps，global batch size 16，8 GPU FSDP，每提示 N=8 rollouts，max response length 3,072 tokens，lr $1\times10^{-6}$，PPO-style clip $\epsilon=0.2$，KL 系数 $0.01$，EPS 阈值 $\tau=0$，教师为 Qwen-VL-Max。按最佳验证性能选 checkpoint。

基线。同设置下的标准 GRPO（无 EPS 筛选、无脚手架）。可选加 SFT 与 zero-shot（N/A）作参照。

判据。主判据为域内与 OOD Avg 是否同时超过 GRPO。可核对的锚点：2B/Geo3K 59.07 vs 55.41、OOD Avg 41.47 vs 39.59；2B/MMK12 56.40 vs 51.40、OOD Avg 42.83 vs 39.50；4B/MMK12 71.15 vs 68.05、OOD Avg 52.67 vs 50.87。注意 4B/Geo3K 的 OOD Avg 仅 49.75 vs 48.54，增益很薄，应视为噪声敏感区。

预期失败模式。(1) EPS 为 rollout 代理，有限样本噪声可能无法正确排序提示，$\tau=0$ 未必最优；(2) 脚手架为 answer-aware，若教师提示泄露答案，增益可能来自标签泄漏而非课程设计——需做无答案脚手架对照；(3) 教师重写会引入教师偏好/偏见，改变训练分布；(4) 任务限于可验证奖励的多模态数学与视觉推理，迁移到非可验证奖励未验证。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| EPS（Exploration Potential Score） | 探索潜力分数，基于 rollout 的提示效用代理，近似当前策略与 KL 正则化改进策略的期望奖励差 |
| $\mathcal{E}(x)$ | 理想化 EPS，提示 $x$ 的效用 |
| $\hat{\mathcal{E}}(x)$ | 由 rollout 估计的 EPS，在线路由信号而非标定量 |
| $x$ | 输入提示，可含文本与图像 token |
| $y$ | 模型生成的回答 |
| $\pi(y\mid x)$ | 给定提示的条件策略；$\pi^{*}(y\mid x)$ 为 KL 正则化最优策略 |
| $R(x,y)$ | 提示-回答对的奖励 |
| $\beta$ | KL 正则化系数，$\beta>0$ |
| $\sigma_i$ | 奖励 softmax 归一化权重，$\sigma_i=\mathrm{softmax}(r_0/\beta,\dots,r_{N-1}/\beta)_i$ |
| $\bar{r}$ | $N$ 个 rollout 奖励的样本均值 |
| $\tau$ | EPS 筛选阈值，默认 0 |
| $\mathcal{P}_{\text{keep}}/\mathcal{P}_{\text{rewrite}}$ | 保留集 / 重写集 |
| GRPO | 组相对策略优化，无 critic 的在线 RL 算法，用组内归一化优势更新策略 |
| Prompt Scaffolding | 提示脚手架，教师对低效用提示生成保留原任务意图的引导性改写 |
| Data Flywheel | 数据飞轮，提示被持续评分、重写、刷新，使训练分布随策略演化自适应 |
| KL-Regularized Policy Improvement | KL 正则化策略改进，在奖励最大化与相对参考策略的 KL 惩罚间权衡 |
| Self-Normalized Importance Sampling | 自归一化重要性采样，用 softmax 奖励权重从当前策略样本估计最优策略期望 |
| In-Domain / OOD | 域内（训练集测试划分）/ 分布外（跨域基准）评估 |
| Answer-Aware Scaffolding | 答案感知脚手架，教师生成时可见参考答案但不直接泄露最终答案 |

估计式：$\hat{\mathcal{E}}(x)=\sum_{i=0}^{N-1}r_i\sigma_i-\bar{r}$。划分规则：$\mathcal{P}_{\text{keep}}=\{x:\hat{\mathcal{E}}(x)>\tau\}$，$\mathcal{P}_{\text{rewrite}}=\{x:\hat{\mathcal{E}}(x)\leq\tau\}$。重写算子：$x'=\mathcal{T}(x,\{y_i,r_i\}_{i=1}^{N},\hat{\mathcal{E}}(x))$。

## 自测

以下问题用于检验你是否真正掌握了该工作的适用边界，而非仅记住数字。答案中标注了「作者主张」与「不确定」之处。

**Q1.** 本文的 EPS 估计量 $\hat{\mathcal{E}}(x)=\sum_{i=0}^{N-1}r_{i}\sigma_{i}-\bar{r}$ 中，$\sigma_i$ 与 $\bar r$ 分别是什么？为什么作者选择 $\tau=0$ 作为默认阈值？

<details><summary>答案</summary>
$\sigma_{i}=\mathrm{softmax}(r_{0}/\beta,\ldots,r_{N-1}/\beta)_{i}$ 是奖励的 softmax 归一化权重（自归一化重要性采样权重），$\bar{r}=\frac{1}{N}\sum_{i}r_{i}$ 是 $N$ 个 rollout 奖励的样本均值。作者主张：理想化 EPS 非负（Proposition B.4, Appendix B），因此负的有限样本估计主要反映采样噪声或当前过难的提示，$\tau=0$ 是自然的工作点。注意作者同时声明 $\hat{\mathcal{E}}(x)$ 应被理解为在线路由信号而非校准量。
</details>

**Q2.** 若你的任务没有可验证奖励（例如开放式写作），本文方法能否直接迁移？请结合证据表与全文说明。

<details><summary>答案</summary>
不能直接迁移。作者在 Limitations 中明确：实验聚焦于多模态数学与视觉推理，「well-suited to verifiable reward signals」，并称扩展到非可验证奖励是未来方向。此外 EPS 的推导依赖奖励 $R(x,y)$ 与 KL 正则化策略改进，softmax 权重 $\exp(r_i/\beta)$ 也预设了标量奖励。因此这是作者自认的适用边界，非本文已验证结论。
</details>

**Q3.** 表 1 与表 2 中，2B 与 4B 模型的相对增益有何系统性差异？作者给出的解释是什么？该解释是否已被验证？

<details><summary>答案</summary>
作者主张相对增益在较小模型上更大（如 MMK12 上 2B 的 OOD Avg 从 39.50→42.83，4B 从 50.87→52.67），同时 4B 在所有基准上取得最强绝对性能。作者给出的可能解释是：更强的基座模型已能胜任更大比例的提示，留给提示级精炼的空间更小。这是「一种可能的解释」（one possible explanation），属推测性说明，未被实验直接验证。
</details>

**Q4.** 跨小节推理：若把本文与 DAPO 类动态采样方法对比，二者在「如何处理低效用提示」上的根本差异是什么？这一差异对训练分布有何影响？

<details><summary>答案</summary>
证据表的 relations 指出：DAPO 等动态采样是「筛选/重加权/重采样」提示，而本文新增「改写」维度——低 EPS 提示被教师改写为脚手架变体后重新注入训练池。因此本文改变的是训练分布本身（通过重写生成新提示），而非仅改变采样权重。作者还维护储备集，定期重估并重新激活效用回升的提示，形成随策略演化的数据飞轮。需注意：作者称与这些方法「互补」，但未做与 DAPO 的直接实验对比（证据表中无此消融）。
</details>

**Q5.** 跨小节推理：本文的脚手架生成是「答案感知」的。这对结果解读与复现意味着什么？若你想在无参考答案的场景复现，会遇到什么问题？

<details><summary>答案</summary>
作者明确说明：教师模型被提供参考答案以产生与答案一致的提示，同时被指示不直接揭示最终答案，因此结果「应在教师辅助训练设定下解读」（should be interpreted under a teacher-assisted training setting）。这意味着：其一，报告的增益部分来自教师可见答案这一信息优势，不能等同于纯学生自举；其二，若在无参考答案场景复现，脚手架质量可能下降，且「不泄露答案」的指令遵循程度无法保证。作者将完全无答案的脚手架列为未来工作，故该设定下的表现属不确定。
</details>
