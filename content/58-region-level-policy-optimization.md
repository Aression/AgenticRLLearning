---
id: region-level-policy-optimization
title: 区域级策略优化：细粒度多模态感知
summary: 多模态大模型在细粒度视觉感知上仍易失败：小字、远处目标与高分辨率杂乱场景会降低准确率，而直接提高输入分辨率会带来视觉与语言侧计算开销。答案相关证据通常只占图像一小部分，因此需要选择性分配高分辨率处理。
stage: FRONTIER
track: 训练算法
kind: paper
depth: deep
evidenceGrade: C
order: 58
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.19745
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.19745
objectives: [理解定位与识别在token压缩容忍度上的不对称性（约3–4倍）, 掌握以连通区域为动作、冻结reader功能贡献为奖励的区域级RL机制, 了解减法/加法策略、控制区域噪声边界与稀疏视觉编码的配合, 评估该方法在精度-效率权衡上相对SD-RPN与剪枝方法的优势]
tags: [region-level RL, MLLM perception, token compression, RoI prediction, policy optimization]
sources: [region-level-policy-optimization-for-fin]
related: [grpo, ppo, policy-gradient]
prerequisites: [policy-gradient, ppo]
---
## 问题与语境

多模态大模型在细粒度视觉感知上的失败模式具有结构性：小字、远处目标与高分辨率杂乱场景会显著降低准确率，而粗粒度场景理解往往仍然可靠。最直接的补救是提高输入分辨率，但这会同时抬高视觉编码与语言模型两侧的开销，且答案相关证据通常只占图像很小一部分，均匀分配分辨率在计算上是浪费的。

论文把细粒度问答拆成两个感知操作：先定位证据，再识别其内容。已有做法大致三类。其一是特权视图蒸馏（如 Vision-OPD、ZwZ），在全模型内优化细粒度感知，代价是完整微调，且不暴露可复用的定位器。其二是 thinking-with-images 式的全模型 RL，用解码轨迹交织裁剪与缩放动作；论文指出这类方法内存密集、不稳定，且近期分析表明其增益主要来自被 RL 优化的模型本身而非工具使用，推理时还要为解码轨迹或重复生成轮次付费。其三是免训练的两阶段路由（注意力引导或搜索树），需要多次预填充/解码，启发式跨模型迁移性差。SD-RPN 提供了更廉价的接口：在中间层挂一个轻量提议网络，单次前向输出 answer-free 的 RoI 图，用 response-to-image attention 蒸馏出的 token-wise 伪标签训练。但论文认为其监督是局部代理——伪激活可能残留、弱注意力证据可能被漏掉，而这两类错误都没有被答案检验过。

论文的定位由此明确：不是提出更强的全模型微调或更复杂的搜索，而是把「区域是否真的支持答案」这一答案级信号，以区域级信用的形式回灌给一个冻结 reader 之外的轻量预测器。其前提是一个受控诊断——定位比识别能承受更强的 token 压缩，因此把高分辨率预算从「整图」转移到「被选中的证据」在原理上可行，而瓶颈落在 RoI 预测器的可靠性上。需要标注的是，该不对称性诊断被作者自己限定为单一骨干、单一基准上的诊断，而非一般规律。

## 核心主张

论文的核心主张可归纳为四条，均以作者主张形式给出，尚无第三方复现记录。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | 定位比识别能承受约 3–4× 更强的 token 压缩 | §1 图 1a,b；附录 C（ZoomBench + Qwen3.5-4B，≤128 visual token，n=238） | 作者主张 |
| C2 | 区域级 RL 在 SD-RPN 上平均 +3.0，稀疏视觉编码再 +1.5；相对冻结基座全系统 +14.9 | §4.4 表 2（Qwen3.5-4B，训练对齐协议，576-token 源限制） | 作者主张 |
| C3 | 4B 模型以 4.2× 更少视觉 token 匹配 SD-RPN 精度 | §4.3 图 4；§1 图 1c | 作者主张 |
| C4 | 9B 模型在表 1 平均分最高，超过 Gemini-3.1-Pro 与 Vision-OPD-9B | §4.2 表 1（共享 16,384 源图像 token 限制） | 作者主张 |

最强的是 C2。它是机制消融，控制变量最干净：同一骨干、同一源 token 限制（576）、同一训练对齐协议下，逐项移除区域级 RL、稀疏编码、功能分数、控制区域 margin、加法组，代价分别为 +3.0、+1.5、−2.3、−1.5、−1.1、−0.9，方向一致且量级可分辨。其中「用生成准确率替代功能分数」损失 −2.3、「用原始平均 log-prob 替代裁剪 log-odds」损失 −1.5，直接支持了论文关于奖励设计的关键论证，而不只是「加了模块就涨点」。相对地，C4 最弱：它是跨方法比较，且论文自述基线来源不一——基座与 Vision-OPD/ZwZ 行由作者在公开权重上重评，大规模参考模型引自 Vision-OPD，其余引自各自发表；同时 9B 在 HR-Bench 4K 上并未领先 Vision-OPD-9B，MME-RealWorld 两个 split 上 4B 与 7B 均落后，作者将此归因于冻结 reader 的设计取舍。因此 C4 更适合读作「在共享 token 预算下具有竞争力」，而非全面超越。

