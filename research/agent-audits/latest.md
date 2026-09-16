# Agent audit · 2026-09-16 23:47 UTC

> DeepSeek generated triage only. Human review is required; this file does not publish sources or claims.

**Summary:** Audited 5 HuggingFace daily-paper candidates against the Agentic RL knowledge base (33 existing sources). No candidate duplicates an existing source. All five are 2026 preprints with abstract-only evidence; none were code-checked or reproduced. Two are plausible additions to the Agentic RL frontier (ModularRSI on harness self-improvement; Elo-per-token on test-time scaling of agents) and are routed to review. RSIAgent is adjacent (training-free memory construction, not RL) and is routed to review with a scope caveat. Emergence World is a multi-agent safety stress test, relevant to the KB's multi-agent and reward-hacking threads but not an RL training method; routed to review. ZGCM-1 is a foundation-model training report, not Agentic RL, and is skipped. No candidate should be treated as published knowledge; all remain abstract-only until human reading and, where applicable, code/experiment verification.

Audited 5 discovered HuggingFace daily-paper entries against the Agentic RL knowledge base (33 existing sources). Two entries are clearly out of scope (music generation, realtime speech) and should be skipped. Three entries are plausibly relevant to Agentic RL (execution-grounded safety guard for computer-use agents; off-policy minimal-intervention RL; MoE expert-space exploration) but are abstract-only preprints with no code verification, so they are routed to review rather than archived as knowledge. No candidate is promoted to published knowledge; no URLs or facts were invented.

Audited 5 HuggingFace daily-paper candidates against the Agentic RL knowledge base (foundations→frontier). None are duplicates of existing source IDs. Two candidates (ScienceBuddy, Atria Dawn) are plausible but broad/product-oriented and require human reading; two (Lightning Weave, HarnessVLN) are adjacent but off-core (efficiency distillation; training-free embodied navigation); one (LynnReal-Omni) is video-generation and out of scope. All evidence is abstract-only from untrusted discovery metadata; no code, reproduction, or peer review was verified. No candidate should be treated as published knowledge.

Audited 5 untrusted discovery entries (HuggingFace daily papers, 2026-09-11 to 2026-09-14) against the Agentic RL knowledge base (33 existing sources). All entries are preprints with abstract-only evidence; none are published knowledge. Two entries are plausible Agentic RL candidates warranting human reading (NGU adaptive sampling; GAI formal framework). One entry (Gavel skill routing) is adjacent but not RL training. Two entries are out of scope (robotics VLA; diffusion LM register tokens). No duplicates of existing source IDs were found. No code, artifacts, or reproduction were verified; all decisions rest on metadata and abstracts only.

Audited 5 discovered preprints against the Agentic RL knowledge base (33 existing sources). None are duplicates of existing entries. Two candidates are plausibly in-scope for Agentic RL and warrant human reading (ImpossibleRubrics on rubric reward-signal robustness; Root-Cause Attribution as a search problem for long-horizon agent failures). Three are out of scope or only tangentially related (visual-generation symbolic policy learning, robotic manipulation agent-as-policy, specialist distillation without reasoning trajectories). All evidence is abstract-only from a discovery feed; no code, no reproduction, and no verification of claims. No candidate should be treated as published knowledge.

## Candidates
### REVIEW · ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement
- Evidence: `abstract-only`
- Reason: Directly on-topic for Agentic RL: harness-level recursive self-improvement, benchmark-disjoint evolution tasks, modular decomposition (Agent Loop, Tool Use, Observation/Context Management, Task Completion Detection), and evaluation on SWE-Bench Verified and TB2.0. Overlaps thematically with existing multi-harness and agent-lightning sources but is not a duplicate. Abstract claims consistent improvements and cross-model transfer; no code or reproduction verified. Requires human reading before any KB inclusion.
- Suggested note: 2026-09-14 preprint. Harness RSI via contrastive success/failure trajectories and five-module decomposition; 2,000 benchmark-disjoint evolution tasks. Abstract-only; claims of transfer across foundation models unverified. Read alongside multi-harness and agent-lightning; check whether 'benchmark-disjoint' curation is actually disjoint from TB2.0/SWE-Bench Verified.

