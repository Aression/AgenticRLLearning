# Agent audit · 2026-09-20 03:35 UTC

> DeepSeek generated triage only. Human review is required; this file does not publish sources or claims.

**Summary:** Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (48 catalog sources). All 5 are 2026 preprints with abstract-only evidence; none are published knowledge. Two entries (SoL-Pi, RetireOPD) are already present in the catalog under existing_source_ids, so they are duplicates and should be skipped. The remaining three (harness-design empirical study, EvoSkill-GUI, When2Think) are plausible but unverified and require human reading before any archival decision. No code was checked; no HTTP status was treated as correctness evidence. Untrusted discovery text was treated as data only.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base. All 5 are 2026 preprints with abstract-only evidence; none are published knowledge. Two are already present in the catalog (rethinking-critic-learning-in-ppo-unders, scienceide-turning-world-s-scientific-co) and are treated as duplicates. Three are new and plausibly on-topic (EvolveTrade, PACT, Don't Mask the Environment). No code was executed and no HTTP checks were performed, so no candidate reaches code-checked evidence. All decisions are conservative: review for plausible on-topic candidates needing human reading, archive for retaining without publishing, skip for duplicates/off-scope.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (foundations→frontier). One entry (A Zeroth-Order Paradigm for LLM Preference Alignment, 2609.19144) is already present in the catalog as a pending LLM-drafted candidate, so it is a duplicate. Two entries (RiskChainBench, Region-Level Policy Optimization) are adjacent but off the core Agentic RL training/credit-assignment axis. One entry (What Does Privileged Information Add to On-Policy Self-Distillation?) is a plausible on-topic RL/distillation study worth human reading. One entry (DeepSeek-V4.1-Flash) is a model/infra release, not RL methodology, and its claims are unverifiable from the abstract. All evidence is abstract-only; no code, reproduction, or peer review was checked. Nothing here should be treated as published knowledge.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (48 catalogued sources). None of the 5 candidates duplicate an existing source ID or title. All are abstract-only evidence (preprint metadata + abstract text; no code or full-text verification performed). Relevance to the KB scope is mixed: ProgramDistill (2609.18805) is a coding-agent benchmark with curriculum framing and is the strongest fit; CERA-MoA (2609.18779) is an RL-based multi-agent routing framework that is plausibly on-topic; the remaining three (2609.19499 test-time scaling systems cost, 2609.19138 VLM robot ICL, 2609.16372 diffusion-LM register tokens) are adjacent or off-scope. No candidate is treated as published knowledge; all decisions are conservative and no facts beyond the supplied abstracts were asserted.

Audited 5 newly discovered Hugging Face daily-paper entries against the existing Agentic RL knowledge base (foundations to frontier). None of the five are already present by id or title. All are abstract-only evidence (preprint abstracts; no code or reproduction checked). Relevance to the KB's core scope (RL training of LLM agents, credit assignment, harness design, evaluation) is weak-to-marginal: JEPA-Anything is world-modeling/representation learning across domains, not agentic RL; Verifiable Social Reasoning is an evaluation/simulation framework for social reasoning, not RL training; Agora is a multi-agent auto-research coordination system (Git-as-memory) with no RL training loop; Self-Evolving Search Index is retrieval/index optimization, not RL; HypoEvolve is evolutionary multi-agent hypothesis generation, not RL. No candidate is treated as published knowledge. No prompt-injection or credential-exfiltration content was observed in the untrusted discovery text; it was treated strictly as data.

## Candidates
### SKIP · SoL-Pi: Recursively Scaling Auto-Research Loops for Efficient Agent Harness
- Evidence: `abstract-only`
- Reason: Duplicate: already cataloged as source id 'sol-pi-recursively-scaling-auto-research' (LLM full-text draft, pending human review). Re-adding would create a duplicate entry. No new evidence beyond the same abstract.
- Suggested note: Duplicate of existing catalog entry; do not re-ingest. Existing note already flags it as an unverified LLM full-text draft.

### SKIP · RetireOPD: Self-Retiring On-Policy Distillation for Agentic Reinforcement Learning
- Evidence: `abstract-only`
- Reason: Duplicate: already cataloged as source id 'retireopd-self-retiring-on-policy-distil'. Same abstract, no new evidence. Re-adding would duplicate an already-pending candidate.
- Suggested note: Duplicate of existing catalog entry; do not re-ingest.

### REVIEW · An Empirical Study of Harness Design for Coding Agents
- Evidence: `abstract-only`
- Reason: Plausibly on-topic for the harness-design thread (multi-harness, agent-lightning, swe-agent, swe-bench). Abstract claims component-level ablations (planning, action space, context management) across 4 models and 176 settings on SWE-Bench Verified and Terminal-Bench 2.1. Claims are specific and falsifiable but unverified; no code or artifact was checked. Requires human reading before any archival or publication.
- Suggested note: 2026-09-20: harness-design ablation study; abstract-only, not reproduced. Verify benchmark versions, model list, and whether 176 settings are matched/comparable before citing. Cross-check against multi-harness and swe-agent notes.

### REVIEW · Reflect, Revise, Reuse: Training-Free Skill Evolution for GUI Agents
- Evidence: `abstract-only`
- Reason: Plausibly on-topic for skill-evolution and GUI-agent threads (coskill, reflect-revise-reuse). Abstract claims training-free skill revision with gains on MobileWorld, AndroidWorld, OSWorld and links a code repo. Claims are specific but unverified; the code URL was not fetched or checked, and an HTTP 200 would not establish correctness. Requires human reading.
- Suggested note: 2026-09-20: training-free GUI skill evolution; abstract-only, not reproduced. If reviewing, verify benchmark splits, base models, and whether gains are within run-to-run variance. Do not treat the linked repo as evidence of correctness.

### REVIEW · When2Think: Learning Difficulty-Aware Length Control for Efficient Hybrid Reasoning Models
- Evidence: `abstract-only`
- Reason: Adjacent to the KB's reasoning-RL and reward-shaping interests (deepseek-r1, dapo, deepseek-math). Abstract claims instance-adaptive computation allocation with critic-free optimization and reported AIME24/AIME25 gains. Claims are specific but unverified; no code or artifact checked. Requires human reading before any archival decision.
- Suggested note: 2026-09-20: difficulty-aware length control for hybrid reasoning; abstract-only, not reproduced. Verify reward-shaping details, baseline comparability, and whether Pass@3/token-usage claims hold under matched budgets.

### SKIP · Rethinking Critic Learning in PPO: Understanding and Mitigating Value Flattening
- Evidence: `abstract-only`
- Reason: Duplicate: already cataloged as 'rethinking-critic-learning-in-ppo-unders' with an LLM full-text draft pending human review. Re-adding would create a duplicate source. No new evidence beyond the existing abstract-only entry.
- Suggested note: Duplicate of existing catalog entry rethinking-critic-learning-in-ppo-unders; do not re-ingest. Existing entry remains abstract-only pending human verification.

### SKIP · ScienceIDE: Turning World's Scientific Codebase into Agent Learnable Environments
- Evidence: `abstract-only`
- Reason: Duplicate: already cataloged as 'scienceide-turning-world-s-scientific-co' with an LLM full-text draft pending human review. No new evidence beyond the existing abstract-only entry.
- Suggested note: Duplicate of existing catalog entry scienceide-turning-world-s-scientific-co; do not re-ingest. Existing entry remains abstract-only pending human verification.

### REVIEW · EvolveTrade: Experience-Driven Policy Refinement for Self-Evolving LLM Trading Agents
- Evidence: `abstract-only`
- Reason: New, not in existing source_ids. Plausibly adjacent to Agentic RL scope: treats a tool-using agent's system prompt as a text-parameterized policy refined from decision traces and portfolio feedback. However, it is a 2026 preprint with abstract-only evidence, no code check, and the domain (trading) is peripheral to the KB's core agentic-RL focus. Requires human reading to judge relevance and whether claims are supported.
- Suggested note: 2026 preprint, abstract-only. Self-evolving tool-use policy via prompt revision from traces; trading domain. Human review needed for scope fit and claim support before any cataloging.

### REVIEW · PACT: Can Enterprise AI Assistants Be Trusted Under Pressure?
- Evidence: `abstract-only`
- Reason: New, not in existing source_ids. Relevant to the KB's safety/compliance and evaluation interests (cf. tau-bench, lilian-reward). It is a benchmark/evaluation paper rather than an RL training method, and evidence is abstract-only with no code check. Human reading needed to assess methodology, judge reliability, and overlap with existing benchmarks.
- Suggested note: 2026 preprint, abstract-only. Compliance-under-pressure benchmark for enterprise LLM agents; 22 models, 12 domains. Human review for benchmark validity and overlap with tau-bench before cataloging.

### REVIEW · Don't Mask the Environment: Observation Supervision Changes How Agents Explore Under RL
- Evidence: `abstract-only`
- Reason: New, not in existing source_ids. Directly on-topic for Agentic RL: studies SFT initialization and GRPO exploration, observation-token supervision, and entropy/policy-movement effects. Strong conceptual fit with existing PPO/GRPO/agentic sources. Still a 2026 preprint with abstract-only evidence and no code check; claims (e.g., pass@k gains) are unverified. Requires human reading.
- Suggested note: 2026 preprint, abstract-only. ActObs supervises observation tokens during SFT; reports GRPO exploration/entropy effects on Terminal-Bench 2.0 and aider-polyglot. Human review needed; do not treat reported gains as verified.

### REVIEW · What Does Privileged Information Add to On-Policy Self-Distillation?
- Evidence: `abstract-only`
- Reason: On-topic for the KB's RL/distillation and on-policy learning thread (adjacent to dpo, deepseek-r1, mintrl-off-policy-intervention). Abstract reports a controlled ablation isolating the contribution of privileged references in on-policy self-distillation, with matched reference-free baselines and cross-model checks. Plausible and methodologically framed, but claims are abstract-only, no code or reproduction verified, and the 'cross-mode transfer' interpretation needs human reading before any note is promoted.
- Suggested note: 2026-09-17 preprint (arXiv:2609.20612). On-policy self-distillation (OPSD) with a frozen teacher that sees a reference/worked solution. Constructs AMPLE-Math (5,319 problems, six reasoning views sharing an answer) and compares each view against matched reference-free distillation. Abstract claims reference-free distillation accounts for much of Qwen3-1.7B's gain; extra reference benefit is modest and depends on the student being trained; swapping short direct-response rollouts for long thinking-enabled rollouts turns gains into losses. Interpretation offered: OPSD improves access to existing capabilities via shared parameters, and privileged-reference value lies in cross-mode transfer. Status: abstract-only, not reproduced. Do not cite as established result.

### SKIP · A Zeroth-Order Paradigm for LLM Preference Alignment
- Evidence: `abstract-only`
- Reason: Duplicate: already present in the catalog as 'a-zeroth-order-paradigm-for-llm-preferen' (arXiv:2609.19144, Peter Chen et al., 2026) with a pending LLM-drafted note. Re-adding would create a duplicate source id. No new information beyond the existing entry.
- Suggested note: Duplicate of existing catalog entry a-zeroth-order-paradigm-for-llm-preferen (arXiv:2609.19144). No action; keep existing pending-review note.

### ARCHIVE · RiskChainBench: A Benchmark for Obfuscated Platform Message Restoration and Evidence-Grounded Web Investigation
- Evidence: `abstract-only`
- Reason: Adjacent to the KB's web-agent and benchmark interests (webarena, gaia, tau-bench) and touches exploration/sandbox themes, but the core contribution is a safety/abuse-investigation benchmark, not Agentic RL training methodology. Worth retaining as a possible future benchmark reference, but not a priority for the current foundations→frontier RL scope. Abstract-only; benchmark, protocol, and sandbox release are claimed but unverified.
- Suggested note: 2026-09-15 preprint (arXiv:2609.16900). Benchmark pairing 3,600 synthetic obfuscated-message restoration inputs (600 source sessions) with 600 human-labeled local web environments; a model restores intent/destination, then a VLM web agent investigates the routed site and emits an evidence-cited report. Abstract reports Entry Top-1 35.2–95.2% and web decision accuracy 26.3–62.8% across ten models; 31.9% of web runs fail on execution. Status: abstract-only, not reproduced. Retained as adjacent benchmark reference, not core RL methodology.

### ARCHIVE · Region-Level Policy Optimization for Fine-grained MLLM Perception
- Evidence: `abstract-only`
- Reason: Uses RL (region-level policy optimization over a proposal network) and is adjacent to the KB's policy-optimization thread, but the application is fine-grained MLLM visual perception, not agentic RL. Retain as a peripheral RL-application reference; not a priority for the agentic scope. Abstract-only; code URL is claimed in the abstract but was not fetched or verified.
- Suggested note: 2026-09-17 preprint (arXiv:2609.19745). Vision-RL2: treats coherent image regions as actions and scores them with a frozen MLLM reader via subtractive/additive objectives, updating only a proposal network without region annotations or reasoning trajectories. Abstract reports gains across six fine-grained benchmarks and four MLLM backbones at every token budget, with ~4x fewer visual tokens. Status: abstract-only, not reproduced; code link in abstract unverified. Peripheral to Agentic RL scope.

### SKIP · DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression
- Evidence: `abstract-only`
- Reason: Model/infrastructure release (MoE backbone, KV-cache compression, deployment optimizations), not RL methodology. Matched only on generic keywords (long-horizon, agent, agentic, memory). Claims of 'substantially better performance' and checkpoint availability are abstract-only and unverified; no RL content relevant to the KB's training/credit-assignment axis.
- Suggested note: Skip: model/infra release, not Agentic RL methodology. Abstract-only claims; no verification performed.

### REVIEW · ProgramDistill: From Interactive Web Apps to Verifiable Reference-Guided SWE Tasks
- Evidence: `abstract-only`
- Reason: Directly relevant to the KB's coding-agent and benchmark cluster (swe-bench, swe-agent, webarena). Abstract claims a scalable, replay-verified benchmark (1,975 behaviors, 4,063 tasks) and reports frontier-agent success rates, plus an explicit curriculum-training motivation that connects to the KB's RL-training interests. However, only the abstract was inspected: no code, dataset, or replay-verification artifacts were checked, and the reported numbers are unverified. Requires human reading before any catalog entry.
- Suggested note: New preprint (2026-09-16). Coding-agent benchmark built by factorizing web apps into replay-verified features; claims 1,975 behaviors / 4,063 tasks and reports cumulative-workflow success for frontier agents. Abstract-only; benchmark construction, replay verification, and reported numbers not independently checked. Candidate for the coding-agent/benchmark cluster alongside swe-bench and webarena; verify task leakage and environment pinning before use.

### REVIEW · CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents
- Evidence: `abstract-only`
- Reason: Plausibly on-topic: an iterative RL framework where a router and independent agent policies co-evolve, with a familiarity estimator over mid-layer hidden states and adaptive agent-subset activation. Touches the KB's multi-agent and RL-training themes (marl-book, agentic-survey, gigpo). But the abstract is the only evidence; no code, no full text, and the claimed superiority over static routing and fixed-workflow baselines is unverified. Human reading needed to judge whether the RL formulation is substantive or incremental.
- Suggested note: New preprint (2026-09-16). Co-evolving router + continually-learning LLM agents via iterative RL; predictive familiarity estimator from mid-layer hidden states; cumulative-threshold adaptive routing. Abstract-only; no code or full text checked, baseline comparisons unverified. Review against marl-book and agentic-survey for credit-assignment and routing overlap before cataloguing.

### SKIP · Sample Count Is Not Enough: Candidate-Generation Strategy Shapes the Energy and Performance of LLM Test-Time Scaling
- Evidence: `abstract-only`
- Reason: Off-scope for Agentic RL. The work is a systems/efficiency study of test-time scaling generation schedules (batched vs. serial candidate generation) measuring latency, throughput, GPU-hours, and energy on GSM8K/SciQ. It concerns inference-time sampling economics, not agentic RL training, credit assignment, or environment interaction. Keyword matches ('test-time', 'reasoning', 'memory', 'evaluation') are incidental. Not a duplicate, but not a fit for this KB.
- Suggested note: Skipped: test-time-scaling systems-cost study (generation schedule vs. energy/latency), not agentic RL. Revisit only if the KB adds an inference-efficiency or evaluation-methodology section.

### SKIP · In-Context Robot Learning with VLM Agents
- Evidence: `abstract-only`
- Reason: Off-scope. Embodied robot learning via in-context learning with commercial VLMs and a constrained controller; explicitly no gradient updates or persistent parameter changes, so it is not RL training. Keyword matches ('agent', 'agentic', 'policy', 'tool', 'generalization') are superficial. Not a duplicate, but outside the Agentic RL foundations-to-frontier scope.
- Suggested note: Skipped: in-context robot learning with VLM agents, no gradient updates. Not RL training; outside KB scope. Revisit only if the KB adds an embodied/robotics track.

### SKIP · Register Tokens for Bounded-State Reasoning in Diffusion Language Models
- Evidence: `abstract-only`
- Reason: Off-scope. Concerns masked diffusion language models and fixed-size carried state (register tokens) across generation chunks, with a brief mention of optional RL refinement. The core contribution is a dLLM architecture/post-training method, not agentic RL. Keyword matches ('long-horizon', 'reinforcement learning', 'reasoning', 'benchmark') are incidental. Not a duplicate, but not a fit.
- Suggested note: Skipped: diffusion-LM register-token state carry for bounded reasoning; RL is only a secondary refinement step. Outside Agentic RL scope.

### SKIP · JEPA-Anything: Learning Predictive Models across Different Worlds
- Evidence: `abstract-only`
- Reason: World-modeling / joint-embedding predictive architecture across seven domains (vision, biology, clinical, control, molecular, physical, weather). Not agentic RL: no policy optimization, no agent-environment RL training loop, no credit assignment. Only tangential keyword overlap (long-horizon, rollout, generalization). Out of KB scope.
- Suggested note: Out of scope for Agentic RL KB. World-modeling/representation learning; abstract-only, no RL training claims relevant to this KB.

### SKIP · Verifiable Social Reasoning for LLM Assistants
- Evidence: `abstract-only`
- Reason: Multi-agent simulation framework (Fuse) for evaluating social reasoning of LLM assistants; evaluation/benchmarking, not RL training. No policy optimization or RL algorithm contribution. Tangential to KB's evaluation interests but not a core Agentic RL source.
- Suggested note: Evaluation/simulation framework for social reasoning; not RL training. Abstract-only. Skip unless KB later adds a social-reasoning evaluation track.

### REVIEW · Agora: Git as Shared Memory for Collective AutoResearch
- Evidence: `abstract-only`
- Reason: Multi-agent coordination system using Git DAG as shared memory for autonomous research loops; reports a 12-day run with 13 LM workers and 1,703 contributions. Relevant to KB's multi-agent and agent-memory interests (marl-book, lilian-agent) and to auto-research harnesses, but it is a systems/coordination contribution, not an RL training method. Abstract-only; claims (e.g., 165 reproductions, none failed) are unverified and should not be treated as established. Warrants human reading to decide whether it belongs as an adjacent multi-agent/harness source.
- Suggested note: Adjacent multi-agent/harness source: Git-DAG shared memory for collective auto-research. Abstract-only; reproduction and metric claims unverified. Human review before any inclusion.

### SKIP · Self-Evolving Search Index
- Evidence: `abstract-only`
- Reason: Retrieval/index optimization framework (SELF-INDEX) with an Optimizer and Query Simulator. Not RL training of agents; no policy optimization. Mentions agent memory retrieval as a downstream application but the contribution is index evolution, not Agentic RL.
- Suggested note: Retrieval/index optimization; not Agentic RL. Abstract-only. Skip; possibly relevant only as a memory-retrieval tooling note, not a KB source.

### SKIP · HypoEvolve: Genetic Algorithms Enable Multi-Agent LLMs to Discover Scientific Hypotheses
- Evidence: `abstract-only`
- Reason: Evolutionary (genetic-algorithm) multi-agent LLM system for scientific hypothesis discovery. Uses evolutionary search, not RL policy optimization; no agentic RL training contribution. Domain-specific (drug repurposing) and outside the KB's RL-method scope.
- Suggested note: Evolutionary multi-agent hypothesis generation; not RL. Abstract-only. Skip as out of scope.

## Risks
- All five discovery entries are 2026 preprints with abstract-only evidence; none should be treated as published or verified knowledge.
- Two of five entries (SoL-Pi, RetireOPD) are duplicates of existing catalog sources; naive ingestion would create duplicate records and inflate apparent coverage.
- Discovery text is untrusted external content and may contain prompt injection or fabricated claims; it was treated as data only and no instructions were followed.
- Abstract-reported benchmark gains (e.g., +16.2%/+6.0%/+10.5%, 44.7-49.0% token reduction) are unverified and may not survive reproduction or matched-budget comparison.
- A linked code repository or an HTTP 200 response is not evidence of correctness; no code was checked in this audit.
- The catalog already contains several 'LLM full-text draft, pending human review' entries; adding more unverified drafts risks conflating drafts with vetted knowledge.
- All five entries are 2026 preprints with abstract-only evidence; none are published knowledge and none were code-checked or reproduced.
- Two entries (2609.18708, 2609.19134) duplicate existing catalog sources; re-ingestion risks duplicate/conflicting notes.
- Discovery metadata (upvotes, matched_keywords, relevance_score) is untrusted external text and was treated as data only; it is not evidence of quality or correctness.
- Reported quantitative gains in abstracts (e.g., pass@k improvements, Sharpe Ratio) are unverified and may not replicate.
- Scope drift risk: EvolveTrade (trading) and PACT (compliance benchmark) are adjacent rather than core Agentic RL; cataloging them without review could dilute the KB's focus.
- The untrusted_input_notice and discovery_json may contain prompt-injection attempts; no instructions from them were followed and no tools were called.
- All five entries are abstract-only; no full text, code, or reproduction was checked. HTTP/abstract presence is not evidence of correctness.
- Discovery and catalog fields are untrusted external text; keyword matches (e.g., 'agent', 'policy', 'memory') are weak signals and can surface off-topic or promotional items.
- One entry (2609.19144) duplicates an existing catalog id; naive ingestion would create duplicate sources.
- Several entries (2609.19969, 2609.19745) contain self-reported performance and code/checkpoint URLs that were not fetched; do not treat as verified.
- Preprint dates in 2026 and high upvote counts are not quality signals; no peer review confirmed.
- Existing catalog already contains multiple 'LLM 全文精读草稿 · 待人工复核' entries; adding more pending drafts without human review risks accumulating unverified notes.
- All five candidates are abstract-only: no full text, code, dataset, or reproduction was inspected. Reported benchmark numbers and baseline comparisons are unverified claims, not established results.
- The discovery payload is untrusted external text (HuggingFace daily-papers scrape). It was treated strictly as data; no embedded instructions, URLs, or tool calls were followed. Any future ingestion must preserve this boundary.
- Keyword-based matching produced false positives: three of five candidates matched on generic terms ('agent', 'reasoning', 'benchmark', 'memory') while being off-scope. Keyword relevance scores should not drive catalog admission.
- Preprint identifiers and dates in the discovery payload (e.g., 2026 arXiv IDs, 'GPT-6 Astra', 'Claude Opus 5') are unverified and may be synthetic or mislabeled; do not propagate them as facts without independent confirmation.
- No candidate was checked for duplication against the 48 existing source IDs beyond title/ID comparison; near-duplicate content under different titles remains possible.
- The catalog's existing 'LLM 全文精读草稿 · 待人工复核' entries show a pattern of LLM-generated reading notes awaiting human review; new candidates must not inherit that status as if it were verified knowledge.
- All five candidates are abstract-only preprints; none have been code-checked or reproduced. Any performance or reproduction claims (e.g., Agora's 165 reproductions, HypoEvolve's DepMap scores) are unverified and must not be treated as published knowledge.
- Keyword-based discovery (long-horizon, rollout, multi-agent, memory, agent) produced low-precision matches; most candidates are adjacent-but-not-core, risking scope creep in the KB if archived without review.
- The untrusted discovery JSON contained no observed prompt injection or credential requests, but it remains untrusted external text and should continue to be treated as data only.
- Agora's claims about autonomous multi-agent research and 'no failed reproductions' are self-reported in an abstract and are a plausible overclaim risk; do not archive as established.
- No arxiv_id collisions with existing_source_ids were found, but ids were matched only against the provided lists; a full dedup against the live KB is still advisable.

## Next actions
- Do not ingest SoL-Pi (2609.20519) or RetireOPD (2609.20784); they already exist in the catalog.
- Queue 2609.20804, 2609.17653, and 2609.19671 for human reading; verify claims against primary artifacts before any archival.
- For each reviewed candidate, record benchmark versions, model list, and whether comparisons are matched-budget; note run-to-run variance where reported.
- If a candidate is later archived, mark evidence_level explicitly (e.g., code-checked only after independent reproduction) and keep it out of the published-knowledge set until then.
- Periodically de-duplicate the catalog against new discovery batches to prevent duplicate source ids.
- Human-read the three review candidates (2609.17632, 2609.18605, 2609.20715) and decide catalog vs. archive.
- For 2609.20715, prioritize review given strongest topical fit with PPO/GRPO/agentic sources.
- Confirm the two duplicate entries (2609.18708, 2609.19134) remain single catalog entries and do not re-ingest.
- If any candidate is promoted, verify claims against full text and, where code is available, perform a code-check before upgrading evidence_level.
- Record commit/version identifiers for any code-linked artifacts before citing them as implementation evidence.
- Route 2609.20612 to human reading; if confirmed, draft a note distinguishing reference-free distillation from privileged-reference benefit and flag the rollout-length sensitivity.
- Do not re-add 2609.19144; instead update the existing catalog entry if new information is found.
- Keep 2609.16900 and 2609.19745 in an archive/adjacent list; revisit only if the KB scope expands to web-investigation benchmarks or MLLM perception RL.
- Skip 2609.19969 unless the KB adds a model/infrastructure track.
- For any candidate promoted, require full-text reading and, where possible, code/commit verification before marking as published knowledge.
- Deduplicate discovery results against existing_source_ids before ingestion to prevent duplicate entries.
- Human-read the two review candidates (2609.18805, 2609.18779) in full text; verify claims, baselines, and any released code/artifacts before any catalog entry.
- For 2609.18805, check task construction, replay verification, and environment pinning for leakage before considering it alongside swe-bench/webarena.
- For 2609.18779, compare its RL formulation and credit-assignment scheme against gigpo, agent-lightning, and marl-book to assess novelty.
- Record the three skip decisions (2609.19499, 2609.19138, 2609.16372) with reasons so they are not re-surfaced by the same keyword query.
- Tighten the discovery query to reduce generic-keyword false positives (e.g., require agentic-RL-specific terms rather than 'agent'/'reasoning'/'benchmark').
- Keep all new entries at abstract-only evidence level until full-text or code verification is performed; do not promote to published knowledge.
- Do not add any of the five candidates to published knowledge; keep all as abstract-only.
- Route Agora (2609.18094) to a human reviewer to decide whether it belongs as an adjacent multi-agent/harness source; if retained, archive with an explicit 'abstract-only, unverified' note.
- Skip JEPA-Anything, Verifiable Social Reasoning, Self-Evolving Search Index, and HypoEvolve as out of core Agentic RL scope; optionally log them in a separate 'adjacent/out-of-scope' list.
- Tighten the discovery query to require RL-training signals (policy optimization, advantage/credit assignment, on-policy/off-policy, reward modeling) to reduce low-precision matches.
- If any candidate is later promoted, require code-checked evidence (repo commit, reproduction) before upgrading evidence_level beyond abstract-only.
