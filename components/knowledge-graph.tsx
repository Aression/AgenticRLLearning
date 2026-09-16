"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, X } from "lucide-react";
import { stageMeta, type Graph, type GraphNode, type NoteMeta } from "@/lib/types";

const WIDTH = 1000;
const HEIGHT = 640;
const EDGE_META: Record<string, { label: string; color: string }> = {
  prerequisite: { label: "先修", color: "#67ddcb" },
  related: { label: "相关", color: "#8b93a1" },
  "shared-source": { label: "共享来源", color: "#f3c578" },
  "shared-concept": { label: "共享概念", color: "#efa3b5" },
  concept: { label: "概念", color: "#4a4f55" },
};

type Position = { x: number; y: number };

/** Deterministic force-directed layout so server and client renders agree. */
function layout(graph: Graph): Record<string, Position> {
  const nodes = graph.nodes;
  const count = nodes.length || 1;
  const positions: (Position & { vx: number; vy: number })[] = nodes.map((node, index) => {
    const angle = (index / count) * Math.PI * 2;
    const radius = node.kind === "note" ? 230 : 330;
    return { x: WIDTH / 2 + Math.cos(angle) * radius, y: HEIGHT / 2 + Math.sin(angle) * (radius * 0.7), vx: 0, vy: 0 };
  });
  const indexById = new Map(nodes.map((node, index) => [node.id, index]));
  const edges = graph.edges
    .map((edge) => ({ s: indexById.get(edge.source), t: indexById.get(edge.target), weight: edge.weight }))
    .filter((edge): edge is { s: number; t: number; weight: number } => edge.s !== undefined && edge.t !== undefined);

  for (let iteration = 0; iteration < 260; iteration += 1) {
    for (let i = 0; i < positions.length; i += 1) {
      for (let j = i + 1; j < positions.length; j += 1) {
        let dx = positions[j].x - positions[i].x;
        let dy = positions[j].y - positions[i].y;
        let distanceSq = dx * dx + dy * dy;
        if (distanceSq < 1) { dx = ((i * 31 + j * 17) % 11) / 11 - 0.5; dy = ((i * 13 + j * 7) % 11) / 11 - 0.5; distanceSq = 1; }
        const distance = Math.sqrt(distanceSq);
        const strength = (nodes[i].kind === "note" && nodes[j].kind === "note" ? 2600 : 1100) / distanceSq;
        const fx = (dx / distance) * strength;
        const fy = (dy / distance) * strength;
        positions[i].x -= fx; positions[i].y -= fy;
        positions[j].x += fx; positions[j].y += fy;
      }
    }
    for (const edge of edges) {
      const a = positions[edge.s];
      const b = positions[edge.t];
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const distance = Math.sqrt(dx * dx + dy * dy) || 1;
      const target = nodes[edge.s].kind === "note" && nodes[edge.t].kind === "note" ? 165 : 110;
      const force = (distance - target) * 0.02;
      const fx = (dx / distance) * force;
      const fy = (dy / distance) * force;
      a.x += fx; a.y += fy; b.x -= fx; b.y -= fy;
    }
    for (const point of positions) {
      point.x += (WIDTH / 2 - point.x) * 0.002;
      point.y += (HEIGHT / 2 - point.y) * 0.002;
    }
  }
  return Object.fromEntries(positions.map((point, index) => [nodes[index].id, { x: Math.max(52, Math.min(WIDTH - 52, point.x)), y: Math.max(36, Math.min(HEIGHT - 36, point.y)) }]));
}

function short(label: string, max = 13) {
  return label.length > max ? `${label.slice(0, max)}…` : label;
}

