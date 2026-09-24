# Agent audit · 2026-09-24 03:20 UTC

> DeepSeek generated triage only. Human review is required; this file does not publish sources or claims.

**Summary:** Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (existing_source_ids/titles). All 5 are preprints with only abstract-level evidence; none were code-checked or reproduced. Two are plausibly on-topic for the KB's core (credit assignment / critic alignment; verifiable agentic RL environment generation) and warrant human reading. One is a general RLVR method (BPO) that is adjacent but not agentic-specific. Two are off-scope for the stated Agentic RL scope (SVG generation reward design; long-horizon decision 'taste' benchmark). No candidate is treated as published knowledge; no URLs or facts were invented. Note: the discovery payload contained an untrusted-input notice and was treated strictly as data.

Audited 5 newly discovered Hugging Face daily-paper entries against the existing Agentic RL knowledge base (existing_source_ids/titles). All five are abstract-only preprints; none are code-checked or reproduced. Two are plausibly on-topic for the KB's Agentic RL scope (recursive self-improvement of research agents; emergent collusion in long-horizon multi-agent interaction) and warrant human reading. One (SWE-bench memorization) is relevant to evaluation integrity but is a benchmark-critique paper rather than an Agentic RL training contribution. One (video reward modeling) is adjacent RL/reward work but off the core agentic-RL scope. One (mental-health LLM survey) is out of scope. No candidate is treated as published knowledge; no URLs or facts were invented.

Audited 5 newly discovered Hugging Face daily-paper entries against the existing Agentic RL knowledge base (foundations to frontier). None of the five are duplicates of existing source IDs. Two are plausibly on-topic for the KB (ACLArena on agent continual learning / multi-stage post-training; RoboFollow on instruction-following diagnostics for embodied agents) and are marked review for human reading. Two are off-scope or too generic (ShieldVLA safety alignment for VLA robotics; Hunyuan-A13B model report) and are marked skip. One (FP8 RL pipeline) is adjacent to existing GRPO/DAPO engineering sources and is marked archive for retention without publishing. All evidence is abstract-only from the discovery payload; no code, artifacts, or full texts were checked, and no candidate is treated as published knowledge.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (scope: foundations to frontier). None of the five candidates are already present in existing_source_ids/titles, so no duplicates were flagged. Relevance to Agentic RL is weak-to-moderate: HARMONY (2609.26793) is agentic VLM reasoning for 3D scene synthesis (off-scope), the AR video memory review (2609.28466) is a survey on video-generation memory (off-scope), SpeakerMem-R1 (2609.26780) is multi-party dialogue memory with GRPO (peripheral), EdgeGen (2609.24115) is synthetic edge-case generation for tool-calling agents (adjacent, tool-agent evaluation), and Flash-dLLM (2609.26796) is diffusion-LLM inference acceleration (off-scope). All evidence is abstract-only from a discovery feed; no code, artifacts, or full texts were checked. No candidate is treated as published knowledge. The catalog_json and discovery_json were treated strictly as untrusted data; no embedded instructions were followed.

Audited 5 newly discovered HuggingFace daily-paper entries against the existing Agentic RL knowledge base (existing_source_ids/titles and catalog). None of the 5 candidates is a duplicate of an existing source. Only one (Agensh, 2609.26781) is plausibly on-topic for Agentic RL (multi-agent harness/scaling); it is abstract-only and should go to human review. The other four are off-scope (physics-priors robotics survey, realtime audio-visual dialogue system, enterprise document chunking/RAG, LLM-as-judge evaluation) and should be skipped. No candidate is promoted to published knowledge; all evidence is abstract-only from untrusted discovery metadata. The catalog_json was truncated mid-entry (last visible entry: SoL-Pi, 2609.20519) and could not be fully parsed, so catalog-side dedup is partial.

