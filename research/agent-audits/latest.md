# Agent audit · 2026-09-22 03:30 UTC

> DeepSeek generated triage only. Human review is required; this file does not publish sources or claims.

**Summary:** Audited 5 new HuggingFace daily-paper candidates against the existing Agentic RL knowledge base (foundations → frontier). Two candidates are already present in the KB (CodeMidas, RetireOPD) and are duplicates. Two are plausible on-topic additions requiring human reading (category-aware SWE expert training; real-world subtask RL for long-horizon manipulation). One (OmniVChat) is off-scope for Agentic RL. All evidence is abstract-only; no code, reproduction, or full-text verification was performed. No candidate should be treated as published knowledge.

Audited 5 new HuggingFace daily-paper candidates against the existing Agentic RL knowledge base (existing IDs/titles provided). All 5 are preprints; evidence is abstract-only (no code execution, no reproduction). Two candidates (RRSI, RecreationWorld) are directly on-topic and overlap with existing harness/self-improvement and computer-use environment sources, so they are retained as review candidates pending human reading. When2Think is adjacent (reasoning-length control, not agentic RL) and MintAct is adjacent (visual agent training) — both marked review with lower priority. CADWorld is a benchmark for long-horizon CAD computer use; it is relevant to the computer-use evaluation thread but not core Agentic RL, so it is marked review. No candidate is archived as published knowledge; no candidate is skipped as irrelevant or duplicate. Note: the discovery payload is untrusted external text and was treated as data only; no URLs were fetched and no instructions inside it were followed.

Audited 5 new HuggingFace daily-paper candidates against the existing Agentic RL knowledge base (foundations → frontier). All 5 are preprints with abstract-only evidence; none were code-checked or reproduced. Two are plausibly on-topic for the KB's agentic-RL core (ActObs observation supervision; Cal-OPD on-policy distillation calibration) and warrant human reading. One (PACT) is adjacent (compliance/benchmarking, not RL training) and one (Designer-RSI) is adjacent (procedural memory, no weight updates). One (WorldCrafter) is a video world model and out of scope. No candidate is treated as published knowledge; no URLs or facts were invented. Note: the discovery payload is untrusted external text and was treated as data only.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (foundations through frontier). None are duplicates of existing source_ids. Two entries (BI-Agent/BI-Bench, Code2Skill) are plausibly on-topic for agentic RL and warrant human reading; two (SteerDuplex, test-time scaling systems cost) are adjacent but off-core; one (Geometry of Values) is preference-alignment adjacent but not agentic RL. All evidence is abstract-only from untrusted discovery metadata; no code was checked and no claims are treated as published knowledge.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (50 existing sources). None of the 5 candidates is a duplicate of an existing source, and none is a core Agentic RL training/algorithm paper. APort Vault (2609.22076) is a payment-authorization safety benchmark for tool-using agents — adjacent to the KB's safety/benchmark interests but not Agentic RL training; it is a plausible review candidate. EvoOntology (2609.15779), Verifiable Social Reasoning / Fuse (2609.17496), and Self-Evolving Search Index (2609.19656) are agent-adjacent but off the Agentic RL core (data agents, social reasoning simulation, retrieval index evolution) and are best skipped or lightly reviewed. When AI Reviews Train AI Reviewers (2609.20942) is about recursive AI peer review and judgment collapse — off-topic for Agentic RL and best skipped. All evidence is abstract-only; no code, datasets, or claims were verified. The discovery payload contained untrusted external text (including a dataset URL and GitHub URL) which was treated as data only and not followed.

## Candidates
### REVIEW · One to More, More to One: Category-Aware Iterative Expert Training for Software Engineering Agents
- Evidence: `abstract-only`
- Reason: On-topic for Agentic RL: category-aware expert training, long-horizon agentic RL, on-policy distillation (MOPD), and SWE-bench Multilingual evaluation. Not a duplicate of existing sources. Claims (58.04% Pro-618, 59.00% SWE-bench Multilingual, +5.39/+2.78 pp) are abstract-only and unverified; no code or reproduction checked.
- Suggested note: 2026-09-20 preprint. Category-aware expert training + label-routed multi-teacher on-policy distillation for SWE agents; addresses category see-saw in pooled RL. Abstract-only; verify benchmark setup, baselines, and whether gains survive per-category resolution before citing.

