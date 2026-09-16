#!/usr/bin/env python3
"""Atlas content database.

Markdown notes stay the human-editable format, but they are imported into a
normalized SQLite database (data/atlas.db) that owns the catalog, the concept
tags and the knowledge graph. The database exports small, split JSON files that
the Next.js app imports at build time, so the app never has to carry one giant
generated TypeScript/JSON blob.

Usage:
    python scripts/atlas_db.py build     # import markdown/sources, derive graph, export JSON
    python scripts/atlas_db.py graph     # print graph statistics
    python scripts/atlas_db.py check     # fail if exports are missing or DB is stale
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
SOURCES = ROOT / "data" / "sources.json"
DB = ROOT / "data" / "atlas.db"
GENERATED = ROOT / "data" / "generated"
NOTES_DIR = GENERATED / "notes"
INDEX = GENERATED / "notes.index.json"
GRAPH = GENERATED / "graph.json"
GEN_SOURCES = GENERATED / "sources.json"

REQUIRED_NOTE = {"id", "title", "summary", "stage", "track", "order", "minutes", "updated", "review", "tags", "sources", "prerequisites"}
STAGES = {"FOUNDATION", "SYSTEMS", "FRONTIER"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  stage TEXT NOT NULL,
  track TEXT NOT NULL,
  "order" INTEGER NOT NULL,
  minutes INTEGER NOT NULL,
  updated TEXT NOT NULL,
  review TEXT NOT NULL,
  content TEXT NOT NULL,
  filename TEXT NOT NULL,
  objectives TEXT NOT NULL DEFAULT '[]',
  key_points TEXT NOT NULL DEFAULT '[]',
  evidence_level TEXT NOT NULL DEFAULT '',
  code_url TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  kind TEXT NOT NULL,
  author TEXT NOT NULL,
  year TEXT NOT NULL,
  url TEXT NOT NULL,
  evidence TEXT NOT NULL,
  note TEXT NOT NULL,
  position INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS note_sources (
  note_id TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  PRIMARY KEY (note_id, source_id)
);
CREATE TABLE IF NOT EXISTS note_prerequisites (
  note_id TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  prereq_id TEXT NOT NULL,
  position INTEGER NOT NULL,
  PRIMARY KEY (note_id, prereq_id)
);
CREATE TABLE IF NOT EXISTS concepts (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS note_concepts (
  note_id TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  PRIMARY KEY (note_id, concept_id)
);
CREATE TABLE IF NOT EXISTS relations (
  source_id TEXT NOT NULL,
  target_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  weight REAL NOT NULL DEFAULT 1,
  PRIMARY KEY (source_id, target_id, kind)
);
CREATE INDEX IF NOT EXISTS idx_note_sources_source ON note_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id);
"""


class AtlasError(Exception):
    pass


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AtlasError(f"{path.name}: frontmatter must start with ---")
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise AtlasError(f"{path.name}: closing frontmatter marker missing")
    data: dict[str, Any] = {}
    for line in parts[0].splitlines()[1:]:
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key.strip()] = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
        elif value.isdigit():
            data[key.strip()] = int(value)
        else:
            data[key.strip()] = value.strip("'\"")
    return data, parts[1]


