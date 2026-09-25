---
id: privileged-info-opsd-ample-math
title: 特权信息在在线自蒸馏中到底加了什么
summary: 在线自蒸馏（OPSD）中，冻结教师借助特权信息（如解答）对学生前缀打分，但“更多解答内容是否带来更多收益”尚不明确。已有研究显示无参考或错误参考也能提升，且结构化指导可能优于完整解答，因此需要把蒸馏本身的增益与参考的额外贡献分离，并考察学生训练轨迹如何改变参考的迁移效果。
stage: FRONTIER
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 38
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.20612
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.20612
objectives: [理解在线自蒸馏中特权参考信息的真实增益边界, 掌握无参考对照与答案匹配视图的消融设计, 识别训练轨迹与评估模式对蒸馏迁移的交互影响]
tags: [self-distillation, privileged-information, on-policy, reasoning, ablation, evaluation]
sources: [what-does-privileged-information-add-to]
related: [retireopd-self-retiring-opd, mintrl-off-policy-intervention, grpo]
prerequisites: []
---
## 问题与语境

在线自蒸馏（OPSD）用冻结教师对学生自己生成的前缀打分，教师额外看到学生不可见的特权信息（PI），例如一份解答。这一设置被普遍理解为「教师看得更多，学生学得更好」，但「更多解答内容是否带来更多收益」在证据上并不成立。已有工作发现：无参考或使用其他题目的错误参考也能提升（Shrestha and Tessier, 2026; Ichihara et al., 2026），而结构化指导有时优于完整解答（Zhao et al., 2026b）。这意味着「相对基座的提升」这一常用指标无法回答参考本身贡献了什么——提升可能主要来自蒸馏过程，而非参考内容。

更麻烦的是，OPSD 中教师并不输出一份待复制的解答，而是对学生的尝试给出反馈；因此参考是否有用，取决于它能否帮助教师对学生当前前缀给出有效信号。这使参考的贡献与学生的训练轨迹耦合：同一参考在不同 rollout 模式下可能产生相反迁移。论文的定位正是把这两件事拆开：构建 AMPLE-Math（5,319 题 × 6 个答案匹配视图，共享同一验证答案、仅改变推理表示），在答案信息固定的条件下比较推理表示；并以无参考对照（保留思考模式教师、去掉 PI，因此仍是跨模式自蒸馏）为基线，在 Qwen3-1.7B 与 SmolLM3-3B 两个模型家族、多个 checkpoint 上追踪参考的增量贡献，再用教师画像与匹配干预区分「监督变了」与「学生行为变了」。它不是提出新蒸馏算法，而是给 OPSD 的参考设计提供一个可控测量框架。

## 核心主张

论文的核心结论可归纳为四条，均属作者主张，尚未见独立复现。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | Qwen 中大部分提升无需参考即可获得，参考的额外贡献小且依赖视图 | §3.1 图2a、表1；Clean Solution − reference-free = +1.30[0.20,2.41]（§3.1, Table 10），Holm 校正后不显著 | 作者主张 |
| C2 | 更完整的解答不带来一致更大的增益，Full Trace 在 Qwen 外部无优势 | §3.1 表1（Full Trace 外部 Δ Avg@12 = +2.29[-0.16,4.88]）；§3.1 表5 | 作者主张 |
| C3 | 将训练 rollout 从直接回答改为思考模式，会使同一参考的迁移由增益转为损失 | §3.2 图3、表11（Qwen pooled step-50 TH−DR = -7.60[-9.31,-5.95]）、表12（SmolLM3 step-50 = -6.84[-8.50,-5.18]） | 作者主张 |
| C4 | 扩大损失覆盖的表观增益主要来自停止时间更早，而非覆盖本身 | §5 图5、表2（First-4K / Distributed-1K 在匹配 step 25 优势低于 1 点且区间含零） | 作者主张 |

最强的是 C3。它在两个模型家族、域内与外部基准、多个 checkpoint 上方向一致，且保持教师与参考不变、只改 rollout 模式，属于干净的对照；外部 pooled 差距 -9.44[-13.24,-5.83] 的区间远离零。C4 也较稳，因为「匹配 checkpoint 后优势消失」是一个可被区间直接检验的机制性解释，而非仅靠相关性。

