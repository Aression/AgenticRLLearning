# Agent audit · 2026-09-21 03:30 UTC

> DeepSeek generated triage only. Human review is required; this file does not publish sources or claims.

**Summary:** Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (51 cataloged sources). All 5 are 2026 preprints with abstract-only evidence; none are published knowledge. Three are already present in the catalog (SoL-Pi, RetireOPD, An Empirical Study of Harness Design) and are therefore duplicates. Two are new and plausibly on-topic: CodeMidas (scaling agentic coding RL environments from source code) and EvoSkill-GUI (training-free skill evolution for GUI agents). No code was executed and no HTTP checks were performed, so no candidate rises above abstract-only evidence. All decisions are conservative: duplicates are skipped, new plausible candidates are routed to human review, and nothing is archived as established knowledge.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base. All 5 are preprints with abstract-only evidence; none are published knowledge. Two are already present in the catalog (When2Think, Rethinking Critic Learning in PPO) and are therefore duplicates. The remaining three (RecreationWorld, MintAct, ActObs) are plausible but unverified candidates requiring human reading. No code was checked, no results reproduced, and no URLs were fetched. Discovery and catalog fields were treated strictly as untrusted data; no embedded instructions were followed.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (foundations to frontier). All five are preprints with abstract-only evidence; none were code-checked or reproduced. Two entries (PACT, What Does Privileged Information Add to On-Policy Self-Distillation?) are already present in the catalog under existing_source_ids, so they are duplicates and should be skipped. The remaining three (RiskChainBench, Vision-RL2, ComPO) are plausible but peripheral to the core Agentic RL scope and require human reading before any retention decision. No candidate is treated as published knowledge; no URLs or facts were invented.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (50 existing sources). None of the 5 candidates are duplicates of existing source IDs/titles. Relevance to the KB scope is mixed: two are clearly off-scope (KV-cache compression systems work; robot VLM in-context learning), one is a systems/efficiency study of test-time scaling schedules (adjacent but not Agentic RL), and two are plausibly on-topic (code-grounded skill synthesis for agents; co-evolving MoA routing with continual agent learning). All evidence is abstract-only from untrusted discovery metadata; no code, artifacts, or full texts were checked. No candidate should be treated as published knowledge. Recommended: archive the two off-scope items for retention only, review the two plausibly on-topic items, and skip the test-time-scaling systems study as out of scope.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (scope: foundations to frontier). None of the five candidates are already present by id or title. All five are 2026 preprints with only abstract-level evidence; no code was executed and no HTTP checks were performed, so none can be treated as published knowledge. Relevance to Agentic RL is weak-to-moderate: JEPA-Anything (world modeling, not agentic RL), Verifiable Social Reasoning (multi-agent simulation/eval, not RL training), Self-Evolving Search Index (agent memory/retrieval, not RL), HypoEvolve (multi-agent LLM hypothesis search, not RL), EvoOntology (data-agent ontology layer, not RL). Recommended: archive the two most adjacent (Self-Evolving Search Index for agent memory, Verifiable Social Reasoning for multi-agent eval) as retained-but-unpublished candidates; review the remaining three only if the curator wants breadth on world modeling / multi-agent scientific search / data-agent tooling; otherwise skip. No candidate should be promoted to published knowledge without human full-text reading and, where applicable, code/benchmark verification.

## Candidates
### SKIP · SoL-Pi: Recursively Scaling Auto-Research Loops for Efficient Agent Harness
- Evidence: `abstract-only`
- Reason: Duplicate: already cataloged as source id 'sol-pi-recursively-scaling-auto-research' with an LLM full-text draft note pending human review. Re-adding would create a duplicate entry; the existing record already carries the appropriate '待人工复核' status.
- Suggested note: Duplicate of existing catalog entry sol-pi-recursively-scaling-auto-research. No new action; defer to the pending human review of that entry.

### REVIEW · CodeMidas: Scaling Agentic Coding RL Environments from Code Itself
- Evidence: `abstract-only`
- Reason: New to the knowledge base and plausibly on-topic: builds executable RL environments from source code alone, reports GRPO training of MiMo-V2.5 with gains on DeepSWE, ProgramBench, and Terminal-Bench v2.1. Relevant to the KB's environment-construction and coding-agent threads (swe-bench, swe-agent, agent-lightning, verl). Abstract-only; no code or artifact verification performed, so it must not be treated as published knowledge.
- Suggested note: 2026-09-18 preprint. Agentic pipeline turning implemented functionality in open-source codebases into executable RL environments (5,545 tasks, 3,185 repos, 23 languages). Reports GRPO training gains on issue repair, whole-program construction, and terminal tasks. Abstract-only; verify task-construction validity, verifier reliability, and benchmark contamination before any KB promotion.

