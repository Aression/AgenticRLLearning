"""Query arXiv Atom API and record discovery separately from curated sources."""
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

query = '(all:"agentic reinforcement learning" OR ti:"agent reinforcement learning")'
url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": query, "sortBy": "submittedDate", "sortOrder": "descending", "max_results": 25})
with urllib.request.urlopen(url, timeout=50) as response:
    feed = ET.fromstring(response.read())
ns = {"a": "http://www.w3.org/2005/Atom"}
entries = [{key: " ".join(entry.findtext("a:" + key, default="", namespaces=ns).split()) for key in ("id", "title", "published", "updated", "summary")} for entry in feed.findall("a:entry", ns)]
Path("research/discovery.json").write_text(json.dumps({"query": query, "searchedAt": datetime.now(timezone.utc).isoformat(), "entries": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for entry in entries:
    print(json.dumps(entry, ensure_ascii=True))
