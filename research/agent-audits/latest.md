# Agent audit · 2026-09-17 15:55 UTC

> DeepSeek generated triage only. Human review is required; this file does not publish sources or claims.

**Summary:** Audited 5 discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (35 sources). No duplicates of existing source IDs were found. Two entries are directly on-topic for agentic RL (ModularRSI on harness self-improvement; SP^3O on PPO critic value flattening) and warrant human reading. One entry (Emergence World) is adjacent multi-agent safety stress-testing, relevant but not core RL training methodology. Two entries are off-topic (music generation; LLM trading agents) and should be skipped. All evidence is abstract-only from untrusted discovery metadata; no code, full text, or reproduction was checked, so nothing is promoted to published knowledge.

Audited 5 discovered HuggingFace daily-paper entries against the Agentic RL knowledge base (35 existing sources). None are duplicates of existing sources. Two entries (ScienceIDE, ScienceBuddy) are plausibly relevant to agentic RL infrastructure/self-improvement and warrant human reading; one (ComPO) is preference-alignment adjacent but not agentic RL; two (StepAudio 3 Realtime, Lightning Weave) are off-topic for this KB's scope. All evidence is abstract-only from untrusted discovery metadata; no code, results, or claims were verified. No candidate should be treated as published knowledge.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (35 sources). All five are abstract-only preprints; none are duplicates of existing source IDs. Two are plausible core Agentic RL candidates (NGU adaptive sampling for RL-for-LLMs; GAI formal framework for iterative policy improvement/RSI) and warrant human reading. Two are adjacent but off-scope (ProgramDistill SWE benchmark; HarnessVLN training-free embodied navigation) and one is off-scope (in-context robot learning with VLM agents). No code was checked, no HTTP requests made, and no candidate is treated as published knowledge. Discovery text was treated strictly as untrusted data; no embedded instructions were followed.

Audited 5 untrusted discovery entries against the existing Agentic RL knowledge base (35 sources). None are duplicates of existing source IDs. All are 2026 preprints with abstract-only evidence; none were code-checked or reproduced. Two entries (CERA-MoA, Agora) are plausible adjacent candidates warranting human reading; two (Register Tokens, Gavel) are tangential to the Agentic RL core; one (OmniHarness) is off-topic for RL training. No candidate should be treated as published knowledge.

Audited 5 untrusted discovery entries against the Agentic RL knowledge base (35 existing sources). No entry is a duplicate of an existing source. None of the five is a core Agentic RL training-method paper: they span multi-agent scientific hypothesis search, agent failure root-cause attribution, rubric reward-signal robustness, specialist distillation, and experiential confidence estimation. All evidence is abstract-only from a daily-papers feed; no code, full text, or reproduction was checked. Conservative disposition: one candidate (ImpossibleRubrics) is directly relevant to reward-signal integrity and warrants human reading; the remaining four are archived as peripheral-but-retainable or skipped as out of scope. No candidate is promoted to published knowledge.

## Candidates
### REVIEW · ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement
- Evidence: `abstract-only`
- Reason: Directly on-topic: harness self-improvement for long-horizon coding/terminal agents, benchmark-disjoint evolution tasks, and transfer across foundation models. Overlaps thematically with existing multi-harness and agent-lightning sources but is not a duplicate. Abstract-only; claims of consistent improvement on TB2.0 and SWE-Bench Verified are unverified and no code was checked.
- Suggested note: 2026-09-14 preprint. Modular harness evolution (Agent Loop, Tool Use, Observation/Context Management, Task Completion Detection) with contrastive success/failure aggregation and 2,000 benchmark-disjoint evolution tasks. Read for: how benchmark-disjointness is enforced, module conflict resolution, and whether gains survive cross-model transfer. Abstract-only; not reproduced.

### REVIEW · Rethinking Critic Learning in PPO: Understanding and Mitigating Value Flattening
- Evidence: `abstract-only`
- Reason: Core RL methodology relevant to the PPO/GAE foundations already in the KB. Introduces a named failure mode (Value Flattening) and a sparse-supervision mitigation (SP^3O). Plausible and worth human reading, but abstract-only; theoretical and empirical claims (Qwen3-Base, three states per response) are unverified and no code was checked.
- Suggested note: 2026-09-16 preprint. Claims PPO critics exhibit 'Value Flattening' tied to an implicit variance penalty and correlated-state redundant updates; proposes SP^3O supervising few well-separated states per response. Read alongside ppo and gae entries. Abstract-only; verify against a controlled environment and check whether the effect reproduces outside the reported setup.