最弱的是 C1 中「参考有额外贡献」的部分。Clean Solution 的 +1.30[0.20,2.41] 原始 p=0.024，但 Holm 校正后为 0.15，且六视图对比中仅此一项接近显著；同时 Wrong answer 对照也提升 +1.67[0.07,3.32]，说明增益并非正确参考内容所特有。C2 的「无一致优势」本身是零结果，作者也明确提示区间含零不等于等价（limits），因此只能读作「未观察到一致优势」，不能读作「完整解答无用」。

## 机制与方法

本文研究的是在线自蒸馏（OPSD）中特权信息（PI）的边际贡献。机制上，冻结教师 $\pi_{\bar{\theta}}$ 在可见特权视图 $z_v(x)$ 的条件下，对学生 $\pi_\theta$ 自己生成的响应前缀打分；学生仅见问题 $x$，在 rollout 配置 $m_S$ 下生成 $y=(y_1,\dots,y_L)$。对前缀 $s_t=(x,y_{<t})$ 与词表 token $a$，学生分布为 $p^S_t(a)=\pi_\theta(a\mid x,y_{<t};m_S)$，教师分布为 $p^T_{v,t}(a)=\pi_{\bar{\theta}}(a\mid x,z_v(x),y_{<t};m_T,\tau)$，其中 $m_T$ 为教师推理配置，$\tau$ 为打分温度。损失为教师到学生的前向 KL，逐词项上限截断 0.05：

$$\mathcal{L}_{v}(\theta;m_{S})=\mathbb{E}_{x,\,y\sim\pi_{\theta}(\cdot\mid x;m_{S})}\left[\frac{1}{|I(y)|}\sum_{t\in I(y)}D_{\mathrm{gKL}}\!\left(p^{T}_{v,t}\,\|\,p^{S}_{t}\right)\right]$$

求导时教师分布与采样完成固定。关键设计取舍在于：无参考对照保留思考模式教师、仅去掉 PI，因此它仍是跨模式自蒸馏，而非教师与学生分布相同的对照——这一点决定了「无参考也有增益」不能被解读为蒸馏无效。

为在答案信息固定下比较推理表示，作者构建 AMPLE-Math：5,319 题各配六个答案匹配视图（Answer Only、Gist、Key Points、Clean Solution、Summary、Full Trace），共享同一验证答案，仅改变推理表示，渲染长度均值从 13 到 4,916 Qwen3 token。

方法还引入教师画像以分离「监督变化」与「学生行为变化」。对每个完成 $y$，取最长可容纳于所有教师上下文的前缀 $J(y)$（直接回答画像上限 1,024 token），定义平均对数概率偏移

$$\Delta_{v}(y)=\frac{1}{|J(y)|}\sum_{t\in J(y)}\big[\log p^{T}_{v,t}(y_{t})-\log p^{S}_{t}(y_{t})\big]$$

正确性对齐 $C_v$ 在同时含正确与错误样本的问题上，先题内对比正确与错误响应的 $\Delta_v$，再跨题等权平均；纠正标记压力 $F_v$ 为 wait、but、check 等标记处的平均偏移；时间 KL 分配为保留跨度各四分位中全词表 $D_{\mathrm{KL}}$ 的占比。适用前提：证据来自两个模型家族（Qwen3-1.7B、SmolLM3-3B）上的短程 LoRA 数学训练，评估限于数学正确性；正确性对齐需同时存在正确与错误评分完成，配对交集仅 48 题；标记规则只识别采样到的标记 token，而非全部语义纠正续写。

## 实验设置

