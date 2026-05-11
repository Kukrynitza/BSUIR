
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class ConceptNetAdapter:

    BASE = "https://api.conceptnet.io/query"

    def __init__(self, timeout: float = 1.2):
        self.timeout = timeout
        self.enabled = os.environ.get("CONCEPTNET_ENABLED", "").lower() in (
            "1",
            "true",
            "yes",
        )
        self._cache: dict[str, dict[str, Any]] = {}

    def _normalize_lemma(self, lemma: str) -> str:
        s = (lemma or "").strip().lower()
        s = re.sub(r"\s+", "_", s)
        return urllib.parse.quote(s, safe="")

    def enrich(self, lemma: str, lang: str = "ru") -> dict[str, Any]:
        if not self.enabled or not lemma:
            return {
                "concept_label": "",
                "concept_uri": "",
                "knowledge_source": "rules",
            }

        key = f"{lang}:{lemma.strip().lower()}"
        if key in self._cache:
            return self._cache[key]

        node = f"/c/{lang}/{self._normalize_lemma(lemma)}"
        params = urllib.parse.urlencode(
            {"start": node, "rel": "/r/RelatedTo", "limit": 5}
        )
        url = f"{self.BASE}?{params}"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "SemanticsSyntaxAnalyzer/1.0"}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            out = {
                "concept_label": "",
                "concept_uri": "",
                "knowledge_source": "fallback",
            }
            self._cache[key] = out
            return out

        edges = data.get("edges") or []
        for edge in edges:
            end = edge.get("end") or {}
            lbl = end.get("label")
            uri = end.get("@id") or end.get("id")
            if lbl and isinstance(lbl, str):
                out = {
                    "concept_label": lbl[:200],
                    "concept_uri": str(uri or "")[:500],
                    "knowledge_source": "conceptnet",
                }
                self._cache[key] = out
                return out

        out = {
            "concept_label": "",
            "concept_uri": "",
            "knowledge_source": "fallback",
        }
        self._cache[key] = out
        return out
