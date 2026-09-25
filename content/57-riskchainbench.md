---
id: riskchainbench
title: RiskChainBench：混淆消息还原与网页调查基准
summary: 在线平台需要治理色情、诈骗、赌博等滥用信息，但规避者用表情符号、同音字、形近字、拆字和冗余符号混淆文本，使消息对人可读却逃避基于表面模式的审核。这些消息常含篡改域名、访问码或操作指令，将用户导向外部网页。
stage: SYSTEMS
track: 评估与安全
kind: paper
depth: deep
evidenceGrade: C
order: 57
minutes: 60
updated: '2026-09-24'
review: LLM 全文精读草稿 · 待人工复核
origin: llm-fulltext
paper_id: 2609.16900
reading_depth: full-text
evidence_level: full-text-llm-draft
claim_count: 4
full_text_url: https://arxiv.org/html/2609.16900
objectives: [理解跨渠道平台风险调查的两阶段评测协议：混淆消息还原与证据锚定网页调查, 掌握入口门（entry gate）机制如何在不重跑网页调查的情况下暴露上游还原损失, 了解十个模型在还原任务与网页调查任务上的排名差异与失败归因分布, 认识现有混淆内容基准与网页智能体基准分离导致的跨阶段损失盲区]
tags: [benchmark, web-agent, obfuscation, evidence-grounding, safety, evaluation]
sources: [riskchainbench-a-benchmark-for-obfuscate]
related: [evaluation, safety, agent-loop]
prerequisites: [agent, evaluation]
---
## 问题与语境

在线平台需要持续治理色情、诈骗、赌博与非法交易等滥用信息，但规避者很少用规范文本表达意图：他们把表情符号与字符交错、用同音字或形近字替换关键词、拆解汉字、插入冗余 token。这类消息对人仍可读，却能绕过基于表面模式的审核，并且往往携带篡改域名、访问码或操作指令，把用户导向外部网页。因此一次可靠的判定并不止于"读懂消息"，而需要串联消息还原、目标识别、网页探索与证据核验——论文把这一整体问题称为 cross-channel platform risk investigation。

已有工作提供了两块基础，但彼此分离。一类是混淆内容基准，研究字符扰动、emoji、同形字、谐音替换与编码语言下的还原或分类；另一类是 web-agent 基准，研究可复现交互以及围绕恶意链接、对抗网页的安全行为。论文明确指出这两者共同留下的缺口：一个小的还原错误会改变下游被调查的目的地，而分离的文本评测与网页评测无法暴露这种跨阶段损失。换言之，现有基准既不能度量"还原错→查错站"的传导，也无法判断网页结论是否真的建立在观察到的证据上。

RiskChainBench 的定位正是补上这条链路：以网站为基本单元，把指向同一站点的消息视为嵌套变体，用固定主变体的 Top-1 入口构成二值"入口门"，在离线端到端评分时把已冻结的还原结果与已冻结的网页轨迹汇合。网页智能体不接收源消息、还原结果、原始域名或解析器输出，从而排除域名声誉捷径，迫使结论落在实际观察到的网页证据上。评测在可重置本地沙箱中进行，使用合成、不可路由的入口，不接触真实服务。

## 核心主张

论文的核心主张可归纳为四点，均来自作者自述与其实验报告，尚无第三方复现记录。

| # | 主张 | 证据 | 状态 |
|---|---|---|---|
| C1 | 同一批十个模型在入口 Top-1 与完整重建上的排名不一致（即可操作入口的恢复能力与整体还原质量不是同一件事） | §4.2 表 1(a)；§5 结论 | 作者主张 |
| C2 | 网页调查中执行失败是最大失败来源，占 31.9% | §4.3 图 5（Task 2 first-failure attribution，每模型 600 次运行） | 作者主张 |
| C3 | 决策正确后仅在类型判定上失败的比例仅 0.9% | §4.3 图 5 | 作者主张 |
| C4 | 离线入口门可在不重跑网页调查的情况下暴露上游还原损失 | §3.2 式 (2)–(3)；§5 结论 | 作者主张 |

