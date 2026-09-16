export type Stage = "FOUNDATION" | "SYSTEMS" | "FRONTIER";

/** Metadata exported from the content database; no article body. */
export type NoteMeta = {
  id: string;
  title: string;
  summary: string;
  stage: Stage;
  track: string;
  order: number;
  minutes: number;
  updated: string;
  review: string;
  filename: string;
  tags: string[];
  concepts: string[];
  objectives: string[];
  keyPoints: string[];
  sections: string[];
  evidenceLevel: string;
  codeUrl: string;
  related: string[];
  degree: number;
  sources: string[];
  prerequisites: string[];
  search: string;
};

/** Full note, loaded server-side from its own generated JSON file. */
export type Note = NoteMeta & { content: string };

export type Source = {
  id: string;
  title: string;
  kind: string;
  author: string;
  year: string;
  url: string;
  evidence: string;
  note: string;
  checkedAt?: string;
  accessible: boolean;
};

export type GraphNode = {
  id: string;
  label: string;
  kind: "note" | "concept";
  stage: string;
  track: string;
  degree: number;
};

export type GraphEdge = {
  source: string;
  target: string;
  kind: "prerequisite" | "related" | "shared-source" | "shared-concept" | "concept" | string;
  weight: number;
};

export type Graph = { generatedAt?: string; nodes: GraphNode[]; edges: GraphEdge[] };

export type RadarPaper = {
  id: string;
  title: string;
  summary: string;
  published: string;
  url: string;
  arxivUrl: string;
  upvotes: number;
  authors: string[];
  matchedKeywords: string[];
  relevanceScore: number;
  decision: "review" | "archive" | "skip" | string;
  evidenceLevel: string;
  reason: string;
  suggestedNote: string;
};

export type Radar = {
  generatedAt?: string;
  source?: string;
  searchedAt?: string;
  considered?: number;
  selected?: number;
  model?: string | string[];
  summary?: string;
  risks?: string[];
  nextActions?: string[];
  papers: RadarPaper[];
};

export const stageMeta: Record<Stage, { label: string; index: string; color: string; hex: string }> = {
  FOUNDATION: { label: "基础层", index: "01", color: "cyan", hex: "#67ddcb" },
  SYSTEMS: { label: "系统层", index: "02", color: "amber", hex: "#f3c578" },
  FRONTIER: { label: "前沿层", index: "03", color: "rose", hex: "#efa3b5" },
};

export const REPO = "https://github.com/Aression/AgenticRLLearning";