### REVIEW · Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems
- Evidence: `abstract-only`
- Reason: Adjacent to the KB's multi-agent and safety interests (marl-book, lilian-reward). Relevant to long-horizon agent failure modes, prompt injection, and memory persistence, but it is a safety stress-test study rather than an RL training method, so it is not core to the Agentic RL training thread. Abstract-only; large-scale operational claims (850k LLM calls, 16 days) are unverified.
- Suggested note: 2026-09-15 preprint. Eight parallel 10-agent worlds; three controlled stress events (indirect prompt injection, misinformation, private-memory exposure). Key claim: model-level alignment is not compositional. Read for failure-mode taxonomy and containment-vs-detection distinction. Abstract-only; treat reported statistics as unverified.

### SKIP · StepAudio 3 Music Technical Report
- Evidence: `abstract-only`
- Reason: Off-topic: long-form music generation. Keyword matches (DPO, preference optimization, planning, curriculum) are incidental; the work is not about agentic RL or agent training. No relevance to the KB scope.
- Suggested note: Skip. Music generation; DPO used only as a final alignment step. Not agentic RL.

### SKIP · EvolveTrade: Experience-Driven Policy Refinement for Self-Evolving LLM Trading Agents
- Evidence: `abstract-only`
- Reason: Off-topic for this KB: domain-specific LLM trading agents with prompt-as-policy refinement, not RL training methodology. Keyword matches (tool use, policy, agent) are incidental. No core contribution to Agentic RL foundations or frontier.
- Suggested note: Skip. Trading-agent prompt refinement; no RL training contribution relevant to this KB.

### REVIEW · ScienceIDE: Turning World's Scientific Codebase into Agent Learnable Environments
- Evidence: `abstract-only`
- Reason: Directly on-topic: proposes infrastructure converting scientific code repos into executable environments for agent learning, explicitly supporting RL, SFT, and evaluation, and reports a trained model family. Plausibly relevant to the KB's environment/harness and agent-training threads. Not a duplicate of existing sources. Abstract-only; no code or results verified, and the listed GitHub URL is untrusted discovery text and was not checked.
- Suggested note: Candidate for the environment/harness section. Abstract claims executable environments for scientific agents supporting RL/SFT/eval plus a PhAI-IDE model family. Needs human reading of the full paper before any note; verify environment construction, task generation, and whether RL is actually used vs. only SFT. Do not cite results yet.

### REVIEW · ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents
- Evidence: `abstract-only`
- Reason: On-topic for agentic RL: couples harness evolution (inner recursion) with model RL training (outer recursion), which relates to the KB's multi-harness and agent-training themes. Not a duplicate. Abstract-only; the 'recursive-in-recursive' framing and benchmark claims are unverified, and the listed website is untrusted discovery text and was not accessed.
- Suggested note: Candidate for the harness-evolution / self-improvement thread; compare against existing multi-harness and agent-lightning notes. Abstract describes alternating harness and model improvement. Needs full-paper reading to confirm the RL loop, evaluation rubrics, and whether claims are reproducible. Treat as unverified preprint.

### SKIP · A Zeroth-Order Paradigm for LLM Preference Alignment
- Evidence: `abstract-only`
- Reason: Preference-alignment method (ComPO) for LLM alignment, not agentic RL. The KB already covers preference optimization via DPO and RLHF sources; this is adjacent but outside the stated scope of Agentic RL from foundations to frontier. No agent, environment, or multi-step decision-making content in the abstract.
- Suggested note: Out of scope for this KB. If a preference-optimization sub-collection is ever added, revisit; otherwise skip.

### SKIP · StepAudio 3 Realtime Technical Report
- Evidence: `abstract-only`
- Reason: Audio-language realtime dialogue model with a voice agent; keyword matches ('agent', 'reasoning', 'tool', 'benchmark') are superficial. Not about RL training of agents and outside the KB's scope. No relevance to agentic RL foundations or frontier.
- Suggested note: Irrelevant to this KB; skip.