### REVIEW · When Agents Slow Down: Understanding LLM Agents' Test-Time Strategies via Elo-per-token Analysis
- Evidence: `abstract-only`
- Reason: Relevant to Agentic RL evaluation methodology: measures marginal Elo gain per token, defines a scaling inflection point, and compares agent test-time strategies against an independent-sampling reference. Provides a measurement framework rather than a training algorithm. Abstract-only; the Bradley-Terry aggregation and the +264/+355 Elo claims are unverified. Worth human reading for the KB's evaluation/benchmark thread.
- Suggested note: 2026-09-14 preprint. Elo-per-token analysis of test-time compute allocation across four agents and four open-ended benchmarks; sessions up to 100M tokens. Abstract-only. Treat the human-contestant superlinear comparison and the parallel-session Elo gains as claims to verify, not established results.

### REVIEW · RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments
- Evidence: `abstract-only`
- Reason: Adjacent to Agentic RL but explicitly training-free: builds frozen environment-specific memory via curriculum/actor/verifier agents without parameter updates. Relevant to the KB's memory, exploration, and self-improvement threads, but it is not an RL training method, so scope fit is partial. Abstract-only; OSWorld-v2 and Agent's Last Exam results and the GPT-6 comparison are unverified.
- Suggested note: 2026-09-14 preprint. Training-free multi-agent recursive self-improvement via frozen memory of action-condition/action-consequence relations; broad-then-deep exploration. Abstract-only. Note scope caveat: no RL updates, so classify as agent-memory/exploration rather than Agentic RL training unless the full paper shows otherwise.

### REVIEW · Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems
- Evidence: `abstract-only`
- Reason: Relevant to the KB's multi-agent and reward-hacking/safety threads: persistent multi-agent deployment, indirect prompt injection, misinformation, memory exposure, goal drift, and non-compositional alignment. Not an RL algorithm contribution, so it belongs in the safety/evaluation periphery rather than the core training path. Abstract-only; the 16-day, 850k-call, 50B-token run and the 'no world fully resilient' claim are unverified.
- Suggested note: 2026-09-15 preprint. Eight parallel ten-agent worlds, three controlled stress events (indirect prompt injection, misinformation, private-memory exposure); reports delayed action on injected content up to 46 hours. Abstract-only. Read alongside lilian-reward and marl-book; treat as safety/evaluation evidence, not as a training method.

### SKIP · ZGCM-1: A Fully Open and Extremely Efficient Foundation Model for Math and Agentic Search
- Evidence: `abstract-only`
- Reason: Primarily a foundation-model pretraining/mid-training report (architecture, FP8 Muon optimizer, context scaling, data recipes). Agentic search and MDP reformulation of interaction traces are mentioned, but the contribution is a base model and training recipe, not Agentic RL methodology. Out of scope for this KB; no duplicate concern.
- Suggested note: Skipped as out of scope: foundation-model training report, not Agentic RL. Revisit only if the MDP mid-training formulation is later shown to be a reusable Agentic RL technique.

### REVIEW · HazardAuditor: From Executable Threats to Safer Computer-Use Agents
- Evidence: `abstract-only`
- Reason: Directly relevant to Agentic RL: execution-grounded safety supervision for computer-use agents across heterogeneous frameworks (Claude Code, Codex, Hermes, OpenClaw), plus a policy-optimization variant (GuardPO) converting deterministic safety outcomes into sequence-level advantages. Overlaps thematically with existing safety/reward-hacking sources (lilian-reward, constitutional) but is not a duplicate. Only the abstract was inspected; no code, no reproduction, and the claimed +16.5pp improvement is unverified. Requires human reading before any archival.
- Suggested note: 2026-09-14 预印本：面向 computer-use agent 的执行级安全审计与 GuardPO 序列级优势优化；跨框架事件归一化。仅核验摘要，未复现；需人工精读并核对代码/评测工件后再决定是否归档。

