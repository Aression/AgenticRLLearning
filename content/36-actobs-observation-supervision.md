---
id: actobs-observation-supervision
title: 观测监督如何改变 RL 下的 Agent 探索
summary: 标准 agent 轨迹 SFT 只对 agent 动作计算损失，环境观测虽在上下文中却被掩码排除。论文检验这一惯例：当 SFT 只是后续 RL 的初始化时，把观测也作为预测目标是否会改变策略的探索行为与下游 RL 表现。
stage: FRONTIER
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 36
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.20715
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 6
full_text_url: https://arxiv.org/html/2609.20715
objectives: [理解 ActObs 如何仅通过修改 SFT 损失掩码把环境观测纳入预测目标, 掌握观测监督对 GRPO 探索动态与 pass@k 曲线的影响机制, 辨析动作与观测梯度冲突、熵保持与策略收缩之间的关系, 评估该方法在 Terminal-Bench 与 aider-polyglot 上的收益与局限]
tags: [observation-supervision, agent-exploration, grpo, sft-initialization, pass-at-k, entropy]
sources: [don-t-mask-the-environment-observation-s]
related: [grpo, multi-turn-rl, lab-agent-rl]
prerequisites: []
---
## 问题与语境

语言 agent 的一条轨迹同时包含两类对齐的监督信号：专家发出的动作 $a_t$，以及环境在动作之后返回的观测 $o_t$。标准轨迹 SFT 只对动作 token 计算损失，观测 token 虽留在上下文中却被掩码排除在预测目标之外（Zeng et al., 2024; Chen et al., 2023; Chen et al., 2024）。论文把这一惯例当作待检验的假设而非既定事实：掩蔽观测隐含地承认「读取环境反馈有用」，但否认「学习预测环境反馈有用」。这一假设在 SFT 只是 RL 初始化时尤其缺乏检验。

失效点在于梯度几何。论文的测量显示，动作梯度与观测梯度的余弦相似度 $c$ 从预训练检查点的 0.83 在 10–20 个 SFT 步内跌到噪声底，此后观测梯度几乎完全落在动作梯度的正交方向上。仅动作的 SFT 无法提供这个正交方向，于是 $g_{\mathrm{act}}$ 被拟合得很小、未被拟合的 $g_{\mathrm{obs}}$ 仍然很大，范数比 $r$ 升到约 41；其后果是模型对终端反馈的预测能力退化到基座模型之下。换言之，ActionSFT 在动作损失上近乎驻定，却在一个正交方向上仍然陡峭，把 SFT 终点推到一个单边特化的区域，再交给 GRPO 去精修。

论文的定位因此不是「多监督一点更好」的增量主张，而是把 SFT 目标函数视为决定 RL 探索动力学的变量：只改损失掩码，不改数据、参数、序列长度、前向次数与 RL 算法，就能改变 GRPO 的策略位移量与保留熵。它同时与两条既有线索对话——RLVR 可能通过集中概率于奖励路径而提升 pass@1、却缩小大 $k$ 下可解问题集合（Yue et al., 2025; Wu et al., 2025），以及预测式世界模型用「动作到后果」的建模塑造动作表示（Lin et al., 2024; Guo et al., 2025; Zhang et al., 2025）——但把后者压缩为一次掩码改动，无需额外模型或 RL 改动。

## 核心主张

论文的核心主张可归纳为：在 SFT 阶段把轨迹中已存在的观测 token 纳入语言建模损失（ActObs），几乎不改变 SFT 后的基准表现，却显著改变同一 GRPO 过程的结果——策略位移更小、保留熵更高、大采样预算下的 pass@$k$ 更强。机制解释是联合监督阻止了动作/观测梯度的单边特化，从而保住了环境后果建模能力。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | SFT 后三种初始化性能相近，但同一 GRPO 后 ActObs 在 4B 每个采样预算上最强，pass@1 相对提升 29% | §3.1 表 1；§3.2；表 1（4B：ActObs → GRPO 7.2 ± 0.4 vs ActionSFT → GRPO 5.6 ± 0.4） | 作者主张 |
| C2 | 8B 上 ActObs 牺牲部分单次可靠性（pass@1 11.0 vs 12.3），pass@16 相对提升 14%，解出 24 个任务而非 21 个 | §3.2；表 1；§3.2 任务覆盖 24 vs 21 | 作者主张 |
| C3 | 跨域 aider-polyglot 上 4B ActObs GRPO 比 ActionSFT GRPO 在 pass@1 高 43%、pass@4 高 24%，且 RL 前 ActObs 检查点更弱 | §3.3；表 1（13.9 ± 0.7 vs 9.7 ± 0.6；25.3 ± 1.0 vs 20.4 ± 0.9） | 作者主张 |
| C4 | 动作与观测梯度在 10–20 步内趋于正交（$c$ 从 0.83 落到噪声底），ActionSFT 的 $r$ 升到约 41、观测预测低于基座，ActObs 的 $r$ 保持近 0.5 | §5.1 图 5(a)(b)；§5.2 图 6(b,c) | 作者主张 |
| C5 | 高熵本身不充分：ECHO 端点熵最高（8B 0.804）但在 pass@16 不敌 ActObs → GRPO；把 ActionSFT → GRPO 温度提到 $T^*=0.64$ 匹配自熵，pass@1/4/8/16 变化至多 0.7 点、未多解出任务、pass@16 差距仍在 | §4.2；表 7；§4.2 | 作者主张 |
| C6 | 时序对照 Obs → Act 拿到同等观测监督却不兑现收益，pass@16 落后 ActObs 2.2 点（4B）与 3.4 点（8B） | §3.2；消融列表 | 作者主张 |

