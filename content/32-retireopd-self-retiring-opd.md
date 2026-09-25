---
id: retireopd-self-retiring-opd
title: RetireOPD：可自适应退场的在线策略蒸馏
summary: 在带可验证奖励的强化学习（RLVR）训练多轮 LLM 智能体时，轨迹级奖励稀疏，中间决策缺乏监督；在线策略蒸馏（OPD）用带特权上下文（如检索到的技能）的教师提供密集 token 级监督。但现有方法默认教师可靠、且蒸馏应持续全程，用固定调度决定何时停止蒸馏。
stage: FRONTIER
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 32
minutes: 58
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.20784
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.20784
objectives: [理解特权上下文教师为何未必可靠，以及师生差异先缩小后扩大的阶段性规律, 掌握 RetireOPD 三阶段机制：技能条件教师训练、GRPO+OPD 联合优化、基于对齐进度与相对能力的在线退场, 了解退场判据 γ、δ 与监控窗口 W 的设定及其鲁棒性范围, 对比 RetireOPD 与 GRPO、GRPO+OPD、OPSD 及线性退火基线在 ALFWorld/WebShop 上的表现]
tags: [on-policy-distillation, teacher-retirement, RLVR, multi-turn-agents, GRPO, adaptive-scheduling]
sources: [retireopd-self-retiring-on-policy-distil]
related: [privileged-info-opsd-ample-math, grpo, multi-turn-rl]
prerequisites: []
---
## 问题与语境

在带可验证奖励的强化学习（RLVR）中训练多轮 LLM 智能体时，一条轨迹只对应一个结果奖励，长交互中的中间决策因此缺乏监督。在线策略蒸馏（OPD）用教师提供 token 级密集监督来补足这一稀疏性；在智能体场景中，教师通常就是同一模型加上仅在训练期可得的特权上下文（如检索到的任务技能），学生则在无该上下文的条件下被训练去复现教师行为，从而把技能内化进参数、推理时不再需要额外上下文。

这套范式依赖两个隐含假设：其一，教师因为看到特权上下文而可靠地优于学生；其二，匹配教师在整个训练过程中始终有益。论文在 ALFWorld 与 WebShop 上检验后指出两个假设都不成立。第一，在 GRPO 与在线策略自蒸馏（OPSD）联合训练下，教师与学生是同一共享策略的两个分支，技能条件分支并不稳定优于它所监督的学生分支——共享参数主要被无技能的学生目标优化，策略从未真正学会利用技能上下文；模型规模也帮不上忙，用同样技能提示的 7B 模型在 ALFWorld 上仅达 23.4% 成功率。第二，师生差异先缩小后扩大：学生一旦内化技能所诱导的行为，奖励优化就会偏向教师不会采取的动作，两个梯度开始冲突，继续匹配教师会把学生压在教师的能力上限附近。

已有做法用训练前就固定的调度来回答"何时停止蒸馏"：退火方法按预定曲线衰减蒸馏权重，两阶段方案在预定步数从蒸馏切到 RL。它们都不观察教师是否仍然有用；更细粒度的在线决策（按 prompt 或按 token）存在，但都不移除教师。论文的定位是：把"教师是否仍有用"当作可从训练信号本身读出的事实——差异不再下降恰是两个目标冲突之时，学生相对教师的成功率则表明技能是否已内化——从而把这一全局切换改为在线判定，而非事先固定。

## 核心主张

论文的核心主张可归纳为四条，其证据定位与状态如下。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | 仅靠特权上下文不能保证教师可靠，技能条件分支未必稳定优于学生 | §1 图2左；§4.4 中 7B 技能提示仅 23.4% 成功率（表1 Skill-Prompt∗ 行） | 作者主张 |
| C2 | 教师监督的收益是阶段性的：师生差异先缩小后扩大，后期两目标梯度冲突 | §1 图2右；§4.3 图4；附录A 一阶分析 | 作者主张 |
| C3 | RetireOPD 在 ALFWorld 上比 GRPO 提升 14.1%–18.8%，WebShop 准确率提升 11.8%–19.0% | §1 贡献段；§4 表1 | 作者主张 |
| C4 | 自适应退场点对阈值不敏感，γ∈[0.80,0.96]、δ∈[-0.10,0.04] 时退场步数在默认值 ±5 步内 | §4.5 图7 | 作者主张 |