### REVIEW · MInTRL: Off-policy Intervention can boost On-policy RL
- Evidence: `abstract-only`
- Reason: Relevant to Agentic RL training methodology: sparse local judge-interventions inside on-policy rollouts plus a sequence-level advantage-regression objective avoiding importance sampling. Connects to existing exploration/credit-assignment sources (dapo, gigpo, edge, agent-g2) but is not a duplicate. Abstract-only; no code or reproduction; the 'minimal intervention' claim and moderate-intensity peak are unverified. Human reading needed.
- Suggested note: 2026-09-11 预印本：在 on-policy rollout 中做稀疏局部干预以扩展探索前沿，训练用序列级优势回归替代重要性采样。仅核验摘要，未复现；与 EDGE/Agent-G² 的探索引导路线相关，需人工对比后决定归档。

### REVIEW · Expert-Space Exploration in MoE Reinforcement Learning
- Evidence: `abstract-only`
- Reason: Relevant to RL post-training methodology: architecture-aware exploration over MoE routing space with anchor experts, entropy-adapted perturbation, and routing replay during policy optimization; reports GRPO-relative gains on Qwen3-30B-A3B. Related to existing GRPO/exploration sources (deepseek-math, dapo) but not a duplicate. Abstract-only; no code, no reproduction; reported Pass@1/Pass@8 deltas unverified. Human reading needed.
- Suggested note: 2026-09-11 预印本：MoE 路由空间探索（锚点专家 + 熵自适应扰动 + 路由回放）用于 RL 后训练。仅核验摘要，未复现；与 GRPO 系工作相关，需人工精读并核对实验设置。

### SKIP · StepAudio 3 Music Technical Report
- Evidence: `abstract-only`
- Reason: Out of scope for an Agentic RL knowledge base: long-form music generation with tokenizer/DiT/VAE design. DPO is mentioned only as a final preference-tuning step, not as agentic RL research. Keyword matches (direct preference optimization, planning, curriculum) are incidental. No archival value for this scope.
- Suggested note: 不相关：音乐生成技术报告，DPO 仅为收尾偏好优化，与 Agentic RL 主题无关，不纳入知识库。

### SKIP · StepAudio 3 Realtime Technical Report
- Evidence: `abstract-only`
- Reason: Out of scope: realtime spoken-dialogue foundation model (duplex audio, think-while-speaking). Mentions a voice agent and tool execution, but the contribution is speech/audio modeling, not Agentic RL training or evaluation methodology. Keyword matches (agent, tool, benchmark) are incidental.
- Suggested note: 不相关：实时语音对话基础模型技术报告，虽提及 voice agent 与工具调用，但核心为音频建模，不纳入 Agentic RL 知识库。

### REVIEW · ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents
- Evidence: `abstract-only`
- Reason: Directly on-theme: couples harness evolution (inner recursion) with model RL (outer recursion), matching the KB's harness/agent-training thread (multi-harness, agent-lightning). Abstract claims case studies across four scientific task families but provides no reproducible protocol, code, or independent verification. Plausible candidate for human reading; not publishable as-is.
- Suggested note: 2026-09-15 preprint. Recursive-in-recursive self-improvement: inner loop evolves harness with model fixed, outer loop trains model under improved harness. Verify: (1) whether 'harness evolution' is automated or human-in-the-loop; (2) task families and evaluation rubrics; (3) any code/artifact release. Abstract-only; do not cite as established result.

