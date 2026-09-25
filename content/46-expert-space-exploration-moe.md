---
id: expert-space-exploration-moe
title: MoE强化学习中的专家空间探索
summary: MoE大模型在RL后训练中，rollout依赖确定性Top-K路由，同一前缀反复激活相同专家，探索仅停留在token空间，缺乏对稀疏计算路径的显式探索；而直接扰动路由虽能提升多样性，却可能激活不匹配专家、损害rollout质量。
stage: FRONTIER
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 46
minutes: 54
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.13058
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 6
full_text_url: https://arxiv.org/html/2609.13058
objectives: [理解MoE RL中确定性Top-K路由导致的探索瓶颈, 掌握ESRL的熵自适应噪声与锚定专家采样机制, 了解Rollout Routing Replay如何对齐训练与生成路由, 评估路由扰动作为架构感知探索手段的收益与边界]
tags: [MoE, Reinforcement Learning, Routing, Exploration, GRPO, LLM Post-training]
sources: [expert-space-exploration-in-moe-reinforc]
related: [grpo, policy-gradient, multi-turn-rl]
prerequisites: [grpo, policy-gradient]
---
## 问题与语境

MoE 大模型的 RL 后训练目前把专家选择当作固定的架构组件：rollout 依赖确定性 Top-$K$ 路由，同一前缀反复激活同一组专家，探索只发生在 token 空间。论文指出，token 采样虽然能通过改写前缀间接影响后续路由，但并不会在同一上下文下显式探索替代的专家计算路径；而每个 token 被路由到的稀疏专家集合恰恰决定了 next-token 分布。因此「计算路径空间」是一个被现有 RL 算法（GRPO、DAPO 等）忽略的探索维度。

已有做法的失效点有两层。其一，直接对 router logits 注入噪声确实能提升多样性：论文的实证分析显示，噪声尺度 $\sigma$ 增大时专家分配改变率上升、Top-$K$ Jaccard 相似度下降、专家负载 CV 下降（§2.1 图 2），且下一 token 分布发生系统性位移与弥散（§2.2 图 3），序列级 Self-BLEU 下降，呈现类似温度的精度–多样性权衡（§2.3 图 4）。其二，这种无约束扰动会激活与当前隐状态不匹配的专家，在同等 Self-BLEU 下往往比纯温度采样精度更低（§2.3 图 4(b)），即多样性收益被 rollout 质量损失抵消。

论文的定位不是提出新的 RL 目标或奖励设计，而是把「专家路由扰动」工程化为一个可控、且与训练一致的架构感知探索机制：用路由熵自适应决定噪声强度（式 4），用锚定专家采样把随机性限制在候选池内（式 5–9），并用 Rollout Routing Replay 让 rollout 时被探索到的专家在优化阶段重新被激活并获得梯度（式 12–14）。策略优化仍沿用 GRPO 目标，不改奖励与损失形式，因此作者将其定位为与 reward-level、loss-level 改进正交的探索维度（§4.2、§6）。

## 核心主张

论文的核心主张可拆为「机制层」与「效果层」两类。机制层主张路由扰动确实构成一个独立于 token 采样的探索维度：噪声增大时专家分配改变率上升、Top-$K$ Jaccard 下降、专家利用更均衡（C1），且这种路由改变会传播到输出端，使原 Top-1 token 排名下降、Top-20 集合相似度降低（C2）。效果层主张 ESRL 在多个 MoE 骨干与任务域上稳定优于 GRPO 及其变体（C3、C4）。

