---
id: lab-agent
title: 实验 02：工具轨迹与独立验证
summary: 在本地确定性任务中重放工具调用，先验证协议再接入语言模型。
stage: SYSTEMS
track: 实验与维护
order: 19
minutes: 30
updated: '2026-09-08'
review: 实验指南
tags: [lab, trajectory, verifier, CPU]
sources: [gymnasium, tau-bench, agent-lightning]
prerequisites: [environments, evaluation, lab-rl]
---
## 为什么先做无模型实验

先证明环境状态和验证器正确，再让模型决策。否则环境 bug 会被误判成模型不足。仓库 `experiments/replay.py` 只有标准库依赖，不联网，也不调用付费 API。

## 任务

一个本地工具环境提供 `lookup`、`add` 和 `finish`。任务是查询两件物品的价格，算总和，提交结果。动作必须按 schema 提供；验证器从独立任务数据计算正确结果，而不是信任策略自报。

```bash
python experiments/replay.py
```

脚本运行成功轨迹、错误答案、越权工具与超预算案例，并输出每个步骤及最终评测结果。这是数据契约演示，不是 LLM 或 RL 性能 benchmark。

## 如何扩展成 Agent 实验

将脚本中的固定动作列表替换为模型的结构化输出；把工具返回追加到历史；保留最大步数和异常处理；记录模型版本、温度、token 与延迟。先比较规则策略和零训练模型，再考虑 SFT / RL。

## 防止评测泄漏

训练任务和测试任务使用不同任务 ID；策略看不到 oracle 的目标字段；最终验证在环境外执行。真实部署还应隔离进程与权限，演示中的 Python 对象边界不是安全沙箱。

## 完成标准

能定位一次失败究竟是工具调用、算术还是结束答案错误；能从轨迹复算成功率；证明非法工具名和步数耗尽不会悄悄当作成功。之后读 [LLM RL 实验设计](/notes/lab-agent-rl)。
