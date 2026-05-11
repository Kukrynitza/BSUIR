import { useMemo, useState } from 'react';
import { translateEntity, translateRole } from '../constants/translations';

export interface SemGraphNode {
  id: number;
  label: string;
  category?: string;
  role?: string;
}

export interface SemGraphEdge {
  from: number;
  to: number;
  label: string;
}

interface SemanticGraphProps {
  nodes: SemGraphNode[];
  edges: SemGraphEdge[];
  emphasisIds?: Set<number> | null;
}

const NODE_W = 108;
const NODE_H = 38;
const LEVEL_GAP = 210;
const ROW_GAP = 50;
const PAD = 28;

function computeLayout(
  nodeIds: number[],
  edges: SemGraphEdge[]
): Map<number, { x: number; y: number }> {
  const pos = new Map<number, { x: number; y: number }>();
  if (nodeIds.length === 0) return pos;

  const children = new Map<number, number[]>();
  for (const e of edges) {
    if (!children.has(e.from)) children.set(e.from, []);
    children.get(e.from)!.push(e.to);
  }
  for (const [, ch] of children) ch.sort((a, b) => a - b);

  const incoming = new Set(edges.map((e) => e.to));
  let roots = nodeIds.filter((id) => !incoming.has(id));
  if (roots.length === 0) roots = [nodeIds[0]];

  const level = new Map<number, number>();
  const queue = [...roots];
  for (const r of roots) level.set(r, 0);

  let qi = 0;
  while (qi < queue.length) {
    const u = queue[qi++];
    const lv = level.get(u) ?? 0;
    for (const v of children.get(u) || []) {
      if (!level.has(v)) {
        level.set(v, lv + 1);
        queue.push(v);
      }
    }
  }
  for (const id of nodeIds) {
    if (!level.has(id)) level.set(id, 0);
  }

  const byLevel = new Map<number, number[]>();
  for (const id of nodeIds) {
    const lv = level.get(id) ?? 0;
    if (!byLevel.has(lv)) byLevel.set(lv, []);
    byLevel.get(lv)!.push(id);
  }
  const sortedLevels = [...byLevel.keys()].sort((a, b) => a - b);
  for (const lv of sortedLevels) {
    byLevel.get(lv)!.sort((a, b) => a - b);
  }

  sortedLevels.forEach((lv) => {
    const row = byLevel.get(lv)!;
    row.forEach((id, j) => {
      pos.set(id, { x: PAD + lv * LEVEL_GAP, y: PAD + j * ROW_GAP });
    });
  });

  return pos;
}

export default function SemanticGraph({
  nodes,
  edges,
  emphasisIds = null,
}: SemanticGraphProps) {
  const [hoverId, setHoverId] = useState<number | null>(null);

  const { positions, width, height, renderedEdges } = useMemo(() => {
    const nodeIds = nodes.map((n) => n.id);
    const positions = computeLayout(nodeIds, edges);
    let maxX = PAD + NODE_W;
    let maxY = PAD + NODE_H;
    positions.forEach((p) => {
      maxX = Math.max(maxX, p.x + NODE_W + PAD);
      maxY = Math.max(maxY, p.y + NODE_H + PAD);
    });

    const center = (id: number) => {
      const p = positions.get(id);
      if (!p) return { cx: 0, cy: 0 };
      return { cx: p.x + NODE_W / 2, cy: p.y + NODE_H / 2 };
    };

    const renderedEdges = edges.map((e, idx) => {
      const a = center(e.from);
      const b = center(e.to);
      const mx = (a.cx + b.cx) / 2;
      const my = (a.cy + b.cy) / 2;
      const short =
        e.label.length > 40 ? `${e.label.slice(0, 38)}…` : e.label;
      return {
        idx,
        d: `M ${a.cx} ${a.cy} L ${b.cx} ${b.cy}`,
        label: short,
        midX: mx,
        midY: my - 8,
        from: e.from,
        to: e.to,
      };
    });

    return { positions, width: maxX, height: maxY, renderedEdges };
  }, [nodes, edges]);

  const dimNode = (id: number) => {
    if (!emphasisIds || emphasisIds.size === 0) return false;
    return !emphasisIds.has(id);
  };

  const dimEdge = (from: number, to: number) => {
    if (!hoverId) return false;
    return hoverId !== from && hoverId !== to;
  };

  if (nodes.length === 0) return null;

  return (
    <div className="semantic-graph-wrap">
      <h5 className="semantic-graph-title">
        Граф семантических связей (проекция зависимостей)
      </h5>
      <svg
        className="semantic-graph-svg"
        width="100%"
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Семантический граф"
      >
        <defs>
          <marker
            id="arrow-semantic"
            markerWidth="9"
            markerHeight="9"
            refX="8"
            refY="4.5"
            orient="auto"
          >
            <path d="M0,0 L9,4.5 L0,9 Z" fill="#4f46e5" />
          </marker>
        </defs>
        <g className="semantic-graph-edges">
          {renderedEdges.map((ep) => (
            <g key={ep.idx}>
              <path
                d={ep.d}
                className={`semantic-graph-edge${dimEdge(ep.from, ep.to) ? ' muted' : ''}`}
                markerEnd="url(#arrow-semantic)"
              />
              <text
                x={ep.midX}
                y={ep.midY}
                className="semantic-graph-edge-label"
                textAnchor="middle"
              >
                {ep.label}
              </text>
            </g>
          ))}
        </g>
        <g className="semantic-graph-nodes">
          {nodes.map((n) => {
            const p = positions.get(n.id);
            if (!p) return null;
            const muted = dimNode(n.id);
            const active = hoverId === n.id;
            return (
              <g
                key={n.id}
                transform={`translate(${p.x},${p.y})`}
                onMouseEnter={() => setHoverId(n.id)}
                onMouseLeave={() => setHoverId(null)}
                className={`semantic-graph-node-group${active ? ' active' : ''}${muted ? ' dimmed' : ''}`}
              >
                <rect
                  rx="8"
                  ry="8"
                  width={NODE_W}
                  height={NODE_H}
                  className="semantic-graph-node-rect"
                />
                <text
                  x={NODE_W / 2}
                  y={16}
                  className="semantic-graph-node-text"
                  textAnchor="middle"
                >
                  {n.label.length > 14 ? `${n.label.slice(0, 12)}…` : n.label}
                </text>
                <text
                  x={NODE_W / 2}
                  y={30}
                  className="semantic-graph-node-meta"
                  textAnchor="middle"
                >
                   {[translateRole(n.role), translateEntity(n.category)].filter(Boolean).join(' · ').slice(0, 22)}

                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
