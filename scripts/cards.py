#!/usr/bin/env python3
"""Turn selected daily papers into *deep* knowledge dossiers via DeepSeek + the harness.

Architecture
------------
The knowledge base has two axes: ``kind`` (what a note is) and ``depth`` (how much
reading investment it carries). See ``scripts/content_model.py`` for the contracts.
This script produces ``kind=paper, depth=deep`` dossiers that must satisfy the
"paper/deep" contract: located claims, mechanism, experimental setup, results,
an evidence-strength assessment, falsification conditions, explicit relations to
existing notes, a verification plan, a notation table and a self-test.

Generation is multi-pass so depth does not depend on one large completion:

  1. ``plan_evidence``  — read the full text and extract an evidence sheet
     (claims with locations, method, experiments, results, ablations, limits,
     relations, notation) as JSON.
  2. ``draft_sections`` — write the required sections in small groups, each group
     grounded in the evidence sheet plus the most relevant full-text slices.
  3. ``grounding``      — deterministic checks: contract compliance, numbers must
     appear in the source excerpt, no new URLs. Violations trigger one repair pass.

Two entry points exist:

  * ``run``    — card newly triaged papers from the audit queue.
  * ``deepen`` — re-read papers that already have a thin ``overview`` LLM card and
    rewrite them into deep dossiers in place (this is how the existing backlog is
    converted).

Nothing is published directly: cards are written with review status
"LLM 全文精读草稿 · 待人工复核" and land in the audit pull request, where a human
reviews them before merge. Full text is never stored in the repository.

Usage:
    python scripts/cards.py run [--limit N] [--paper ARXIV_ID]
    python scripts/cards.py deepen [--limit N] [--paper NOTE_OR_ARXIV_ID] [--force]
    python scripts/cards.py status
    python scripts/cards.py check
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from llm_gate import require_llm_enabled  # noqa: E402
from content_model import (  # noqa: E402
    CLAIM_STATUSES,
    PAPER_DEEP,
    check_structure,
    parse_claims,
    section_sizes,
    ungrounded_numbers,
)

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
SOURCES = ROOT / "data" / "sources.json"
CONFIG = ROOT / "harness.config.json"
RADAR = ROOT / "data" / "generated" / "radar.json"
CARDS_DIR = ROOT / "research" / "cards"
AUDITS_DIR = ROOT / "research" / "agent-audits"
MODEL = "deepseek-v4-flash"
REVIEW_STATUS = "LLM 全文精读草稿 · 待人工复核"
STAGES = {"FOUNDATION", "SYSTEMS", "FRONTIER"}
TRACKS = ["概念与基础", "训练算法", "Agent 系统", "评估与安全", "前沿专题", "实验与维护"]
HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
BLOCK_TAGS = ("p", "li", "dd", "dt", "figcaption", "caption", "blockquote")
SKIP_TAGS = ("script", "style", "svg", "nav", "footer", "header")
KEEP_SECTION = re.compile(r"abstract|introduction|background|related|method|approach|model|framework|training|objective|experiment|result|evaluation|benchmark|analysis|ablation|discussion|limitation|conclusion|appendix", re.I)

# Section keyword routing used to give each drafting call the relevant slices.
SECTION_SOURCES = {
    "问题与语境": ("abstract", "introduction", "background", "related"),
    "核心主张": ("abstract", "introduction", "conclusion", "result"),
    "机制与方法": ("method", "approach", "model", "framework", "training", "objective"),
    "实验设置": ("experiment", "evaluation", "benchmark", "training", "method"),
    "证据与结果": ("experiment", "result", "evaluation", "benchmark", "analysis", "ablation"),
    "证据强度评估": ("analysis", "ablation", "limitation", "experiment", "result"),
    "边界与反例": ("limitation", "discussion", "analysis", "conclusion"),
    "与知识库的关系": ("abstract", "introduction", "conclusion"),
    "复现与验证计划": ("experiment", "evaluation", "method", "appendix"),
    "术语与记号": ("method", "approach", "model", "background"),
    "自测": ("abstract", "method", "experiment", "limitation"),
}
DEFAULT_SECTION_SOURCES = ("abstract", "introduction", "method", "result", "conclusion")

HEADERS = {"User-Agent": "AgenticRLAtlas/0.2 (personal research; deep-card draft)", "Accept": "text/html,application/xhtml+xml"}
SYSTEM = """你是 Agentic RL 知识库的论文精读助手。你的产出会被写进一个长期维护的深度知识档案，读者是具备 RL 与 LLM 基础的研究者。

硬性规则：
- 只使用用户提供的论文全文摘录，绝不编造事实、数字、基准结果、作者、机构或 URL。
- 严格区分「作者主张」与「已有共识」；没有摘录支撑的判断必须标注为不确定。
- 保留关键数字的原文写法，不四舍五入到摘录中没有的精度，不做跨论文外推。
- 结论强度必须匹配证据强度：摘要级、单项实验、单一模型上的结论都要说明边界。
- 数学公式使用 $...$ 或 $$...$$，符号必须与论文一致。
- 用简体中文写作，术语首次出现时给出英文原词。

只返回 JSON，不要输出解释性前后缀。"""


class CardError(Exception):
    pass


# ---------------------------------------------------------------- full text

class PaperParser(HTMLParser):
    """Extract headings, paragraphs, list items, table rows and math from arXiv HTML.

    Tables hold most of the numbers that make a deep card possible, and LaTeXML
    puts the LaTeX source of equations in the ``alttext`` attribute of ``<math>``.
    Both are captured; images, scripts and navigation are dropped.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.sections: list[dict[str, Any]] = []
        self._loose: list[str] = []
        self._current: dict[str, Any] | None = None
        self._mode: str | None = None
        self._heading_level = 0
        self._buf: list[str] = []
        self._skip = 0
        self._table_depth = 0
        self._row: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attributes = {key: value for key, value in attrs if value is not None}
        if tag == "math":
            alt = attributes.get("alttext")
            if alt:
                self._buf.append(f" ${alt.strip()}$ ")
            self._skip += 1
            return
        if tag in SKIP_TAGS:
            self._skip += 1
            return
        if self._skip:
            return
        if tag == "table":
            self._flush()
            self._table_depth += 1
            return
        if self._table_depth:
            if tag == "tr":
                self._flush()
                self._row = []
            elif tag in ("td", "th"):
                self._flush()
                self._mode = "cell"
            return
        if tag == "title":
            self._flush()
            self._mode, self._buf = "title", []
        elif tag in HEADINGS:
            self._flush()
            self._mode, self._buf = "heading", []
            self._heading_level = int(tag[1])
        elif tag in BLOCK_TAGS:
            self._flush()
            self._mode, self._buf = "block", []

    def handle_endtag(self, tag: str) -> None:
        if tag == "math":
            self._skip = max(0, self._skip - 1)
            return
        if tag in SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag == "table":
            self._flush()
            self._table_depth = max(0, self._table_depth - 1)
            return
        if self._table_depth:
            if tag in ("td", "th"):
                self._flush()
            elif tag == "tr":
                if self._row:
                    self._append_line(" | ".join(cell for cell in self._row if cell))
                self._row = None
            return
        if tag == "title" or tag in HEADINGS or tag in BLOCK_TAGS:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip or self._mode is None:
            return
        self._buf.append(data)

    def _line(self) -> str:
        text = " ".join("".join(self._buf).split())
        self._buf = []
        return text

    def _append_line(self, text: str) -> None:
        if not text:
            return
        if self._current is None:
            self._loose.append(text)
        elif self._current["text"]:
            self._current["text"] += "\n" + text
        else:
            self._current["text"] = text

    def _flush(self) -> None:
        mode, self._mode = self._mode, None
        text = self._line()
        if not text:
            return
        if mode is None:
            return
        if mode == "title":
            self.title = text
        elif mode == "heading":
            if self._heading_level == 1:
                if not self.title:
                    self.title = text
                self._current = None
            else:
                self._current = {"title": text, "level": self._heading_level, "text": ""}
                self.sections.append(self._current)
        elif mode == "cell":
            if self._row is not None:
                self._row.append(text)
        else:
            self._append_line(text)

    def result(self) -> dict[str, Any]:
        sections = self.sections
        if self._loose and not any(section["title"].lower().startswith("abstract") for section in sections):
            sections.insert(0, {"title": "Abstract", "level": 2, "text": "\n".join(self._loose)})
        return {"title": self.title, "sections": sections}