主实验在 Qwen3-1.7B 上用 LoRA（$r=64$，$\alpha=128$）训练 100 优化步，SmolLM3-3B 作跨家族检验；教师始终为冻结的思考模式骨干。主配置为直接回答训练、思考模式评估。学生生成上限 1,024 token（思考关闭），思考模式训练对比则延长 rollout。域内评估每题 4 个无特权思考样本，Avg@4 先题内平均再跨题平均；外部评估每题 12 个思考样本（Avg@12），在 AIME 2024、AIME 2025、HMMT 2025 上各 30 题。域内用 16,384 token 预算并对截断响应以同种子重生成至多 32,512 token；长度分析直接对首轮保存的前 4,096/8,192/16,384 token ID 打分，而非重新生成。配对 95% 区间用 10,000 次问题聚类 bootstrap；六视图初始对照用 seed-0 学生对比三 seed 对照并做 Holm 校正。训练/开发/测试划分为 1,536/192/384 题。总计算量约 1,000 H100 GPU-hours。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| AMPLE-Math 域内（384 题测试集） | Qwen3-1.7B（LoRA r=64, α=128） | 冻结基座 / 无参考学生 | 100 优化步，直接回答训练，思考模式评估 | Avg@4 相对冻结基座增益 |
| 外部（AIME24/AIME25/HMMT25，各 30 题） | Qwen3-1.7B | 冻结基座 | step 50，思考模式 | Δ Avg@12 |
| AMPLE-Math 域内 | Qwen3-1.7B | 无参考学生 | step 100，三 seed Clean Solution vs 三 seed 无参考 | Avg@4 差值 |
| AMPLE-Math 域内 | SmolLM3-3B | 无参考学生 | step 50，思考模式，三 seed | Avg@4 差值 |
| AMPLE-Math 域内 | SmolLM3-3B | 冻结基座 | step 50 / step 100，思考模式与直接回答 | Avg@4 增益 |
| AMPLE-Math 域内 | Qwen3-1.7B | 直接回答训练 | 思考模式训练 rollout，共同步 25/50/100 | Avg@4 差距（TH − DR） |
| 外部（AIME24/AIME25/HMMT25） | Qwen3-1.7B Full Trace | 直接回答训练 | step 50 | Δ Avg@12（TH − DR） |
| 原始 OPSD 训练数据，外部 | Qwen3-1.7B | 冻结基座 | step 50 | Avg@12 差值 |

## 证据与结果

