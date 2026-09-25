---
id: mintrl-off-policy-intervention
title: MInTRL：稀疏干预让离策略经验服务在策略 RL
summary: 现有 RLVR 多采用 on-policy 学习，受限于策略自身采样能发现的推理轨迹，难以扩展推理能力；引入外部知识又会带来 off-policy 信息与行为策略不匹配。论文要回答：LLM 能否在 RL 训练中有效吸收外部知识，以及应引入多少 off-policy 信息。
stage: FRONTIER
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 24
minutes: 59
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.12419
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.12419
objectives: [理解 on-policy RLVR 的探索瓶颈与 off-policy 信息引入的权衡, 掌握 MInTRL 的生成–审查–干预半在策略 rollout 机制, 了解 off-policy 干预强度的倒 U 形规律与 2–4% 最佳比例, 评估稀疏局部纠正相比蒸馏与行为策略重要性加权的优势]
tags: [reinforcement-learning, RLVR, on-policy, off-policy, intervention, LLM-reasoning]
sources: [mintrl-off-policy-intervention-can-boost]
related: [privileged-info-opsd-ample-math, retireopd-self-retiring-opd, grpo]
prerequisites: []
---
## 问题与语境

RLVR 已成为 LLM 后训练中提升数学与代码推理的主力手段，其主流实现建立在 on-policy 学习之上：策略只用自己当前采样出的 rollout 做优化。这一设计的好处是彻底回避了行为策略不匹配（behavior-policy mismatch），代价则是把可学习的经验严格限制在「当前策略在有限采样下能自己发现」的范围内。论文引用的近期工作（Chen et al., 2026b; Wu et al., 2025）指出，on-policy RLVR 往往难以发现基模型在有限采样下本就不可达的推理轨迹，因此对推理能力的扩张存在天花板。

自然的补救是引入外部知识——更强教师的纠正、专家前缀、特权上下文等。但一旦把这些信息注入 RL 训练，轨迹就不再由当前策略生成，off-policy 信息随之进入。已有做法大致分两支：一支走监督路线（ReGFT 先构造参考引导轨迹做 SFT 再 RL；ReLIFT 在难例上交替做监督更新；InT、SCoRe 定位并纠正首个错误后用于监督训练），另一支直接把外部引导放进 RL（LUFFY 混合专家演示与 on-policy rollout 并做 policy shaping；Zhang et al., 2026 用上下文提示或专家前缀引导 rollout）。论文指出，后一支普遍依赖 policy-gradient 更新，并常需修改重要性权重、优势或奖励；而混合来源轨迹上的重要性比率会沿序列累积，即使只有少量 token 来自外部，也可能导致训练不稳定。

论文的定位因此不是「再提一个蒸馏或干预方法」，而是把问题重述为一个可调的控制问题：能否在保持轨迹绝大部分 on-policy 的前提下吸收外部知识，以及应当引入多少 off-policy 信息。MInTRL 的答案是「稀疏局部干预 + 回归式 RL 目标」：由评判–干预策略在检测到错误处截断并只生成一小段纠正 token，随后立刻交还控制权；训练时用可验证结果奖励直接回归，不除以行为概率。论文同时给出一个简化的支撑分析，把干预强度与「覆盖度–可学习性」权衡联系起来，并用实验定位最佳 off-policy token 比例。

## 核心主张

论文的核心主张可归纳为四条，覆盖方法有效性、具体增益、干预强度的非单调性、以及对评判模型替换的鲁棒性。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | MInTRL 在数学与代码任务上优于 on-policy RL、蒸馏和干预基线，最高提升 9.44 个百分点 | §1 贡献 / §4.1 表1 | 作者主张 |
| C2 | Qwen3-1.7B 上 MInTRL-Const 数学均分 35.45、代码均分 61.95，较 GRPO/OPD 中更强基线提升 13.61 和 14.12 个百分点 | §4.1 表1 | 作者主张 |
| C3 | 性能随 off-policy 干预强度呈倒 U 形，最佳 off-policy token 比例约为 2–4%，过度干预会低于纯 on-policy 基线 | §5.2 图6 | 作者主张 |
| C4 | 用 DeepSeek-V4-Flash 替换 Qwen3-4B-Instruct-2507 作为评判干预模型后，MInTRL 仍优于 GRPO 和 OPD 基线 | §5.3 / 附录F 表4 | 作者主张 |

