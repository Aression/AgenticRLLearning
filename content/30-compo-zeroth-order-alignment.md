---
id: compo-zeroth-order-alignment
title: ComPO：基于比较oracle的零阶偏好对齐
summary: 针对DPO类直接对齐中的似然位移问题，提出用零阶比较oracle从低边际噪声偏好对中提取更新方向。
stage: FRONTIER
track: 训练算法
order: 30
minutes: 18
updated: '2026-09-17'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.19144
reading_depth: full-text
evidence_level: full-text-llm-draft
full_text_url: https://arxiv.org/html/2609.19144
objectives: [理解似然位移（likelihood displacement）为何在低边际偏好对上出现, 说明ComPO如何用比较oracle替代可微偏好损失来利用噪声对, 区分论文的理论主张（可行性/覆盖界）与启发式在线实现之间的差距]
tags: [preference-optimization, DPO, zeroth-order, likelihood-displacement, RLHF]
sources: [a-zeroth-order-paradigm-for-llm-preferen]
related: [preferences, rewards]
prerequisites: []
---
## 论文要解决的问题

RLHF 的多阶段流程（先训奖励模型再 RL）在内存与算力上代价高，DPO 及其变体等直接对齐方法因此流行。作者指出这类方法有一个已被多篇工作讨论的问题：似然位移（likelihood displacement）——训练提高了偏好回答相对非偏好回答的似然，却降低了偏好回答的绝对概率，可能把概率质量推向不安全回答；另一相关现象是冗长化（verbosity）。已有共识（Pal、Razin 等）认为，位移与「偏好/非偏好回答在模型相关度量下过于相似」的小边际对有关，Razin 等提出用 CHES 分数过滤这类对。作者的主张是：过滤会把这些对完全丢弃，而它们仍可能携带比较信息，因此应换一种使用方式。

## 方法

ComPO 把对齐看作比较 oracle 问题而非固定可微损失：不显式写出对齐目标函数，而是对当前策略施加扰动，检查该扰动是否同时提高偏好回答似然、降低非偏好回答似然，再把每个扰动产生的一比特信号聚合成归一化更新方向。这样低边际（被标为 noisy）的偏好对只贡献方向信息，不直接参与边际式损失优化；干净对仍走标准直接对齐方法。论文进一步给出在线版本：离线比较方向保持不变，用当前策略的无标注生成做 reverse-KL 正则，通过长度归一化统计量以软阻尼规则调节步长，并配合 replay buffer。

## 证据与实验

离线实验在 UltraFeedback 上，以 Mistral-7B、Llama-3-8B、Gemma-2-9B-it 的 Base/Instruct 初始化，评估 AlpacaEval 2（WR 与长度控制 LC）、Arena-Hard、MT-Bench，硬件为 30 张 A40。在线实验在 Qwen3-4B-Base、Llama-3.2-3B-Instruct、Gemma-3-4B-it 上比较离线 ComPO、加阻尼、再加 replay 三种配置。作者称 ComPO 能改进现有直接对齐方法，且 pair-level 诊断与缓解似然位移一致。需注意：摘录中具体数值被省略，无法核验幅度；论文自述在线实现是「对基础方案的启发式近似」，并不真正评估下一步策略、也不强制定理中的序列级 reverse-KL 约束。

## 边界与未解问题

理论部分（可行性、基于覆盖的性能界）针对的是基础约束方案，而非实际部署的启发式在线实现，二者之间存在明确缺口。噪声/干净对的划分依赖边际阈值，摘录中阈值数值缺失，其敏感性只能由消融间接说明。评估依赖 GPT-4 系裁判，存在裁判偏差与长度混杂（LC 只做长度校正，不等于回答更短）。此外，本卡片仅基于论文摘录，实验数字与收敛性主张均属作者主张，未经独立复现。

## 与知识库的关系

ComPO 处在偏好对齐主线（RLHF → DPO → 直接对齐变体）的延长线上，与偏好数据、奖励建模、DPO 类方法等基础笔记直接相关；它不涉及 agent 循环或多轮交互，因此对 agentic RL 属于邻近而非核心。可作为「偏好数据几何如何影响对齐稳定性」这一专题的补充材料。

## 自测

1. 用自己的话解释似然位移，并说明为什么小边际对更容易触发它。
2. ComPO 与「过滤噪声对」在数据使用上的根本差别是什么？
3. 论文的理论保证覆盖哪一版算法？实际在线实现偏离了哪些假设？