核心数字（均照抄摘录，未给出的不补）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| Avg@4 gain over base | +1.80[0.20,3.47] | Reference-free, 3 seeds | Table 1 |
| Avg@4 gain over base | +1.67[0.07,3.32] | Wrong answer, 3 seeds | Table 1 |
| Avg@4 gain over base | +2.41[0.86,3.99] | Answer Only, 4 seeds | Table 1 |
| Avg@4 gain over base | +2.15[0.26,4.04] | Gist, 1 seed | Table 1 |
| Avg@4 gain over base | +2.80[0.72,4.88] | Key Points, 1 seed | Table 1 |
| Avg@4 gain over base | +3.10[1.54,4.73] | Clean Solution, 3 seeds | Table 1 |
| Avg@4 gain over base | +2.54[0.71,4.43] | Summary, 1 seed | Table 1 |
| Avg@4 gain over base | +2.38[0.91,3.86] | Full Trace, 4 seeds | Table 1 |
| Δ Avg@12 external | +4.07[1.73,6.54] | Reference-free | Table 1 |
| Δ Avg@12 external | +4.14[1.33,7.07] | Wrong answer | Table 1 |
| Δ Avg@12 external | +3.73[1.27,6.41] | Answer Only | Table 1 |
| Δ Avg@12 external | +4.35[1.30,7.59] | Gist | Table 1 |
| Δ Avg@12 external | +3.61[0.37,7.04] | Key Points | Table 1 |
| Δ Avg@12 external | +4.91[2.04,7.96] | Clean Solution | Table 1 |
| Δ Avg@12 external | +3.61[0.83,6.48] | Summary | Table 1 |
| Δ Avg@12 external | +2.29[-0.16,4.88] | Full Trace | Table 1 |
| Clean Solution − reference-free | +1.30[0.20,2.41] | 3 seeds each, thinking-enabled | §3.1, Table 10 |
| Full Trace − reference-free (SmolLM3) | +2.00[0.82,3.17] / +3.06[1.71,4.41] | step 50 / step 100 | §3.1, Table 6B |
| Answer Only − Full Trace | +5.32[3.47,7.16] / +0.03[-0.91,0.98] | direct-response / thinking-enabled, 4 seeds | Table 10, Table 14 |
| Mode interaction | +5.29[3.26,7.32] | direct-response minus thinking-enabled | Table 10, Table 14 |
| SmolLM3 step-50 mode interaction | 11.02[8.14,13.95] | DR contrast − TH contrast | Table 6 |
| Qwen TH − DR pooled | -2.89[-4.08,-1.71] / -7.60[-9.31,-5.95] / -7.14[-8.66,-5.64] | step 25/50/100 | Table 11 |
| SmolLM3 Full Trace TH − DR | -3.45[-4.98,-1.89] / -6.84[-8.50,-5.18] / -8.24[-10.16,-6.28] | step 25/50/100 | Table 12 |
| Qwen Full Trace external TH − DR | -13.06[-20.56,-5.83] / -12.78[-19.72,-6.39] / -2.50[-6.39,1.11] / pooled -9.44[-13.24,-5.83] | step 50, Avg@12 | Table 13 |
| Qwen Full Trace vs base external | TH -6.57[-9.81,-3.43]; DR +2.87[0.00,5.93] | step 50, pooled | Table 13 |
| Original-data external Avg@12 | base 47.22/39.17/23.89/36.76; OPSD 54.72/42.78/29.44/42.31; diff +7.50/+3.61/+5.56/+5.56 | AIME24/AIME25/HMMT25/Pooled | Table 8 |
| 零正确组增益 | Ref-free +3.97[0.39,7.62]; Answer Only +4.69[1.32,8.25]; Clean Solution +7.03[3.52,10.74]; Full Trace +5.66[2.59,8.84] | 128 problems | Table 7 |
| Clean Solution − reference-free（零正确组） | +3.06[0.46,5.79] | step 100 | Table 7 |
| 冻结基座分组准确率 | 61.91% (0/4), 83.98% (1–2/4), 94.73% (3–4/4) | Qwen3-1.7B | Table 7 |
| 外部按基座12样本分组 | 27 never-solved +0.62; 49 intermittently +10.03; 14 always-solved -0.60 | Avg@12 changes | §C.2 |
| 保存前缀评分 | 4K: -3.01[-4.85,-1.22], -3.99[-6.26,-1.78]; 8K: +3.29[1.46,5.06], +3.86[1.75,5.98]; 16K: +5.09[3.26,6.92], +9.51[7.41,11.62]; Full: +5.32[3.47,7.16], +10.81[8.60,13.00] | Answer Only−FT / Ref-free−FT | Table 15 |
| 其他问题参考干预 | Clean Solution 81.84[78.71,84.83], Δ -1.95[-3.78,-0.20]; Key Points 80.86[77.67,83.85], Δ -2.15[-3.97,-0.39] | 单种子 | Table 2 |
| 轨迹开头截断 | FT→CS 82.03[78.97,84.96], Δ -0.59[-2.28,1.11]; →KP Δ -0.20[-2.02,1.69]; →Summary Δ -1.11[-2.86,0.65] | 单种子 | Table 2 |
| 纠正标记损失编辑 | FT exclude Δ -0.65[-2.41,1.17]; downweight Δ -0.78[-2.34,0.78]; CS exclude/downweight Δ -0.72 | 单种子 | Table 2 |
| 损失窗口替代 | First-4K: +0.98/-0.85/-1.56; Distributed-1K: +0.98/+0.52/-1.30 | step 25/50/100 | Table 2, Figure 5 |
| 提示模板替换 | FT swap Δ -1.63[-3.39,0.13]; CS swap Δ +0.13[-1.50,1.76] | 单种子 | Table 2 |
| 数据集规模 | 5,319 题 × 6 视图 = 31,914 条；排除 161 题 | 来自 5,480 冻结池 | §B.1 |
| 视图渲染长度 | 13 至 4,916 Qwen3 tokens | Answer Only 至 Full Trace | §2.3 |
| 划分规模 | train/dev/test = 1,536/192/384 | 每带 512/64/128 | §2.3, §B.3 |
| 测试集与已发布 OPSD 数据重叠 | 384 题中 202 题（52.6%） | 同一上游来源 | §B.1 |
| 计算量 | 约 1,000 H100 GPU-hours | 全项目 | §A.5 |
| 外部截断样本 | 79/1,080（TH 训练）vs 2（DR 训练） | 38,912-token cap | §C.4 |
| 排除截断样本后差距 | -8.16[-12.16,-4.25] | FT TH − DR external | §C.4 |
| 截断样本全判对 | -2.13[-6.85,+2.69] | FT TH − DR external | §C.4 |
| SmolLM3 无答案率 | Ref-free 20.2%→42.0%; Answer Only 22.0%→39.4% | step 50→100 | §C.1 |
| SmolLM3 FT TH step 50 无答案率 | 19.7% → 1.3% | 初始 vs 重生成 | §C.1 |
| 冻结基座 Avg@4 | SmolLM3 82.16% TH / 40.23% DR; Qwen 80.21% TH | — | Table 6, Table 11 |

