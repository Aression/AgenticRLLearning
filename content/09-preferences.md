---
id: preferences
title: RLHF、RLAIF 与 DPO 的位置
summary: 偏好数据、奖励模型、KL 正则和离线优化，解决的问题并不完全相同。
stage: SYSTEMS
track: 训练算法
order: 10
minutes: 18
updated: '2026-09-08'
review: 综合笔记
tags: [RLHF, RLAIF, DPO, alignment]
sources: [instructgpt, constitutional, dpo]
prerequisites: [ppo, rewards]
---
## 经典 RLHF 流程

InstructGPT 的代表流程是：监督微调得到初始策略；收集人类比较并训练奖励模型；使用带 KL 约束的 RL 优化。人类偏好提供目标近似，并不保证无偏或覆盖所有任务。

## RLAIF 改变了监督来源

Constitutional AI 用原则引导模型批评、修订和比较，减少对某些人工反馈的依赖。AI 裁判仍可能继承训练数据偏差，对格式和长度敏感，或与被评估模型共享盲点。

## DPO 的边界

原始 DPO 在特定偏好建模和 KL 正则化假设下，把优化写成直接作用于优选/劣选回答概率的损失。常见的离线 DPO 不需要训练一个独立 reward model，也不需要每步在线采集环境轨迹。

这不意味着 DPO 与 RL 没有理论联系，而是说“使用 DPO”本身不足以说明一个 agent 正在进行多步环境交互强化学习。偏好轨迹优化也可用于 agent，但要额外定义比较粒度与数据分布。

## 如何选择

| 可用反馈 | 起点 | 要警惕 |
| --- | --- | --- |
| 好的示范轨迹 | SFT / 行为克隆 | 模仿错误、分布外状态 |
| 离线偏好对 | DPO 等偏好优化 | 覆盖不足、偏好噪声 |
| 可运行环境和可靠验证器 | 在线 RL | rollout 成本、奖励投机 |
| 昂贵的人类判断 | 混合监督 | 裁判校准与代表性 |

## 自测

解释旧策略和参考策略为何不同；说明语言风格偏好与真实任务成功的关系为何需要实证。继续 [GRPO 与 R1](/notes/grpo)。