### REVIEW · Atria Dawn: The Dawn of Agentic Superintelligence
- Evidence: `abstract-only`
- Reason: High-visibility (424 upvotes) agentic model report claiming a 'Verifiable Experience Pipeline' linking tool interactions to executable environments and externally verified outcomes, plus 16-benchmark evaluation. Relevant to agentic RL evaluation and verifiable rewards, but it is a product/model report with self-reported SOTA on five benchmarks and no independent replication. Requires human reading and skepticism about benchmark selection and verification claims.
- Suggested note: 2026-09-14 preprint. Claims Verifiable Experience Pipeline (tool-mediated interaction → executable env → external verification) and top score on 5/16 benchmarks. Treat benchmark claims as self-reported. Check: benchmark list, verification mechanism, whether 'externally verified' is independent, and any artifact release. Abstract-only.

### ARCHIVE · Lightning Weave: Improving the Accuracy-Efficiency Frontier of Reasoning Models through Capability Composition
- Evidence: `abstract-only`
- Reason: On-policy distillation composing capability shifts (log-ratio shifts, Tilted-Target DOPD) for accuracy-efficiency tradeoff. Adjacent to the KB's reasoning-RL and distillation threads but not core Agentic RL (no agent loop, tool use, or environment interaction). Retain as a reference on capability composition/distillation; do not publish as agentic-RL knowledge.
- Suggested note: 2026-09-13 preprint. Capability composition via on-policy distillation of policy shifts; claims HMMT 2025 59.2→64.0 with 10.7% fewer tokens on Qwen3.5-4B. Code 'to be released soon' — unverified. Filed under reasoning efficiency/distillation, not agentic RL.

### ARCHIVE · HarnessVLN: Unifying Training-Free Embodied Navigation through an Agent Harness
- Evidence: `abstract-only`
- Reason: Training-free (zero-shot) embodied navigation harness with tool interface, event memory, and spatiotemporal graph. Relevant to the KB's harness/agent-architecture thread but explicitly training-free, so it is not RL training evidence. Retain as an agent-harness architecture reference; do not treat as RL method.
- Suggested note: 2026-09-14 preprint. Zero-shot training-free navigation harness; reports R2R 60.8%, RxR 53.9%, HM3D-v2 76.0%, HM3D-OVON 59.3%. No RL training involved. Useful for harness design patterns (validation, recovery, memory), not for RL algorithm claims.

### SKIP · LynnReal-Omni: Native multi-modal Video Generation for Agentic Visual Workflows
- Evidence: `abstract-only`
- Reason: Video diffusion generation framework; 'agentic' here refers to visual creation workflows, not RL-trained agents. Out of scope for an Agentic RL knowledge base. Keyword matches (agent, agentic, long-horizon) are incidental.
- Suggested note: Out of scope: multimodal video generation, not agentic RL. No action.

### REVIEW · Learning to Solve Hard Problems in RL for LLMs by Never Giving Up
- Evidence: `abstract-only`
- Reason: Directly on-topic for Agentic RL: adaptive sampling / compute reallocation for GRPO-style LLM RL, with claimed gains on DeepScaler math and Manufactoria coding. Overlaps thematically with existing dapo (dynamic sampling) and deepseek-math (GRPO) sources, so it may extend or duplicate known ideas. Abstract-only; no code, no reproduction, no independent verification. Requires human reading before any archival as knowledge.
- Suggested note: 2026-09-11 preprint. Claims 'Matthew Effect' in RL for LLMs and proposes Never Give Up (NGU) adaptive sampling with async RL. Compare against DAPO dynamic sampling and GRPO. Verify: off-policy robustness claims, benchmark setup, and whether gains survive matched compute budgets. Do not treat as established until reproduced.

### REVIEW · Generalized Agent Iteration: One Formal Framework for Iterative Policy Improvement and Recursive Self-Improvement
- Evidence: `abstract-only`
- Reason: Conceptual/formal framework connecting generalized policy iteration (GPI) to recursive self-improvement (RSI) via two dials (improver inside/outside agent; standard grounded outside or not). Relevant to Agentic RL foundations and complements existing sutton-barto (GPI) and agentic-survey. No empirical results in abstract; value depends on whether the formalization is rigorous and useful. Human reading needed to assess definitions and claims.
- Suggested note: 2026-09-11 preprint. Proposes GAI as a unifying framework for GPI and RSI. Read alongside Sutton & Barto Ch. 4 (GPI) and the agentic RL survey. Assess: formal precision, whether the two dials are well-defined, and whether 'polarity' (anchored / goal drift / self-referential) is operationalizable. Conceptual only; no benchmarks.