C1 是全文的动机来源，但作者明确限定其为单骨干、单基准上的诊断，迁移性需自行验证；C3 的效率声明依赖 SD-RPN 这一特定对照，且 4.2× 的数值出现在 4B 设置下，9B 上对应表述为「半个点以内 2.5× 更少 token」，两者不可混用。

## 机制与方法

Vision-RL2 的出发点是：RoI 预测器输出的稠密热图经二值化、连通域提取、裁剪重编码后，答案梯度无法回传到热图，因此需要一种「答案级信号 + 区域级信用」的监督。方法在已训练的 SD-RPN 检查点上做区域级强化学习，**只更新 RPN 参数 $\theta$，冻结 MLLM 作为 reader $p_\phi$**。

**动作单元与掩码。** 与把 $H_gW_g$ 个格子当作独立二值动作（$2^{H_gW_g}$ 种掩码）不同，方法以「连通视觉区域」为原子动作。区域 $R$ 由共享的 map-to-region 算子从空间源图产生（平滑、按峰值相对阈值二值化、取连通分量）。区域集合 $\mathcal{A}$ 渲染为掩码并集 $M(\mathcal{A})=\bigvee_{R\in\mathcal{A}}m_R$，上采样后得到掩码图像 $I[M]$，掩码外像素置为逐通道均值。

**功能分数。** 不评几何、评功能。冻结 reader 在 $I[M]$ 与问题 $q$ 条件下对金答案 $y^\star$ 做 teacher forcing，取答案 token 概率的几何平均及其 log-odds：

$$P_\phi(M)=\exp\!\Big(\tfrac{1}{T}\sum_{t=1}^{T}\log p_\phi(y_t^\star\mid I[M],q,y_{<t}^\star)\Big),\qquad h_\phi(M)=\operatorname{logit}(P_\phi(M))$$

区域 $R$ 相对参考掩码 $M_{\mathrm{ref}}$ 的留一贡献为 $\Delta_\phi(R\mid M_{\mathrm{ref}})=h_\phi(M_{\mathrm{ref}})-h_\phi(M_{\mathrm{ref}}\ominus R)$，并裁剪到 $[-\delta,\delta]$，$\delta=5$。该估计只需 $n+1$ 次 reader 评估（一个参考掩码 + $n$ 个单区域留一掩码），而非子集搜索；$h_\phi$ 在优化中视为常数（stop-gradient）。

**减法组与噪声校准。** 对策略图 $\bm{P}_\theta$ 提取候选区域，按区域平均 RoI logit $z_\theta(R)$ 排序取 top-$K$（$K\le K_{\max}$）。由于掩码本身会带来 reader 的似然抖动，用控制区域估计样本级噪声边界：控制区域在膨胀预测之外、$\bm{P}_\theta<0.02$ 处生长，面积匹配中位预测区域，$|\mathcal{R}_c|=2$，

$$b=\min\!\Big(\kappa\max_{R\in\mathcal{R}_c}\big|h_\phi(M(\mathcal{R}_p\cup\{R\}))-h_\phi(M_p)\big|,\;b_{\max}\Big)$$

其中 $b_{\max}=1$，$\kappa$ 为校准强度。移除策略由区域置信度经 softmax 给出：$\pi_\theta^{\mathrm{sub}}(a_k\mid x)=\exp(-z_k)/(1+\sum_{j\in\mathcal{K}}\exp(-z_j))$，单位项对应「不移除」。优势为 $A_k^{\mathrm{p}}=(b-\Delta_k^{\mathrm{p}})/(s_{\mathrm{p}}+\varepsilon_{\mathrm{adv}})$，$\varepsilon_{\mathrm{adv}}=1$，$s_{\mathrm{p}}$ 为 $\{\Delta_k^{\mathrm{p}}\}$ 的标准差；$\Delta_k^{\mathrm{p}}>b$ 时移除得负信用，从而抬高 $z_k$ 保留该区域，否则压低其置信度。注意 $\pi_\theta^{\mathrm{sub}}$ 从不采样，它只是把信用分配到稠密图的**可微通道**。

**加法组。** 仅靠剪枝无法恢复漏检证据。训练时用六层冻结的 response-to-image 注意力图（式 1 形式）经同一算子提取 $M_p$ 之外的残差区域并跨层合并，取 top-$J$（$J\le4$）为 $\mathcal{R}_s$。以 $M_{\mathrm{aug}}=M(\mathcal{R}_p\cup\mathcal{R}_s)$ 为参考，$\Delta_j^{\mathrm{s}}=\Delta_\phi(R_j^{\mathrm{s}}\mid M_{\mathrm{aug}})$，优势 $A_j^{\mathrm{s}}=\Delta_j^{\mathrm{s}}/(s_{\mathrm{s}}+\varepsilon_{\mathrm{adv}})$，信用经平均包含对数似然 $\ell^+_\theta(R)=\frac{1}{|R|}\sum_{u\in R}\log\bm{P}_\theta(u)$ 回传，损失 $\mathcal{L}_{\mathrm{add}}=-\sum_j A_j^{\mathrm{s}}\ell^+_\theta(R_j^{\mathrm{s}})$。加法组**不施加控制区域边界**：对无真实贡献的候选，排除本就是零梯度默认，加边界只会偏向压制弱但真实的恢复。两组信用通道与各自决策结构匹配——减法组是互斥移除间的类别选择，故在式 5 的归一化下竞争；加法组是各自独立的包含决策，共享归一化会扭曲其信用。