### SKIP · RetireOPD: Self-Retiring On-Policy Distillation for Agentic Reinforcement Learning
- Evidence: `abstract-only`
- Reason: Duplicate: already cataloged as source id 'retireopd-self-retiring-on-policy-distil' with an LLM full-text draft note pending human review. The existing record already reflects the correct non-published status.
- Suggested note: Duplicate of existing catalog entry retireopd-self-retiring-on-policy-distil. No new action; defer to the pending human review of that entry.

### SKIP · An Empirical Study of Harness Design for Coding Agents
- Evidence: `abstract-only`
- Reason: Duplicate: already cataloged as source id 'an-empirical-study-of-harness-design-for' with an LLM full-text draft note pending human review. Re-adding would duplicate an existing record.
- Suggested note: Duplicate of existing catalog entry an-empirical-study-of-harness-design-for. No new action; defer to the pending human review of that entry.

### REVIEW · Reflect, Revise, Reuse: Training-Free Skill Evolution for GUI Agents
- Evidence: `abstract-only`
- Reason: New to the knowledge base and plausibly on-topic: training-free skill evolution for GUI agents via a reflect-revise-reuse loop, evaluated on MobileWorld, AndroidWorld, and OSWorld. Relevant to the KB's skill-evolution and agent-harness threads (coskill, reflect-revise-reuse-training-free-skill). Abstract-only; the abstract cites a code repository but no code was checked, and reported gains are self-reported.
- Suggested note: 2026-09-15 preprint. EvoSkill-GUI: training-free framework where skills are structured multi-file packages revised from execution feedback at deployment time. Reports max gains of +16.2% (MobileWorld), +6.0% (AndroidWorld), +10.5% (OSWorld). Abstract-only; verify benchmark setup, critic information isolation, and whether evolved skill libraries transfer without leakage.

### SKIP · When2Think: Learning Difficulty-Aware Length Control for Efficient Hybrid Reasoning Models
- Evidence: `abstract-only`
- Reason: Duplicate: already present in the knowledge base as source id 'when2think-learning-difficulty-aware-len' with the same arXiv id and title. No new information to add.
- Suggested note: Duplicate of existing KB entry; no action. If revisited, verify the claimed AIME24/AIME25 numbers against the paper body rather than the abstract.

### SKIP · Rethinking Critic Learning in PPO: Understanding and Mitigating Value Flattening
- Evidence: `abstract-only`
- Reason: Duplicate: already present in the knowledge base as source id 'rethinking-critic-learning-in-ppo-unders' with the same arXiv id and title. The catalog note already flags it as an LLM full-text draft pending human review.
- Suggested note: Duplicate of existing KB entry; no action. Existing entry remains '待人工复核'.

### REVIEW · RecreationWorld: Scalable and Verifiable Environments for Hybrid Computer-Use Agents
- Evidence: `abstract-only`
- Reason: Plausibly on-topic for Agentic RL: hybrid computer-use agents, execution-grounded rewards from a running reference, trajectory generation, and a held-out benchmark (RecreationBench). Claims are abstract-only and unverified; the reported GPT-6 Astra figure and benchmark composition need human reading before any KB inclusion.
- Suggested note: Candidate environment/benchmark for hybrid computer-use agents. Abstract-only; verify environment reproducibility, reward construction, and benchmark freezing procedure before citing.

### REVIEW · MintAct: A Unified Visual Agent for Digital Environments
- Evidence: `abstract-only`
- Reason: Plausibly on-topic: unified visual agent across mobile/desktop/web with an asynchronous RL training framework and cross-domain distribution control. Relevant to the KB's agentic-RL and harness themes, but claims (e.g., 48.9 OSWorld-Verified) are abstract-only and unverified.
- Suggested note: Candidate for visual/computer-use agent RL infrastructure. Abstract-only; check environment backends, async RL stability claims, and benchmark comparability before citing.