### ARCHIVE · The Router Within: Eliciting Native Skill Routing from a Frozen LLM
- Evidence: `abstract-only`
- Reason: Adjacent to Agentic RL (skill routing for LLM agents, rollout-time skill selection) but the method trains only two linear maps on a frozen backbone — it is representation probing / routing, not RL policy optimization. Relevant context for agent skill libraries and harness design; retain for reference without publishing as RL knowledge. Abstract-only; new benchmark SkillTraj is self-reported.
- Suggested note: 2026-09-14 preprint. Gavel: two linear maps read routing signal from frozen LLM forward passes; claims zero-shot transfer and gains over progressive disclosure / retrieve-and-rerank. Not an RL training method. Keep as context for skill-library routing; verify SkillTraj benchmark and comparisons independently before citing.

### SKIP · Dynin-Robotics: Omnimodal Unified Diffusion Vision-Language-Action Model
- Evidence: `abstract-only`
- Reason: Robotics vision-language-action model with diffusion backbone; matched keywords (policy, trajectory, test-time) are incidental. Outside the Agentic RL scope (no RL training loop, no LLM agent policy optimization). Not relevant to this knowledge base.
- Suggested note: 

### SKIP · Register Tokens for Bounded-State Reasoning in Diffusion Language Models
- Evidence: `abstract-only`
- Reason: Masked diffusion language model reasoning with register tokens; RL is mentioned only as optional refinement. Core contribution is dLLM state carry, not Agentic RL. Out of scope for this knowledge base.
- Suggested note: 

### REVIEW · ImpossibleRubrics: Stress-Testing Generated Rubrics as Reward Signals
- Evidence: `abstract-only`
- Reason: Directly relevant to reward design and reward hacking, which the KB already covers (lilian-reward, dpo, deepseek-math). Abstract reports adversarial exploitation rates of generated rubrics as reward signals, a core Agentic RL concern. However, only the abstract was read; benchmark construction, oracle certificates, and the 8-26%/36%/64% figures are unverified and not reproduced.
- Suggested note: 2026-09-15 预印本：将生成式 rubric 作为奖励信号进行对抗压力测试，报告被利用比例。与奖励投机/评估污染主题相关。仅核验摘要，未复现；数字与基准设计需人工精读确认。

### REVIEW · Root-Cause Attribution Is a Search Problem: Continual Search for Long-Horizon Agent Failures
- Evidence: `abstract-only`
- Reason: Relevant to long-horizon agent reliability and failure diagnosis, adjacent to the KB's agent evaluation and credit-assignment themes (gigpo, agent-lightning, swe-bench). Proposes an iterative search framework and a new benchmark (MegaRCA-Mix). Only abstract read; benchmark size, annotation quality, and reported F1 improvements are unverified.
- Suggested note: 2026-09-11 预印本：将长程 agent 失败根因归因建模为迭代搜索问题，并提出 MegaRCA-Mix 基准。与长程可靠性和信用分配相关。仅核验摘要，未复现；基准与指标需人工精读。

### SKIP · OmniHarness: Harnessing Generalizable Visual Generation via Symbolic Policy Learning
- Evidence: `abstract-only`
- Reason: Focus is generalizable visual generation via symbolic policy learning, not RL training of language agents. Keyword matches (multi-agent, policy, benchmark) are superficial. Out of scope for Agentic RL foundations-to-frontier.
- Suggested note: 