**稳定化与总目标。** 组内归一化在 reader 对所有掩码都给低似然时会放大噪声，故两个策略损失都乘以 detached 的可达性权重 $w_i$（样本最佳金答案似然的 EMA 归一化裁剪比）。冻结的初始 SD-RPN 提供 KL 锚 $\mathcal{L}_{\mathrm{KL}}$；当 $K_i=1$ 时无相对移除，$\mathcal{L}_{\mathrm{sub}}=0$，改用 BCE 项 $\mathcal{L}_{\mathrm{K1}}$ 保持单分量提议。每样本目标为

$$\mathcal{L}_i=\mathcal{L}_{\mathrm{KL},i}+w_i\big(\mathcal{L}_{\mathrm{sub},i}+\mathcal{L}_{\mathrm{add},i}\big)+\mathbf{1}[K_i=1]\,\mathcal{L}_{\mathrm{K1},i}$$

**推理与稀疏视觉编码。** 推理时对 $(I,q)$ 做一次无答案 RoI 预测。取预测前景的包围盒，测前景占比 $\rho_{\mathrm{fg}}\in(0,1]$，以空间放大 $\eta=\min(\sqrt{1/\rho_{\mathrm{fg}}},\eta_{\max})$ 重编码裁剪，只保留前景 token，背景 token 不进入视觉编码器与语言模型；位置嵌入在完整 bbox-crop 网格上先分配再丢弃背景 token，使稀疏 token 集在位置上与同裁剪的稠密编码不可区分。因裁剪面积增长 $\eta^2$，保留 token 数 $\rho_{\mathrm{fg}}\eta^2N_{\mathrm{crop}}$ 约等于稠密裁剪预算 $N_{\mathrm{crop}}$，而证据以 $\eta$ 倍更细分辨率被观察。多区域时取单一外包包围盒而非逐区域独立裁剪——独立裁剪同样省 token，但各自带坐标系，会削弱共享网格通过位置嵌入编码的区域间空间关系。源图 token 不重编码，其 KV cache 在部分 LLM 层复用。

**适用前提与取舍。** 方法要求：(1) 存在可用的 SD-RPN 式单次无答案 RoI 预测器作为起点；(2) 训练需要问答对以计算功能分数，但**不需要区域标注**；(3) reader 保持冻结，因此无法修复需要微调全模型才能修复的识别失败——作者明确指出这在 MME-RealWorld 最小规模上可见。此外，压缩不对称性探针只是单一骨干、单一基准上的诊断，作者自称并非普遍规律。

## 实验设置

**模型与训练。** 在 Qwen3.5 4B/9B、Qwen2.5-VL-7B 与 encoder-free 的 Gemma-4-12B 上验证。每个模型的 RoI 预测器沿用 SD-RPN 配置，RL 从监督训练的 SD-RPN 检查点起步，完整冻结的 MLLM 作为 reader $p_\phi$。RL 池为 VisualCoT 训练语料中的 7K QA 对（InfographicVQA 5K，TextVQA 1K，DocVQA 1K）；每个 10K 候选划分内按初始 SD-RPN 下区域移除奖励的标准差排序，取前一半。训练时源图编码在 576 视觉 token 限制下，故所有区域动作与奖励都在该区间内。所有模型单 epoch 训练，统一配方：batch size 32，学习率 $1.5\times10^{-5}$。

