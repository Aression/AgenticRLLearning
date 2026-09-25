---
id: compo-zeroth-order-alignment
title: ComPO：基于比较oracle的零阶偏好对齐
summary: 直接对齐方法（如DPO）在偏好对相似（低边距/噪声对）时会出现似然位移：偏好回答的相对似然上升但绝对概率下降，甚至把概率质量移向不安全回答，并伴随冗长问题。已有做法是过滤噪声对或加正则，但过滤会丢弃其中仍可能存在的比较信息。
stage: FRONTIER
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 30
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.19144
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.19144
objectives: [理解直接对齐方法（如DPO）在噪声偏好对下的似然位移问题及其危害, 掌握ComPO如何把偏好对当作比较oracle、用零阶符号信号估计更新方向, 了解ComPO在离线与在线设置下的实验结果与阻尼、重采样等设计选择, 认识在线反向KL约束的可行性与覆盖假设等理论边界]
tags: [preference-alignment, zeroth-order-optimization, dpo, likelihood-displacement, online-alignment]
sources: [a-zeroth-order-paradigm-for-llm-preferen]
related: [preferences, grpo, value-flattening-ppo]
prerequisites: []
---
## 问题与语境

直接对齐方法（DPO 及其变体）用偏好对上的 margin 型损失替代 RLHF 的多阶段流程，简单稳定，但存在**似然位移**（likelihood displacement）：训练提高了偏好回答 $\mathbf{y}^{+}$ 相对非偏好回答 $\mathbf{y}^{-}$ 的似然，却降低了 $\mathbf{y}^{+}$ 的绝对概率，甚至把概率质量移向语义相反的（如不安全）回答。论文给出的例子是：训练模型偏好 "No" 而非 "Never" 可能反而抬高 "Yes" 的似然；当提示要求为恐怖组织渗透政府机构提供步骤时，Gemma-2B-it 原本给出拒绝回答，DPO 训练后可能因概率质量离开拒绝回答而顺从该不安全请求（引自 Razin et al. 2025, Table 18）。与之相关的还有冗长（verbosity）问题：RLHF 或直接对齐方法微调后的模型倾向生成更长回答而质量未相应提升。

已有诊断把似然位移与**噪声偏好对**联系起来——即偏好与非偏好回答在模型相关度量下相似、边距很小的对。已有做法分两类：加正则（Pal et al. 2024；Rafailov et al. 2024b），或用 CHES 分数识别并**过滤**问题对（Razin et al. 2025），后者被经验证明比加 SFT 正则更有效。但过滤的代价是把这些对完全移出训练，而它们仍可能含有可用的比较信息。

论文的定位正在于此：它不追求显式定义一个可优化的对齐目标函数（作者称这"exceptionally challenging"），而是把偏好对当作**比较 oracle**——只问"对当前策略做一个小扰动，是否同时提高 $\mathbf{y}^{+}$ 似然、降低 $\mathbf{y}^{-}$ 似然"，用一比特符号信号聚合出更新方向。噪声对因此从"不适合 margin 损失的样本"变成"关于潜在对齐目标的比较信号"，与干净对上的常规直接对齐优化互补。这一视角把零阶优化与比较 oracle 引入 LLM 偏好对齐，并进一步扩展到在线设定。

## 核心主张

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | ComPO 作为 DPO 的增强，在多个模型与基准上提升长度控制胜率等指标 | §4.1 表 1（Mistral-7B-Instruct AlpacaEval 2 LC 23.89→26.17；Llama-3-8B-Instruct 32.92→35.79） | 作者主张 |
| C2 | ComPO 训练中偏好回答对数似然不降、非偏好回答对数似然不升 | §4.2 表 2（Llama-3-Instruct-8B 与 Gemma-2-9B-it 三次独立试验，$\gamma\in\{0.1,1\}$） | 作者主张 |
| C3 | 在线阻尼与重采样在离线 ComPO 基础上进一步提升 AlpacaEval 2 与 Arena-Hard 指标 | §4.3 表 10（Qwen3-4B-Base、Llama-3.2-3B-Instruct、Gemma-3-4B-it） | 作者主张 |
| C4 | 基本在线方案在反向 KL 邻域内保持可行，且策略性能可由分布内成对误差界定 | §3.2 式 (11)(12) 与定理 3.4；附录 B.3 证明 | 作者主张 |

