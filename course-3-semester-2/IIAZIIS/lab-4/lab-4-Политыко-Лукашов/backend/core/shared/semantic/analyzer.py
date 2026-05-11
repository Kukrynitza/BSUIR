
from __future__ import annotations

import re
import logging
from typing import Any

from core.shared.semantic.llm_adapter import LLMAdapter

logger = logging.getLogger(__name__)

SYNTAX_TO_SEMANTIC: dict[str, tuple[str, str]] = {
    "подлежащее": ("Agent", "участник-субъект (агент или экспериенцер)"),
    "сказуемое": ("Predicate", "предикат события / процесса"),
    "дополнение": ("Patient", "объект / пациент действия"),
    "определение": ("Attribute", "атрибутивная характеристика"),
    "обстоятельство": ("Circumstance", "обстоятельственная характеристика"),
}

POS_HINT_CATEGORY: dict[str, str] = {
    "NOUN": "Object",
    "NPRO": "Entity",
    "VERB": "Event",
    "INFN": "Event",
    "GRND": "Event",
    "ADJF": "Property",
    "ADJS": "Property",
    "COMP": "Property",
    "NUMR": "Quantity",
    "ADVB": "Manner",
    "PREP": "FunctionWord",
    "CONJ": "FunctionWord",
    "PRCL": "FunctionWord",
    "INTJ": "FunctionWord",
    "PUNCT": "Punctuation",
    "LATN": "Entity",
    "ROMN": "Quantity",
    "APRO": "Entity",
    "DET": "FunctionWord",
}

_DEP_ROLE_RULES: list[tuple[str, str, str]] = [
    ("nsubj:pass", "Patient", "носитель действия при пассиве (nsubj:pass)"),
    ("nsubj", "Agent", "субъект ситуации (nsubj)"),
    ("obj", "Patient", "объект / цель (obj)"),
    ("iobj", "Patient", "косвенный объект (iobj)"),
    ("xcomp", "Patient", "открытая клауза (xcomp)"),
    ("ccomp", "Patient", "придаточное дополнение (ccomp)"),
    ("obl:agent", "Agent", "агент в обстоятельственной группе"),
    ("obl", "Circumstance", "обстоятельство (obl)"),
    ("advmod", "Circumstance", "обстоятельство (наречие)"),
    ("advcl", "Circumstance", "обстоятельственное придаточное"),
    ("amod", "Attribute", "определение (amod)"),
    ("nmod", "Attribute", "именное определение (nmod)"),
    ("acl", "Attribute", "определительная клауза (acl)"),
    ("appos", "Attribute", "приложение (appos)"),
    ("case", "FunctionWord", "предложный маркер"),
    ("det", "FunctionWord", "детерминатив"),
    ("aux:pass", "FunctionWord", "вспомогательный (пассив)"),
    ("aux", "FunctionWord", "вспомогательный глагол"),
    ("cop", "FunctionWord", "связка"),
    ("conj", "FunctionWord", "сочинение"),
    ("cc", "FunctionWord", "союз"),
    ("fixed", "FunctionWord", "устойчивое выражение"),
    ("compound", "Entity", "компонент составного имени"),
    ("flat", "Entity", "неразложимое имя"),
]

LINK_SEMANTIC_GLOSS: dict[str, str] = {
    "nsubj": "участник → предикат",
    "nsubj:pass": "пассивный носитель → предикат",
    "root": "корень предложения",
    "obl": "обстоятельство → глагол",
    "obl:agent": "агент → процесс",
    "obj": "предикат → объект",
    "iobj": "предикат → адресат",
    "ccomp": "предикат → придаточное",
    "xcomp": "предикат → открытая клауза",
    "amod": "определение → имя",
    "nmod": "атрибут → имя",
    "appos": "уточнение",
    "conj": "однородность",
    "advmod": "обстоятельство",
    "advcl": "обстоятельственное придаточное",
    "acl": "определительная клауза",
    "case": "предложная связка",
    "aux": "вспомогательность",
    "cop": "связка",
    "dep": "общая зависимость",
}

_COPULA_LEMMA_RE = re.compile(
    r"^(быть|стать|являться|оказаться|казаться|остаться)$", re.I
)