**评测协议。** 主协议（表 1）沿用近期细粒度感知工作的设置：所有方法共享 16,384 源图 token 限制，输出自由形式回答，用规则解析加 LLM judge 对剩余样本打分。训练对齐协议用于消融与 token 预算分析，改在 576 token 训练限制下评测（token 预算曲线扩展到 $\{576,1024,2048,4096\}$），采用短答案提示、直接回答与纯规则打分，使被消融组件处于目标函数所优化的区间。Gemma-4-12B 无原生分辨率模式，其行使用最大视觉 token 档 1,120 tokens。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
| --- | --- | --- | --- | --- |
| V* Bench, ZoomBench, HR-Bench 4K, HR-Bench 8K, MME-RealWorld EN, MME-RealWorld CN | Vision-RL2 (Ours) 9B | Gemini-3.1-Pro, Vision-OPD-9B, Qwen3.5-9B | 16,384 source-image token limit | accuracy（规则解析 + LLM judge） |
| 同上六基准 | Vision-RL2 (Ours) 4B | Vision-OPD-4B, Qwen3.5-4B | 16,384 source-image token limit | accuracy |
| 同上六基准 | Vision-RL2 (Ours) 7B (Qwen2.5-VL) | ZwZ-7B, DeepEyes, Thyme, DeepEyesV2 | 16,384 source-image token limit | accuracy |
| 同上六基准 | Vision-RL2 (Ours) 12B (Gemma-4) | SD-RPN 12B, Gemma-4 12B | 1,120 visual-token tier | accuracy |
| 六基准平均（效率分析） | Vision-RL2 4B | SD-RPN, base model, Vision-OPD | source-image token limits {576,1024,2048,4096} | accuracy vs visual tokens / latency |
| 高分辨率套件（HR-Bench 4K, HR-Bench 8K, MME-RW Lite） | Vision-RL2 (Ours) on Qwen2.5-VL-7B | VisionZip, DART | 4,096-token source limit；本文测得 41.2% 与 24.7% | accuracy retention |
| 文档套件（OCRBench, ChartQA, DocVQA, TextVQA） | Vision-RL2 (Ours) on Qwen2.5-VL-7B | VisionZip, DART | 4,096-token source limit；本文测得 46.6% 与 27.2% | accuracy retention |

**关键超参（附录 B.1）。** 控制边界尺度 $\kappa=1.25$（Qwen3.5-4B），$\kappa=1.0$（Qwen3.5-9B、Qwen2.5-VL-7B、Gemma-4-12B）；冻结 MLLM 块数 $B=21$（Qwen3.5 系列）、$B=18$（Qwen2.5-VL-7B）、$B=27$（Gemma-4-12B）。加法组注意力图取自层 7、11、15、19、23、27。区域算子平滑 $\sigma_g=1.0$、阈值 $\rho=0.3$，丢弃 peak-to-mean $<3.0$ 的弥散图，减法组 $K_{\max}=6$。

**需注意的评测口径差异。** 表 1 中 base-model 与 Vision-OPD/ZwZ 行由作者在公开权重上重评，大规模参考模型引自 Vision-OPD，其余引自各自论文；因此跨行比较并非全部同源复现。此外，4B 与 7B 模型在 MME-RealWorld 两个划分上落后于全量微调基线，作者将其归因于冻结 reader 的设计取舍。

## 证据与结果

下表汇总摘录中可确认的数字。所有数值均照抄原文，未在摘录中出现的量一律标注「摘录未给出」。

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| 定位 vs 识别的压缩容忍度 | 定位约容忍 3–4× 更强压缩 | ZoomBench, Qwen3.5-4B, ≤128 visual tokens | §1, Fig. 1a,b |
| box 重预测成功点 | 25× token reduction 仍正确 | localization sweep | Fig. 1a |
| crop 阅读失败点 | 9× 时失败 | recognition sweep | Fig. 1a |
| 存活样本量 | n=238 | 单独压缩 locator 场景或 recognizer crop | Fig. 1b |
| 视觉 token 减少（vs SD-RPN） | 4.2× fewer | Qwen3.5-4B，匹配 SD-RPN 精度 | Fig. 1c |
| 区域级 RL 增益 | +3.0 average | Qwen3.5-4B, 576-token 源限制 | §4.4, Table 2 |
| 稀疏视觉编码增益 | +1.5 | 同上 | §4.4, Table 2 |
| 全系统 vs 冻结基座 | +14.9 | 同上 | §4.4, Table 2 |
| 奖励替换为生成准确率 | −2.3 | 同上 | §4.4, Table 2 |
| 奖励替换为原始 log-prob | −1.5 | 同上 | §4.4, Table 2 |
| 加入 pair removals | +0.1 | 同上 | §4.4, Table 2 |
| cell-level keep-sets | −1.2 | 同上 | §4.4, Table 2 |
| 去掉 control-region margin (κ=0) | −1.1 | 同上 | §4.4, Table 2 |
| 去掉 additive group | −0.9 | 同上 | §4.4, Table 2 |
| 4B 主表六基准 | 91.1 / 65.1 / 84.3 / 80.3 / 65.8 / 65.3 / 75.3 | 16,384 源 token 限制 | §4.2, Table 1 |
| 9B 主表六基准 | 95.3 / 68.4 / 86.8 / 86.1 / 73.4 / 70.6 / 80.1 | 同上 | §4.2, Table 1 |
| 7B (Qwen2.5-VL) 六基准 | 91.6 / 59.8 / 78.8 / 75.0 / 62.2 / 58.7 / 71.0 | 同上 | §4.2, Table 1 |
| 12B (Gemma-4) 六基准 | 82.2 / 60.7 / 85.0 / 79.4 / 67.6 / 61.6 / 72.8 | 1,120 visual-token tier | §4.2, Table 1 |
| Gemma-4-12B vs SD-RPN | +3.8 points | average | §4.2 |
| Gemma-4-12B vs base | +9.5 | average | §4.2 |
| 576 限制 vs 基座 4,096 限制 | 高 >3 points，token 约 1/4 | 效率分析 | §4.3 |
| 延迟 vs SD-RPN | 2.1× lower | 4B, 1,024 限制 | §4.3 |
| 延迟 vs SD-RPN | 2.4× lower | 9B | §4.3 |
| 延迟 vs base | 2.3× lower | 两模型 576 限制 | §4.3 |
| 速度 vs Vision-OPD-4B | 2.6× faster | 4B, 576 限制 | §4.3 |
| attention routing 延迟 | 1.1–1.8 s/query | 4,096 源限制 | §4.3, Fig. 5 |
| RPN head 路由延迟 | 31–49 ms | 4,096 源限制 | §4.3, Fig. 5 |
| RPN head 相对 attention routing | 约 30× cheaper | 同上 | §4.3, Fig. 5 |
| 剪枝对照 25% tier | VisionZip 73.3% (InfoVQA), 56.5% (OCRBench); 本文 94–99% | Qwen2.5-VL-7B, 4,096 源限制 | Appendix B.5 |
| 高分辨率套件保留 | 41.2% 与 24.7% | 1,024/576 rungs | Appendix B.5 |
| 文档套件保留 | 46.6% 与 27.2% | src/a (a=3,6) | Appendix B.5 |
| 超参 | δ=5, \|R_c\|=2, b_max=1, ε_adv=1, J≤4 | 训练配置 | §3.2, §3.3 |
| 训练池 | 7K QA (5K InfographicVQA, 1K TextVQA, 1K DocVQA) | VisualCoT | §4.1 |
| 训练源 token 限制 | 576 | 训练 | §4.1 |
| batch size / lr | 32 / 1.5×10^-5 | 训练 | §4.1 |
| 主评测源 token 限制 | 16,384 | 主协议 | §4.1 |
| 训练对齐 token 限制 | {576,1024,2048,4096} | 消融与 token 预算分析 | §4.1 |
| κ | 1.25 (4B); 1.0 (9B, 7B, 12B) | 超参 | Appendix B.1 |
| 冻结 MLLM blocks B | 21 (Qwen3.5), 18 (Qwen2.5-VL-7B), 27 (Gemma-4-12B) | RoI predictor | Appendix B.1 |