**最强的是 C1**：它是唯一有跨四个模型配置、三个基准（AlpacaEval 2、Arena-Hard、MT-Bench）点估计支撑的主张，且增益方向一致。但需注意其内部并不整齐——Mistral-7B-Instruct 的 Arena-Hard WR 从 DPO_clean 的 14.2 降到 10.5，Llama-3-8B-Base 的 Arena-Hard WR 12.0→12.1 基本持平，说明"全面提升"只在 AlpacaEval 2 LC 上成立。此外表 1 报告的是单次运行的点估计，论文自述"main tables report point estimates from the reported runs"，无方差信息，因此 C1 目前只能算作者主张而非已复现。

**最弱的是 C4**：定理 3.4 的可行性与性能界针对的是 Algorithm 3 的基本方案，而论文明确承认实际在线实现"is a heuristic approximation to the basic scheme... it does not evaluate the proposed next policy or enforce the hard sequence-level reverse-KL constraint analyzed in Theorem 3.4"。也就是说，理论保证与表 10 的经验结果之间没有直接对应关系；且"Coverage remains a separate assumption and is not implied by the KL constraint"，界本身依赖一个未被 KL 约束蕴含的额外假设。C2 的强度居中：表 2 的单调性在报告的三次试验内成立，但样本量小（两个模型 × 两个 $\gamma$ × 三次），且作者只声称"across the reported trials"，未给出跨更多模型或更大规模的验证。

## 机制与方法

ComPO 的出发点是把偏好对视为**比较 oracle**（只能得到一比特比较结果，无法获得函数值或梯度），而不是固定损失函数的样本。核心符号：策略 $\pi_\theta$、SFT 参考策略 $\pi_{\text{ref}}$、偏好数据集 $D=\{(\mathbf{x},\mathbf{y}^{+},\mathbf{y}^{-})\}$，其中 $\mathbf{y}^{+}/\mathbf{y}^{-}$ 为偏好/非偏好回答。

**离线方案。** 先用边距阈值 $\delta_{\text{margin}}=3$ 把 $D$ 分为干净对与噪声对。干净对仍用 DPO/SimPO 等直接对齐损失做常规优化；噪声对只提供比较方向。对非空子集 $S\subseteq D$，定义扰动前后平均对数似然差：

$$\Delta^{+}_{S}(\theta,\theta^{\prime})=\tfrac{1}{|S|}\sum_{(\mathbf{x},\mathbf{y}^{+},\mathbf{y}^{-})\in S}\left(\log\pi_{\theta^{\prime}}(\mathbf{y}^{+}|\mathbf{x})-\log\pi_{\theta}(\mathbf{y}^{+}|\mathbf{x})\right),\quad \Delta^{-}_{S}\ \text{同理对}\ \mathbf{y}^{-}$$

比较 oracle $\mathcal{C}_{\pi}^{S}$ 判断候选 $\theta+r\mathbf{z}_i$ 是否同时提高 $\mathbf{y}^{+}$ 似然、降低 $\mathbf{y}^{-}$ 似然，返回符号信号 $y_i$。聚合 $m$ 个随机方向 $\{\mathbf{z}_i\}$ 的符号信号估计归一化更新方向 $\hat{\mathbf{g}}_t$，再按步长 $\eta$ 更新 $\theta_{t+1}=\theta_t-\eta\hat{\mathbf{g}}_t$。关键设计取舍：**不显式定义对齐目标函数**，只用「更好的策略应给 $\mathbf{y}^{+}$ 更高、$\mathbf{y}^{-}$ 更低的似然」这一局部比较信息，从而让低边距对在不被直接优化 margin 损失的前提下仍贡献信号——这正是与 Razin et al. (2025) 过滤噪声对做法的差异。

**在线扩展。** 保留离线比较方向，用当前策略的无标注生成估计序列级反向 KL：

$$D_{\text{RKL}}(\pi\|\pi_{\text{ref}})=\mathbb{E}_{\mathbf{x}\sim P_{\text{on}},\mathbf{y}\sim\pi(\cdot|\mathbf{x})}\left[\log\tfrac{\pi(\mathbf{y}|\mathbf{x})}{\pi_{\text{ref}}(\mathbf{y}|\mathbf{x})}\right]$$

并定义反向 KL 邻域 $\Pi_{\tau}=\{\pi:D_{\text{RKL}}(\pi\|\pi_{\text{ref}})\leq\tau\}$。基本方案对候选 $\tilde{\theta}_{t+1}=\theta_t-\eta\hat{\mathbf{g}}_t$ 做可行性检查：若 $\tilde{D}_t=D_{\text{RKL}}(\pi_{\tilde{\theta}_{t+1}}\|\pi_{\text{ref}})\leq\tau$ 则接受，否则保持原策略，从而由归纳保持可行性。实用实现（Algorithm 4）是启发式近似：用长度归一化统计量做软阻尼调整步长，并加入窗口长度 $n=50$ 的重放缓冲。