class SemanticAnalyzer:
    def __init__(self):
        self.llm = LLMAdapter()

    def _refine_by_dep(
        self, dep_relation: str, _pos: str, base_role: str, base_desc: str
    ) -> tuple[str, str]:
        dr = dep_relation or ""
        for prefix, role, desc in _DEP_ROLE_RULES:
            if dr == prefix or dr.startswith(f"{prefix}:"):
                return role, desc
        return base_role, base_desc

    def _predicate_family(self, pos: str, lemma: str) -> bool:
        if pos in ("VERB", "INFN", "GRND"):
            return True
        if pos == "ADJF" and _COPULA_LEMMA_RE.match((lemma or "").lower()):
            return True
        return False

    async def build_for_sentence(
        self,
        sentence_id: int,
        sentence_text: str,
        tokens_ordered: list[Any],
        flat_dep: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        tokens_ordered: ORM Token в порядке position.
        flat_dep: list[dict[str, Any]],
        """
        by_pos: dict[int, Any] = {t.position: t for t in tokens_ordered}
        annotations: list[dict[str, Any]] = []
        links: list[dict[str, Any]] = []
        seen_tid: set[int] = set()

        llm_concepts = {}
        tokens_for_llm = [
            {"id": t.id, "text": t.token_text, "pos": t.pos}
            for t in tokens_ordered
        ]

        try:
            concepts_data = await self.llm.analyze_semantics(sentence_text, tokens_for_llm)
            for item in concepts_data:
                tid = item.get("token_id")
                if tid:
                    llm_concepts[tid] = item.get("concept_label", "")
        except Exception as e:
            logger.error(f"Error during LLM concept extraction: {e}")

        for row in flat_dep:
            tid = row.get("id")
            if tid is None or tid not in by_pos:
                continue
            if tid in seen_tid:
                continue
            seen_tid.add(tid)
            tok = by_pos[tid]
            syn_role = (tok.syntax_role or "").strip()
            pos = str(tok.pos or "")
            dep_rel = str(row.get("relation") or "")

            base_role, base_desc = SYNTAX_TO_SEMANTIC.get(
                syn_role, ("Participant", "участник ситуации (общий)")
            )
            sem_role, sem_desc = self._refine_by_dep(
                dep_rel, pos, base_role, base_desc
            )

            if self._predicate_family(pos, tok.lemma or "") and syn_role == "сказуемое":
                sem_role, sem_desc = "EventCore", "ядро предикации (глагольное или именное сказуемое)"

            if pos == "ADJF" and syn_role == "сказуемое" and not _COPULA_LEMMA_RE.match(
                (tok.lemma or "").lower()
            ):
                sem_role, sem_desc = "Predicate", "именное сказуемое (признак)"

            category = POS_HINT_CATEGORY.get(pos, "Entity")
            
            concept = llm_concepts.get(tok.id)
            source = "llm"
            
            if not concept:
                lemma = (tok.lemma or tok.token_text or "").strip()
                concept = f"лемма: {lemma}" if lemma else ""
                source = "fallback"

            annotations.append(
                {
                    "sentence_id": sentence_id,
                    "token_id": tok.id,
                    "entity_category": category,
                    "semantic_role": sem_role,
                    "semantic_role_description": sem_desc,
                    "syntax_basis": syn_role or row.get("relation_ru", ""),
                    "concept_label": concept,
                    "concept_uri": "",
                    "knowledge_source": source,
                }
            )

        id_to_tok = {t.position: t for t in tokens_ordered}
        seen_edges: set[tuple[int, int, str]] = set()
        for row in flat_dep:
            head = row.get("head") or 0
            cid = row.get("id")
            if not cid or head <= 0 or cid == head:
                continue
            child = id_to_tok.get(cid)
            parent = id_to_tok.get(head)
            if not child or not parent:
                continue
            rel = str(row.get("relation") or "dep")
            relation_ru = row.get("relation_ru") or rel
            gloss = LINK_SEMANTIC_GLOSS.get(rel.split(":")[0], "")
            if gloss:
                link_label = f"{gloss} · {relation_ru}"
            else:
                link_label = str(relation_ru)
            key = (parent.id, child.id, rel)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            links.append(
                {
                    "sentence_id": sentence_id,
                    "from_token_id": parent.id,
                    "to_token_id": child.id,
                    "link_type": rel,
                    "link_label_ru": link_label,
                    "knowledge_source": "syntax_projection",
                }
            )

        return annotations, links
