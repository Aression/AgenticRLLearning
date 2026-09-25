#!/usr/bin/env python3
"""Content model for the Agentic RL Atlas.

This module is the single source of truth for the knowledge-base structure:

* ``kind``    — what a note *is* (orientation, concept, system, paper, synthesis, lab, reference)
* ``depth``   — how much reading investment a note represents (overview, working, deep)
* contracts  — the per-(kind, depth) section/length/claims requirements a note must satisfy
* grades     — the evidence rubric used on every note and every claim

``scripts/harness.py`` validates notes against the contracts, ``scripts/atlas_db.py``
exports the fields for the site, and ``scripts/cards.py`` generates deep cards that
satisfy them. Keeping the schema here means the three consumers cannot drift apart.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

STAGES = ("FOUNDATION", "SYSTEMS", "FRONTIER")
KINDS = ("orientation", "concept", "system", "paper", "synthesis", "lab", "reference")
DEPTHS = ("overview", "working", "deep")
EVIDENCE_GRADES = ("A", "B", "C", "D")
CLAIM_STATUSES = ("作者主张", "与共识一致", "已复现", "存疑")

KIND_LABELS = {
    "orientation": "导航",
    "concept": "概念",
    "system": "系统",
    "paper": "论文精读",
    "synthesis": "专题综述",
    "lab": "实验",
    "reference": "索引",
}
DEPTH_LABELS = {"overview": "概览", "working": "工作级", "deep": "深读"}
DEPTH_ORDER = {"overview": 0, "working": 1, "deep": 2}

# Evidence rubric. The grade describes the *strongest* support behind the note's claims.
EVIDENCE_RUBRIC = {
    "A": "有多处独立证据或本地复现支撑；结论已交叉验证",
    "B": "全文精读且方法、实验设置、代码或数据可核验；未复现",
    "C": "全文级阅读，但结论依赖单一来源的作者自述，未经人工复核",
    "D": "仅摘要、元数据或未运行的计划；不得当作已确证结论",
}


@dataclass(frozen=True)
class Contract:
    """Requirements a note of a given (kind, depth) must satisfy."""

    min_chars: int = 600
    min_sections: int = 3
    required_sections: tuple[str, ...] = ()
    section_min_chars: int = 0
    min_claims: int = 0
    min_related: int = 0
    require_evidence_grade: bool = True
    require_self_test: bool = False


# Section names are matched as substrings of the ``##`` heading, so
# "## 核心主张与证据" satisfies the "核心主张" requirement.
PAPER_DEEP = (
    "问题与语境",
    "核心主张",
    "机制与方法",
    "实验设置",
    "证据与结果",
    "证据强度评估",
    "边界与反例",
    "与知识库的关系",
    "复现与验证计划",
    "术语与记号",
    "自测",
)
CONCEPT_DEEP = (
    "定义与边界",
    "机制",
    "形式化",
    "例子与反例",
    "常见误解",
    "与知识库的关系",
    "自测",
)
SYSTEM_DEEP = (
    "问题与约束",
    "组成与数据流",
    "关键设计取舍",
    "失效模式",
    "度量与诊断",
    "与知识库的关系",
    "验证计划",
    "自测",
)
SYNTHESIS_DEEP = (
    "问题与范围",
    "证据地图",
    "共识与分歧",
    "机制对比",
    "迁移条件",
    "开放问题",
    "与知识库的关系",
    "自测",
)
LAB_DEEP = (
    "假设与可反驳预测",
    "冻结协议",
    "结果与原始计数",
    "失败与异常",
    "成本",
    "结论边界",
    "下一步",
    "自测",
)
ORIENTATION_DEEP = (
    "范围与读者",
    "知识地图",
    "阅读顺序",
    "常见误区",
    "与知识库的关系",
    "自测",
)
REFERENCE_DEEP = (
    "用途",
    "使用方式",
    "维护约定",
    "与知识库的关系",
)

CONTRACTS: dict[tuple[str, str], Contract] = {
    # Deep tiers: the target architecture. Each deep card must state claims,
    # support them with located evidence, grade the evidence, and link outward.
    ("paper", "deep"): Contract(min_chars=4500, min_sections=9, required_sections=PAPER_DEEP, section_min_chars=150, min_claims=3, min_related=2, require_self_test=True),
    ("concept", "deep"): Contract(min_chars=3200, min_sections=6, required_sections=CONCEPT_DEEP, section_min_chars=150, min_related=2, require_self_test=True),
    ("system", "deep"): Contract(min_chars=3200, min_sections=6, required_sections=SYSTEM_DEEP, section_min_chars=150, min_related=2, require_self_test=True),
    ("synthesis", "deep"): Contract(min_chars=3600, min_sections=6, required_sections=SYNTHESIS_DEEP, section_min_chars=150, min_claims=3, min_related=3, require_self_test=True),
    ("lab", "deep"): Contract(min_chars=2400, min_sections=6, required_sections=LAB_DEEP, section_min_chars=120, min_related=1, require_self_test=True),
    ("orientation", "deep"): Contract(min_chars=2400, min_sections=5, required_sections=ORIENTATION_DEEP, section_min_chars=120, min_related=3, require_self_test=True),
    ("reference", "deep"): Contract(min_chars=2000, min_sections=4, required_sections=REFERENCE_DEEP, section_min_chars=120, min_related=2),
    # Working tier: a real note with a defined structure but no claim table yet.
    ("paper", "working"): Contract(min_chars=1800, min_sections=5, min_related=1),
    ("concept", "working"): Contract(min_chars=1400, min_sections=4, min_related=1, require_self_test=True),
    ("system", "working"): Contract(min_chars=1400, min_sections=4, min_related=1),
    ("synthesis", "working"): Contract(min_chars=1600, min_sections=4, min_related=2),
    ("lab", "working"): Contract(min_chars=1000, min_sections=4),
    ("orientation", "working"): Contract(min_chars=1200, min_sections=4, min_related=1),
    ("reference", "working"): Contract(min_chars=800, min_sections=3),
    # Overview tier: the grandfather tier. Existing notes live here until deepened.
    ("_default", "overview"): Contract(min_chars=500, min_sections=3),
    ("_default", "working"): Contract(min_chars=1200, min_sections=4),
}

DEFAULT_CONTRACT = Contract()


def contract_for(kind: str, depth: str) -> Contract:
    """Resolve the contract for a note, falling back to the kind/global default."""
    return CONTRACTS.get((kind, depth)) or CONTRACTS.get(("_default", depth)) or DEFAULT_CONTRACT


HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.M)
CLAIM_HEADING_RE = re.compile(r"^#{2,3}\s+.*(主张|证据地图|共识).*$", re.M)


def sections(body: str) -> list[tuple[str, str]]:
    """Split a note body into (heading, section text) pairs on ``##``/``###`` headings."""
    matches = list(HEADING_RE.finditer(body))
    result = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result.append((match.group(2).strip(), body[start:end].strip()))
    return result