**适用前提与不确定处。** 作者明确指出：在线实现**不评估候选下一策略、也不强制 Theorem 3.4 分析的硬序列级反向 KL 约束**；覆盖性（coverage）是独立假设，**不由 KL 约束蕴含**。离线分析依赖平滑性、梯度稀疏性与 oracle 相容性假设（Theorem 3.2）。此外，作者强调 ComPO 并非专为控制冗长设计，更高的 LC 胜率应解读为「按长度调整后的评判表现提升」，而非回答更短的直接证据。

## 实验设置

实验分两组：离线方案（作为 DPO 及其变体的增强，从噪声对提取方向）与在线方案（用当前策略无标注生成做反向 KL 代理阻尼）。离线实验统一使用 UltraFeedback 数据集，初始化自 Meng et al. (2024) 所用的 SFT Base/Instruct 模型；超参按模型族设定：Mistral-7B 用 $r=0.0005$、$m=1600$、$\lambda_g=0.00022$、$\lambda=0.2$；Llama-3-8B 与 Gemma-2-9B-it 用 $r=0.00075$、$m=1800$、$\lambda_g=0.00008$、$\lambda=0.2$。在线实验：Qwen3-4B-Base 用 $r=0.0008$、$m=1800$、$\lambda_g=0.000085$；Gemma-3-4B-it 用 $r=0.00045$、$m=1800$、$\lambda_g=0.000075$；重放缓冲窗口 $n=50$。评测协议沿用 Meng et al. (2024)：AlpacaEval 2-v0.6.6（GPT-4 Turbo 作基线与裁判，报 WR 与 LC）、Arena-Hard（基线 GPT-4-0314，裁判 GPT-4 Turbo，报 WR）、MT-Bench（GPT-4 十分制，报 Turn-1/Turn-2/Avg.）。在线组使用 AlpacaEval 2 与 Arena-Hard 的 GPT-4.1 配置。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| AlpacaEval 2, Arena-Hard, MT-Bench | Mistral-7B-Base, Mistral-7B-Instruct, Llama-3-8B-Base, Llama-3-8B-Instruct | PA, DPO, DPO_clean | 30 NVIDIA A40 GPUs, each with 46 GB of memory | LC (%), WR (%), Turn-1, Turn-2, Avg. |
| AlpacaEval 2, Arena-Hard (GPT-4.1 配置) | Qwen3-4B-Base, Llama-3.2-3B-Instruct, Gemma-3-4B-it | PA, DPO, DPO+ComPO (offline) | 未说明 | LC (%), WR (%) |

需注意：主表报告的是所报告运行的点估计，消融表才显式报告重复运行间的波动；表 2 的成对对数似然为三次独立试验（$\gamma\in\{0.1,1\}$，其余超参取默认值）。上述设置与结果均为**作者主张**，本档案未包含独立复现证据。

## 证据与结果

以下数字均直接取自全文摘录中的 Table 1、Table 2、Table 10，未做换算或推断。

离线增强（Table 1，UltraFeedback，30×A40 46GB）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| AlpacaEval 2 LC (%) | 7.33 / 9.71 / 9.41 / 11.66 | Mistral-7B-Base：PA / DPO / DPO_clean / DPO_clean+ComPO | Table 1 |
| AlpacaEval 2 LC (%) | 16.54 / 24.14 / 23.89 / 26.17 | Mistral-7B-Instruct 同上四档 | Table 1 |
| AlpacaEval 2 LC (%) | 3.21 / 4.14 / 4.28 / 5.39 | Llama-3-8B-Base 同上四档 | Table 1 |
| AlpacaEval 2 LC (%) | 24.06 / 32.59 / 32.92 / 35.79 | Llama-3-8B-Instruct 同上四档 | Table 1 |
| Arena-Hard WR (%) | 1.1 / 2.9 / 3.0 / 3.2 | Mistral-7B-Base 同上四档 | Table 1 |
| Arena-Hard WR (%) | 10.9 / 14.4 / 14.2 / 10.5 | Mistral-7B-Instruct 同上四档 | Table 1 |
| Arena-Hard WR (%) | 4.1 / 12.1 / 12.0 / 12.1 | Llama-3-8B-Base 同上四档 | Table 1 |
| Arena-Hard WR (%) | 20.8 / 22.9 / 22.9 / 23.1 | Llama-3-8B-Instruct 同上四档 | Table 1 |
| MT-Bench Avg. | 5.57 / 5.79 / 5.70 / 5.77 | Mistral-7B-Base 同上四档 | Table 1 |
| MT-Bench Avg. | 5.65 / 5.86 / 5.73 / 7.69 | Mistral-7B-Instruct 同上四档 | Table 1 |
| MT-Bench Avg. | 6.10 / 6.23 / 6.33 / 6.44 | Llama-3-8B-Base 同上四档 | Table 1 |
| MT-Bench Avg. | 7.90 / 7.93 / 7.94 / 8.05 | Llama-3-8B-Instruct 同上四档 | Table 1 |