C1 有最直接的数字支撑：表 1(a) 中 GPT-5.4 的 Entry Top-1 为 95.22 而 Full 为 66.06，GPT-5.6 SOL 为 94.31 / 73.31，Kimi K3 为 84.58 / 65.64，而 Kimi K2.6 仅 35.19 / 16.06；表 1(b) 的网页侧排序（GPT-5.6 SOL 62.8 Acc.，Claude Sonnet 5 26.3 Acc.）与文本侧排序同样不重合。这种"排序不一致"是可直接从表格读出的描述性事实，但论文并未给出统计显著性检验，因此"不一致"应理解为观测到的排序差异，而非已确立的稳健结论。

C4 是机制性主张，其可信度依赖协议设计而非实验结果：入口门 $g_i=\mathbb{I}[\rho(\widehat{z}_i^{(1)})=i]$ 只使用预先冻结的主变体 Top-1 入口，且明确"lower-ranked candidates do not repair the gate"，因此"不重跑浏览器即可门控"在实现层面成立。但论文没有报告门控视图下的端到端数值，也没有给出该门控与真实端到端调查一致性的验证，故其"暴露上游损失"的效用仍是设计意图而非已量化结论。

C2 与 C3 最弱。二者来自首次失败归因（first-failure attribution），而论文自陈的限制包括：每个模型–网站对只跑一条轨迹、若干违规类型样本稀疏、证据诊断以 judge 成功覆盖为条件。单轨迹意味着 31.9% 与 0.9% 无法区分模型间差异与运行方差，作者也把"measure rerun variance"列为未来工作。因此这两个比例应视为该次运行下的归因快照，不宜外推为稳定的失败分布。

## 机制与方法

RiskChainBench 以「网站」为基本单元，把指向同一站点的多条消息视为嵌套变体，从而把消息还原与网页调查通过「目标身份」绑定起来。第 $i$ 个网站实例记为

$$b_i=(\mathcal{M}_i,\mathcal{X}_i,y_i),\qquad \mathcal{X}_i=\{(x^{*}_{ij},\widetilde{x}_{ij})\}_{j=1}^{K_i},\qquad y_i=(d_i,c_i)$$

其中 $\mathcal{M}_i$ 是本地环境，$x^{*}_{ij}$ 是规范源消息，$\widetilde{x}_{ij}$ 是其 token-text 混淆版本。网站决策 $d_i\in\mathcal{D}=\{\mathrm{V},\mathrm{N},\mathrm{U}\}$ 分别表示违规、非违规与证据不足；主类型满足 $d_i=\mathrm{V}$ 时 $c_i\in\mathcal{C}$，$d_i=\mathrm{N}$ 时 $c_i=\mathrm{NONE}$，$d_i=\mathrm{U}$ 时 $c_i=\mathrm{UNKNOWN}$。构造上固定 $S=600$ 个网站簇、每个源会话 $K_i=6$ 个变体，得 $N=\sum_i K_i=3{,}600$。

**Task 1（混淆消息还原）**：模型只接收 $\widetilde{x}_{ij}$，输出规范消息 $\widehat{x}_{ij}$、操作意图 $\widehat{\iota}_{ij}$ 与排序入口列表 $\widehat{Z}_{ij}=(\widehat{z}^{(1)}_{ij},\ldots,\widehat{z}^{(k)}_{ij})$，且不得访问网页、域名声誉服务或外部信息。指标为

$$\mathrm{CER}=\frac{\sum_i\sum_j \mathrm{ED}(\widehat{x}_{ij},x^{*}_{ij})}{\sum_i\sum_j |x^{*}_{ij}|},\quad \mathrm{Entry@1}=\frac{1}{N}\sum_i\sum_j \mathbb{I}[\rho(\widehat{z}^{(1)}_{ij})=i]$$

以及完整重建率 $\mathrm{FR}$（要求规范消息、意图与 Top-1 入口同时正确）。由于入口是保留的三标签 `.test` 名称、不含 URL scheme，作者报告 entry 而非 URL 指标。

**入口门（entry gate）**：每个网站预先固定一个主变体，其 Top-1 入口经私有解析器 $\rho$ 计算二值门

$$g_i=\mathbb{I}\!\left[\rho(\widehat{z}^{(1)}_i)=i\right]$$

