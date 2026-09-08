---
id: multi-agent
title: 多智能体：编排、MARL 与 CTDE
summary: 多个角色聊天并不自动构成多智能体强化学习。
stage: FRONTIER
track: 前沿专题
order: 16
minutes: 18
updated: '2026-09-08'
review: 综合笔记
tags: [MARL, CTDE, coordination]
sources: [marl-book, agentic-survey, coskill]
prerequisites: [multi-turn-rl, evaluation]
---
## 从编排到学习

把任务交给 planner、coder、reviewer 是系统组织方式。只有定义联合交互过程、奖励和可学习策略更新后，才进入 MARL。多个 agent 可以共享同一套参数，也可以有不同策略与目标。

## CTDE

集中训练、分散执行（CTDE）允许训练时使用全局信息或集中 critic，执行时各 agent 只用自己的局部观测。论文必须说明训练可见信息与执行可见信息的边界，否则评测可能利用现实不可得的状态。

## 三个困难

- **非平稳性**：其他 agent 也在更新，一个 agent 看到的环境随之变化。
- **信用分配**：团队成功不代表每个成员都贡献了正效用。
- **通信成本**：更长对话增加 token、延迟和错误传播，不等于更强协作。

## 必需的基线

与同一预算的单 agent 比较；固定总 token、工具调用和时间。增加多个模型调用后成功率上升，可能只是用了更多计算。应比较不同角色、共享参数与通信协议的消融。

## 与技能演化的联系

近期 CoSkill 摘要提出推理 agent 与管理技能的 agent 联合学习。本库将其作为研究假设入口，尚未复现，不将其等同于 MARL 的普适结论。先读 [MARL 教材](https://www.marl-book.com/)，再看 [研究雷达](/notes/frontier-radar)。