最强的是 C4 与 C5 的组合：它们不是单点分数，而是可独立测量的中间量（梯度余弦相似度、范数比、端点 KL、自熵、温度匹配对照），且温度匹配这一对照直接排除了「只是采样更随机」的替代解释，使「分布本身变了」这一因果链更难被绕过。相对最弱的是 C2：8B 上 pass@1 方向反转（11.0 vs 12.3），优势只在 pass@4 之后出现且 pass@4 仅 0.6 点、3% 相对差距，落在 bootstrap 标准误量级附近；作者自己也在 limits 中承认这是「牺牲单次可靠性换大预算覆盖」，因此该条更像规模相关的条件性结论，而非稳健增益。C6 的对照设计有力，但只报告了 pass@16 一个口径的差距，缺少完整曲线，强度次之。需注意全部六条均为作者主张，本档案未获得独立复现证据；表 1 的不确定性为固定任务集、在任务内重采样尝试得到的单倍 bootstrap 标准误，跨任务泛化不在该误差范围内。

## 机制与方法

ActObs 的核心主张是：标准 agent 轨迹 SFT 只对 agent 动作计算损失、把环境观测掩码排除，这一惯例在「SFT 只是 RL 初始化」的设定下值得质疑。ActObs 仅修改 SFT 损失掩码，把轨迹中**已经存在**的观测 token 也纳入语言建模损失，不增加数据、参数、序列 token、前向传播次数，也不改动 RL 算法。

记第 $t$ 步之前的轨迹上下文为 $h_t$，agent 动作为 $a_t$，环境返回的观测 token 序列为 $o_t$。标准 ActionSFT 在动作位置优化 $p_\theta(a_t \mid h_t)$；ActObs 额外在观测位置优化

$$p_\theta(o_t \mid h_t, a_t)$$

即模型必须表示「前一个动作对当前环境做了什么」。两条目标共享同一组参数，因此每条轨迹同时充当模仿样本与状态转移样本。观测损失权重记为 $\lambda$：$\lambda=0$ 退化为仅动作 SFT，$\lambda=1$ 为默认 ActObs。作者给出的直觉是，学习动作到后果的关系可以塑造用于选择后续动作的表示，这与预测式世界模型方法的动机一致，但实现上只是一个损失掩码改动。

机制层面的诊断量有两个。设 $g_{\mathrm{act}}$、$g_{\mathrm{obs}}$ 分别为动作 token 与观测 token 的梯度，定义余弦相似度 $c=\cos(g_{\mathrm{obs}}, g_{\mathrm{act}})$ 与范数比 $r=\lVert g_{\mathrm{obs}}\rVert/\lVert g_{\mathrm{act}}\rVert$。作者给出分解

$$g_{\mathrm{obs}}=r\lVert g_{\mathrm{act}}\rVert\left(c\,\hat{g}_{\mathrm{act}}+\sqrt{1-c^{2}}\,\hat{g}_{\mathrm{act}}^{\perp}\right)$$

其中 $\hat{g}_{\mathrm{act}}$ 是动作梯度方向的单位向量，$\hat{g}_{\mathrm{act}}^{\perp}$ 是观测梯度正交分量的单位向量。当 $c\approx 0$ 时平行分量消失，$r$ 直接近似正交观测分量相对动作梯度的规模。作者报告：在预训练检查点上 $c$ 初始为 0.83，10–20 个 SFT 步内降到噪声底并保持；ActionSFT 下 $r$ 升到约 41（动作梯度变小而未被拟合的观测梯度仍大），ActObs 下 $r$ 全程保持在 0.5 附近。据此作者主张：动作与观测梯度很快趋于正交后，仅动作训练无法提供正交方向上的更新，会单边特化并侵蚀环境预测能力；联合监督保持两个目标平衡，从而给 GRPO 一个不同、且保留更高熵、移动更小的初始化。