在线扩展（Table 10，GPT-4.1 配置）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| AlpacaEval 2 LC (%) | 12.70 / 15.28 / 16.20 / 17.43 / 18.57 | Qwen3-4B-Base：PA / DPO / DPO+ComPO / +online+RKL / +resampling | Table 10 |
| Arena-Hard WR (%) | 16.2 / 29.3 / 30.8 / 31.4 / 32.6 | Qwen3-4B-Base 同上五档 | Table 10 |
| AlpacaEval 2 LC (%) | 11.16 / 11.72 / 12.35 / 12.70 / 13.05 | Llama-3.2-3B-Instruct 同上五档 | Table 10 |
| Arena-Hard WR (%) | 9.8 / 11.6 / 11.9 / 12.4 / 12.8 | Llama-3.2-3B-Instruct 同上五档 | Table 10 |
| AlpacaEval 2 LC (%) | 34.54 / 38.30 / 40.00 / 42.07 / 42.55 | Gemma-3-4B-it 同上五档 | Table 10 |
| Arena-Hard WR (%) | 54.8 / 56.9 / 57.7 / 63.3 / 63.7 | Gemma-3-4B-it 同上五档 | Table 10 |

消融与对照。离线侧：DPO_clean 相对 DPO 在多数格上并未提升（如 Mistral-7B-Instruct LC 23.89 vs 24.14；Arena-Hard 14.2 vs 14.4），说明增益主要来自 ComPO 而非过滤本身；但 Mistral-7B-Instruct 的 Arena-Hard 由 14.2 降至 10.5，是摘录中唯一明显反向的格。在线侧：阻尼相对离线 ComPO 提升 AlpacaEval 2 LC / WR / Arena-Hard WR 分别为 Qwen3-4B-Base 1.23 / 1.47 / 0.6 个百分点，Llama-3.2-3B-Instruct 0.35 / 0.73 / 0.5，Gemma-3-4B-it 2.07 / 1.83 / 5.6；加入 replay 后三个指标在每个模型上均进一步提升。似然诊断（Table 2）：Llama-3-Instruct-8B 初始 $(-46.761,-47.410)$，$\gamma=1$ 三次试验为 $(-46.728,-47.520)$、$(-46.743,-47.525)$、$(-46.753,-47.517)$；Gemma-2-9B-it 初始 $(-133.122,-134.557)$，$\gamma=1$ 为 $(-133.059,-134.562)$、$(-133.122,-134.564)$、$(-133.112,-134.565)$。超参：$\delta_{\text{margin}}=3$，Mistral $r=0.0005,m=1600,\lambda_g=0.00022,\lambda=0.2$；Llama-3-8B 与 Gemma-2-9B-it $r=0.00075,m=1800,\lambda_g=0.00008,\lambda=0.2$；Qwen3-4B-Base $r=0.0008,m=1800,\lambda_g=0.000085$；Gemma-3-4B-it $r=0.00045,m=1800,\lambda_g=0.000075$；replay 窗口 $n=50$。摘录未给出 Table 1/10 的方差、置信区间或多次运行统计（Table 2 除外）。

## 证据强度评估

证据分级：B（中等偏弱）。理由：结论有跨 7 个模型、3 个基准的一致方向性支持，且提供了机制层面的似然诊断（Table 2 三次独立试验），但主表（Table 1、Table 10）为单次运行的点估计，无方差或显著性检验；在线部分作者自述为启发式近似，理论保证（定理 3.4）并不覆盖实际实现。因此属于「方向可信、幅度不可信」的证据。

主要威胁：