| # | 主张 | 证据 | 状态 |
| --- | --- | --- | --- |
| C1 | 路由噪声增大时专家分配改变率上升、Top-$K$ Jaccard 相似度下降，专家利用更均衡 | §2.1 图 2(a)(b) | 作者主张 |
| C2 | 路由扰动会改变下一 token 分布，使原 Top-1 token 排名下降、Top-20 集合相似度降低 | §2.2 图 3(a)(b) | 作者主张 |
| C3 | ESRL 在 Qwen3-30B-A3B 上数学基准平均 Pass@1/Pass@8 较 GRPO 提升 3.2/4.5 个百分点 | §4.2 表 1 | 作者主张 |
| C4 | ESRL 在科学推理与代码任务上平均 Pass@1 由 53.2 升至 55.9、Pass@8 由 64.9 升至 77.0 | §4.3 表 2 | 作者主张 |
| C5 | ESRL 在 Sigma / Moonlight-16B-A3B 上平均 Pass@8 较 GRPO 分别提升 2.7 / 3.5 点 | §4.2 | 作者主张 |
| C6 | 锚定专家防止可靠路径被过度破坏，熵自适应噪声优于固定扰动强度 | 消融（§1 贡献概述、§6） | 作者主张 |

最强的是 C4：它对应 §4.3 表 2 的完整逐基准数字（GPQA 35.7→39.0 / 53.5→76.8，MMLU-Pro 57.6→62.5 / 67.4→82.5，MMLU-Redux 79.3→80.3 / 86.3→94.5，LiveCodeBench v6 40.1→42.0 / 52.2→54.3），且 Pass@8 的大幅提升（GPQA +23.3、MMLU-Pro +15.1）与「扩大成功轨迹覆盖而非仅移动单样本精度」的解释自洽；同时表 2 中 ESRL 也优于 GSPO 与 GRPO-R3，说明增益不只是相对最弱基线。C3 与 C5 同为跨骨干证据，但证据表中只给出聚合数字，缺少逐基准明细，可信度略低一档。

最弱的是 C6：消融结论在给定摘录中只有定性表述（「锚定专家防止可靠路径被过度破坏」「熵自适应噪声优于固定扰动强度」「候选池大小决定可探索专家范围」），没有对应的数值、表号或图号，无法判断效应量级与是否在多种子下稳定。此外 C1、C2 属于机制性观察，摘录中同样只给出趋势描述而无具体数值，且实验仅在 Qwen3-30B-A3B-Base（48 个 MoE 层、每 token 每层激活 128 个路由专家中的 8 个）上完成，向 top-1 与 shared-expert 路由结构的迁移性未被这两条主张直接覆盖。所有主张的状态均为「作者主张」，本档案未获得独立复现证据。

## 机制与方法

ESRL 的核心主张是：MoE 的稀疏路由本身构成一个可探索的维度，与 token 采样互补。标准 rollout 使用确定性 Top-$K$ 路由，同一前缀反复激活同一组专家，替代计算路径从未被显式探索。ESRL 在 rollout 阶段对路由器 logits 注入噪声，使同一前缀可激活替代专家路径，从而改变下一 token 分布。

**符号约定**：$l_{t,\ell,e}$ 为 token $t$、层 $\ell$、专家 $e$ 的原始路由器 logit；$p_{t,\ell,e}$ 为对全部路由专家归一化后的路由概率；$\mathcal{H}_{t,\ell}\in[0,1]$ 为归一化路由器熵；$\sigma_{t,\ell}$ 为自适应噪声尺度；每层每 token 激活 $K$ 个专家，拆为 $K_{\mathrm{anchored}}$ 个锚定专家与 $K_{\mathrm{explore}}$ 个探索专家，$K_{\mathrm{anchored}}+K_{\mathrm{explore}}=K$；$M_{\mathrm{explore}}$ 为探索候选池大小；$\mathcal{S}^{\mathrm{roll}}$、$\mathcal{S}^{\mathrm{train}}$ 分别为 rollout 与训练时实际激活的专家集合；$\mathcal{Z}^i$ 为第 $i$ 条轨迹的完整稀疏计算路径记录；$\rho_t^i$ 为 token 级策略比率。

**三个组件。**

（1）熵自适应噪声。先归一化路由分布并计算归一化熵：
$$p_{t,\ell,e}=\frac{\exp(l_{t,\ell,e})}{\sum_{j=1}^{E}\exp(l_{t,\ell,j})},\qquad \mathcal{H}_{t,\ell}=-\frac{1}{\log E}\sum_{e=1}^{E}p_{t,\ell,e}\log p_{t,\ell,e}$$
噪声尺度由熵线性插值得到：
$$\sigma_{t,\ell}=\sigma_{\min}+(\sigma_{\max}-\sigma_{\min})(1-\mathcal{H}_{t,\ell})$$
设计取舍：路由分布越尖锐（熵越低）说明确定性 Top-$K$ 反复选中窄专家子集，需要更大扰动才能改变选择；分布已弥散时则减小扰动，避免无谓破坏。这是「按置信度分配探索预算」的启发式，而非从目标函数推导出的最优规则。

