---
id: environments
title: 环境、工具协议与轨迹数据
summary: 让每一步动作可观测、可验证、可重放，是训练之前的基础设施。
stage: SYSTEMS
track: Agent 系统
order: 8
minutes: 18
updated: '2026-09-08'
review: 综合笔记
tags: [environment, trajectory, masking]
sources: [gymnasium, swe-agent, webarena, agent-lightning]
prerequisites: [agent-loop]
---
## 环境接口

Gymnasium 的 `reset(seed=...)` 和 `step(action)` 提供统一心智模型。网页与代码环境不必完全套用数值 observation，但应该明确：观测、动作 schema、奖励、terminated、truncated 与诊断信息。

终止表示任务语义结束，截断常来自时间或资源限制。若任务将预算耗尽视为失败终点，应在协议中写清，不能让 learner 自行猜测 bootstrap 行为。

## 最小轨迹记录

```json
{
  "run_id": "demo-001",
  "task_id": "heldout-007",
  "policy_version": "checkpoint-sha",
  "environment_version": "container-digest",
  "seed": 42,
  "step": 3,
  "observation": {"test_status": "failing"},
  "action": {"tool": "read_file", "args": {"path": "src/main.py"}},
  "reward": 0,
  "terminated": false,
  "truncated": false,
  "latency_ms": 180,
  "generated_token_mask": [1, 1, 1]
}
```

这只是字段示意，生产 schema 还需记录 token IDs、行为 logprobs、实际返回、有效动作、总预算与错误。不可把含私人数据或凭据的原始轨迹直接提交到 Git。

## 动作与副作用

工具应校验参数类型、范围和权限；重试带副作用的动作必须考虑幂等性。训练通常从可重置的隔离环境开始。评测依赖环境状态的验证器，而不是模型回答“我完成了”。

## 数据质量关卡

按 task ID 分割训练与测试；对轨迹去重；记录异常和超时，不能只保留成功运行。用户和工具文本应从 actor loss 中遮罩，模型生成的工具参数才是可优化动作的一部分。

## 完成标准

可以重放一次失败并判断来自策略、工具还是基础设施。不能重放并不总是 bug，例如实时网页会变化，但这类限制必须记录。继续 [奖励设计](/notes/rewards)。
