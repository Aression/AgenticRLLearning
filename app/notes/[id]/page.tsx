import Link from "next/link";
import { notFound } from "next/navigation";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { ArrowLeft, ArrowRight, ArrowUpRight, ExternalLink, Network } from "lucide-react";
import { getModelInfo, getNote, getNotes, getSources } from "@/lib/content";
import { REPO, stageMeta, type NoteMeta } from "@/lib/types";
import { ProgressButton } from "@/components/progress-button";

export function generateStaticParams() {
  return getNotes().map((note) => ({ id: note.id }));
}
export const dynamicParams = false;

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const note = getNotes().find((item) => item.id === id);
  return { title: note ? `${note.title} | Agentic RL Atlas` : "笔记未找到", description: note?.summary };
}

export default async function NotePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const notes = getNotes();
  const allSources = getSources();
  const modelInfo = getModelInfo();
  const note = getNote(id);
  if (!note) notFound();
  const index = notes.findIndex((item) => item.id === id);
  const backlinks = notes.filter((item) => item.id !== id && (item.prerequisites.includes(id) || item.related.includes(id)));
  const headings = note.keyPoints.length > 0 ? note.keyPoints : note.sections;
  const related = note.related.map((relatedId) => notes.find((item) => item.id === relatedId)).filter((item): item is NoteMeta => Boolean(item));

  return (
    <div className="reader">
      <header className="reader-bar">
        <Link className="brand" href="/"><Network size={19} /><span>AGENTIC RL / ATLAS</span></Link>
        <Link className="text-link" href="/"><ArrowLeft size={15} />知识地图</Link>
      </header>
      <main id="main-content" className="reader-layout">
        <article className="reader-article">
          <div className="article-meta">
            <span className={`stage-label ${stageMeta[note.stage].color}`}>{stageMeta[note.stage].index} / {stageMeta[note.stage].label}</span>
            <span>{note.track}</span>
            <span>{note.kindLabel}</span>
            <span className={note.deep ? "stage-label cyan" : ""}>{note.depthLabel}{note.deep ? "深读" : ""}</span>
            <span title={modelInfo.evidenceRubric[note.evidenceGrade]}>证据 {note.evidenceGrade}</span>
            <span>{note.minutes} MIN</span>
            {note.evidenceLevel && <span>{note.evidenceLevel}</span>}
            {note.origin === "llm-fulltext" && <span className="stage-label rose">LLM 全文精读草稿 · 待人工复核</span>}
          </div>
          <h1>{note.title}</h1>
          <p className="article-summary">{note.summary}</p>
          <div className="article-info"><span>更新 {note.updated}</span><span>{note.review}</span><span>图谱度 {note.degree}</span></div>
          <ProgressButton id={note.id} />
          <section className="article-dossier">
            <h2>档案信息</h2>
            <div className="dossier-grid">
              <div><span>类型</span><strong>{note.kindLabel}</strong></div>
              <div><span>深度</span><strong>{note.depthLabel}{note.claimCount > 0 ? ` · ${note.claimCount} 条主张` : ""}</strong></div>
              <div><span>证据分级</span><strong>{note.evidenceGrade}</strong><small>{modelInfo.evidenceRubric[note.evidenceGrade]}</small></div>
              <div><span>正文规模</span><strong>{note.bodyChars} 字</strong><small>{note.keyPoints.length} 个小节</small></div>
            </div>
          </section>
          {note.objectives.length > 0 && (
            <section className="article-objectives">
              <h2>读完你能</h2>
              <ul>{note.objectives.map((objective) => <li key={objective}>{objective}</li>)}</ul>
            </section>
          )}
          {note.keyPoints.length > 0 && (
            <section className="article-keypoints">
              <h2>本页要点</h2>
              <ol>{note.keyPoints.map((point) => <li key={point}><a href={`#${point}`}>{point}</a></li>)}</ol>
            </section>
          )}
          {note.prerequisites.length > 0 && (
            <div className="prerequisites">
              <strong>先修</strong>
              {note.prerequisites.map((prerequisite) => <Link href={`/notes/${prerequisite}`} key={prerequisite}>{notes.find((item) => item.id === prerequisite)?.title}<ArrowUpRight size={12} /></Link>)}
            </div>
          )}
          <div className="prose">
            <Markdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]} components={{ h2: ({ children }) => <h2 id={String(children)}>{children}</h2>, table: ({ children }) => <div className="table-scroll"><table>{children}</table></div>, a: ({ href, children }) => href?.startsWith("/") ? <Link href={href}>{children}</Link> : <a href={href} target="_blank" rel="noreferrer">{children}</a> }}>{note.content}</Markdown>
          </div>
          {note.concepts.length > 0 && <div className="tag-list article-concepts">{note.concepts.map((concept) => <span key={concept}>#{concept}</span>)}</div>}
          {related.length > 0 && (
            <section className="article-related">
              <h2>相关笔记</h2>
              <div>{related.map((item) => <Link key={item.id} href={`/notes/${item.id}`}>{item.title}<ArrowUpRight size={12} /></Link>)}</div>
            </section>
          )}
          {note.codeUrl && <p className="article-code"><a href={note.codeUrl} target="_blank" rel="noreferrer">相关代码<ExternalLink size={13} /></a></p>}
          {note.fullTextUrl && <p className="article-code"><a href={note.fullTextUrl} target="_blank" rel="noreferrer">论文全文（LLM 精读来源）<ExternalLink size={13} /></a></p>}
          <section className="article-sources" id="references">
            <h2>引用与延伸阅读</h2>
            {note.sources.map((sourceId) => {
              const source = allSources.find((item) => item.id === sourceId)!;
              return <a key={source.id} href={source.url} target="_blank" rel="noreferrer"><div><strong>{source.title}</strong><span>{source.author} · {source.year} · {source.evidence}</span></div><ExternalLink size={14} /></a>;
            })}
          </section>
          <div className="article-navigation">
            {index > 0 && <Link href={`/notes/${notes[index - 1].id}`}><small><ArrowLeft size={13} />上一篇</small>{notes[index - 1].title}</Link>}
            {index < notes.length - 1 && <Link href={`/notes/${notes[index + 1].id}`}><small>下一篇<ArrowRight size={13} /></small>{notes[index + 1].title}</Link>}
          </div>
        </article>
        <aside className="reader-aside">
          <p className="nav-label">ON THIS PAGE</p>
          <nav aria-label="文章目录">{headings.map((heading) => <a href={`#${heading}`} key={heading}>{heading}</a>)}<a href="#references">引用与延伸阅读</a></nav>
          <div className="sidebar-divider" />
          <p className="nav-label">BACKLINKS / {backlinks.length}</p>
          {backlinks.map((item) => <Link className="backlink" href={`/notes/${item.id}`} key={item.id}>{item.title}<ArrowUpRight size={11} /></Link>)}
          <a className="edit-link" href={`${REPO}/edit/master/content/${note.filename}`} target="_blank" rel="noreferrer">编辑这篇笔记<ArrowUpRight size={12} /></a>
        </aside>
      </main>
    </div>
  );
}
