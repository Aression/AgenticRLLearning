#!/usr/bin/env python3
"""One-shot, idempotent migration of existing notes into the content model.

Adds ``kind``, ``depth`` and ``evidenceGrade`` to every note that is missing them.
Bodies are never touched. Existing notes enter at ``depth: overview`` so the deeper
contracts only bind new or explicitly promoted notes; ``scripts/cards.py deepen``
promotes thin LLM paper cards to ``depth: deep``.

Usage:
    python scripts/migrate_content_model.py [--apply]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from content_model import EVIDENCE_GRADES, KINDS, DEPTHS  # noqa: E402

CONTENT = ROOT / "content"

LAB_IDS = {"lab-rl", "lab-agent", "lab-agent-rl"}
REFERENCE_IDS = {"glossary", "learning-paths", "maintenance", "frontier-radar"}
SYNTHESIS_TRACKS = {"前沿专题"}
CONCEPT_TRACKS = {"概念与基础", "训练算法"}
SYSTEM_TRACKS = {"Agent 系统", "评估与安全"}


def parse_frontmatter(text: str) -> tuple[list[str], str]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter must start with ---")
    end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    return lines[1:end], "\n".join(lines[end + 1:])


def field(lines: list[str], key: str) -> str:
    prefix = f"{key}:"
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip().strip("'\"")
    return ""


def classify(note_id: str, track: str, origin: str) -> tuple[str, str, str]:
    """Return (kind, depth, evidenceGrade) for a legacy note."""
    if origin == "llm-fulltext":
        return "paper", "overview", "C"
    if note_id in LAB_IDS:
        return "lab", "overview", "D"
    if note_id in REFERENCE_IDS:
        return "reference", "overview", "C"
    if note_id == "orientation":
        return "orientation", "overview", "C"
    if track in SYNTHESIS_TRACKS:
        return "synthesis", "overview", "C"
    if track in CONCEPT_TRACKS:
        return "concept", "overview", "C"
    if track in SYSTEM_TRACKS:
        return "system", "overview", "C"
    return "reference", "overview", "C"


def migrate(apply: bool) -> int:
    changed, skipped = [], []
    for path in sorted(CONTENT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        lines, body = parse_frontmatter(text)
        note_id, track, origin = field(lines, "id"), field(lines, "track"), field(lines, "origin")
        kind, depth, grade = classify(note_id, track, origin)
        additions = []
        if not field(lines, "kind"):
            additions.append(f"kind: {kind}")
        if not field(lines, "depth"):
            additions.append(f"depth: {depth}")
        if not field(lines, "evidenceGrade"):
            additions.append(f"evidenceGrade: {grade}")
        if not additions:
            skipped.append(path.name)
            continue
        insert_at = next((index for index, line in enumerate(lines) if line.startswith("track:")), len(lines) - 1) + 1
        lines[insert_at:insert_at] = additions
        changed.append(f"{path.name}: +{' +'.join(item.split(':')[0] for item in additions)}")
        if apply:
            path.write_text("---\n" + "\n".join(lines) + "\n---\n" + body, encoding="utf-8")
    for item in changed:
        print(item)
    print(f"migrate: {len(changed)} updated, {len(skipped)} already current, apply={apply}")
    if not apply and changed:
        print("migrate: dry run; re-run with --apply to write")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes instead of a dry run")
    args = parser.parse_args()
    for name, values in (("kind", KINDS), ("depth", DEPTHS), ("evidenceGrade", EVIDENCE_GRADES)):
        if not values:
            print(f"migrate: ERROR: empty vocabulary for {name}", file=sys.stderr)
            return 2
    return migrate(args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