消融与对照方面：Table 2 顶部机制块显示区域级 RL 单独贡献 +3.0，稀疏编码再 +1.5，二者互补；底部按设计轴分组，奖励轴（−2.3、−1.5）、动作轴（+0.1、−1.2）、信用轴（−1.1、−0.9）分别给出对照。剪枝对照（VisionZip/DART）在 25% tier 崩溃而本文保持 94–99%。需注意效率分析与主表协议不同（MME-RealWorld-Lite、直接作答），原文明确「Values are therefore not comparable with the main table」。

## 证据强度评估

证据分级：B（中等偏强，但存在结构性缺口）。

理由：正面证据较厚——四个骨干（Qwen3.5-4B/9B、Qwen2.5-VL-7B、Gemma-4-12B）在六个基准上的一致提升、机制消融（+3.0/+1.5/+14.9）与设计轴消融（奖励、动作、信用）方向自洽，且效率分析在统一协议、同一 GPU 上给出 token 与延迟曲线。但所有关键数字均为作者自报，摘录中未见方差、置信区间或多种子重复；主表部分基线为作者复评、部分引自他文，评测口径不完全统一；核心诊断（压缩不对称）作者自己限定为「one backbone and one benchmark rather than a general law」。因此不足以评为 A。

主要威胁：

1. 构造效度：功能分数 $h_\phi(M)$ 用冻结 reader 对金答案的 teacher-forced log-odds 定义，奖励信号与评测目标（生成准确率）并非同一量。消融显示用生成准确率替换功能分数反而 −2.3，作者解释为二值正确性缺乏相对信用，但这同时说明该奖励是代理指标，其与真实感知质量的对齐未被独立验证。

2. 外部效度：压缩不对称结论仅在 ZoomBench + Qwen3.5-4B、≤128 visual tokens、n=238 上测得，作者明确称其为 diagnostic 而非 general law。迁移到其他骨干、其他分辨率区间或其他任务（如视频、3D）时该前提是否成立，摘录未给出。

3. 基线选择与可比性：主表 16,384 token 限制下，部分行由作者复评、部分引自原文，Gemma-4 行使用 1,120 token tier（无原生分辨率模式），效率分析又改用 MME-RealWorld-Lite 与直接作答，原文声明与主表不可比。跨行比较需谨慎。

4. 统计显著性与评测污染：摘录未给出任何显著性检验、误差棒或重复次数；+0.1（pair removals）这类量级是否在噪声内无法判断。此外训练池来自 VisualCoT（InfographicVQA/TextVQA/DocVQA），而评测含 OCRBench、ChartQA、DocVQA、TextVQA，训练与评测语料存在同源重叠风险，摘录未说明去重或污染检查。

5. 设计取舍的代价：冻结 reader 无法修复识别失败，作者承认在 MME-RealWorld 最小尺度上可见；这意味着该方法的能力上界受基座 reader 限制，收益主要来自「选对证据」而非「读懂证据」。