若 $g_i=0$，门控端到端输出为 $\bot$，而冻结的网页轨迹与分数不变；低排名候选不能修复门。这是关键设计取舍：还原结果在任何网页观察之前冻结，网页分支无法回头修改已提交的还原，从而避免「先看网页再猜消息」的泄漏。

**Task 2（证据锚定网页调查）**：在统一指令 $u$、控制器生成的无标签动作类别脚手架 $h_i$ 与本地环境 $\mathcal{M}_i$ 下，智能体在 BrowserGym/Playwright 中产生有界轨迹 $\tau_i=(o_0,a_0,\ldots,a_{T_i-1},o_{T_i})$，$T_i\le H$。控制器不向网页智能体暴露源消息、还原结果、原始域名或解析器输出，因此网站结论必须基于实际观察到的证据。轨迹冻结后，同一模型在不重跑浏览器的前提下输出冻结结论 $\widehat{y}_i=(\widehat{d}_i,\widehat{c}_i)$、理由 $\widehat{r}_i$ 与证据引用 $\widehat{E}_i=\{(t_k,\ell_k)\}_{k=1}^{L_i}$，其中 $t_k$ 指向轨迹步骤、$\ell_k$ 定位支撑内容；只有轨迹中记录的观察可作证据。两分支仅在离线端到端评分时通过 $g_i$ 汇合。

**适用前提**：环境为离线构建、可重置的本地沙箱，入口为合成、不可路由的保留域名，不接触真实服务；标注 $y_i$ 是 $\mathcal{M}_i$ 的属性，不对消息修辞施加标签一致性假设。因此该方法适用于「消息→目标→网页证据」链路的可复现评测，而非真实平台流量的在线判定。

## 实验设置

两个任务评测同一批十个底层模型。Task 1 为纯文本还原，使用来自 600 个合成源会话、每会话六个变体的 3,600 条输入；Task 2 将同一批模型作为 VLM 驱动的网页智能体，在对应的 600 个人工标注本地网站上评测，每个模型–网站对产生一条调查轨迹。Task 2 的准确率、决策 macro-F1 与 H-EM 保留全部 600 个网站并把 $\bot$ 计为错误；Type F1 在 394 个 gold-violation 网站上计算。作者未报告任何基线系统（表中 baseline 字段为空），因此下表「基线」列填「未说明」。

| 基准 | 模型/规模 | 基线 | 预算 | 指标 |
|---|---|---|---|---|
| RiskChainBench Task 1（混淆消息还原） | GPT-5.4 | 未说明 | 3,600 条纯文本还原输入，来自 600 个合成源会话、每会话六个变体 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | GPT-5.6 SOL | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | Claude Opus 4.8 | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | Kimi K3 | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | GPT-5.2 | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | Claude Sonnet 5 | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | Doubao Seed 2.0 | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | Kimi K2.5 | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | Qwen3.6 Plus | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 1（混淆消息还原） | Kimi K2.6 | 未说明 | 同上 | Entry Top-1 / Full / CER |
| RiskChainBench Task 2（网页调查） | GPT-5.6 SOL | 未说明 | 600 个人工标注本地网站，每个模型–网站对一次调查 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | GPT-5.2 | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | Kimi K2.5 | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | GPT-5.4 | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | Qwen3.6 Plus | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | Claude Opus 4.8 | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | Kimi K3 | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | Kimi K2.6 | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | Doubao Seed 2.0 | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |
| RiskChainBench Task 2（网页调查） | Claude Sonnet 5 | 未说明 | 同上 | Acc. / Dec. F1 / Type F1 / H-EM |

诊断分析按首次失败阶段（执行、缺失报告、决策、类型）对每次运行归因，决策与类型均正确者为层次成功。作者报告执行是最大的合并失败来源，占 31.9%；决策正确后仅在类型判定上失败的比例为 0.9%。需注意的评测限制（作者自述）：结果基于每个模型–网站对的一条轨迹，若干违规类型样本稀疏，证据诊断以 judge 覆盖成功为条件；人工标注不提供常规的轨迹证据分数，固定多模态证据 judge 只做覆盖条件下的诊断、不评任务标签；抽样人工证据审计仅为验证分支，不用于所报告的常规分数。