需要强调，以上四条在证据表中均被标注为「作者主张」，没有一条被标记为已复现或与共识一致；论文自身也说明 Table 1 的数值取自三基准平均最高的 checkpoint，而非固定步数（最终 checkpoint 结果另见附录 E / 表3）。

最强的是 C2。它指向表1中可逐项核对的数字：Qwen3-1.7B 上 MInTRL-Const 的 AIME25 40.73、AIME26 41.56、HMMT25 24.06、Math Avg. 35.45，以及 LCB 37.85、HE+ 80.81、MBPP+ 67.20、Code Avg. 61.95，且论文声称在每个单项基准上都有提升。这条主张的边界清晰、可被独立复算，且 1.7B 尺度上相对 GRPO（17.74 / 47.01）的差距足够大，不易被噪声解释。

最弱的是 C1 中的「9.44 个百分点」这一全局表述。它是一个跨模型、跨领域、跨基线的汇总极值，论文未在给定摘录中指明该数字对应的具体模型、基准与对手，因此无法据此判断其适用条件；同时它与 C2 的 13.61 / 14.12 pp 在量级上并不一致（后者更大），说明「最高 9.44 pp」很可能来自另一组对照口径。C3 的 2–4% 区间同样需要谨慎：它来自图6的目测峰值，论文只给出「roughly 2–4%」的定性描述，未报告置信区间或重复实验次数，属于趋势可信、具体阈值不宜直接迁移的主张。C4 的方向性结论（仍优于基线）较稳，但论文自己指出「更强的独立评判模型并不稳定地带来更好的下游性能」，并推测更强纠正会引入更大的策略不匹配——这实际上削弱了「换更强评判即可获益」的直觉，读者不应把 C4 读成对评判模型质量的正面结论。

## 机制与方法

MInTRL（Minimal Intervention Reinforcement Learning）是一个半在策略（semi-on-policy）RL 框架，其核心设计是：让当前策略 $\pi_t$ 保持对生成过程的控制权，仅由评判–干预策略 $\pi_{\mathrm{JI}}$ 在检测到错误时注入极少量纠正 token，从而在扩展探索覆盖的同时维持轨迹与当前策略的接近性。

**符号约定**：$x\sim\mathcal{D}$ 为输入提示；$y=(y_1,\ldots,y_T)$ 为响应序列；$r(x,y)$ 为可验证的结果奖励；$c_i$ 为 $\pi_t$ 生成的第 $i$ 个短块；$a_i\in\{\textsc{Keep},\textsc{Revise}\}$ 为评判动作；$e_i$ 为检测到的最早错误 token 位置；$h_i$ 为 $\pi_{\mathrm{JI}}$ 生成的短纠正续写；$\mu_N$ 表示至多 $N$ 个纠正 token 位置的 rollout 分布。$\pi_{\mathrm{JI}}$ 可以是更强的教师模型，也可以是带特权上下文（privileged context）的同一模型。

**算法流程**（Algorithm 1，generate–review–intervene 循环）：
1. $\pi_t$ 按短块增量生成，首块为 $c_1=(y_1,\ldots,y_k)\sim\pi_t(\cdot\mid x)$；
2. 评判器输出 $(a_1,e_1)=\mathcal{J}_{\mathrm{JI}}(x,c_1)$；
3. 若 $a_1=\textsc{Keep}$，整块保留并追加到已接受前缀；
4. 若 $a_1=\textsc{Revise}$，在 $e_1$ 处截断，仅保留 $(y_1,\ldots,y_{e_1-1})$，再由 $\pi_{\mathrm{JI}}$ 生成 $h_1\sim\pi_{\mathrm{JI}}(\cdot\mid x,y_1,\ldots,y_{e_1-1})$，拼接为 $(y_1,\ldots,y_{e_1-1})\|h_1$；
5. 控制权立即交还 $\pi_t$，从新前缀继续生成，重复直至响应完成。

该构造的关键性质是**局部性**：干预只产生一小段纠正 span，轨迹绝大部分仍由 $\pi_t$ 生成，因此 off-policy token 占比很低。