### SKIP · Lightning Weave: Improving the Accuracy-Efficiency Frontier of Reasoning Models through Capability Composition
- Evidence: `abstract-only`
- Reason: Post-training capability-composition / on-policy distillation for reasoning models. Related to reasoning-model efficiency, not agentic RL (no agent, environment, or multi-step interaction). Name similarity to 'Agent Lightning' is coincidental and not a duplicate. Outside KB scope.
- Suggested note: Out of scope; skip. If a reasoning-efficiency/distillation sub-collection is added, reconsider.

### REVIEW · Learning to Solve Hard Problems in RL for LLMs by Never Giving Up
- Evidence: `abstract-only`
- Reason: Directly on-topic for Agentic RL training: adaptive sampling / compute reallocation for hard problems, GRPO comparison, off-policy robustness discussion. Authors include known RL-for-LLM researchers. Abstract claims improvements on Deepscaler and Manufactoria but no code or reproduction was verified.
- Suggested note: Abstract-only preprint (2026-09-11). Claims a 'Matthew Effect' in RL-for-LLMs and proposes Never Give Up (NGU) adaptive sampling with asynchronous RL. Relevant to GRPO/DAPO sampling and off-policy robustness threads. Needs human reading of method and experimental setup; verify claims against DAPO/GRPO baselines before any catalog entry.

### REVIEW · Generalized Agent Iteration: One Formal Framework for Iterative Policy Improvement and Recursive Self-Improvement
- Evidence: `abstract-only`
- Reason: Conceptual/formal framework connecting generalized policy iteration (GPI) to recursive self-improvement (RSI), with two axes (improver inside/outside agent; external grounding). Potentially useful as a conceptual scaffold for the knowledge base, but it is a position/framework paper with no empirical validation in the abstract.
- Suggested note: Abstract-only preprint (2026-09-11). Proposes Generalized Agent Iteration (GAI) as a unifying framework for GPI and RSI, with dials for improver location and external anchoring. Treat as conceptual scaffolding only; no experiments or code verified. Cross-check against sutton-barto GPI chapter before citing.

### ARCHIVE · ProgramDistill: From Interactive Web Apps to Verifiable Reference-Guided SWE Tasks
- Evidence: `abstract-only`
- Reason: Adjacent to existing SWE-bench / SWE-agent sources but is a benchmark for coding agents rather than an RL training method. Could be relevant later for curriculum-based training of coding agents. Not a duplicate of existing IDs.
- Suggested note: Abstract-only preprint (2026-09-16). Benchmark of 4,063 reference-guided SWE tasks from 26 web apps. Retain as a possible future benchmark reference; not core Agentic RL training content. Verify task construction and leakage properties before use.

### ARCHIVE · HarnessVLN: Unifying Training-Free Embodied Navigation through an Agent Harness
- Evidence: `abstract-only`
- Reason: Training-free embodied navigation agent harness; overlaps thematically with agent-harness and tool-interface sources but is outside the LLM Agentic RL training focus. No RL training component. Retain only as peripheral reference.
- Suggested note: Abstract-only preprint (2026-09-14). Zero-shot training-free navigation harness with hierarchical event memory and spatiotemporal graph. Peripheral to Agentic RL; archive for possible cross-reference on agent harness design, not for RL training claims.

### SKIP · In-Context Robot Learning with VLM Agents
- Evidence: `abstract-only`
- Reason: In-context robot learning with VLM agents; explicitly no gradient updates and no RL training loop. Outside the scope of Agentic RL from foundations to frontier. No overlap with existing sources.
- Suggested note: Abstract-only preprint (2026-09-16). VLM-based in-context robot learning without gradient updates; not RL training. Skip as out of scope.

### REVIEW · CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents
- Evidence: `abstract-only`
- Reason: Directly on-topic for Agentic RL: co-evolving router and agent policies via iterative RL, with a familiarity estimator to avoid full rollouts. Overlaps thematically with existing routing/credit-assignment sources (gigpo, agent-lightning, multi-harness) but is not a duplicate. Abstract-only; no code or reproduction verified.
- Suggested note: 2026-09-17: Co-evolving router + agent policies via iterative RL; predictive familiarity estimator from mid-layer hidden states to avoid full rollouts; cumulative-threshold adaptive routing. Read for routing/credit-assignment angle; verify claims against gigpo and multi-harness. Abstract-only, not reproduced.