设计取舍与适用前提需要显式标注。其一，观测损失**无法直接约束标准 GRPO**，因为它不在 RL 目标里，其效果只能通过交给 GRPO 的 SFT 检查点传递——这是作者自陈的限制。其二，时序对照 Obs → Act（先仅观测 SFT 再仅动作 SFT）接受了同等观测监督却未获得收益，作者据此认为需要的是**联合**动作-观测学习，而非单纯暴露观测。其三，$\lambda$ 扫描显示这是权衡而非一致提升：随 $\lambda$ 增大，post-GRPO 的 pass@8 相对优势单调增长，而 pass@1 反向移动。其四，高熵本身不充分：ECHO 产生最高端点熵，却在 pass@16 上不及 ActObs → GRPO。以上均为作者主张，尚未见独立复现。

## 实验设置

主实验在两个基准上进行：Terminal-Bench 2.0（89 个任务，每任务 16 次尝试）与 aider-polyglot（225 个多语言代码编辑任务，每任务四次尝试）。模型为 Qwen3-4B 与 Qwen3-8B。对照的 SFT 初始化包括 Base、ActionSFT、ActObs、Obs → Act；RL 方法包括 GRPO 与 ECHO（GRPO + 下一观测预测损失）。不确定性报告为 one bootstrap standard error，固定任务集、在任务内重采样尝试。aider-polyglot 的 225 个任务不出现在终端 SFT 语料或 Endless Terminals RL 集合中，因此被作者用作跨域评测。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
| --- | --- | --- | --- | --- |
| Terminal-Bench 2.0 | Qwen3-4B | ActionSFT → GRPO | 16 attempts per task | pass@1 / pass@4 / pass@8 / pass@16 |
| Terminal-Bench 2.0 | Qwen3-8B | ActionSFT → GRPO | 16 attempts per task | pass@1 / pass@4 / pass@8 / pass@16 |
| aider-polyglot | Qwen3-4B | ActionSFT → GRPO | four attempts per task | pass@1 / pass@4 |
| aider-polyglot | Qwen3-8B | ActionSFT → GRPO | four attempts per task | pass@1 / pass@4 |
| Terminal-Bench 2.0 | Qwen3-4B | ActionSFT → ECHO | 16 attempts per task | pass@4 至 pass@16 |
| Terminal-Bench 2.0 | Qwen3-8B | ActionSFT → ECHO | 16 attempts per task | 至 pass@8 |
| Terminal-Bench 2.0 | Qwen3-8B | ActionSFT | doubled agent wall-clock budget, four attempts per task | pass@1 |

补充设置：SFT 阶段共 781 步，梯度诊断在 256 条 held-out 轨迹上分别计算动作与观测梯度；KL 与 self-entropy 探针使用 200 条共享 Terminal-Bench 2.0 轨迹；teacher-forced 观测交叉熵使用 Nemotron-Terminal-Corpus 验证划分的 300 条 held-out 轨迹。扩展预算评测将 agent wall-clock 上限翻倍，verifier 超时与服务配置不变，采用每任务四次尝试，与标准预算下的 16 次尝试头条结果对比。温度匹配对照把 ActionSFT → GRPO 的采样温度提高到 $T^{*}=0.64$（原为 0.6）以对齐 ActObs → GRPO 的 self-entropy。上述设置细节均来自作者报告，未标注为已独立复现。

## 证据与结果