### REVIEW · Don't Mask the Environment: Observation Supervision Changes How Agents Explore Under RL
- Evidence: `abstract-only`
- Reason: Plausibly on-topic and methodologically interesting: supervises observation tokens during SFT and studies downstream GRPO exploration effects. Directly relevant to the KB's SFT-to-RL initialization and exploration themes. Claims are abstract-only; the entropy/orthogonality analysis and benchmark deltas need human reading.
- Suggested note: Candidate on observation supervision as RL initialization. Abstract-only; verify GRPO comparison setup, benchmark versions (Terminal-Bench 2.0, aider-polyglot), and whether gains replicate.

### SKIP · PACT: Can Enterprise AI Assistants Be Trusted Under Pressure?
- Evidence: `abstract-only`
- Reason: Duplicate: already catalogued as existing source 'pact-can-enterprise-ai-assistants-be-tru'. No new information to add; re-archiving would create a duplicate entry.
- Suggested note: Duplicate of existing catalog entry; no action needed.

### SKIP · What Does Privileged Information Add to On-Policy Self-Distillation?
- Evidence: `abstract-only`
- Reason: Duplicate: already catalogued as existing source 'what-does-privileged-information-add-to'. Abstract-only preprint; no new evidence beyond the existing entry.
- Suggested note: Duplicate of existing catalog entry; no action needed.

### REVIEW · RiskChainBench: A Benchmark for Obfuscated Platform Message Restoration and Evidence-Grounded Web Investigation
- Evidence: `abstract-only`
- Reason: Plausible but peripheral: a web-agent benchmark touching exploration, sandboxing, and evidence-grounded investigation, which overlaps the KB's webarena/gaia/tau-bench benchmark cluster. However, it is an abstract-only preprint with no code check, and its primary focus (platform-abuse message restoration) is outside the core Agentic RL training scope. Requires human reading to decide relevance.
- Suggested note: Abstract-only preprint. Benchmark for obfuscated message restoration plus VLM web-agent investigation; reports Entry Top-1 35.2-95.2% and web decision accuracy 26.3-62.8% across ten models, with execution failures at 31.9%. Not reproduced; verify benchmark construction and sandbox claims before any retention.

### REVIEW · Region-Level Policy Optimization for Fine-grained MLLM Perception
- Evidence: `abstract-only`
- Reason: Plausible but off-core: applies region-level RL to a proposal network for MLLM visual perception. Methodologically adjacent to policy optimization in the KB (ppo, gae) but the application domain (fine-grained vision) is outside Agentic RL. Abstract-only; code URL is claimed in the abstract but not verified. Requires human reading to judge whether it belongs.
- Suggested note: Abstract-only preprint. Vision-RL2 treats coherent regions as actions scored by a frozen MLLM reader; reports gains across six fine-grained benchmarks and four backbones at ~4x fewer visual tokens. Code URL claimed in abstract but unverified; not reproduced.

### REVIEW · A Zeroth-Order Paradigm for LLM Preference Alignment
- Evidence: `abstract-only`
- Reason: Plausible and adjacent to existing DPO/RLHF sources (dpo, instructgpt, constitutional). Proposes ComPO, a zeroth-order comparison-oracle alignment method with convergence and performance guarantees. Abstract-only preprint; theoretical claims and empirical comparisons are unverified. Requires human reading before any retention.
- Suggested note: Abstract-only preprint. ComPO extracts directional information from preference pairs via comparison oracles without optimizing a differentiable preference loss; claims convergence guarantees and length-controlled win-rate improvements on Mistral, Llama, Gemma-2, Qwen3, Gemma-3. Not reproduced; verify theory and baselines.

### ARCHIVE · DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression
- Evidence: `abstract-only`
- Reason: Systems/infrastructure paper on KV-cache compression, MoE architecture, and deployment optimization for long-context inference. It mentions agentic workloads as motivation but contributes no RL algorithm, environment, benchmark, or training methodology relevant to Agentic RL. Not a duplicate of any existing source. Retain for potential future reference on serving long-horizon agents, but do not publish as KB knowledge.
- Suggested note: Off-scope for Agentic RL core; systems/inference-efficiency work. Abstract-only, untrusted discovery metadata. Retain as background on long-context serving costs for agents; do not cite as RL evidence.

### SKIP · Sample Count Is Not Enough: Candidate-Generation Strategy Shapes the Energy and Performance of LLM Test-Time Scaling
- Evidence: `abstract-only`
- Reason: Empirical systems study of generation scheduling (batched vs. serial candidate generation) and its effect on latency, throughput, GPU-hours, and energy for test-time scaling on GSM8K/SciQ. Concerns inference efficiency, not Agentic RL training, credit assignment, or agent environments. No overlap with existing KB sources; not relevant enough to retain.
- Suggested note: Skipped: test-time-scaling systems/efficiency study, outside Agentic RL scope. Abstract-only.