1. 构造效度（理论与实现脱节）。作者明确写道在线实现「is a heuristic approximation to the basic scheme in Algorithm 3. Indeed, it does not evaluate the proposed next policy or enforce the hard sequence-level reverse-KL constraint analyzed in Theorem 3.4」，且「Coverage remains a separate assumption and is not implied by the KL constraint」。这意味着 C4 的可行性/性能界不能用来解释 Table 10 的增益，在线提升的机制归因是开放的。

2. 统计显著性与基线选择。Table 1/10 只报告点估计，摘录未给出重复次数、方差或显著性；而多处增益幅度很小（如 Llama-3-8B-Base Arena-Hard 12.0→12.1；Llama-3-8B-Instruct Arena-Hard 22.9→23.1；Llama-3.2-3B-Instruct LC 12.35→12.70），在无方差信息时无法判断是否超出噪声。此外 DPO_clean 这一基线在部分格上低于 DPO，说明基线本身波动不小。

3. 外部效度与评测污染。评测依赖 GPT-4 Turbo / GPT-4.1 作为评判者，AlpacaEval 2 与 Arena-Hard 均为 LLM-as-judge 范式，存在对特定风格（含长度）的系统性偏好；作者也提示 LC 只应解读为「按长度调整后的评判表现」，而非回答更短的证据。MT-Bench 上 Mistral-7B-Instruct 的 5.73→7.69 跳幅异常大，与其余三档（5.65/5.86/5.73）不成比例，摘录未给出解释，需谨慎对待。

4. 结论范围受限。作者自述示例「illustrate response presentation rather than systematic improvements in safety, factual accuracy, or mathematical ability」，且「Additional detail does not by itself establish factual correctness」。因此 C1/C3 只能支持「在测试配置下评判胜率提升」，不能外推为安全性、事实性或推理能力的改善；C2 的似然单调性也仅在 Table 2 报告的两个模型、三次试验范围内成立。

## 边界与反例

**会推翻结论的观察。** 若在相同设置下重复 Table 1 / Table 10 的训练，出现「偏好回答对数似然下降」或「非偏好回答对数似然上升」的稳定反例，则 C2 及其支撑的机制解释（噪声对作为比较信号可缓解似然位移）即被推翻。作者自己在 Table 2 中只报告了「Across the reported trials, the preferred-response log-likelihood is nondecreasing and the dispreferred-response log-likelihood is nonincreasing」，且明确限定为「the reported trials」——即两个模型、$\gamma\in\{0.1,1\}$、各三次试验。样本量小，且 Gemma-2-9B-it 在 $\gamma=0.1$ 时三次试验的 $y^+$ 值几乎不动（$-133.122,-133.122,-133.121$），这更像「未发生位移」而非「被纠正」，读者不应把它读成强证据。

**最可能失效的条件。** 其一，噪声对的定义依赖 $\delta_{\text{margin}}=3$ 这一固定阈值；若换数据集或换模型使干净/噪声划分改变，比较信号的方向可能不再与真实偏好一致。其二，在线部分作者自陈「The implementation is a heuristic approximation to the basic scheme in Algorithm 3. Indeed, it does not evaluate the proposed next policy or enforce the hard sequence-level reverse-KL constraint analyzed in Theorem 3.4」，因此 C4 的可行性与性能界并不覆盖实际跑的 Algorithm 4，Table 10 的提升不能用来支持定理 3.4。其三，作者指出「Coverage remains a separate assumption and is not implied by the KL constraint」，故在覆盖假设不成立（参考策略邻域外密度比无界）的场景，性能界失效。

**易被误推的方向。** 作者明确声明「Although ComPO is not specifically designed to control verbosity, we evaluate its length-controlled (LC) win rates... rather than direct evidence of shorter responses」，因此不能由 LC 提升推断回答变短。同理，Arena-Hard WR 在 Mistral-7B-Instruct 上从 DPO_clean 的 14.2 降到 10.5，说明提升并非在所有基准上一致；MT-Bench 上 Mistral-7B-Base 的 DPO_clean+ComPO（5.77）也低于 DPO（5.79）。此外作者提示「These examples illustrate response presentation rather than systematic improvements in safety, factual accuracy, or mathematical ability」，故不应外推到安全性或事实性。

## 与知识库的关系

