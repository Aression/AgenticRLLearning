---
id: prerequisites
title: 数学、机器学习与 LLM 先修
summary: 概率、梯度和自回归模型是理解策略优化的最短准备路径。
stage: FOUNDATION
track: 概念与基础
order: 2
minutes: 15
updated: '2026-09-08'
review: 综合笔记
tags: [probability, gradient, LLM]
sources: [sutton-barto, silver]
prerequisites: [orientation]
---
## 最低起点

能读 Python、理解条件概率和期望、知道反向传播与训练/验证集的作用，就可以开始。无需先精通控制理论。若这些概念陌生，先用纸笔算一个两动作 bandit，再进入复杂 Agent 环境。

## 三个需要真正会算的式子

条件期望把不确定的结果变成可优化目标：$\mathbb E[R]=\sum_x p(x)R(x)$。策略就是条件分布 $\pi_\theta(a\mid s)$，并非必须是确定性函数。

对数导数技巧是策略梯度的关键：$\nabla_\theta p_\theta(x)=p_\theta(x)\nabla_\theta\log p_\theta(x)$。它使采样得到的回报可以给动作概率提供更新方向，而无需对环境本身求导。

自回归 LLM 的序列概率为 $p_\theta(y\mid x)=\prod_t p_\theta(y_t\mid x,y_{<t})$。取对数后变成 token 对数概率之和。训练中必须知道哪些 token 是模型生成的动作，哪些来自用户或工具。

## LLM 最小背景

- **预训练**学习语言与知识分布；**SFT**模仿示范输出；**RL**优化由奖励定义的目标。这些阶段互补。
- **上下文窗口**承载本次推理信息，不等于模型长期参数记忆。
- **温度**改变采样分布，不代表参数学习；记录评测温度才能复现结果。
- **KL 散度**衡量分布差异。使用 KL 正则通常是限制偏离参考策略，而不是证明行为安全。

## 纸笔练习

两动作成功概率为 0.2 和 0.8，策略各以 0.5 选择时，期望成功率是 0.5。如果把第二个动作概率提高到 0.75，期望变为 0.65。注意单次失败不能否定第二个动作更优；学习面对的是随机回报。

## 完成标准

能解释“损失对参数求梯度”和“环境产生回报”之间的区别；能算序列 log probability；能说明评测集为何不能同时用于奖励调参。之后读 [MDP 与 POMDP](/notes/mdp)。