def http_get(url: str, timeout: int = 90, retries: int = 2) -> bytes:
    last: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            last = exc
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
    raise last if last else CardError(f"cannot fetch {url}")


def select_sections(parsed: dict[str, Any], include_appendix: bool = True) -> list[dict[str, str]]:
    """Keep readable sections; reference lists and acknowledgements waste the budget."""
    dropped = re.compile(r"^(references|bibliography|acknowledg|author contributions|supplementary material)", re.I)
    kept = []
    for section in parsed["sections"]:
        if (section.get("level") or 9) > 3:
            continue
        title = str(section.get("title") or "Untitled")
        text = str(section.get("text") or "").strip()
        if not text or dropped.search(title.strip()):
            continue
        if not include_appendix and title.lower().startswith("appendix"):
            continue
        kept.append({"title": title, "text": text})
    if not kept:
        kept = [{"title": str(section.get("title") or "Untitled"), "text": str(section.get("text") or "")} for section in parsed["sections"][:8]]
    return kept


def allocate_budget(sections: list[dict[str, str]], max_chars: int, per_section: int) -> list[dict[str, str]]:
    """Give each kept section a slice, prioritising the sections that carry evidence."""
    ranked = sorted(range(len(sections)), key=lambda index: (0 if KEEP_SECTION.search(sections[index]["title"]) else 1, index))
    budget: dict[int, str] = {}
    total = 0
    for index in ranked:
        cap = min(per_section, max_chars - total)
        if cap < 200:
            break
        budget[index] = sections[index]["text"][:cap]
        total += len(budget[index])
    # Return in the paper's own order so the excerpt reads coherently.
    return [{"title": sections[index]["title"], "text": budget[index]} for index in sorted(budget)]


