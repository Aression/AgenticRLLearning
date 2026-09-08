import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import catalog from "@/data/sources.json";
import audit from "@/research/source-audit.json";
import type { Note, Source } from "./types";

export function getNotes(): Note[] {
  return fs.readdirSync(path.join(process.cwd(), "content")).filter((file) => file.endsWith(".md")).map((filename) => {
    const { data, content } = matter(fs.readFileSync(path.join(process.cwd(), "content", filename), "utf8"));
    return { ...data, content, filename } as Note;
  }).sort((a, b) => a.order - b.order);
}
export function getSources(): Source[] {
  return catalog.map((source) => {
    const record = audit.find((entry) => entry.url === source.url);
    const authors = record?.metadata?.citation_author;
    return { ...source, author: source.author === "见原文作者列表" && authors ? `${authors.slice(0, 2).join(" / ")}${authors.length > 2 ? " et al." : ""}` : source.author, accessible: record?.status === 200, checkedAt: record?.checkedAt.slice(0, 10) };
  });
}
