---
id: policy-gradient
title: Policy Gradient、Actor-Critic 与 GAE
summary: 用回报加权动作概率，并用价值基线改善梯度估计。
stage: FOUNDATION
track: 训练算法
order: 5
minutes: 22
updated: '2026-09-08'
review: 综合笔记
tags: [REINFORCE, actor-critic, GAE]
sources: [sutton-barto, gae]
prerequisites: [value-learning]
---
## 从采样到梯度

目标 $J(\theta)=\mathbb E_{\tau\sim\pi_\theta}[R(\tau)]$ 的一种蒙特卡洛梯度估计为：

$$
\widehat{\nabla J}=\sum_t\nabla_\theta\log\pi_\theta(a_t\mid h_t)\hat A_t.
$$

好于基线的动作获得正优势，差于基线则为负。环境可以是不可微的程序或网页，因为我们对策略对数概率求导，不对网页执行过程求导。

## 为什么要基线

REINFORCE 可用回报减去与当前动作无关的基线来降低方差。在满足相应采样假设时，这不会改变期望梯度。Actor-Critic 用 critic 估计价值，actor 根据优势更新动作分布；critic 不需要与 actor 同一套参数。

## GAE 的权衡

令 $\delta_t=r_t+\gamma V(h_{t+1})-V(h_t)$，广义优势估计为：

$$
\hat A_t^{GAE}=\sum_{l\ge 0}(\gamma\lambda)^l\delta_{t+l}.
$$

实际在有限轨迹上求和并处理边界。较大的 $\lambda$ 更依赖长回报，一般会提高方差、减少对短期价值估计的依赖；具体偏差还取决于 critic 误差。

## LLM 中的两个粒度

token 级动作有易取得的 log probability；一次工具调用可能由很多 token 组成。若把工具返回文本也纳入 actor loss，模型就会被要求学习自己没有生成的文本，这是常见数据管线错误。一个轨迹优势广播到所有动作 token 也不等于解决了细粒度信用分配。

## 自测

能解释：降低梯度方差不等于提高环境奖励；critic 估计有偏会影响策略更新；reward 为正但 advantage 仍可为负。接着读 [PPO](/notes/ppo)。