核心数字来自 Table 1（Terminal-Bench 2.0：89 任务、每任务 16 次尝试；aider-polyglot：225 任务、每任务 4 次尝试），不确定度为一倍 bootstrap 标准误（固定任务集、任务内重采样尝试）。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| pass@1 | 1.2 ± 0.2 | Qwen3-4B Base, Terminal-Bench 2.0, after SFT | Table 1 |
| pass@1 | 4.5 ± 0.4 | Qwen3-4B ActionSFT, after SFT | Table 1 |
| pass@1 | 4.4 ± 0.4 | Qwen3-4B ActObs, after SFT | Table 1 |
| pass@1 | 4.4 ± 0.4 | Qwen3-4B Obs → Act, after SFT | Table 1 |
| pass@16 | 16.9 ± 1.2 | Qwen3-4B ActionSFT, after SFT | Table 1 |
| pass@16 | 18.0 ± 1.4 | Qwen3-4B ActObs, after SFT | Table 1 |
| pass@1 | 5.6 ± 0.4 | Qwen3-4B ActionSFT → GRPO | Table 1 |
| pass@1 | 7.2 ± 0.4 | Qwen3-4B ActObs → GRPO | Table 1 |
| pass@16 | 18.0 ± 1.4 | Qwen3-4B ActionSFT → GRPO | Table 1 |
| pass@16 | 19.1 ± 1.4 | Qwen3-4B ActObs → GRPO | Table 1 |
| pass@1 | 5.3 ± 0.4 | Qwen3-4B Obs → Act → GRPO | Table 1 |
| pass@16 | 16.9 ± 1.0 | Qwen3-4B Obs → Act → GRPO | Table 1 |
| pass@1 | 9.2 ± 0.5 | Qwen3-8B ActionSFT, after SFT | Table 1 |
| pass@1 | 7.9 ± 0.5 | Qwen3-8B ActObs, after SFT | Table 1 |
| pass@16 | 24.7 ± 1.2 | Qwen3-8B ActionSFT, after SFT | Table 1 |
| pass@16 | 22.5 ± 1.2 | Qwen3-8B ActObs, after SFT | Table 1 |
| pass@1 | 12.3 ± 0.5 | Qwen3-8B ActionSFT → GRPO | Table 1 |
| pass@1 | 11.0 ± 0.5 | Qwen3-8B ActObs → GRPO | Table 1 |
| pass@16 | 23.6 ± 1.2 | Qwen3-8B ActionSFT → GRPO | Table 1 |
| pass@16 | 27.0 ± 1.3 | Qwen3-8B ActObs → GRPO | Table 1 |
| pass@1 | 9.7 ± 0.6 | Qwen3-4B ActionSFT → GRPO, aider-polyglot | Table 1 |
| pass@1 | 13.9 ± 0.7 | Qwen3-4B ActObs → GRPO, aider-polyglot | Table 1 |
| pass@4 | 20.4 ± 0.9 | Qwen3-4B ActionSFT → GRPO, aider-polyglot | Table 1 |
| pass@4 | 25.3 ± 1.0 | Qwen3-4B ActObs → GRPO, aider-polyglot | Table 1 |
| pass@1 | 12.7 ± 0.8 | Qwen3-8B ActionSFT → GRPO, aider-polyglot | Table 1 |
| pass@1 | 14.2 ± 0.8 | Qwen3-8B ActObs → GRPO, aider-polyglot | Table 1 |
| pass@4 | 28.4 ± 1.3 | Qwen3-8B ActionSFT → GRPO, aider-polyglot | Table 1 |
| pass@4 | 28.9 ± 1.2 | Qwen3-8B ActObs → GRPO, aider-polyglot | Table 1 |
| task coverage | 24 | Qwen3-8B ActObs → GRPO | §3.2 |
| task coverage | 21 | Qwen3-8B ActionSFT → GRPO | §3.2 |
| self-entropy | 0.683 / 0.706 | 8B ActionSFT / 8B ActObs | Table 7 |
| self-entropy | 0.716 / 0.779 | 8B ActionSFT → GRPO / 8B ActObs → GRPO | Table 7 |
| self-entropy | 0.794 / 0.804 | 8B ActionSFT → ECHO / 8B ActObs → ECHO | Table 7 |
| cmd margin | 7.00 / 6.56 | 8B ActionSFT / 8B ActObs | Table 7 |
| cmd margin | 7.55 / 7.24 | 8B ActionSFT → GRPO / 8B ActObs → GRPO | Table 7 |
| cosine similarity c | 0.83 | 初始 SFT checkpoint，action vs observation 梯度 | Figure 5(a) |
| norm ratio r | about 41 | ActionSFT SFT | Figure 5(b) |
| norm ratio r | near 0.5 | ActObs SFT | Figure 5(b) |
| pass@1 at 2× budget | 10.1 / 7.9 | 8B ActObs / 8B ActionSFT | Table 8 |
| pass@1 at 2× budget | 12.6 / 14.0 | 8B ActObs → GRPO / 8B ActionSFT → GRPO | Table 8 |
| temperature matching T* | 0.64 instead of 0.6 | ActionSFT → GRPO 熵匹配 ActObs → GRPO | §4.2 |
| temperature matching effect | at most 0.7 points | pass@1/4/8/16，16 次尝试 | §4.2 |
| SFT steps | 781 | 熵曲线在 step 100 of 781 分离 | §5.1 |
| held-out trajectories | 256 | SFT 期间梯度计算 | §5.1 |
| shared traces | 200 | KL 与 self-entropy 探针 | Figure 4(a) |
| held-out trajectories | 300 | teacher-forced observation 交叉熵 | Figure 6(b,c) |

