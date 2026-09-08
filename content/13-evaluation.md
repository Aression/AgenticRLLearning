---
id: evaluation
title: Agent 评测：成功、成本与可靠性
summary: 明确任务分布和执行协议，才能判断提升来自模型、训练还是 harness。
stage: SYSTEMS
track: 评估与安全
order: 14
minutes: 20
updated: '2026-09-08'
review: 综合笔记
tags: [SWE-bench, WebArena, GAIA, tau-bench]
sources: [swe-bench, webarena, gaia, tau-bench, swe-agent]
prerequisites: [environments, rewards]
---
## 基准覆盖不同能力

| 基准 | 核心任务 | 特别注意 |
| --- | --- | --- |
| SWE-bench | 修复仓库 issue | 版本、测试隔离、数据污染 |
| WebArena | 网站上的多步任务 | 站点状态重置、工具与浏览器版本 |
| GAIA | 多工具综合助手题 | 检索时效、附件、外部依赖 |
| tau-bench | 工具与用户交互 | 业务规则、重复运行可靠性 |

这些基准之间没有直接可比的“总分”。挑选与目标工作流相似的任务，再明确它没有覆盖什么。

## 推荐最小报告

报告单次成功数 / 总任务数、平均与尾部工具调用数、token 成本、延迟、超时率、无效动作率、违反约束次数。多随机种子或重复任务时，给出区间估计与原始样本数，避免只展示最好一次。

## pass@k 与可靠性

pass@k 关注多次尝试中至少一次成功，增加 k 会增加测试时预算。tau-bench 中关注的 pass^k 风格指标强调多次运行均成功；它与 pass@k 方向不同。声明采用的精确定义与估计器，不要混用符号。

## 公平对比

固定模型 revision、工具、提示、最大步数、温度、任务集、环境快照和验证器。比较“训练前后”时先冻结 harness；再用未见 harness 测可迁移性。否则接口改进可能被误认为模型训练收益。

## 反例也要保留

按错误归因存例子：理解失败、检索失败、计划失效、工具错误、验证器漏洞、基础设施超时。训练失败轨迹是数据，评测失败更是结果，不能默默删去。

## 实践入口

先在 [本地评测实验](/notes/lab-agent) 做可回放的确定性任务，再迁移到大型 benchmark。之后阅读 [安全与奖励投机](/notes/safety)。