## 边界与反例

**会推翻结论的观察。** 核心机制主张是「区域级 RL 提供答案级、区域级信用信号，从而在同等 token 预算下优于 SD-RPN 的 token-wise 代理监督」。若在相同训练池、相同 reader、相同 token 限制下，把 SD-RPN 的伪标签监督换成任意等容量的密集监督（例如直接用 Eq. 1 的注意力图做逐 token 回归，或对 RoI 图做几何监督），并取得与 +3.0 相当的增益，则「区域级信用」这一解释被削弱，增益可能只来自额外训练量或正则化。另一个反例方向：若把功能分数 $h_\phi$ 换成任意单调变换（如直接使用 $P_\phi$ 而非 logit），消融中 -1.5 的差距消失，则说明收益来自尺度而非「log-odds 功能分数」本身。

**最可能失效的条件。** 作者自陈两点：reader 被刻意冻结，因此无法修复识别类失败，这在 MME-RealWorld 最小尺度上可见；压缩不对称性探针只是「单一 backbone、单一 benchmark 上的诊断，而非普遍规律」。据此可推断失效边界：(1) 当失败模式以识别（小字、模糊文本）为主而非定位时，减法/加法策略都无从下手，因为区域选择正确但 reader 读不出；(2) 当答案所需证据高度分散、无法用少量连通区域覆盖时，$K_{\max}=6$、$J\le 4$ 的动作空间与「单一包围盒」裁剪会丢失跨区域空间关系；(3) 控制区域噪声边界 $b$ 依赖 $\kappa$ 与 $b_{\max}=1$，且 $\kappa$ 在 4B 上取 1.25、其余取 1.0，说明该标定对模型规模敏感，换 backbone 需重调。

**未验证但易被误推的方向。** 第一，训练需要 QA 对来打分，作者明确「无区域标注」但未说明 QA 分布偏移下的行为——在 VisualCoT 的 InfographicVQA/TextVQA/DocVQA 上训练，不能直接外推到自然场景或视频。第二，效率结论（4.2×、2.1–2.4× 延迟）在 §4.3 使用 MME-RealWorld-Lite 与 InfoVQA val、短答直答协议，作者已声明「与主表不可比」，不应把该数字与表 1 精度并列引用。第三，Gemma-4-12B 行使用 1,120 visual-token tier 而非 16,384，跨行比较平均分不成立。

## 与知识库的关系

**PPO/GAE 策略优化（笔记 id: rl-policy-optimization-ppo-gae）。** 新增：把「动作」从 token 换成连通视觉区域，奖励不是环境回报而是冻结 reader 对金答案的 teacher-forced log-odds 留一贡献 $\Delta_\phi$，并用控制区域估计噪声边界 $b$ 替代 GAE 的基线。印证：优势归一化思想被保留（$A=(b-\Delta)/(s+\varepsilon_{adv})$，$\varepsilon_{adv}=1$），KL 锚 $\mathcal{L}_{KL}$ 对应 PPO 的信任域约束。张力：本文不做采样——减法组「所有移除都被评估，$\pi^{sub}_\theta$ 从不被采样」，因此没有重要性比率与 clip，与标准 PPO 的 off-policy 修正机制不同，不能直接套用 PPO 的收敛论证。

**Agentic RL / tool use（笔记 id: agentic-rl-tool-use）。** 印证：本文引用近期分析（Ma et al., 2026; Wei et al., 2026）称 thinking-with-images 的增益主要来自被 RL 优化的模型本身而非工具使用，与知识库中「工具调用增益需与模型自身提升解耦」的判断一致。新增：给出替代接口的量化代价——RPN 头在答案调用自身 prefill 上加三个 block，路由 31–49 ms，比注意力路由便宜约 30×，而注意力路由与坐标解码需 1.1–1.8 s/query，为「轻量路由优于全模型搜索」提供了具体数字。

**视觉 token 剪枝（笔记 id: visual-token-pruning-visionzip-dart）。** 新增：剪枝方法仍支付完整视觉编码，只省 LLM 侧 token；本文在编码前重分配分辨率，同时压缩编码器与 LLM 预算。印证并强化了「文本密集场景剪枝崩溃」的结论：25% tier 下 VisionZip 在 InfoVQA 保留 73.3%、OCRBench 56.5%，DART 更低，而本文保持 94–99%。张力：本文的 108.8%/103.4%（高分辨率套件）与 97.1%/87.1%（文档套件）是相对自身参考的保留率，与剪枝论文常用的绝对精度不可直接比较。

**SD-RPN / 自蒸馏区域提议（笔记 id: sd-rpn-self-distilled-region-proposal）。** 印证：本文承认 SD-RPN 的 token-wise 代理监督「从不验证提议区域是否支持答案」，与知识库中「注意力伪标签可能保留伪激活或漏掉弱注意力证据」的判断同向。新增：把该缺陷转化为可优化目标，并给出 +3.0（区域级 RL）与 +1.5（稀疏编码）的分解，以及相对冻结基座 +14.9 的总增益。