**训练目标的设计取舍**：作者明确不直接蒸馏干预策略，理由是干预的局部纠正"may not always provide reliable supervision"，学习信号采用规则化结果奖励 $r(x,y)$。若直接套用 GRPO 式目标，混合来源轨迹需要行为策略重要性加权，而重要性比率会沿轨迹累积并变得高度不稳定。因此 MInTRL 改用**基于回归的 RL 目标**，直接在带奖励的半在策略轨迹上优化，不除以行为概率。这是方法规避混合策略不稳定性的核心机制。

**适用前提与边界**：(i) 需要存在一个可用的 $\pi_{\mathrm{JI}}$（更强教师或带特权上下文的同模型）；(ii) 干预必须稀疏——§5.2 显示性能随 off-policy token 比例呈倒 U 形，最佳区间约 2–4%，过度干预会低于纯 on-policy 基线；(iii) 干预内容不被视为真值监督，Figure 9 给出错误干预反而破坏原本正确推理的失败案例；(iv) 作者在 §4.1 指出，在相对弱的策略下，有用干预 token 在当前策略下概率极低，会被 MInTRL-Proxy 的策略依赖锚点过度约束，故主实验中 MInTRL-Const 通常更优——这一取舍在自评判设定下发生反转（见实验设置小节）。理论侧，作者将 MInTRL 形式化为对当前策略的稀疏扰动，给出覆盖度–可学习性权衡的简化支撑分析，但该分析为 stylized，非严格收敛保证。

## 实验设置

下表汇总证据表中可确认的实验块。所有数值来自论文 Table 1–4 与 Figure 6；未在摘录中写明的字段标注「未说明」。需注意 Table 1 的数值取自三基准平均最高的 checkpoint，Table 3 为固定最终 checkpoint（500 steps）评估，两者不可直接混用。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| AIME25, AIME26, HMMT25（数学）；LCB, HE+, MBPP+（代码） | Qwen3-1.7B | GRPO, OPD, MENTOR, SFT+GRPO, MInTRL-Proxy | 500 steps（最终 checkpoint） | average score (Avg.) |
| 同上 | Qwen3-4B | GRPO, OPD, MENTOR, SFT+GRPO, MInTRL-Proxy | 500 steps（最终 checkpoint） | average score (Avg.) |
| AIME25, AIME26, HMMT25 | Qwen3-4B-Instruct-2507（自评判干预） | GRPO, OPSD, MInTRL-Proxy | 未说明 | average score (Avg.) |
| AIME25, AIME26, HMMT25（数学）；LCB, HE+, MBPP+（代码） | Qwen3-1.7B 与 Qwen3-4B，DeepSeek-V4-Flash 作评判干预模型 | GRPO | 未说明 | average score (Avg.) |
| AIME25, AIME26, HMMT25（数学）；LCB, HE+, MBPP+（代码） | Qwen3-1.7B 与 Qwen3-4B | GRPO, OPD, MENTOR, SFT+GRPO, MInTRL-Proxy | last checkpoints（500 steps） | average score (Avg.) |

**主结果（Table 1，best checkpoint）**：Qwen3-1.7B 上 MInTRL-Const 数学均分 35.45、代码均分 61.95，较 GRPO 与 OPD 中更强者的提升为 +13.61 pp 与 +14.12 pp；Qwen3-4B 上 MInTRL-Const 为 55.73 与 72.63，提升 +3.02 pp 与 +6.80 pp。逐基准数值（Qwen3-1.7B，MInTRL-Const）：AIME25 40.73、AIME26 41.56、HMMT25 24.06、LCB 37.85、HE+ 80.81、MBPP+ 67.20。Qwen3-4B 对应为 AIME25 65.31、AIME26 64.17、HMMT25 37.71、LCB 54.19、HE+ 87.84、MBPP+ 75.85。

**最终 checkpoint（Table 3，500 steps）**：Qwen3-1.7B MInTRL-Const 数学 35.45 / 代码 61.95；Qwen3-4B 数学 55.73 / 代码 72.52。作者称 MInTRL 在此固定 checkpoint 评估下仍具竞争力。

