import { useEffect, useMemo, useState } from 'react';
import {
  api,
  Sentence,
  SemanticAnnotation,
  DirectSemanticSentence,
  SemanticLink,
} from '../api/client';
import { translateEntity, translateRole } from '../constants/translations';
import SemanticGraph, { SemGraphEdge, SemGraphNode } from './SemanticGraph';
import LoadingOverlay from './LoadingOverlay';

const ENTITY_OPTIONS = [
  'Object',
  'Entity',
  'Event',
  'Property',
  'Quantity',
  'Manner',
  'FunctionWord',
  'Punctuation',
  'Participant',
];

const ROLE_OPTIONS = [
  'Agent',
  'Patient',
  'Predicate',
  'FunctionWord',
  'Attribute',
  'Circumstance',
  'EventCore',
  'Participant',
];

function intersectSets(a: Set<number>, b: Set<number>): Set<number> {
  const out = new Set<number>();
  for (const x of a) {
    if (b.has(x)) out.add(x);
  }
  return out;
}

function emphasisFromFilters(
  annotations: Array<Pick<SemanticAnnotation, 'token_id' | 'entity_category' | 'semantic_role'>>,
  links: Array<Pick<SemanticLink, 'from_token_id' | 'to_token_id' | 'link_type' | 'link_label_ru'>>,
  filterEntity: string,
  filterRole: string,
  filterLink: string
): Set<number> | null {
  if (!filterEntity && !filterRole && !filterLink) return null;
  const parts: Set<number>[] = [];
  if (filterEntity) {
    parts.push(
      new Set(
        annotations
          .filter((a) => a.entity_category === filterEntity)
          .map((a) => a.token_id)
      )
    );
  }
  if (filterRole) {
    parts.push(
      new Set(
        annotations
          .filter((a) => a.semantic_role === filterRole)
          .map((a) => a.token_id)
      )
    );
  }
  if (filterLink) {
    const fl = filterLink.toLowerCase();
    parts.push(
      new Set(
        links
          .filter(
            (l) =>
              l.link_type.toLowerCase().includes(fl) ||
              l.link_label_ru.toLowerCase().includes(fl)
          )
          .flatMap((l) => [l.from_token_id, l.to_token_id])
      )
    );
  }
  if (parts.length === 0) return null;
  let acc = parts[0]!;
  for (let i = 1; i < parts.length; i++) {
    acc = intersectSets(acc, parts[i]!);
  }
  return acc;
}

function buildGraph(
  annotations: Array<
    Pick<
      SemanticAnnotation,
      'token_id' | 'token_text' | 'entity_category' | 'semantic_role'
    >
  >,
  links: Array<Pick<SemanticLink, 'from_token_id' | 'to_token_id' | 'link_label_ru'>>
): { nodes: SemGraphNode[]; edges: SemGraphEdge[] } {
  const byId = new Map<number, SemGraphNode>();
  for (const a of annotations) {
    byId.set(a.token_id, {
      id: a.token_id,
      label: a.token_text || String(a.token_id),
      category: a.entity_category,
      role: a.semantic_role,
    });
  }
  for (const l of links) {
    if (!byId.has(l.from_token_id)) {
      byId.set(l.from_token_id, {
        id: l.from_token_id,
        label: `id:${l.from_token_id}`,
      });
    }
    if (!byId.has(l.to_token_id)) {
      byId.set(l.to_token_id, {
        id: l.to_token_id,
        label: `id:${l.to_token_id}`,
      });
    }
  }
  const nodes = [...byId.values()].sort((a, b) => a.id - b.id);
  const edges: SemGraphEdge[] = links.map((l) => ({
    from: l.from_token_id,
    to: l.to_token_id,
    label: l.link_label_ru,
  }));
  return { nodes, edges };
}