（2）锚定专家采样。锚定集由原始 logits 的 Top-$K_{\mathrm{anchored}}$ 直接选出，保留高置信计算路径；探索候选池取剩余专家中 logits 最高的 $M_{\mathrm{explore}}$ 个，仅对池内 logits 加高斯噪声 $\xi\sim\mathcal{N}(0,\sigma_{t,\ell}^2)$ 后取 Top-$K_{\mathrm{explore}}$，最终激活集为二者并集。关键细节：扰动 logits 只用于决定激活哪些专家；专家索引确定后，聚合权重仍由原始 logits 计算，从而保持原路由器对所选专家的相对置信度不变。取舍在于：无约束扰动会激活与当前隐状态不匹配的专家、损害 rollout 质量，锚定 + 候选池是对这一风险的显式约束，代价是探索范围被 $M_{\mathrm{explore}}$ 限制。

（3）Rollout Routing Replay（R3）。若训练时重算确定性 Top-$K$，同一 token 的专家集可能与 rollout 不同，被探索的专家拿不到梯度。ESRL 记录 rollout 时每 token 每层的专家激活集合 $\mathcal{Z}^i$ 与 rollout 对数概率，优化时绕过 Top-$K$、固定复用该集合，仅用当前 logits 重算门控权重，使被探索专家获得梯度并降低 rollout 与训练的路由不匹配。策略优化沿用 GRPO 目标，不修改奖励函数与损失形式。

**适用前提**：模型必须是稀疏 MoE 且路由为 Top-$K$ 形式（论文覆盖 top-$K$、top-1 与 shared-expert 结构）；训练框架需支持记录并回放专家激活路径；评估时路由扰动被关闭。方法在 rollout 阶段生效，因此与 reward 层、loss 层的改进正交，作者称可与之组合。

## 实验设置

评估覆盖数学推理、科学推理与代码生成三类任务。除另有说明外，每个问题独立采样 32 条回复，报告 Pass@1 与 Pass@8；Pass@1 为 32 条采样的平均正确率，Pass@8 由同批采样用无偏估计量估计。全部评估通过 OpenCompass 进行，且评估时关闭路由扰动。训练数据方面，科学推理与代码任务使用 NVIDIA 的 Nemotron-RL-knowledge-mcqa 数据集与代码数据集。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
| --- | --- | --- | --- | --- |
| Qwen3-Math（数学） | Qwen3-30B-A3B-Base | GRPO（另对比 GSPO、RO-GRPO） | 未说明 | Pass@1/Pass@8 |
| GPQA / MMLU-Pro / MMLU-Redux / LiveCodeBench v6（科学推理与代码） | Qwen3-30B-A3B | GRPO（另对比 GSPO、GRPO-R3） | 未说明 | Pass@1/Pass@8 |
| OlympiadBench / AIME / AMC / MinervaMath（数学） | Qwen3-30B-A3B-Instruct | GRPO（另对比 GRPO-R3、GSPO） | 未说明 | Pass@1/Pass@8 |
| Sigma-Math | Sigma | GRPO | 未说明 | 平均 Pass@8 |
| Moonlight-16B-A3B | Moonlight-16B-A3B | GRPO | 未说明 | 平均 Pass@8 |

主要结果（作者主张，来自表 1、表 2、表 3）：Qwen3-30B-A3B 上 ESRL 平均 Pass@1 42.1、Pass@8 64.2，较 GRPO 提升 3.2 与 4.5 个百分点；科学推理与代码四基准平均 Pass@1 由 53.2 升至 55.9、Pass@8 由 64.9 升至 77.0，其中 GPQA Pass@8 提升 23.3、MMLU-Pro 提升 15.1、MMLU-Redux 提升 8.2、LiveCodeBench v6 Pass@1 提升 1.9、Pass@8 提升 2.1；Qwen3-30B-A3B-Instruct 上平均 Pass@1 由 63.4 升至 68.9、Pass@8 由 77.3 升至 79.0；Sigma 与 Moonlight-16B-A3B 上平均 Pass@8 分别较 GRPO 提升 2.7 与 3.5 点。

