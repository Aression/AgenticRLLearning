---
id: ppo
title: PPO：限制每次策略更新
summary: 看懂裁剪目标、旧策略、KL 与 critic，再理解 LLM RL 的工程变体。
stage: FOUNDATION
track: 训练算法
order: 6
minutes: 22
updated: '2026-09-08'
review: 综合笔记
tags: [PPO, clipping, KL]
sources: [ppo, gae, sb3]
prerequisites: [policy-gradient]
---
## 原始目标

记 $\rho_t(\theta)=\pi_\theta(a_t\mid h_t)/\pi_{old}(a_t\mid h_t)$，PPO 的裁剪替代目标是：

$$
L^{CLIP}=\mathbb E_t[\min(\rho_t\hat A_t,\operatorname{clip}(\rho_t,1-\epsilon,1+\epsilon)\hat A_t)].
$$

它降低某些过大更新的收益，但**不是**对每个概率比施加硬约束，也不保证每次更新都改善真实任务表现。实际训练还可能有价值损失与熵项。

## 三个分布不要混淆

- **当前策略**：正在被优化的模型。
- **旧策略**：产生本批 rollout 的行为模型，用于概率比。
- **参考策略**：通常固定的 SFT 模型，用于 KL 正则；不必等于旧策略。

如果旧 log probability 是另一种采样/推理设置算出来的，概率比可能失真。训练与推理引擎精度、温度、采样过滤都会影响这种一致性。

## 实用诊断

同时记录奖励均值、成功率、KL、熵、clip fraction、value loss、梯度范数和有效 token 数。奖励上升但独立成功率下降可能是 reward hacking。熵过早坍缩会减少探索，过高则可能无法稳定执行格式化动作。

## 入门建议

先用 [Stable Baselines3](https://stable-baselines3.readthedocs.io/en/master/) 跑离散环境的 PPO，观察不同种子。不要为理解公式而从零写一个完整 RL 训练器。LLM PPO 需要更多显存与 rollout 工程，不适合当作第一个十分钟实验。

## 阅读问题

找原论文的目标函数与实验设置：epsilon 取值为何是超参数？小 KL 是否能证明工具调用安全？答案是不能，安全约束还取决于动作权限与评估。下一步 [LLM Agent 闭环](/notes/agent-loop)。
