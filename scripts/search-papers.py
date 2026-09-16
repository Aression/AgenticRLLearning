"""Fetch HuggingFace Daily Papers and keep the ones relevant to the knowledge base.

HuggingFace curates a daily list at https://huggingface.co/api/daily_papers.
This replaces the hand-written arXiv query: we pull that list, grep each paper's
title and abstract against keywords derived from this knowledge base, and write
research/discovery.json for the DeepSeek audit. On network failure we keep the
previous discovery file instead of failing the maintenance pipeline.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "discovery.json"
CONFIG = ROOT / "harness.config.json"

API_URL = "https://huggingface.co/api/daily_papers"
HEADERS = {
    "User-Agent": "AgenticRLAtlas/0.1 (personal research; HuggingFace daily papers)",
    "Accept": "application/json",
}
ATTEMPTS = 3
TIMEOUT_SECONDS = 60
DEFAULT_MAX_RESULTS = 25

# Specific phrases and acronyms: one hit is enough to consider a paper relevant.
# Keep this list aligned with the topics covered by content/ and data/sources.json.
STRONG_KEYWORDS = [
    # Agentic RL / LLM post-training
    "agentic reinforcement learning",
    "agentic rl",
    "reinforcement learning from human feedback",
    "reinforcement learning from ai feedback",
    "rlhf",
    "rlaif",
    "rlvr",
    "group relative policy optimization",
    "group-relative policy optimization",
    "grpo",
    "gigpo",
    "dapo",
    "proximal policy optimization",
    "direct preference optimization",
    "preference optimization",
    "generalized advantage estimation",
    "advantage estimation",
    "credit assignment",
    "reward model",
    "reward hacking",
    "process reward",
    "outcome reward",
    "verifiable reward",
    "policy optimization",
    "policy gradient",
    "actor-critic",
    "actor critic",
    "markov decision process",
    "reward shaping",
    "sparse reward",
    "experience distillation",
    # Agents
    "llm agent",
    "language model agent",
    "language agent",
    "agent training",
    "training agents",
    "multi-agent",
    "multiagent",
    "tool use",
    "tool-use",
    "tool calling",
    "function calling",
    "tool agent",
    "computer use",
    "computer-use",
    "web agent",
    "gui agent",
    "coding agent",
    "code agent",
    "software engineering agent",
    "swe-bench",
    "swe agent",
    "swe-agent",
    "webarena",
    "tau-bench",
    "gaia benchmark",
    "long-horizon",
    "long horizon",
    "multi-turn",
    "multi turn",
    "chain-of-thought",
    "chain of thought",
    "test-time",
    "test time scaling",
    "test-time compute",
    "constitutional ai",
    "prompt injection",
    "agent lightning",
    "reasoning model",
    "self-improvement",
]

# Broader terms: require at least two distinct hits so a single generic word
# such as "memory" or "planning" does not pull in unrelated papers.
BROAD_KEYWORDS = [
    "reinforcement learning",
    "agent",
    "agentic",
    "reward",
    "policy",
    "reasoning",
    "alignment",
    "planning",
    "memory",
    "exploration",
    "tool",
    "trajectory",
    "rollout",
    "sandbox",
    "benchmark",
    "verifier",
    "curriculum",
    "hierarchical",
    "generalization",
    "distillation",
    "evaluation",
]


def compile_keyword(keyword: str) -> re.Pattern[str]:
    """Match whole tokens for single words (so 'ppo' does not hit 'support')."""
    escaped = re.escape(keyword)
    if " " in keyword or "-" in keyword:
        return re.compile(escaped, re.IGNORECASE)
    return re.compile(rf"(?<![A-Za-z0-9]){escaped}s?(?![A-Za-z0-9])", re.IGNORECASE)


def load_max_results() -> int:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        value = int(config.get("refresh", {}).get("maxDiscoveryResults", DEFAULT_MAX_RESULTS))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_MAX_RESULTS
    return value if value > 0 else DEFAULT_MAX_RESULTS


def fetch_daily_papers() -> list[dict]:
    last_error: Exception | None = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            request = urllib.request.Request(API_URL, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                data = json.loads(response.read().decode("utf-8"))
            if isinstance(data, dict):
                data = data.get("dailyPapers") or data.get("papers") or data.get("data")
            if not isinstance(data, list) or not data:
                raise ValueError("HuggingFace returned no daily papers")
            return data
        except Exception as error:  # noqa: BLE001 - network/parse errors are expected and retried
            last_error = error
            if attempt < ATTEMPTS:
                backoff = 5 * attempt
                print(
                    f"search-papers: attempt {attempt}/{ATTEMPTS} failed ({error}); "
                    f"retrying in {backoff}s",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(backoff)
    if OUTPUT.exists():
        print(
            f"search-papers: WARNING: HuggingFace refresh failed after {ATTEMPTS} attempts "
            f"({last_error}); keeping existing {OUTPUT.relative_to(ROOT)}",
            file=sys.stderr,
            flush=True,
        )
    else:
        print(
            f"search-papers: WARNING: HuggingFace refresh failed after {ATTEMPTS} attempts "
            f"({last_error}); no previous discovery file to keep",
            file=sys.stderr,
            flush=True,
        )
    return []


def normalize(record: dict) -> dict | None:
    paper = record.get("paper") if isinstance(record.get("paper"), dict) else record
    paper_id = str(paper.get("id") or paper.get("paperId") or record.get("id") or "").strip()
    paper_id = re.sub(r"^arxiv:", "", paper_id, flags=re.IGNORECASE)
    title = str(paper.get("title") or record.get("title") or "").strip()
    if not paper_id or not title:
        return None
    summary = str(paper.get("summary") or paper.get("abstract") or record.get("summary") or "").strip()
    authors = paper.get("authors") or record.get("authors") or []
    author_names = [
        str(author.get("name"))
        for author in authors
        if isinstance(author, dict) and author.get("name")
    ]
    try:
        upvotes = int(paper.get("upvotes") or record.get("upvotes") or 0)
    except (TypeError, ValueError):
        upvotes = 0
    published = str(
        paper.get("publishedAt") or record.get("publishedAt") or record.get("date") or ""
    ).strip()
    return {
        "id": paper_id,
        "title": title,
        "summary": summary,
        "published": published,
        "url": f"https://huggingface.co/papers/{paper_id}",
        "arxiv_url": f"https://arxiv.org/abs/{paper_id}",
        "upvotes": upvotes,
        "authors": author_names[:8],
    }


def match_keywords(
    text: str,
    strong: list[tuple[str, re.Pattern[str]]],
    broad: list[tuple[str, re.Pattern[str]]],
) -> tuple[list[str], int]:
    matched: list[str] = []
    strong_hits = 0
    broad_hits = 0
    for keyword, pattern in strong:
        if pattern.search(text):
            matched.append(keyword)
            strong_hits += 1
    for keyword, pattern in broad:
        if pattern.search(text):
            matched.append(keyword)
            broad_hits += 1
    if strong_hits == 0 and broad_hits < 2:
        return [], 0
    return matched, strong_hits * 2 + broad_hits


def main() -> int:
    records = fetch_daily_papers()
    if not records:
        # Exit 0 so a transient HuggingFace outage does not fail maintenance.
        return 0

    strong = [(keyword, compile_keyword(keyword)) for keyword in STRONG_KEYWORDS]
    broad = [(keyword, compile_keyword(keyword)) for keyword in BROAD_KEYWORDS]
    max_results = load_max_results()

    entries: list[dict] = []
    seen: set[str] = set()
    for record in records:
        entry = normalize(record)
        if not entry or entry["id"] in seen:
            continue
        seen.add(entry["id"])
        matched, score = match_keywords(f"{entry['title']}\n{entry['summary']}", strong, broad)
        if not matched:
            continue
        entry["matched_keywords"] = matched
        entry["relevance_score"] = score
        entries.append(entry)

    entries.sort(key=lambda item: (item["relevance_score"], item["upvotes"]), reverse=True)
    entries = entries[:max_results]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "source": "huggingface-daily-papers",
                "query": "daily papers grepped against knowledge-base keywords",
                "searchedAt": datetime.now(timezone.utc).isoformat(),
                "considered": len(seen),
                "selected": len(entries),
                "entries": entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "source": "huggingface-daily-papers",
                "considered": len(seen),
                "selected": len(entries),
                "output": str(OUTPUT.relative_to(ROOT)) if OUTPUT.is_relative_to(ROOT) else str(OUTPUT),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    for entry in entries:
        print(json.dumps(entry, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