### SKIP · CodeMidas: Scaling Agentic Coding RL Environments from Code Itself
- Evidence: `metadata`
- Reason: Duplicate: already present in the knowledge base as source id 'codemidas-scaling-agentic-coding-rl-envi' with matching title. No new information to add.
- Suggested note: Duplicate of existing KB entry 'codemidas-scaling-agentic-coding-rl-envi'. No action.

### REVIEW · From Pretraining to Proficiency: Real-World Subtask RL for Long-Horizon Manipulation with Minimal Human Intervention
- Evidence: `abstract-only`
- Reason: Plausibly relevant to Agentic RL foundations: subtask-targeted RL, sparse/outcome rewards, residual policy corrections, and success verifiers for long-horizon tasks. However it is robotics manipulation (YAM/Franka), not LLM agents, so scope fit is partial. Claims (32%→61%, 50%→95%) are abstract-only and unverified.
- Suggested note: 2026-09-18 preprint. PARTS: subtask RL with frozen pretrained policy, agent-generated selectors/verifiers, success-reweighted retraining. Robotics domain — decide whether KB scope includes embodied long-horizon RL. Abstract-only; no reproduction.

### SKIP · RetireOPD: Self-Retiring On-Policy Distillation for Agentic Reinforcement Learning
- Evidence: `metadata`
- Reason: Duplicate: already present in the knowledge base as source id 'retireopd-self-retiring-on-policy-distil' with matching title. No new information to add.
- Suggested note: Duplicate of existing KB entry 'retireopd-self-retiring-on-policy-distil'. No action.

### SKIP · OmniVChat: Synthesizing, Benchmarking, and Training for Native Audio-Visual Dialogue
- Evidence: `abstract-only`
- Reason: Off-scope for Agentic RL: native audio-visual dialogue for omni models. RL reward design is incidental; no agentic RL, tool use, or long-horizon decision-making contribution relevant to this KB.
- Suggested note: Not relevant to Agentic RL scope. Skip.

### REVIEW · RRSI: Regularized Recursive Self-Improvement of Agent Harnesses
- Evidence: `abstract-only`
- Reason: Directly on-topic for the harness self-improvement thread already represented by modularrsi-modular-and-generalizable-rec and sol-pi-recursively-scaling-auto-research. Abstract claims regularization of candidate proposal/selection to reduce benchmark overfitting and reports OOD gains plus token reduction. Claims are unverified; abstract-only; code URL present but not checked. Overlaps with existing KB entries, so human reading is needed to determine whether it adds distinct mechanisms or duplicates ModularRSI.
- Suggested note: 2026-09-21 preprint. Harness-level recursive self-improvement with annealed edit budget, history-based exploration, critic+pruner selection. Claims up to +14.1 in-distribution and +4.7 OOD across eight benchmarks, 30% fewer policy tokens. Abstract-only; not reproduced. Compare against modularrsi and sol-pi before deciding whether to merge or keep separate.

### REVIEW · RecreationWorld: Scalable and Verifiable Environments for Hybrid Computer-Use Agents
- Evidence: `abstract-only`
- Reason: On-topic for the computer-use environment/benchmark thread (webarena, gaia, tau-bench, recreationworld already listed in existing titles). Abstract describes five-platform reproducible environments, execution-grounded rewards from a running reference, and a held-out RecreationBench. Claims are unverified; abstract-only. Overlaps with the existing recreationworld entry, so human reading is needed to confirm whether this is the same work or a distinct version.
- Suggested note: 2026-09-18 preprint. Hybrid GUI+coding computer-use agents; reference-grounded programmatic and visual assertions; RecreationBench 250 tasks. Reports GPT-6 Astra 58.1% overall but only 2.8% full programmatic pass. Abstract-only; not reproduced. Check overlap with existing recreationworld source before adding.

### REVIEW · When2Think: Learning Difficulty-Aware Length Control for Efficient Hybrid Reasoning Models
- Evidence: `abstract-only`
- Reason: Adjacent rather than core: it is reasoning-length/compute-allocation post-training, not agentic RL with tools/environments. Relevant to the reasoning-RL thread (deepseek-r1, deepseek-math, dapo) and to reward shaping. Abstract-only; no reproduction. Lower priority than RRSI/RecreationWorld.
- Suggested note: 2026-09-17 preprint. Instance-level difficulty-aware control (IDAC) with reference statistics, verifier rewards, critic-free optimization. Reports AIME24 Pass@3 +10.0% with 27.9% fewer tokens; AIME25 40.0% Pass@3. Abstract-only; not reproduced. Treat as reasoning-efficiency adjacent, not agentic RL.