最强的是 C2，因为它不只是一个性能数字，而是一条可被独立检验的机制性论断，且论文给出了多重交叉证据：训练曲线上的差异先降后升（图2右）、从退场点继续训练的三策略对照（图4，移除 OPD 后成功率从 76.6% 升至 93.8%，而继续联合优化出现平台、切回 OPD 甚至退化），以及附录 A 的一阶分析指出差异停滞意味着梯度局部对立。这条主张也解释了 C3 为何成立，并直接支撑方法设计。

最弱的是 C4。它只报告了退场步数在阈值扰动下的稳定性（±5 步内），并未说明这种稳定性是否伴随最终性能的稳定；"极端阈值才出现明显延迟"这一表述也缺少可核对的定量边界。此外，C1 与 C3 均为作者主张：C1 的关键证据是单一环境（ALFWorld）上的 23.4% 成功率，C3 的区间来自三个模型规模在两个环境上的汇总，论文未报告种子数、方差或显著性检验，因此这些数字应视为作者报告值而非已复现结论。C2 的机制解释同样依赖作者自己的训练动态观测，尚无第三方复现。

## 机制与方法

RetireOPD 把「特权技能蒸馏」拆成三段流水线：先造一个可信教师，再让学生联合优化奖励与蒸馏，最后在线判断教师何时退场。

**阶段一：教师构建。** 论文的核心诊断是「特权上下文本身不保证教师可靠」：在 GRPO+OPSD 下，技能条件分支与学生共享参数，而共享参数主要被无技能的学生目标优化，策略从未被训练去真正使用技能上下文，因此技能分支并不稳定优于它所监督的学生（作者主张，§1 图2左）。相应地，RetireOPD 把教师与学生解耦，用环境奖励在技能上下文 $c^{+}$ 下单独训练一个同容量的技能条件教师，使蒸馏从一个已经学会利用技能的策略出发。

**阶段二：联合技能内化。** 学生不接触 $c^{+}$，在自身采样轨迹上同时优化环境奖励与教师监督：

$$\mathcal{L}_{\mathrm{student}}(\theta)=\mathcal{L}_{\mathrm{GRPO}}(\theta)+\lambda\mathcal{L}_{\mathrm{OPD}}(\theta)$$

其中 $\mathcal{L}_{\mathrm{GRPO}}$ 为组相对优势的 RL 损失，$\mathcal{L}_{\mathrm{OPD}}$ 为 token 级在线策略蒸馏损失，$\lambda$ 控制教师监督权重（默认 0.01）。蒸馏建立在师生 token 级对数概率差 $\Delta_t$ 之上。

**阶段三：自适应退场。** 训练被划分为长度为 $W$ 的监控窗口。记第 $n$ 步第 $i$ 条轨迹第 $t$ 个 token 的师生对数概率差为 $\Delta_t^{(i)}$，步级与窗口级对齐进度为

$$K_{n}=\frac{1}{G}\sum_{i=1}^{G}\frac{1}{|y_{n}^{(i)}|}\sum_{t=1}^{|y_{n}^{(i)}|}\Delta_{t}^{(i)},\qquad \bar{K}_{m}=\frac{1}{W}\sum_{n=mW}^{mW+W-1}K_{n}$$

再定义窗口间对齐进度的相对变化率与学生相对教师的能力：

$$\rho_{m}^{(K)}=\frac{\bar{K}_{m}-\bar{K}_{m-1}}{\bar{K}_{m}},\qquad \eta_{m}=\frac{SR_{m}+SR_{m-1}}{2\,SR_{T}}$$

$SR_m$ 与 $SR_T$ 分别为学生与教师成功率；$\eta_m$ 对连续两个窗口取平均以抑制短期波动。$\rho_m<0$ 表示师生差异仍在缩小，$\rho_m\ge 0$ 表示缩小停滞或反转。退场窗口取首个同时满足两条件的窗口：

$$m^{*}=\inf\left\{m\geq 2:\rho_{m}^{(K)}\geq\delta\ \wedge\ \eta_{m}\geq\gamma\right\}$$

