#!/usr/bin/env python3
"""Turn selected daily papers into knowledge cards via DeepSeek + the harness.

Flow:
  1. read data/generated/radar.json (HuggingFace discovery + DeepSeek triage)
  2. select interesting papers (decision=review) that are not already in the KB
  3. fetch the full text from arXiv HTML (or ar5iv), extract the main sections
  4. ask DeepSeek for a structured, conservative Chinese knowledge card
  5. write the card to content/ and the paper to data/sources.json

Nothing is published directly: cards are written with review status
"LLM 全文精读草稿 · 待人工复核" and land in the audit pull request, where a
human reviews them before merge. Full text is never stored in the repository.

Usage:
    python scripts/cards.py run [--limit N] [--paper ARXIV_ID]
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
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
SOURCES = ROOT / "data" / "sources.json"
CONFIG = ROOT / "harness.config.json"
RADAR = ROOT / "data" / "generated" / "radar.json"
CARDS_DIR = ROOT / "research" / "cards"
MODEL = "deepseek-v4-flash"
MAX_TOKENS = 6000
REVIEW_STATUS = "LLM 全文精读草稿 · 待人工复核"
STAGES = {"FOUNDATION", "SYSTEMS", "FRONTIER"}
TRACKS = ["概念与基础", "训练算法", "Agent 系统", "评估与安全", "前沿专题", "实验与维护"]
HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
SKIP_TAGS = ("script", "style", "svg", "math", "nav", "footer", "header", "figure", "figcaption")
KEEP_SECTION = re.compile(r"abstract|introduction|background|related|method|approach|model|framework|training|objective|experiment|result|evaluation|benchmark|analysis|ablation|discussion|limitation|conclusion", re.I)
HEADERS = {"User-Agent": "AgenticRLAtlas/0.1 (personal research; full-text card draft)", "Accept": "text/html,application/xhtml+xml"}
SYSTEM = """你是 Agentic RL 知识库的论文精读助手。你只使用用户提供的论文全文摘录，绝不编造事实、数字、基准结果或 URL。用简体中文写一张可审阅的知识卡，风格克制：区分论文作者的主张与已有共识，明确证据边界，不把摘要级信息当成已确证结论。只返回 JSON。"""


class CardError(Exception):
    pass


# ---------------------------------------------------------------- full text

class PaperParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.sections: list[dict[str, Any]] = []
        self._loose: list[str] = []
        self._current: dict[str, Any] | None = None
        self._mode: tuple | None = None
        self._buf: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in SKIP_TAGS:
            self._skip += 1
            return
        if self._skip:
            return
        if tag == "title":
            self._mode = ("title",)
            self._buf = []
        elif tag in HEADINGS:
            self._flush()
            self._mode = ("heading", int(tag[1]))
            self._buf = []
        elif tag == "p":
            self._flush()
            self._mode = ("para",)
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag == "title" or tag in HEADINGS or tag == "p":
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip or self._mode is None:
            return
        self._buf.append(data)

    def _flush(self) -> None:
        mode, self._mode = self._mode, None
        text = " ".join("".join(self._buf).split())
        self._buf = []
        if not text:
            return
        if mode is None:
            return
        if mode[0] == "title":
            self.title = text
        elif mode[0] == "heading":
            level = mode[1]
            if level == 1:
                if not self.title:
                    self.title = text
                self._current = None
            else:
                self._current = {"title": text, "level": level, "text": ""}
                self.sections.append(self._current)
        else:
            if self._current is None:
                self._loose.append(text)
            elif self._current["text"]:
                self._current["text"] += "\n" + text
            else:
                self._current["text"] = text

    def result(self) -> dict[str, Any]:
        sections = self.sections
        if self._loose and not any(section["title"].lower().startswith("abstract") for section in sections):
            sections.insert(0, {"title": "Abstract", "level": 2, "text": "\n".join(self._loose)})
        return {"title": self.title, "sections": sections}


def http_get(url: str, timeout: int = 90) -> bytes:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def extract_excerpt(html: str, max_chars: int) -> dict[str, Any]:
    parser = PaperParser()
    parser.feed(html)
    parsed = parser.result()
    selected = [section for section in parsed["sections"] if (section["level"] or 9) <= 3 and KEEP_SECTION.search(section["title"])]
    if not selected:
        selected = parsed["sections"][:8]
    parts, total = [], 0
    for section in selected:
        text = section["text"].strip()
        if not text:
            continue
        block = f"## {section['title']}\n{text[:6000]}"
        if total + len(block) > max_chars:
            block = block[: max(0, max_chars - total)]
        parts.append(block)
        total += len(block)
        if total >= max_chars:
            break
    return {"title": parsed["title"], "excerpt": "\n\n".join(parts), "chars": total}


def fetch_fulltext(arxiv_id: str, max_chars: int) -> dict[str, Any] | None:
    for url in (f"https://arxiv.org/html/{arxiv_id}", f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"):
        try:
            raw = http_get(url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            continue
        if len(raw) < 20000:
            continue
        excerpt = extract_excerpt(raw.decode("utf-8", errors="replace"), max_chars)
        if len(excerpt["excerpt"]) < 2000:
            continue
        return {"url": url, "title": excerpt["title"], "excerpt": excerpt["excerpt"], "chars": excerpt["chars"]}
    return None


# ---------------------------------------------------------------- LLM

def chat_json(api_key: str, system: str, user: str) -> dict[str, Any]:
    body = json.dumps({
        "model": MODEL,
        "temperature": 0.2,
        "max_tokens": MAX_TOKENS,
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }).encode()
    request = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": "AgenticRLAtlas-cards/1.0"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise CardError(f"DeepSeek API HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise CardError(f"DeepSeek API network error: {exc}") from None
    except json.JSONDecodeError:
        raise CardError("DeepSeek API returned a non-JSON response") from None
    try:
        choice = result["choices"][0]
        text = (choice["message"].get("content") or "").strip()
        finish_reason = choice.get("finish_reason")
    except (KeyError, IndexError, TypeError):
        raise CardError("DeepSeek API response missing choices.message.content") from None
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise CardError(f"DeepSeek returned no JSON object (finish_reason={finish_reason}, chars={len(text)})")
    try:
        parsed = json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        raise CardError(f"DeepSeek returned invalid JSON ({exc.msg})") from None
    if not isinstance(parsed, dict):
        raise CardError("DeepSeek returned a JSON value instead of an object")
    return parsed


# ---------------------------------------------------------------- helpers

def slugify(value: str, limit: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return slug[:limit].strip("-") or "card"


def unique_slug(base: str, taken: set[str]) -> str:
    candidate = slugify(base)
    if candidate not in taken:
        return candidate
    index = 2
    while f"{candidate}-{index}" in taken:
        index += 1
    return f"{candidate}-{index}"


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


def clean_list(value: Any, limit: int = 6) -> list[str]:
    if not isinstance(value, list):
        return []
    items = []
    for item in value:
        text = str(item).replace(",", "，").strip()
        if text and text not in items:
            items.append(text)
    return items[:limit]


def clean_body(value: Any) -> str:
    body = str(value or "").replace("\r\n", "\n")
    body = re.sub(r"\n-{3,}\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body


def load_config() -> dict[str, Any]:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        config = {}
    card = config.get("cardGeneration", {}) if isinstance(config, dict) else {}
    return {
        "limit": int(card.get("maxCards", 3)),
        "decisions": card.get("decisions", ["review"]),
        "max_chars": int(card.get("maxFullTextChars", 60000)),
        "review_status": card.get("reviewStatus", REVIEW_STATUS),
    }


def existing_state() -> dict[str, Any]:
    notes, ids, orders, paper_ids, titles = [], set(), [], set(), set()
    for path in sorted(CONTENT.glob("*.md")):
        data = parse_frontmatter(path)
        if not data.get("id"):
            continue
        notes.append(data)
        ids.add(str(data["id"]))
        titles.add(str(data.get("title", "")).strip().lower())
        if isinstance(data.get("order"), int):
            orders.append(data["order"])
        if data.get("paper_id"):
            paper_ids.add(str(data["paper_id"]))
    catalog = json.loads(SOURCES.read_text(encoding="utf-8")) if SOURCES.exists() else []
    return {"notes": notes, "ids": ids, "titles": titles, "paper_ids": paper_ids, "max_order": max(orders, default=0), "catalog": catalog, "catalog_ids": {str(item.get("id")) for item in catalog}}


def select_candidates(radar: dict[str, Any], state: dict[str, Any], limit: int, decisions: list[str], only: str | None) -> list[dict[str, Any]]:
    known_urls = {str(item.get("url")) for item in state["catalog"]}
    picked = []
    for paper in radar.get("papers", []):
        if not isinstance(paper, dict):
            continue
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
    picked.sort(key=lambda item: (-int(item.get("relevanceScore") or 0), -int(item.get("upvotes") or 0)))
    return picked[: max(limit, 1)] if not only else picked


# ---------------------------------------------------------------- card draft

def draft_card(api_key: str, paper: dict[str, Any], full: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    authors = ", ".join(str(name) for name in (paper.get("authors") or [])[:6])
    user = "\n".join([
        "论文元数据:",
        json.dumps({
            "arxiv_id": paper.get("id"),
            "title": paper.get("title"),
            "authors": authors,
            "published": paper.get("published"),
            "url": paper.get("arxivUrl"),
            "matched_keywords": paper.get("matchedKeywords"),
            "triage_reason": paper.get("reason"),
        }, ensure_ascii=False, indent=2),
        "",
        "论文全文摘录（可能被截断）:",
        full["excerpt"],
        "",
        "请只根据以上摘录返回 JSON，字段如下：",
        '{"id": "小写英文短横线 slug，<=40 字符", "title": "中文标题 <=40 字", "summary": "一句话说明论文解决什么问题，<=90 字", "stage": "FOUNDATION|SYSTEMS|FRONTIER", "track": "概念与基础|训练算法|Agent 系统|评估与安全|前沿专题|实验与维护", "minutes": 10到25的整数, "tags": ["2到5个英文/缩写主题标签"], "objectives": ["2到3条 读完你能..."], "related": ["从已有笔记 id 中选0到3个最相关的"], "body": "Markdown 正文"}',
        "约束:",
        "- body 必须包含这些二级标题: ## 论文要解决的问题 / ## 方法 / ## 证据与实验 / ## 边界与未解问题 / ## 与知识库的关系 / ## 自测",
        "- 不复制摘要原文、不编造数字或 URL、不使用 --- 分隔线，正文 500-900 字",
        "- 明确区分作者主张与已有共识；摘要级或未复现内容要说明",
        "- stage 选择：基础概念/算法原理用 FOUNDATION；训练系统/评估/安全用 SYSTEMS；前沿未复现用 FRONTIER",
        "",
        "已有笔记 id（related 只能从这里选）:",
        ", ".join(sorted(state["ids"])),
    ])
    card = chat_json(api_key, SYSTEM, user)
    # Validate and normalize.
    for key in ("id", "title", "summary", "stage", "track", "body"):
        if not str(card.get(key) or "").strip():
            raise CardError(f"card missing field: {key}")
    stage = str(card["stage"]).upper()
    card["stage"] = stage if stage in STAGES else "FRONTIER"
    card["track"] = str(card["track"]) if str(card["track"]) in TRACKS else "前沿专题"
    try:
        card["minutes"] = max(10, min(25, int(card.get("minutes") or 15)))
    except (TypeError, ValueError):
        card["minutes"] = 15
    card["tags"] = clean_list(card.get("tags"), 5) or ["paper"]
    card["objectives"] = clean_list(card.get("objectives"), 3)
    card["related"] = [item for item in clean_list(card.get("related"), 3) if item in state["ids"]]
    card["body"] = clean_body(card.get("body"))
    headings = len(re.findall(r"^##\s+", card["body"], re.M))
    if headings < 4 or len(card["body"]) < 300:
        raise CardError(f"card body too thin (headings={headings}, chars={len(card['body'])})")
    card["summary"] = str(card["summary"]).replace(",", "，").strip()[:140]
    card["title"] = str(card["title"]).replace(",", "，").strip()[:60]
    return card


# ---------------------------------------------------------------- writing

def write_card(card: dict[str, Any], paper: dict[str, Any], full: dict[str, Any], state: dict[str, Any], order: int, review_status: str) -> dict[str, Any]:
    note_id = unique_slug(card.get("id") or paper.get("title", ""), state["ids"])
    source_id = unique_slug(paper.get("title") or paper.get("id", ""), state["catalog_ids"])
    authors = list(paper.get("authors") or [])
    year = str(paper.get("published") or "")[:4] or str(dt.datetime.now(dt.timezone.utc).year)
    source = {
        "id": source_id,
        "title": str(paper.get("title") or "").strip(),
        "kind": "论文",
        "author": f"{authors[0]} et al." if authors else "见原文作者列表",
        "year": year,
        "url": str(paper.get("arxivUrl") or f"https://arxiv.org/abs/{paper.get('id')}"),
        "evidence": review_status,
        "note": f"LLM 全文精读草稿：{str(paper.get('reason') or card['summary'])[:160]}",
    }
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    frontmatter = [
        "---",
        f"id: {note_id}",
        f"title: {card['title']}",
        f"summary: {card['summary']}",
        f"stage: {card['stage']}",
        f"track: {card['track']}",
        f"order: {order}",
        f"minutes: {card['minutes']}",
        f"updated: '{today}'",
        f"review: {review_status}",
        "origin: llm-fulltext",
        f"paper_id: {paper.get('id')}",
        "reading_depth: full-text",
        "evidence_level: full-text-llm-draft",
        f"full_text_url: {full['url']}",
        f"objectives: [{', '.join(card['objectives'])}]",
        f"tags: [{', '.join(card['tags'])}]",
        f"sources: [{source_id}]",
        f"related: [{', '.join(card['related'])}]",
        "prerequisites: []",
        "---",
    ]
    note_path = CONTENT / f"{order:02d}-{note_id}.md"
    note_path.write_text("\n".join(frontmatter) + "\n" + card["body"] + "\n", encoding="utf-8")
    catalog = state["catalog"] + [source]
    SOURCES.write_text("[\n" + ",\n".join("  " + json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in catalog) + "\n]\n", encoding="utf-8")
    return {"note_id": note_id, "note_path": str(note_path.relative_to(ROOT)), "source_id": source_id, "title": card["title"], "stage": card["stage"], "minutes": card["minutes"]}


def run(limit: int | None, only: str | None) -> int:
    config = load_config()
    api_key = os.environ.get("DEEPSEEK_V4_FLASH_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_V4_FLASH_API_KEY is required")
    if not RADAR.exists():
        print("cards: no radar.json; run the audit first", file=sys.stderr)
        return 0
    radar = json.loads(RADAR.read_text(encoding="utf-8"))
    state = existing_state()
    candidates = select_candidates(radar, state, limit or config["limit"], config["decisions"], only)
    generated, skipped = [], []
    for paper in candidates:
        paper_id = str(paper.get("id"))
        print(f"cards: fetching full text for {paper_id}", file=sys.stderr, flush=True)
        full = fetch_fulltext(paper_id, config["max_chars"])
        if not full:
            skipped.append({"id": paper_id, "reason": "no full text"})
            continue
        print(f"cards: drafting {paper_id} ({full['chars']} chars)", file=sys.stderr, flush=True)
        try:
            card = draft_card(api_key, paper, full, state)
            result = write_card(card, paper, full, state, state["max_order"] + len(generated) + 1, config["review_status"])
        except CardError as error:
            skipped.append({"id": paper_id, "reason": str(error)})
            continue
        state["ids"].add(result["note_id"])
        state["catalog_ids"].add(result["source_id"])
        generated.append({**result, "arxiv_id": paper_id, "full_text_url": full["url"]})
        time.sleep(2)
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "requested": len(candidates),
        "generated": generated,
        "skipped": skipped,
        "reviewStatus": config["review_status"],
        "publishDirectly": False,
    }
    (CARDS_DIR / "latest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["", "## 自动生成的知识卡", "", f"> LLM 全文精读草稿，需人工复核后才算已审核知识。本次生成 {len(generated)} 张。", ""]
    for item in generated:
        lines += [f"### {item['title']}", f"- 笔记：`content/{item['note_path'].split('/')[-1]}`", f"- 来源：`{item['source_id']}` · arXiv `{item['arxiv_id']}`", f"- 全文：{item['full_text_url']}", ""]
    if skipped:
        lines += ["### 跳过", "", *[f"- `{item['id']}`：{item['reason']}" for item in skipped], ""]
    (CARDS_DIR / "latest.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"generated": len(generated), "skipped": len(skipped), "notes": [item["note_id"] for item in generated]}, ensure_ascii=False))
    return 0


def check() -> int:
    problems = []
    for path in sorted(CONTENT.glob("*.md")):
        data = parse_frontmatter(path)
        if data.get("origin") != "llm-fulltext":
            continue
        for field in ("paper_id", "full_text_url", "evidence_level", "review"):
            if not data.get(field):
                problems.append(f"{path.name}: missing {field}")
        body = path.read_text(encoding="utf-8").split("\n---\n", 1)[-1]
        if len(re.findall(r"^##\s+", body, re.M)) < 4:
            problems.append(f"{path.name}: fewer than 4 sections")
    if problems:
        print("\n".join(f"cards: {item}" for item in problems), file=sys.stderr)
        return 1
    print("cards: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", default="run", choices=["run", "check"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--paper", default=None)
    args = parser.parse_args()
    try:
        return check() if args.command == "check" else run(args.limit, args.paper)
    except (CardError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"cards: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