消融与参数分析（作者主张）：锚定专家防止可靠路径被过度破坏；熵自适应噪声优于固定扰动强度；候选池大小决定可探索专家范围，锚定专家数与扰动位置进一步塑造精度—多样性权衡。此外，解耦专家空间与 token 空间探索的实验显示，仅路由噪声即可支撑有效 RL 训练并改善 Pass@$N$ 曲线。需注意：证据表中未给出各实验的采样预算、训练步数与算力开销，这些字段均标注为「未说明」；上述数字均为论文自报，本档案未记录独立复现。

## 证据与结果

ESRL 的核心量化证据集中在三张表：表1（数学，三种 MoE 骨干）、表2（科学+代码，Qwen3-30B-A3B）、表3（Qwen3-30B-A3B-Instruct 数学）。摘录中可直接确认的数字如下。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Pass@1 / Pass@8 | 42.1 / 64.2，较 GRPO +3.2 / +4.5 | Qwen3-30B-A3B-Base，数学基准平均 | §4.2 表1 |
| Pass@8 | +2.7 / +3.5 | Sigma / Moonlight-16B-A3B 平均，ESRL vs GRPO | §4.2 |
| Pass@1 / Pass@8 | 53.2 → 55.9，64.9 → 77.0 | Qwen3-30B-A3B，GPQA/MMLU-Pro/MMLU-Redux/LiveCodeBench v6 平均 | §4.3 表2 |
| Pass@8 | +23.3 | GPQA，ESRL vs GRPO | 表2 |
| Pass@8 | +15.1 | MMLU-Pro，ESRL vs GRPO | 表2 |
| Pass@8 | +8.2 | MMLU-Redux，ESRL vs GRPO | 表2 |
| Pass@1 / Pass@8 | +1.9 / +2.1 | LiveCodeBench v6，ESRL vs GRPO | §4.3 |
| Pass@1 / Pass@8 | 63.4 → 68.9，77.3 → 79.0 | Qwen3-30B-A3B-Instruct，OlympiadBench/AIME/AMC/MinervaMath 平均 | §4.4 表3 |
| Pass@1 / Pass@8 | +5.5 / +1.7 | 同上，平均 Δ | 表3 |

表2 的逐项对照（GRPO → ESRL）：GPQA 35.7→39.0（Pass@1）、53.5→76.8（Pass@8）；MMLU-Pro 57.6→62.5、67.4→82.5；MMLU-Redux 79.3→80.3、86.3→94.5；LiveCodeBench v6 40.1→42.0、52.2→54.3。表2 同时给出 GSPO（平均 53.9/71.5）与 GRPO-R3（52.3/69.4）作为对照，ESRL 在平均与全部四项 Pass@8 上均最高；但 MMLU-Redux 的 Pass@1 上 GSPO 为 75.3，低于 GRPO 的 79.3，说明该列存在基线间不一致。表3 中 GRPO-R3 与 GSPO 平均 Pass@1 均为 67.9，ESRL 为 68.9，差距较小。

消融方面，摘录只给出三条定性结论：锚定专家防止可靠路径被过度破坏；熵自适应噪声优于固定扰动强度；候选池大小决定可探索专家范围。摘录未给出这些消融的具体数值、扰动强度网格或候选池大小的取值区间，因此无法量化各组件贡献。对照还包括 §2.3 的直接路由扰动 vs 温度采样（同等 Self-BLEU 下直接扰动精度更低），以及 §4.2 关于 ESRL 与奖励/损失层方法正交的论述。评测协议见附录 A：每题独立采样 32 条回复，Pass@1 为 32 条平均正确率，Pass@8 用无偏估计量，评测时关闭路由扰动。