消融与对照：Obs → Act 时序对照在 SFT 后与 ActionSFT/ActObs 相近，但未实现 post-GRPO 收益，pass@16 落后 ActObs 2.2 点（4B）与 3.4 点（8B）；λ 扫描显示随 λ 增大，post-GRPO pass@8 相对优势单调上升而 pass@1 反向移动；ECHO 对照下 ActObs 在八个报告点中的七个领先或持平，仅 8B pass@16 例外；温度匹配（T*=0.64）最多改变 0.7 点、未多解出任务、pass@16 差距保留；2× wall-clock 下四个观测监督 checkpoint 的 pass@1 均上升，ActionSFT 是唯一未受益者（-1.3）。qemu-startup 案例中，获胜轨迹在 900 秒 wall-clock 到期时仍在等待 guest 启动，验证器仍给 1.0（Appendix G.1）。

## 证据强度评估

证据分级：B（内部一致、机制性证据较完整，但外部效度与统计稳健性受限，尚不足以升为 A）。

理由：结论建立在同一套 SFT 数据、同一 GRPO 配方下的多组对照（ActionSFT、ActObs、Obs → Act、ECHO、λ 扫描、温度匹配、2× budget）之上，方向一致且跨两个模型规模与两个基准（Terminal-Bench 2.0、aider-polyglot）复现；机制侧给出梯度几何（c 从 0.83 降到噪声底、r 在 ActionSFT 升至约 41 而在 ActObs 保持 near 0.5）、熵与策略位移的联合排序，属于「作者主张」但内部自洽。然而所有数字均为单一训练/评测运行的点估计，未报告多种子方差或显著性检验，且部分优势幅度接近噪声（如 8B aider-polyglot pass@4 仅 0.5 点领先）。

主要威胁：
1. 统计显著性：不确定度为一倍 bootstrap 标准误（固定任务集、任务内重采样），只覆盖评测采样噪声，不含训练随机性；4B pass@16 的 1.1 点优势与 8B pass@4 的 0.6 点优势均落在 ±1.0–1.4 区间内，无法排除运行间波动。
2. 构造效度：观测损失不在 RL 目标中，其作用只能经由 SFT checkpoint 传递（作者自述），因此「观测监督改变 RL 探索」的因果链是间接的；温度匹配实验虽排除「单纯注入随机性」这一替代解释，但未排除 checkpoint 选择、SFT 步数等混杂。
3. 外部效度：仅两个基准、两个模型规模（4B/8B）、单一 SFT 语料与 RL 环境；aider-polyglot 虽为跨域，但仍是代码编辑任务族，向更异构的 agent 环境（长程、多工具、非文本观测）迁移未验证。
4. 基线选择与评测污染：主基线 ActionSFT 是标准做法，但 Obs → Act 对照与 ECHO 对照的结论依赖具体实现；qemu-startup 案例显示验证器在 900 秒超时后仍给 1.0，提示 pass@k 判定可能存在与「真实完成」不一致的宽松边界，需警惕评测口径对高 k 指标的抬升。

## 边界与反例

**会推翻结论的观察。** 若在相同 SFT 数据、相同 GRPO 配方下，把观测 token 纳入损失后得到的 SFT 检查点在梯度几何上仍出现 $r$ 增长到数十量级（即观测残差未被优化），却依然复现下游 pass@k 优势，则「联合监督防止单边特化」这一机制解释失效。反之，若把 ActionSFT 的观测预测能力人为恢复到基座水平（例如加正则或蒸馏）而不改变损失掩码，却拿不到同等下游收益，则说明起作用的是别的因素而非观测监督本身。作者已用 Obs → Act 时序对照排除了「观测曝光量」这一混淆：该对照获得同等观测监督，SFT 后表现相近，但 pass@16 落后 ActObs 2.2 点（4B）与 3.4 点（8B），说明需要联合学习而非单纯暴露。

**最可能失效的条件。** 其一，模型规模。8B 上 pass@1 反被 ActionSFT 领先（12.3 vs 11.0），优势只在 pass@4 之后出现且逐步扩大（3%、12%、14%）；若读者只关心单次成功率，ActObs 在 8B 是负收益。其二，RL 算法。ECHO 下八个报告点中仅 8B pass@16 一项偏向 ActionSFT，其余 ActObs 领先或持平，领先幅度 1.1–2.2 点（4B）与 1.4–2.1 点（8B），说明观测感知的 RL 会部分吸收该收益。其三，推理预算。2× wall-clock 下四个观测监督检查点 pass@1 均上升（ActObs +2.2），而 ActionSFT 是唯一不获益者（−1.3），提示收益与交互预算耦合。