## 复现与验证计划

目标：在最小成本下验证两条核心可检验主张——(i) 区域级 RL 相对 SD-RPN 的增益，(ii) 稀疏视觉编码在同等源 token 预算下的精度/效率优势。以下计划只使用证据表中已给出的配置，未给出的项标注为不确定。

环境与模型。取 Qwen3.5-4B 作为最小验证骨干（证据表同时给出 4B/9B/7B/12B 行，4B 成本最低）。RoI 预测器沿用 SD-RPN 配置，RL 从监督 SD-RPN checkpoint 初始化，冻结完整 MLLM 作为 reader $p_\phi$。关键超参按原文：$\delta=5$、$|\mathcal{R}_c|=2$、$b_{\max}=1$、$\varepsilon_{adv}=1$、$J\le 4$、$K_{\max}=6$、$\kappa=1.25$（4B）；训练源图 token 上限 576、batch size 32、学习率 $1.5\times10^{-5}$、单 epoch。

数据。训练池 7K QA：5K InfographicVQA + 1K TextVQA + 1K DocVQA（VisualCoT 语料）。评测用 V* Bench、ZoomBench、HR-Bench 4K/8K、MME-RealWorld EN/CN。注意训练只需 QA 对，不需要区域标注。

基线与预算。主协议共享 16,384 源图 token 上限；消融与 token 预算曲线用训练对齐协议（576，扩展到 {576,1024,2048,4096}），短答案提示、纯规则打分。

判据（可证伪）。1) 区域级 RL 单独相对 SD-RPN 应约 +3.0 平均，稀疏编码再 +1.5，全系统相对冻结基座 +14.9；2) 4B 在 4,096 上限下以约 4.2× 更少视觉 token 匹配 SD-RPN 精度；3) 消融方向：功能分数换成生成准确率应约 -2.3，log-odds 换成原始平均 log 概率应约 -1.5，去掉控制区域 margin 应约 -1.1，去掉加法组应约 -0.9，cell-level 对照应约 -1.2。若这些差值符号或量级明显不符，则核心机制未被复现。

预期失败模式。reader 冻结导致无法修复识别类失败，在 MME-RealWorld 最小尺度上尤其明显；压缩不对称探针只是单骨干单基准诊断，不应外推为普遍规律；训练需 QA 对来打分贡献。此外证据表未给出随机种子数、方差与显著性检验，复现时应自行重复并报告方差。

## 术语与记号

本节的记号沿用原文：区域 $R$ 是视觉网格上的连通单元集合，作为动作单元；$M(\mathcal{A})=\bigvee_{R\in\mathcal{A}}m_R$ 是保留区域集合的网格指示掩码并集；$I[M]$ 为掩码图像（掩码外像素置通道均值）。冻结 reader $p_\phi$ 在金答案上 teacher-forced，功能分数为 $h_\phi(M)=\operatorname{logit}(P_\phi(M))$，其中 $P_\phi(M)=\exp(\frac{1}{T}\sum_t \log p_\phi(y_t^\star\mid I[M],q,y_{<t}^\star))$。区域贡献为留一形式 $\Delta_\phi(R\mid M_{\mathrm{ref}})=h_\phi(M_{\mathrm{ref}})-h_\phi(M_{\mathrm{ref}}\ominus R)$，裁剪到 $[-\delta,\delta]$，$\delta=5$。噪声边界 $b$ 由控制区域估计，$b_{\max}=1$；减法组优势 $A^p_k=(b-\Delta^p_k)/(s_p+\varepsilon_{adv})$，加法组优势 $A^s_j=\Delta^s_j/(s_s+\varepsilon_{adv})$，$\varepsilon_{adv}=1$。稀疏编码的空间放大倍数 $\eta=\min(\sqrt{1/\rho_{fg}},\eta_{\max})$，$\rho_{fg}$ 为包围盒内前景占比。

| 术语 | 含义 |
| --- | --- |
| MLLM | 多模态大语言模型 |
| RoI | 感兴趣区域，答案相关证据所在区域 |
| RPN | 区域提议网络，此处指轻量 RoI 预测器 |
| SD-RPN | 自蒸馏区域提议网络，用响应-图像注意力伪标签训练的答案无关预测器 |
| response-to-image attention | 响应 token 对视觉 token 的注意力，可反映答案相关证据 |
| functional contribution | 区域对金答案功能支持度的留一贡献 |
| teacher forcing | 以金答案前缀为条件计算答案 token 概率 |
| log-odds | 概率的 logit 变换，此处用作功能分数 |
| control region | 预测区域外、低概率处生成的控制区域，用于估计噪声边界 |
| subtractive policy | 减法策略，移除贡献低于噪声边界的预测区域 |
| additive policy | 加法策略，恢复被漏检但有正贡献的补充区域 |
| sparse visual encoding | 稀疏视觉编码，只编码前景 token 并以更细分辨率重编码 |
| KV cache reuse | 复用源图像 token 的键值缓存以减少重复编码 |
| privileged-view distillation | 特权视图蒸馏，用区域增强教师离线训练主干 |
| ZoomBench / HR-Bench | 细粒度与高分辨率视觉感知评测基准 |