### REVIEW · Agora: Git as Shared Memory for Collective AutoResearch
- Evidence: `abstract-only`
- Reason: Relevant to multi-agent/collective agentic systems and shared memory, adjacent to existing multi-agent and agent-memory sources. Reports a long autonomous run with claimed independent reproductions, but the abstract itself notes the controlled comparison that would settle the core claim has not been done. High upvote count is not evidence of correctness. Abstract-only.
- Suggested note: 2026-09-17: Git-DAG shared memory for collective coding agents; append-only commits with verification status and diversity-aware selection. Reported 12-day run, 1703 contributions, 165 claimed reproductions. Authors themselves flag the missing controlled comparison. Read critically; do not treat as established. Abstract-only.

### REVIEW · The Router Within: Eliciting Native Skill Routing from a Frozen LLM
- Evidence: `abstract-only`
- Reason: Skill routing for LLM agents is adjacent to the knowledge base (coskill, agentic-survey) but the method trains only two linear maps on a frozen backbone and is not an RL training contribution. Plausible but tangential to the Agentic RL core; worth a human read to decide whether it belongs as a skill-routing reference. Abstract-only.
- Suggested note: 2026-09-17: Frozen-LLM skill routing via two trained linear maps (Gavel); no skill text in context. Adjacent to coskill but not an RL method. Decide whether to include as a skill-routing reference. Abstract-only, not reproduced.

### SKIP · Register Tokens for Bounded-State Reasoning in Diffusion Language Models
- Evidence: `abstract-only`
- Reason: Primarily a diffusion-LM architecture contribution (register tokens for bounded-state reasoning). RL appears only as a final refinement step. Not central to Agentic RL foundations or frontier; low marginal value for this knowledge base.
- Suggested note: 2026-09-17: Diffusion-LM register tokens for bounded-state reasoning; RL only as optional refinement. Out of scope for Agentic RL core. Skipped.

### SKIP · OmniHarness: Harnessing Generalizable Visual Generation via Symbolic Policy Learning
- Evidence: `abstract-only`
- Reason: Visual generation via symbolic policy learning with frozen model parameters; not RL training of agents. Off-topic for an Agentic RL knowledge base despite matching generic keywords (multi-agent, policy, benchmark).
- Suggested note: 2026-09-17: Symbolic policy learning for visual generation; frozen parameters, no RL training loop. Off-topic. Skipped.

### REVIEW · ImpossibleRubrics: Stress-Testing Generated Rubrics as Reward Signals
- Evidence: `abstract-only`
- Reason: Directly touches a core Agentic RL concern already represented in the KB (reward hacking, lilian-reward): whether LLM-generated rubrics used as reward signals can be adversarially exploited. Abstract reports a benchmark of 169 impossible tasks with verifiable oracle certificates plus 48 answerable controls, and reports exploitation rates (8-26% on an unbiased cut; 36% for the strongest generator on a stress cut; 64% for a single generic rubric). These are self-reported abstract numbers, not verified; no code or full text was inspected. Plausible and relevant enough to require human reading before any note is written.
- Suggested note: Candidate for the reward-signal-integrity thread alongside lilian-reward. Claim to verify on reading: generated rubrics can be gamed by adversarial answers, and task-tailored rubrics may be exploited more than a single generic rubric. Check benchmark construction, the oracle-certificate definition, the 150-of-169 cut, and whether exploitation rates are reproducible. Do not cite numbers until full text and any released code are checked.

### ARCHIVE · Root-Cause Attribution Is a Search Problem: Continual Search for Long-Horizon Agent Failures
- Evidence: `abstract-only`
- Reason: Relevant to agent reliability and long-horizon evaluation, which the KB covers via agentic-survey, tau-bench, and webarena, but it is a diagnostic/attribution method rather than an RL training contribution. Abstract-only; the reported F1 improvement (0.349 to 0.498 on a newly introduced MegaRCA-Mix set of 50 annotated trials) is unverified and the benchmark is self-introduced, so it cannot be treated as established. Retain for possible future reading without publishing.
- Suggested note: Peripheral to the Agentic RL core; relevant if the KB later adds an agent-failure-diagnosis or observability thread. Note that MegaRCA-Mix is introduced by the same paper, so benchmark independence is unestablished.