### REVIEW · MintAct: A Unified Visual Agent for Digital Environments
- Evidence: `abstract-only`
- Reason: Adjacent: unified visual agent for UI grounding, multi-step navigation, and visual tool use, with async RL infrastructure. Relevant to computer-use agents and to the existing mintact entry in the KB. Abstract-only; no reproduction. Overlaps with existing mintact source, so human reading is needed to confirm novelty/version.
- Suggested note: 2026-09-18 preprint. 2B/4B/8B VLMs; hundreds of concurrent heterogeneous environment instances; async RL stable under noisy feedback and off-policy drift. Reports 48.9 on OSWorld-Verified. Abstract-only; not reproduced. Check overlap with existing mintact source.

### REVIEW · CADWorld: Computer-Use Benchmark for Long-Horizon Computer-Aided Design
- Evidence: `abstract-only`
- Reason: Relevant to long-horizon computer-use evaluation but domain-specific (FreeCAD/CAD) and not core Agentic RL. Abstract describes 200 tasks, executable checks over saved artifacts, and a large gap between best agent (17.5%) and expert reference (87.0%). Abstract-only; no reproduction. Lower priority; retain for the evaluation/benchmark thread.
- Suggested note: 2026-09-14 preprint. FreeCAD benchmark across 11 mechanical-CAD workflow categories; success via task-specific executable checks on saved artifacts. Best agent 17.5% vs 87.0% expert reference. Abstract-only; not reproduced. Domain-specific; consider only if the KB expands into engineering computer-use evaluation.

### REVIEW · Don't Mask the Environment: Observation Supervision Changes How Agents Explore Under RL
- Evidence: `abstract-only`
- Reason: Directly on-topic for agentic RL: questions the SFT convention of masking environment observation tokens and reports GRPO divergence on Terminal-Bench 2.0 and aider-polyglot. Plausible and relevant to existing KB entries (ppo, gae, dapo, agentic-survey), but claims are abstract-only, unreproduced, and the mechanism (orthogonal action/observation gradients) needs human verification.
- Suggested note: Preprint (2026-09-17). ActObs supervises observation tokens already present in trajectories; claims higher pass@k under GRPO vs action-only SFT on Qwen3-4B/8B. Abstract-only, not reproduced. Read for: SFT initialization for RL, exploration/entropy effects, cross-domain transfer claims.

### REVIEW · Calibrating Teacher--Student Discrepancy for On-Policy Distillation
- Evidence: `abstract-only`
- Reason: On-topic for the KB's distillation/RL frontier (cf. RetireOPD, privileged-information entries). Proposes Cal-OPD to remove teacher self-deviation from the teacher-student discrepancy signal. Plausible but abstract-only; the privileged-intervention calibration and the 52-65% signal-retention claim require human reading and ideally code/data checks.
- Suggested note: Preprint (2026-09-18). Cal-OPD estimates teacher self-deviation via positive/negative privileged interventions and calibrates OPD. Abstract-only, math-reasoning benchmarks, not reproduced. Read alongside existing OPD/privileged-information sources.

### REVIEW · PACT: Can Enterprise AI Assistants Be Trusted Under Pressure?
- Evidence: `abstract-only`
- Reason: Adjacent rather than core: a compliance/robustness benchmark for enterprise LLM assistants under user pressure, not an RL training method. Relevant to the KB's safety/evaluation interests (lilian-reward, tau-bench) but the 22-model, 48-scenario results are abstract-only and LLM-as-judge audited, so claims need human scrutiny before any retention.
- Suggested note: Preprint (2026-09-16). PACT benchmark: rule-following under pressure across 12 enterprise domains, PACTScore metric. Abstract-only; LLM-as-judge construction. Consider only if KB scope extends to agent compliance/safety evaluation.

### ARCHIVE · Designer-RSI: Evolving Procedural Memory from User Traffic for Agentic Graphic Design
- Evidence: `abstract-only`
- Reason: Adjacent to agentic RL but explicitly no weight updates and no human labels; it evolves an external natural-language procedural memory. Interesting for the KB's harness/memory themes (cf. ModularRSI, Reflect-Revise-Reuse) but not an RL-training contribution, so retain as a candidate without publishing. Abstract-only; reported gains unreproduced.
- Suggested note: Preprint (2026-09-18). Frozen frontier model + external procedural memory (widening/deepening with matched replay gate) for graphic design; 230+ tools, 1,406 briefs. No weight updates. Abstract-only. Archive for memory/harness cross-reference; do not publish as RL evidence.

