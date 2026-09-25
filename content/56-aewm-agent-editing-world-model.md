---
id: aewm-agent-editing-world-model
title: AEWM：把语言世界模型改为编辑智能体状态
summary: 论文主张语言世界模型不应预测工具观测，而应判断决策效果并改写有噪声的推理-动作，以缓解长程任务中的状态污染。
stage: FRONTIER
track: 前沿专题
order: 56
minutes: 18
updated: '2026-09-25'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.28416
reading_depth: full-text
evidence_level: full-text-llm-draft
full_text_url: https://arxiv.org/html/2609.28416
objectives: [理解 AEWM 为何把预测目标从环境观测转向决策效果, 说清 Action Judge 与 State Revision 的分工及 EditAct 的执行流程, 评估其跨域增益与 RFT 迁移结论的证据强度]
tags: [world-model, llm-agent, long-horizon, state-revision, RFT]
sources: [agent-editing-world-model-rethinking-wor]
related: [actobs-observation-supervision, agent-loop, multi-turn-rl]
prerequisites: []
---
## 论文要解决的问题

长程 LLM 智能体在陌生环境中需要维护假设、计划与对已验证进展的判断。作者通过轨迹分析提出一个反复出现的失败机制：**任务状态污染**（task-state contamination）——智能体把未经验证的假设当成事实、在矛盾反馈下保留过时计划、把部分进展误认为完成。这些错误留在历史中，并通过局部看似合理的动作不断累积。

作者由此质疑主流语言世界模型的建模目标。已有共识是：世界模型学习动作条件下的下一状态或观测预测，在具身与交互视频生成中有效。但作者主张，任务导向的智能体需要的是环境反馈来完成任务，而非重建环境；搜索排名、终端输出、测试结果往往高熵且依赖执行状态，预测它们价值有限，甚至可能引入伪造证据。

## 方法

AEWM 把建模对象改为「智能体状态与决策 → 未来任务进展」。执行前状态包含任务、历史与候选推理-动作对，模型提供两项能力：

- **Action Judge**：把候选对判为 Critical（推进解法）、Exploratory（降低不确定性）或 Noisy（无产出方向）。
- **State Revision**：对 Noisy 决策，基于当前状态生成改写后的推理与动作。

**EditAct** 把二者与真实执行结合：保留有效决策、改写噪声决策，然后在真实环境中执行所选动作，真实观测再进入后续历史。作者强调这不是仅给批评意见，而是直接改变后续推理所依赖的状态。

训练上，作者用标注智能体合成 Action Judge 数据，用提议与改写智能体构造 State Revision 样本；两阶段训练为 52B token 中期训练加 120K 精选样本 SFT（Action Judge 与 State Revision 各 60K）。此外用 EditAct 轨迹做拒绝采样微调（AEWM-RFT），把决策模式迁移回智能体。

## 证据与实验

作者报告：自建 3,000 条决策的 Action Judge 基准上达到 70.5% macro-F1，超过最强基线 10.6 点；EditAct 在六个基准、三个骨干上均优于 ReAct 与步级/轨迹级 Best@3，对 Qwen3.5-4B/9B/35B-A3B 平均分提升 6.7/5.2/3.2 点；AEWM-RFT 在三个域超过 Self-RFT 2.2–2.6 点，且推理时不需 AEWM。消融称 EditAct 优于智能体重采样与推理提示。

需要注意证据边界：以上均为论文自述，本次仅见摘录，未见代码、数据或第三方复现；基准与评测协议由作者自建，跨模型比较的公平性无法独立核验。

## 边界与未解问题

作者自己指出，对更强的 Qwen3.5-Plus，EditAct 在 BrowseComp 有提升，但 Terminal 与 SWE 增益有限，推测源于 AEWM 与更强智能体之间的能力差距。此外，Action Judge 的三分类标签体系是否覆盖真实决策空间、Noisy 判定错误带来的改写风险、以及 52B token 中期训练的成本，摘录中均未给出充分讨论。

## 与知识库的关系

该工作与「观测监督」类思路形成对照：后者让模型预测观测，AEWM 主张改为编辑状态。它也与多轮 RL 中的干预/信用分配问题相关——State Revision 可视为一种推理时的状态级干预，而 AEWM-RFT 则接近用修正轨迹做离线蒸馏。

## 自测

1. 作者认为预测工具响应为何对任务型智能体价值有限？
2. Action Judge 与 State Revision 在 EditAct 中如何衔接？
3. 若要复现，哪些数字与协议最需要独立验证？