符号：$P_\theta=\sigma(Z_\theta)$ 为 RoI 概率图，$Z_\theta$ 为 logit 图；$z_\theta(R)$ 为区域平均 RoI logit 置信度；$\pi^{sub}_\theta$ 为减法组移除策略；$A_k$ 为区域动作优势；$K_{\max}=6$、$J\le4$ 分别为预测与补充区域上限。

## 自测

以下问题用于检验你是否真正掌握了本档案的证据边界，而非记住结论。答案折叠在 `<details>` 中，建议先自行作答。

**Q1（证据强度）** 论文声称「定位比识别能承受约 3–4× 更强的 token 压缩」。若你要把这一结论迁移到自己的 backbone 上，作者本人给出了什么限定？请指出该结论的支撑实验规模。

<details><summary>答案</summary>
作者在 Appendix D 明确写道：「The compression-asymmetry probe is a diagnostic on one backbone and one benchmark rather than a general law」。支撑实验为 ZoomBench + Qwen3.5-4B，最多 128 visual tokens，存活样本 n=238（Fig. 1b）。因此这是单 backbone、单 benchmark 的诊断，不是可外推的定律；迁移前需自行复现该 sweep。
</details>

**Q2（数字核对）** 表 1 中 Vision-RL2 9B 在六个基准上的分数序列是什么？它是否在所有基准上都超过 Vision-OPD-9B？

<details><summary>答案</summary>
序列为 95.3 | 68.4 | 86.8 | 86.1 | 73.4 | 70.6 | 80.1（V* Bench, ZoomBench, HR-Bench 4K, HR-Bench 8K, MME-RW EN, MME-RW CN，末位为平均）。并非全部超过：正文说明 9B 模型「a lead over Vision-OPD-9B on every remaining benchmark except HR-Bench 4K」。注意 4B 模型在 MME-RealWorld 两个 split 上落后于 Vision-OPD-4B，作者归因于 frozen-reader 设计。
</details>

**Q3（跨小节推理：机制与消融的对应）** 消融显示「移除 control-region margin 损失 -1.1」、「移除 additive recovery group 损失 -0.9」。请从 §3.3 的机制出发解释这两个组件各自解决什么问题，并说明为什么 additive 组不施加 control-region margin。

<details><summary>答案</summary>
control-region margin（Eq. 4，|R_c|=2，b_max=1，κ 见 Appendix B.1）用预测区域外的低概率控制区域估计样本级噪声边界 b，使 Δ 的微小波动不被误判为真实贡献——没有它，减法组会把噪声当作信号。additive 组（Eq. 7，J≤4）从冻结 response-to-image 注意力图恢复被漏检的证据，其优势为 Δ_j / (s_s + ε_adv)，不施加 margin：正文解释「For a candidate with no true contribution, exclusion is already the zero-gradient default of the loss below, so a margin would only bias against weak genuine recoveries」。两者分别对应「剪除假阳性」与「召回假阴性」，故消融中各自独立贡献 -1.1 与 -0.9。
</details>

**Q4（跨小节推理：效率主张的成立条件）** 论文称 4B 模型以 4.2× 更少 visual token 匹配 SD-RPN 精度，并称 RPN head 路由仅 31–49 ms、比 attention routing 便宜约 30×。这两项主张分别在什么协议下测得？能否直接与表 1 的 16,384 token 主协议结果并列引用？

<details><summary>答案</summary>
不能直接并列。4.2× 的效率主张来自训练对齐协议（source-image token limits {576,1024,2048,4096}，短答案提示、纯规则打分），见 §4.3 与 Fig. 4；而表 1 主协议使用 16,384 source-image token limit、自由形式回答、规则解析加 LLM judge。31–49 ms 与「约 30× 更便宜」同样是在 4,096-token source limit 下测得（§4.3, Fig. 5），attention routing 为 1.1–1.8 s per query，约为本文端到端延迟的 2.1–2.2×。跨协议引用会混淆 token 预算与评分方式两个变量。
</details>

**Q5（可迁移性与失败模式）** 若你的场景是文档 OCR 类高文本密度任务，本文方法相对 VisionZip/DART 的预期表现如何？本文方法在什么情况下会明确失效？

<details><summary>答案</summary>
文档类预期较好：在 Qwen2.5-VL-7B、4,096-token source limit 下，25% tier 时 VisionZip 在 InfoVQA 保留 73.3%、OCRBench 保留 56.5%，DART 更低，而本文保持 94–99%；document suite（OCRBench, ChartQA, DocVQA, TextVQA）在 50%/25% tier 保留 97.1%/87.1%。原因是本文在编码前重新分配分辨率，而剪枝仍支付完整视觉编码。明确失效场景：reader 被冻结，无法修复需要微调整个模型才能解决的识别失败，作者指出这在 MME-RealWorld 最小尺度上可见；此外训练需要 QA 对来打分贡献（但不需要区域标注）。
</details>