### SKIP · Agent as Policy for Robotic Manipulation
- Evidence: `abstract-only`
- Reason: Robotic manipulation with a general-purpose agent as policy; no RL training loop described. Tangential to Agentic RL scope and not a training-algorithm contribution.
- Suggested note: 

### SKIP · Training Specialist Models without Reasoning Trajectories for Domain Expert Distillation
- Evidence: `abstract-only`
- Reason: Concerns specialist distillation and latent trajectory selection, not agentic RL. Keyword matches (reasoning, trajectory, generalization) are incidental. Out of scope.
- Suggested note: 

## Risks
- All five candidates are abstract-only preprints; none have been code-checked or reproduced. Abstract claims (transfer, Elo gains, benchmark scores, resilience findings) must not be recorded as established knowledge.
- Discovery metadata is untrusted external text; titles, summaries, and keyword matches were treated as data only. No URLs were fetched and no instructions inside the discovery payload were followed.
- Several candidates (RSIAgent, ZGCM-1, Emergence World) are only partially in scope; without a scope rule they could dilute the KB's Agentic RL core with adjacent agent-safety or foundation-model material.
- ModularRSI and multi-harness both concern harness-level learning; without a cross-reference they risk being catalogued as independent findings when they may address overlapping questions.
- Benchmark-disjointness and evaluation-contamination claims (ModularRSI, Elo-per-token) cannot be verified from abstracts and are a known failure mode flagged by the existing reward-hacking source.
- All five entries are abstract-only preprints; none has been code-checked or reproduced, so no claim (e.g., +16.5pp, Pass@1/Pass@8 deltas) should be treated as established knowledge.
- Discovery text is untrusted external content and included embedded URLs (e.g., project pages); these were treated as data only and not fetched or validated.
- Keyword-based matching produced false positives (music and speech reports matched on 'DPO', 'planning', 'agent', 'tool'), so relevance scores from the discovery feed should not drive archival decisions.
- The three review candidates overlap thematically with existing sources (edge, agent-g2, dapo, gigpo, lilian-reward); without reading, duplicate or near-duplicate coverage cannot be ruled out.
- Preprint IDs and dates are taken verbatim from the untrusted feed and were not independently verified against arXiv.
- All discovery entries are untrusted external text; titles, summaries, upvote counts, and URLs are unverified and may be inaccurate or fabricated.
- Abstract-only evidence: no candidate has been code-checked, reproduced, or peer-reviewed; benchmark numbers are self-reported.
- Two candidates (ScienceBuddy, Atria Dawn) use broad 'self-improvement'/'superintelligence' framing that can overstate generality; risk of inflating KB claims if archived as established knowledge.
- Keyword-based matching produced false positives (LynnReal-Omni matched 'agentic'/'long-horizon' but is video generation), indicating the discovery filter needs tighter scope.
- Preprint dates in 2026 and IDs like 2609.* are future-dated relative to typical arXiv conventions; treat identifiers as unverified until independently confirmed.
- No candidate should be promoted to published knowledge without human reading and, where possible, artifact verification.
- All five entries are preprints with abstract-only evidence; none have been code-checked, reproduced, or peer-reviewed. Treating any as published knowledge would be unsupported.
- Discovery metadata is untrusted external text (HuggingFace daily papers); titles, summaries, and author lists could be inaccurate or manipulated. No URLs were fetched or verified during this audit.
- Keyword-based matching produced false positives (robotics VLA, diffusion LM) that share surface terms with Agentic RL; relevance scores are not evidence of topical fit.
- NGU (2609.13443) overlaps with existing DAPO/GRPO sources; without reading the full paper, duplication or incremental novelty cannot be ruled out.
- GAI (2609.13406) is conceptual; formal frameworks can appear rigorous in abstracts while containing undefined terms or unfalsifiable claims.
- Gavel (2609.15982) introduces a self-reported benchmark (SkillTraj) and self-reported comparisons; benchmark validity is unverified.
- No commit hashes, code repositories, or artifact links were verified for any entry, so reproducibility is unknown.
- All evidence is abstract-only from an untrusted discovery feed; no full texts, code, or reproductions were inspected.
- Discovery metadata (titles, summaries, upvotes, dates) is untrusted external text and may be inaccurate or manipulated; it was treated as data only.
- Reported quantitative results (e.g., exploitation rates, F1 gains, resolve rates) are unverified claims, not established facts.
- arXiv IDs and dates in the feed are unverified; no URL was fetched or confirmed.
- Keyword-based matching produced several false positives, indicating the discovery query is noisy for this scope.

