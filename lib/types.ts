export type Stage = "FOUNDATION" | "SYSTEMS" | "FRONTIER";
export type Note = { id: string; title: string; summary: string; stage: Stage; track: string; order: number; minutes: number; updated: string; review: string; tags: string[]; sources: string[]; prerequisites: string[]; content: string; filename: string };
export type Source = { id: string; title: string; kind: string; author: string; year: string; url: string; evidence: string; note: string; checkedAt?: string; accessible: boolean };
export const stageMeta: Record<Stage, { label: string; index: string; color: string }> = {
  FOUNDATION: { label: "基础层", index: "01", color: "cyan" },
  SYSTEMS: { label: "系统层", index: "02", color: "amber" },
  FRONTIER: { label: "前沿层", index: "03", color: "rose" },
};
export const REPO = "https://github.com/Aression/AgenticRLLearning";