def fetch_fulltext(arxiv_id: str, max_chars: int, per_section: int) -> dict[str, Any] | None:
    """Fetch arXiv HTML (or ar5iv) and return budgeted, section-labelled text."""
    for url in (f"https://arxiv.org/html/{arxiv_id}", f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"):
        try:
            raw = http_get(url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            continue
        if len(raw) < 20000:
            continue
        parser = PaperParser()
        parser.feed(raw.decode("utf-8", errors="replace"))
        parsed = parser.result()
        sections = allocate_budget(select_sections(parsed), max_chars, per_section)
        excerpt = "\n\n".join(f"## {section['title']}\n{section['text']}" for section in sections)
        if len(excerpt) < 4000:
            continue
        return {"url": url, "title": parsed["title"], "sections": sections, "excerpt": excerpt, "chars": len(excerpt)}
    return None


def slice_for_sections(full: dict[str, Any], names: tuple[str, ...], budget: int) -> str:
    """Concatenate the full-text sections most relevant to the requested sections."""
    keywords: list[str] = []
    for name in names:
        keywords.extend(SECTION_SOURCES.get(name, DEFAULT_SECTION_SOURCES))
    keywords = list(dict.fromkeys(keywords))
    scored = []
    for index, section in enumerate(full["sections"]):
        title = section["title"].lower()
        score = sum(1 for keyword in keywords if keyword in title)
        if index == 0:
            score += 1
        scored.append((score, index, section))
    scored.sort(key=lambda item: (-item[0], item[1]))
    parts, total = [], 0
    for _, _, section in scored:
        if total >= budget:
            break
        block = f"## {section['title']}\n{section['text'][: budget - total]}"
        parts.append(block)
        total += len(block)
    return "\n\n".join(parts)


# ---------------------------------------------------------------- LLM

def repair_json_escapes(raw: str) -> str:
    r"""Make model output parseable when it embeds LaTeX in JSON strings.

    ``\mathcal``/``\rho``/``\theta`` look like JSON escapes but are not, and the
    short ones are the dangerous cases: ``\rho`` parses as a carriage return
    followed by "ho", and ``\underline`` fails outright. LaTeX commands are
    escaped first (backslash followed by two or more letters), then lone invalid
    escapes, then truncated ``\u`` sequences.
    """
    raw = re.sub(r"(?<!\\)\\u(?![0-9a-fA-F]{4})", r"\\\\u", raw)
    raw = re.sub(r"(?<!\\)\\(?=[A-Za-z]{2,})", r"\\\\", raw)
    return re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r"\\\\", raw)


def chat_json(api_key: str, system: str, user: str, *, max_tokens: int, temperature: float = 0.2, label: str = "call") -> dict[str, Any]:
    body = json.dumps({
        "model": MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }).encode()
    request = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": "AgenticRLAtlas-cards/2.0"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise CardError(f"{label}: DeepSeek API HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise CardError(f"{label}: DeepSeek API network error: {exc}") from None
    except json.JSONDecodeError:
        raise CardError(f"{label}: DeepSeek API returned a non-JSON response") from None
    try:
        choice = result["choices"][0]
        text = (choice["message"].get("content") or "").strip()
        finish_reason = choice.get("finish_reason")
    except (KeyError, IndexError, TypeError):
        raise CardError(f"{label}: DeepSeek API response missing choices.message.content") from None
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise CardError(f"{label}: DeepSeek returned no JSON object (finish_reason={finish_reason}, chars={len(text)})")
    candidate = text[start:end + 1]
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        # LaTeX in the model's prose is not legal JSON; repair and retry once.
        try:
            parsed = json.loads(repair_json_escapes(candidate))
        except json.JSONDecodeError:
            raise CardError(f"{label}: DeepSeek returned invalid JSON ({exc.msg}; finish_reason={finish_reason}, content_chars={len(text)})") from None
    if not isinstance(parsed, dict):
        raise CardError(f"{label}: DeepSeek returned a JSON value instead of an object")
    return parsed


def chat_text(api_key: str, system: str, user: str, *, max_tokens: int, temperature: float = 0.2, label: str = "call") -> tuple[str, str | None]:
    """Plain-text completion, used for Markdown drafting.

    JSON is a poor container for LaTeX-heavy Markdown: backslash commands are not
    legal JSON escapes, so section drafting uses a sentinel-delimited format
    instead. Returns the text plus the provider's finish_reason.
    """
    body = json.dumps({
        "model": MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "thinking": {"type": "disabled"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }).encode()
    request = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": "AgenticRLAtlas-cards/2.0"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise CardError(f"{label}: DeepSeek API HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise CardError(f"{label}: DeepSeek API network error: {exc}") from None
    except json.JSONDecodeError:
        raise CardError(f"{label}: DeepSeek API returned a non-JSON envelope") from None
    try:
        choice = result["choices"][0]
        text = (choice["message"].get("content") or "").strip()
        finish_reason = choice.get("finish_reason")
    except (KeyError, IndexError, TypeError):
        raise CardError(f"{label}: DeepSeek API response missing choices.message.content") from None
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if not text:
        raise CardError(f"{label}: DeepSeek returned empty content (finish_reason={finish_reason})")
    return text, finish_reason


TRUNCATION_HINTS = ("finish_reason=length", "Unterminated string", "invalid JSON", "no JSON object")
CONCISE_NUDGE = (
    "\n\n注意：上一次输出因超出长度预算而被截断，整段 JSON 作废。请大幅精简后重新输出：\n"
    "- 数组最多 3 项，每项不超过 40 字；\n"
    "- 不要复述摘录原文，不要解释；\n"
    "- 必须输出完整、合法、可解析的 JSON。"
)


def chat_json_resilient(api_key: str, system: str, user: str, *, max_tokens: int, temperature: float, label: str, attempts: int = 3) -> dict[str, Any]:
    """Retry a truncated answer with a stricter, shorter-output instruction.

    The model can overrun the output budget on long evidence sheets; a smaller ask
    recovers the call without losing the card, while non-truncation errors (HTTP,
    network) are surfaced immediately.
    """
    last: CardError | None = None
    for attempt in range(attempts):
        prompt = user if attempt == 0 else user + CONCISE_NUDGE
        try:
            return chat_json(api_key, system, prompt, max_tokens=max_tokens, temperature=temperature, label=f"{label}#{attempt + 1}")
        except CardError as exc:
            last = exc
            print(f"cards: {exc}", file=sys.stderr, flush=True)
            if not any(hint in str(exc) for hint in TRUNCATION_HINTS):
                raise
    raise last if last else CardError(f"{label}: no attempt succeeded")


# ---------------------------------------------------------------- helpers

def slugify(value: str, limit: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    if len(slug) > limit:
        # Trim at a word boundary so ids do not end mid-word.
        slug = slug[:limit].rsplit("-", 1)[0] if "-" in slug[:limit] else slug[:limit]
    return slug.strip("-") or "card"


def unique_slug(base: str, taken: set[str]) -> str:
    candidate = slugify(base)
    if candidate not in taken:
        return candidate
    index = 2
    while f"{candidate}-{index}" in taken:
        index += 1
    return f"{candidate}-{index}"


WEAK_SLUG_LENGTH = 8


def best_slug(candidates: list[str], taken: set[str]) -> str:
    """Pick a descriptive note id.

    Chinese titles slugify to the fallback "card" (or to a stray acronym like
    "moe") because ``slugify`` keeps only ASCII. Prefer the English paper title in
    that case so ids stay meaningful and stable in the knowledge graph.
    """
    for value in candidates:
        candidate = slugify(value)
        if candidate != "card" and len(candidate) >= WEAK_SLUG_LENGTH:
            return unique_slug(value, taken)
    fallback = next((value for value in candidates if value), "")
    return unique_slug(fallback, taken)


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    block = text.split("\n---\n", 1)[0]
    data: dict[str, Any] = {}
    for line in block.splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key.strip()] = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
        elif value.isdigit():
            data[key.strip()] = int(value)
        else:
            data[key.strip()] = value.strip("'\"")
    return data


def clean_list(value: Any, limit: int = 8) -> list[str]:
    if not isinstance(value, list):
        return []
    items = []
    for item in value:
        text = str(item).replace(",", "，").replace("|", "／").replace("\n", " ").strip()
        if text and text not in items:
            items.append(text)
    return items[:limit]


def clean_body(value: Any) -> str:
    body = str(value or "").replace("\r\n", "\n")
    body = re.sub(r"\n-{3,}\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body


def sanitize_scalar(value: Any) -> str:
    """Keep model output from corrupting the flat frontmatter parser.

    Frontmatter is line-based (``key: value``), so stray brackets would turn a
    scalar into a list and newlines would break the block entirely.
    """
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text.replace("[", "（").replace("]", "）").replace("#", "＃")


def load_config() -> dict[str, Any]:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        config = {}
    card = config.get("cardGeneration", {}) if isinstance(config, dict) else {}
    return {
        "limit": int(card.get("maxCards", 2)),
        "decisions": card.get("decisions", ["review"]),
        "max_chars": int(card.get("maxFullTextChars", 160000)),
        "per_section_chars": int(card.get("maxSectionChars", 24000)),
        "section_source_budget": int(card.get("sectionSourceBudget", 30000)),
        "sections_per_call": int(card.get("sectionsPerCall", 3)),
        "planning_tokens": int(card.get("planningMaxTokens", 8000)),
        "plan_attempts": int(card.get("planningAttempts", 3)),
        "planning_chars": int(card.get("planningMaxChars", 80000)),
        "section_tokens": int(card.get("sectionMaxTokens", 4000)),
        "repair_attempts": int(card.get("repairAttempts", 1)),
        "max_ungrounded_numbers": int(card.get("maxUngroundedNumbers", 3)),
        "review_status": card.get("reviewStatus", REVIEW_STATUS),
        "target_depth": card.get("targetDepth", "deep"),
    }


def existing_state() -> dict[str, Any]:
    notes, ids, orders, paper_ids, titles = [], set(), [], set(), set()
    records = []
    for path in sorted(CONTENT.glob("*.md")):
        data = parse_frontmatter(path)
        if not data.get("id"):
            continue
        data["_path"] = path
        records.append(data)
        notes.append(data)
        ids.add(str(data["id"]))
        titles.add(str(data.get("title", "")).strip().lower())
        if isinstance(data.get("order"), int):
            orders.append(data["order"])
        if data.get("paper_id"):
            paper_ids.add(str(data["paper_id"]))
    catalog = json.loads(SOURCES.read_text(encoding="utf-8")) if SOURCES.exists() else []
    return {"notes": notes, "records": records, "ids": ids, "titles": titles, "paper_ids": paper_ids, "max_order": max(orders, default=0), "catalog": catalog, "catalog_ids": {str(item.get("id")) for item in catalog}}


# ---------------------------------------------------------------- candidate selection

def audit_queue(radar: dict[str, Any]) -> list[dict[str, Any]]:
    """Keep historical reviews until carded; the latest decision wins per paper."""
    queue: dict[str, dict[str, Any]] = {}
    for path in sorted(AUDITS_DIR.glob("audit-*.json")):
        audit = json.loads(path.read_text(encoding="utf-8"))
        metadata = {str(entry.get("id")): entry for entry in audit.get("discovery_entries", []) if isinstance(entry, dict)}
        for candidate in audit.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            paper_id = str(candidate.get("arxiv_id") or "").strip()
            if not re.fullmatch(r"\d{4}\.\d{4,5}", paper_id):
                continue
            entry = metadata.get(paper_id, {})
            previous = queue.get(paper_id, {})
            queue[paper_id] = {
                **previous,
                "id": paper_id,
                "title": entry.get("title") or candidate.get("title") or previous.get("title", ""),
                "published": entry.get("published") or previous.get("published", ""),
                "authors": entry.get("authors") or previous.get("authors", []),
                "arxivUrl": entry.get("arxiv_url") or previous.get("arxivUrl") or f"https://arxiv.org/abs/{paper_id}",
                "relevanceScore": entry.get("relevance_score") or previous.get("relevanceScore", 0),
                "upvotes": entry.get("upvotes") or previous.get("upvotes", 0),
                "decision": candidate.get("decision"),
                "reason": candidate.get("reason", ""),
                "suggestedNote": candidate.get("suggested_note", ""),
            }
    for paper in radar.get("papers", []):
        if isinstance(paper, dict) and paper.get("id"):
            queue[str(paper["id"])] = {**queue.get(str(paper["id"]), {}), **paper}
    return list(queue.values())


def select_candidates(radar: dict[str, Any], state: dict[str, Any], limit: int, decisions: list[str], only: str | None) -> list[dict[str, Any]]:
    known_urls = {str(item.get("url")) for item in state["catalog"]}
    picked = []
    for paper in audit_queue(radar):
        paper_id = str(paper.get("id") or "").strip()
        if only and paper_id != only:
            continue
        if not paper_id or paper_id in state["paper_ids"]:
            continue
        if paper.get("decision") not in decisions:
            continue
        if str(paper.get("arxivUrl") or "") in known_urls or str(paper.get("title", "")).strip().lower() in state["titles"]:
            continue
        picked.append(paper)
    # Older reviews go first so a rotating daily radar cannot starve the backlog.
    return picked[: max(limit, 1)] if not only else picked


def deepen_targets(state: dict[str, Any], only: str | None = None, target_depth: str = "deep") -> list[dict[str, Any]]:
    """Existing LLM paper cards that are still thinner than the target depth."""
    targets = []
    for record in state["records"]:
        if record.get("origin") != "llm-fulltext":
            continue
        if str(record.get("depth") or "overview") == target_depth:
            continue
        if only and str(record.get("paper_id")) != only and str(record.get("id")) != only:
            continue
        targets.append(record)
    targets.sort(key=lambda record: int(record.get("order") or 0))
    return targets


def complete_metadata(paper: dict[str, Any]) -> dict[str, Any]:
    """Historical audits predate discovery_entries; recover authors and date."""
    if paper.get("authors") and paper.get("published"):
        return paper
    paper_id = paper["id"]
    try:
        metadata = json.loads(http_get(f"https://huggingface.co/api/papers/{paper_id}", timeout=20, retries=1))
        authors = [item.get("name") for item in metadata.get("authors", []) if isinstance(item, dict) and item.get("name")]
        published = metadata.get("publishedAt", "")
        if authors and published:
            return {**paper, "authors": authors, "published": published}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, TypeError):
        pass
    raise CardError(f"metadata unavailable for {paper_id}; author and publication date required")


# ---------------------------------------------------------------- deep card drafting

PLAN_CORE_SYSTEM = """你在为深度知识档案做证据抽取（第一批：问题、主张、方法、术语）。只从给定的论文全文中抽取，不补充外部知识、不推断未写出的数字。
输出 JSON：
{
  "problem": "论文要解决的问题与语境，<=200字",
  "claims": [{"id":"C1","claim":"可证伪的主张，<=40字","evidence":"定位，如 §4.2 表2 / 图3 / 附录B","status":"作者主张|与共识一致|已复现|存疑"}],
  "method": {"mechanism":"机制与算法核心，<=300字","notation":[{"symbol":"","meaning":""}],"steps":["关键步骤"]},
  "glossary": [{"term":"英文术语","meaning":"中文解释"}]
}
要求：claims 3 到 4 条，每条必须有 evidence 定位。不要在 JSON 字符串里使用 LaTeX 反斜杠命令（如 \\mathcal、\\rho）；公式用简单文字或 Unicode 符号描述，否则 JSON 会非法。"""

PLAN_DATA_SYSTEM = """你在为深度知识档案做证据抽取（第二批：实验、结果、消融、局限、关系、原文片段）。只从给定的论文全文中抽取，数字必须原文照抄。
输出 JSON：
{
  "experiments": [{"benchmark":"","model":"","baseline":"","budget":"","metric":"","result":""}],
  "results": [{"metric":"","value":"","setting":"","source":"§/表/图编号"}],
  "ablations": ["消融设置与结论"],
  "limits": ["作者自陈或可从设置看出的局限"],
  "relations": [{"hint":"与哪个已有笔记主题相关","delta":"本文相对该主题新增/冲突/印证了什么"}],
  "quotes": ["可直接引用的关键原文片段，保留数字"]
}
要求：results 只记录摘录中出现的数字，原文照抄；没有的信息留空数组。"""

PLANNED_LISTS = ("claims", "experiments", "results", "ablations", "limits", "relations", "glossary", "quotes")


def plan_evidence(api_key: str, paper: dict[str, Any], full: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Extract the evidence sheet in two calls.

    One call used to exceed the output budget and return truncated JSON, so the
    sheet is split: claims/method/glossary first, experiments/results/limits second.
    """
    metadata = json.dumps({
        "arxiv_id": paper.get("id"),
        "title": paper.get("title"),
        "authors": ", ".join(str(name) for name in (paper.get("authors") or [])[:6]),
        "published": paper.get("published"),
        "url": paper.get("arxivUrl"),
        "triage_reason": paper.get("reason"),
    }, ensure_ascii=False, indent=2)
    excerpt = full["excerpt"][: config["planning_chars"]]
    base = "\n".join([
        "论文元数据:",
        metadata,
        "",
        "论文全文摘录（可能被截断，表格用 | 分隔）:",
        excerpt,
        "",
    ])
    core = chat_json_resilient(api_key, PLAN_CORE_SYSTEM, base + "请输出第一批 JSON（problem/claims/method/glossary）。", max_tokens=config["planning_tokens"], temperature=0.1, label="plan-core", attempts=config["plan_attempts"])
    data = chat_json_resilient(api_key, PLAN_DATA_SYSTEM, base + "请输出第二批 JSON（experiments/results/ablations/limits/relations/quotes）。", max_tokens=config["planning_tokens"], temperature=0.1, label="plan-data", attempts=config["plan_attempts"])
    evidence: dict[str, Any] = {**data, **core}
    for key in PLANNED_LISTS:
        if not isinstance(evidence.get(key), list):
            evidence[key] = []
    if not isinstance(evidence.get("method"), dict):
        evidence["method"] = {"mechanism": "", "notation": [], "steps": []}
    if not evidence["claims"]:
        raise CardError("evidence sheet has no claims")
    return evidence


DRAFT_SYSTEM = """你在写一份长期维护的深度论文档案的指定小节。读者是具备 RL 与 LLM 基础的研究者，他们要能据此判断这个结论值不值得信、能不能迁移到自己的场景。

写作规则：
- 只使用给定的证据表与全文摘录；不得编造数字、基准、作者或 URL。
- 数字必须与摘录一致（原文照抄）；无法确认的数字就不写。
- 表格优先于长段落来呈现实验设置与结果。
- 必须区分「作者主张」和「已复现/共识」；不确定处显式标注不确定。
- 使用 Markdown，公式用 $...$ 或 $$...$$。
- 不要输出 JSON，不要输出代码块围栏。

输出格式（严格遵守）：为每个请求的小节输出一个块，依次排列：
<<<SECTION 小节标题>>>
该小节的 Markdown 正文
<<<END>>>

标题必须与请求完全一致；每个块必须有 <<<END>>> 收尾；不要输出任何额外说明。"""

SECTION_RE = re.compile(r"<<<SECTION\s*(?P<title>[^\n>]+?)\s*>>>\s*(?P<body>.*?)(?=<<<SECTION|<<<END>>>|\Z)", re.S)


def parse_section_blocks(text: str) -> dict[str, str]:
    """Parse ``<<<SECTION title>>> ... <<<END>>>`` blocks into {title: markdown}."""
    blocks: dict[str, str] = {}
    for match in SECTION_RE.finditer(text):
        title = match.group("title").strip()
        body = clean_body(match.group("body"))
        if title and body:
            blocks[title] = body
    return blocks


def draft_sections(api_key: str, paper: dict[str, Any], evidence: dict[str, Any], names: tuple[str, ...], full: dict[str, Any], config: dict[str, Any], extra: str = "") -> dict[str, str]:
    slices = slice_for_sections(full, names, config["section_source_budget"])
    sections_json = json.dumps(evidence, ensure_ascii=False, indent=2)
    if len(sections_json) > 40000:
        sections_json = sections_json[:40000]
    user = "\n".join([
        f"论文：{paper.get('title')}（arXiv {paper.get('id')}）",
        "",
        "证据表（已从全文抽取）:",
        sections_json,
        "",
        "相关全文摘录:",
        slices,
        "",
        "需要撰写的小节（按此顺序输出对应的 <<<SECTION>>> 块）:",
        json.dumps(list(names), ensure_ascii=False),
        "",
        "每个小节的要求（长度、必须包含的内容）:",
        json.dumps({name: SECTION_BRIEFS.get(name, "") for name in names}, ensure_ascii=False, indent=2),
        "",
        "额外约束:",
        extra or "无",
    ])
    last_error = "unknown"
    for attempt in range(config["plan_attempts"]):
        prompt = user if attempt == 0 else user + SECTION_NUDGE.format(names="、".join(names))
        text, finish_reason = chat_text(api_key, DRAFT_SYSTEM, prompt, max_tokens=config["section_tokens"], temperature=0.2, label=f"draft[{names[0] if names else '?'}]")
        blocks = parse_section_blocks(text)
        missing = [name for name in names if name not in blocks]
        if not missing and finish_reason != "length":
            return {name: blocks[name] for name in names}
        last_error = f"missing={missing or 'none'}, finish_reason={finish_reason}, chars={len(text)}"
        print(f"cards: draft attempt {attempt + 1} incomplete ({last_error})", file=sys.stderr, flush=True)
    raise CardError(f"draft incomplete after {config['plan_attempts']} attempts: {last_error}")


SECTION_NUDGE = (
    "\n\n注意：上一次输出不完整（被长度截断或缺少收尾标记），整段作废。请重新输出：\n"
    "- 只输出这些小节：{names}；\n"
    "- 严格控制在给定字数区间内（总长约 300-550 字/节），不要超出上调；\n"
    "- 每个块必须以 <<<END>>> 收尾，不得省略；\n"
    "- 不要复述摘录原文，不要额外说明。"
)


SECTION_BRIEFS = {
    "问题与语境": "300-450 字。说明问题为何重要、已有做法及其失效点；给出论文的定位（不是复述摘要）。",
    "核心主张": "350-500 字，并包含一个 Markdown 表格，列为 `| # | 主张 | 证据 | 状态 |`，至少 3 行；证据列必须写具体定位（§、表、图编号）；状态列只能取 作者主张/与共识一致/已复现/存疑。表格后再写一段说明哪条主张最强、哪条最弱。",
    "机制与方法": "500-700 字。讲清机制与算法，包含关键公式、符号含义与设计取舍；指出方法的适用前提。",
    "实验设置": "300-450 字，包含一个 Markdown 表格，列为 `| 基准 | 模型/规模 | 基线 | 预算 | 指标 |`，每行一个实验块；没有写明的字段填「未说明」。",
    "证据与结果": "400-600 字。用表格列出摘录中出现的数字（`| 指标 | 数值 | 设置 | 出处 |`），再说明消融与对照；数字无法确认时明确写「摘录未给出」。",
    "证据强度评估": "350-500 字。给出本档案的证据分级（A/B/C/D）与理由，列出 2-4 条对该结论的主要威胁（构造效度、外部效度、统计显著性、基线选择、评测污染）。",
    "边界与反例": "350-500 字。写出什么观察会推翻结论、在什么条件下最可能失效，以及作者未验证但读者可能误推的方向。",
    "与知识库的关系": "300-450 字。逐条说明与相关笔记的差异（新增了什么、印证了什么、与哪条结论存在张力），并给出可链接的笔记 id。",
    "复现与验证计划": "300-450 字。给出可执行的最小验证：环境、数据/任务、基线、预算、判据、预期失败模式。",
    "术语与记号": "250-400 字，包含 `| 术语 | 含义 |` 表格，覆盖正文出现的关键符号与缩写。",
    "自测": "250-400 字，5 个问题，其中至少 2 个需要跨小节推理；每题给出折叠答案（用 `<details><summary>答案</summary>` 包裹）。",
}


def assemble_body(drafted: dict[str, str], order: tuple[str, ...]) -> str:
    parts = []
    for name in order:
        body = drafted.get(name)
        if not body:
            continue
        heading = name if name.startswith("##") else f"## {name}"
        parts.append(f"{heading}\n\n{body.strip()}")
    return "\n\n".join(parts).strip()


def summarize(evidence: dict[str, Any], paper: dict[str, Any]) -> str:
    """One-line problem statement, cut at a sentence boundary rather than mid-clause."""
    problem = sanitize_scalar(evidence.get("problem")).replace(",", "，")
    if not problem:
        return sanitize_scalar(paper.get("title"))[:140]
    if len(problem) <= 140:
        return problem
    cut = max(problem.rfind(mark, 40, 140) for mark in "。；;.")
    return problem[: cut + 1] if cut >= 40 else problem[:140]


def estimate_minutes(body: str) -> int:
    return max(20, min(60, round(len(body) / 260)))


def grounding_violations(body: str, full: dict[str, Any], config: dict[str, Any]) -> list[str]:
    problems = []
    numbers = ungrounded_numbers(body, full["excerpt"])
    if len(numbers) > config["max_ungrounded_numbers"]:
        problems.append("numbers not found in source excerpt: " + ", ".join(numbers[:12]))
    for url in re.findall(r"\]\((https?://[^)\s]+)\)", body):
        if url not in full["excerpt"]:
            problems.append(f"URL not present in source excerpt: {url}")
    return problems


def final_violations(kind: str, depth: str, card: dict[str, Any], normalized: dict[str, Any], full: dict[str, Any], config: dict[str, Any]) -> list[str]:
    """Contract + grounding checks that need the resolved relations to be complete."""
    problems = check_structure(kind, depth, card["body"], related_count=len(normalized["related"]), has_evidence_grade=True)
    problems += grounding_violations(card["body"], full, config)
    return problems


def build_deep_card(
    api_key: str,
    paper: dict[str, Any],
    full: dict[str, Any],
    state: dict[str, Any],
    config: dict[str, Any],
    *,
    kind: str = "paper",
    draft: Callable[..., dict[str, str]] = draft_sections,
    plan: Callable[..., dict[str, Any]] = plan_evidence,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate a deep card body plus the evidence sheet used to write it."""
    evidence = plan(api_key, paper, full, config)
    groups = [tuple(PAPER_DEEP[index:index + config["sections_per_call"]]) for index in range(0, len(PAPER_DEEP), config["sections_per_call"])]
    drafted: dict[str, str] = {}
    for group in groups:
        drafted.update(draft(api_key, paper, evidence, group, full, config))
    body = assemble_body(drafted, PAPER_DEEP)

    violations: list[str] = []
    for attempt in range(config["repair_attempts"] + 1):
        # related_count is validated after metadata resolution, so it is not gated here.
        violations = check_structure(kind, config["target_depth"], body, related_count=99, has_evidence_grade=True)
        violations += grounding_violations(body, full, config)
        if not violations or attempt == config["repair_attempts"]:
            break
        instructions = "\n".join(f"- {item}" for item in violations)
        extra = (
            "上一稿存在以下问题，请在重写本次请求的小节时全部修正，并保持与未重写小节一致：\n"
            f"{instructions}"
        )
        # Rewrite group by group: requesting all sections in one call overruns the output budget.
        repaired: dict[str, str] = {}
        try:
            for group in groups:
                repaired.update(draft(api_key, paper, evidence, group, full, config, extra=extra))
        except CardError:
            break
        drafted.update(repaired)
        body = assemble_body(drafted, PAPER_DEEP)

    card = {
        "summary": summarize(evidence, paper),
        "body": body,
        "evidence": evidence,
        "violations": violations,
        "claims": parse_claims(body),
        "sectionSizes": section_sizes(body),
    }
    return card, evidence


# ---------------------------------------------------------------- writing

def render_note(
    *,
    note_id: str,
    title: str,
    summary: str,
    stage: str,
    track: str,
    order: int,
    minutes: int,
    review_status: str,
    evidence_grade: str,
    objectives: list[str],
    tags: list[str],
    source_id: str,
    related: list[str],
    prerequisites: list[str],
    paper: dict[str, Any],
    full: dict[str, Any],
    body: str,
    kind: str = "paper",
    depth: str = "deep",
    claim_count: int = 0,
    today: str | None = None,
) -> str:
    date = today or dt.datetime.now(dt.timezone.utc).date().isoformat()
    # Sanitize here as well as in normalize_card: render_note is the last gate before
    # the flat frontmatter parser sees the text, so it must not trust its caller.
    def scalar(value: Any) -> str:
        return sanitize_scalar(value).replace(",", "，")

    def items(values: list[str]) -> str:
        return ", ".join(scalar(item) for item in values if str(item).strip())

    frontmatter = [
        "---",
        f"id: {note_id}",
        f"title: {scalar(title)}",
        f"summary: {scalar(summary)}",
        f"stage: {scalar(stage)}",
        f"track: {scalar(track)}",
        f"kind: {scalar(kind)}",
        f"depth: {scalar(depth)}",
        f"evidenceGrade: {scalar(evidence_grade)}",
        f"order: {order}",
        f"minutes: {minutes}",
        f"updated: '{date}'",
        f"review: {scalar(review_status)}",
        "origin: llm-fulltext",
        f"paper_id: {scalar(paper.get('id'))}",
        "reading_depth: full-text",
        "evidence_level: full-text-llm-draft",
        f"claim_count: {claim_count}",
        f"full_text_url: {scalar(full['url'])}",
        f"objectives: [{items(objectives)}]",
        f"tags: [{items(tags)}]",
        f"sources: [{items([source_id])}]",
        f"related: [{items(related)}]",
        f"prerequisites: [{items(prerequisites)}]",
        "---",
    ]
    return "\n".join(frontmatter) + "\n" + body.strip() + "\n"


def normalize_card(card: dict[str, Any], paper: dict[str, Any], state: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    for key in ("summary", "body"):
        if not str(card.get(key) or "").strip():
            raise CardError(f"card missing field: {key}")
    meta = card.get("meta") if isinstance(card.get("meta"), dict) else {}
    original = sanitize_scalar(paper.get("title"))
    title = sanitize_scalar(meta.get("title")).replace(",", "，")[:60] or original[:60]
    # Relations are resolved from the model's proposal only: inventing links would
    # pollute the knowledge graph with edges nobody wrote.
    related = [str(item) for item in meta.get("related", []) if str(item) in state["ids"] and str(item) != card.get("note_id")]
    if len(related) < 2:
        raise CardError(f"needs at least 2 valid related note ids, got {related}")
    stage = str(meta.get("stage") or "FRONTIER").upper()
    return {
        "title": title,
        "stage": stage if stage in STAGES else "FRONTIER",
        "track": str(meta.get("track")) if str(meta.get("track")) in TRACKS else "前沿专题",
        "objectives": clean_list(meta.get("objectives"), 4) or ["理解该论文的主张与证据边界"],
        "tags": clean_list(meta.get("tags"), 6) or ["paper"],
        "related": related[:3],
        "prerequisites": [str(item) for item in meta.get("prerequisites", []) if str(item) in state["ids"]][:2],
    }


def source_record(source_id: str, paper: dict[str, Any], summary: str, review_status: str) -> dict[str, Any]:
    authors = list(paper.get("authors") or [])
    year = str(paper.get("published") or "")[:4] or str(dt.datetime.now(dt.timezone.utc).year)
    return {
        "id": source_id,
        "title": sanitize_scalar(paper.get("title")),
        "kind": "论文",
        "author": sanitize_scalar(f"{authors[0]} et al.") if authors else "见原文作者列表",
        "year": year,
        "url": str(paper.get("arxivUrl") or f"https://arxiv.org/abs/{paper.get('id')}"),
        "evidence": review_status,
        "note": sanitize_scalar(f"LLM 深度精读草稿：{summary[:160]}"),
    }


def write_sources(state: dict[str, Any], source: dict[str, Any]) -> None:
    state["catalog"].append(source)
    SOURCES.write_text("[\n" + ",\n".join("  " + json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in state["catalog"]) + "\n]\n", encoding="utf-8")


def metadata_from_evidence(api_key: str, paper: dict[str, Any], evidence: dict[str, Any], state: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Ask for the card-level metadata (title, stage, track, objectives, tags, related)."""
    note_ids = sorted(state["ids"])
    user = "\n".join([
        f"论文：{paper.get('title')}（arXiv {paper.get('id')}）",
        "",
        "证据表:",
        json.dumps(evidence, ensure_ascii=False, indent=2)[:20000],
        "",
        "请返回 JSON：",
        '{"title":"中文标题 <=40 字","stage":"FOUNDATION|SYSTEMS|FRONTIER","track":"概念与基础|训练算法|Agent 系统|评估与安全|前沿专题|实验与维护","objectives":["2到4条 读完你能..."],"tags":["2到6个英文主题标签"],"related":["从下面已有笔记 id 中选 2 到 4 个最相关"],"prerequisites":["0到2个已有笔记 id"]}',
        "",
        "已有笔记 id:",
        ", ".join(note_ids),
    ])
    return chat_json_resilient(api_key, "你为知识库卡片选择元数据，只返回 JSON。related 只能从给定 id 中选。", user, max_tokens=1500, temperature=0.1, label="metadata", attempts=config["plan_attempts"])


def run(limit: int | None, only: str | None) -> int:
    require_llm_enabled("cards")
    config = load_config()
    api_key = os.environ.get("DEEPSEEK_V4_FLASH_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_V4_FLASH_API_KEY is required")
    radar = json.loads(RADAR.read_text(encoding="utf-8")) if RADAR.exists() else {"papers": []}
    state = existing_state()
    candidates = select_candidates(radar, state, 100000, config["decisions"], only)
    generated, skipped = [], []
    card_limit = max(1, limit if limit is not None else config["limit"])
    for paper in candidates:
        if len(generated) >= card_limit:
            break
        paper_id = str(paper.get("id"))
        try:
            paper = complete_metadata(paper)
        except CardError as error:
            skipped.append({"id": paper_id, "reason": str(error)})
            continue
        print(f"cards: fetching full text for {paper_id}", file=sys.stderr, flush=True)
        full = fetch_fulltext(paper_id, config["max_chars"], config["per_section_chars"])
        if not full:
            skipped.append({"id": paper_id, "reason": "no full text"})
            continue
        print(f"cards: planning evidence for {paper_id} ({full['chars']} chars)", file=sys.stderr, flush=True)
        try:
            card, _ = build_deep_card(api_key, paper, full, state, config)
            if card["violations"]:
                skipped.append({"id": paper_id, "reason": "contract violations: " + "; ".join(card["violations"][:4])})
                continue
            meta = metadata_from_evidence(api_key, paper, card["evidence"], state, config)
            card["meta"] = meta
            note_id = best_slug([str(meta.get("title") or ""), str(paper.get("title") or ""), f"arxiv {paper_id}"], state["ids"])
            card["note_id"] = note_id
            normalized = normalize_card(card, paper, state, config)
            final = final_violations("paper", config["target_depth"], card, normalized, full, config)
            if final:
                skipped.append({"id": paper_id, "reason": "contract violations: " + "; ".join(final[:4])})
                continue
            source_id = unique_slug(paper.get("title") or paper_id, state["catalog_ids"])
            body = card["body"]
            note_path = CONTENT / f"{state['max_order'] + len(generated) + 1:02d}-{note_id}.md"
            note_path.write_text(render_note(
                note_id=note_id,
                title=normalized["title"],
                summary=card["summary"],
                stage=normalized["stage"],
                track=normalized["track"],
                order=state["max_order"] + len(generated) + 1,
                minutes=estimate_minutes(body),
                review_status=config["review_status"],
                evidence_grade="C",
                objectives=normalized["objectives"],
                tags=normalized["tags"],
                source_id=source_id,
                related=normalized["related"],
                prerequisites=normalized["prerequisites"],
                paper=paper,
                full=full,
                body=body,
                claim_count=len(card["claims"]),
            ), encoding="utf-8")
            write_sources(state, source_record(source_id, paper, card["summary"], config["review_status"]))
        except CardError as error:
            skipped.append({"id": paper_id, "reason": str(error)})
            continue
        state["ids"].add(note_id)
        state["catalog_ids"].add(source_id)
        # Keep the queue state honest so pendingReviews excludes what we just wrote.
        state["paper_ids"].add(paper_id)
        state["titles"].add(normalized["title"].strip().lower())
        generated.append({
            "note_id": note_id, "note_path": str(note_path.relative_to(ROOT)), "source_id": source_id,
            "title": normalized["title"], "stage": normalized["stage"], "depth": config["target_depth"],
            "claims": len(card["claims"]), "chars": len(body), "minutes": estimate_minutes(body),
            "arxiv_id": paper_id, "full_text_url": full["url"],
        })
        time.sleep(2)
    write_summary(generated, skipped, config, state, radar)
    print(json.dumps({"generated": len(generated), "skipped": len(skipped), "notes": [item["note_id"] for item in generated]}, ensure_ascii=False))
    return 0


def deepen(limit: int | None, only: str | None, force: bool) -> int:
    """Rewrite thin LLM paper cards as deep dossiers, in place."""
    require_llm_enabled("cards")
    config = load_config()
    api_key = os.environ.get("DEEPSEEK_V4_FLASH_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_V4_FLASH_API_KEY is required")
    state = existing_state()
    targets = deepen_targets(state, only, config["target_depth"])
    if not force:
        targets = [record for record in targets if str(record.get("review")) == config["review_status"]]
    deepened, skipped = [], []
    depth_limit = max(1, limit if limit is not None else config["limit"])
    for record in targets:
        if len(deepened) >= depth_limit:
            break
        paper_id = str(record.get("paper_id") or "")
        if not paper_id:
            skipped.append({"id": str(record.get("id")), "reason": "no paper_id"})
            continue
        title = str(record.get("title") or "")
        print(f"cards: deepening {record.get('id')} ({paper_id})", file=sys.stderr, flush=True)
        full = fetch_fulltext(paper_id, config["max_chars"], config["per_section_chars"])
        if not full:
            skipped.append({"id": str(record.get("id")), "reason": "no full text"})
            continue
        base = {"id": paper_id, "title": title, "authors": [], "published": "", "arxivUrl": f"https://arxiv.org/abs/{paper_id}"}
        try:
            base = complete_metadata(base)
        except CardError:
            base["authors"] = ["见原文作者列表"]
            base["published"] = str(record.get("updated") or "")[:4]
        existing_sources = record.get("sources") if isinstance(record.get("sources"), list) else []
        if not existing_sources:
            skipped.append({"id": str(record.get("id")), "reason": "card has no source reference"})
            continue
        try:
            card, _ = build_deep_card(api_key, base, full, state, config)
            if card["violations"]:
                skipped.append({"id": str(record.get("id")), "reason": "contract violations: " + "; ".join(card["violations"][:4])})
                continue
            meta = metadata_from_evidence(api_key, base, card["evidence"], state, config)
            card["meta"] = meta
            card["note_id"] = str(record["id"])
            normalized = normalize_card(card, base, state, config)
            final = final_violations("paper", config["target_depth"], card, normalized, full, config)
            if final:
                skipped.append({"id": str(record.get("id")), "reason": "contract violations: " + "; ".join(final[:4])})
                continue
            body = card["body"]
            path = Path(record["_path"])
            path.write_text(render_note(
                note_id=str(record["id"]),
                title=title or normalized["title"],
                summary=card["summary"],
                stage=str(record.get("stage") or normalized["stage"]),
                track=str(record.get("track") or normalized["track"]),
                order=int(record.get("order") or 0),
                minutes=estimate_minutes(body),
                review_status=config["review_status"],
                evidence_grade=str(record.get("evidenceGrade") or "C"),
                objectives=normalized["objectives"] or record.get("objectives", []),
                tags=normalized["tags"] or record.get("tags", []),
                source_id=str(existing_sources[0]),
                related=normalized["related"] or record.get("related", []),
                prerequisites=[str(item) for item in (record.get("prerequisites") or [])],
                paper=base,
                full=full,
                body=body,
                claim_count=len(card["claims"]),
            ), encoding="utf-8")
        except CardError as error:
            skipped.append({"id": str(record.get("id")), "reason": str(error)})
            continue
        deepened.append({
            "note_id": str(record["id"]), "note_path": str(path.relative_to(ROOT)),
            "title": title, "depth": config["target_depth"], "claims": len(card["claims"]),
            "chars": len(body), "minutes": estimate_minutes(body), "arxiv_id": paper_id,
        })
        time.sleep(2)
    summary = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "deepen",
        "requested": len(targets),
        "deepened": deepened,
        "skipped": skipped,
        "reviewStatus": config["review_status"],
        "publishDirectly": False,
    }
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    (CARDS_DIR / "latest-deepen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    remaining = deepen_targets(existing_state(), None, config["target_depth"])
    lines = ["", "## 存量卡片深化", "", f"> 本次深化 {len(deepened)} 张，仍有 {len(remaining)} 张薄卡待深化。", ""]
    for item in deepened:
        lines += [f"### {item['title']}", f"- 笔记：`{item['note_path']}`", f"- 深度：`{item['depth']}` · 主张 {item['claims']} 条 · 约 {item['chars']} 字", f"- 论文：arXiv `{item['arxiv_id']}`", ""]
    if skipped:
        lines += ["### 跳过", "", *[f"- `{item['id']}`：{item['reason']}" for item in skipped], ""]
    (CARDS_DIR / "latest-deepen.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"deepened": len(deepened), "skipped": len(skipped), "notes": [item["note_id"] for item in deepened]}, ensure_ascii=False))
    return 0


def write_summary(generated: list[dict[str, Any]], skipped: list[dict[str, Any]], config: dict[str, Any], state: dict[str, Any], radar: dict[str, Any]) -> None:
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    pending = select_candidates(radar, state, 100000, config["decisions"], None)
    backlog = deepen_targets(state, None, config["target_depth"])
    summary = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "run",
        "targetDepth": config["target_depth"],
        "requested": len(pending),
        "pendingReviews": len(pending),
        "deepenBacklog": len(backlog),
        "generated": generated,
        "skipped": skipped,
        "reviewStatus": config["review_status"],
        "publishDirectly": False,
    }
    (CARDS_DIR / "latest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["", "## 自动生成的深度知识卡", "", f"> LLM 全文深读草稿，需人工复核后才算已审核知识。本次生成 {len(generated)} 张深读卡，待深化存量 {len(backlog)} 张。", ""]
    for item in generated:
        lines += [
            f"### {item['title']}",
            f"- 笔记：`{item['note_path']}`",
            f"- 深度：`{item['depth']}` · 主张 {item['claims']} 条 · 约 {item['chars']} 字",
            f"- 论文：arXiv `{item['arxiv_id']}` · 全文：{item['full_text_url']}",
            "",
        ]
    if skipped:
        lines += ["### 跳过", "", *[f"- `{item['id']}`：{item['reason']}" for item in skipped], ""]
    (CARDS_DIR / "latest.md").write_text("\n".join(lines), encoding="utf-8")


def preview(paper_id: str) -> int:
    """Fetch and report extraction quality without calling the model (debug entry point)."""
    config = load_config()
    full = fetch_fulltext(paper_id, config["max_chars"], config["per_section_chars"])
    if not full:
        print(f"cards: no full text for {paper_id}", file=sys.stderr)
        return 1
    excerpt = full["excerpt"]
    print(json.dumps({
        "arxiv_id": paper_id,
        "url": full["url"],
        "title": full["title"],
        "chars": full["chars"],
        "sections": [{"title": section["title"], "chars": len(section["text"])} for section in full["sections"]],
        "tableRows": sum(1 for line in excerpt.splitlines() if line.count(" | ") >= 1),
        "mathSpans": excerpt.count(" $"),
        "substantiveNumbers": len(re.findall(r"\d+\.\d+", excerpt)),
    }, ensure_ascii=False, indent=2))
    return 0


def status() -> int:
    config = load_config()
    radar = json.loads(RADAR.read_text(encoding="utf-8")) if RADAR.exists() else {"papers": []}
    state = existing_state()
    pending = select_candidates(radar, state, 100000, config["decisions"], None)
    backlog = deepen_targets(state, None, config["target_depth"])
    deep = sum(1 for record in state["records"] if str(record.get("depth")) == config["target_depth"])
    print(json.dumps({
        "pendingReviews": len(pending),
        "deepenBacklog": len(backlog),
        "deepNotes": deep,
        "totalNotes": len(state["records"]),
        "deepShare": round(deep / max(len(state["records"]), 1), 3),
        "papers": [{"id": item["id"], "title": item["title"]} for item in pending],
        "deepen": [{"id": item["id"], "paper_id": item.get("paper_id"), "title": item.get("title")} for item in backlog],
    }, ensure_ascii=False, indent=2))
    return 0


def check() -> int:
    """Validate deep LLM cards against the contract; report the thin backlog."""
    config = load_config()
    problems, backlog = [], []
    for path in sorted(CONTENT.glob("*.md")):
        data = parse_frontmatter(path)
        if data.get("origin") != "llm-fulltext":
            continue
        for field in ("paper_id", "full_text_url", "evidence_level", "review"):
            if not str(data.get(field, "")).strip():
                problems.append(f"{path.name}: missing {field}")
        depth = str(data.get("depth") or "overview")
        if depth != config["target_depth"]:
            backlog.append(f"{path.name}: depth={depth}")
            continue
        body = path.read_text(encoding="utf-8").split("\n---\n", 1)[-1]
        related = data.get("related") if isinstance(data.get("related"), list) else []
        violations = check_structure("paper", depth, body, related_count=len(related), has_evidence_grade=bool(data.get("evidenceGrade")))
        problems.extend(f"{path.name}: {item}" for item in violations)
        declared = data.get("claim_count")
        if isinstance(declared, int) and declared != len(parse_claims(body)):
            problems.append(f"{path.name}: claim_count={declared} does not match {len(parse_claims(body))} table rows")
    if backlog:
        print("\n".join(f"cards: thin draft pending deepen: {item}" for item in backlog), file=sys.stderr)
    if problems:
        print("\n".join(f"cards: {item}" for item in problems), file=sys.stderr)
        return 1
    print(f"cards: OK · deep cards valid · {len(backlog)} thin drafts pending deepen")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", default="run", choices=["run", "deepen", "check", "status", "fetch"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--paper", default=None)
    parser.add_argument("--force", action="store_true", help="deepen cards even if they were marked as human-reviewed")
    args = parser.parse_args()
    try:
        if args.command == "check":
            return check()
        if args.command == "status":
            return status()
        if args.command == "fetch":
            if not args.paper:
                print("cards: fetch requires --paper ARXIV_ID", file=sys.stderr)
                return 2
            return preview(args.paper)
        if args.command == "deepen":
            return deepen(args.limit, args.paper, args.force)
        return run(args.limit, args.paper)
    except (CardError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"cards: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