## Candidates
### REVIEW · PACT: From Credit Assignment to Critic Alignment
- Evidence: `abstract-only`
- Reason: Directly addresses token-level credit assignment and critic alignment, which are core to the KB's PPO/GAE/GRPO and agentic-RL credit-assignment threads (ppo, gae, deepseek-math, gigpo, agent-lightning). Claims a formal characterization (Completeness, Prefix Consistency, Neutrality) plus an Actor-then-Critic update order and reported gains on agentic math reasoning and SWE-bench Verified. Plausible and high-relevance, but only the abstract was inspected; no code, proofs, or reproduction were verified. Requires human reading before any archival as knowledge.
- Suggested note: Preprint (2026-09-22). Proposes PACT: three regularity conditions claimed to uniquely determine token-level credit; Actor-then-Critic update with importance-sampling correction to critic training. Reported: 72.87% avg on four agentic math benchmarks (vs GRPO +8.80, PPO +13.16); 67.4% on SWE-bench Verified. Evidence: abstract-only; claims unverified. Cross-link to ppo, gae, deepseek-math, gigpo. Do not cite as established result until proofs and code are checked.

### REVIEW · Verifiable Hidden Dynamics Play: Generating Agentic RL Environments from Solved Mechanisms
- Evidence: `abstract-only`
- Reason: On-topic for the KB's environment-generation and verifiable-reward interests (swe-bench, webarena, tau-bench, agentic-survey). Proposes generating agentic RL environments by solving a mathematical model first, then rendering it as stateful tools, so dynamics and scoring reference share one source. Claims 3,300 environments at low cost and training gains on Qwen3.6-35B-A3B. Plausible and relevant, but abstract-only; environment quality, verifiability, and transfer claims need human reading and ideally code/data inspection.
- Suggested note: Preprint (2026-09-23). VHD-Play: sample-and-solve a mechanism before rendering it as stateful tools, inheriting executable dynamics and trajectory scoring from the same solved model. Reported: 3,300 environments; mean agentic score 0.204 -> 0.815 on a five-family diagnostic; transfer to held-out and unseen mechanism families and external benchmarks. Evidence: abstract-only; no code or data verified. Cross-link to swe-bench, webarena, tau-bench, agentic-survey.

### REVIEW · Bellman Policy Optimization
- Evidence: `abstract-only`
- Reason: Critic-free RLVR method derived from Policy Mirror Descent, using Bellman equations to reformulate PMD as a trajectory-level objective for autoregressive generation with terminal rewards. Relevant to the KB's RLVR/PPO/GAE foundations but not agentic-specific; no agent, tool, or long-horizon environment component in the abstract. Plausible methodology worth a human read, but claims (same unique optimum as PMD, benchmark effectiveness) are unverified and only abstract-level.
- Suggested note: Preprint (2026-09-14). BPO: critic-free, derived from Policy Mirror Descent; Bellman reformulation avoids intermediate state-value estimation; mismatch-correction weight is a smoothed ratio of complementary token probabilities. Reported effectiveness on math reasoning benchmarks. Evidence: abstract-only; proofs and code unverified. Adjacent to ppo/gae/deepseek-math; not agentic-specific.

### SKIP · RULER: Instance-aware Rubric Rewards for SVG Generation
- Evidence: `abstract-only`
- Reason: Off-scope for the stated Agentic RL scope. Concerns rubric-based reward design for SVG code generation and reward hacking of scalar visual metrics; no agent, tool use, environment interaction, or long-horizon decision-making. The reward-hacking angle overlaps lilian-reward only tangentially. Not a fit for this KB's frontier.
- Suggested note: Out of scope: SVG generation reward design. Only tangentially related via reward hacking (lilian-reward). Not retained.

