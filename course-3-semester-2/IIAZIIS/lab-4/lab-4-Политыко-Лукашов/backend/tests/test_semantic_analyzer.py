from __future__ import annotations

import os

os.environ.setdefault("CONCEPTNET_ENABLED", "0")

from core.shared.semantic.analyzer import SemanticAnalyzer 


class _Tok:
    __slots__ = (
        "id",
        "position",
        "token_text",
        "lemma",
        "pos",
        "syntax_role",
    )

    def __init__(
        self,
        tid: int,
        pos: int,
        text: str,
        lemma: str,
        pos_tag: str,
        syn: str,
    ):
        self.id = tid
        self.position = pos
        self.token_text = text
        self.lemma = lemma
        self.pos = pos_tag
        self.syntax_role = syn


def test_nsubj_pass_is_patient_not_agent():
    sa = SemanticAnalyzer()
    tokens = [
        _Tok(1, 1, "Книга", "книга", "NOUN", "подлежащее"),
        _Tok(2, 2, "читается", "читаться", "VERB", "сказуемое"),
    ]
    flat = [
        {
            "id": 1,
            "head": 2,
            "relation": "nsubj:pass",
            "relation_ru": "подлежащее (страдат.)",
        },
        {
            "id": 2,
            "head": 0,
            "relation": "root",
            "relation_ru": "корень",
        },
    ]
    ann, _links = sa.build_for_sentence(1, tokens, flat)
    subj = next(a for a in ann if a["token_id"] == 1)
    assert subj["semantic_role"] == "Patient"


def test_nsubj_is_agent():
    sa = SemanticAnalyzer()
    tokens = [
        _Tok(1, 1, "Кот", "кот", "NOUN", "подлежащее"),
        _Tok(2, 2, "спит", "спать", "VERB", "сказуемое"),
    ]
    flat = [
        {"id": 1, "head": 2, "relation": "nsubj", "relation_ru": "подлежащее"},
        {"id": 2, "head": 0, "relation": "root", "relation_ru": "корень"},
    ]
    ann, links = sa.build_for_sentence(1, tokens, flat)
    subj = next(a for a in ann if a["token_id"] == 1)
    assert subj["semantic_role"] == "Agent"
    assert any(l["link_type"] == "nsubj" for l in links)


def test_link_label_contains_gloss():
    sa = SemanticAnalyzer()
    tokens = [
        _Tok(1, 1, "Кот", "кот", "NOUN", "подлежащее"),
        _Tok(2, 2, "спит", "спать", "VERB", "сказуемое"),
    ]
    flat = [
        {"id": 1, "head": 2, "relation": "nsubj", "relation_ru": "подлежащее"},
        {"id": 2, "head": 0, "relation": "root", "relation_ru": "корень"},
    ]
    _ann, links = sa.build_for_sentence(1, tokens, flat)
    nsubj_link = next(l for l in links if l["link_type"] == "nsubj")
    assert "участник" in nsubj_link["link_label_ru"].lower()
    assert "подлежащее" in nsubj_link["link_label_ru"].lower()
