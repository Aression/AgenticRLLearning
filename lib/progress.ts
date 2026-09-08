"use client";
import { useSyncExternalStore } from "react";
type Progress = { version: 1; read: string[]; bookmarks: string[] };
const key = "agentic-rl-atlas:progress:v1";
const empty = '{"version":1,"read":[],"bookmarks":[]}';
let warning = "";
const listeners = new Set<() => void>();
function notify() { listeners.forEach((fn) => fn()); }
function snapshot() { try { return localStorage.getItem(key) ?? empty; } catch { return empty; } }
function parse(value: string): Progress {
  try {
    const data = JSON.parse(value);
    if (data.version === 1 && Array.isArray(data.read) && data.read.every((x: unknown) => typeof x === "string") && Array.isArray(data.bookmarks) && data.bookmarks.every((x: unknown) => typeof x === "string")) return data;
  } catch { /* Invalid local data is ignored; imports report errors. */ }
  return JSON.parse(empty);
}
function subscribe(fn: () => void) { listeners.add(fn); window.addEventListener("storage", fn); return () => { listeners.delete(fn); window.removeEventListener("storage", fn); }; }
function save(data: Progress) {
  try { localStorage.setItem(key, JSON.stringify(data)); warning = ""; } catch { warning = "浏览器存储不可用，进度未保存。"; }
  notify();
}
export function useProgress() {
  const raw = useSyncExternalStore(subscribe, snapshot, () => empty);
  const error = useSyncExternalStore(subscribe, () => warning, () => "");
  return {
    ...parse(raw), error,
    toggle(id: string, field: "read" | "bookmarks") {
      const current = parse(snapshot()); const values = new Set(current[field]);
      if (values.has(id)) values.delete(id); else values.add(id);
      save({ ...current, [field]: [...values] });
    },
    exportData() {
      const url = URL.createObjectURL(new Blob([JSON.stringify(parse(snapshot()), null, 2)], { type: "application/json" }));
      const anchor = document.createElement("a"); anchor.href = url; anchor.download = "agentic-rl-progress.json"; anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    },
    importData(text: string, allowed: string[]) {
      const value = JSON.parse(text);
      if (!value || value.version !== 1 || !Array.isArray(value.read) || !Array.isArray(value.bookmarks) || [...value.read, ...value.bookmarks].some((id) => typeof id !== "string")) throw new Error("不是有效的 Atlas 进度文件。");
      const current = parse(snapshot());
      save({ version: 1, read: [...new Set([...current.read, ...value.read])].filter((id) => allowed.includes(id)), bookmarks: [...new Set([...current.bookmarks, ...value.bookmarks])].filter((id) => allowed.includes(id)) });
    },
  };
}
