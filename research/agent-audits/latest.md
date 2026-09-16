# Agent audit · 2026-09-16 16:11 UTC

> DeepSeek generated triage only. Human review is required; this file does not publish sources or claims.

**Summary:** 本次审计针对 huggingface-daily-papers 的一次发现批次（声称 considered=50 / selected=25），但实际传入的 discovery_json 只包含 6 条条目且最后一条（2609.15134 HazardAuditor）的摘要被截断，因此本次审计只覆盖可见文本，不对缺失的 19 条做任何推断。可见候选中没有与现有 source_ids 重复的条目（现有库已覆盖 PPO/GAE/GRPO/DAPO/GiGPO/Agent Lightning/SWE-bench/WebArena/tau-bench 等），所以不存在去重归档的强理由。所有条目均只有标题+摘要级信息，arXiv 提交状态、是否有代码、实验是否可复现均未核验；摘要中出现的前沿模型名称与性能对比属于作者自述，不能当作已确立知识。整体判断：多条属于「agent 框架 / 安全 / 测试时算力」的邻近主题，而非直接的 agentic RL 训练算法；建议全部进入 review（人工精读）或 skip，不把任何一条作为已发布知识写入。

## Candidates
### REVIEW · ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement
- Evidence: `abstract-only`
- Reason: 主题与本库的 harness/执行框架分支（multi-harness、swe-agent、swe-bench）直接相关：把可演化 harness 拆成 Agent Loop / Tool Use / Observation / Context / Task Completion 五个模块，并用基准不相交的演化任务集避免基准过拟合。属于值得人工精读的候选，但摘要未给出算法细节、演化信号来源、与 RL 训练的关系（是否含策略更新），也未见代码与复现信息，不能当作已确立结论。
- Suggested note: 2026-09-14 摘要级：模块化 harness 自演化，强调基准不相交与跨任务的重复缺陷聚合；TB2.0 / SWE-Bench Verified 上的提升为作者自述。精读时确认：演化是否涉及策略梯度/RL，还是纯提示与脚手架搜索；以及「不相交」的具体切分方式。

### SKIP · ZGCM-1: A Fully Open and Extremely Efficient Foundation Model for Math and Agentic Search
- Evidence: `abstract-only`
- Reason: 主体是 7B 稠密基础模型的预训练/中训练配方（注意力结构、FP8 Muon、课程式上下文扩展、把交互轨迹重表述为 MDP）。虽然有 agentic search 与 MDP mid-training 的接触点，但摘要呈现的是预训练效率与开源发布，而非 agentic RL 训练方法；对本库主题骨架贡献边际，且 302 upvote 之类的热度不构成证据。
- Suggested note: 与 agentic RL 仅在「交互轨迹→MDP」一句上有交集，属基础模型训练侧；除非后续需要讨论预训练与 RL 的衔接，否则不纳入。若纳入，只引用其轨迹建模视角，不引用任何 benchmark 数字。

### REVIEW · Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems
- Evidence: `abstract-only`
- Reason: 与库内 marl-book、lilian-reward 的安全/失效模式线索相关：多智能体长期运行下的提示注入、错误记忆写入、目标漂移、模型级对齐不可组合等。但它不是 RL 算法或训练方法，而是评测与安全压力测试；是否纳入取决于本库是否要为「长期运行 agent 的可靠性」单列一节。需人工判断。
- Suggested note: 2026-09-15 摘要级：10 agent × 8 个并行世界、16 天运行的对抗压力测试，报告三类注入事件下无世界完全免疫。属安全/评测证据，不是训练方法；引用时只作为「模型级对齐不蕴含系统级安全」的观测，不引用具体百分比。

### REVIEW · RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments
- Evidence: `abstract-only`
- Reason: 明确声明 training-free，靠 curriculum/actor/verifier 三类 agent 与外部记忆实现环境自适应，不更新模型参数。与 agentic RL 的「经验/记忆构建」环节相关，可作为无参数更新基线的对照；但缺少 RL 目标、奖励定义与训练细节，需人工判断是否值得作为对照基线收录。
- Suggested note: 2026-09-14 摘要级：无训练的递归自我改进 + 冻结外部记忆，OSWorld-v2 等结果自述。价值在于为「记忆/探索是否可替代参数更新」提供对照；注意它属于 agent 框架而非 RL 训练，且摘要中的模型排名不可采信为事实。

