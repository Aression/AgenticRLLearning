---
id: grpo
title: GRPO、DeepSeek-R1 与可验证推理
summary: 组内相对优势减少 critic 依赖，但不自动解决长时程 Agent 学习。
stage: SYSTEMS
track: 训练算法
order: 11
minutes: 22
updated: '2026-09-08'
review: 综合笔记
tags: [GRPO, RLVR, DeepSeek-R1]
sources: [deepseek-math, deepseek-r1, dapo]
prerequisites: [ppo, rewards]
---
## GRPO 的核心

DeepSeekMath 引入 Group Relative Policy Optimization。对同一问题采样一组回答，用组内回报构建相对优势，减少对单独价值模型的依赖。常见形式为：

$$
\hat A_i=\frac{r_i-\operatorname{mean}(r_1,\ldots,r_G)}{\operatorname{std}(r_1,\ldots,r_G)+\varepsilon}.
$$

再以这个信号优化生成 token 的概率，配合裁剪及可能的 KL 正则。不同代码库在标准化、长度归一化和 KL 处理上可能不同，不能只看算法名。

## 三个失败模式

1. **组内全同分**：优势接近零，难以提供区分信号。更可靠的任务难度分布与采样策略很重要。
2. **长度偏差**：按序列平均还是 token 平均会改变长短回答的贡献。
3. **验证器漏洞**：可验证不等于无法作弊，解析器和公开测试都可能被利用。

## R1-Zero 和 R1

原始技术报告区分直接从基础模型进行 RL 的 R1-Zero 与包含冷启动等阶段的 R1。不能把 R1 的所有结果概括为“完全不需要监督数据”。本库不复述未经复现的性能排名；重点是可验证回报、推理行为和多阶段训练之间的关系。

## 走向 Agentic RL 还缺什么

数学问题的最终答案奖励通常不涉及持续变化的外部环境。真实 agent 还需要工具观测遮罩、多轮终止逻辑、稀疏信用分配、状态重置和成本控制。对长轨迹直接套用组内终局优势可能过粗。

## 阅读顺序

先读 DeepSeekMath 算法章节，再读 R1 的训练阶段，最后看 DAPO 的动态采样与系统细节。下一步 [多轮 Agent RL](/notes/multi-turn-rl)。