$\delta$ 为差异变化阈值，$\gamma$ 为相对能力阈值（默认 0.9）。一旦满足，OPD 被永久移除，仅用 GRPO 继续训练，此后不再需要教师前向计算。

**设计取舍与前提。** 两个条件缺一不可：只用 $\rho_m$ 会在学生尚弱、差异偶然停滞时过早退场；只用 $\eta_m$ 则无法捕捉「学生已达标但两目标梯度已冲突」的情形。窗口 $W$（默认 5）与 $m\ge 2$ 的下界共同构成对瞬时波动的防护。方法的前提假设是：师生差异的停滞可作为两目标梯度局部对立的代理信号（附录 A 给出一阶分析，作者主张），且学生成功率相对教师成功率能刻画技能是否已内化。这两点均由作者在 ALFWorld 与 WebShop 上以实验支持，属于作者主张而非独立复现的共识。

## 实验设置

所有方法在统一训练配置下比较（附录 B 表 4）：学习率 $1\times10^{-6}$，组大小 $G=8$，蒸馏损失系数 $\lambda=0.01$，KL 惩罚系数 $\alpha_{\mathrm{KL}}=0.01$，训练批大小 16，验证集规模 128，训练步数 150；PPO 的 critic 学习率为 $1\times10^{-5}$。RetireOPD 另设能力阈值 0.9、监控窗口 5。评测环境为 ALFWorld（具身家务，指标为平均成功率 Avg success rate）与 WebShop（网页购物，指标为 Accuracy），模型为 Qwen2.5-1.5B/3B/7B-Instruct。基线覆盖纯 RL（GRPO、GiGPO、PPO、RLOO、Skill-GRPO）、蒸馏（OPD-Skill、OPSD）与混合方法（GRPO+OPD、GRPO+OPSD），以及 Prompt 类（Vanilla、Skill-Prompt）。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
| --- | --- | --- | --- | --- |
| ALFWorld | Qwen2.5-1.5B-Instruct | GRPO | 150 training steps | Avg success rate |
| ALFWorld | Qwen2.5-3B-Instruct | GRPO | 150 training steps | Avg success rate |
| ALFWorld | Qwen2.5-7B-Instruct | GRPO | 150 training steps | Avg success rate |
| WebShop | Qwen2.5-1.5B-Instruct | GRPO | 150 training steps | Accuracy |
| WebShop | Qwen2.5-3B-Instruct | GRPO | 150 training steps | Accuracy |
| WebShop | Qwen2.5-7B-Instruct | GRPO | 150 training steps | Accuracy |
| ALFWorld | Qwen2.5-1.5B-Instruct | GRPO+OPD | 150 training steps | Avg success rate |
| ALFWorld | Qwen2.5-3B-Instruct | GRPO+OPD | 150 training steps | Avg success rate |
| ALFWorld | Qwen2.5-7B-Instruct | GRPO+OPD | 150 training steps | Avg success rate |
| WebShop | Qwen2.5-1.5B-Instruct | GRPO+OPD | 150 training steps | Accuracy |
| WebShop | Qwen2.5-3B-Instruct | GRPO+OPD | 150 training steps | Accuracy |
| WebShop | Qwen2.5-7B-Instruct | GRPO+OPD | 150 training steps | Accuracy |
| ALFWorld | Qwen2.5-1.5B-Instruct | OPD-Skill-1.5B | 150 training steps | Avg success rate |
| ALFWorld | Qwen2.5-3B-Instruct | OPD-Skill-3B | 150 training steps | Avg success rate |
| ALFWorld | Qwen2.5-7B-Instruct | OPD-Skill-7B | 150 training steps | Avg success rate |
| WebShop | Qwen2.5-1.5B-Instruct | OPD-Skill-1.5B | 150 training steps | Accuracy |
| WebShop | Qwen2.5-3B-Instruct | OPD-Skill-3B | 150 training steps | Accuracy |
| WebShop | Qwen2.5-7B-Instruct | OPD-Skill-7B | 150 training steps | Accuracy |
| ALFWorld | Qwen2.5-7B-Instruct | Skill-Prompt | 未说明 | Avg success rate |

