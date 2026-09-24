---
id: pact-credit-critic-alignment
title: PACT：信用分配的公理化刻画与评论家对齐
summary: 提出信用的三条正则条件并证明其唯一表示，据此设计 Actor-then-Critic 更新顺序与 BCE 评论家训练。
stage: FRONTIER
track: 训练算法
order: 49
minutes: 18
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.26355
reading_depth: full-text
evidence_level: full-text-llm-draft
full_text_url: https://arxiv.org/html/2609.26355
objectives: [理解作者提出的 Completeness / Prefix Consistency / Neutrality 三条条件如何约束 token 级信用, 说清 PACT 的 Actor-then-Critic 更新顺序与 BCE 评论家目标相对 PPO/GRPO 的差异, 判断该唯一性定理与实验结论的证据边界]
tags: [credit-assignment, actor-critic, grpo, gae, swe-bench]
sources: [pact-from-credit-assignment-to-critic-al]
related: [grpo, ppo, value-learning]
prerequisites: []
---
## 论文要解决的问题

LLM 强化学习中，奖励往往只在整条轨迹结束后以标量形式给出，而策略更新发生在单个 token 上。这种粒度错配构成信用分配问题：最终结果应如何归因到轨迹中的各个 token。作者指出，把自回归生成建模为 token 级 MDP 只给出马尔可夫表示，并不能说明「与最终奖励相关的统计信息如何随轨迹展开而变化」，因此需要 MDP 之外的额外刻画。作者还强调，信用本身在文献中缺乏公认的数学定义，现有方法各自用算法相关的量来操作化它。

## 方法

作者提出三条正则条件——Completeness（完备性）、Prefix Consistency（前缀一致性）、Neutrality（中性）——并证明在这三条条件下信用被唯一确定。这是论文的核心理论主张，属于作者自证的结果，摘录中未给出证明细节（作者称证明放在附录）。

作者进一步给出若干推论：在理想教师下，On-Policy Distillation 的更新在期望意义上与唯一信用诱导的策略梯度成正比（差一个缩放因子），教师充当隐式评论家；RLOO 的响应级信号虽非 token 级信用，却诱导相同的期望策略梯度贡献；在奖励有界时 token 级信用具有近似稀疏性，这被用来解释 GAE 类 Actor-Critic 在长程任务中对评论家误差敏感、训练困难的现象。

工程侧提出 PACT（Policy Aligned Critic Training）：采用 Actor-then-Critic 的更新顺序，使评论家训练中可以做重要性采样校正，从而让评论家更贴合更新后的策略；并用 BCE 替代 MSE 训练评论家以更好逼近真实值。训练基于 Dressage（构建在 slime 之上的 agentic RL 框架）。

## 证据与实验

摘要与结论声称：在四个数学推理基准上平均准确率 72.87%，分别超过 GRPO 与 PPO 8.80 与 13.16 个百分点；在 SWE-bench Verified 上通过率 67.4%，分别超过 PPO、GRPO、SAO 2.4、2.0、3.8 个百分点。正文 5.2 节的表格数字在摘录中被占位符替换，无法核对逐项结果。作者还提到 PPO 在训练中出现策略崩溃，与其对 GAE 中间评论家误差的分析一致。

需要明确：以上均为论文自报结果，摘录中未见代码、超参细节（附录 E.4 仅提及 PACT 使用 TIS 与比例范围，具体数值缺失）或第三方复现。

## 边界与未解问题

作者在附录 F 主动列出三点限制：唯一性结论以三条正则条件为前提，换一组条件可能得到不同但自洽的表示（作者用更换欧氏平行公设作类比）；这里的信用是统计意义而非因果意义，由条件期望定义，不刻画替换单个 token 的反事实效应；论文刻画的是「信用应当是什么」，并未解决实际 LLM RL 中如何精确估计它的问题。

因此，把该唯一性定理当作「信用的唯一正确定义」是过度解读；它更接近一组公理下的条件性结论。PACT 的增益是否主要来自更新顺序、BCE 目标还是 TIS 校正，摘录中未提供充分的消融证据。

## 与知识库的关系

该工作直接落在 PPO/GAE 与 GRPO 的信用分配线索上：它把 GRPO 的组相对优势、RLOO 的留一基线、OPD 的蒸馏更新放在同一表示框架下解释，并延续了 VC-PPO、VAPO 对长链推理中价值估计失效的关注。与 value-learning 笔记中关于评论家训练的内容互补，可作为理解「为何 critic-free 方法流行」的理论视角。

## 自测

1. 三条正则条件分别约束信用的什么性质？去掉其中一条会失去什么？
2. Actor-then-Critic 顺序为何是重要性采样校正的前提？
3. 论文的稀疏性结论对 GAE 在长程任务中的表现给出了什么解释？
4. 若把该唯一性定理用于指导新算法，哪些前提必须先被接受？