消融与对照：无参考对照（保留思考教师、去掉 PI）显示 Qwen 大部分提升已存在；错误答案对照（+1.67[0.07,3.32]）说明增益不专属于正确参考内容；长度匹配的其他问题参考使思考模式准确率下降约 2 点，说明参考内容本身有作用；轨迹开头截断在思考模式下无明确增益，但在直接回答下比匹配的 Full Trace 高约 8–11 点；纠正标记损失排除或降权在 step 100 均无准确率增益；损失窗口替代（First-4K、Distributed-1K）在匹配 checkpoint 下优势低于 1 点且区间含零，作者归因于停止时间；训练轨迹消融（DR→TH rollout）在两个模型家族中把增益变为损失。

## 证据强度评估

证据分级：B（中等偏强，但结论受单种子与评测污染限制）。

理由：正面看，本文的核心设计——答案匹配视图（同一验证答案、仅改推理表示）加无参考对照——直接针对「参考内容 vs 蒸馏本身」的混淆，这是该问题上的构造效度改进；跨两个模型家族（Qwen3-1.7B、SmolLM3-3B）、域内 384 题与外部 AIME24/AIME25/HMMT25 各 30 题、以及问题聚类 bootstrap 区间，提供了可迁移性证据；训练轨迹反转（TH − DR 在两个家族均为负，Qwen pooled step-50 -7.60[-9.31,-5.95]）是跨家族一致且量级较大的效应，可信度较高。但多数关键对照是单种子（Table 2 有十七个单种子比较），Clean Solution 的额外收益在 Holm 校正后不再显著（raw p=0.024，Holm-adjusted 0.15），且作者自述「区间含零不等于等价」。

主要威胁：

1. 构造效度：无参考对照并非同分布对照。作者明确说明它保留思考模式教师对直接回答前缀打分，因此是跨模式自蒸馏，而非相同师生分布的比较；「参考的额外贡献」因此与「模式不对称」纠缠。此外，正确性对齐需要同时有正确与错误评分完成，仅 116 题（TH）与 200 题（DR）可用，配对交集仅 48 题，画像结论的样本基础薄弱。

2. 统计显著性：核心的「参考有额外价值」证据（Clean Solution +1.30[0.20,2.41]）未通过多重比较校正；损失窗口替代的区间在每个匹配 checkpoint 都含零；许多干预为单种子，作者自述「区间含零不能确立等价」。

3. 评测污染与外部效度：384 道测试题中 202 道（52.6%）也出现在已发布的 OPSD 训练数据中，只有原始数据实现检查在外部评测；证据限于数学正确性的短程 LoRA 训练（100 步），作者明确不应解读为通用安全性评估。外部评测还受长度截断影响：TH 训练学生在 1,080 个外部样本中有 79 个触及 38,912-token 上限（DR 仅 2 个），排除截断样本后差距为 -8.16[-12.16,-4.25]，全判对时为 -2.13[-6.85,+2.69]，说明外部负迁移的量级对截断处理敏感。

4. 基线选择与评测模式敏感性：参考排序随评测模式翻转（Qwen step 100 直接回答下 Answer Only 与 reference-free 分别超过 Full Trace 5.32 与 10.81 点），且直接回答下的胜者写更长回答，仅评前 4K token 即反转排序（4K 时 Answer Only − Full Trace 为 -3.01[-4.85,-1.22]）。这意味着「哪个参考更好」的结论高度依赖评测模式与长度预算，迁移到其他场景时需重新验证。

## 边界与反例

**会推翻结论的观察。** 本文核心主张是「参考的额外贡献小且依赖视图与训练阶段」（C1、C2）。若在更长训练（远超 100 步）、全参数微调或更大模型上，出现「更完整参考一致地带来更大增益」且区间不含零，则 C2 被推翻。若在匹配 checkpoint 后，更广损失覆盖（First-4K、Distributed-1K）仍稳定优于 Early-1K 且区间不含零，则 C4「表观增益主要来自停止时间」被推翻——作者自己指出该优势在共同 step 25 时「falls below one point」且「intervals include zero at every matched checkpoint」，因此 C4 目前只是「未发现覆盖本身的独立收益」，而非已证伪覆盖有用。