### REVIEW · When Agents Slow Down: Understanding LLM Agents' Test-Time Strategies via Elo-per-token Analysis
- Evidence: `abstract-only`
- Reason: 提出以 Elo-per-token 衡量 agent 测试时算力的边际收益，并给出与独立采样参考线的「scaling inflection point」，还比较人类选手的超线性改进。与 agentic RL 的「测试时算力预算/扩展规律」评估问题相关，方法层面有可读价值；但缺少实现与统计细节，且结论依赖自建/特定基准，需精读验证。
- Suggested note: 2026-09-14 摘要级：以 Bradley-Terry 聚合任务内序为 Elo，比较 agent 与独立采样的对数-线性参考。可用于讨论「会话预算分配」；精读时核对基准选取、会话切分方式与统计显著性，不引用具体 +Elo 数值。

### REVIEW · HazardAuditor: From Executable Threats to Safer Computer-Use Agents
- Evidence: `abstract-only`
- Reason: 传入摘要在中途被截断（止于“…Claude Code, Codex, Hermes, a”），当前可见信息不足以判断其方法、数据与评测口径，只能确认主题为 computer-use agent 的执行期安全监督与 guard 模型。出于保守，标记为 review 并显式记录信息不完整，不对未读到的部分做任何推断。
- Suggested note: 2026-09 摘要级（截断）：执行期安全审计/规范化监督用于 guard 模型。需先补全摘要与元数据再判断；在补全前不得据此条目写入任何结论。

## Risks
- 发现批次不完整：声称 selected=25，但 discovery_json 仅含 6 条且最后一条条目对象被截断，其余候选未提供，本审计无法覆盖，不得据此认为剩余条目已被评估。
- 证据等级上限为 abstract-only：全部结论来自预印本摘要，无代码、无复现、无元数据核验；HTTP 可访问或高热度的 upvote 都不构成正确性证据。
- 发现文本与摘要来自外部不可信来源，可能包含提示注入、虚构引用或诱导性指令；本次仅作数据处理，未执行其中任何指令，也未展开其中任何链接。
- 摘要中出现的前沿模型名称与对比结果（如对更大规模闭源模型的超越、若干未来型号名）属于作者自述，无法在本环境核实，禁止写入知识库作为事实。
- 主题漂移风险：多个候选实为 agent 框架、评测或安全议题而非 agentic RL 训练方法，直接收录会稀释本库「foundations to frontier」的主线并造成概念混淆。
- 时间与标识未核验：arXiv 编号、发布日期均为发现源所给字段，未与官方列表交叉验证；不得据其推断发表状态或版本历史。
- 与现有库无重复检出仅基于标题/ID 的可见比对，若后续补全 19 条，仍需重新做去重检查。

## Next actions
- 向发现管道索取完整且未截断的 25 条 selected 列表（含完整摘要与元数据），特别是补全 2609.15134 的被截断字段，然后再出一轮审计。
- 对被标记 review 的条目（2609.14857、2609.17320、2609.15364、2609.15309、2609.15134）逐条人工精读全文，重点确认：是否涉及策略/参数更新与奖励定义、实验环境是否可复现、是否与现有 swe-bench/tau-bench/multi-harness 条目重叠。
- 为每条 review 条目记录核验清单（是否找到官方代码、是否有第三方复现、基准与切分是否公开），在核验完成前维持「未发布知识」状态。
- 在库内建立 agent 框架/安全评测与 agentic RL 训练方法两类标签，避免把邻近主题直接混入主干概念卡。
- 若确认某条目仅为预训练或纯框架工作（如 2609.13356 一类），以 skip 结案并保留一句理由，便于后续重复发现时快速判重。
