import Link from "next/link";
import { notFound } from "next/navigation";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { ArrowLeft, ArrowRight, ArrowUpRight, ExternalLink, Network } from "lucide-react";
import { getNotes, getSources } from "@/lib/content";
import { REPO, stageMeta } from "@/lib/types";
import { ProgressButton } from "@/components/progress-button";

export function generateStaticParams() { return getNotes().map((note) => ({ id: note.id })); }
export const dynamicParams = false;
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const note = getNotes().find((item) => item.id === id);
  return { title: note ? `${note.title} | Agentic RL Atlas` : "笔记未找到", description: note?.summary };
}
export default async function NotePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const notes = getNotes(), allSources = getSources();
  const note = notes.find((item) => item.id === id);
  if (!note) notFound();
  const index = notes.indexOf(note);
  const backlinks = notes.filter((item) => item.id !== id && (item.prerequisites.includes(id) || item.content.includes(`/notes/${id})`)));
  const headings = note.content.split("\n").filter((line) => line.startsWith("## ")).map((line) => line.slice(3));
  return <div className="reader"><header className="reader-bar"><Link className="brand" href="/"><Network size={19} /><span>AGENTIC RL / ATLAS</span></Link><Link className="text-link" href="/"><ArrowLeft size={15} />知识地图</Link></header><main id="main-content" className="reader-layout"><article className="reader-article"><div className="article-meta"><span className={`stage-label ${stageMeta[note.stage].color}`}>{stageMeta[note.stage].index} / {stageMeta[note.stage].label}</span><span>{note.track}</span><span>{note.minutes} MIN</span></div><h1>{note.title}</h1><p className="article-summary">{note.summary}</p><div className="article-info"><span>更新 {note.updated}</span><span>{note.review}</span></div><ProgressButton id={note.id} />{note.prerequisites.length > 0 && <div className="prerequisites"><strong>先修</strong>{note.prerequisites.map((prerequisite) => <Link href={`/notes/${prerequisite}`} key={prerequisite}>{notes.find((item) => item.id === prerequisite)?.title}<ArrowUpRight size={12} /></Link>)}</div>}<div className="prose"><Markdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]} components={{ h2: ({ children }) => <h2 id={String(children)}>{children}</h2>, table: ({ children }) => <div className="table-scroll"><table>{children}</table></div>, a: ({ href, children }) => href?.startsWith("/") ? <Link href={href}>{children}</Link> : <a href={href} target="_blank" rel="noreferrer">{children}</a> }}>{note.content}</Markdown></div><section className="article-sources" id="references"><h2>引用与延伸阅读</h2>{note.sources.map((sourceId) => { const source = allSources.find((item) => item.id === sourceId)!; return <a key={source.id} href={source.url} target="_blank" rel="noreferrer"><div><strong>{source.title}</strong><span>{source.author} · {source.year} · {source.evidence}</span></div><ExternalLink size={14} /></a>; })}</section><div className="article-navigation">{index > 0 && <Link href={`/notes/${notes[index - 1].id}`}><small><ArrowLeft size={13} />上一篇</small>{notes[index - 1].title}</Link>}{index < notes.length - 1 && <Link href={`/notes/${notes[index + 1].id}`}><small>下一篇<ArrowRight size={13} /></small>{notes[index + 1].title}</Link>}</div></article><aside className="reader-aside"><p className="nav-label">ON THIS PAGE</p><nav aria-label="文章目录">{headings.map((heading) => <a href={`#${heading}`} key={heading}>{heading}</a>)}<a href="#references">引用与延伸阅读</a></nav><div className="sidebar-divider" /><p className="nav-label">BACKLINKS / {backlinks.length}</p>{backlinks.map((item) => <Link className="backlink" href={`/notes/${item.id}`} key={item.id}>{item.title}<ArrowUpRight size={11} /></Link>)}<a className="edit-link" href={`${REPO}/edit/main/content/${note.filename}`} target="_blank" rel="noreferrer">编辑这篇笔记<ArrowUpRight size={12} /></a></aside></main></div>;
}