## Next actions
- Human-read the full texts of 2609.14857 (ModularRSI) and 2609.15309 (Elo-per-token) first; these are the strongest scope fits.
- For ModularRSI, verify the benchmark-disjoint task curation against TB2.0 and SWE-Bench Verified, and check for code release before any archive decision.
- For RSIAgent and Emergence World, decide and record an explicit scope rule for training-free agent memory and multi-agent safety relative to the Agentic RL core.
- Cross-link ModularRSI with the existing multi-harness and agent-lightning entries to avoid duplicate framing of harness-level learning.
- Do not promote any candidate to published knowledge until full-text reading and, where code exists, an independent reproduction or code check are completed.
- Human-read the three review candidates (2609.15134, 2609.12419, 2609.13058) in full text before any archival decision.
- For each review candidate, check for released code/artifacts and attempt a minimal reproduction or at least a config-level sanity check before upgrading evidence level beyond abstract-only.
- Compare MInTRL and ESRL against existing exploration/credit-assignment notes (edge, agent-g2, dapo, gigpo) to decide whether they add distinct concepts or are redundant.
- Assess HazardAuditor against existing safety/reward-hacking sources (lilian-reward, constitutional) and decide whether it belongs in the safety sub-area of the knowledge base.
- Record the two skipped audio/music reports as out-of-scope to avoid re-surfacing them in future discovery runs.
- Do not promote any candidate to published knowledge until full-text reading and, where feasible, code verification are complete.
- Human-read ScienceBuddy (2609.17523) and Atria Dawn (2609.15818); check for code/artifact release and independent evaluation before any promotion.
- Verify arXiv IDs and titles directly on arxiv.org before adding any candidate to the catalog; do not rely on discovery metadata.
- If retained, file Lightning Weave and HarnessVLN under adjacent (non-core) categories with explicit 'abstract-only, not RL-training evidence' notes.
- Tighten the discovery keyword filter to exclude video/vision generation and require agent-loop or RL-training signals for inclusion.
- Record commit/version and reproduction status for any candidate later promoted; keep all current entries at 'review' or 'archive' status only.
- Human-read 2609.13443 (NGU) in full; compare its adaptive sampling against DAPO dynamic sampling and GRPO; check whether compute-matched baselines are reported.
- Human-read 2609.13406 (GAI) in full; assess formal rigor and whether the two dials are operationalizable; cross-reference Sutton & Barto GPI chapter.
- If NGU or GAI pass review, add as 'review' notes with explicit abstract-only evidence level and no publication claim.
- Retain 2609.15982 (Gavel) as archived context only; do not cite as RL training evidence.
- Do not add 2609.13053 or 2609.16372 to the knowledge base; they are out of scope.
- Re-run discovery with tighter Agentic RL keyword filters to reduce robotics/dLLM false positives.
- For any candidate promoted beyond review, require code/artifact verification and a reproduction attempt before marking as knowledge.
- Human-read the two review candidates (2609.16816, 2609.13463) in full before any catalog entry.
- If retained, record them as 'new preprint, abstract-only, unreproduced' with explicit evidence level, not as published knowledge.
- Check for overlap between ImpossibleRubrics and existing lilian-reward / reward-hacking notes to avoid duplication.
- Verify arXiv IDs and publication status directly before adding any URL to the catalog.
- Tighten discovery keyword filters to reduce visual-generation and robotics false positives.