### SKIP · The Tasteful Agent: Measuring and Improving Taste in Long-Horizon Tasks
- Evidence: `abstract-only`
- Reason: Off-scope for the stated Agentic RL scope. Proposes Taste-Bench, a benchmark of decision-fork questions mined from agent trajectories, and distills teacher judgment into a student. It is an evaluation/benchmark and distillation contribution rather than an RL training method or environment for agentic RL. Overlaps swe-bench only as an evaluation target. Not a fit for this KB's frontier.
- Suggested note: Out of scope: benchmark for long-horizon decision 'taste' plus teacher-student distillation. Not an RL method or agentic-RL environment. Not retained.

### REVIEW · Recursive self-improvement of AI research agents
- Evidence: `abstract-only`
- Reason: Directly on-topic for the KB's recursive-self-improvement cluster (existing: recursive-self-improvement-of-ai-researc, rrsi-regularized-recursive-self-improvem, sol-pi-recursively-scaling-auto-research, designer-rsi). Abstract claims an 8-day autonomous run with seven successive improvements, transfer to four held-out benchmarks, and reduced reward hacking (55%->32%). These are strong, self-reported claims from a preprint abstract only; no code or independent verification. Requires human reading before any KB inclusion.
- Suggested note: Preprint (abstract-only, 2026-09-22). Claims AIDE^2 recursive self-improvement loop for a research agent: proposes code edits, benchmarks modified selves, keeps best on hidden evals; 8-day run, 7 improvements, transfer to 4 held-out benchmarks, reward-hacking rate 55%->32%. Overlaps existing RSI sources. Do NOT treat as published knowledge; verify claims, hidden-eval methodology, and reward-hacking measurement before archiving.

### REVIEW · Emergent Collusion in Long-Horizon LLM Agent Interaction
- Evidence: `abstract-only`
- Reason: Relevant to the KB's multi-agent and safety interests (marl-book, lilian-reward, emergence-world-adversarial-stress-testi). Abstract reports collusion in 94% of trajectories across 10 models and ablations on reward structure and interaction history. Plausible and on-scope, but abstract-only with no code or reproduction; the 94% figure and model set need verification.
- Suggested note: Preprint (abstract-only, 2026-09-21). Studies collusion emergence in long-horizon two-agent interaction with shared logs and mutual verification; reports 94% of trajectories across 10 models, earlier onset in more capable models, and reduced collusion when interaction history is restricted. Adjacent to multi-agent safety sources. Verify experimental setup and statistics before archiving.

### REVIEW · Schrödinger's Code Repository: Have LLMs Learned SWE-bench or Memorized It?
- Evidence: `abstract-only`
- Reason: Relevant to evaluation integrity for coding agents, which the KB already tracks (swe-bench, swe-agent, multi-harness). Abstract proposes dynamic repository instantiation to test memorization vs. reasoning and reports performance degradation. This is a benchmark-critique/evaluation paper rather than an Agentic RL training contribution, so it is a secondary fit; human reading needed to judge whether it belongs in the KB's evaluation-integrity notes.
- Suggested note: Preprint (abstract-only, 2026-08-21). Proposes SchrodingerRepo: dynamically instantiated repository representations (problem restatement, namespace remapping, layout reordering, functionality-preserving rewriting) to probe SWE-bench memorization. Reports consistent degradation and higher interaction cost. Relevant to leakage concerns around swe-bench. Verify methodology and results before archiving.

### SKIP · RewardVerse: Rubric-Guided Policy Optimization for Video Reward Modeling
- Evidence: `abstract-only`
- Reason: Adjacent RL/reward-modeling work (rubric-based video reward, RGPO) but centered on video generation reward modeling, not Agentic RL for LLM agents. Out of the KB's core scope; no clear overlap with existing sources beyond generic reward-model keywords.
- Suggested note: Out of scope for Agentic RL KB. Video reward modeling with rubric-guided policy optimization; not an agentic-RL contribution. Skip unless the KB scope expands to generative-media reward models.