**作者未验证、读者易误推的方向。** (1) 高熵本身不是充分条件：ECHO 端点熵最高（0.804）却在 pass@16 不及 ActObs → GRPO（0.779）；温度匹配到 $T^*=0.64$ 后 pass@1/4/8/16 变化至多 0.7 点、未多解出任何任务，故不能把结论简化为「加随机性」。(2) 观测损失无法直接约束标准 GRPO，其作用只经由 SFT 检查点传递，不能推断为「RL 目标里加观测项等价」。(3) 论文未验证 λ 扫描在 8B 或跨域上的形状，pass@1→pass@8 的单调权衡是否普遍成立未知。(4) qemu-startup 的获胜轨迹在 900 秒 wall-clock 到期时仍在等待 guest 启动，验证器却判 1.0，提示 pass@k 指标本身可能奖励「阻塞式等待」，读者不应把该案例当作探索质量的正面证据。

## 与知识库的关系

**新增（此前笔记未覆盖）。** 本工作把「SFT 损失掩码」这一实现细节提升为影响下游 RL 探索的变量，并给出机制性证据链：动作与观测梯度余弦相似度 $c$ 从 0.83 在 10–20 步内跌至噪声底，ActionSFT 的范数比 $r$ 升至约 41，ActObs 保持约 0.5；熵曲线在第 100/781 步分离并持续。这为「SFT 作为 RL 初始化」提供了可测量的几何量（$c$、$r$、endpoint KL、self-entropy），是既有笔记中缺失的中间层证据。可链接：`note/sft-as-rl-init`、`note/gradient-geometry-sft`。

**印证。** 与 RLVR 可能通过集中概率于奖励路径而提升 pass@1、却缩小大 $k$ 下可解问题集合的结论一致（Yue et al., 2025; Wu et al., 2025）：本文观测到 ActionSFT → GRPO 在 8B 的 RL 增益随 $k$ 增大转负，而 ActObs 端点位移最小、保留熵最高、pass@16 最强。可链接：`note/rlvr-passk-contraction`、`note/policy-entropy-collapse`。

**张力。** 其一，与「熵越高探索越好」的朴素读法冲突：ECHO 端点熵最高（0.804）却不及 ActObs → GRPO（0.779）的 pass@16，说明熵是必要非充分，需与策略位移联合看。可链接：`note/entropy-exploration-tradeoff`。其二，与预测式世界模型路线（Lin et al., 2024; Guo et al., 2025; Zhang et al., 2025）共享直觉但实现路径相反：本文不引入额外模型或 RL 目标，仅改损失掩码，因此「世界模型收益是否必须来自显式模块」这一笔记假设受到挑战。可链接：`note/predictive-world-model-agent`。其三，与「观测不可训练、只作上下文」的工程惯例直接对立，且 Obs → Act 对照表明时序拆分无法替代联合监督，削弱了「先学读再学做」的课程式直觉。可链接：`note/observation-masking-convention`。

## 复现与验证计划

目标：在最小成本下验证「仅改 SFT 损失掩码（ActObs）→ 同一 GRPO 后 pass@k 提升」这一核心结论，并检验其是否只是熵/随机性效应。

环境与数据。基座 Qwen3-4B（若算力允许再加 Qwen3-8B）。SFT 数据用标准 agent 轨迹（含动作与环境观测 token），RL 用 Terminal-Bench 2.0 训练集；评测集为 Terminal-Bench 2.0（89 任务，每任务 16 次尝试）与 aider-polyglot（225 任务，每任务 4 次尝试）。三组初始化必须共享同一数据、上下文与训练流程：ActionSFT（仅动作损失）、ActObs（动作+观测损失，默认 $\lambda=1$）、Obs → Act（先仅观测 SFT 再仅动作 SFT，作为时序对照）。

预算与判据。SFT 步数对齐论文量级（约 781 步），GRPO 用同一超参与同一采样温度（0.6）。主判据：SFT 后三者在 pass@1 上应相近（论文 4B：ActionSFT 4.5 ± 0.4、ActObs 4.4 ± 0.4、Obs → Act 4.4 ± 0.4），而同一 GRPO 后 ActObs 在 4B 每个采样预算上领先（pass@1 7.2 ± 0.4 vs 5.6 ± 0.4，pass@16 19.1 ± 1.4 vs 18.0 ± 1.4）。关键否证性检验：把 ActionSFT → GRPO 的采样温度升到 $T^*=0.64$ 以匹配 ActObs → GRPO 的 self-entropy，若 pass@k 差距被抹平，则结论退化为「更多随机性」而非分布差异；论文报告该操作改变 pass@1/4/8/16 至多 0.7 点、未多解出任何任务、pass@16 差距仍在。

