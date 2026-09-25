---
id: glossary
title: 术语速查与容易混淆的缩写
summary: 中英对照，连接到概念正文，避免算法名和系统名混在一起。
stage: FOUNDATION
track: 概念与基础
kind: reference
depth: overview
evidenceGrade: C
order: 23
minutes: 8
updated: '2026-09-08'
review: 参考索引
objectives: [能快速查证易混缩写, 能连接到对应概念正文]
tags: [glossary, reference]
sources: [sutton-barto, agentic-survey]
prerequisites: []
---
## 用途

这是全库的命名基线。同一个词在不同论文里经常指向不同对象（例如 critic、verifier、memory、harness），缩写混用会让跨论文比较失效。阅读任何一篇新论文前，先用这张表确认它说的 policy、rollout、horizon 到底指什么。

## 速查表

| 术语 | 中文与含义 | 延伸 |
| --- | --- | --- |
| Policy | 策略，给定观测/历史的动作分布 | [MDP](/notes/mdp) |
| Rollout | 当前策略在环境中采样的交互轨迹 | [系统](/notes/training-systems) |
| Episode | 从任务初始化到结束的一次运行 | [环境](/notes/environments) |
| Horizon | 决策时程，不等于 token 上限 | [多轮 RL](/notes/multi-turn-rl) |
| Reward | 奖励，优化目标的反馈信号 | [奖励](/notes/rewards) |
| Return | 回报，未来奖励的累积 | [MDP](/notes/mdp) |
| Advantage | 优势，相对基线的价值差 | [策略梯度](/notes/policy-gradient) |
| Critic | 价值估计器，不一定是 LLM 裁判 | [PPO](/notes/ppo) |
| Verifier | 验证器，检查结果或过程 | [奖励](/notes/rewards) |
| RLVR | 具有可验证奖励的 RL | [GRPO](/notes/grpo) |
| Credit assignment | 信用分配，把结果归因给早期行为 | [多轮 RL](/notes/multi-turn-rl) |
| Harness | 执行框架：工具、提示、调度与环境封装 | [评测](/notes/evaluation) |
| On-policy | 从当前或近邻策略采样并学习 | [价值学习](/notes/value-learning) |
| Off-policy | 数据行为策略不同于学习目标策略 | [价值学习](/notes/value-learning) |
| Offline RL | 仅用固定数据训练，不能继续交互采样 | [价值学习](/notes/value-learning) |
| SFT | 监督微调，模仿示范 | [偏好优化](/notes/preferences) |
| KL | 分布差异；正则化不等于安全保证 | [PPO](/notes/ppo) |
| CTDE | 集中训练、分散执行 | [多智能体](/notes/multi-agent) |
| Ablation | 消融，移除组件以判断贡献 | [实验设计](/notes/lab-agent-rl) |
| Reward hacking | 利用奖励实现与真实目标的差距 | [安全](/notes/safety) |

## 常见混淆

上下文记忆、外部经验库、技能文件与模型参数不是同一种存储：它们的更新对象、写入时机与容量都不同。记忆改善表现并不自动意味着发生了 RL——要检查更新发生在哪一层、目标函数是什么。精确命名能减少阅读不同论文时的错位比较。

## 使用方式

1. 读到不熟悉的缩写时先在此处定位，再点进概念正文看定义与边界。
2. 如果一篇论文对某个术语的定义与这里冲突，先记录差异，再决定是修正词条还是新增词条。
3. 只写“最小可判定定义”：能据此判断一个具体系统算不算该术语即可。

## 维护约定

新增词条必须同时满足三条：给出中文含义、指向至少一篇本库笔记、说明它与最邻近术语的差别。只在大类标签下堆同义词不加分隔会降低检索价值。当某个术语积累到足够材料时，把它升级为独立的 concept 或 system 深读笔记，这里只保留一行索引。

## 与知识库的关系

本页是横向索引，不承载结论：它回答“这个词是什么”，不回答“这个方法是否有效”。判断有效性要回到对应的 concept、system 或 paper 笔记，并核对那里的证据分级。若发现词条与正文结论不一致，以正文为准并回来修正词条。