**自评判干预（Table 2）**：Qwen3-4B-Instruct-2507 同时充当两个角色，数学均分 MInTRL-Proxy 52.29 > MInTRL-Const 48.47 > GRPO 47.26 > OPSD 45.03。此处 MInTRL-Proxy 反超 MInTRL-Const，与 Table 4 的趋势相反。

**评判模型鲁棒性（Table 4，DeepSeek-V4-Flash）**：Qwen3-1.7B 上 MInTRL-Proxy 数学 36.84 / 代码 53.42，MInTRL-Const 34.76 / 52.95，GRPO 17.74 / 47.01；Qwen3-4B 上 MInTRL-Proxy 52.88 / 72.59，MInTRL-Const 53.68 / 66.46，GRPO 52.71 / 65.83。

**off-policy 强度（Figure 6 / §5.2）**：通过改变最大评判次数与最大干预续写长度控制 off-policy token 比例，性能呈非单调倒 U 形，最佳约在 2–4%，过度干预低于纯 on-policy 基线（0% 干预条件为同目标、同设置的纯 on-policy 对照）。

**未说明项**：Table 2 与 Table 4 的对应实验未在摘录中给出训练步数或预算；Table 4 中 DeepSeek-V4-Flash 自身作为独立模型的分数行（数学 51.32、代码 73.70）在表中单独列出，不属被训练策略。所有上述结论均为作者主张，本档案未记录独立复现。

## 证据与结果

主结果（Table 1，取三基准平均最高的 checkpoint）如下。表中数值均照抄摘录，未给出的单元格写「摘录未给出」。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| AIME25 | 40.73 | Qwen3-1.7B, MInTRL-Const | Table 1 |
| AIME26 | 41.56 | Qwen3-1.7B, MInTRL-Const | Table 1 |
| HMMT25 | 24.06 | Qwen3-1.7B, MInTRL-Const | Table 1 |
| Math Avg. | 35.45 | Qwen3-1.7B, MInTRL-Const | Table 1 |
| LCB | 37.85 | Qwen3-1.7B, MInTRL-Const | Table 1 |
| HE+ | 80.81 | Qwen3-1.7B, MInTRL-Const | Table 1 |
| MBPP+ | 67.20 | Qwen3-1.7B, MInTRL-Const | Table 1 |
| Code Avg. | 61.95 | Qwen3-1.7B, MInTRL-Const | Table 1 |
| AIME25 | 65.31 | Qwen3-4B, MInTRL-Const | Table 1 |
| AIME26 | 64.17 | Qwen3-4B, MInTRL-Const | Table 1 |
| HMMT25 | 37.71 | Qwen3-4B, MInTRL-Const | Table 1 |
| Math Avg. | 55.73 | Qwen3-4B, MInTRL-Const | Table 1 |
| LCB | 54.19 | Qwen3-4B, MInTRL-Const | Table 1 |
| HE+ | 87.84 | Qwen3-4B, MInTRL-Const | Table 1 |
| MBPP+ | 75.85 | Qwen3-4B, MInTRL-Const | Table 1 |
| Code Avg. | 72.63 | Qwen3-4B, MInTRL-Const | Table 1 |

对照基线（摘录给出的部分）：Qwen3-1.7B 上 GRPO 数学 17.74 / 代码 47.01，OPD 数学 21.84 / 代码 47.83；Qwen3-4B 上 GRPO 数学 52.71 / 代码 65.83，OPD 数学 40.52 / 代码 58.80。作者据此报告 1.7B 上相对 GRPO/OPD 中更强者的增益为 +13.61 pp（数学）与 +14.12 pp（代码），4B 上为 +3.02 pp 与 +6.80 pp。注意 4B 上 MENTOR 数学 55.35、代码 71.80，与 MInTRL-Const 的 55.73 / 72.63 差距很小，而摘要式主张「最高提升 9.44 个百分点」的对照对象在摘录中未明确指向。