**与「DPO 与直接对齐方法」的关系（新增）。** 既有笔记把 DPO 视为在偏好对上最小化对比损失 $\mathcal{L}_{\text{DPO}}$，其目标是相对似然边距。ComPO 新增的是一条正交路径：对噪声对不再优化固定损失，而是「perturbs the current policy, evaluates whether each perturbation increases the likelihood of preferred responses and decreases that of dispreferred responses, and aggregates the resulting one-bit signals to estimate a normalized update direction」。即把偏好对从「损失样本」改写为「比较 oracle 查询」。可链接笔记：`alignment/dpo-basics`、`alignment/direct-alignment-overview`。

**与「似然位移与噪声偏好对」的关系（印证 + 张力）。** 印证：ComPO 复述了 Razin et al. (2025) 的发现——「filtering out preference pairs identified by the CHES score as problematic can be more effective for mitigating likelihood displacement than adding supervised fine-tuning (SFT) regularization」，并给出与之一致的 pair-level 诊断。张力：Razin 的做法是**过滤**噪声对，ComPO 主张「filtering noisy pairs also removes them from training entirely, even though these pairs may still contain useful comparative information」，即保留并改用途。两者在「噪声对有害」上一致，在「是否丢弃」上分歧。可链接笔记：`alignment/likelihood-displacement`、`alignment/noisy-preference-pairs`、`alignment/ches-score`。

**与「零阶优化」的关系（新增）。** 既有零阶笔记多关注函数值查询；ComPO 新增的是把**比较 oracle**（一比特符号）用于 LLM 偏好对齐，并在附录 B.1 中借用 one-bit estimation 框架（Plan and Vershynin, 2012; Cai et al., 2022a）给出收敛分析。可链接笔记：`optimization/zeroth-order`、`optimization/one-bit-estimation`。

**与「在线对齐与反向 KL 正则」的关系（新增 + 需标注不确定）。** 新增：用当前策略的无标注生成估计反向 KL，并以接受/拒绝规则把策略限制在 $\Pi_\tau$ 内。但需注意作者自陈实用实现是启发式近似，未执行硬约束，故与知识库中「反向 KL 约束可保证可行性」的结论之间存在**未闭合的间隙**，迁移时应视为待验证。可链接笔记：`alignment/online-alignment`、`alignment/reverse-kl-regularization`、`theory/coverage-assumption`。

## 复现与验证计划

目标：以最小成本验证两条核心可检验主张——(i) 在干净对 DPO 之上叠加 ComPO 能提升长度控制胜率（C1）；(ii) ComPO 训练中偏好回答对数似然不降、非偏好回答对数似然不升（C2）。C3（在线阻尼/重采样）与 C4（定理 3.4 的可行性界）优先级较低，前者依赖启发式实现，后者为纯理论。

环境与数据：UltraFeedback（HuggingFaceH4/ultrafeedback_binarized）作为离线偏好数据；用边距阈值 $\delta_{\text{margin}}=3$ 划分干净对与噪声对。初始化自 SFT 后的 Base/Instruct 检查点（如 Mistral-7B 系列、Llama-3-8B 系列）。评测用 AlpacaEval 2-v0.6.6（GPT-4 Turbo 作基线与裁判，报 LC 与 WR）、Arena-Hard（基线 GPT-4-0314）、MT-Bench（GPT-4 打分，报 Turn-1/Turn-2/Avg.）。

超参：Mistral-7B 用 $r=0.0005$、$m=1600$、$\lambda_g=0.00022$、$\lambda=0.2$；Llama-3-8B 与 Gemma-2-9B-it 用 $r=0.00075$、$m=1800$、$\lambda_g=0.00008$、$\lambda=0.2$。作者报告全部 ComPO 运行使用 30 张 NVIDIA A40（每张 46 GB 显存）——这是完整复现的预算量级，最小验证应据此缩减模型规模或方向数 $m$，并显式记录缩减带来的偏差。

基线与判据：基线为 PA、DPO、DPO_clean。判据一：DPO_clean+ComPO 相对 DPO_clean 在 AlpacaEval 2 LC 上提升（作者报告 Mistral-7B-Instruct 23.89→26.17，Llama-3-8B-Instruct 32.92→35.79）。判据二：三次独立试验（独立采样扰动 $\{z_i\}$）中 $\log\pi_\theta(y^+|x)$ 不降、$\log\pi_\theta(y^-|x)$ 不升（表 2，$\gamma\in\{0.1,1\}$）。

