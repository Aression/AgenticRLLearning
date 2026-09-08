---
id: mdp
title: MDP、POMDP 与 Bellman 方程
summary: 用状态、观测、动作、转移和回报，把 Agent 行为写成明确的学习问题。
stage: FOUNDATION
track: 概念与基础
order: 3
minutes: 20
updated: '2026-09-08'
review: 综合笔记
tags: [MDP, POMDP, Bellman]
sources: [sutton-barto, silver, agentic-survey]
prerequisites: [prerequisites]
---
## MDP 的组成

MDP 通常写为 $(\mathcal S,\mathcal A,P,r,\gamma)$。状态 $s$ 总结预测未来所需的信息；动作 $a$ 改变环境；$P(s'\mid s,a)$ 是转移；$r$ 给出即时反馈；$\gamma$ 控制未来回报折扣。

轨迹的折扣回报为 $G_t=\sum_{k=0}^{T-t-1}\gamma^k r_{t+k}$。这是一种索引约定；部分教材从 $R_{t+1}$ 开始，不能混用。LLM 有限任务也常设 $\gamma=1$，前提是明确定义终止和最大预算。

## Bellman 递推

策略价值满足：

$$
V^\pi(s)=\mathbb E_{a\sim\pi,s'\sim P}[r(s,a,s')+\gamma V^\pi(s')].
$$

动作价值 $Q^\pi(s,a)$ 衡量“先做这个动作，再遵循策略”的回报。优势 $A^\pi(s,a)=Q^\pi(s,a)-V^\pi(s)$ 比较该动作与策略平均行为。它是训练信号，不是动作的客观永久分数。

## 为什么 Agent 常是 POMDP

浏览器只提供截图或 DOM，代码 Agent 只看已读取的文件。真实状态 $s_t$ 通常不可见，模型接收观测 $o_t$ 并依赖历史 $h_t=(o_0,a_0,\ldots,o_t)$ 或其压缩记忆。

写成 $\pi(a_t\mid h_t)$ 是较稳妥的表达。截断上下文、摘要记忆都可能丢掉状态信息。不能因为把历史叫作 state 就自动获得良好的 Markov 性或可计算的 belief state。

## 建模示例

修复 bug 时，完整仓库与运行环境是状态；命令输出是观测；一次文件编辑是动作；测试结果和开销构成奖励信息。单独把“测试输出”当作全部状态，会漏掉未读文件和之前的修改。

## 常见错误与自测

工具输出是一条 observation，并不天然等于 reward。成功信号也可能延迟到任务结束。试着给一个检索问答任务写出观测、动作、终止、奖励和隐藏信息各是什么，再读 [价值学习](/notes/value-learning)。
