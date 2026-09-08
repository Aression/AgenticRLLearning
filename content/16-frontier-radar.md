---
id: frontier-radar
title: 研究雷达：2026 年 8–9 月
summary: 技能共演化、经验蒸馏和跨 harness 泛化；所有近期条目均为摘要核验、待精读。
stage: FRONTIER
track: 前沿专题
order: 17
minutes: 18
updated: '2026-09-08'
review: 摘要核验 · 待精读
tags: [2026, skills, generalization, exploration]
sources: [coskill, multi-harness, agent-g2, edge, agentic-survey]
prerequisites: [multi-agent, training-systems]
---
## 调研边界

本页基于 2026-09-08 的 arXiv API 检索和原始摘要页，搜索记录保存在 `research/discovery.json`。只核验题目、日期与作者摘要中的主张，**未全文精读、未复现，也不声称穷尽最新文献**。arXiv 收录不等于同行评审通过。

## 四个值得追踪的问题

| 方向 | 新论文 | 作者提出的思路 | 下一步应核验 |
| --- | --- | --- | --- |
| 技能与策略共演化 | [CoSkill, 2026-09-04](https://arxiv.org/abs/2609.04865) | 联合训练推理与元技能 agent | 同预算基线、共享参数消融、任务泄漏 |
| 跨执行框架泛化 | [Multi-Harness RL, 2026-09-03](https://arxiv.org/abs/2609.04518) | 分离组内归因与 harness 混合影响 | 冻结轨迹的适用边界、未见框架、置信区间 |
| 长任务探索 | [Agent-G², 2026-08-24](https://arxiv.org/abs/2608.23318) | 按任务调节专家轨迹前缀深度 | 引导信息来源、总 rollout 成本、分布外任务 |
| 经验蒸馏 | [EDGE, 2026-08-22](https://arxiv.org/abs/2608.21946) | 训练时利用经验，再内化到策略 | 无经验推理消融、负迁移、经验库污染 |

## 为什么不能只抄最高分

不同模型、harness、任务版本和尝试预算会改变结果。近期 Multi-Harness RL 的摘要尤其强调执行框架对测得性能的影响。这个观察值得审查，但仍不应从一篇预印本推断所有任务的训练增益都来自框架。

## 更长期的研究轴

持续学习如何防止遗忘；记忆何时应写入参数、何时保留外部检索；过程信号如何降低稀疏奖励；异步训练如何校正策略陈旧；安全约束如何跨工具迁移。这些轴比按发布时间追热点更稳定。

## 晋级规则

读完方法、附录、数据与代码后，写论文卡并记录可反驳假设；复现实验后再增加“复现”标签。本文只能作为候选阅读队列。下一步按 [维护协议](/notes/maintenance) 整理新的证据。