### SKIP · WorldCrafter: Consistent Video World Model with Implicit 3D-aware Memory
- Evidence: `abstract-only`
- Reason: Out of scope for an Agentic RL knowledge base: a video world model with implicit 3D-aware memory for scene exploration. Keyword overlap (long-horizon, memory, distillation) is incidental; no agent policy, RL training, or agentic task relevance.
- Suggested note: Skip: video world-model paper, not agentic RL. Keyword matches are incidental.

### REVIEW · BI-Agent and BI-Bench: Towards Automating End-to-End Business Intelligence
- Evidence: `abstract-only`
- Reason: Plausibly on-topic: tool-augmented agent with SFT+RL post-training on synthesized trajectories, plus a new benchmark. Overlaps KB themes (tool use, agentic RL post-training, benchmark design) but abstract-only and no code/repro verified. Requires human reading before any KB inclusion.
- Suggested note: Candidate: end-to-end BI agent (search/join/transform subtasks) with SFT+RL post-training and BI-Bench. Verify RL algorithm, reward design, and whether benchmark is public; check for overlap with tau-bench/GAIA tool-agent evaluation themes.

### REVIEW · Grounded Skill Synthesis from Code at Scale for Agentic Intelligence
- Evidence: `abstract-only`
- Reason: Plausibly on-topic: automated skill synthesis from source code with verification, positioned against trajectory-based skill banks; relates to KB skill/harness themes (coskill, modularrsi). High upvote count is not evidence of correctness. Abstract-only; no code checked.
- Suggested note: Candidate: Code2Skill pipeline producing a verified skill bank from GitHub repos; claims gains over trajectory-derived skills. Verify verification methodology, benchmark protocol matching, and whether skills are executable/grounded as claimed.

### SKIP · SteerDuplex: Steerable Duplex Speech Dialogue Models
- Evidence: `abstract-only`
- Reason: Off-core for Agentic RL: full-duplex speech dialogue steerability. Mentions RL with hybrid rewards and reward hacking, but the contribution is speech-model steering, not agentic RL methodology. Not a duplicate; simply out of scope.
- Suggested note: Out of scope for Agentic RL KB. Reward-hacking observation is incidental; existing lilian-reward already covers that theme.

### SKIP · Sample Count Is Not Enough: Candidate-Generation Strategy Shapes the Energy and Performance of LLM Test-Time Scaling
- Evidence: `abstract-only`
- Reason: Off-core: systems/energy analysis of test-time scaling generation schedules, not agentic RL training. Adjacent to inference-efficiency concerns but does not address RL, agents, or credit assignment. Not a duplicate.
- Suggested note: Out of scope. Could be a peripheral note on inference systems cost if the KB later adds a test-time-compute section, but not now.

### SKIP · Geometry of Values: Task Vector Composition for Ethical Preference Alignment in Language Models
- Evidence: `abstract-only`
- Reason: Preference-alignment/ethics topic, not agentic RL. Uses DPO and task-vector arithmetic but contributes to value-conflict alignment, not agent training or environments. Not a duplicate of dpo/constitutional but out of scope.
- Suggested note: Out of scope for Agentic RL KB. Preference-alignment adjacent; existing dpo/constitutional/instructgpt already anchor that area.

### REVIEW · APort Vault: Benchmarking AI Agent Payment Authorization with the Open Agent Passport
- Evidence: `abstract-only`
- Reason: Tool-using agent safety/authorization benchmark with a large replay corpus (225,964 evaluations) and a deterministic pre-action policy layer. Adjacent to the KB's agent-safety and benchmark interests (tau-bench, webarena, lilian-reward) but not an Agentic RL training method. Abstract-only; the reported zero-violation result and dataset/code links are unverified and must not be treated as established knowledge.
- Suggested note: 2026-09-22: 支付授权安全基准，面向工具型 agent；与 tau-bench/webarena 的评估思路相邻，但不属于 Agentic RL 训练算法。仅核验摘要，未复现；摘要中的数据集与代码链接未验证，勿当作已发布知识。

### SKIP · EvoOntology: A Self-Evolving Ontology Layer for Data Agents
- Evidence: `abstract-only`
- Reason: Data-agent ontology/MCP-server layer with a self-evolution loop. Off the Agentic RL core (no RL training objective, no policy optimization); overlaps only loosely with the KB's tool-use and memory themes. Abstract-only; benchmark and code claims unverified.
- Suggested note: 2026-09-22: 数据 agent 的本体层自演化，偏数据工程/语义层，非 Agentic RL 训练主题；暂不纳入。