## 证据强度评估

证据分级：B（中等偏强，但不足以直接迁移）。

理由：正面看，结论在三种 MoE 骨干（Qwen3-30B-A3B-Base、Qwen3-30B-A3B-Instruct、Sigma、Moonlight-16B-A3B）与三个任务域（数学、科学、代码）上方向一致，且表2 同时报告了 GSPO 与 GRPO-R3 两个较强基线，ESRL 在平均 Pass@8 上领先幅度大（+12.2 平均）。评测协议明确（32 样本、Pass@8 无偏估计、评测时关闭扰动），方法描述完整到可复现级别（公式 2–16 给出噪声尺度、锚定/探索划分、权重用原始 logits、R3 回放）。但所有数字均为作者自报，档案中无第三方复现、无方差/置信区间、无随机种子数，故不能升为 A。

主要威胁：

1. 统计显著性与报告粒度。摘录只给点估计与 Δ，未给标准差、种子数或显著性检验。表3 中 ESRL 平均 Pass@1 68.9 vs GSPO/GRPO-R3 67.9，差 1.0 分；AMC 上 ESRL Pass@8 91.3 与 GRPO 相同（Δ=+0.0），说明部分子项增益在噪声量级。Pass@8 的大幅提升（如 GPQA +23.3）可能部分来自采样覆盖而非策略质量，需与 Pass@1 的 +3.3 对照解读。

2. 基线选择与混淆。表2 中 GRPO-R3 已包含路由回放，其平均 Pass@8（69.4）高于 GRPO（64.9），说明 R3 本身贡献约 +4.5；ESRL 相对 GRPO-R3 的净增益需从表2 逐项相减才能得到，摘录未直接给出该差值。若 ESRL 的主要增益来自 R3 而非路由扰动，则「专家空间探索」这一机制归因会被削弱。此外 MMLU-Redux 上 GSPO Pass@1 低于 GRPO，提示基线训练配置可能未完全对齐。

3. 构造效度。§2.1/§2.2 的机制证据（专家改变率、Jaccard、Top-20 相似度、PCA 位移）均为作者主张，且是相关性观察，未证明「路由扰动 → 下一 token 分布改变 → 序列多样性 → RL 收益」这条因果链的每一环。§2.3 明确指出无约束扰动在同等 Self-BLEU 下精度更低，即扰动本身有质量代价，ESRL 的锚定+熵自适应是缓解手段，但摘录未给出这些组件各自的定量消融。

4. 外部效度与评测污染。所有实验限于 Qwen3/Sigma/Moonlight 系列与数学/科学/代码基准，未涉及长上下文、多语言或 agent 类任务；GPQA、MMLU-Pro、LiveCodeBench v6 等均为公开基准，存在训练数据污染可能，摘录未报告去污染处理。此外超参（σ_min、σ_max、K_anchored、M_explore）的敏感性只在定性层面描述，迁移到新 MoE 结构时如何设定未知。

## 边界与反例

**什么观察会推翻结论。** 论文的核心因果链是「路由扰动 → 替代专家路径 → 下一 token 分布改变 → 序列多样性上升 → RL 收益」。若在受控实验中，把 ESRL 的噪声注入替换为等量 token 级温度采样后，Pass@8 增益消失或反超，则「专家空间是独立且互补的探索维度」这一主张（C1–C4 的上游假设）即被推翻。作者自己给出的反例线索是：无约束路由扰动在同等 Self-BLEU 下常低于温度采样精度（§2.3 图4(b)），说明扰动本身并不自动带来质量提升，收益依赖锚定与熵自适应两个约束项。

**最可能失效的条件。** 其一，路由分布本身已弥散（$\mathcal{H}$ 高）时，$\sigma=\sigma_{\min}+(\sigma_{\max}-\sigma_{\min})(1-\mathcal{H})$ 会把噪声压到接近 $\sigma_{\min}$，探索量趋近于零，此时 ESRL 退化为 GRPO-R3。其二，$M_{\mathrm{explore}}$ 过小则候选池无法覆盖有效替代路径，过大则引入不匹配专家、损害 rollout 质量——论文只给出「候选池大小决定可探索专家范围」的定性消融，未给出跨模型的取值规律。其三，top-1 路由与 shared-expert 结构（Sigma、Moonlight）上 $K_{\mathrm{anchored}}$ 的可分配空间更小，锚定-探索的划分自由度受限。

