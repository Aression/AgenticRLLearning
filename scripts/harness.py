#!/usr/bin/env python3
"""Maintenance harness for the Agentic RL Atlas.

Commands are intentionally explicit:
  check   validate content and repository contracts (offline)
  refresh fetch source metadata and arXiv discovery (network, writes audit files)
  report  emit a maintenance report and git diff summary (offline)
  all     run check + report; use --refresh to refresh first
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
SOURCES = ROOT / "data" / "sources.json"
AUDIT = ROOT / "research" / "source-audit.json"
DISCOVERY = ROOT / "research" / "discovery.json"
REPORT_DIR = ROOT / "research" / "reports"
REQUIRED_NOTE = {"id", "title", "summary", "stage", "track", "order", "minutes", "updated", "review", "tags", "sources", "prerequisites"}
STAGES = {"FOUNDATION", "SYSTEMS", "FRONTIER"}
ALLOWED_REVIEW = {"综合笔记", "实验指南", "实验设计 · 未运行 GPU 训练", "摘要核验 · 待精读", "维护规范", "参考索引", "学习路线"}
SOURCE_URL_RE = re.compile(r"https?://[^)\s>]+")
NOTE_LINK_RE = re.compile(r"/notes/([a-z0-9][a-z0-9-]*)(?:[)#?]|$)")


class HarnessError(Exception):
    pass


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise HarnessError(f"{path.relative_to(ROOT)}: frontmatter must start with ---")
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise HarnessError(f"{path.relative_to(ROOT)}: closing frontmatter marker missing")
    data: dict[str, Any] = {}
    for line in parts[0].splitlines()[1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise HarnessError(f"{path.relative_to(ROOT)}: invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key.strip()] = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
        elif value in {"[]", "[ ]"}:
            data[key.strip()] = []
        elif value.isdigit():
            data[key.strip()] = int(value)
        else:
            data[key.strip()] = value.strip("'\"")
    return data, parts[1]


def load_catalog() -> list[dict[str, Any]]:
    try:
        catalog = json.loads(SOURCES.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HarnessError(f"cannot parse {SOURCES.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(catalog, list):
        raise HarnessError("data/sources.json must contain an array")
    return catalog


def load_notes() -> tuple[list[dict[str, Any]], list[str]]:
    notes, errors = [], []
    for path in sorted(CONTENT.glob("*.md")):
        try:
            data, body = parse_frontmatter(path)
            data["filename"], data["body"] = path.name, body
            notes.append(data)
        except HarnessError as exc:
            errors.append(str(exc))
    return notes, errors


def check() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    notes, parse_errors = load_notes()
    errors.extend(parse_errors)
    seen_note_ids: set[str] = set()
    catalog = load_catalog()
    source_id_values = [str(item.get("id")) for item in catalog]
    duplicate_source_ids = sorted({sid for sid in source_id_values if source_id_values.count(sid) > 1})
    errors.extend(f"duplicate source id: {sid}" for sid in duplicate_source_ids)
    source_ids = {str(item.get("id")) for item in catalog}
    source_urls: dict[str, str] = {}
    note_ids: dict[str, str] = {str(note.get("id")): note["filename"] for note in notes if note.get("id")}
    for source in catalog:
        sid, url = source.get("id"), source.get("url")
        if not sid or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(sid)):
            errors.append(f"source has invalid id: {sid!r}")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            errors.append(f"source {sid}: invalid URL")
        elif url in source_urls:
            errors.append(f"duplicate source URL: {url} (also {source_urls[url]})")
        else:
            source_urls[url] = str(sid)
        for field in ("title", "kind", "author", "year", "evidence", "note"):
            if not str(source.get(field, "")).strip():
                errors.append(f"source {sid}: missing {field}")
    for note in notes:
        path = note["filename"]
        nid = note.get("id")
        if not nid or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(nid)):
            errors.append(f"{path}: invalid id {nid!r}")
        elif str(nid) in seen_note_ids:
            errors.append(f"duplicate note id: {nid}")
        else:
            seen_note_ids.add(str(nid))
        missing = REQUIRED_NOTE - note.keys()
        errors.extend(f"{path}: missing frontmatter: {key}" for key in sorted(missing))
        if note.get("stage") not in STAGES:
            errors.append(f"{path}: invalid stage {note.get('stage')!r}")
        if not isinstance(note.get("order"), int) or not isinstance(note.get("minutes"), int):
            errors.append(f"{path}: order and minutes must be integers")
        try:
            dt.date.fromisoformat(str(note.get("updated")))
        except ValueError:
            errors.append(f"{path}: updated must be ISO date")
        if not str(note.get("review", "")):
            errors.append(f"{path}: review is empty")
        refs = note.get("sources") if isinstance(note.get("sources"), list) else []
        for sid in refs:
            if sid not in source_ids:
                errors.append(f"{path}: unknown source id {sid}")
        for prerequisite in note.get("prerequisites", []) if isinstance(note.get("prerequisites"), list) else []:
            if prerequisite not in note_ids and prerequisite != nid:
                warnings.append(f"{path}: prerequisite {prerequisite} is not present in current filename order")
        for target in NOTE_LINK_RE.findall(note.get("body", "")):
            if target not in note_ids and not (CONTENT / f"{target}.md").exists():
                errors.append(f"{path}: broken note link /notes/{target}")
        if not refs:
            warnings.append(f"{path}: no source references")
        if str(note.get("review", "")).endswith("待精读") and note.get("stage") != "FRONTIER":
            warnings.append(f"{path}: preprint review status is outside FRONTIER")
    orders = [note.get("order") for note in notes]
    if len(orders) != len(set(orders)):
        errors.append("content order values must be unique")
    if not AUDIT.exists():
        errors.append("research/source-audit.json is missing; run refresh")
    else:
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        audit_urls = {item.get("url") for item in audit}
        for url in source_urls:
            if url not in audit_urls:
                warnings.append(f"source has no audit record: {url}")
    discovery_stats = {"entries": 0, "duplicate_ids": 0, "empty_titles": 0}
    if DISCOVERY.exists():
        discovery = json.loads(DISCOVERY.read_text(encoding="utf-8")); entries = discovery.get("entries", [])
        ids = [str(entry.get("id")) for entry in entries]
        discovery_stats = {"entries": len(entries), "duplicate_ids": len(ids) - len(set(ids)), "empty_titles": sum(not str(entry.get("title", "")).strip() for entry in entries)}
        if discovery_stats["duplicate_ids"] or discovery_stats["empty_titles"]:
            errors.append(f"discovery quality failure: {discovery_stats}")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "notes": len(notes), "sources": len(catalog), "discovery": discovery_stats, "checkedAt": dt.datetime.now(dt.timezone.utc).isoformat()}


def run_script(name: str) -> None:
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / name)], cwd=ROOT, text=True)
    if result.returncode:
        raise HarnessError(f"{name} exited with {result.returncode}")


def git_summary() -> dict[str, Any]:
    def run(args: list[str]) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()
    return {"branch": run(["branch", "--show-current"]), "status": run(["status", "--short"]), "diffStat": run(["diff", "--stat"]), "head": run(["log", "-1", "--format=%h %s"])}


def report(result: dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {"harness": "agentic-rl-atlas", "version": 1, "result": result, "git": git_summary()}
    json_path = REPORT_DIR / f"maintenance-{stamp}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest = REPORT_DIR / "latest.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return json_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "refresh", "report", "all"])
    parser.add_argument("--refresh", action="store_true", help="for all: refresh source metadata and discovery first")
    parser.add_argument("--json", action="store_true", help="print JSON result")
    args = parser.parse_args()
    try:
        if args.command == "refresh" or (args.command == "all" and args.refresh):
            run_script("research.py")
            run_script("search-papers.py")
        result = check()
        if args.command == "report" or args.command == "all":
            path = report(result)
            result["report"] = str(path.relative_to(ROOT))
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"harness: {'PASS' if result['ok'] else 'FAIL'} | notes={result['notes']} sources={result['sources']} errors={len(result['errors'])} warnings={len(result['warnings'])}")
        if result["errors"] and not args.json:
            print("Errors:"); print("\n".join(f"- {item}" for item in result["errors"]))
        if result["warnings"] and not args.json:
            print("Warnings:"); print("\n".join(f"- {item}" for item in result["warnings"]))
        return 0 if result["ok"] else 1
    except (HarnessError, OSError, json.JSONDecodeError) as exc:
        print(f"harness: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