function FilterBar(props: {
  filterEntity: string;
  filterRole: string;
  filterLink: string;
  onEntity: (v: string) => void;
  onRole: (v: string) => void;
  onLink: (v: string) => void;
  linkHints: string[];
}) {
  const { filterEntity, filterRole, filterLink, onEntity, onRole, onLink, linkHints } =
    props;
  return (
    <div className="semantic-filter-bar">
      <span className="semantic-filter-label">Фильтры:</span>
      <select
        className="semantic-filter-select"
        value={filterEntity}
        onChange={(e) => onEntity(e.target.value)}
        aria-label="Категория сущности"
      >
         <option value="">все категории</option>
         {ENTITY_OPTIONS.map((o) => (
           <option key={o} value={o}>
             {translateEntity(o)}
           </option>
         ))}
       </select>
       <select
         className="semantic-filter-select"
         value={filterRole}
         onChange={(e) => onRole(e.target.value)}
         aria-label="Семантическая роль"
       >
         <option value="">все роли</option>
         {ROLE_OPTIONS.map((o) => (
           <option key={o} value={o}>
             {translateRole(o)}
           </option>
         ))}
       </select>

      <select
        className="semantic-filter-select semantic-filter-link"
        value={filterLink}
        onChange={(e) => onLink(e.target.value)}
        aria-label="Тип связи"
      >
        <option value="">все связи</option>
        {linkHints.map((h) => (
          <option key={h} value={h}>
            {h}
          </option>
        ))}
      </select>
    </div>
  );
}

interface SemanticPanelProps {
  sentences?: Sentence[];
  docId?: string;
  onAnalysisRefresh?: (rows: Sentence[]) => void;
  directSemantic?: DirectSemanticSentence[] | null;
}