def section_titles(body: str) -> list[str]:
    return [title for title, _ in sections(body)]


def section_sizes(body: str) -> dict[str, int]:
    return {title: len(text) for title, text in sections(body)}


def section_text(body: str, needle: str) -> str:
    """Text of the first section whose heading contains ``needle``."""
    for title, text in sections(body):
        if needle in title:
            return text
    return ""


def _table_rows(block: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        rows.append(cells)
    return rows


def parse_claims(body: str) -> list[dict[str, str]]:
    """Extract the claim table from a deep card.

    Canonical form (extra columns are allowed and preserved positionally)::

        | # | 主张 | 证据 | 状态 |
        | --- | --- | --- | --- |
        | C1 | ... | §5 表 2 | 作者主张 |
    """
    heading = CLAIM_HEADING_RE.search(body)
    if not heading:
        return []
    block = body[heading.end():]
    next_heading = re.search(r"^#{2,3}\s+", block, re.M)
    if next_heading:
        block = block[: next_heading.start()]
    rows = _table_rows(block)
    if len(rows) < 2:
        return []
    claims: list[dict[str, str]] = []
    for row in rows[1:]:
        if len(row) < 4:
            continue
        claims.append({"id": row[0], "claim": row[1], "evidence": row[2], "status": row[3]})
    return claims


def invalid_claim_statuses(claims: list[dict[str, str]]) -> list[str]:
    return sorted({claim["status"] for claim in claims if claim["status"] not in CLAIM_STATUSES})


def normalize_heading(title: str) -> str:
    return re.sub(r"[\s:：、，,。.]+", "", title)


def check_structure(kind: str, depth: str, body: str, *, related_count: int = 0, has_evidence_grade: bool = True) -> list[str]:
    """Return a list of contract violations for a note body (empty means compliant)."""
    contract = contract_for(kind, depth)
    problems: list[str] = []
    sizes = section_sizes(body)
    normalized = {normalize_heading(title): size for title, size in sizes.items()}
    if len(sizes) < contract.min_sections:
        problems.append(f"needs at least {contract.min_sections} sections, found {len(sizes)}")
    if len(body.strip()) < contract.min_chars:
        problems.append(f"needs at least {contract.min_chars} chars, found {len(body.strip())}")
    for required in contract.required_sections:
        needle = normalize_heading(required)
        match = next((key for key in normalized if needle in key), None)
        if match is None:
            problems.append(f"missing required section: {required}")
        elif contract.section_min_chars and normalized[match] < contract.section_min_chars:
            problems.append(f"section too thin: {required} ({normalized[match]} < {contract.section_min_chars} chars)")
    claims = parse_claims(body)
    if contract.min_claims:
        if len(claims) < contract.min_claims:
            problems.append(f"needs at least {contract.min_claims} claim rows, found {len(claims)}")
        bad = invalid_claim_statuses(claims)
        if bad:
            problems.append(f"invalid claim status: {', '.join(bad)} (allowed: {'、'.join(CLAIM_STATUSES)})")
        if claims and any(not claim["evidence"].strip() for claim in claims):
            problems.append("claim rows must cite evidence for each claim")
    if contract.min_related and related_count < contract.min_related:
        problems.append(f"needs at least {contract.min_related} related notes, found {related_count}")
    if contract.require_self_test and not any("自测" in key for key in normalized):
        problems.append("missing required section: 自测")
    if contract.require_evidence_grade and not has_evidence_grade:
        problems.append("missing evidenceGrade")
    return problems


NUMERIC_RE = re.compile(r"-?\d+(?:\.\d+)?%?")
# Structural references the model is *required* to write ("§4.2 表 2", "Table 3", "C1")
# are not data values; flagging them as ungrounded numbers would be a false positive.
STRUCTURAL_REF_RE = re.compile(
    r"(?:§+|第|表|图|附录|节|步)\s*[A-Za-z]?\d+(?:\.\d+)*"
    r"|(?:Table|Figure|Fig\.?|Appendix|Section|Sec\.?|Eq\.?|Algorithm)\s*[A-Za-z]?\d+(?:\.\d+)*"
    r"|\b[A-Z]{1,4}\d+(?:\.\d+)?\b"
)
IGNORED_NUMBERS = {"1", "2", "3", "4", "5", "0", "1.", "2.", "3."}


def substantive_numbers(text: str) -> list[str]:
    """Numbers worth grounding: decimals, percentages and integers >= 100.

    Bare small integers are dropped because they are usually list markers, component
    counts or model sizes rather than reported results; structural references are
    stripped first (see ``STRUCTURAL_REF_RE``).
    """
    cleaned = STRUCTURAL_REF_RE.sub(" ", text)
    found: list[str] = []
    for raw in NUMERIC_RE.findall(cleaned):
        token = raw.rstrip(".")
        digits = token.rstrip("%")
        if token in IGNORED_NUMBERS or digits in IGNORED_NUMBERS:
            continue
        if "." not in digits and "%" not in token:
            try:
                if abs(int(digits)) < 100:
                    continue
            except ValueError:
                continue
        if token not in found:
            found.append(token)
    return found


def ungrounded_numbers(body: str, excerpt: str, *, limit: int = 40) -> list[str]:
    """Substantive numbers in the draft that do not appear in the source excerpt.

    A cheap, deterministic hallucination guard for LLM-generated cards. Structural
    references (section/table/figure numbers, claim ids) are ignored, and only
    decimals, percentages and integers >= 100 are treated as claims about results.
    """
    haystack = excerpt.replace(",", "").replace("，", "")
    suspected: list[str] = []
    for token in substantive_numbers(body):
        candidates = {token, token.replace("%", ""), token.replace(",", "")}
        if any(candidate and candidate in haystack for candidate in candidates):
            continue
        suspected.append(token)
        if len(suspected) >= limit:
            break
    return suspected