预期失败模式。其一，8B 上 pass@1 可能反向（论文：ActionSFT 12.3 ± 0.5 领先 ActObs 11.0 ± 0.5），优势只在较大 $k$ 出现，故不能只用 pass@1 判定。其二，Obs → Act 对照可能复现不出收益（论文：pass@16 落后 ActObs 2.2 点@4B、3.4 点@8B），提示需要联合监督而非单纯观测暴露。其三，ECHO 在 8B pass@16 上反超（25.8 ± 1.6 vs 24.7 ± 1.2），说明「熵更高」不等于更好。其四，观测损失不在 RL 目标内，其作用只能经由 SFT 检查点传递，故须固定 RL 算法本身。建议同时记录梯度诊断（$c$ 在 10–20 步内落到噪声底、$r$ 在 ActionSFT 升至约 41 而 ActObs 保持约 0.5）作为机制旁证。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| ActObs | 把轨迹中环境观测 token 也纳入 SFT 损失的训练目标；仅改损失掩码，不加数据、参数、序列 token、前向次数，也不改 RL 算法 |
| ActionSFT | 标准 agent SFT，只对 agent 动作 token 计算损失，观测留在上下文但被掩码 |
| Obs → Act | 时序对照：先做仅观测 SFT 再做仅动作 SFT，用于区分「观测暴露」与「联合监督」 |
| GRPO | 基于组相对优势的策略优化 RL 算法，本文中作为统一的下游 RL 过程 |
| ECHO | 在 GRPO 中加入下一观测预测损失的 RL 变体，用于检验观测感知 RL 是否可替代 ActObs 的 SFT 初始化 |
| pass@k | 每任务采样 $k$ 次至少成功一次的比例；本文报告 $k=1,4,8,16$ |
| self-entropy | 冻结策略在其自身评估 rollout 上的下一 token 平均熵（论文用 200 条自身 rollout） |
| fixed-state entropy | 所有检查点在共享的同一批轨迹上打分得到的熵，用于控制状态访问差异 |
| endpoint KL | 最终 RL 策略相对其 SFT 初始化在固定 200 条轨迹上的平均 KL 位移，度量策略移动量 |
| Terminal-Bench 2.0 | 终端任务评测集，89 个任务，每任务 16 次尝试 |
| aider-polyglot | 多语言代码编辑跨域评测集，225 个任务，每任务 4 次尝试 |

记号。$o_t$ 为第 $t$ 步环境返回的观测 token 序列；$a_t$ 为第 $t$ 步 agent 发出的动作 token 序列；$h_t$ 为第 $t$ 步之前的轨迹上下文。ActObs 在观测位置优化 $p_\theta(o_t \mid h_t, a_t)$，在动作位置优化 $p_\theta(a_t \mid h_t)$，两者共享参数。$\lambda$ 为观测 token 预测损失权重，$\lambda=0$ 退化为仅动作 SFT，$\lambda=1$ 为默认 ActObs。梯度诊断量：$g_{\mathrm{act}}$、$g_{\mathrm{obs}}$ 分别为动作与观测 token 的求和梯度，$c=\cos(g_{\mathrm{obs}}, g_{\mathrm{act}})$ 为余弦相似度，$r=\lVert g_{\mathrm{obs}}\rVert/\lVert g_{\mathrm{act}}\rVert$ 为范数比；分解式 $g_{\mathrm{obs}}=r\lVert g_{\mathrm{act}}\rVert\left(c\hat{g}_{\mathrm{act}}+\sqrt{1-c^{2}}\,\hat{g}_{\mathrm{act}}^{\perp}\right)$ 中 $\hat{g}_{\mathrm{act}}$ 为动作梯度方向单位向量，$\hat{g}_{\mathrm{act}}^{\perp}$ 为观测梯度正交分量方向单位向量。$T^*$ 为温度匹配实验中使 ActionSFT → GRPO 的 self-entropy 对齐 ActObs → GRPO 所需的采样温度（论文为 0.64，默认 0.6）。

## 自测

以下问题用于检验你是否真正掌握了本档案的证据链，而非仅记住结论。跨小节题需要把「SFT 几何」「RL 动态」「下游 pass@k」三处证据串起来。