需要说明的是，上表仅列出证据表中明确给出数值的对照块；表 1 还包含 GiGPO、PPO、RLOO、Skill-GRPO、OPSD、GRPO+OPSD 等基线，但证据表未逐项抽取其数值，故不在此列出。Skill-Prompt 一行在证据表中预算字段为空，此处标为「未说明」。

## 证据与结果

主结果来自 §4 表 1（ALFWorld 六个子任务平均成功率 Avg 与 WebShop 准确率 Acc），统一设置：Qwen2.5-1.5B/3B/7B-Instruct，150 training steps，学习率 $1\times10^{-6}$，组大小 $G=8$，$\lambda=0.01$，$\alpha_{\mathrm{KL}}=0.01$，train batch size 16，validation data size 128（Table 4）。RetireOPD 自身超参：competence threshold 0.9，window size 5。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| ALFWorld Avg success | RetireOPD 89.8 vs GRPO 72.8 | 1.5B, 150 steps | §4 表1 |
| ALFWorld Avg success | RetireOPD 93.8 vs GRPO 75.0 | 3B, 150 steps | §4 表1 |
| ALFWorld Avg success | RetireOPD 95.3 vs GRPO 81.2 | 7B, 150 steps | §4 表1 |
| WebShop Acc | RetireOPD 75.8 vs GRPO 56.8 | 1.5B, 150 steps | §4 表1 |
| WebShop Acc | RetireOPD 77.3 vs GRPO 63.3 | 3B, 150 steps | §4 表1 |
| WebShop Acc | RetireOPD 84.4 vs GRPO 72.6 | 7B, 150 steps | §4 表1 |
| ALFWorld Avg success | RetireOPD 89.8 vs GRPO+OPD 87.5 | 1.5B | §4 表1 |
| ALFWorld Avg success | RetireOPD 93.8 vs GRPO+OPD 82.8 | 3B | §4 表1 |
| ALFWorld Avg success | RetireOPD 95.3 vs GRPO+OPD 92.2 | 7B | §4 表1 |
| WebShop Acc | RetireOPD 75.8 vs GRPO+OPD 69.9 | 1.5B | §4 表1 |
| WebShop Acc | RetireOPD 77.3 vs GRPO+OPD 74.2 | 3B | §4 表1 |
| WebShop Acc | RetireOPD 84.4 vs GRPO+OPD 81.2 | 7B | §4 表1 |
| ALFWorld Avg success | RetireOPD 89.8 vs OPD-Skill-1.5B 71.1 | 1.5B | §4 表1 |
| ALFWorld Avg success | RetireOPD 93.8 vs OPD-Skill-3B 74.2 | 3B | §4 表1 |
| ALFWorld Avg success | RetireOPD 95.3 vs OPD-Skill-7B 86.7 | 7B | §4 表1 |
| WebShop Acc | RetireOPD 75.8 vs OPD-Skill-1.5B 69.1 | 1.5B | §4 表1 |
| WebShop Acc | RetireOPD 77.3 vs OPD-Skill-3B 66.4 | 3B | §4 表1 |
| WebShop Acc | RetireOPD 84.4 vs OPD-Skill-7B 78.1 | 7B | §4 表1 |
| ALFWorld Avg success | Skill-Prompt 23.4 | 7B, 带技能提示 | §4 表1 / §1 |
| ALFWorld 相对 GRPO 提升 | 14.1% to 18.8% | 1.5B/3B/7B | §1 |
| WebShop 相对 GRPO 提升 | 11.8% to 19.0% | 1.5B/3B/7B | §1 |
| 退场点后仅用 GRPO 的成功率 | 76.6% → 93.8% | 从退场 checkpoint 继续 | §4.3 |
| 退场步数跨模型/任务变化 | step 50 to step 90 | 差异停止下降处 | §1 / 附录E |
| 退场步数稳定性 | γ∈[0.80,0.96]、δ∈[-0.10,0.04] 时在默认 ±5 步内 | 阈值扫描 | §4.5 |

