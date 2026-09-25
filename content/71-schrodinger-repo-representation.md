---
id: schrodinger-repo-representation
title: 仓库表示作为评测变量：SWE-bench 是学会还是记住
summary: 提出在评测时动态生成语义等价的仓库视图，检验编码智能体是否依赖熟悉的仓库线索而非真实推理。
stage: SYSTEMS
track: 评估与安全
kind: paper
depth: overview
evidenceGrade: C
order: 71
minutes: 18
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.27891
reading_depth: full-text
evidence_level: full-text-llm-draft
full_text_url: https://arxiv.org/html/2609.27891
objectives: [理解静态基准表示为何会混淆记忆与推理能力, 掌握 SchrodingerRepo 的四级语义保持变换设计, 能区分作者主张与已有共识，并识别该研究的证据边界]
tags: [swe-bench, benchmark-validity, data-leakage, coding-agent, evaluation]
sources: [schr-dinger-s-code-repository-have-llms]
related: [evaluation, harness-design-coding-agents, category-expert-swe-agents]
prerequisites: []
---
## 论文要解决的问题

SWE-bench 及其 Verified 子集已成为仓库级编码智能体的标准评测基准，但实例来自公开且被广泛使用的开源仓库，每个 issue 只以单一固定的仓库呈现形式反复出现在训练、开发与评测中。作者主张：高分可能反映模型对仓库特有模式（命名约定、API、文件布局）的熟悉，而非真正的代码推理。已有共识是 SWE 类基准存在数据泄漏风险，OpenAI 也曾分析 SWE-bench Verified 不再可靠地衡量前沿编码能力；近期工作（SWE-bench Live、SWE-rebench、SWE-bench Pro）通过持续纳入新实例来缓解污染，但作者认为这些方案在规模与问题类型覆盖上仍受限。

## 方法

SchrodingerRepo 把仓库表示从固定的基准产物变成评测时才实例化的隐变量：对既有仓库施加受控变换，生成语义等价、可执行行为不变的代码库，同时抹去熟悉的仓库侧线索。变换分四级：Level 1 重构问题陈述；Level 2 重映射仓库自有命名空间；Level 3 重排文件内布局；Level 4 在保持功能的前提下重写局部实现。随机种子决定每次评测得到确定但不同的仓库视图。作者称这是首个对仓库表示敏感性进行系统研究的框架。

## 证据与实验

作者在 SWE-bench Verified、SWE-rebench 2026 年 3 月榜单中发布于被测模型之后的时间留出实例、以及 SWE-QA 上评测了若干模型（GPT-5.4-mini、GPT 5.1、DeepSeek-v4-Flash、Gemini-3.1-Flash-Lite）。摘录给出的结论包括：完整变换使 SWE-bench Verified 的 Pass@1 下降 6.0–14.4 个百分点，其中命名空间映射影响最大；额外动作中 81.6–83.6% 用于探索与定位；SWE-QA 上答案质量最多下降 4.64 分、动作增加 18.15–43.02%；在时间留出的 SWE-rebench 实例上 Pass@1 保持而交互成本上升。作者据此论证退化并非任务本身变难，而是熟悉线索被移除。此外，动机实验用人工专家逐轮揭示问题陈述语义单元，报告超过 65% 的实例存在明显泄漏证据、超过 18% 可回忆到补丁/测试级别。

## 边界与未解问题

以上均为论文摘要与摘录层面的作者主张，本卡片未复现实验，也未核验代码或数据。动机实验中「泄漏证据」的判定依赖人工专家流程，其标注一致性未在摘录中说明。时间留出实验上 Pass@1 不变而成本上升，这一结果与「依赖熟悉线索」的解释相容，但也可能反映其他因素，作者未给出排除性证据。变换是否在所有仓库类型上都严格保持语义等价，摘录未提供验证细节。作者提出的未来方向是支持更丰富的仓库感知工具接口（IDE API、语言服务器查询），说明当前结论主要限于命令行智能体工作流。

## 与知识库的关系

本工作属于评估与安全方向，与 evaluation 笔记中关于基准有效性的讨论直接相关；其「表示即变量」的思路可与 harness-design-coding-agents 中关于评测脚手架影响结果的观察对照；对 SWE 智能体能力来源的质疑也与 category-expert-swe-agents 的能力归因问题呼应。

## 自测

1. 为什么「持续更新基准」不能完全解决作者关心的泄漏问题？
2. 四级变换各自针对哪类仓库侧线索？
3. 时间留出实验的结果如何支持作者的解释，又留下什么替代解释？