消融与对照：
- 自评判干预（Table 2，Qwen3-4B-Instruct-2507 同模型 + 特权上下文）：MInTRL-Proxy 52.29 > MInTRL-Const 48.47 > GRPO 47.26 > OPSD 45.03，趋势与 Table 4 相反。
- 干预强度（Figure 6 / §5.2）：性能随 off-policy token 比例呈倒 U 形，峰值约 2–4%，过度干预低于纯 on-policy 基线。
- 更换评判模型（Table 4，DeepSeek-V4-Flash）：1.7B 上 MInTRL-Proxy 数学 36.84 / 代码 53.42，MInTRL-Const 34.76 / 52.95，GRPO 17.74 / 47.01；4B 上 MInTRL-Proxy 52.88 / 72.59，MInTRL-Const 53.68 / 66.46，GRPO 52.71 / 65.83。
- 末次 checkpoint（Table 3，500 步）：1.7B MInTRL-Const 35.45 / 61.95；4B 55.73 / 72.52。

## 证据强度评估

证据分级：B（单一来源、内部一致但缺乏独立复现）。

理由：证据全部来自论文自身的 Table 1–4、Figure 6 与附录，覆盖两个模型规模、两个域、六项基准、四类基线（on-policy RL、蒸馏、教师引导、干预式），并包含自评判、干预强度、评判模型替换、末次 checkpoint 四组消融，内部一致性较好（如 1.7B 的 35.45/61.95 在 Table 1 与 Table 3 中一致）。但没有任何第三方复现，且作者自述未复现 Xu et al. (2026) 的对照数字，说明外部可比性未经检验。故定为 B 而非 A。

主要威胁：

1. 构造效度：核心机制是「少量 off-policy token」，但干预强度由「最大审查次数」与「最大续写长度」两个超参间接控制，摘录未给出这两个超参的具体取值，也未给出 2–4% 这一最优区间的置信区间或多次运行方差。倒 U 形结论可能对超参网格敏感。

2. 基线选择与对照公平性：4B 上 MInTRL-Const（55.73/72.63）与 MENTOR（55.35/71.80）差距在 1 pp 量级，而「最高提升 9.44 pp」的对照对象在摘录中未指明；若最强竞争者实为 MENTOR，则 4B 上的增益叙述会被显著削弱。此外 MInTRL-Proxy 在主实验中反而弱于 MInTRL-Const，作者以「弱策略下干预 token 概率过低」解释，属事后假设，未做直接验证。

3. 外部效度：仅 Qwen3-1.7B / Qwen3-4B 两个同族模型，评判模型仅 Qwen3-4B-Instruct-2507 与 DeepSeek-V4-Flash 两种；且更换更强评判并未稳定提升下游表现，说明方法对评判模型质量不单调依赖，迁移到其他模型族或更大规模时增益是否保持未知。

4. 统计显著性与评测污染：摘录未报告任何方差、种子数或显著性检验；AIME/HMMT 类基准题量小，单点差异易受采样噪声影响。同时未说明是否对评测集做过去污染处理，存在潜在污染风险。

## 边界与反例

**什么观察会推翻结论。** 核心主张 C1/C2 是「稀疏干预优于纯 on-policy RL 与蒸馏」。若在同等算力预算下（而非同等 step 数）比较，MInTRL 的每步 rollout 需额外调用 $\pi_{\mathrm{JI}}$ 做逐块审查与纠正生成，其 wall-clock 成本高于 GRPO；论文仅在 Appendix G 声明做了效率分析，但证据表中未给出任何具体数字，因此「500 steps 下更优」不能直接换算为「单位算力下更优」。若按 token 数或 GPU 小时对齐后优势消失，结论的实用价值即被削弱。

**最可能失效的条件。** 第一，干预强度越界：作者自述性能随 off-policy token 比例呈倒 U 形，峰值在约 2–4%，过度干预会低于纯 on-policy 基线（C3，作者主张，仅 Figure 6 单图支撑，无跨模型重复）。第二，评判者质量与策略不匹配：Table 4 显示换成更强的 DeepSeek-V4-Flash 后，Qwen3-4B 上 MInTRL-Const 数学 53.68、代码 66.46，反而低于 Qwen3-4B-Instruct-2507 作评判时的 55.73 / 72.63，说明「更强评判者」不保证更好下游表现。第三，锚定方式与策略强度的耦合：Table 2 中 MInTRL-Proxy（52.29）反超 MInTRL-Const（48.47），与 Table 4 趋势相反，作者归因于强基座策略下干预 token 概率不再极低。这意味着 Const/Proxy 的选择依赖基座强度，读者若把某一档的结论外推到另一档会出错。