消融与对照：Figure 5 为教师构造与教师退场的消融（虚线为无教师监督的 GRPO 基线）；Figure 6 为自适应退场 vs 线性退火（LA）；§4.3 从退场 checkpoint 出发比较三种续训策略——继续联合优化出现平台且师生差异持续扩大，切换到 OPD 进一步缩小差异但不提升任务表现甚至退化，移除 OPD 改用 GRPO 则从 76.6% 升至 93.8%。表 1 中 OPD-3B（1.5B 学生）、OPD-7B（3B 学生）、OPD-14B（7B 学生）等跨规模教师对照的完整数值摘录未逐项给出，仅见 5.6 / 38.3 / 64.8 等 Avg 值；OPSD 与 GRPO+OPSD 的完整数值亦未在摘录中全部列出。所有主结果均为单次运行的报告值，摘录未给出方差、置信区间或显著性检验。

## 证据强度评估

证据分级：B（中等偏强，但不足以直接迁移）。

理由：结论建立在两个标准多轮智能体基准（ALFWorld、WebShop）× 三个模型规模（1.5B/3B/7B）的一致方向上，且对照覆盖三类基线——纯 RL（GRPO、GiGPO、PPO、RLOO）、蒸馏（OPD-Skill、OPSD）、混合（GRPO+OPD、GRPO+OPSD），并额外与自身技能条件教师比较（§1、§4 表1）。超参在 Table 4 中统一披露，退场阈值做了扫描（§4.5）。但所有数字均为单点报告，摘录中无随机种子数、无方差/置信区间、无显著性检验；消融以图（Figure 5、6）而非表呈现，摘录未给出具体数值，因此无法独立核算效应量。故定为 B 而非 A。

主要威胁：

1. 构造效度：核心机制依赖两个在线信号 $\rho_m$（师生对数概率差的窗口相对变化）与 $\eta_m$（学生/教师成功率之比）。§4.3 的因果论证是「从退场点续训」的事后对照，而非对退场时机本身的随机化干预；「差异停止下降 ⇒ 梯度冲突」的推断依赖附录 A 的一阶分析，摘录未给出该分析的完整条件与近似误差。此外 $\eta_m$ 需要教师成功率 $SR_T$，退场后不再需要教师前向，但退场前仍需周期性评估教师，这部分开销未在摘录中量化。

2. 外部效度：仅两个环境、单一模型家族（Qwen2.5-Instruct）、单一训练预算（150 steps）。退场点本身随模型与任务在 step 50–90 间漂移（§1、附录 E），说明该信号的时间尺度对设置敏感；在更长训练、更大模型或不同 RL 算法（如 PPO/RLOO 作为底座）下是否仍成立，摘录未给出。

3. 基线选择与公平性：最强基线 GRPO+OPD 与 RetireOPD 共享同一教师与同一 $\lambda$，差距（如 3B 上 93.8 vs 82.8）可较干净地归因于退场机制；但 GiGPO 在 7B ALFWorld 上达 90.8、Skill-GRPO 达 90.6，与 RetireOPD 95.3 的差距小于与 GRPO 的差距，说明「相对 GRPO 提升 14.1%–18.8%」这一表述会高估相对当前最优 RL 基线的增益。此外 OPD-3B/OPD-7B/OPD-14B 等跨规模教师基线表现极低（如 5.6、38.3、64.8），其配置是否与 RetireOPD 的教师同等训练，摘录未说明。

4. 评测污染与统计：ALFWorld/WebShop 为公开基准，摘录未说明训练数据与评测集的隔离方式；所有对比均为单次运行，无法排除阈值 0.9 与窗口 5 的默认值恰好在本次运行中占优（§4.5 的 ±5 步稳定性是作者主张，未给逐点数值）。

## 边界与反例

**什么观察会推翻结论。** 论文的核心因果链是「师生差异先降后升 ⇒ 两目标梯度冲突 ⇒ 应退场」。若在退场点之后继续联合优化（GRPO+OPD）而不出现性能平台、或师生差异持续单调下降且任务成功率同步上升，则 C2 被推翻。作者在 §4.3 报告了相反方向：从退场点继续联合优化导致平台期且差异持续扩大，切换回纯 OPD 进一步缩小差异但任务性能不升甚至退化，而移除 OPD 后成功率从 76.6% 升到 93.8%。这些是作者主张，未见独立复现。