预期失败模式：Arena-Hard WR 未必同向提升——表 1 中 Mistral-7B-Instruct 的 Arena-Hard WR 由 DPO_clean 的 14.2 降至 10.5，说明该指标对 ComPO 不稳健；MT-Bench 亦非单调（Mistral-7B-Base 5.70→5.77 微增，但 Mistral-7B-Instruct 由 5.73 跳至 7.69，量级异常，需警惕评测噪声或配置差异）。此外 LC 提升不等于回答更短，作者明确不作此解读。以上均为作者主张，尚无独立复现记录。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| $\pi_\theta$ | 参数为 $\theta$ 的语言模型策略，给出回答的条件概率 |
| $\pi_{\text{ref}}$ | SFT 后的参考策略 |
| $D$ | 成对偏好数据集，样本为 $(x,y^+,y^-)$ |
| $y^+ / y^-$ | 偏好回答 / 非偏好回答 |
| $\Delta^+_S,\Delta^-_S$ | 集合 $S$ 上扰动前后偏好/非偏好回答的平均对数似然差（式 8） |
| $\mathcal{C}_\pi^S$ | 基于集合 $S$ 的偏好比较 oracle，返回一比特比较结果 |
| $z_i$ | 第 $i$ 个随机扰动方向 |
| $m$ | 每次更新采样的扰动方向数 |
| $r$ | 扰动幅度（步长尺度） |
| $\eta$ | 参数更新步长 |
| $\delta_{\text{margin}}$ | 区分干净对与噪声对的边距阈值，实验取 3 |
| $D_{\text{RKL}}$ | 序列级反向 KL 散度（式 3） |
| $\Pi_\tau$ | 反向 KL 不超过 $\tau$ 的参考策略邻域（式 4） |
| $\tau$ | 反向 KL 半径 |
| $\gamma$ | 表 2 中比较的扰动尺度，取值 0.1 或 1 |
| $n$ | 在线重放缓冲窗口长度，实验取 50 |
| $\lambda_g,\lambda$ | ComPO 训练超参（见 §4.1 取值） |
| likelihood displacement | 似然位移：偏好回答相对似然上升但绝对概率下降，概率质量可能移向不安全回答 |
| noisy preference pair | 噪声偏好对：模型相关度量下偏好与非偏好回答相似、边距很小的偏好对 |
| comparison oracle | 比较 oracle：只能获得两点函数值比较结果（一比特）的查询接口 |
| zeroth-order method | 零阶方法：仅用函数值或比较信息、不用显式梯度的优化方法 |
| direct preference alignment | 直接偏好对齐：直接用偏好对优化策略、不单独训练奖励模型（如 DPO） |
| reverse KL | 反向 KL：从当前策略采样估计的 KL 散度，用于约束策略不偏离参考策略 |
| local coverage | 局部覆盖：参考策略邻域内策略间密度比有界的假设 |
| length-controlled win rate (LC) | 长度控制胜率：按回答长度调整后的胜率，不直接说明回答更短 |
| CHES score | 中心化隐藏嵌入相似度：用隐藏表示相似度衡量偏好与非偏好回答接近程度 |
| PA | pre-alignment，DPO 训练前的监督/指令微调检查点 |

## 自测

以下问题用于检验读者是否真正掌握了 ComPO 的机制、证据强度与适用边界。答案折叠，建议先自行作答。

**Q1（机制）** ComPO 把噪声偏好对当作「比较 oracle」而非固定损失的样本。请写出这一替换在更新方向上的具体差别：DPO 用式(1)的什么量做梯度信号，ComPO 用式(8)的什么量、经过什么聚合得到更新方向？

<details><summary>答案</summary>
DPO 用 $\log\frac{\pi_\theta(\mathbf{y}^+|\mathbf{x})}{\pi_{\text{ref}}(\mathbf{y}^+|\mathbf{x})}-\log\frac{\pi_\theta(\mathbf{y}^-|\mathbf{x})}{\pi_{\text{ref}}(\mathbf{y}^-|\mathbf{x})}$ 的 sigmoid 对比损失的梯度（即似然边距的梯度）。ComPO 则在当前 $\theta$ 处采样 $m$ 个随机方向 $\mathbf{z}_i$，用式(8)的 $\Delta^+_S,\Delta^-_S$（扰动前后偏好/非偏好回答的平均对数似然差）构造比较 oracle $\mathcal{C}_\pi^S$，得到一比特符号信号 $y_i$，聚合后估计归一化更新方向 $\hat{\mathbf{g}}_t$，再按 $\theta_{t+1}=\theta_t-\eta\hat{\mathbf{g}}_t$ 更新。关键差别：不要求噪声对上的损失可微可优化，只要求它能对「附近策略是否更好」投一票。
</details>

