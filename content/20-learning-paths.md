---
id: learning-paths
title: 三条学习路线与里程碑
summary: 从概念入门、工程实践到论文复现，每一步都有可检查的产出。
stage: FOUNDATION
track: 实验与维护
order: 21
minutes: 10
updated: '2026-09-08'
review: 学习路线
tags: [roadmap, curriculum, milestones]
sources: [sutton-barto, silver, agentic-survey, diataxis]
prerequisites: [orientation]
---
## 路线 A：概念入门，建议 2 周

每周 4–6 小时，按已有基础调整。

1. [定义边界](/notes/orientation) -> [先修](/notes/prerequisites) -> [MDP](/notes/mdp)。产出：用同一个任务画出状态、观测、动作和奖励。
2. [价值学习](/notes/value-learning) -> [策略梯度](/notes/policy-gradient) -> [PPO](/notes/ppo)。产出：解释 baseline、GAE 和概率比。
3. [Agent 闭环](/notes/agent-loop) -> [实验 01](/notes/lab-rl)。产出：三种子实验卡，明确它不是 LLM Agent 训练。

## 路线 B：工程实践，建议 4 周

先完成 A，或确认能够解释 PPO。

1. [环境](/notes/environments) -> [奖励](/notes/rewards) -> [实验 02](/notes/lab-agent)。产出：可重放工具轨迹及独立验证器。
2. [偏好优化](/notes/preferences) -> [GRPO](/notes/grpo) -> [多轮 RL](/notes/multi-turn-rl)。产出：算法与反馈类型比较表。
3. [训练系统](/notes/training-systems) -> [评测](/notes/evaluation) -> [安全](/notes/safety)。产出：固定预算的评测协议与失败归因。
4. [实验 03](/notes/lab-agent-rl)。产出：有资源上限的训练提案；GPU 实验另按硬件实施。

## 路线 C：研究与复现，持续维护

1. [多智能体](/notes/multi-agent) 与领域综述建立问题树。
2. [研究雷达](/notes/frontier-radar) 选择一篇近期论文，不同时追所有方向。
3. 用论文卡记录主张、证据、限制和待验证假设；先复现基线，再测消融。
4. 将失败和不确定结果写入实验卡，更新概念笔记的适用边界。

## 进度含义

站点里的“已读”只是个人阅读标记，不宣称掌握或论文已复现。知识笔记的复核状态与浏览器阅读进度分开维护。导出进度可用于迁移设备；它不会自动同步到 Git。