**最可能失效的条件。** 其一，教师本身不可靠时，退场判据 $\eta_m \ge \gamma$ 失去参照系——论文自己指出未优化的技能条件教师不稳定优于学生（7B 技能提示仅 23.4% 成功率），因此该方法依赖第一阶段用环境奖励单独训练教师，若该阶段训练不充分，$\eta_m$ 的分母（教师成功率）本身失真。其二，退场点跨模型跨任务在 step 50 到 step 90 之间漂移，说明「差异停止下降」这一信号的时间尺度随任务变化；论文只验证了 $\gamma\in[0.80,0.96]$、$\delta\in[-0.10,0.04]$ 时退场步数在默认值 ±5 步内，超出该范围「明显延迟仅在较极端阈值下出现」——但极端阈值之外的行为未给出定量边界。其三，全部实验固定在 150 步、batch 16、验证集 128，长训练与更大规模下窗口统计量 $\bar K_m$ 的噪声特性可能改变。

**作者未验证但易被误推的方向。** (a) 论文只覆盖 ALFWorld 与 WebShop 两个多轮环境，不能直接外推到单轮推理任务或非智能体 RLVR。(b) 退场后「不再需要教师前向计算」是效率主张，但论文未报告实际 wall-clock 或显存节省数字，不应据此推断加速比。(c) 退场判据依赖成功率，若任务奖励不可靠或成功率估计方差大（小验证集），$\eta_m$ 的窗口平均未必足够稳健。(d) 论文未做退场后是否可「再引入」教师的实验，不能推断单向退场是最优策略。

## 与知识库的关系

**与「On-policy distillation (OPD) with privileged teachers」的关系（新增）。** 既有笔记把特权上下文视为教师可靠性的充分条件；本文给出反例：GRPO+OPSD 下技能条件分支并不一致优于学生分支，共享参数主要被无技能学生目标优化，策略从未学会利用技能上下文。新增的可链接结论：教师必须先用环境奖励训练才能监督（对应笔记 id：`opd-privileged-teacher-reliability`）。

**与「On-policy self-distillation (OPSD)」的关系（张力）。** 既有笔记默认条件分支是更强分支；本文的观察与之直接冲突，并给出机制解释（共享参数优化路径）。若读者此前把 OPSD 当作「免费教师」，需标注该结论在智能体多轮设定下不成立（笔记 id：`opsd-conditioned-branch-stronger`）。

**与「Combining OPD with RL (hybrid methods)」的关系（新增 + 印证）。** 印证：退火、两阶段切换等固定调度确实能缓解干扰。新增：固定调度无法在线判断教师是否仍有用，且退场点跨模型跨任务在 step 50–90 漂移，任何单一调度都会在某些设定下过早或过晚。本文把决策粒度从 per-prompt / per-token 提升到全局一次性退场（笔记 id：`hybrid-opd-rl-fixed-schedule`）。

**与「RLVR for multi-turn agents」的关系（印证 + 扩展）。** 印证：轨迹级奖励稀疏、需要密集监督。扩展：在 ALFWorld 与 WebShop 上 RetireOPD 优于纯 RL、蒸馏与混合基线，并超过自身技能条件教师；相对 GRPO 的提升为 ALFWorld 14.1%–18.8%、WebShop 11.8%–19.0%（作者主张，笔记 id：`rlvr-multiturn-agentic`）。

**待建笔记。** 建议新增 `adaptive-teacher-retirement`（退场判据 $\rho_m \ge \delta \wedge \eta_m \ge \gamma$）与 `teacher-student-discrepancy-nonmonotone`（差异先降后升作为梯度冲突的可观测代理），后者目前仅有作者的一阶分析（附录 A）支撑，标注为待复现。

## 复现与验证计划

目标：在最小成本下检验两条核心主张——(C1) 未优化的技能条件教师不可靠；(C2) 教师监督收益是阶段性的，退场后应继续纯 RL。

环境与任务：ALFWorld 与 WebShop 两个多轮智能体环境（具身家务 / 网页购物）。模型取 Qwen2.5-1.5B-Instruct 与 3B-Instruct 两档即可覆盖规模趋势，7B 可选。

统一超参（据 Table 4，可直接照抄）：学习率 $1\times10^{-6}$；组大小 $G=8$；蒸馏损失系数 $\lambda=0.01$；KL 惩罚系数 $\alpha_{\mathrm{KL}}=0.01$；train batch size 16；validation data size 128；训练步数 150。RetireOPD 专属：能力阈值 0.9，窗口 $W=5$。PPO 若作为对照需 critic 学习率 $1\times10^{-5}$。