**未验证但易被误推的方向。** 证据表与摘录中所有实验均为数学、科学推理与代码，且评测时关闭路由扰动（附录 A）；因此不能外推到开放式生成、长程 agent 任务或需要严格格式遵循的场景。论文亦未验证 ESRL 与 reward-level（RO-GRPO）、loss-level（GSPO）方法的叠加效果，只声明「正交、可组合」——这是作者主张而非已复现结论。此外，R3 需要存储每条轨迹每 token 每层的专家集合，显存/带宽开销随 $T_i \times L$ 增长，论文未报告该成本，读者不应默认其可忽略。最后，所有增益数字均来自作者自报表格，证据表中无第三方复现记录，应标注为「作者主张」。

## 与知识库的关系

**新增维度（相对 GRPO/DAPO 等 RL 算法笔记）。** 既有笔记把探索完全放在 token 空间（温度、top-p、熵正则、组内采样）。ESRL 新增的是「稀疏计算路径」这一探索轴：同一前缀下通过扰动 router logits 激活替代专家集合，且用 Rollout Routing Replay 把该离散路径固定到训练阶段，使被探索专家获得梯度。这补上了 MoE RL 笔记中长期缺失的一环——rollout 与训练的路由不一致（importance ratio 因重算 Top-K 而漂移）。可链接笔记：`rl/grpo`、`rl/dapo`、`moe/routing`、`rl/rollout-training-mismatch`。

**印证的部分。** 与「RL 训练中策略逐渐集中、rollout 多样性衰减」的既有结论一致：§2.3 图4(a) 显示后续 checkpoint 需要更高温度才能维持同等 Self-BLEU。这与 `rl/entropy-collapse`、`rl/diversity-decay` 笔记相互印证，并给出一个架构层面的缓解手段。同时印证了「探索强度应与当前分布置信度挂钩」这一直觉（熵自适应噪声），与 `rl/adaptive-temperature` 的思路同构但作用在路由层。

**存在张力的结论。** 其一，与「温度采样足以提供探索」的默认假设存在张力：论文主张路由扰动是温度式效应但可独立支撑 RL 训练（§1 贡献 3），若该结论成立，则 `rl/temperature-sampling` 笔记中「多样性只需调温度」的表述需限定于稠密模型。其二，与「MoE 路由应保持确定性以保证训练稳定」的工程共识存在张力——ESRL 恰恰在 rollout 阶段破坏确定性，再用 R3 在训练阶段恢复一致性；这提示 `moe/training-stability` 笔记中的「确定性路由」应细化为「rollout 可随机、训练需回放」。其三，证据表中「路由扰动在同等 Self-BLEU 下常低于温度采样精度」与「ESRL 全面超越 GRPO」并列，说明增益来自约束机制而非扰动本身，链接 `moe/expert-load-balance` 时需注意区分「均衡」与「有效」。

## 复现与验证计划

目标：在自有 MoE 模型上验证「路由层扰动是否带来超出 token 采样的探索增益」，并检验 R3 回放是否必要。建议按最小可行路径分三步。

**环境与数据**：需支持自定义路由 logits 注入与专家路径记录的 MoE 训练框架（论文未给出具体框架，属不确定项）。任务先用数学推理（如 AIME/AMC 类），因其 Pass@1/Pass@8 信号清晰、评测成本低。评测协议对齐论文：每题独立采样 32 条回复，报告 Pass@1 与 Pass@8，评测时关闭路由扰动（Appendix A）。

**基线**：至少三条——(1) 纯 GRPO；(2) GRPO + R3（即只做路由回放、不做扰动，论文中作为对照出现）；(3) 无约束路由扰动（全专家加噪）。第 (3) 条用于复现「直接扰动会降低 rollout 质量」这一关键动机。