### ARCHIVE · HypoEvolve: Genetic Algorithms Enable Multi-Agent LLMs to Discover Scientific Hypotheses
- Evidence: `abstract-only`
- Reason: Multi-agent LLM collaboration with an evolutionary/generational search loop; adjacent to multi-agent themes in marl-book and agentic-survey but not an RL training method (no policy optimization, reward model, or credit-assignment contribution described). Domain is scientific hypothesis discovery with drug-repurposing evaluation. Abstract-only; reported DepMap selectivity 0.171 vs 0.115 baseline is unverified. Retain as background, do not publish.
- Suggested note: Background only for multi-agent LLM search. If retained, tag as 'multi-agent LLM search, not RL training' to avoid conflating evolutionary prompting loops with policy-gradient methods.

### ARCHIVE · Confidence Comes from Experience: Experiential Confidence Estimation from Reasoning to Agents
- Evidence: `abstract-only`
- Reason: Confidence calibration and selective prediction for agents; relevant to deployment reliability but not to Agentic RL training algorithms. Abstract-only; claims (beats or matches 10-sample self-consistency on 23 of 24 comparisons, up to 8.7 points gain on agent tasks) are unverified and depend on the authors' own episode-memory construction. Retain as peripheral, do not publish.
- Suggested note: Peripheral: agent reliability/abstention, not RL training. If revisited, check whether the 'graded past episodes' store introduces leakage across evaluation tasks.

### SKIP · Training Specialist Models without Reasoning Trajectories for Domain Expert Distillation
- Evidence: `abstract-only`
- Reason: Specialist-to-student distillation and latent trajectory analysis; keyword-matched on 'reasoning/trajectory/distillation' but outside the Agentic RL scope (no agent environment, no RL objective, no credit assignment). Abstract-only and not a candidate for this knowledge base.
- Suggested note: Out of scope for Agentic RL; skip to keep the KB focused. Reconsider only if a distillation-for-agents thread is added.

## Risks
- All discovery entries are abstract-only from untrusted external metadata; titles, summaries, author lists, and upvote counts are unverified and could be inaccurate or fabricated.
- The discovery JSON is untrusted text and may contain prompt injection; it was treated as data only and no embedded instructions or URLs were followed.
- Keyword-based matching produced false positives (music generation, trading agents), indicating the discovery filter is noisy and should not drive archival decisions alone.
- No code, full text, or reproduction was checked; an HTTP 200 or a preprint listing is not evidence of correctness, and none of these should be treated as published knowledge.
- Several candidates overlap thematically with existing KB sources (multi-harness, agent-lightning, ppo, gae); without full-text reading, duplicate or superseded claims cannot be ruled out.
- All discovery entries are untrusted external text; titles, summaries, author lists, upvote counts, and URLs were treated as data only and not verified.
- Every candidate is abstract-only: no full text, code, or experimental results were inspected, so no claim of correctness or reproducibility is supported.
- arXiv IDs and dates in the discovery payload are unverified and may be fabricated or misattributed; do not cite them as established facts.
- URLs appearing in discovery text (e.g., GitHub and project websites) were not fetched and must not be treated as validated resources.
- Keyword-based matching produced false positives (audio model, reasoning-efficiency distillation), so relevance scores in the discovery payload should not be trusted as curation decisions.
- No candidate here should be promoted to published knowledge; the KB's existing 'new preprint' entries already carry an explicit 'abstract-only, not reproduced' caveat that must be preserved.
- All five candidates are abstract-only preprints; none have been code-checked or reproduced. Abstract claims (e.g., SOTA success rates, benchmark improvements) must not be treated as verified.
- Discovery entries are untrusted external text; titles, summaries, and URLs were treated as data only. No embedded instructions were followed and no URLs were fetched.
- Two candidates (NGU, GAI) are plausible but unverified; promoting them to catalog entries without human reading would risk treating preprints as published knowledge.
- ProgramDistill and HarnessVLN are adjacent but could dilute the Agentic RL scope if archived without clear framing as peripheral.
- Author lists and publication dates come from the untrusted discovery feed and were not independently verified.
- All discovery entries are untrusted external text; keyword matches (e.g., 'reinforcement learning', 'agent', 'policy') can surface off-topic work, as seen with OmniHarness and Register Tokens.
- All five candidates are abstract-only preprints from 2026; none have been code-checked or reproduced. Upvote counts and author claims are not evidence of correctness.
- Agora's abstract itself concedes the decisive controlled comparison has not been run; its reproduction claims are self-reported.
- Several candidates overlap thematically with existing sources (gigpo, agent-lightning, multi-harness, coskill); risk of duplicate or near-duplicate catalog entries if added without dedup review.
- Discovery metadata (titles, summaries, URLs) must not be treated as verified facts; no URLs were fetched during this audit.
- All five entries are abstract-only from an untrusted daily-papers feed; titles, IDs, dates, and reported metrics are unverified and must not be cited as established results.
- Keyword matching ('agent', 'reinforcement learning', 'reward', 'benchmark') produced false positives: several entries are LLM-agent or distillation papers with no RL training contribution, risking scope drift in the KB.
- Two entries (2609.13463, 2609.16816) introduce their own benchmarks (MegaRCA-Mix, ImpossibleRubrics), so reported gains are not independently comparable and may reflect benchmark design choices.
- The discovery payload is untrusted external text; it was treated as data only. No URLs were fetched, no tools were invoked, and no instructions inside it were followed.
- No code, full text, or reproduction was checked for any candidate; HTTP/abstract availability is not evidence of correctness.