**最可能失效的条件。** 证据限于短程 LoRA（r=64, α=128）、数学域、两个模型家族（Qwen3-1.7B、SmolLM3-3B），总计算约 1,000 H100 GPU-hours。作者明确列出：评测仅限数学正确性，不可外推为通用安全性评估；无参考对照仍是「思考模式教师给直接回答前缀打分」的跨模式自蒸馏，并非同分布对照；正确性对齐分析仅 116 题（思考模式）与 200 题（直接回答），配对交集仅 48 题；标记规则只识别采样到的标记 token，非全部语义纠正续写；视图生成与审核用同一模型，可能共享盲点；384 道测试题中 202 道（52.6%）与已发布 OPSD 训练数据重叠。此外 Table 2 的十七项干预多为单种子，损失窗口实验仅一个训练种子，作者亦声明「intervals including zero do not establish equivalence」。

**读者可能误推的方向。** 其一，把「无参考也能提升」误读为「参考内容无关」——作者用其他问题参考降低约两点（Clean Solution −1.95[−3.78,−0.20]；Key Points −2.15[−3.97,−0.39]）明确反驳。其二，把「Full Trace 无优势」误推为「长参考有害」——外部 Full Trace 仅 +2.29[−0.16,4.88]，区间含零，属未确立而非负效应。其三，把直接回答下的排序反转（Answer Only、reference-free 分别超 Full Trace 5.32 与 10.81 点）误推为「思考模式评测不可信」——作者用 4K/8K/16K 前缀评分显示 4K 时排序即反转，指向长度与评分预算混杂，而非单一模式优劣。其四，把 SmolLM3 step-100 全体低于基线误推为「蒸馏有害」——作者解读为 Full Trace「loses less」，是相对而非绝对收益。

## 与知识库的关系

**新增（相对既有 OPSD / 特权信息笔记）。** 本文把「蒸馏本身的增益」与「特权参考的额外贡献」显式分离：Qwen 中大部分提升在无参考时已存在，仅 Clean Solution 有 +1.30[0.20,2.41] 的小幅未校正优势，且不通过 Holm 校正。同时构建 AMPLE-Math（5,319 题 × 6 个答案匹配视图，共享同一验证答案），在答案信息固定下比较推理表示，得出「更完整的解（Full Trace）并不一致地带来更大增益」。这两点应作为新条目挂到 `note/opsd-privileged-information` 与 `note/reference-representation-distillation` 之下。

**印证并细化。** 与 Kaur et al. (2026) 的「思考模型退化 / 抑制重新考虑」一致：所有视图在两种前缀模式下都降低采样纠正标记概率；但本文进一步指出该共享符号无法区分迁移结果相反的配置，且放宽标记损失几乎不改变标记使用（Full Trace exclude −0.65[−2.41,1.17]；downweight −0.78[−2.34,0.78]）。这为 `note/thinking-degradation-reconsideration` 增加了一个「机制解释力不足」的限定。

**新增（损失覆盖）。** 对 `note/loss-coverage-long-rollout`：更广损失覆盖的表观收益主要来自停止时间，匹配 checkpoint 后优势低于 1 点且区间含零。

**新增（训练轨迹）。** 对 `note/training-trajectory-transfer`：保持教师与参考不变，把 direct-response rollout 换成 thinking-enabled rollout，在两个模型家族中把增益变为损失（Qwen pooled step-50 −7.60[−9.31,−5.95]；SmolLM3 step-50 −6.84[−8.50,−5.18]）。

**存在张力。** 与「更完整参考更有用」的直觉（可链接 `note/more-complete-solution-better`）直接冲突：Qwen 外部 Full Trace 仅 +2.29[−0.16,4.88]，而 Clean Solution 为 +4.91[2.04,7.96]。与「评测模式无关」的假设（`note/eval-mode-invariance`）冲突：同一学生在直接回答与思考回答下参考排序不同。需注意这些张力均建立在短程 LoRA 与数学域之上，迁移到其他设置前应视为待检验假设。

## 复现与验证计划

目标：在自有算力上验证「蒸馏增益 ≠ 参考贡献」这一核心分离，以及「训练轨迹反转迁移」这一最可迁移的结论。

环境与数据。取 Qwen3-1.7B 作学生与冻结教师（thinking-enabled 教师、direct-response 学生），LoRA $r=64,\alpha=128$，100 optimizer steps。数据可用 AMPLE-Math 的构造方式自建：从 OpenThoughts-114k 筛题，每题配 Answer Only / Gist / Key Points / Clean Solution / Summary / Full Trace 六个答案匹配视图，共享同一验证答案。若无法复现视图生成，最小可行替代是只保留 Answer Only、Clean Solution、Full Trace 三档加一个无参考对照，因为这三档覆盖了「无推理体—精炼解—完整轨迹」的跨度。评测用 384 题 in-domain 测试切分，每题 4 个 thinking-enabled 样本，Avg@4。