### REVIEW · Grounded Skill Synthesis from Code at Scale for Agentic Intelligence
- Evidence: `abstract-only`
- Reason: Plausibly on-topic: proposes Code2Skill, an automated pipeline that mines GitHub repositories into a verified skill bank (CodeSkillBank) and reports retrieval-augmented gains across benchmarks. Relates to existing KB themes of skill evolution (coskill) and agent harnesses, but claims (1M+ records, 11.7% average improvement, 72 evaluations) are unverified and rest only on the abstract. Requires human reading of the full paper and, ideally, code/artifact checks before any KB inclusion.
- Suggested note: Candidate for KB: code-grounded skill synthesis for agents. Abstract-only; verify skill-bank construction, verification protocol, and benchmark methodology before publishing. Possible relation to coskill (skill evolution) and agentic-survey.

### ARCHIVE · In-Context Robot Learning with VLM Agents
- Evidence: `abstract-only`
- Reason: Embodied/robotics in-context learning with commercial VLMs; explicitly no gradient updates or persistent parameter changes, so it is not RL training and sits outside the Agentic RL scope. Mentions a commercial model name and vendor-specific claims that cannot be verified from the abstract. Retain only as adjacent embodied-agent context.
- Suggested note: Off-scope: embodied VLM in-context learning without gradient updates. Abstract-only, untrusted metadata; do not treat vendor/model claims as verified. Retain as adjacent robotics context only.

### REVIEW · CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents
- Evidence: `abstract-only`
- Reason: Plausibly on-topic: an iterative RL framework where a router and independent agent policies co-evolve, with a familiarity estimator and adaptive routing. Touches multi-agent orchestration and continual post-training, adjacent to KB interests (marl-book, agentic-survey, gigpo). However, all claims (outperforming SOTA routing/fine-tuning baselines) are abstract-only and unverified; the 'mid-layer hidden states' familiarity estimator and co-evolution dynamics need human reading and, ideally, code inspection.
- Suggested note: Candidate for KB: co-evolving router + continually learning agents via RL. Abstract-only; verify co-evolution objective, routing mechanism, and baseline comparisons before publishing. Possible relation to marl-book and agentic-survey.

### SKIP · JEPA-Anything: Learning Predictive Models across Different Worlds
- Evidence: `abstract-only`
- Reason: World-modeling / representation-learning paper (JEPA extension, orthogonal predictive factorization) evaluated on vision, biology, clinical, control, molecular, physical, weather domains. Matched keywords (long-horizon, rollout, generalization) are generic and do not indicate agentic RL training. No policy optimization, no agent-environment RL loop, no agent harness. Out of scope for this KB; would dilute the Agentic RL spine.
- Suggested note: Not Agentic RL: predictive world modeling across domains. Skip unless the KB later adds a world-modeling branch.

### ARCHIVE · Verifiable Social Reasoning for LLM Assistants
- Evidence: `abstract-only`
- Reason: Multi-agent simulation framework (Fuse) with verifiable ground truth by construction, human-validated (24k annotations), applied to 12 LLMs, 21k-example dataset. Relevant to the KB's multi-agent and evaluation interests (marl-book, tau-bench, gaia) as an evaluation methodology, but it is not RL training and the abstract alone cannot confirm benchmark validity or leakage properties. Retain as a candidate without publishing.
- Suggested note: Candidate: multi-agent simulation for verifiable social-reasoning evaluation. Abstract-only; verify dataset construction and ground-truth claims before any use.

### ARCHIVE · Self-Evolving Search Index
- Evidence: `abstract-only`
- Reason: Self-evolving retrieval index with an Optimizer and Query Simulator; explicitly claims benefits for search agents and agent memory systems. Adjacent to the KB's agent-memory and tool-use threads (lilian-agent, react). Not RL training and no agentic-RL objective; abstract-only, no reproduction. Retain as a candidate for the memory/retrieval branch.
- Suggested note: Candidate: self-evolving index for agent retrieval/memory. Abstract-only; check whether 'self-evolution' is RL or heuristic before citing.