**Q1（基础）** ActObs 相对标准 ActionSFT 究竟改了什么？请说明它是否增加了数据、参数、序列 token、前向传播，或修改了 RL 算法。

<details><summary>答案</summary>
只改 SFT 损失掩码：把轨迹中已存在的环境观测 token 也纳入语言建模损失，使每个轨迹同时充当模仿样本与状态转移样本。动作位置训练 $p(\text{action}\mid\text{history})$，观测位置训练 $p(\text{observation}\mid\text{history},\text{action})$，两者共享参数。不增加数据、参数、序列 token、前向次数，也不改 RL 算法。注意：观测损失无法直接约束标准 GRPO，因为它在 RL 目标中缺席，其效果只能通过交给 GRPO 的 SFT 检查点传递。
</details>

**Q2（基础）** 在 4B 与 8B 上，ActObs → GRPO 相对 ActionSFT → GRPO 的优势分别出现在哪个采样预算区间？请给出关键数字。

<details><summary>答案</summary>
4B：ActObs 在整个采样曲线上最强，pass@1/4/8/16 分别领先 1.6、1.4、1.5、1.1 个百分点，相对优势 29%、13%、11%、6%。8B：优势出现在更大采样预算，ActionSFT 在 pass@1 领先（12.3 vs 11.0），ActObs 在 pass@4 反超，优势从 pass@4 的 0.6 点增至 pass@8 的 2.6 点、pass@16 的 3.4 点，相对边际 3%、12%、14%；任务覆盖 24 对 21。
</details>

**Q3（跨小节）** 论文用「温度匹配」实验来排除什么替代解释？该实验的结果如何与 §5.1 的梯度诊断相互支持？

<details><summary>答案</summary>
温度匹配排除「高 $k$ 优势只是推理时注入更多随机性」这一解释：把 ActionSFT → GRPO 的采样温度提到 $T^{*}=0.64$ 以匹配 ActObs → GRPO 的 self-entropy，结果 pass@1/4/8/16 变化至多 0.7 点，没有多解出任何任务，pass@16 差距依然存在。与 §5.1 相互支持之处在于：梯度诊断显示 ActionSFT 的 $r$ 升至约 41、观测预测退化到基座模型以下，而 ActObs 的 $r$ 保持约 0.5、保留环境预测；因此差异来自 SFT 学到的分布本身（策略支撑与策略位移），而非推理温度。ECHO 是这条解释的边界：它端点熵最高却不匹配 ActObs → GRPO 的 pass@16，说明高熵本身不充分。
</details>

**Q4（跨小节）** 为什么「Obs → Act」时序对照在 SFT 后与 ActObs 表现相近，却在 GRPO 后无法复现收益？这对「观测监督的作用机制」意味着什么？

<details><summary>答案</summary>
Obs → Act 先做仅观测 SFT 再做仅动作 SFT，接收了同等量的观测监督，但 pass@16 上 ActObs 领先它 2.2 点（4B）与 3.4 点（8B）。这说明收益不来自「观测暴露」本身，而来自动作与观测的联合学习：只有联合监督才能在动作梯度与观测梯度于 10–20 步内趋于正交后，继续沿正交方向降低观测残差，避免单边特化。时序对照在动作阶段仍会留下未被拟合的观测残差，因此无法为 GRPO 提供同样的初始化。
</details>

**Q5（跨小节）** 若你要把该结论迁移到自己的 agent 场景，哪些证据支持迁移、哪些限制要求你谨慎？请至少引用两处不同小节的证据。

<details><summary>答案</summary>
支持迁移：改动成本极低（仅损失掩码，不加数据/参数/前向/RL 改动）；跨域证据显示在 aider-polyglot 的 225 个多语言代码编辑任务上，4B ActObs → GRPO 比 ActionSFT → GRPO 在 pass@1 高 43%、pass@4 高 24%，且 RL 前 ActObs 检查点在该基准上更弱，说明优势不能归因于 RL 前更强；ECHO 实验显示观测感知的 RL 与 ActObs 互补而非替代（八个工作点中七个 ActObs 领先或持平）。谨慎之处：8B 上 pass@1 反而落后（11.0 vs 12.3），收益集中在更大采样预算；λ 扫描显示 pass@1 与 pass@8 存在权衡，观测权重越高越牺牲单次可靠性；ECHO 下 8B pass@16 是唯一不利于 ActObs 的工作点；此外 qemu-startup 的获胜轨迹在 900 秒墙钟到期时仍在等待 guest 启动，验证器却给 1.0 分，提示评测口径本身存在边界情形。
</details>
