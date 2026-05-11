import uuid
from pathlib import Path
from typing import Any
from datetime import datetime
import time

from sqlalchemy.orm import Session
from sqlalchemy import delete

from sqlalchemy.orm import selectinload

from core.models import (
    Document,
    Sentence,
    Token,
    SyntaxRelation,
    SemanticAnnotation,
    SemanticLink,
    SessionLocal,
)
from core.shared.parser.txt_parser import TxtParser
from core.shared.parser.rtf_parser import RtfParser
from core.shared.parser.docx_parser import DocxParser
from core.shared.syntax.analyzer import (
    SyntaxAnalyzer,
    DependencyTreeBuilder,
    ConstituencyTreeBuilder,
)
from core.shared.semantic.analyzer import SemanticAnalyzer


class SyntaxManager:
    def __init__(self, data_dir: Path | str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.txt_parser = TxtParser()
        self.rtf_parser = RtfParser()
        self.docx_parser = DocxParser()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.dep_tree_builder = DependencyTreeBuilder(self.syntax_analyzer)
        self.const_tree_builder = ConstituencyTreeBuilder(self.syntax_analyzer)
        self.semantic_analyzer = SemanticAnalyzer()

    def _get_db(self) -> Session:
        return SessionLocal()

    def load_file(self, content: bytes, filename: str) -> Document:
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        if ext == "rtf":
            text = self.rtf_parser.parse(content)
        elif ext == "docx":
            text = self.docx_parser.parse(content)
        else:
            text = self.txt_parser.parse(content)

        title = filename.rsplit(".", 1)[0] if "." in filename else filename

        doc = Document(
            id=str(uuid.uuid4()),
            title=title,
            content=text,
            source=filename,
            text_type="текст для семантико-синтаксического анализа",
            created_at=datetime.now(),
            word_count=len(text.split()),
            char_count=len(text),
        )

        return doc

    def add_document(self, doc: Document) -> Document:
        db = self._get_db()
        try:
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc
        finally:
            db.close()

    def get_document(self, doc_id: str) -> Document | None:
        db = self._get_db()
        try:
            return db.query(Document).filter(Document.id == doc_id).first()
        finally:
            db.close()

    def get_all_documents(self) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            docs = db.query(Document).order_by(Document.created_at.desc()).all()
            return [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "word_count": doc.word_count,
                    "metadata": doc.to_dict()["metadata"],
                }
                for doc in docs
            ]
        finally:
            db.close()

    def update_document(self, doc_id: str, content: str) -> Document | None:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return None
            doc.content = content
            doc.word_count = len(content.split())
            doc.char_count = len(content)
            db.commit()
            db.refresh(doc)
            return doc
        finally:
            db.close()

    def delete_document(self, doc_id: str) -> bool:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return False
            db.delete(doc)
            db.commit()
            return True
        finally:
            db.close()

    async def analyze_document(self, doc_id: str) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return []

            # До expunge_all: после отсоединения doc.content недоступен (DetachedInstanceError)
            document_text = doc.content

            sentences = db.query(Sentence).filter(Sentence.document_id == doc_id).all()
            for sent in sentences:
                db.query(SemanticLink).filter(
                    SemanticLink.sentence_id == sent.id
                ).delete(synchronize_session=False)
                db.query(SemanticAnnotation).filter(
                    SemanticAnnotation.sentence_id == sent.id
                ).delete(synchronize_session=False)
                db.query(Token).filter(Token.sentence_id == sent.id).delete(
                    synchronize_session=False
                )
                db.query(SyntaxRelation).filter(
                    SyntaxRelation.sentence_id == sent.id
                ).delete(synchronize_session=False)
            db.query(Sentence).filter(Sentence.document_id == doc_id).delete(
                synchronize_session=False
            )
            db.commit()
            db.expunge_all()

            start_time = time.perf_counter()
            analysis = self.syntax_analyzer.analyze_text(document_text)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            doc_row = db.query(Document).filter(Document.id == doc_id).first()
            if doc_row:
                doc_row.analysis_time_ms = elapsed_ms
                db.commit()

            for sentence_data in analysis:
                sentence = Sentence(
                    document_id=doc_id,
                    sentence_index=sentence_data["sentence_index"],
                    sentence_text=sentence_data["sentence"],
                    created_at=datetime.now(),
                )
                db.add(sentence)
                db.flush()

                tokens_data = sentence_data.get("tokens", [])
                token_objects = []
                for token_data in tokens_data:
                    token = Token(
                        document_id=doc_id,
                        sentence_id=sentence.id,
                        token_index=token_data.get(
                            "token_index", token_data.get("position", 0)
                        ),
                        token_text=token_data.get("token", ""),
                        lemma=token_data.get("lemma", ""),
                        pos=token_data.get("pos", ""),
                        pos_name=token_data.get("pos_name", ""),
                        case=token_data.get("case", ""),
                        case_name=token_data.get("case_name", ""),
                        number=token_data.get("number", ""),
                        number_name=token_data.get("number_name", ""),
                        gender=token_data.get("gender", ""),
                        gender_name=token_data.get("gender_name", ""),
                        tense=token_data.get("tense", ""),
                        person=token_data.get("person", ""),
                        animacy=token_data.get("animacy", ""),
                        syntax_role=token_data.get("syntax_role", ""),
                        syntax_role_name=token_data.get("syntax_role_name", ""),
                        position=token_data.get("position", 0),
                    )
                    db.add(token)
                    token_objects.append(token)

                db.flush()

                relations = self.syntax_analyzer.detect_relations(token_objects)
                for rel in relations:
                    relation = SyntaxRelation(
                        sentence_id=sentence.id,
                        from_token_id=rel["from_token_id"],
                        to_token_id=rel["to_token_id"],
                        relation_type=rel["relation_type"],
                        relation_name=rel["relation_name"],
                        description=rel.get("description", ""),
                    )
                    db.add(relation)

                tokens_sorted = sorted(token_objects, key=lambda t: t.position)
                sent_for_tree = {
                    "sentence_index": sentence.sentence_index,
                    "sentence_text": sentence.sentence_text,
                    "tokens": [
                        {
                            "token": t.token_text,
                            "lemma": t.lemma,
                            "pos": t.pos,
                            "pos_name": t.pos_name,
                            "syntax_role": t.syntax_role,
                            "syntax_role_name": t.syntax_role_name,
                            "position": t.position,
                        }
                        for t in tokens_sorted
                    ],
                }
                dep = self.dep_tree_builder.build_tree(sent_for_tree)
                flat_dep = dep.get("flat_representation", [])
                ann_rows, link_rows = await self.semantic_analyzer.build_for_sentence(
                    sentence.id, sentence.sentence_text, tokens_sorted, flat_dep
                )
                for ar in ann_rows:
                    db.add(
                        SemanticAnnotation(
                            sentence_id=ar["sentence_id"],
                            token_id=ar["token_id"],
                            entity_category=ar["entity_category"],
                            semantic_role=ar["semantic_role"],
                            semantic_role_description=ar.get(
                                "semantic_role_description", ""
                            ),
                            syntax_basis=ar.get("syntax_basis", ""),
                            concept_label=ar.get("concept_label", ""),
                            concept_uri=ar.get("concept_uri", ""),
                            knowledge_source=ar.get("knowledge_source", "rules"),
                        )
                    )
                for lr in link_rows:
                    db.add(
                        SemanticLink(
                            sentence_id=lr["sentence_id"],
                            from_token_id=lr["from_token_id"],
                            to_token_id=lr["to_token_id"],
                            link_type=lr["link_type"],
                            link_label_ru=lr.get("link_label_ru", ""),
                            knowledge_source=lr.get(
                                "knowledge_source", "syntax_projection"
                            ),
                        )
                    )

            db.commit()

            return self.get_analysis(doc_id)
        finally:
            db.close()

    def get_analysis(self, doc_id: str) -> list[dict[str, Any]] | None:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return None

            sentences = (
                db.query(Sentence)
                .options(
                    selectinload(Sentence.tokens),
                    selectinload(Sentence.relations),
                    selectinload(Sentence.semantic_annotations).selectinload(
                        SemanticAnnotation.token
                    ),
                    selectinload(Sentence.semantic_links).selectinload(
                        SemanticLink.from_token
                    ),
                    selectinload(Sentence.semantic_links).selectinload(
                        SemanticLink.to_token
                    ),
                )
                .filter(Sentence.document_id == doc_id)
                .order_by(Sentence.sentence_index)
                .all()
            )

            result = []
            for sent in sentences:
                sent_dict = sent.to_dict()
                result.append(sent_dict)

            return result
        finally:
            db.close()

    def get_relations(self, doc_id: str) -> list[dict[str, Any]] | None:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return None

            sentences = (
                db.query(Sentence)
                .filter(Sentence.document_id == doc_id)
                .order_by(Sentence.sentence_index)
                .all()
            )

            all_relations = []
            for sent in sentences:
                relations = (
                    db.query(SyntaxRelation)
                    .filter(SyntaxRelation.sentence_id == sent.id)
                    .all()
                )
                for rel in relations:
                    all_relations.append(
                        {
                            "sentence_index": sent.sentence_index,
                            "sentence_text": sent.sentence_text,
                            "relation": rel.to_dict(),
                        }
                    )

            return all_relations
        finally:
            db.close()

    def update_token_role(
        self,
        doc_id: str,
        sentence_id: int,
        token_id: int,
        syntax_role: str,
        syntax_role_name: str,
    ) -> bool:
        db = self._get_db()
        try:
            token = (
                db.query(Token)
                .filter(
                    Token.id == token_id,
                    Token.document_id == doc_id,
                    Token.sentence_id == sentence_id,
                )
                .first()
            )

            if not token:
                return False

            token.syntax_role = syntax_role
            token.syntax_role_name = syntax_role_name
            db.commit()
            return True
        finally:
            db.close()

    def get_dependency_tree(
        self, doc_id: str, sentence_index: int | None = None
    ) -> dict[str, Any]:
        analysis = self.get_analysis(doc_id)
        if not analysis:
            return {"error": "Документ не найден"}

        if sentence_index is not None:
            sentences = [s for s in analysis if s["sentence_index"] == sentence_index]
        else:
            sentences = analysis

        trees = []
        for sent in sentences:
            tree = self.dep_tree_builder.build_tree(sent)
            trees.append(
                {
                    "sentence_index": sent["sentence_index"],
                    "sentence_text": sent["sentence_text"],
                    "tree": tree.get("tree"),
                    "flat_representation": tree.get("flat_representation", []),
                    "root_token": tree.get("root_token"),
                }
            )

        return {"document_id": doc_id, "trees": trees}

    def get_constituency_tree(
        self, doc_id: str, sentence_index: int | None = None
    ) -> dict[str, Any]:
        analysis = self.get_analysis(doc_id)
        if not analysis:
            return {"error": "Документ не найден"}

        if sentence_index is not None:
            sentences = [s for s in analysis if s["sentence_index"] == sentence_index]
        else:
            sentences = analysis

        trees = []
        for sent in sentences:
            tree = self.const_tree_builder.build_tree(sent)
            trees.append(
                {
                    "sentence_index": sent["sentence_index"],
                    "sentence_text": sent["sentence_text"],
                    "tree": tree.get("tree"),
                    "linearized": tree.get("linearized", ""),
                }
            )

        return {"document_id": doc_id, "trees": trees}

    async def analyze_text_trees(self, text: str) -> dict[str, Any]:
        analysis = self.syntax_analyzer.analyze_text(text)

        dependency_trees = []
        constituency_trees = []

        for sent_data in analysis:
            dep_tree = self.dep_tree_builder.build_tree(sent_data)
            const_tree = self.const_tree_builder.build_tree(sent_data)

            dependency_trees.append(
                {
                    "sentence_index": sent_data["sentence_index"],
                    "sentence_text": sent_data["sentence"],
                    "tree": dep_tree.get("tree"),
                    "flat_representation": dep_tree.get("flat_representation", []),
                    "root_token": dep_tree.get("root_token"),
                }
            )

            constituency_trees.append(
                {
                    "sentence_index": sent_data["sentence_index"],
                    "sentence_text": sent_data["sentence"],
                    "tree": const_tree.get("tree"),
                    "linearized": const_tree.get("linearized", ""),
                }
            )

        semantic_by_sentence: list[dict[str, Any]] = []
        for sent_data in analysis:
            tokens_data = sent_data.get("tokens", [])
            fake_tokens: list[Any] = []
            for i, td in enumerate(tokens_data):
                ft = type(
                    "Tok",
                    (),
                    {
                        "id": i + 1,
                        "position": td.get("position", i + 1),
                        "token_text": td.get("token", ""),
                        "lemma": td.get("lemma", ""),
                        "pos": td.get("pos", ""),
                        "pos_name": td.get("pos_name", ""),
                        "syntax_role": td.get("syntax_role", ""),
                        "syntax_role_name": td.get("syntax_role_name", ""),
                    },
                )()
                fake_tokens.append(ft)
            fake_tokens.sort(key=lambda t: t.position)
            dep = self.dep_tree_builder.build_tree(sent_data)
            flat_dep = dep.get("flat_representation", [])
            ann_rows, link_rows = await self.semantic_analyzer.build_for_sentence(
                0, sent_data["sentence_text"], fake_tokens, flat_dep
            )

            semantic_by_sentence.append(
                {
                    "sentence_index": sent_data["sentence_index"],
                    "sentence_text": sent_data["sentence"],
                    "annotations": [
                        {
                            **ar,
                            "token_text": next(
                                (
                                    t.token_text
                                    for t in fake_tokens
                                    if t.id == ar["token_id"]
                                ),
                                "",
                            ),
                        }
                        for ar in ann_rows
                    ],
                    "links": link_rows,
                }
            )

        return {
            "text": text,
            "dependency_trees": dependency_trees,
            "constituency_trees": constituency_trees,
            "semantic_analysis": semantic_by_sentence,
            "statistics": self.syntax_analyzer.get_statistics(analysis),
        }

    def update_semantic_annotation(
        self,
        doc_id: str,
        annotation_id: int,
        entity_category: str | None = None,
        semantic_role: str | None = None,
        concept_label: str | None = None,
    ) -> bool:
        db = self._get_db()
        try:
            ann = (
                db.query(SemanticAnnotation)
                .join(Sentence)
                .filter(
                    SemanticAnnotation.id == annotation_id,
                    Sentence.document_id == doc_id,
                )
                .first()
            )
            if not ann:
                return False
            if entity_category is not None:
                ann.entity_category = entity_category
            if semantic_role is not None:
                ann.semantic_role = semantic_role
            if concept_label is not None:
                ann.concept_label = concept_label
                ann.knowledge_source = "user"
            db.commit()
            return True
        finally:
            db.close()

    def export_semantic_json(self, doc_id: str) -> dict[str, Any] | None:
        analysis = self.get_analysis(doc_id)
        if analysis is None:
            return None
        doc = self.get_document(doc_id)
        return {
            "document_id": doc_id,
            "title": doc.title if doc else "",
            "sentences": [
                {
                    "sentence_index": s["sentence_index"],
                    "sentence_text": s["sentence_text"],
                    "semantic_annotations": s.get("semantic_annotations", []),
                    "semantic_links": s.get("semantic_links", []),
                }
                for s in analysis
            ],
        }