**Q2（证据强度）** 表2 声称「偏好回答对数似然不降、非偏好回答对数似然不升」。请对照证据表中 Llama-3-Instruct-8B 与 Gemma-2-9B-it 的数值，说明这一说法在报告的三次试验里是否严格成立，并指出该证据能支持什么、不能支持什么。

<details><summary>答案</summary>
在报告数值内成立：Llama-3-Instruct-8B 初始 $(-46.761,-47.410)$，$\gamma=0.1$ 三次为 $(-46.744,-47.411)$、$(-46.760,-47.411)$、$(-46.759,-47.410)$，$\gamma=1$ 为 $(-46.728,-47.520)$、$(-46.743,-47.525)$、$(-46.753,-47.517)$；Gemma-2-9B-it 初始 $(-133.122,-134.557)$，各次试验的 $\mathbf{y}^+$ 值均不低于初始、$\mathbf{y}^-$ 值均不高于初始。但注意：这是单次训练后的点估计、仅两个模型、仅三次独立扰动试验，且 $\gamma=0.1$ 时 Gemma 的 $\mathbf{y}^+$ 变化量级极小（如 $-133.122\to-133.121$）。它支持「与缓解似然位移一致的配对级诊断」，不支持「普遍保证不降」或「因果上由比较 oracle 导致」。
</details>

**Q3（跨小节：主张 vs 已复现）** 论文的 C1（离线提升）与 C3（在线阻尼/重采样提升）分别由表1与表10支撑。请指出这两组结果在「是否被独立复现」「是否与理论保证对应」上的差别，并说明为什么不能把 C3 的增益直接归因于定理3.4 的约束。

<details><summary>答案</summary>
两组均为作者主张，证据表中无独立复现记录。差别在于：C1 对应离线方案，其分析（定理3.2）针对的是零阶比较更新的收敛性；C3 对应在线实用实现，而论文明确说明该实现是 Algorithm 3 的启发式近似——「does not evaluate the proposed next policy or enforce the hard sequence-level reverse-KL constraint analyzed in Theorem 3.4」。因此表10 中 +RKL/+resampling 的增益（如 Qwen3-4B-Base AlpacaEval 2 LC 16.20→17.43→18.57）来自软阻尼与重放缓冲的经验组合，论文自己也只说「support the empirical benefit of the combined procedure in the tested configurations, without identifying a separate variance-reduction mechanism」，不能归因于定理3.4 的硬约束。
</details>

**Q4（跨小节：边界与迁移）** 若你想把 ComPO 迁移到自己的场景，论文列出了哪些必须自行承担的前提？请至少结合「coverage」「在线实现」「长度控制指标」三点说明。

<details><summary>答案</summary>
(1) Coverage：论文明确「Coverage remains a separate assumption and is not implied by the KL constraint」，即定理3.4 的性能界依赖局部覆盖假设，该假设不由反向 KL 约束保证，需自行验证。(2) 在线实现：实用版不评估候选策略、不执行硬序列级反向 KL 约束，因此理论可行性结论不自动适用于你实际跑的代码。(3) 长度控制：论文声明 ComPO 并非为控制冗长而设计，LC 胜率应理解为「按回答长度调整后的评判表现」，而非回答更短的直接证据；同时「Additional detail does not by itself establish factual correctness」，示例只说明回答呈现方式，不构成安全性、事实准确性或数学能力的系统性提升证据。
</details>

**Q5（实验设置）** 根据摘录，离线实验的数据集、干净/噪声对划分阈值、以及 Mistral-7B 与 Llama-3-8B 的超参设置分别是什么？在线实验的重放窗口长度是多少？

<details><summary>答案</summary>
数据集为 UltraFeedback（HuggingFaceH4/ultrafeedback_binarized）。用 $\delta_{\text{margin}}=3$ 区分干净对与噪声对。Mistral-7B：$r=0.0005$，$m=1600$，$\lambda_g=0.00022$，$\lambda=0.2$；Llama-3-8B 与 Gemma-2-9B-it：$r=0.00075$，$m=1800$，$\lambda_g=0.00008$，$\lambda=0.2$。在线：Qwen3-4B-Base 用 $r=0.0008$，$m=1800$，$\lambda_g=0.000085$；Gemma-3-4B-it 用 $r=0.00045$，$m=1800$，$\lambda_g=0.000075$；重放缓冲窗口长度 $n=50$。所有 ComPO 运行使用 30 张 NVIDIA A40（每张 46 GB 显存）。
</details>