## 证据与结果

本节的数字全部来自证据表与全文摘录，未在摘录中出现的量一律标注「摘录未给出」。

基准构造规模（§3 Method）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| $S$（网站簇） | 600 | 基准构造 | §3 Method |
| $K_i$（每源会话变体数） | 6 | 基准构造 | §3 Method |
| $N=\sum_i K_i$（消息变体总数） | 3,600 | 基准构造 | §3 Method |
| Task 2 网页案例数 | 600 | 每模型–网站对一条轨迹 | §3 Method |
| Type F1 评测集规模 | 394 | gold-violation 网站 | Table 1 caption |

Task 1（混淆消息还原，3,600 条纯文本输入，来自 600 个合成源会话、每个 6 个变体；指标为 Entry Top-1 / Full / CER）：

| 模型 | Entry Top-1 | Full | CER |
|---|---|---|---|
| GPT-5.4 | 95.22 | 66.06 | 1.62 |
| GPT-5.6 SOL | 94.31 | 73.31 | 1.11 |
| Claude Opus 4.8 | 92.94 | 65.72 | 1.64 |
| Kimi K3 | 84.58 | 65.64 | 1.59 |
| GPT-5.2 | 73.39 | 45.72 | 16.01 |
| Claude Sonnet 5 | 72.17 | 43.72 | 10.69 |
| Doubao Seed 2.0 | 62.86 | 38.36 | 14.14 |
| Kimi K2.5 | 39.86 | 19.94 | 17.11 |
| Qwen3.6 Plus | 39.06 | 25.33 | 11.79 |
| Kimi K2.6 | 35.19 | 16.06 | 20.19 |

Task 2（网页调查，600 个人工标注本地网站，每模型–网站对一次调查；指标为 Acc. / Dec. F1 / Type F1 / H-EM）：

| 模型 | Acc. | Dec. F1 | Type F1 | H-EM |
|---|---|---|---|---|
| GPT-5.6 SOL | 62.8 | 59.3 | 42.8 | 61.0 |
| GPT-5.2 | 57.3 | 51.2 | 28.0 | 56.3 |
| Kimi K2.5 | 55.2 | 48.8 | 48.1 | 54.3 |
| GPT-5.4 | 53.7 | 51.7 | 26.4 | 53.2 |
| Qwen3.6 Plus | 51.7 | 50.2 | 44.1 | 51.0 |
| Claude Opus 4.8 | 49.8 | 51.4 | 40.6 | 47.5 |
| Kimi K3 | 47.5 | 52.4 | 40.8 | 46.5 |
| Kimi K2.6 | 41.5 | 51.0 | 33.7 | 40.7 |
| Doubao Seed 2.0 | 29.5 | 38.0 | 32.6 | 29.5 |
| Claude Sonnet 5 | 26.3 | 36.5 | 26.0 | 26.2 |

诊断性归因（§4.3 / Figure 5，Task 2 每模型全部 600 次运行的首次失败归因）：

| 指标 | 数值 | 设置 | 出处 |
|---|---|---|---|
| 执行失败占比（合并首次失败归因） | 31.9% | Task 2 首次失败归因 | §4.3 / Figure 5 |
| 决策正确后仅在类型判定失败占比 | 0.9% | Task 2 首次失败归因 | §4.3 / Figure 5 |

消融与对照：证据表的 `ablations` 字段为空，摘录中亦未给出任何消融实验（如去掉入口门、去掉证据引用约束、改变变体数 $K_i$ 或轨迹预算 $H$ 的对照）。因此本档案无法报告消融结论，摘录未给出。可视为「对照」的只有两类：一是同一批十个模型在 Task 1 与 Task 2 上的并列排名（Table 1 两个面板独立排序，分别按 Entry Top-1 与三分类决策准确率排名）；二是 Task 1 内部的 Entry Top-1 与 Full 之间的差异，作者据此主张两指标排名不一致（C1）。此外，入口门 $g_i$ 的离线组合（式 2–3）被描述为可在不重跑网页调查的情况下暴露上游还原损失（C4），但摘录未给出该门控端到端分数的具体数值，摘录未给出。

## 证据强度评估

证据分级：B。