### SKIP · Verifiable Social Reasoning for LLM Assistants
- Evidence: `abstract-only`
- Reason: Multi-agent simulation framework (Fuse) for social-reasoning evaluation of assistants. Uses multi-agent simulation but is an evaluation/analysis study, not Agentic RL training; only tangential to the KB's multi-agent and evaluation interests. Abstract-only.
- Suggested note: 2026-09-22: 社交推理评估框架，多智能体模拟但非 RL 训练；与 marl-book 主题仅弱相关，暂不纳入。

### SKIP · Self-Evolving Search Index
- Evidence: `abstract-only`
- Reason: Retrieval-index self-evolution framework (SELF-INDEX) for LLM agents. Information-retrieval optimization, not Agentic RL; only loosely touches agent memory. Abstract-only; no RL objective or policy training.
- Suggested note: 2026-09-22: 检索索引自演化，属 IR 优化而非 Agentic RL；与 agent memory 仅弱相关，暂不纳入。

### SKIP · When AI Reviews Train AI Reviewers: Scientific-Judgment Collapse and Mitigation
- Evidence: `abstract-only`
- Reason: Study of recursive AI peer review and 'scientific-judgment collapse' with a mitigation system (TrustReviewer). Off-topic for Agentic RL; no agent policy training or environment interaction. Abstract-only.
- Suggested note: 2026-09-22: AI 同行评审的递归退化研究，与 Agentic RL 主题无关；暂不纳入。