**预算**：论文未披露训练步数、GPU 时与 rollout 组大小，故无法照抄。建议以「与 GRPO 基线同等 rollout token 预算」为约束做对照，并额外跑一组更小 group size，因为作者主张 ESRL 在有限采样预算下仍保持更多 advantage-informative group。

**判据**：主判据为平均 Pass@8 相对 GRPO 的提升方向与幅度量级（论文报告数学基准 +4.5 个百分点、科学/代码平均 +12.2）。次判据：专家负载 CV 是否下降、Self-BLEU 是否在同等精度下更低。

**预期失败模式**：(a) 若候选池 $M_{\mathrm{explore}}$ 设得过大，等价于无约束扰动，精度在同等 Self-BLEU 下低于温度采样；(b) 若省略 R3，被探索专家在训练时不再激活，探索收益消失甚至训练不稳；(c) 若锚定专家数 $K_{\mathrm{anchored}}$ 过小，可靠路径被破坏，rollout 质量下降。建议对 $K_{\mathrm{anchored}}$、$M_{\mathrm{explore}}$、$\sigma_{\min}/\sigma_{\max}$ 各做单变量扫描，先确认消融结论可复现再谈迁移。

## 术语与记号

ESRL 在 rollout 阶段对 MoE 路由器 logits 注入噪声，使同一前缀可激活替代专家路径，从而把探索从 token 空间扩展到稀疏计算路径空间。核心控制手段有三：熵自适应噪声强度、锚定专家采样、Rollout Routing Replay。

| 术语 | 含义 |
| --- | --- |
| MoE | 混合专家模型，每 token 仅激活稀疏专家子集参与计算 |
| Top-K routing | 按路由器 logit 取前 $K$ 个专家的确定性路由 |
| Router logits | 路由器对每个专家输出的未归一化打分 |
| Router entropy | 路由分布的归一化熵，衡量路由置信度 |
| Anchored expert sampling | 锚定专家采样，保留高置信专家、仅在候选池内随机探索其余专家 |
| Rollout Routing Replay (R3) | 回放 rollout 时记录的专家路径，使训练与生成路由一致 |
| GRPO | 组相对策略优化，用组内相对优势做策略梯度的 RL 算法 |
| Self-BLEU | 同一提示多个回复间的相似度指标，越低表示多样性越高 |
| Pass@1 / Pass@8 | 单次采样正确率与 8 次采样中至少一次正确的估计值 |
| Advantage-informative group | 组内奖励存在差异、能提供有效优势信号的 rollout 组 |

关键符号：$l_{t,\ell,e}$ 为 token $t$、层 $\ell$、专家 $e$ 的原始路由器 logit；$p_{t,\ell,e}$ 为对全部路由专家归一化后的路由概率；$\mathcal{H}_{t,\ell}\in[0,1]$ 为归一化路由器熵；$\sigma_{t,\ell}$ 为自适应噪声尺度，由 $\sigma_{t,\ell}=\sigma_{\min}+(\sigma_{\max}-\sigma_{\min})(1-\mathcal{H}_{t,\ell})$ 插值得到（路由越尖锐、熵越低，噪声越大）。$K$ 为每 token 每层激活的专家数，拆为 $K_{\mathrm{anchored}}$ 与 $K_{\mathrm{explore}}$，二者之和为 $K$；$M_{\mathrm{explore}}$ 为探索候选池大小。$\mathcal{S}^{\mathrm{roll}}_{t,\ell}$ 与 $\mathcal{S}^{\mathrm{train}}_{t,\ell}$ 分别为 rollout 与训练时实际激活的专家集合；$\mathcal{Z}^{i}$ 为第 $i$ 条轨迹完整的稀疏计算路径记录；$\rho_{t}^{i}(\theta)$ 为 token 级策略比率，即当前策略与 rollout 策略之比。注意：扰动 logits 仅用于确定激活哪些专家，聚合权重仍由原始 logits 计算，以保持相对置信度不变。

## 自测

以下问题用于检验读者是否真正掌握了 ESRL 的机制与其证据边界。答案折叠，建议先自行作答。