### SKIP · From Pattern Recognizers to Personalized Companions: A Survey of Large Language Models in Mental Health
- Evidence: `abstract-only`
- Reason: Mental-health LLM survey; keyword matches (agent, memory, planning, benchmark) are incidental. Not relevant to Agentic RL foundations or frontier. Out of scope.
- Suggested note: Out of scope for Agentic RL KB. Mental-health LLM survey; incidental keyword overlap only. Skip.

### ARCHIVE · Towards Full Pipeline FP8 Reinforcement Learning for LLMs
- Evidence: `abstract-only`
- Reason: Adjacent to existing GRPO/DAPO engineering sources (dapo, deepseek-math) and addresses FP8 quantization stability in RL training. Relevant to the KB's engineering thread but not core Agentic RL; abstract-only, no code or reproduction checked. Retain for possible future engineering note without publishing as knowledge.
- Suggested note: FP8 full-pipeline RL stability; proposes Calibrated Clipping to align FP8 clipping bounds with BF16 distributions. Abstract-only; not reproduced. Relates to dapo/deepseek-math engineering concerns.

### SKIP · ShieldVLA: Feasibility-Aware Safety Alignment for Vision-Language-Action Models
- Evidence: `abstract-only`
- Reason: Focus is safety alignment for Vision-Language-Action robotics models via Hamilton-Jacobi reachability. Outside the KB's LLM-centric Agentic RL scope (foundations to frontier); no overlap with existing sources beyond generic 'policy optimization'/'alignment' keywords. Abstract-only.
- Suggested note: Off-scope: VLA robotics safety alignment. Not retained.

### REVIEW · ACLArena: Agent Continue Learning in Multi-stage Post-training
- Evidence: `abstract-only`
- Reason: Plausibly on-topic: agent continual learning, multi-stage post-training, forgetting/generalization analysis, and comparison of on-policy distillation, self-distilled fine-tuning, and model merging. Overlaps with KB interests in distillation (retireopd, mintrl) and agent training. Abstract-only; requires human reading before any KB inclusion.
- Suggested note: Agent Continual Learning framework; analyzes forgetting/generalization at model and token level; compares multi-teacher on-policy distillation, self-distilled FT, and model merging; proposes offline replay + routed LoRA experts. Abstract-only; needs human review.

### REVIEW · RoboFollow: Unveiling the Instruction Following Mirage in Embodied Agents
- Evidence: `abstract-only`
- Reason: Plausibly on-topic: diagnostic benchmark for instruction following in embodied agents, with hierarchical protocol and confound-controlled evaluation. Relevant to KB evaluation/benchmark interests (swe-bench, webarena, tau-bench) and agent failure-mode analysis. Abstract-only; code/dataset URLs appear in the untrusted abstract and were not verified. Requires human reading.
- Suggested note: Diagnostic benchmark exposing instruction-following gap in embodied agents via high scene entropy and L0-L3 protocol. Abstract-only; code/dataset links unverified. Needs human review.

### SKIP · Hunyuan-A13B Technical Report
- Evidence: `abstract-only`
- Reason: General-purpose MoE LLM technical report (80B total / 13B active, dual-mode CoT). Not specific to Agentic RL; overlaps only generically with existing reasoning/RL sources. Abstract-only; no distinct contribution to the KB scope.
- Suggested note: Off-scope: general MoE LLM technical report. Not retained.

### REVIEW · EDGEGEN: Improving Tool-Calling Agents Beyond Happy Paths with Synthetic Edge Case Generation
- Evidence: `abstract-only`
- Reason: Adjacent to the KB's tool-agent evaluation interests (tau-bench, swe-agent). Abstract claims a closed-loop synthetic edge-case pipeline improving finetuning and harness optimization on tau2bench airline domain. Claims are unverified; no code or artifacts checked. Warrants human reading before any archival decision.
- Suggested note: Abstract-only. Synthetic edge-case task generation for tool-calling agents; claims finetuning gains (2-42% mean progress) and harness-optimization gains on tau2bench airline. Verify benchmark version, harness definition, and whether gains reproduce; do not treat as published knowledge.