### REVIEW · HypoEvolve: Genetic Algorithms Enable Multi-Agent LLMs to Discover Scientific Hypotheses
- Evidence: `abstract-only`
- Reason: Multi-agent LLM system with a generational genetic algorithm for hypothesis discovery, evaluated on 34 cancer types against six baselines with external measures (DepMap, Open Targets). Relevant to the KB's multi-agent and autonomous-research interests (marl-book, SoL-Pi, ScienceIDE) but the optimization is evolutionary search, not RL, and the abstract-only evidence cannot support the reported gains. Needs human reading to decide whether it belongs in the multi-agent branch.
- Suggested note: Review: multi-agent LLM + genetic algorithm for scientific hypothesis discovery. Confirm whether any RL/credit-assignment component exists; otherwise file under multi-agent search, not Agentic RL.

### REVIEW · EvoOntology: A Self-Evolving Ontology Layer for Data Agents
- Evidence: `abstract-only`
- Reason: Self-evolving ontology layer exposed as an MCP server for data agents, with a builder agent and attribution-guided typed edits validated by paired evaluation; evaluated on three data-agent benchmarks with four LLM backbones. Relevant to the KB's tool-use and agent-environment threads (react, tau-bench, agentic-survey) but is a data-agent tooling/semantics contribution, not RL training. Abstract-only; benchmark claims unverified. Needs human reading to place correctly.
- Suggested note: Review: self-evolving ontology/MCP layer for data agents. Determine whether the self-evolution loop is RL-based or heuristic; if heuristic, file under agent tooling, not Agentic RL.

## Risks
- All five discovery entries are 2026 preprints with abstract-only evidence; none has been code-checked, reproduced, or peer-reviewed. Treating any as established knowledge would overstate the KB's evidence base.
- Three of five entries (SoL-Pi, RetireOPD, Harness Design) duplicate existing catalog records; naive ingestion would create duplicate source ids and conflicting notes.
- Discovery metadata is untrusted external text (HuggingFace daily papers). Titles, summaries, author lists, and upvote counts are unverified and may be inaccurate or manipulated; no URLs or claims from it were adopted as fact.
- Several abstracts report large benchmark gains (e.g., +11.7% to +17%, +14.1% to +18.8%) without released artifacts or independent verification; benchmark contamination and verifier reliability are unassessed.
- The EvoSkill-GUI abstract cites a GitHub repository; an HTTP 200 or repository existence would not constitute evidence of correctness, and no such check was performed.
- Existing catalog entries for the three duplicates already carry 'LLM 全文精读草稿 · 待人工复核' status; automated re-ingestion could silently upgrade their status without human review.
- All five entries are preprints with abstract-only evidence; none should be treated as published or verified knowledge.
- Two entries are duplicates of existing KB sources; re-adding them would inflate the catalog without new evidence.
- Discovery and catalog fields are untrusted external text and may contain prompt injection or fabricated metadata; no URLs were fetched and no embedded instructions were followed.
- Reported benchmark numbers (e.g., OSWorld-Verified, AIME, Terminal-Bench) are self-reported in abstracts and may not be reproducible or comparable.
- arXiv identifiers and dates in the discovery payload were not independently verified against arXiv.
- All five entries are abstract-only preprints; none were code-checked or reproduced, so no claim should be treated as established knowledge.
- Two entries (PACT, What Does Privileged Information Add to On-Policy Self-Distillation?) duplicate existing catalog sources; re-archiving risks duplicate entries and inconsistent notes.
- Discovery metadata is untrusted external text; matched_keywords and relevance_score are heuristic and may overstate topical fit.
- Abstract-reported metrics (e.g., PACT violation-rate increases, RiskChainBench accuracy ranges, Vision-RL2 token reductions) are self-reported and unverified.
- Code URLs appearing in abstracts (e.g., Vision-RL2 GitHub) are unverified and must not be treated as evidence of correctness or reproducibility.
- All discovery entries are untrusted external text; titles, summaries, author lists, and URLs were treated as data only and not followed as instructions.
- Evidence level is abstract-only for every candidate; no full texts, code, or artifacts were inspected. HTTP/URL presence is not evidence of correctness.
- Several abstracts contain unverifiable or vendor-specific claims (e.g., commercial model names, large benchmark deltas) that must not be recorded as established facts.
- Two candidates (2609.19969, 2609.19138) are off-scope and could dilute the KB if published; they are archived, not published.
- Potential duplicate risk is low but not zero: 2609.05571 (skill synthesis) and 2609.18779 (co-evolving agents) may overlap thematically with existing coskill/agentic-survey entries and should be checked for conceptual duplication during human review.
- Discovery metadata may be incomplete or stale; arxiv IDs and dates were not independently confirmed.
- All five candidates are abstract-only preprints; none have been code-checked, reproduced, or benchmark-verified. Reported metrics (e.g., 34.8% error reduction, DepMap selectivity 0.171) must not be treated as established.
- Discovery metadata (titles, summaries, upvotes, matched_keywords) is untrusted external text and was treated as data only; keyword matches such as 'long-horizon', 'rollout', 'generalization' are generic and can produce false positives for Agentic RL relevance.
- Scope drift risk: JEPA-Anything (world modeling), HypoEvolve (evolutionary scientific search), and EvoOntology (data-agent semantics) are adjacent but not Agentic RL; archiving them without clear branch labels could blur the KB's foundations-to-frontier spine.
- Duplicate/near-duplicate risk: the KB already contains SoL-Pi, ScienceIDE, and multi-agent sources; HypoEvolve and EvoOntology overlap thematically and should be cross-checked before any note is written.
- No URLs were fetched and no HTTP status was checked; a 200 response would not have constituted evidence of correctness in any case.