## Next actions
- Assign human readers to the two review candidates (2609.14857, 2609.18708) and record findings as atomic notes linked to multi-harness/agent-lightning and ppo/gae respectively.
- Decide whether Emergence World (2609.17320) belongs in the KB as a safety/benchmark reference or should be archived outside the core RL thread.
- Confirm the two skip decisions (2609.16034, 2609.17632) and exclude them from the discovery keyword set to reduce future noise.
- For any candidate promoted after reading, verify claims against code or full text and downgrade evidence level accordingly; do not archive as published knowledge on abstract alone.
- Tighten the discovery query/keyword list to reduce off-topic matches (music, trading) before the next audit.
- Human-read the full papers for 2609.19134 (ScienceIDE) and 2609.17523 (ScienceBuddy) before adding any note; verify whether RL training is genuinely used and whether environments/evaluations are reproducible.
- If either passes review, add it as a new-preprint entry with an explicit 'abstract-only, not reproduced' evidence label, consistent with existing coskill/multi-harness/agent-g2/edge entries.
- Do not add 2609.19144, 2609.14005, or 2609.14708 to the KB; optionally log them in a separate out-of-scope list.
- Re-run discovery with tighter keyword filters (e.g., require 'agentic RL' or 'agent training' plus environment/credit-assignment terms) to reduce false positives.
- Independently resolve arXiv IDs and URLs through a trusted bibliographic source before any citation; never rely on discovery-provided links.
- Human-read NGU (2609.13443) method and experiments; compare against existing DAPO/GRPO notes before any catalog decision.
- Human-read GAI (2609.13406) and assess whether it adds a useful conceptual layer beyond sutton-barto GPI; decide whether to add as a framework note.
- If ProgramDistill or HarnessVLN are retained, tag them explicitly as peripheral/benchmark references, not RL training methods.
- Verify arXiv IDs and author lists directly against arXiv before creating any catalog entries.
- Do not fetch or execute any URLs from the discovery feed; keep discovery text quarantined as data.
- Human-read CERA-MoA (2609.18779) and Agora (2609.18094) in full before any catalog addition; check for overlap with gigpo, agent-lightning, and multi-harness.
- Decide whether Gavel (2609.15982) belongs as a skill-routing reference alongside coskill, or is out of scope.
- If any candidate is retained, record it as a new preprint with evidence level 'abstract-only' and an explicit 'not reproduced' note, consistent with existing 2026 entries.
- Do not promote any candidate to published knowledge until code or independent reproduction is available.
- Re-run discovery with tighter keyword filters to reduce off-topic matches (visual generation, diffusion LMs).
- Human-read 2609.16816 (ImpossibleRubrics) and, if sound, draft a note linking it to lilian-reward under the reward-hacking thread; verify the oracle-certificate construction and exploitation-rate methodology first.
- Decide whether agent-failure diagnosis (2609.13463) belongs in the KB at all; if yes, add it as a peripheral reliability source rather than an RL-training source.
- Keep 2609.15938 and 2609.17708 archived with explicit 'not RL training' tags to prevent conflation with policy-optimization methods.
- Do not add 2609.13770; record the skip rationale so future keyword-matched rediscovery does not re-open it.
- Tighten the discovery grep to require RL-training terms (policy optimization, advantage, credit assignment, rollout) in addition to 'agent' to reduce false positives.