基线与判据。四个必测臂：frozen base、reference-free（保留 thinking 教师、去掉 PI）、Clean Solution、Full Trace。判据一：reference-free 相对 base 的增益应显著为正（原文 Qwen step 100 为 $+1.80\,[0.20,3.47]$）；若你的 reference-free 增益接近零，说明跨模式自蒸馏未生效，后续比较无意义。判据二：Clean Solution 相对 reference-free 的增量应小且区间可能含零（原文 $+1.30\,[0.20,2.41]$，Holm 校正后不显著）。判据三：把训练 rollout 从 direct-response 换成 thinking-enabled，同一参考应从增益转为损失（原文 Qwen pooled step 50 为 $-7.60\,[-9.31,-5.95]$）。

预算与统计。原文全项目约 1,000 H100 GPU-hours；最小验证建议至少 3 seeds，用问题聚类 bootstrap（10,000 次重采样）给配对 95% 区间，并对多视图对比做 Holm 校正。

预期失败模式。其一，评测模式敏感：同一 checkpoint 在 direct-response 评测下排序可能反转（原文 step 100 Answer Only 与 reference-free 分别超 Full Trace $5.32$ 与 $10.81$ 点），故必须固定评测模式。其二，长 rollout 被 1,024-token 损失窗口截断，thinking-enabled 训练只监督到开头，需显式记录窗口。其三，区间含零不等于等价，勿据此宣称无差异。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| OPSD（On-policy self-distillation） | 在线自蒸馏：冻结教师对学生自己生成的响应前缀打分，学生仅见问题 |
| PI（Privileged information） | 特权信息：训练时教师可见、推理时学生不可见的额外信息，如解答 |
| Answer-matched views | 答案匹配视图：共享同一验证答案、仅推理表示不同的多个参考版本 |
| Reference-free control | 无参考对照：保留 thinking-enabled 教师但去掉 PI，仍是跨模式自蒸馏，而非师生分布相同的比较 |
| Correctness alignment $C_v$ | 正确性对齐：正确响应比错误响应获得更大教师–学生概率偏移的程度 |
| Correction-marker pressure $F_v$ | 纠正标记压力：在 wait、but、check 等标记处教师–学生概率偏移的平均值，负值表示标记概率被压低 |
| Generalized KL $D_{\mathrm{gKL}}$ | 广义 KL：逐词项上限截断（0.05）的前向 KL 散度，用于 OPSD 损失 |
| Avg@n | 每题采样 $n$ 次正确率的平均，先题内平均再跨题平均 |
| Holm correction | Holm 多重比较校正，控制族错误率 |
| Rasch model | 联合估计评估者能力与题目难度的二项模型，用于标注题目难度 |

记号。问题 $x$，视图 $v$ 提供特权信息 $z_v(x)$；学生 $\pi_\theta$，冻结教师 $\pi_{\bar\theta}$；学生 rollout 配置 $m_S$，教师推理配置 $m_T$，教师打分温度 $\tau$。前缀 $s_t=(x,y_{<t})$ 上，学生下一词分布 $p^S_t(a)=\pi_\theta(a\mid x,y_{<t};m_S)$，教师分布 $p^T_{v,t}(a)=\pi_{\bar\theta}(a\mid x,z_v(x),y_{<t};m_T,\tau)$。损失为

$$\mathcal{L}_{v}(\theta;m_{S})=\mathbb{E}_{x,\,y\sim\pi_{\theta}(\cdot\mid x;m_{S})}\left[\frac{1}{|I(y)|}\sum_{t\in I(y)}D_{\mathrm{gKL}}\!\left(p^{T}_{v,t}\,\|\,p^{S}_{t}\right)\right],$$

求导时教师分布与采样完成固定。教师画像用平均对数概率偏移 $\Delta_v(y)=\frac{1}{|J(y)|}\sum_{t\in J(y)}[\log p^T_{v,t}(y_t)-\log p^S_t(y_t)]$，$J(y)$ 为适配所有教师上下文的最长前缀。注意 $C_v$ 与 $F_v$ 描述的是特定响应分布与跨度上的监督，不是参考的固定属性。

## 自测

以下问题用于检验读者是否真正区分了「蒸馏本身的增益」与「特权参考的额外贡献」，以及能否把该结论迁移到自己的训练配置。

