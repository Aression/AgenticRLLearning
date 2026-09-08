---
id: value-learning
title: 从 Bandit 到 TD 与 Q-learning
summary: 先理解探索和自举，再比较 on-policy、off-policy 与离线学习。
stage: FOUNDATION
track: 概念与基础
order: 4
minutes: 18
updated: '2026-09-08'
review: 综合笔记
tags: [TD, Q-learning, exploration]
sources: [sutton-barto, silver]
prerequisites: [mdp]
---
## Bandit 是最小起点

多臂老虎机只有动作选择和即时奖励，没有由动作改变后续状态的长期规划。它适合学探索与利用，但不足以模拟软件修复里“先检查再修改”的序列依赖。

Monte Carlo 用完整回合回报估计价值，方差可能较大。TD 用当前奖励和下一状态价值进行自举：

$$
V(s_t)\leftarrow V(s_t)+\alpha[r_t+\gamma V(s_{t+1})-V(s_t)].
$$

终止状态的后续价值设为零。时间限制导致的截断可能仍需 bootstrap，取决于任务定义；这也是使用 Gymnasium 时必须区分 terminated 与 truncated 的原因。

## Q-learning 的更新

$$
Q(s_t,a_t)\leftarrow Q(s_t,a_t)+\alpha[r_t+\gamma\max_aQ(s_{t+1},a)-Q(s_t,a_t)].
$$

采样行为可以是 epsilon-greedy，而目标是贪心策略，所以是 off-policy。SARSA 使用实际采样的下一个动作，在常见设定下是 on-policy。

## 三种数据关系

| 名词 | 核心区别 | Agent 训练中的含义 |
| --- | --- | --- |
| On-policy | 样本来自当前或近邻策略 | 更新后通常需重新收集 rollout |
| Off-policy | 行为策略与学习目标不同 | 陈旧轨迹可能需要校正或约束 |
| Offline RL | 训练时不能继续与环境交互 | 数据支持范围之外的价值容易外推失真 |

## 不要直接照搬

语言动作空间巨大，表格 Q-learning 无法直接枚举完整回答。深度值函数也面对分布偏移与估计误差。先在小离散任务中理解原理，再讨论 LLM 的策略梯度与序列训练。

## 完成标准

能解释 TD 的 bootstrap、off-policy 和 offline 不是同义词，以及探索为何会消耗工具调用预算。下一步 [策略梯度](/notes/policy-gradient)。