**反例与未验证方向。** Figure 9 给出明确反例：学生已自行改正符号错误得到 $f'(1)=-1$，评判者却以错误符号驳回，学生服从后输出错误答案 1——即干预本身可能成为错误监督源。作者未验证但易被误推的方向包括：(a) 把「2–4% 最优」当作跨模型、跨任务的普适常数，论文只给出该区间且未报告置信区间或多种子方差；(b) 把 MInTRL 视为可替代蒸馏的通用知识注入手段，但作者明确不蒸馏干预策略、只用规则结果奖励，因此对无可靠 verifier 的任务（如开放式写作）该框架缺乏学习信号；(c) 把 Table 1 的 +13.61/+14.12 pp 当作方法本身的增益，而 1.7B 上 GRPO 仅 17.74，基线偏低会放大相对提升。

## 与知识库的关系

**与「RLVR 与 on-policy RL 的探索瓶颈」的关系（印证并扩展）。** 论文复述了 on-policy RLVR 难以发现基模型有限采样外轨迹的观点，并把它作为问题动机。新增的是解法方向：不靠更大采样预算，而靠在 rollout 中途注入稀疏局部纠正来扩展支撑集。可链接笔记：`rlvr-onpolicy-exploration-bottleneck`。

**与「知识蒸馏与 on-policy distillation (GKD/OPSD)」的关系（新增半在策略框架）。** 既有笔记把 GKD/OPSD 归为「学生轨迹 + 教师逐前缀监督」的分布匹配范式。本文新增一条中间路线：不蒸馏 $\pi_{\mathrm{JI}}$，只用规则结果奖励做回归式 RL，且不除以行为概率。张力点在于 Table 2 的 OPSD 对照——OPSD 45.03 低于 MInTRL-Proxy 52.29，但该对照仅在 Qwen3-4B-Instruct-2507 自评判设定下成立，不能推广为「OPSD 普遍弱于 MInTRL」。可链接笔记：`on-policy-distillation-gkd-opsd`。

**与「从 off-policy 经验学习 (ReGFT, ReLIFT, InT, SCoRe, LUFFY)」的关系（新增在线稀疏纠正 + 序列级优势回归）。** 既有笔记中 InT/SCoRe 定位首个错误并用于监督式训练，LUFFY 用策略塑形处理 off-policy 轨迹。本文的差异是：纠正在在线 rollout 生成过程中发生、控制权立即交还 $\pi_t$、且不做行为策略重要性加权。可链接笔记：`off-policy-experience-learning`。

**与「RLVR 覆盖度-可学习性权衡」的关系（提供简化支撑分析）。** 本文给出稀疏最优纠正下的支撑集分析，与经典覆盖条件相关；但作者自述为 stylized analysis，且倒 U 形仅有 Figure 6 一条经验曲线支撑，属于「理论提示 + 单点经验」而非已复现共识。可链接笔记：`rlvr-coverage-learnability-tradeoff`。

## 复现与验证计划

目标：在最小成本下验证「稀疏局部干预 + 回归式 RL 目标」是否真能带来超出 GRPO 的增益，以及倒 U 形干预强度曲线是否可复现。

环境与任务。策略取 Qwen3-1.7B（若算力允许再加 Qwen3-4B）。数学评测用 AIME25、AIME26、HMMT25，代码用 LCB、HE+、MBPP+，指标为各域平均分（Avg.）。评判–干预模型按论文主设置用 Qwen3-4B-Instruct-2507；若不可得，退化为 self judge-intervention（π_JI = π_0 + 特权上下文），但需注意此时论文中 MInTRL-Proxy 反超 MInTRL-Const（52.29 vs 48.47），结论方向会变。

基线与预算。至少跑 GRPO 与 OPD 两条基线，外加 MInTRL-Const。预算对齐论文的 500 步，并同时记录 best checkpoint 与 final checkpoint（论文 Table 1 用 best，Table 3 用 final，两者数值不同，例如 Qwen3-4B 代码均分 72.63 vs 72.52），避免用不同 checkpoint 规则做不公平比较。