基线与预算：全部 150 training steps。必跑四条：GRPO、GRPO+OPD、OPD-Skill（同容量技能条件教师）、RetireOPD。指标：ALFWorld 用 Avg success rate，WebShop 用 Accuracy。参照点（作者报告值，非本文复现）：1.5B 上 GRPO 72.8 / GRPO+OPD 87.5 / OPD-Skill-1.5B 71.1 / RetireOPD 89.8（ALFWorld）；3B 上 75.0 / 82.8 / 74.2 / 93.8。

判据（按优先级）：
1. C1：OPD-Skill 是否显著优于同规模 GRPO。若 OPD-Skill 未超过 GRPO，则支持「特权上下文不保证教师可靠」。
2. C2：记录师生 token 级对数概率差 $\Delta_t$ 的窗口均值 $\bar K_m$ 与相对变化 $\rho_m$，检查是否先降后升；并做退场点续训三分支对照（继续联合优化 / 切纯 OPD / 切纯 GRPO），看纯 GRPO 分支是否持续上升（作者报告 76.6% → 93.8%）。
3. 退场时机稳健性：扫 $\gamma\in[0.80,0.96]$、$\delta\in[-0.10,0.04]$，看退场步是否落在默认设置 $\pm5$ 步内。

预期失败模式：教师未先用环境奖励训练时蒸馏无效甚至有害（表中 OPD-3B 在 1.5B 学生上仅 5.6，OPSD 仅 14.1）；退场过早导致学生未内化技能、退场过晚导致性能平台；阈值取极端值时退场明显延迟。注意：以上数值均为作者报告，本计划未做独立复现，跨环境迁移性未知。

## 术语与记号

| 术语 | 含义 |
| --- | --- |
| RLVR | 带可验证奖励的强化学习，用可自动判定的结果奖励训练模型 |
| OPD | 在线策略蒸馏，在学生自己采样的轨迹上用教师提供 token 级监督 |
| OPSD | 在线策略自蒸馏，同一模型的条件分支蒸馏到无条件分支 |
| 特权上下文 / 技能 $c^{+}$ | 仅训练时可得的检索或事后技能信息，推理时不可用 |
| GRPO | 组相对策略优化，用组内相对优势的 RL 算法 |
| 师生差异 | token 级对数概率差，衡量行为对齐程度 |
| 自适应教师退场 | 依据训练信号在线移除教师监督 |
| 相对能力 | 学生成功率与教师成功率之比 |
| 监控窗口 | 按固定步数 $W$ 划分训练以计算退场信号 |
| 线性退火 (LA) | 按预定调度线性衰减蒸馏权重的基线 |
| ALFWorld / WebShop | 两个多轮智能体评测环境（具身家务 / 网页购物） |

关键记号：学生总目标 $\mathcal{L}_{\mathrm{student}}(\theta)=\mathcal{L}_{\mathrm{GRPO}}(\theta)+\lambda\mathcal{L}_{\mathrm{OPD}}(\theta)$，其中 $\lambda$ 为蒸馏损失权重（默认 0.01）。第 $t$ 个 token 的师生对数概率差记为 $\Delta_t$；第 $n$ 步的步级对齐进度 $K_n$ 为该步各轨迹 token 差的均值，窗口级对齐进度 $\bar K_m$ 为窗口 $W$ 内 $K_n$ 的均值。窗口间相对变化 $\rho_m^{(K)}=(\bar K_m-\bar K_{m-1})/\bar K_m$，$\rho_m<0$ 表示差异仍在下降，$\rho_m\ge 0$ 表示下降停滞或反转。相对能力 $\eta_m=(SR_m+SR_{m-1})/(2SR_T)$，$SR_m$ 与 $SR_T$ 分别为学生与教师成功率，学生侧取连续两窗平均以抑制短期波动。退场窗口 $m^{*}=\inf\{m\ge 2:\rho_m^{(K)}\ge\delta \wedge \eta_m\ge\gamma\}$，$\delta$ 为差异变化阈值，$\gamma$ 为相对能力阈值（默认 0.9），$W$ 默认 5。首次满足即永久移除 OPD，此后仅用 GRPO 训练。