**Q1.** ESRL 在 rollout 阶段对路由器 logits 注入噪声，但论文强调「扰动后的 logits 只用于决定激活哪些专家」。那么被选中专家的聚合权重由什么计算？这样设计想保住什么性质？

<details><summary>答案</summary>
聚合权重仍由原始 logits 计算（式 10：$\alpha^{\mathrm{roll}}_{t,\ell,e}=\exp(l_{t,\ell,e})/\sum_{j\in\mathcal{S}^{\mathrm{roll}}_{t,\ell}}\exp(l_{t,\ell,j})$）。这样改变的是离散计算路径，而保留原始路由器对已选专家的相对置信度，避免噪声同时污染权重、破坏输出质量。
</details>

**Q2.** 自适应噪声尺度 $\sigma_{t,\ell}$ 与归一化路由熵 $\mathcal{H}_{t,\ell}$ 是正相关还是负相关？为什么方向是这样？

<details><summary>答案</summary>
负相关。$\sigma_{t,\ell}=\sigma_{\min}+(\sigma_{\max}-\sigma_{\min})(1-\mathcal{H}_{t,\ell})$。路由分布越尖锐（熵越低、越自信），需要更大扰动才能改变被选专家；分布已弥散时则减小扰动，避免不必要地破坏专家选择。
</details>

**Q3.**（跨小节）论文在 §2.3 观察到「无约束路由扰动在同等 Self-BLEU 下精度常低于温度采样」，而 §3.3 又引入锚定专家与候选池。请说明这两个设计之间的因果链条，并指出 §2.3 的观察在方法中对应哪个组件。

<details><summary>答案</summary>
§2.3 表明直接扰动会激活不匹配专家、损害 rollout 质量，因此需要「受控」探索。§3.3 的锚定专家采样保留 Top-$K_{\mathrm{anchored}}$ 高置信路径，仅在 logits 最高的 $M_{\mathrm{explore}}$ 个非锚定专家构成的候选池内加噪取 Top-$K_{\mathrm{explore}}$，把随机性限制在「合理替代」范围内。消融也支持这一点：锚定专家防止可靠路径被过度破坏。
</details>

**Q4.**（跨小节）为什么仅有 rollout 阶段的扰动还不够，必须配合 Rollout Routing Replay（R3）？如果不做 replay，被探索到的专家会怎样？

<details><summary>答案</summary>
若训练时重新执行确定性 Top-$K$，同一 token 的专家集合可能与 rollout 时不同，被探索的替代专家不再被激活、拿不到梯度，探索效果被抹掉；同时 rollout 策略 $\pi_{\mathrm{roll}}$ 与当前策略 $\pi_\theta$ 的路由不一致会放大重要性采样比率的波动。R3 记录每条轨迹各 token 各层的专家集合 $\mathcal{Z}^i$，优化时绕过 Top-$K$、固定复用该集合，仅用当前 logits 重算门控权重，使被探索专家获得梯度并降低路由不匹配。
</details>

**Q5.**（跨小节）证据表把 C3/C4 标为「作者主张」。请指出支持 C3 与 C4 的具体数字来源，并说明这些结论在迁移到你自己场景前需要注意什么。

<details><summary>答案</summary>
C3 来自 §4.2 表 1：Qwen3-30B-A3B 上 ESRL 平均 Pass@1 42.1、Pass@8 64.2，较 GRPO 提升 3.2/4.5 个百分点；C4 来自 §4.3 表 2：平均 Pass@1 由 53.2 升至 55.9、Pass@8 由 64.9 升至 77.0。注意：这些均为作者报告的单篇结果，证据表中无独立复现记录，故标注为「作者主张」而非共识。迁移时需注意：(1) 增益集中在 Pass@8（覆盖度）而非 Pass@1，若你的场景只关心单样本精度，收益可能有限；(2) 结果依赖具体 MoE 结构（top-$K$、top-1、shared-expert 均被测，但均为特定模型）；(3) 评测时路由扰动被禁用（附录 A），即收益体现在训练后的策略而非推理期扰动；(4) 方法不改奖励与损失，理论上可与 reward/loss 层改进叠加，但论文未给出叠加实验。
</details>
