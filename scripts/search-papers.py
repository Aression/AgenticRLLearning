"""Query arXiv Atom API and record discovery separately from curated sources.

The arXiv API is frequently slow or returns transient errors. This script
retries with backoff, and on persistent failure keeps the previous
research/discovery.json instead of failing the whole maintenance pipeline.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "discovery.json"

QUERY = '(all:"agentic reinforcement learning" OR ti:"agent reinforcement learning")'
URL = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
    {
        "search_query": QUERY,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": 25,
    }
)
HEADERS = {"User-Agent": "AgenticRLAtlas/0.1 (personal research; arXiv discovery)"}
ATTEMPTS = 3
TIMEOUT_SECONDS = 60


def fetch() -> bytes:
    request = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def parse(raw: bytes) -> list[dict[str, str]]:
    feed = ET.fromstring(raw)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    return [
        {
            key: " ".join(entry.findtext("a:" + key, default="", namespaces=ns).split())
            for key in ("id", "title", "published", "updated", "summary")
        }
        for entry in feed.findall("a:entry", ns)
    ]


def discover() -> list[dict[str, str]]:
    last_error: Exception | None = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            entries = parse(fetch())
            if not entries:
                raise ValueError("arXiv returned no entries")
            return entries
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
            f"search-papers: WARNING: arXiv refresh failed after {ATTEMPTS} attempts "
            f"({last_error}); keeping existing {OUTPUT.relative_to(ROOT)}",
            file=sys.stderr,
            flush=True,
        )
    else:
        print(
            f"search-papers: WARNING: arXiv refresh failed after {ATTEMPTS} attempts "
            f"({last_error}); no previous discovery file to keep",
            file=sys.stderr,
            flush=True,
        )
    return []


def main() -> int:
    entries = discover()
    if not entries:
        # Exit 0 so a transient arXiv outage does not fail the maintenance job.
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "query": QUERY,
                "searchedAt": datetime.now(timezone.utc).isoformat(),
                "entries": entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    for entry in entries:
        print(json.dumps(entry, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