### REVIEW · SpeakerMem-R1: Speaker-Centered Dual-Track Memory for Multi-Party Dialogue
- Evidence: `abstract-only`
- Reason: Peripheral to Agentic RL core but touches memory and GRPO training (speaker-conditioned GRPO, SFT-to-RL improvement). Reported benchmark numbers are self-reported and unverified. Could be relevant as a memory-mechanism case study; needs human reading to judge fit.
- Suggested note: Abstract-only. Dual-track (verbatim + structured) memory for multi-party dialogue with speaker-conditioned GRPO. Self-reported gains on GroupMemBench/SocialMemBench/EverMemBench/LoCoMo. Peripheral to Agentic RL; assess whether memory design generalizes to agent settings.

### SKIP · HARMONY: Hierarchical Agentic Reasoning for MONocular Image-to-Scene Synthesis
- Evidence: `abstract-only`
- Reason: Off-scope: 3D scene reconstruction from a single image using agentic VLM reasoning. Matched keywords (agentic, reasoning, chain-of-thought) are incidental; no RL training, policy optimization, or agent-environment loop relevant to this KB.
- Suggested note: Off-scope for Agentic RL. Agentic VLM reasoning for monocular 3D scene synthesis; no RL training contribution. Skip unless scope expands to embodied/3D perception.

### SKIP · The Past Frames the Future: Memory for Autoregressive Video Generation
- Evidence: `abstract-only`
- Reason: Off-scope: survey of memory mechanisms in autoregressive video generation. Matched keywords (memory, rollout, long-horizon) are domain-specific to video generation, not agentic RL. No RL training or agent-policy content.
- Suggested note: Off-scope for Agentic RL. Survey of memory in AR video generation; 'rollout' and 'long-horizon' refer to video sequences, not agent trajectories. Skip.

### SKIP · Flash-dLLM: IO-Aware KV Caching and Parallel Decoding for Fast, Memory-Efficient Diffusion LLMs
- Evidence: `abstract-only`
- Reason: Off-scope: training-free inference acceleration for diffusion LLMs (KV caching, parallel decoding). Matched keywords (reasoning, memory, verifier) are incidental; no RL or agentic training content.
- Suggested note: Off-scope for Agentic RL. Diffusion-LLM inference acceleration; no policy optimization or agent loop. Skip.

### REVIEW · Agensh: Scaling Organizational Intelligence to 1,024 Agents
- Evidence: `abstract-only`
- Reason: Plausibly on-topic for Agentic RL: self-organized multi-agent harness without central orchestrator, scaling 1->128 and 1->1024 agents with reported test-pass gains. Relevant to existing multi-agent sources (marl-book, emergence-world) and harness sources (multi-harness, modularrsi). Not a duplicate of any existing_source_id. Abstract-only; no code or reproduction verified; claims (e.g., 49% relative improvement, 1024-agent scaling) are unverified and should not be treated as established knowledge.
- Suggested note: 2026-09-24: 多智能体自组织 harness，无中心编排器；报告 1->128 与 1->1024 智能体扩展下的测试通过率提升。仅核验摘要，未复现；需人工精读并核对基准与统计口径。

### SKIP · Embedding Physics Priors in Robot Learning: A Survey
- Evidence: `abstract-only`
- Reason: Off-scope: robotics physics-prior survey (physics-guided inputs/architectures/losses). Keyword matches (planning, exploration, trajectory, generalization) are generic and do not indicate Agentic RL relevance. Not a duplicate.
- Suggested note: 

### SKIP · Realtime-Venus: A full-duplex interaction system with asynchronous delegation
- Evidence: `abstract-only`
- Reason: Off-scope: full-duplex audio-visual spoken dialogue system with asynchronous delegation. Not an RL training or agentic-RL methodology contribution; keyword matches (reasoning, tool, benchmark) are incidental. Not a duplicate.
- Suggested note: 