def concept_id(label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return slug or "concept"


def section_points(body: str) -> list[str]:
    return [line[3:].strip() for line in body.splitlines() if line.startswith("## ")]


def load_notes() -> list[dict[str, Any]]:
    notes = []
    for path in sorted(CONTENT.glob("*.md")):
        data, body = parse_frontmatter(path)
        missing = REQUIRED_NOTE - data.keys()
        if missing:
            raise AtlasError(f"{path.name}: missing frontmatter {sorted(missing)}")
        if data["stage"] not in STAGES:
            raise AtlasError(f"{path.name}: invalid stage {data['stage']!r}")
        data.update(
            content=body.strip(),
            filename=path.name,
            objectives=data.get("objectives", []),
            key_points=section_points(body),
            evidence_level=str(data.get("evidence_level", "")),
            code_url=str(data.get("code_url", "")),
        )
        notes.append(data)
    return notes


def load_sources() -> list[dict[str, Any]]:
    catalog = json.loads(SOURCES.read_text(encoding="utf-8"))
    if not isinstance(catalog, list):
        raise AtlasError("data/sources.json must contain an array")
    return catalog


def build_tables(connection: sqlite3.Connection, notes: list[dict[str, Any]], sources: list[dict[str, Any]]) -> None:
    connection.executescript(SCHEMA)
    for table in ("note_sources", "note_prerequisites", "note_concepts", "relations", "concepts", "notes", "sources"):
        connection.execute(f"DELETE FROM {table}")
    for position, source in enumerate(sources):
        connection.execute(
            "INSERT INTO sources (id,title,kind,author,year,url,evidence,note,position) VALUES (?,?,?,?,?,?,?,?,?)",
            (source.get("id"), source.get("title", ""), source.get("kind", ""), source.get("author", ""), str(source.get("year", "")), source.get("url", ""), source.get("evidence", ""), source.get("note", ""), position),
        )
    concepts: set[str] = set()
    for note in notes:
        connection.execute(
            'INSERT INTO notes (id,title,summary,stage,track,"order",minutes,updated,review,content,filename,objectives,key_points,evidence_level,code_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (note["id"], note["title"], note["summary"], note["stage"], note["track"], note["order"], note["minutes"], note["updated"], note["review"], note["content"], note["filename"], json.dumps(note["objectives"], ensure_ascii=False), json.dumps(note["key_points"], ensure_ascii=False), note["evidence_level"], note["code_url"]),
        )
        for position, source_id in enumerate(note.get("sources", [])):
            connection.execute("INSERT OR REPLACE INTO note_sources (note_id,source_id,position) VALUES (?,?,?)", (note["id"], source_id, position))
        for position, prereq in enumerate(note.get("prerequisites", [])):
            connection.execute("INSERT OR REPLACE INTO note_prerequisites (note_id,prereq_id,position) VALUES (?,?,?)", (note["id"], prereq, position))
        for tag in note.get("tags", []) + note.get("concepts", []):
            concepts.add(tag)
            connection.execute("INSERT OR IGNORE INTO concepts (id,label) VALUES (?,?)", (concept_id(tag), tag))
            connection.execute("INSERT OR IGNORE INTO note_concepts (note_id,concept_id) VALUES (?,?)", (note["id"], concept_id(tag)))
    connection.commit()


def derive_relations(connection: sqlite3.Connection) -> None:
    note_ids = [row[0] for row in connection.execute("SELECT id FROM notes")]
    # Prerequisite edges (prerequisite -> note).
    for note_id, prereq_id in connection.execute("SELECT note_id, prereq_id FROM note_prerequisites"):
        connection.execute("INSERT OR REPLACE INTO relations (source_id,target_id,kind,weight) VALUES (?,?,?,?)", (prereq_id, note_id, "prerequisite", 1.0))
    # Explicit related edges from frontmatter.
    for path in sorted(CONTENT.glob("*.md")):
        data, _ = parse_frontmatter(path)
        for related in data.get("related", []):
            pair = tuple(sorted((data["id"], related)))
            connection.execute("INSERT OR REPLACE INTO relations (source_id,target_id,kind,weight) VALUES (?,?,?,?)", (pair[0], pair[1], "related", 1.0))
    # Similarity edges from shared sources and shared concepts (skip existing pairs).
    pairs: set[tuple[str, str]] = set()
    for kind, query in (
        ("shared-source", "SELECT a.note_id, b.note_id FROM note_sources a JOIN note_sources b ON a.source_id=b.source_id AND a.note_id < b.note_id"),
        ("shared-concept", "SELECT a.note_id, b.note_id FROM note_concepts a JOIN note_concepts b ON a.concept_id=b.concept_id AND a.note_id < b.note_id"),
    ):
        weights: dict[tuple[str, str], int] = {}
        for a, b in connection.execute(query):
            weights[(a, b)] = weights.get((a, b), 0) + 1
        for (a, b), weight in weights.items():
            if (a, b) in pairs:
                continue
            pairs.add((a, b))
            connection.execute("INSERT OR REPLACE INTO relations (source_id,target_id,kind,weight) VALUES (?,?,?,?)", (a, b, kind, float(weight)))
    connection.commit()


def export(connection: sqlite3.Connection) -> dict[str, int]:
    GENERATED.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    for stale in NOTES_DIR.glob("*.json"):
        stale.unlink()
    note_rows = connection.execute('SELECT id,title,summary,stage,track,"order",minutes,updated,review,content,filename,objectives,key_points,evidence_level,code_url FROM notes ORDER BY "order"').fetchall()
    node_rows = connection.execute("SELECT id,label FROM concepts ORDER BY id").fetchall()
    degree: dict[str, int] = {row[0]: 0 for row in note_rows}
    for source_id, target_id in connection.execute("SELECT source_id,target_id FROM relations"):
        if source_id in degree:
            degree[source_id] += 1
        if target_id in degree:
            degree[target_id] += 1
    index_notes = []
    for row in note_rows:
        (note_id, title, summary, stage, track, order, minutes, updated, review, content, filename, objectives, key_points, evidence_level, code_url) = row
        concepts = [label for (label,) in connection.execute("SELECT c.label FROM note_concepts nc JOIN concepts c ON c.id=nc.concept_id WHERE nc.note_id=? ORDER BY c.label", (note_id,))]
        neighbours = connection.execute("SELECT target_id, weight FROM relations WHERE source_id=? AND kind != 'prerequisite' UNION SELECT source_id, weight FROM relations WHERE target_id=? AND kind != 'prerequisite'", (note_id, note_id)).fetchall()
        related = [neighbour for neighbour, _ in sorted(neighbours, key=lambda row: (-row[1], row[0])) if neighbour != note_id][:6]
        meta = {
            "id": note_id, "title": title, "summary": summary, "stage": stage, "track": track,
            "order": order, "minutes": minutes, "updated": updated, "review": review,
            "filename": filename, "tags": concepts, "concepts": concepts,
            "objectives": json.loads(objectives), "keyPoints": json.loads(key_points),
            "evidenceLevel": evidence_level, "codeUrl": code_url,
            "sections": json.loads(key_points), "related": related, "degree": degree.get(note_id, 0),
        }
        meta["sources"] = [source_id for (source_id,) in connection.execute("SELECT source_id FROM note_sources WHERE note_id=? ORDER BY position", (note_id,))]
        meta["prerequisites"] = [prereq for (prereq,) in connection.execute("SELECT prereq_id FROM note_prerequisites WHERE note_id=? ORDER BY position", (note_id,))]
        meta["search"] = " ".join([title, summary, track, " ".join(concepts), " ".join(meta["objectives"]), " ".join(meta["keyPoints"])]).lower()
        index_notes.append(meta)
        (NOTES_DIR / f"{note_id}.json").write_text(json.dumps({**meta, "content": content}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    INDEX.write_text(json.dumps({"generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(), "notes": index_notes}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sources = [
        {"id": row[0], "title": row[1], "kind": row[2], "author": row[3], "year": row[4], "url": row[5], "evidence": row[6], "note": row[7]}
        for row in connection.execute("SELECT id,title,kind,author,year,url,evidence,note FROM sources ORDER BY position")
    ]
    GEN_SOURCES.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    nodes = [{"id": row[0], "label": row[1], "kind": "note", "stage": next(n["stage"] for n in index_notes if n["id"] == row[0]), "track": next(n["track"] for n in index_notes if n["id"] == row[0]), "degree": degree.get(row[0], 0)} for row in note_rows]
    nodes += [{"id": row[0], "label": row[1], "kind": "concept", "stage": "", "track": "", "degree": 0} for row in node_rows]
    note_concept_edges = [{"source": a, "target": b, "kind": "concept", "weight": 1} for a, b in connection.execute("SELECT note_id, concept_id FROM note_concepts")]
    relation_edges = [{"source": a, "target": b, "kind": kind, "weight": weight} for a, b, kind, weight in connection.execute("SELECT source_id,target_id,kind,weight FROM relations ORDER BY kind, source_id, target_id")]
    GRAPH.write_text(json.dumps({"generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(), "nodes": nodes, "edges": relation_edges + note_concept_edges}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"notes": len(index_notes), "concepts": len(node_rows), "relations": len(relation_edges), "sources": len(sources)}


def build() -> dict[str, int]:
    notes, sources = load_notes(), load_sources()
    DB.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB)
    try:
        build_tables(connection, notes, sources)
        derive_relations(connection)
        return export(connection)
    finally:
        connection.close()


def check() -> int:
    required = [DB, INDEX, GRAPH, GEN_SOURCES]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print(f"atlas_db: missing {missing}; run build", file=sys.stderr)
        return 2
    notes = load_notes()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    exported = {note["id"] for note in index["notes"]}
    expected = {note["id"] for note in notes}
    if exported != expected:
        print(f"atlas_db: generated notes out of date (missing {sorted(expected - exported)}, extra {sorted(exported - expected)})", file=sys.stderr)
        return 1
    connection = sqlite3.connect(DB)
    try:
        stored = {row[0]: row[1] for row in connection.execute("SELECT id, content FROM notes")}
    finally:
        connection.close()
    for note in notes:
        if stored.get(note["id"]) != note["content"]:
            print(f"atlas_db: DB content stale for {note['id']}; run build", file=sys.stderr)
            return 1
    print(f"atlas_db: OK · {len(notes)} notes · {len(index['notes'])} exported")
    return 0


def graph_stats() -> int:
    if not GRAPH.exists():
        print("atlas_db: no graph; run build", file=sys.stderr)
        return 2
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    kinds: dict[str, int] = {}
    for edge in graph["edges"]:
        kinds[edge["kind"]] = kinds.get(edge["kind"], 0) + 1
    print(json.dumps({"nodes": len(graph["nodes"]), "noteNodes": sum(n["kind"] == "note" for n in graph["nodes"]), "conceptNodes": sum(n["kind"] == "concept" for n in graph["nodes"]), "edges": kinds}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "check", "graph"])
    args = parser.parse_args()
    try:
        if args.command == "build":
            print(json.dumps(build(), ensure_ascii=False))
            return 0
        if args.command == "check":
            return check()
        return graph_stats()
    except (AtlasError, sqlite3.Error, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"atlas_db: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
