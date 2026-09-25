import fs from "node:fs";
import path from "node:path";
import type { Graph, ModelInfo, Note, NoteMeta, Radar, Source } from "./types";

type RawSource = Omit<Source, "accessible" | "checkedAt">;
type AuditRecord = { url: string; status?: number; checkedAt?: string; metadata?: { citation_author?: string[] } };
type NoteIndexFile = { notes: NoteMeta[] } & Partial<ModelInfo>;

let noteIndex: NoteMeta[] | null = null;
let modelInfo: ModelInfo | null = null;
let sourceList: Source[] | null = null;
let graphData: Graph | null = null;
let radarData: Radar | null | undefined;

/** Metadata for every note, read from the generated database export. */
export function getNotes(): NoteMeta[] {
  loadIndex();
  return noteIndex!;
}

/** The content model (evidence rubric, kind and depth labels) exported alongside the notes. */
export function getModelInfo(): ModelInfo {
  loadIndex();
  return modelInfo!;
}

function loadIndex(): void {
  if (noteIndex) return;
  const file = path.join(process.cwd(), "data/generated/notes.index.json");
  const data = JSON.parse(fs.readFileSync(file, "utf8")) as NoteIndexFile;
  noteIndex = [...data.notes].sort((a, b) => a.order - b.order);
  modelInfo = { evidenceRubric: data.evidenceRubric ?? {}, kinds: data.kinds ?? {}, depths: data.depths ?? {} };
}

/** One full note (with body), loaded from its own split JSON file. */
export function getNote(id: string): Note | undefined {
  const file = path.join(process.cwd(), "data/generated/notes", `${id}.json`);
  if (!fs.existsSync(file)) return undefined;
  return JSON.parse(fs.readFileSync(file, "utf8")) as Note;
}

/** Curated sources, enriched with the latest link-audit metadata. */
export function getSources(): Source[] {
  if (!sourceList) {
    const catalog = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data/sources.json"), "utf8")) as RawSource[];
    const audit = JSON.parse(fs.readFileSync(path.join(process.cwd(), "research/source-audit.json"), "utf8")) as AuditRecord[];
    sourceList = catalog.map((source) => {
      const record = audit.find((entry) => entry.url === source.url);
      const authors = record?.metadata?.citation_author;
      const author = source.author === "见原文作者列表" && authors ? `${authors.slice(0, 2).join(" / ")}${authors.length > 2 ? " et al." : ""}` : source.author;
      return { ...source, author, accessible: record?.status === 200, checkedAt: record?.checkedAt?.slice(0, 10) };
    });
  }
  return sourceList;
}

/** Knowledge graph derived from the database (prerequisites, sources, concepts). */
export function getGraph(): Graph {
  if (!graphData) {
    graphData = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data/generated/graph.json"), "utf8")) as Graph;
  }
  return graphData;
}

/** Latest HuggingFace discovery with DeepSeek triage; null before the first audit. */
export function getRadar(): Radar | null {
  if (radarData === undefined) {
    const file = path.join(process.cwd(), "data/generated/radar.json");
    radarData = fs.existsSync(file) ? (JSON.parse(fs.readFileSync(file, "utf8")) as Radar) : null;
  }
  return radarData;
}