**Q1.** 在 Qwen3-1.7B 的 in-domain 设置（step 100，Avg@4）中，reference-free 对照相对 frozen base 的增益是多少？Clean Solution 相对 reference-free 的额外增益是多少？后者是否通过 Holm 校正？

<details><summary>答案</summary>
reference-free 为 $+1.80\,[0.20,3.47]$；Clean Solution − reference-free 为 $+1.30\,[0.20,2.41]$（三 seed，thinking-enabled）。该效应在未校正时区间不含零（raw $p=0.024$），但 Holm 校正后为 $0.15$，不通过。作者据此主张这是「小的、视图特定的贡献」，而非「提供更多解答内容的一般性收益」。
</details>

**Q2.** 为什么「reference-free 对照」不能被当作「教师与学生分布相同」的对照？这对解读 C1 有何影响？

<details><summary>答案</summary>
因为该对照保留了 thinking-enabled 教师去给 direct-response 学生的前缀打分，只是去掉了 PI 段落，因此它仍是跨模式自蒸馏（cross-mode self-distillation），而非同分布对照。所以 reference-free 的增益本身可能来自「思考模式教师监督直接回答前缀」这一不对称，而非来自蒸馏的某种中性基线。这意味着 C1（「Qwen 中大部分提升无需参考即可获得」）成立，但「无需参考」不等于「无任何教师–学生不对称」。
</details>

**Q3.**（跨小节）在 Qwen 上，Full Trace 在 in-domain step 100 的增益为 $+2.38\,[0.91,3.86]$，在 external step 50 的 $\Delta$ Avg@12 为 $+2.29\,[-0.16,4.88]$；而 Answer Only 在 direct-response 评估下比 Full Trace 高 $5.32\,[3.47,7.16]$。这三组数字如何共同支持 C2（「更完整的解答不带来一致更大的增益」）？

<details><summary>答案</summary>
三点：(1) in-domain 上 Full Trace 与 Answer Only（$+2.41$）几乎持平，且都只比 reference-free 高约 $0.6$ 点、区间含零；(2) external 上 Full Trace 的区间跨零，是六视图中最弱的一档；(3) 在 direct-response 评估下排序反转，Answer Only 反超 Full Trace $5.32$ 点。因此「更完整」既未在 in-domain 带来一致优势，也未在 external 带来优势，且其相对排序还依赖评估模式——支持 C2，同时提示参考排序不是参考的固有属性。
</details>

**Q4.**（跨小节）把训练 rollout 从 direct-response 换成 thinking-enabled 后，同一参考的迁移结果如何变化？请给出 Qwen 与 SmolLM3 各一个数字，并说明为什么这一对比不能简单归因于「参考内容变了」。

<details><summary>答案</summary>
Qwen pooled（Answer Only/Clean Solution/Full Trace）step 50 的 TH − DR 为 $-7.60\,[-9.31,-5.95]$，step 100 为 $-7.14\,[-8.66,-5.64]$；SmolLM3 Full Trace step 50 为 $-6.84\,[-8.50,-5.18]$，step 100 为 $-8.24\,[-10.16,-6.28]$。外部 Qwen Full Trace step 50 pooled 为 $-9.44\,[-13.24,-5.83]$。教师与参考均保持不变，变的只是学生 rollout 的分布（即教师被要求打分的那些前缀），因此这是「参考的迁移效果依赖学生轨迹」，而非参考内容本身改变。注意作者也指出该对比中推理模式、horizon 与被监督比例同时变化，属于混杂。
</details>

**Q5.**（跨小节）作者称「扩大损失覆盖的表观增益主要来自停止时间」。请用 First-4K / Distributed-1K 与 Early-1K 的对比数字说明这一判断，并指出该结论的一个方法学限制。

<details><summary>答案</summary>
First-4K 与 Distributed-1K 相对 development-selected Early-1K 各高出约 4 点，但它们停在 step 25 而 Early-1K 停在 step 50；在共同 step 25 上优势降到 1 点以下（First-4K $+0.98\,[-0.91,2.86]$，Distributed-1K 同为 $+0.98\,[-0.91,2.86]$），且在每个匹配 checkpoint 上两者区间都含零（step 50：$-0.85$、$+0.52$；step 100：$-1.56$、$-1.30$）。因此差异主要来自 checkpoint 选择而非覆盖本身。限制：损失窗口实验只用一个训练 seed，且区间含零不能用来主张等价。
</details>