理由：该结论有明确的基准构造公式（$S=600$、$K_i=6$、$N=3{,}600$）、公开的评测协议与可重置本地沙箱，且十个模型在两项任务上的完整数值表可核对，属于「有可复现协议与完整数字、但复现证据与统计检验缺失」的一档，故为 B 而非 A。未达 A 的关键缺口是：证据表 `ablations` 为空，摘录未给出任何消融；未报告重跑方差或置信区间；证据诊断依赖一个固定的多模态证据评判器，且作者自述「人类标注不提供常规轨迹证据分数」，因此证据锚定这一核心卖点的评测链条并非全人工验证。

主要威胁：

1. 构造效度。Task 1 的输入是「完全合成、平台格式化的 token-text 消息」，Task 2 的环境是「离线构建的本地环境」，入口是保留的三标签 `.test` 名称而非真实 URL（§3.2）。混淆形式、严重度、入口位置的分布由作者设定，真实平台中规避者的混淆策略分布是否一致无法从摘录判断。作者亦承认「若干违规类型样本稀疏」（§5），Type F1 仅在 394 个 gold-violation 网站上计算，类型层面的结论尤其脆弱。

2. 外部效度。评测在隔离沙箱中进行，不接触真实服务（§6），这保证了安全性，但也意味着网页调查不涉及真实反爬、登录、动态渲染与对抗性页面演化。此外「每模型–网站对仅一条轨迹」（§5）意味着结果对单次采样敏感，作者自己把「测量重跑方差」列为未来工作，说明当前无法区分模型能力差异与采样噪声。

3. 统计显著性与基线选择。摘录未给出任何显著性检验、方差或置信区间；Task 2 中相邻模型差距很小（例如 GPT-5.2 的 57.3 与 Kimi K2.5 的 55.2，H-EM 56.3 与 54.3），在单轨迹设置下这些排序是否稳定无法确认。基线方面，证据表中 `baseline` 字段全部为空，摘录未给出任何非 LLM 基线、随机基线或人工基线，因此「模型表现如何」缺少绝对参照，只能做模型间相对比较。

4. 评测污染与评判器依赖。证据诊断「以成功评判器覆盖为条件」（§5），即只在评判器成功覆盖的样本上报告，这会系统性排除难以评判的轨迹，可能高估证据锚定质量。同时，网页结论由「同一被测模型」在轨迹冻结后给出（§3.3），存在自评倾向；作者用「不重跑浏览器」「不向网页代理暴露源消息、还原结果、原始域名或解析器输出」来阻断域名声誉捷径，这一设计缓解了部分污染，但无法排除模型对合成环境模板的记忆性适配。作者提出的补救路径是「在同一隔离环境内通过冻结的人类轨迹审计来验证证据评分细则」（§5），该验证在本次报告中尚未完成。

## 边界与反例

**会推翻结论的观察。** 本档案的核心结论是「入口门可在不重跑网页调查的前提下暴露上游还原损失」（C4，作者主张）。若在同一批 600 个网站簇上重跑网页调查，发现门控后的端到端成功率与门控前冻结分数之差不能由 $g_i$ 解释（例如 $g_i=0$ 的样本其冻结网页结论本身也系统性更差），则「离线门控只暴露上游损失、不引入新偏差」这一说法失效。此外，若把主变体从 6 个变体中随机重抽，Entry Top-1 排名发生大幅翻转，则 C1 的「排名不一致」可能只是单变体抽样噪声，而非模型能力差异。

**最可能失效的条件。** 其一，作者明确承认「results use one trajectory per model–website pair」，因此所有 Task 2 数字（含 31.9% 执行失败、0.9% 类型失败）都无重跑方差估计，单次轨迹的随机性无法与模型差异分离。其二，「several violation types are sparsely populated」，按类型分层的结论（尤其 Type F1 只在 394 个 gold-violation 网站上计算）在小样本类型上不稳定。其三，证据诊断「conditioned on successful judge coverage」，即未被证据裁判覆盖的运行被排除在诊断之外，覆盖率低的模型其证据质量可能被高估。其四，全部环境为合成、非可路由入口与本地沙箱，真实平台的消息分布、域名生态与对抗演化均未覆盖。