判据。主判据：MInTRL-Const 在数学与代码均分上均不低于 GRPO/OPD 中较强者。论文报告 Qwen3-1.7B 上为 35.45 / 61.95，较更强基线 +13.61 pp 与 +14.12 pp；Qwen3-4B 上为 55.73 / 72.63，+3.02 pp 与 +6.80 pp。注意这些是作者主张，未在本计划中独立复现。次判据：扫描干预强度（最大审查次数、最大纠正续写长度），确认 off-policy token 比例在约 2–4% 处出现峰值，且过度干预低于纯 on-policy 基线。

预期失败模式：(1) 干预 token 在当前策略下概率极低，导致 MInTRL-Proxy 的锚点约束过强而弱于 MInTRL-Const；(2) 错误干预把已正确的推理带偏（论文 Figure 9 的符号错误案例）；(3) 换用更强评判模型（DeepSeek-V4-Flash）不必然提升下游表现，反而可能因策略错配加剧而变差。

## 术语与记号

MInTRL 属半 on-policy RL 框架：轨迹默认由当前策略生成，评判–干预策略仅在检测到错误处插入一小段纠正 token，随后立即交还控制权。训练用回归式 RL 目标，直接对带可验证结果奖励的轨迹回归，不做行为策略重要性加权，以规避混合来源轨迹中重要性比率累积的不稳定。

| 术语 | 含义 |
| --- | --- |
| RLVR | 带可验证奖励的强化学习，用自动可验证的结果奖励训练 LLM 推理 |
| on-policy learning | 仅用当前策略自身采样轨迹进行优化 |
| off-policy information | 非当前策略生成的外部经验或纠正信息 |
| semi-on-policy rollout | 大部分由当前策略生成、仅少量 token 来自干预策略的轨迹 |
| judge–intervention policy | 评判并局部纠正当前策略输出的策略，可为更强教师或带特权上下文的同模型 |
| regression-based RL objective | 直接对带奖励轨迹做回归、不做行为策略重要性加权的 RL 目标 |
| coverage–learnability trade-off | 稀疏干预扩大成功轨迹覆盖，但过度干预使轨迹超出当前策略可学习范围的权衡 |
| off-policy intensity | 轨迹中由干预策略生成的 token 比例，用于控制 off-policy 信息量 |
| privileged context | 评判干预模型可见、而当前策略生成时不可见的额外上下文 |
| Pass@k | 采样 k 次中至少一次正确的评估指标 |

记号：$\pi_t$ 为第 $t$ 次迭代的当前策略；$\pi_{\mathrm{JI}}$ 为评判–干预策略；$x$ 为输入提示；$y=(y_1,\dots,y_T)$ 为响应序列；$r(x,y)$ 为可验证结果奖励；$c_i$ 为 $\pi_t$ 生成的第 $i$ 个短块；$a_i\in\{\textsc{Keep},\textsc{Revise}\}$ 为评判动作；$e_i$ 为检测到的最早错误 token 位置；$h_i$ 为 $\pi_{\mathrm{JI}}$ 生成的短纠正续写；$\mu_N$ 为至多 $N$ 个纠正 token 位置的 rollout 分布。变体命名：MInTRL-Const 使用常数锚点，MInTRL-Proxy 使用依赖策略的锚点。

## 自测

以下问题用于检验你是否真正读懂了 MInTRL 的证据边界，而非仅记住结论。答案中标注了「作者主张」与「已复现/共识」的区分。

**Q1（数字核对）** 论文声称 MInTRL 相对最强竞争者最高提升 9.44 个百分点。请指出该数字出现在哪类表述中，并说明它与 Qwen3-1.7B 上「+13.61 pp / +14.12 pp」的关系。

<details><summary>答案</summary>
9.44 pp 出现在 §1 贡献与摘要式表述中（「outperforms ... by up to 9.44 percentage points over the strongest competitor」），属于作者主张，未给出对应的具体基准与基线组合。而 +13.61 pp（数学）与 +14.12 pp（代码）是 §4.1 表1 中 Qwen3-1.7B 上 MInTRL-Const 相对「GRPO 与 OPD 中更强者的平均分」的差值（35.45 vs 21.84；61.95 vs 47.83）。两者口径不同：前者是跨全部设置的「最高」单点提升，后者是特定模型尺度下的平均分差，不能互相替代引用。
</details>