export function KnowledgeGraph({ graph, notes }: { graph: Graph; notes: NoteMeta[] }) {
  const router = useRouter();
  const [hovered, setHovered] = useState<string | null>(null);
  const [focus, setFocus] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [enabled, setEnabled] = useState<Record<string, boolean>>({ prerequisite: true, related: true, "shared-source": true, "shared-concept": true, concept: true });

  const positions = useMemo(() => layout(graph), [graph]);
  const nodeById = useMemo(() => new Map(graph.nodes.map((node) => [node.id, node])), [graph]);
  const titleById = useMemo(() => new Map(notes.map((note) => [note.id, note.title])), [notes]);
  const active = focus ?? hovered;
  const neighbours = useMemo(() => {
    if (!active) return null;
    const set = new Set([active]);
    for (const edge of graph.edges) {
      if (edge.source === active) set.add(edge.target);
      if (edge.target === active) set.add(edge.source);
    }
    return set;
  }, [active, graph.edges]);
  const matches = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return null;
    return new Set(graph.nodes.filter((node) => node.label.toLowerCase().includes(needle)).map((node) => node.id));
  }, [query, graph.nodes]);
  const visibleEdges = graph.edges.filter((edge) => enabled[edge.kind] !== false);

  function activate(node: GraphNode) {
    if (node.kind === "note") {
      router.push(`/notes/${node.id}`);
      return;
    }
    setQuery(node.label);
    setFocus(node.id);
  }

  return (
    <div className="graph-wrap">
      <div className="graph-toolbar">
        <label className="search"><Search size={15} /><input aria-label="搜索图谱节点" placeholder="搜索笔记或概念…" value={query} onChange={(event) => { setQuery(event.target.value); setFocus(null); }} />{query && <button className="icon-button" onClick={() => { setQuery(""); setFocus(null); }} aria-label="清空搜索"><X size={13} /></button>}</label>
        <div className="graph-legend">
          {Object.entries(EDGE_META).map(([kind, meta]) => (
            <button key={kind} className={enabled[kind] ? "on" : ""} onClick={() => setEnabled((current) => ({ ...current, [kind]: !current[kind] }))} aria-pressed={enabled[kind]}>
              <i style={{ background: meta.color }} />{meta.label}
            </button>
          ))}
        </div>
      </div>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="graph-canvas" role="img" aria-label="知识图谱：笔记与概念的关系网络">
        <g className="graph-edges">
          {visibleEdges.map((edge, index) => {
            const from = positions[edge.source];
            const to = positions[edge.target];
            if (!from || !to) return null;
            const dim = neighbours ? !(neighbours.has(edge.source) && neighbours.has(edge.target)) : false;
            return <line key={`${edge.source}-${edge.target}-${index}`} x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke={EDGE_META[edge.kind]?.color ?? "#4a4f55"} strokeWidth={Math.min(3, 0.7 + edge.weight * 0.5)} strokeOpacity={dim ? 0.05 : 0.5} />;
          })}
        </g>
        <g className="graph-nodes">
          {graph.nodes.map((node) => {
            const point = positions[node.id];
            if (!point) return null;
            const dim = neighbours ? !neighbours.has(node.id) : false;
            const hit = matches?.has(node.id) ?? false;
            const isNote = node.kind === "note";
            const color = isNote ? stageMeta[node.stage as keyof typeof stageMeta]?.hex ?? "#bec7d0" : "#6a7076";
            const label = isNote ? titleById.get(node.id) ?? node.label : node.label;
            return (
              <g key={node.id} transform={`translate(${point.x} ${point.y})`} className={`graph-node ${isNote ? "is-note" : "is-concept"} ${dim ? "dim" : ""} ${hit ? "hit" : ""}`} onMouseEnter={() => setHovered(node.id)} onMouseLeave={() => setHovered(null)} onClick={() => activate(node)} role="button" tabIndex={0} onKeyDown={(event) => { if (event.key === "Enter") activate(node); }}>
                <circle r={isNote ? 9 + Math.min(5, node.degree / 5) : 4.5} fill={color} stroke={hit ? "#fff" : "transparent"} strokeWidth={hit ? 2 : 0} />
                {(isNote || active === node.id || (neighbours?.has(node.id) && !isNote)) && <text y={isNote ? -16 : -10} textAnchor="middle" className="graph-label">{short(label, isNote ? 14 : 16)}</text>}
              </g>
            );
          })}
        </g>
      </svg>
      <p className="graph-foot mono">{graph.nodes.length} 节点 · {visibleEdges.length} 关系 · 点击笔记打开正文，点击概念聚焦邻居。图谱由 <code>scripts/atlas_db.py</code> 从先修、来源与标签关系生成。</p>
    </div>
  );
}
