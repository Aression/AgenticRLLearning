---
id: training-systems
title: Rollout、训练解耦与系统预算
summary: 模型更新只是一部分，环境吞吐、策略陈旧度和验证成本共同决定效率。
stage: SYSTEMS
track: Agent 系统
order: 13
minutes: 18
updated: '2026-09-08'
review: 综合笔记
tags: [verl, Agent Lightning, rollout, asynchronous]
sources: [verl, lightning-code, agent-lightning, dapo]
prerequisites: [multi-turn-rl]
---
## 一个训练批次的生命周期

任务采样器选题；actor/inference engine 生成动作；环境执行；验证器评分；轨迹整理器计算 mask 与优势；learner 更新参数；新权重同步给 rollout workers。每个环节都可能成为瓶颈。

## 同步与异步

同步流程在更新边界等待全部轨迹完成，便于控制策略版本，但长尾任务会拖慢吞吐。异步让环境继续运行，提高利用率，却带来陈旧样本与更复杂的 off-policy 校正。不能只比较 tokens/s 而不比较有效成功任务/成本。

## 预算分解

显存包括参数、梯度、优化器状态、激活和推理 KV cache；PPO 还可能需要 critic 与 reference。GRPO 减少 critic 成本，但多样本 rollout 仍然昂贵。小模型、LoRA、短上下文可以降低门槛，但不保证训练稳定或获得同样能力。

## 框架选择

| 目标 | 建议起点 | 固定哪些版本 |
| --- | --- | --- |
| 理解经典 PPO | Gymnasium + SB3 | Python、环境、库版本 |
| LLM RL 配方 | verl | git SHA、模型 revision、推理引擎 |
| 接入已有 Agent | Agent Lightning | runtime、adapter、训练后端 |

框架主页反映当前状态，论文描述发表时版本。阅读实现前先查看支持矩阵与变更日志。知识库不会自动执行 GPU 训练或调用付费模型。

## 最小实验记录

保留模型 revision、数据 hash、split、奖励代码 hash、所有随机种子、硬件、总 GPU 小时、环境版本、成功率与原始计数。不要把一次成功的 demo 当作训练提升的证据。下一步 [评测](/notes/evaluation)。