**作者未验证但易被误推的方向。** 第一，Task 1 与 Task 2 是两套独立评测，作者只给出离线门控的构造，并未报告门控后的端到端数值；读者不应把表 1(a) 的 Entry Top-1 与表 1(b) 的 Acc. 相乘当作端到端成功率。第二，Task 2 的网页智能体不接收源消息、还原结果、原始域名或解析器输出，因此其分数不能解读为「模型在知道消息语义时的调查能力」。第三，作者未做任何消融（ablations 为空），脚手架 $h_i$、统一指令 $u$、交互预算 $H$ 的贡献均未知。第四，作者未验证证据 rubric 的人工一致性，仅说明「sampled human evidence audit is a validation-only branch」，故不应引用任何四维人工审计结论。

## 与知识库的关系

**新增（此前笔记未覆盖）。** 相对 web-agent 基准笔记（webarena/gaia/tau-bench 簇，笔记 id: `kb/web-agent-benchmarks`），本文新增两点：一是把混淆消息还原与证据锚定网页调查通过入口门 $g_i=\mathbb{I}[\rho(\widehat{z}_i^{(1)})=i]$ 链接为两阶段协议，并给出可重置本地沙箱；二是明确「控制器不向网页智能体暴露源消息、还原结果、原始域名或解析器输出」，从而切断域名声誉捷径。这两点应作为新条目写入 `kb/web-agent-benchmarks` 的「跨阶段损失」子节。

**印证（与既有结论一致）。** 相对混淆内容基准笔记（字符扰动、emoji、同形字、谐音替换、编码语言，笔记 id: `kb/obfuscated-content`），本文印证「表面模式审核可被 token-text 混淆规避」这一前提，并把它从分类任务推进到「还原—目标识别—网页探索—证据核验」的链路。同时印证 `kb/web-agent-benchmarks` 中「可靠探索是判断前提」的观察：执行失败占 31.9%，而决策正确后仅在类型上失败仅 0.9%，说明瓶颈在探索而非判断。

**张力（需在笔记中标注冲突）。** 与 `kb/agent-eval-protocols` 中「多轨迹重复评测以估计方差」的通行做法存在张力：本文每个 model–website 对只跑一条轨迹，作者自己在 limits 中承认应「measure rerun variance」，因此其排名（如 GPT-5.6 SOL 62.8 vs GPT-5.2 57.3）在未给方差前不宜作为稳定结论引用。另与 `kb/evidence-grounding` 中「证据评分应由人工审计锚定」存在张力：本文的常规证据诊断由固定多模态裁判给出，人工审计仅为 validation-only 分支，故其证据分数不能与人工锚定的证据质量直接比较。

**可链接笔记 id 建议**：`kb/web-agent-benchmarks`、`kb/obfuscated-content`、`kb/agent-eval-protocols`、`kb/evidence-grounding`、`kb/cross-channel-risk`（新建，用于承载入口门与两阶段协议）。

## 复现与验证计划

**目标**：以最小成本验证两条核心主张——(C1) 入口 Top-1 与完整重建的模型排名不一致；(C4) 离线入口门可在不重跑网页调查的前提下暴露上游还原损失。

**环境**：按 §3 描述，使用可重置本地沙箱（resettable local sandbox），浏览器侧为 BrowserGym + Playwright，本地主机名随机化；入口为保留的三标签 `.test` 名称、无 URL scheme，私有解析器 $\rho$ 仅用于计算 $g_i$。不接触真实服务。

**数据/任务**：Task 1 用全部 $N=3{,}600$ 条 token-text 混淆消息（$S=600$ 网站簇，每簇 $K_i=6$ 变体）；Task 2 用对应的 600 个人工标注本地网站，每个模型–网站对一条轨迹。注意 Type F1 只在 394 个 gold-violation 网站上计算。

**基线**：直接复用表 1 的十模型数值作为对照，无需重跑全部模型。最小验证建议只选 2–3 个模型，且刻意选取排名分歧的组合：例如 GPT-5.4（Entry Top-1 95.22 / Full 66.06）与 GPT-5.6 SOL（94.31 / 73.31）——前者入口更高、后者完整重建更高，正是 C1 的最小反例对。