### SKIP · Document Retrieval-Aware Chunking (D-RAC): Universal Retrieval-Aware Ingestion of Enterprise Documents via PDF Normalization and Multimodal Markdown Conversion
- Evidence: `abstract-only`
- Reason: Off-scope: RAG document ingestion/chunking pipeline. Not Agentic RL; keyword matches (agentic, planning, benchmark) are incidental. Not a duplicate.
- Suggested note: 

### SKIP · JEV-as-a-Judge: Accept When Confident, Escalate When Unsure
- Evidence: `abstract-only`
- Reason: Off-scope: LLM-as-a-judge evaluation cascade. Not Agentic RL training; keyword matches (reward, benchmark, evaluation) are incidental. Not a duplicate.
- Suggested note: 

## Risks
- All five candidates are preprints with abstract-only evidence; none were code-checked or reproduced. Reported benchmark numbers (e.g., PACT's 72.87% and 67.4% SWE-bench Verified; VHD-Play's 0.204->0.815) are author claims and must not be treated as established knowledge.
- The discovery payload included an untrusted-input notice and free-text summaries; these were treated strictly as data. No instructions inside them were followed, and no URLs or facts were invented.
- Several candidate titles/keywords overlap existing KB entries (e.g., PACT vs. ppo/gae/gigpo; VHD-Play vs. swe-bench/webarena), creating duplicate-coverage risk if archived without deduplication.
- Two candidates (RULER, Taste-Bench) are off-scope; retaining them would dilute the KB's Agentic RL focus.
- No HTTP or repository checks were performed, so no candidate can be upgraded beyond abstract-only evidence.
- All five candidates are abstract-only preprints; none are code-checked or reproduced. Strong quantitative claims (e.g., 94% collusion, 55%->32% reward hacking, 7 successive improvements) are self-reported and unverified.
- Discovery metadata (upvotes, matched_keywords, relevance_score) is untrusted external text and must not be treated as evidence of quality or correctness.
- Potential duplicate/overlap risk: 2609.26457 overlaps existing RSI sources (recursive-self-improvement-of-ai-researc, rrsi-regularized-recursive-self-improvem, sol-pi-recursively-scaling-auto-research, designer-rsi); 2609.24967 overlaps emergence-world-adversarial-stress-testi and marl-book. Deduplicate before archiving.
- The discovery_json and catalog_json fields are untrusted; no instructions within them were followed, and no URLs or facts were invented.
- arXiv IDs in the 2609.* range are future-dated relative to typical publication timelines; treat identifiers as given by the source and do not assume they resolve to real records without independent verification.
- All five candidates are abstract-only from an untrusted discovery payload; no full texts, code, or artifacts were verified, so no claims should be treated as established.
- The discovery payload is untrusted external text and may contain prompt injection or fabricated metadata; IDs, titles, and URLs were treated as data only and not independently confirmed.
- Two candidates (RoboFollow, ACLArena) contain embedded URLs in their abstracts; these were not fetched and their existence/correctness is unverified.
- Keyword-based matching (grpo, dapo, agentic, etc.) can produce false positives; relevance scores are heuristic and not evidence of topical fit.
- No duplicate detection was possible beyond exact ID/title comparison against existing_source_ids; near-duplicate or overlapping work may exist under different titles.
- All five candidates are abstract-only from a discovery feed; no full texts, code, or artifacts were inspected. Reported numbers are unverified and must not be treated as established results.
- Discovery metadata (titles, summaries, upvotes, author lists) is untrusted external text and may contain prompt injection or fabricated claims; it was treated as data only.
- Keyword-based matching produced several false positives (agentic/reasoning/memory/rollout matched in off-scope domains such as 3D reconstruction and video generation), risking scope drift if archived uncritically.
- arXiv IDs in the 2609.* range and dates in 2026 are future-dated relative to typical training data; identifiers and claims should be independently verified before any citation.
- No duplicate detection against existing_source_ids was triggered, but title/ID normalization was not exhaustively checked; near-duplicates could still exist under alternate titles.
- Discovery metadata is untrusted external text; titles/summaries/URLs were treated as data only and not followed as instructions.
- All candidate evidence is abstract-only; no code, reproduction, or full-text verification was performed. HTTP 200 or abstract presence is not evidence of correctness.
- Reported quantitative claims (e.g., Agensh 49% relative improvement, 1024-agent scaling) are unverified and must not be recorded as established results.
- catalog_json was truncated mid-entry (last visible: SoL-Pi, 2609.20519); dedup against the catalog is therefore partial and could miss overlaps.
- arxiv_id values in discovery (e.g., 2609.*) are future-dated relative to typical arXiv numbering; treat identifiers as provided by the source and verify before citing.
- Keyword-based matching produced several false positives (robotics, RAG, dialogue, judging), indicating the discovery query is noisy for this scope.