**Q2（跨小节推理）** 表1 中 Qwen3-4B 上 MENTOR 的数学均分（55.35）高于 MInTRL-Proxy（51.18），但论文仍称 MInTRL「best overall」。请结合表1 与附录 E 表3 判断这一说法在何种口径下成立。

<details><summary>答案</summary>
在表1 的「三基准平均最高 checkpoint」口径下，Qwen3-4B 数学上 MENTOR（55.35）确实高于 MInTRL-Proxy（51.18），但 MInTRL-Const（55.73）略高于 MENTOR；代码上 MInTRL-Const（72.63）也高于 MENTOR（71.80）。因此「best overall」成立的前提是取 MInTRL-Const 而非 Proxy，且需同时看数学与代码两个域。附录 E 表3（固定 500 步末次 checkpoint）中，Qwen3-4B 上 MENTOR 数学 55.21、代码 71.80，MInTRL-Const 数学 55.73、代码 72.52，结论方向一致。注意这是作者主张，且 MInTRL-Proxy 在 4B 数学上并不占优。
</details>

**Q3（机制理解）** 为什么 MInTRL 使用基于回归的 RL 目标，而不是直接对干预策略做蒸馏？请从「干预可靠性」与「重要性比率」两个角度回答。

<details><summary>答案</summary>
两个理由。其一，干预只用于引导生成，其局部纠正「may not always provide reliable supervision」（§2.2），因此用规则化结果奖励而非蒸馏干预内容；附录 D 图9 给出反例：评判误判学生的正确修正并给出错误符号，学生跟随错误干预输出错误答案。其二，半 on-policy 轨迹是混合来源，若用 GRPO 式目标需做行为策略重要性加权，而「importance ratios can accumulate across the trajectory and become highly unstable」（§2.2），即使干预只影响少量 token。回归式目标直接对带奖励轨迹学习，不除以行为概率。
</details>

**Q4（跨小节推理）** 表2（self judge-intervention）中 MInTRL-Proxy（52.29）反超 MInTRL-Const（48.47），而表4（DeepSeek-V4-Flash 评判）中 Qwen3-4B 上 MInTRL-Const（53.68）反超 MInTRL-Proxy（52.88）。作者如何解释这一方向相反的现象？该解释属于哪类证据？

<details><summary>答案</summary>
作者给出两种互补解释，均为作者主张（假设性）。表2 中基座是 Qwen3-4B-Instruct-2507，本身较强，已对许多干预 token 赋予合理概率，因此「relaxing their reference probabilities with the constant anchor becomes less necessary」，保留原策略概率反而是更稳定的正则，故 Proxy 占优。表4 中 1.7B 等较弱策略下，有用干预 token 在当前策略下概率极低，被 policy-dependent anchor 过度约束，故 Const 更优（§4.1 对 Proxy 落后于 Const 的解释）。此外 §5.3 指出更强评判（DeepSeek-V4-Flash）可能产生在当前策略下概率更低的 token，带来更大策略不匹配，因此更强评判不必然带来更好下游表现。这些均为假设，论文未做受控验证。
</details>

**Q5（可迁移性判断）** 若你想把「2–4% off-policy token 比例」直接搬到自己的 RLVR 流程，需要额外确认哪些前提？请至少指出两点证据表/摘录中未覆盖的内容。

<details><summary>答案</summary>
该 2–4% 来自 §5.2 图6，是作者主张，且是在「改变最大评判次数与最大干预续写长度」这一特定参数化下、对训练平均的 Pass@1 提升相对无干预基线测得的。迁移前需确认：(1) 该比例是否随模型尺度、任务域（数学 vs 代码）与基座强度变化——论文只给出倒 U 形趋势，未给出跨尺度的最优比例表；(2) 干预强度由两个超参耦合控制，2–4% 是结果而非可直接设定的旋钮，需重新标定；(3) 评判模型质量与策略不匹配的交互（§5.3）会改变可学习性，换评判模型后最优比例可能移动；(4) 论文未报告该比例下的方差、多种子稳定性与统计显著性。以上均属证据表未覆盖处，应显式标注不确定。
</details>