**预算**：Task 1 每条消息一次前向；Task 2 每模型 600 次有界轨迹（$T_i \le H$）。若只做门控验证，可仅重算 $g_i$，不重跑浏览器。

**判据**：(1) 复现出 Entry Top-1 与 Full 的排名反转，即支持 C1；(2) 对同一批冻结轨迹，比较 $g_i=1$ 与 $g_i=0$ 两种门控下的端到端接纳率，若差异显著且无需二次浏览，即支持 C4。

**预期失败模式**：执行失败应为最大失败来源（作者报告 pooled 31.9%），决策正确后仅类型错误应很低（0.9%）。若本地沙箱的执行失败率远低于此，需怀疑环境配置或动作预算 $H$ 与原文不一致。不确定处：原文未给出 $H$、随机种子与重跑方差，故本计划无法预先声明可接受的复现容差，需自行设定。

## 术语与记号

| 术语 | 含义 |
|---|---|
| cross-channel platform risk investigation | 跨渠道平台风险调查：跨越消息还原、目标识别、网页探索与证据核验的端到端过程 |
| obfuscated message restoration | 混淆消息还原：从表情、同音字、形近字、拆字等混淆文本恢复规范消息、意图与入口 |
| token-text obfuscation | token-text 混淆：用平台 token 字符串、分解字符与冗余符号规避表面模式审核 |
| entry gate | 入口门：由固定主变体 Top-1 入口是否解析到关联网站决定的二值门，控制端到端成功接纳 |
| evidence-grounded web investigation | 证据锚定的网页调查：结论必须基于轨迹中实际观察到的证据 |
| hierarchical success | 层次成功：决策与类型均正确的运行 |
| first-failure attribution | 首次失败归因：将每次运行归入执行、缺失报告、决策或类型中最早失败的阶段 |
| H-EM | 层次精确匹配：同时要求决策与类型正确的严格指标 |
| insufficient evidence | 证据不足：观察环境不足以支持违规或非违规判断的有效语义决策 |
| resettable local sandbox | 可重置本地沙箱：离线构建、可复现、不接触真实服务的调查环境 |

**关键记号**：$b_i=(\mathcal{M}_i,\mathcal{X}_i,y_i)$ 为第 $i$ 个网站实例，$\mathcal{M}_i$ 为本地环境，$\mathcal{X}_i=\{(x^{*}_{ij},\widetilde{x}_{ij})\}_{j=1}^{K_i}$ 为消息变体集，其中 $x^{*}_{ij}$ 为规范源消息、$\widetilde{x}_{ij}$ 为其 token-text 混淆。标注 $y_i=(d_i,c_i)$，$d_i\in\{\mathrm{V},\mathrm{N},\mathrm{U}\}$ 分别表示违规、非违规、证据不足；$c_i\in\mathcal{C}$ 当 $d_i=\mathrm{V}$，否则为 $\mathrm{NONE}$ 或 $\mathrm{UNKNOWN}$。规模固定为 $S=600$、$K_i=6$、$N=\sum_i K_i=3{,}600$。

还原器输出规范消息 $\widehat{x}_{ij}$、操作意图 $\widehat{\iota}_{ij}$ 与排序入口列表 $\widehat{Z}_{ij}=(\widehat{z}^{(1)}_{ij},\dots,\widehat{z}^{(k)}_{ij})$。入口门定义为 $g_i=\mathbb{I}[\rho(\widehat{z}^{(1)}_i)=i]$，其中 $\rho$ 为私有解析器。网页轨迹 $\tau_i=(o_0,a_0,\dots,a_{T_i-1},o_{T_i})$，$T_i\le H$；冻结结论 $\widehat{y}_i=(\widehat{d}_i,\widehat{c}_i)$，理由 $\widehat{r}_i$，证据引用 $\widehat{E}_i=\{(t_k,\ell_k)\}_{k=1}^{L_i}$。指标含 CER、Entry@1、Entry Recall@$k$、完整重建率 FR、Acc.、Dec. F1、Type F1、H-EM。

## 自测

以下问题用于检验读者是否真正掌握了 RiskChainBench 的评测协议与结论边界。答案折叠在 `<details>` 中，建议先自行作答。

