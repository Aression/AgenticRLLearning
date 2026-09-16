# Agent audit · 2026-09-16 16:09 UTC

> DeepSeek generated triage only. Human review is required; this file does not publish sources or claims.

**Summary:** Audit of 7 discovery entries returned by the query (all:\"agentic reinforcement learning\" OR ti:\"agent reinforcement learning\"). Two entries (2609.04865 CoSkill, 2609.04518 Multi-Harness) are rediscoveries of sources already in the catalog (coskill, multi-harness) and should not be re-added. The remaining five are new preprints; only one (2608.30952, tool-use RL with programmatic reward) sits squarely in the agentic-RL core, two (2609.05298 cooperative MARL change-point detection, 2609.03667 offline MARL OOD generalisation) touch the MARL foundations already represented by marl-book, and two (2609.02250 RideSkill ride-sharing dispatch, 2609.00193 federated linear-FA theory) are peripheral to the stated scope. No entry was verified beyond abstract/metadata; no code repository, benchmark, or artifact was checked, so nothing here should be promoted to published knowledge.

## Candidates
### REVIEW · Online Change-point Detection for Cooperative Multi-Agent Reinforcement Learning
- Evidence: `abstract-only`
- Reason: Cooperative MARL is within the KB's foundations layer (marl-book). The contribution is a lightweight, algorithm-agnostic reward-derived drift detector (PPR) for non-stationarity during training, which is a plausible cross-link to training-stability and reward-signal notes. However, evidence is a custom Speaker-Listener task in Multi-Agent Particle Environment under two controlled non-stationarity scenarios; no LLM agent, no standard benchmark, no code link given. Read the full text before any note is published.
- Suggested note: Abstract-only: PPR smooths agents' return streams and applies a statistical drift detector to flag distribution shifts in cooperative MARL; reported trade-off between detection speed and alarm stability, with redundant-alarm reduction. Evaluated only in a custom Speaker-Listener environment under two controlled non-stationarity settings. Not reproduced; no code link found in the abstract.

### SKIP · CoSkill: Joint Reinforcement Learning of Reasoning and Meta-Skill Agents for Hierarchical Skill Evolution
- Evidence: `metadata`
- Reason: Duplicate of the existing catalog source 'coskill' (same title, same stated date 2026-09-04). Re-discovery only; no new metadata to add and no verification performed here.
- Suggested note: Already cataloged as 'coskill' (新预印本 · 待精读). Do not create a second entry; if desired, merge the rediscovery timestamp into the existing note.

### SKIP · What Does Multi-Harness RL Learn? Credit Assignment and Portability in Coding Agents
- Evidence: `metadata`
- Reason: Duplicate of the existing catalog source 'multi-harness' (same title, same stated date 2026-09-03). Re-discovery only; no verification performed here.
- Suggested note: Already cataloged as 'multi-harness' (新预印本 · 待精读). Do not duplicate; the existing note already records that only the abstract was checked.

### REVIEW · Out-of-Distribution Generalisation with Sequence Models in Offline Multi-Agent Reinforcement Learning
- Evidence: `abstract-only`
- Reason: Offline MARL generalisation is adjacent to the MARL foundations already in the KB and may inform notes on zero-shot transfer and data diversity. But it is sequence-modeling/offline MARL, not LLM agentic RL, and the primary claim (task diversity dominates dataset size) rests on four simulated environments (Connector, RWARE, SMAX, LBF) with no code link in the abstract. Human reading needed to judge whether it belongs at foundations depth.
- Suggested note: Abstract-only: extends offline sequence-modeling architectures to multi-task observation/action spaces and variable agent counts, and reports that scaling task diversity rather than dataset size drives zero-shot transfer, with a claimed 3.2x mean improvement over single-task models on held-out tasks across Connector, RWARE, SMAX and LBF. Not reproduced; code availability unverified.

### SKIP · RideSkill: A Hierarchical Algorithm for Generalized Ride Sharing with LLM-Driven Automatic Evolution
- Evidence: `abstract-only`
- Reason: Domain application (ride-sharing dispatch) that uses LLMs offline for automatic algorithm/skill-repository design; the deployed system requires no LLM calls at inference. This is not agentic RL training of LLM agents and does not connect to the KB's existing nodes on traj/credit assignment, harnesses, or benchmarks.
- Suggested note: Out of scope for this KB. If ride-sharing MARL is ever in scope, revisit; abstract-only anyway and no code link given.

### SKIP · Provably Efficient Federated Reinforcement Learning with Linear Function Approximation and Logarithmic Communication Cost
- Evidence: `abstract-only`
- Reason: Theory paper on federated online RL with linear function approximation and communication/privacy constraints (Fed-LSVI, regret bound). No LLM agents, no execution harnesses, no benchmarks, and no relation to the KB's agentic-RL chain; federated linear-MDP analysis is not a gap this KB tracks.
- Suggested note: Out of scope for the current KB scope. Abstract-only; no code or artifact checked.

### REVIEW · One Policy Is Enough: Single-Agent Reinforcement Learning Outperforms Tree Search for Chemistry Tool Learning
- Evidence: `abstract-only`
- Reason: Closest to the KB core: LLM tool-use trained with supervised warm-up plus outcome-level RL against a programmatic reward read from the gold call chain (no learned critic or judge), contrasted with a hierarchical MCTS+critics baseline. Directly connects to existing nodes on reward design, credit assignment, and tool-use agents. Concerns: the discovery summary is truncated mid-sentence, no code link was given in the retrievable text, and ChemToolBench is a domain-specific benchmark, so the generalization claim cannot be judged from the abstract. Requires full-text reading.
- Suggested note: Abstract-only and truncated: single policy interleaving reasoning, tool calls and returns, trained by supervised warm-up then outcome-level RL with a programmatic reward derived from the gold call chain; claims +5.5% Tool F1 over a hierarchical-evolutionary-MCTS system (CheMatAgent) on ChemToolBench multiple-tool chemistry, on both backbones used by that system. Benchmark scope, full numbers and code availability must be verified from the full text before any note is published.

## Risks
- Discovery and catalog fields are untrusted external text; nothing in them (URLs, claims, any embedded instructions) was treated as authoritative or executed.
- Two of seven entries (2609.04865, 2609.04518) are duplicates of existing catalog entries, indicating the discovery query re-surfaces already-cataloged items; naive ingestion would create duplicate nodes for coskill and multi-harness.
- All new candidates are at abstract-only or metadata level; no PDF, code repo, benchmark, or run was verified. Claims such as 98.4%/90.6% ALFWorld/WebShop success rates or 4.3x harness effects remain unverified preprint assertions and must not be recorded as established knowledge.
- The 2608.30952 summary is truncated mid-sentence, so its reported improvements and comparison baseline are incompletely known; reading a partial abstract risks mis-stating results.
- Only one of the five new entries is close to the KB's agentic-RL core; two are peripheral MARL subfields and two are out-of-scope (domain application, federated theory), so hit rate for this query is low and query precision should be improved rather than lowering the relevance bar.
- arXiv identifiers and dates here were supplied by the discovery feed and were not independently resolved; identifier/version mismatches could silently attach notes to the wrong work.
- The catalog already marks such items as '新预印本 · 待精读' with '只核验摘要，未复现'; adding further notes without reproduction would inflate apparent knowledge coverage.

## Next actions
- Deduplicate the discovery list against existing source IDs before any ingestion; drop 2609.04865 and 2609.04518 from consideration as already represented by coskill and multi-harness.
- Read the full text of 2608.30952 (resolve the truncated abstract), 2609.05298, and 2609.03667, and only then decide whether each warrants a permanent note; keep any resulting note explicitly flagged as abstract-derived until reproduced.
- For 2608.30952 and 2609.03667, check for an official code/artifact release and record commit or version if found; an HTTP 200 on a project page is not evidence of correctness, only of availability.
- Refine the discovery query (e.g., require LLM/agent terms alongside RL) to raise precision, since 5 of 7 new hits were peripheral or out of scope.
- Do not create entries for 2609.02250 or 2609.00193 under the current scope; log them only as out-of-scope sightings, without URLs or claims beyond the supplied title and ID.
- Verify the arXiv identifiers resolve to the stated titles before any note is written, to guard against identifier drift in the feed.