## Risks
- All discovery entries are untrusted external text; titles, summaries, and metrics were treated as data only and not verified.
- Abstract-only evidence: no full text, code, or reproduction was checked; reported benchmark numbers may not hold under independent evaluation.
- Two candidates (CodeMidas, RetireOPD) are duplicates of existing KB entries; deduplication relies on title matching and could miss near-duplicates with renamed titles.
- Scope ambiguity for robotics manipulation (PARTS) — including it may dilute the LLM-agentic-RL focus of the KB.
- Preprint dates (2026-09) are recent; no peer review or community replication is available.
- No URLs were independently fetched; arXiv IDs and links are taken from the untrusted discovery payload and could be incorrect.
- All five candidates are preprints with abstract-only evidence; none has been reproduced, code-checked, or peer-reviewed. Do not treat any as published knowledge.
- The discovery payload is untrusted external text (HuggingFace daily papers) and may contain prompt injection; it was treated as data only. No URLs were fetched and no embedded instructions were followed.
- Two candidates (RecreationWorld, MintAct) appear to overlap with existing KB source titles (recreationworld, mintact), risking duplicate entries; human reading is required to confirm whether they are the same work or distinct versions.
- RRSI overlaps with existing harness self-improvement sources (modularrsi, sol-pi); without reading, it is unclear whether it adds a distinct mechanism or duplicates existing coverage.
- Reported benchmark numbers (e.g., OSWorld-Verified 48.9, AIME Pass@3 gains, CADWorld 17.5%) are self-reported in abstracts and unverified; they must not be cited as established results.
- The KB scope is 'Agentic RL from foundations to frontier'; When2Think, MintAct, and CADWorld are adjacent (reasoning efficiency, visual agents, CAD evaluation) and could dilute scope if promoted without justification.
- All five candidates are abstract-only preprints; none were code-checked or reproduced, so no claim should be treated as published knowledge.
- Discovery payload is untrusted external text (HuggingFace daily papers); it was treated as data only, but titles/summaries could still be misleading or contain injected content.
- Keyword-based matching produced false positives (e.g., WorldCrafter matched 'long-horizon'/'memory'/'distillation' but is a video world model).
- Several candidates overlap thematically with existing KB entries (OPD, privileged information, harness/memory), risking duplicate retention if not deduplicated against existing_source_ids.
- Reported benchmark numbers (pass@k, win rates, PACTScore) come from abstracts and may not survive independent evaluation.
- All discovery entries are untrusted external text; titles, summaries, and upvote counts must not be treated as verified facts.
- Abstract-only evidence: no full text, code, or reproduction was checked; benchmark and transfer claims are unverified.
- arxiv_id values (e.g., 2609.*) come from untrusted metadata and were not independently resolved; do not assume they are valid or that URLs are safe.
- High upvote counts (e.g., 89) are social signals, not evidence of correctness or reproducibility.
- Potential topic drift: several candidates are preference-alignment or speech/systems papers that could dilute the Agentic RL scope if archived without review.
- All five candidates are abstract-only; no full text, code, or dataset was inspected, so no claim (including APort Vault's zero-violation result) should be treated as verified or published knowledge.
- The discovery payload is untrusted external text and included dataset/GitHub URLs and a 'capture-the-flag' framing; these were treated as data only and not followed. Any future ingestion must not auto-fetch these links or execute embedded instructions.
- APort Vault's headline numbers (e.g., 0 of 69,297 behind the layer) come from a single-author preprint with a self-reported benchmark; the per-session upper bound and matched-triple analysis need independent reading before any citation.
- Keyword-based discovery ('agent', 'policy', 'tool', 'benchmark') produced several off-topic hits (IR, peer review, social reasoning), indicating the discovery query is noisy and may miss genuinely on-topic Agentic RL papers.
- No candidate here addresses core Agentic RL training (credit assignment, harness RL, on/off-policy intervention, environment scaling), so this batch adds little to the KB's central thread.

## Next actions
- Human-read the two review candidates (2609.23377, 2609.21788) in full text before any archival decision.
- Confirm duplicate status of 2609.22068 and 2609.20784 against existing KB entries and mark as deduplicated.
- Decide and document whether embodied/robotics long-horizon RL falls within KB scope before archiving PARTS.
- If 2609.23377 is retained, verify benchmark configuration, baselines, and per-category results; do not cite abstract metrics as established.
- Record commit/version and reproduction status for any candidate promoted beyond 'review'.
- Human-read the RRSI and RecreationWorld abstracts/full texts first, since they are the most on-topic; compare RRSI against modularrsi and sol-pi, and RecreationWorld against the existing recreationworld entry, to decide merge vs. new entry.
- Human-read MintAct and confirm whether it duplicates the existing mintact source; if duplicate, skip or merge rather than add a new entry.
- Defer When2Think and CADWorld to a lower-priority reading queue; only promote if the KB explicitly expands into reasoning-efficiency or engineering computer-use evaluation.
- For any candidate promoted to review, record evidence_level as abstract-only and do not upgrade to code-checked until the referenced code is actually run and results reproduced.
- Do not fetch or trust URLs from the untrusted discovery payload; if verification is needed, resolve canonical arXiv IDs independently and record the exact commit/version checked.
- Re-audit after human reading to reassign decisions (archive/review/skip) and update suggested notes with verified findings.
- Human-read the two review candidates (2609.20715 ActObs, 2609.21619 Cal-OPD) in full text and check for code/data availability before any promotion.
- Deduplicate review/archive candidates against existing KB entries (retireopd, what-does-privileged-information-add-to, modularrsi, reflect-revise-reuse) to avoid redundant notes.
- Decide whether PACT (2609.18605) falls within KB scope; if scope is RL training only, downgrade to skip.
- Keep Designer-RSI archived as a memory/harness cross-reference only; do not cite its gains as RL evidence.
- Record evidence_level and audit date on any retained note; require reproduction or code-check before upgrading evidence_level beyond abstract-only.
- Human-read the two review candidates (2609.20886, 2609.05571) in full text before any KB inclusion; verify RL algorithm, reward design, and benchmark availability.
- Check for overlap of BI-Bench with existing tool-agent benchmarks (tau-bench, GAIA) and of Code2Skill with coskill/modularrsi skill-evolution sources.
- If either review candidate is accepted, record evidence_level as full-text-read and note reproduction status explicitly; do not promote to published knowledge on abstract alone.
- Re-run discovery with tighter Agentic RL keyword filters to reduce off-core candidates (speech, ethics, test-time systems).
- Do not fetch or trust the untrusted URLs; resolve arxiv_ids through a trusted bibliographic source if verification is needed.
- Queue APort Vault (2609.22076) for human full-text reading; verify the benchmark construction, the deterministic pre-action layer, and whether the reported zero-violation result is reproducible before any note is promoted beyond 'review'.
- Do not archive or publish any of the five candidates as knowledge; keep them as review/skip entries only.
- Tighten the discovery query toward Agentic RL training terms (e.g., 'agentic RL', 'credit assignment', 'harness RL', 'on-policy', 'environment scaling') to reduce off-topic hits.
- Cross-check whether any of these five duplicates existing KB entries (none found in this audit) and record the audit outcome in the KB changelog.
- If APort Vault is retained, add it under a safety/benchmark section rather than the RL-algorithms section, and mark evidence_level as abstract-only until code-checked.