**Q1（协议细节）** Task 1 的评测单元与 Task 2 的评测单元分别是什么？为什么入口门 $g_i$ 只由「固定主变体」的 Top-1 入口决定，而其余 5 个变体不参与门控？

<details><summary>答案</summary>
Task 1 的评测单元是消息变体 $(i,j)$，共 $N=\sum_i K_i=3{,}600$ 条；Task 2 的评测单元是网站 $i$，共 600 个 web case，每个 model–website 对一条轨迹。原文：$S=600$、$K_i=6$、$N=3{,}600$。门控只用固定主变体，是因为离线端到端评分保持网站级：每网站预先固定一个主变体作为唯一入口门，其余五个变体只参与 Task 1。这样 $g_i$ 与冻结的网页轨迹一一对应，无需重跑浏览器。
</details>

**Q2（指标解读）** 表 1(a) 中 GPT-5.4 的 Entry Top-1 为 95.22、Full 为 66.06；GPT-5.6 SOL 为 94.31 / 73.31。这两个模型的排名说明了什么？请结合 C1 判断该结论的证据强度。

<details><summary>答案</summary>
GPT-5.4 的 Entry Top-1 更高（95.22 > 94.31），但 Full 更低（66.06 < 73.31），即入口 Top-1 与完整重建的排名不一致，支持 C1「同一批十个模型在入口 Top-1 与完整重建上的排名不一致」。证据强度：这是作者基于表 1(a) 的主张，属于单次评测的观测结果；全文未报告重跑方差（limits 明确指出「results use one trajectory per model–website pair」），因此排名差异的稳定性未被验证，应视为作者主张而非已复现共识。
</details>

**Q3（跨小节推理）** 若某模型 Task 1 的 Entry Top-1 很高但 Task 2 的 Acc. 很低，能否据此断定「还原不是瓶颈」？请结合入口门机制与 §4.3 的首次失败归因回答。

<details><summary>答案</summary>
不能直接断定。入口门 $g_i$ 只在离线端到端评分时把冻结的网页结果接纳或置为 $\bot$，而 Task 2 的 Acc./Dec. F1/H-EM 是在「正确关联」下、每个 model–website 对一条轨迹上计算的，并不经过门控。§4.3 指出执行失败是最大池化失败来源，占 31.9%，而决策正确后仅在类型上失败的比例只有 0.9%。因此 Task 2 低分更可能来自执行阶段而非还原阶段；但也不能反推还原无损失，因为门控视图与 web-only 视图是分开报告的，需同时看 $g_i$ 与冻结轨迹。
</details>

**Q4（跨小节推理）** 为什么网页智能体不接收源消息、还原结果、原始域名或解析器输出？这一设计对「证据锚定」和「域名声誉捷径」分别意味着什么？

<details><summary>答案</summary>
原文明确：控制器不向 web agent 暴露源消息、其还原、原始域名或 resolver 输出；web agent 既不接收源消息也不接收还原结果，因此网站结论必须基于实际观察到的网页证据。对证据锚定：只有轨迹中记录的观察才可作为证据（$\widehat{E}_i$ 的 $t_k$ 指向已观察轨迹步），使「非违规目的地 + 暗示性重定向话术」成为有意义的 hard negative。对域名声誉捷径：由于不暴露原始域名与解析器输出，模型无法靠域名声誉直接判定，必须依赖网页观察。
</details>

**Q5（结论边界）** 本文的证据诊断（evidence diagnostics）在什么条件下有效？作者自己承认了哪些限制？

<details><summary>答案</summary>
证据诊断以「judge 成功覆盖」为条件（conditioned on successful judge coverage）。作者承认的限制包括：结果基于每个 model–website 对一条轨迹；若干违规类型样本稀疏；证据诊断条件于 judge 覆盖；人工标注不提供常规轨迹证据分，固定多模态证据 judge 只做覆盖条件下的诊断且不评任务标签；抽样人工证据审计仅为验证分支，不用于报告的常规分数，本文不主张四维人工审计结果。未来工作应测量重跑方差、扩展欠代表的风险类型与语言，并在同一隔离环境中通过冻结的人工轨迹审计验证证据评分标准。
</details>
