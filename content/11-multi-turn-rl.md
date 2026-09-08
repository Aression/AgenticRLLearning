---
id: multi-turn-rl
title: 多轮 Agent RL：轨迹、步骤与层级
summary: 从完整任务优势走向更细的步骤归因，并处理部分可观测和长轨迹。
stage: SYSTEMS
track: 训练算法
order: 12
minutes: 22
updated: '2026-09-08'
review: 综合笔记
tags: [GiGPO, long-horizon, hierarchical]
sources: [agentic-survey, gigpo, agent-lightning]
prerequisites: [grpo, environments]
---
## 三个时间尺度

一个环境动作可能包含很多 token，一个子任务可能包含很多工具调用，一个完整任务可能包含很多子任务。对所有 token 使用同一终局信号简单，但会掩盖局部错误。选择优化粒度就是选择归因偏差、方差和工程成本。

## GiGPO 的代表思路

GiGPO 在完整轨迹分组之外，利用跨轨迹重复环境状态构造步骤组，估计更局部的相对优势。它试图同时利用全局任务质量和局部动作效果。[原始论文](https://arxiv.org/abs/2505.10978)

关键阅读问题是：什么算同一 anchor state？部分观测相同是否对应相同真实状态？状态很少重复的任务是否还能得到足够组？论文特定环境的提升，不能外推为所有 agent 任务的固定收益。

## Agent Lightning 的代表思路

Agent Lightning 将执行运行时与 RL 训练解耦，通过统一数据接口和信用分配模块生成训练转移。这里的 “ANY” 是论文标题中的主张，落地时仍需检查可观测字段、支持的算法、环境依赖和实际集成改动。

## 训练前检查

- 采样组是否属于同一任务和可比较初始条件？
- 工具返回有没有进入 actor loss？
- 异常、超时和被截断轨迹如何处理？
- 参考策略、行为策略和 learner 版本是否可追踪？
- 奖励是否误把环境变化归功于策略？

## 完成标准

能对同一任务画出 token、步骤、子任务和 episode 四层结构，说明每层有哪些反馈与假设。下一步 [训练系统](/notes/training-systems)。