## Next actions
- Route CodeMidas (2609.22068) and EvoSkill-GUI (2609.17653) to human reading; do not promote either to published knowledge until full text is reviewed.
- Deduplicate: confirm the three existing catalog records (sol-pi-recursively-scaling-auto-research, retireopd-self-retiring-on-policy-distil, an-empirical-study-of-harness-design-for) match the discovery entries and take no further ingestion action.
- For CodeMidas, verify task-construction methodology, verifier soundness, and benchmark contamination before any KB note is upgraded beyond abstract-only.
- For EvoSkill-GUI, verify benchmark setup, critic information isolation, and skill-library transfer claims; check whether the cited code repository is real and reproducible, without treating availability as correctness.
- Keep all new entries at abstract-only evidence level and record the audit date; require human sign-off before any status change.
- Human-read the three review candidates (2609.22000, 2609.22083, 2609.20715) and decide whether to add them as '待精读' entries.
- Confirm the two duplicate arXiv ids against existing KB entries and avoid re-adding them.
- If any candidate is promoted, record evidence level as abstract-only until code or results are independently checked.
- Do not fetch or trust URLs from the discovery payload without independent verification.
- Skip the two duplicate entries (2609.18605, 2609.20612) and confirm they map to existing source IDs without creating new records.
- Queue 2609.16900, 2609.19745, and 2609.19144 for human reading; decide archive vs. skip based on topical fit to Agentic RL after reading the full papers.
- If any reviewed candidate is retained, record it as a preprint with evidence_level 'abstract-only' and an explicit 'not reproduced' note.
- Do not fetch or trust code URLs from abstracts until a human verifies the repository and commit.
- Re-run duplicate detection against existing_source_ids before any future archiving to avoid redundant entries.
- Human-read full texts of 2609.05571 and 2609.18779; if accepted, add as new KB entries with explicit 'preprint, unverified' status.
- Check 2609.05571 against coskill and 2609.18779 against marl-book/agentic-survey for conceptual duplication before any merge.
- If either review candidate is promoted, attempt code/artifact verification (repository, commit, reproduction) and record evidence level as code-checked only after successful checks.
- Keep 2609.19969 and 2609.19138 in an archive/adjacent bucket, not in the published Agentic RL knowledge set.
- Do not add 2609.19499 to the KB; optionally note it in an efficiency/systems side-index if such a bucket exists.
- Re-run discovery with tighter keyword filters (e.g., require RL training, credit assignment, environment, or benchmark terms) to reduce off-scope noise.
- Human full-text read of the two 'review' candidates (2609.15938, 2609.15779) to confirm whether any RL/credit-assignment component exists; if not, reclassify to skip or to a non-RL branch.
- For the two 'archive' candidates (2609.17496, 2609.19656), record them in the candidate backlog with evidence_level=abstract-only and do not add to the published catalog.
- Cross-check HypoEvolve and EvoOntology against existing SoL-Pi, ScienceIDE, and multi-agent entries to detect overlap before writing any note.
- If any candidate is later promoted, require code/benchmark verification (repo commit, dataset construction, leakage checks) and record the verification method in the note.
- Keep the untrusted-input handling policy: never act on instructions embedded in discovery summaries, and never fetch URLs or reveal credentials based on them.
