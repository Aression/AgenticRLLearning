"use client";
import { Bookmark, Check, Circle } from "lucide-react";
import { useProgress } from "@/lib/progress";
export function ProgressButton({ id }: { id: string }) {
  const progress = useProgress();
  const read = progress.read.includes(id), bookmarked = progress.bookmarks.includes(id);
  return <div className="reading-actions"><button className={`command ${read ? "selected" : ""}`} onClick={() => progress.toggle(id, "read")} aria-pressed={read}>{read ? <Check size={16} /> : <Circle size={16} />}{read ? "已读" : "标记已读"}</button><button className="icon-button" title={bookmarked ? "取消收藏" : "收藏笔记"} aria-label={bookmarked ? "取消收藏" : "收藏笔记"} aria-pressed={bookmarked} onClick={() => progress.toggle(id, "bookmarks")}><Bookmark size={17} fill={bookmarked ? "currentColor" : "none"} /></button>{progress.error && <span role="alert">{progress.error}</span>}</div>;
}