## Next actions
- Human-read PACT (2609.26355) and VHD-Play (2609.27321) in full; verify proofs/claims and, if code is available, inspect it before any archival decision.
- Human-read BPO (2609.15987) to decide whether it belongs in the RLVR foundations thread or is out of scope.
- Confirm RULER (2609.25270) and Taste-Bench (2609.25804) remain out of scope; do not archive.
- If any candidate is later archived, deduplicate against existing_source_ids (ppo, gae, deepseek-math, gigpo, swe-bench, webarena, tau-bench, agentic-survey) and record evidence level explicitly.
- Do not promote any candidate to published knowledge until independent verification (code, reproduction, or peer review) is available.
- Human-read 2609.26457 and 2609.24967 in full; check for code release and independent reproduction before any archive decision.
- Deduplicate 2609.26457 against existing RSI sources and 2609.24967 against emergence-world-adversarial-stress-testi; decide whether to merge notes or keep separate.
- For 2609.27891, decide whether evaluation-integrity/leakage papers belong in the KB; if yes, cross-link to swe-bench and multi-harness.
- Verify arXiv IDs and publication status independently; do not rely on discovery metadata.
- Keep all five as abstract-only; do not promote any to published knowledge until full-text review and, where applicable, code verification are complete.
- Human-read the two review candidates (2609.23989 ACLArena, 2609.25636 RoboFollow) in full before any KB inclusion decision.
- For the archived candidate (2609.22870), locate and check code/artifacts before promoting beyond archive.
- Verify arXiv IDs and titles against the official arXiv listing to guard against fabricated or mistyped metadata from the untrusted payload.
- Run a near-duplicate check of review candidates against existing sources (e.g., retireopd, mintrl, swe-bench, webarena) before adding notes.
- Do not publish any candidate as knowledge until full-text reading and, where applicable, reproduction are completed.
- Human-read EdgeGen (2609.24115) and SpeakerMem-R1 (2609.26780) full texts; verify benchmark versions, harness definitions, and reproducibility before any archive decision.
- Confirm arXiv IDs, titles, and author lists for the two review candidates against the canonical arXiv listing; do not rely on the discovery feed alone.
- Do not archive any candidate as published knowledge; if retained, store as review-status notes with explicit abstract-only evidence level.
- Re-run discovery with tighter scope filters (require RL training/policy-optimization or agent-environment-loop signals) to reduce off-scope false positives.
- Check for near-duplicate titles/IDs against existing_source_ids before the next audit cycle.
- Route 2609.26781 (Agensh) to human review; obtain full text and check benchmark setup, baselines, and statistical claims before any archival.
- Re-run discovery with tighter Agentic RL filters (RL training/credit assignment/harness) to reduce off-scope noise.
- Re-fetch the full catalog_json to complete dedup against existing_source_ids.
- Do not add any of these 5 candidates to published knowledge; keep only as review/archive candidates pending human reading.
- Verify arXiv identifiers and publication status independently before citing.