## 自测

以下问题用于检验你是否真正读懂了本档案的证据边界，而非记住了数字。建议先自行作答，再展开答案对照。

**Q1.** 论文声称 RetireOPD 在 ALFWorld 上相对 GRPO 提升 14.1%–18.8%。请用证据表中的具体数值验证这一区间是否与 1.5B/3B/7B 三档结果自洽，并说明该区间是绝对百分点还是相对提升。

<details><summary>答案</summary>
证据表给出：1.5B 为 89.8 vs 72.8（差 17.0），3B 为 93.8 vs 75.0（差 18.8），7B 为 95.3 vs 81.2（差 14.1）。三档差值恰为 14.1–18.8，与 §1 引文一致，因此该区间是绝对百分点差（success rate 之差），不是相对提升。注意 WebShop 的 11.8%–19.0% 同理：75.8−56.8=19.0，77.3−63.3=14.0，84.4−72.6=11.8，但 3B 档为 14.0 而非区间端点，区间由 1.5B 与 7B 端点界定。
</details>

**Q2.** 若把基线从 GRPO 换成 GRPO+OPD，RetireOPD 的优势在哪个模型/任务组合上最小？这说明什么？

<details><summary>答案</summary>
最小差距出现在 ALFWorld 7B：95.3 vs 92.2，仅 3.1 个百分点；WebShop 7B 为 84.4 vs 81.2，差 3.2。而 1.5B/3B 上差距更大（ALFWorld 2.3 与 11.0，WebShop 5.9 与 3.1）。这说明随模型变大，持续联合优化 GRPO+OPD 本身已接近 RetireOPD，退场机制带来的边际收益缩小；作者未对此做专门分析，属本档案的推断而非作者主张。
</details>

**Q3.** 论文的核心机制依赖两个在线信号 ρ_m 与 η_m。请说明为什么单独使用其中任何一个都可能导致错误退场，并指出论文用什么设计来缓解。

<details><summary>答案</summary>
ρ_m ≥ δ 表示师生差异不再下降（对齐停滞或反转），但若学生仍很弱，差异停滞可能只是暂时波动，此时退场会过早；η_m ≥ γ 表示学生能力已达教师的一定比例，但若差异仍在快速下降，说明蒸馏仍在有效传递知识，此时退场会浪费监督。论文用 Eq.9 的合取条件 ρ_m ≥ δ ∧ η_m ≥ γ，且从 m ≥ 2 起判定，η_m 取连续两窗平均以抑制短期波动（§3.3）。
</details>

**Q4.**（跨小节）§4.3 报告从退场点继续训练时，移除 OPD 后成功率从 76.6% 升到 93.8%。这个 93.8% 与主表 ALFWorld 3B 的 RetireOPD 结果数值相同。这是否意味着两者是同一实验？请说明你的判断依据与不确定处。

<details><summary>答案</summary>
数值相同（93.8）且 §4.3 的动力学分析以 3B on ALFWorld 为例（图 2 即 3B），因此很可能是同一组实验的两个视角：主表报告最终 Avg success rate，§4.3 报告从退场检查点起的轨迹。但证据表未显式声明二者同源，档案中应标注为「高度可能但未在摘录中确证」。此外 76.6% 是退场点的成功率，与主表中任何一档的最终值都不对应，说明它是中间检查点数值。
</details>

**Q5.**（跨小节）论文称退场点对阈值不敏感（γ∈[0.80,0.96]、δ∈[-0.10,0.04] 时退场步数在默认值 ±5 步内），但又称退场点在不同模型/任务上从 step 50 变到 step 90。这两个说法是否矛盾？对迁移到你自己的场景意味着什么？

<details><summary>答案</summary>
不矛盾。前者是「固定模型/任务、扰动阈值」下的稳定性（§4.5 图 7），后者是「固定默认阈值、跨模型/任务」的差异性（§1 / 附录 E）。二者共同支持论文的核心论点：退场时机应由训练信号在线决定，而非预设单一调度——因为最优时机本身随设置漂移，但判定准则在阈值上稳健。迁移含义：你不必精调 γ、δ，但必须实现在线监测；同时不能假设退场步数可跨任务复用。注意这两条均为作者主张，档案中未见独立复现。
</details>