export default function SemanticPanel({
  sentences = [],
  docId,
  onAnalysisRefresh,
  directSemantic,
}: SemanticPanelProps) {
  const [savingId, setSavingId] = useState<number | null>(null);
  const [filterEntity, setFilterEntity] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [filterLink, setFilterLink] = useState('');

  const handleSave = async (
    ann: SemanticAnnotation,
    entity: string,
    role: string,
    concept: string
  ) => {
    if (!docId) return;
    try {
      setSavingId(ann.id);
      const res = await api.updateSemanticAnnotation(docId, ann.id, {
        entity_category: entity,
        semantic_role: role,
        concept_label: concept,
      });
      onAnalysisRefresh?.(res.analysis);
    } catch {
      console.error('semantic save failed');
    } finally {
      setSavingId(null);
    }
  };

  const directLinkHints = useMemo(() => {
    if (!directSemantic) return [];
    const s = new Set<string>();
    for (const b of directSemantic) {
      for (const l of b.links) {
        if (l.link_type) s.add(l.link_type);
      }
    }
    return [...s].sort();
  }, [directSemantic]);

  const docLinkHints = useMemo(() => {
    const s = new Set<string>();
    for (const sent of sentences) {
      for (const l of sent.semantic_links || []) {
        if (l.link_type) s.add(l.link_type);
      }
    }
    return [...s].sort();
  }, [sentences]);

  if (directSemantic != null) {
    if (directSemantic.length === 0) {
      return (
        <div className="semantic-panel">
          <h3>Семантико-синтаксический анализ (введённый текст)</h3>
          <p className="semantic-hint">Нет данных семантики для этого текста.</p>
        </div>
      );
    }
    return (
      <div className="semantic-panel">
        <h3>Семантико-синтаксический анализ (введённый текст)</h3>
        <p className="semantic-hint">
          Роли уточняются по синтаксису и типам зависимостей; внешнее обогащение —
          только при <code>CONCEPTNET_ENABLED=1</code> на сервере.
        </p>
        <FilterBar
          filterEntity={filterEntity}
          filterRole={filterRole}
          filterLink={filterLink}
          onEntity={setFilterEntity}
          onRole={setFilterRole}
          onLink={setFilterLink}
          linkHints={directLinkHints}
        />
        {directSemantic.map((block) => {
          const idToWord: Record<number, string> = {};
          block.annotations.forEach((a) => {
            idToWord[a.token_id] = a.token_text || String(a.token_id);
          });
          const annFull = block.annotations.map((a) => ({
            ...a,
            token_text: a.token_text || idToWord[a.token_id],
          }));
          const emphasis = emphasisFromFilters(
            annFull,
            block.links,
            filterEntity,
            filterRole,
            filterLink
          );
          const { nodes, edges } = buildGraph(annFull, block.links);
          return (
            <div key={block.sentence_index} className="semantic-sentence-block">
              <h4>Предложение {block.sentence_index}</h4>
              <p className="tree-sentence">«{block.sentence_text}»</p>
              {edges.length > 0 && (
                <SemanticGraph nodes={nodes} edges={edges} emphasisIds={emphasis} />
              )}
              <table className="semantic-table">
                <thead>
                  <tr>
                    <th>Слово</th>
                    <th>Категория</th>
                    <th>Семант. роль</th>
                    <th>Основа (синтаксис)</th>
                    <th>Концепт / источник</th>
                  </tr>
                </thead>
                <tbody>
                  {block.annotations.map((a, idx) => {
                    const muted =
                      emphasis &&
                      emphasis.size > 0 &&
                      !emphasis.has(a.token_id);
                    return (
                      <tr
                        key={idx}
                        className={muted ? 'semantic-row-muted' : undefined}
                      >
                        <td>{a.token_text || '—'}</td>
                         <td>{translateEntity(a.entity_category)}</td>
                         <td>{translateRole(a.semantic_role)}</td>
                         <td>{a.syntax_basis}</td>

                        <td>
                          <span className="concept-cell">
                            {a.concept_label || '—'}
                          </span>
                          <br />
                          <small className="source-badge">{a.knowledge_source}</small>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {block.links.length > 0 && (
                <>
                  <h5>Связи (список)</h5>
                  <ul className="semantic-links-list">
                    {block.links.map((l, i) => (
                      <li
                        key={i}
                        className={
                          emphasis &&
                          emphasis.size > 0 &&
                          !emphasis.has(l.from_token_id) &&
                          !emphasis.has(l.to_token_id)
                            ? 'semantic-row-muted'
                            : undefined
                        }
                      >
                        <strong>{idToWord[l.from_token_id] || l.from_token_id}</strong>
                        {' → '}
                        <strong>{idToWord[l.to_token_id] || l.to_token_id}</strong>
                        : {l.link_label_ru} <code>({l.link_type})</code>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  const hasDocSemantic = sentences.some(
    (s) =>
      (s.semantic_annotations && s.semantic_annotations.length > 0) ||
      (s.semantic_links && s.semantic_links.length > 0)
  );
  if (!hasDocSemantic) return null;

  return (
    <div className="semantic-panel">
      <h3>Семантико-синтаксический анализ</h3>
      <p className="semantic-hint">
        Фильтры подсвечивают узлы и строки, попадающие во все выбранные критерии.
      </p>
      <FilterBar
        filterEntity={filterEntity}
        filterRole={filterRole}
        filterLink={filterLink}
        onEntity={setFilterEntity}
        onRole={setFilterRole}
        onLink={setFilterLink}
        linkHints={docLinkHints}
      />
      {sentences.map((sentence) => {
        const anns = sentence.semantic_annotations || [];
        const links = sentence.semantic_links || [];
        if (anns.length === 0 && links.length === 0) return null;
        const emphasis = emphasisFromFilters(
          anns,
          links,
          filterEntity,
          filterRole,
          filterLink
        );
        const { nodes, edges } = buildGraph(anns, links);
        return (
          <div key={sentence.sentence_index} className="semantic-sentence-block">
            <h4>Предложение {sentence.sentence_index}</h4>
            <p className="tree-sentence">«{sentence.sentence_text}»</p>
            {edges.length > 0 && (
              <SemanticGraph nodes={nodes} edges={edges} emphasisIds={emphasis} />
            )}
            {anns.length > 0 && (
              <table className="semantic-table">
                <thead>
                  <tr>
                    <th>Слово</th>
                    <th>Категория</th>
                    <th>Семант. роль</th>
                    <th>Описание роли</th>
                     <th className="concept-col" style={{ width: '40%', minWidth: '200px' }}>Описание концепта</th>
                     <th>Источник</th>

                    {docId ? <th>Действия</th> : null}
                  </tr>
                </thead>
                <tbody>
                  {anns.map((ann) => {
                    const muted =
                      emphasis &&
                      emphasis.size > 0 &&
                      !emphasis.has(ann.token_id);
                    return (
                      <SemanticRowEditable
                        key={ann.id}
                        ann={ann}
                        docId={docId}
                        saving={savingId === ann.id}
                        onSave={handleSave}
                        rowMuted={!!muted}
                      />
                    );
                  })}
                </tbody>
              </table>
            )}
            {links.length > 0 && (
              <>
                <h5>Связи (список)</h5>
                <table className="semantic-table links-table">
                  <thead>
                    <tr>
                      <th>От</th>
                      <th>К</th>
                      <th>Подпись</th>
                      <th>Тип</th>
                    </tr>
                  </thead>
                  <tbody>
                    {links.map((l) => {
                      const muted =
                        emphasis &&
                        emphasis.size > 0 &&
                        !emphasis.has(l.from_token_id) &&
                        !emphasis.has(l.to_token_id);
                      return (
                        <tr key={l.id} className={muted ? 'semantic-row-muted' : undefined}>
                          <td>{l.from_token_text}</td>
                          <td>{l.to_token_text}</td>
                          <td>{l.link_label_ru}</td>
                          <td>
                            <code>{l.link_type}</code>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}

function SemanticRowEditable({
  ann,
  docId,
  saving,
  onSave,
  rowMuted,
}: {
  ann: SemanticAnnotation;
  docId?: string;
  saving: boolean;
  onSave: (ann: SemanticAnnotation, e: string, r: string, c: string) => void;
  rowMuted?: boolean;
}) {
  const entityChoices = [...ENTITY_OPTIONS];
  if (ann.entity_category && !entityChoices.includes(ann.entity_category)) {
    entityChoices.unshift(ann.entity_category);
  }
  const roleChoices = [...ROLE_OPTIONS];
  if (ann.semantic_role && !roleChoices.includes(ann.semantic_role)) {
    roleChoices.unshift(ann.semantic_role);
  }
  const [entity, setEntity] = useState(ann.entity_category);
  const [role, setRole] = useState(ann.semantic_role);
  const [concept, setConcept] = useState(ann.concept_label);

  useEffect(() => {
    setEntity(ann.entity_category);
    setRole(ann.semantic_role);
    setConcept(ann.concept_label);
  }, [ann.id, ann.entity_category, ann.semantic_role, ann.concept_label]);

  return (
    <tr className={rowMuted ? 'semantic-row-muted' : undefined}>
      <td>{ann.token_text}</td>
      <td>
        <select
          className="semantic-select"
          value={entity}
          onChange={(e) => setEntity(e.target.value)}
          disabled={!docId}
        >
          {entityChoices.map((o) => (
            <option key={o} value={o}>
              {translateEntity(o)}
            </option>
          ))}
        </select>
      </td>
      <td>
        <select
          className="semantic-select"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          disabled={!docId}
        >
          {roleChoices.map((o) => (
            <option key={o} value={o}>
              {translateRole(o)}
            </option>
          ))}
        </select>
      </td>
      <td>
        <small>{ann.semantic_role_description}</small>
      </td>
      <td className="concept-col" style={{ whiteSpace: 'normal', wordBreak: 'break-word', textAlign: 'left' }}>
        {docId ? (
          <input
            className="semantic-input concept-input"
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            disabled={!docId}
          />
        ) : (
          <span className="concept-text">{ann.concept_label || '—'}</span>
        )}
      </td>
      <td>
        <small className="source-badge">{ann.knowledge_source}</small>
      </td>
      {docId ? (
        <td>
          <button
            type="button"
            className="semantic-save-btn"
            disabled={saving}
            onClick={() => onSave(ann, entity, role, concept)}
          >
            {saving ? '…' : 'Сохранить'}
          </button>
        </td>
      ) : null}
    </tr>
  );

}
