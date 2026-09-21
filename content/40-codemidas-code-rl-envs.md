---
id: codemidas-code-rl-envs
title: CodeMidas：从源码自动构造编码 RL 环境
summary: 提出以源码为唯一任务输入，自动生成任务陈述、开发环境与可执行验证器，并用 GRPO 训练编码智能体。
stage: FRONTIER
track: Agent 系统
order: 40
minutes: 18
updated: '2026-09-21'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.22068
reading_depth: full-text
evidence_level: full-text-llm-draft
full_text_url: https://arxiv.org/html/2609.22068
objectives: [说清 CodeMidas 如何把已实现功能转成任务陈述、起始代码库与隐藏验证器, 理解 rollout 后过滤（对抗探测、解法审查、成功率筛选）在环境构造中的作用, 区分论文报告的基准提升与尚未复现的证据边界]
tags: [coding-agent, RL-environment, GRPO, verifier, SWE]
sources: [codemidas-scaling-agentic-coding-rl-envi]
related: [environments, grpo, harness-design-coding-agents]
prerequisites: []
---
## 论文要解决的问题

编码智能体的强化学习需要两样东西：足够多样的任务，以及可信的奖励。已有流水线通常从开发痕迹中造题——issue、PR、commit、既有测试或文档。作者主张，这类做法把任务供给绑定在「被记录下来的变更、测试或文档覆盖范围」上，因而难以规模化。CodeMidas 的出发点是：已实现的代码本身就是任务与参考答案的来源，公开接口与可观察行为定义「要实现什么」，执行原代码则为测试期望提供证据。

## 方法

每个任务由三部分组成：任务陈述、容器化开发环境、隐藏的可执行验证器。验证器始终置于求解者环境之外，只在评分时注入，返回二值执行奖励。流程上，CodeMidas 先识别既有功能、写出行为级任务陈述，并把代码库改造成「目标功能尚待实现」的起始点；再基于原代码执行构造测试并做执行一致性检查；最后用 rollout 做后置过滤——对抗式 rollout 探测可被利用的泄漏，解法审查核对验证器判定是否符合陈述要求，成功率则用于任务筛选。作者强调设计张力：陈述要把所需行为讲清楚，同时不锁死内部实现；测试要拒绝错误解，也要接受其他正确实现。

## 证据与实验

作者用该流水线从 3,185 个开源代码库构造 5,545 个可验证任务，覆盖 23 种语言、15 个技术领域，并用 GRPO 训练 MiMo-V2.5（batch size 32，每任务 32 条 rollout，二值执行奖励）。报告称五个外部基准全部提升：DeepSWE 通过率 10.0%→21.7%，Terminal-Bench v2.1 63.7%→72.2%，ProgramBench 的 Almost Solved 4.5→21.5；CodeMidas Val 通过率 35.0%→44.7%，且轨迹变长。消融方面，高质量任务从 1k 增至 3k 再到 5,545 时 SWE-bench Pro、DeepSWE、CodeMidas Val 分数递增，3k 子集在三个基准上均优于未清洗过滤的 8k 基线。行为分析称训练中智能体更多探索代码库、自验证形式更多样，且自写检查与更高成功率相关，这些变化也出现在外部任务上。

## 边界与未解问题

以上均为论文作者的主张，本卡仅基于摘要与正文摘录，未做代码或产物核验，也未复现任何数字。需要留意的点：训练集与 CodeMidas Val 及五个外部基准任务集被声明为不相交，但这一声明本身依赖作者的划分流程；「自写检查与成功率相关」是相关性观察，不能读作因果；任务质量筛选的具体判据、对抗 rollout 的强度、以及验证器对替代正确实现的接受度，摘录中未给出可复核细节。此外，全部结果来自单一基座模型 MiMo-V2.5，跨模型可迁移性未知。

## 与知识库的关系

本文属于「环境构造」这条线：与 environments 笔记关注的可执行环境供给问题直接对应，与 grpo 笔记共享同一训练算法设定，与 harness-design-coding-agents 在「智能体如何探索代码库、如何自验证」的行为观察上互补。它可视为把 SWE 类环境从「依赖历史变更」推向「依赖现存功能」的一种规模化尝试。

## 自测

1. CodeMidas 相对既有流水线的关键差异是什么？为什么作者认为这能扩大任务供给？
2. 验证器为何要放在求解者环境之外、只在评分时注入？这对奖励可信度意味着什么？
3. 若把「3k 过滤子集优于 8k 未过滤基线」当作结论，你需要哪些额外信息才能接受它？
