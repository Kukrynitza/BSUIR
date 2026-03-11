
import json
import uuid
from pathlib import Path
from typing import Any
from datetime import datetime

from core.shared.parser.txt_parser import TxtParser
from core.shared.parser.rtf_parser import RtfParser
from core.shared.morphology.analyzer import MorphAnalyzer


class TextDocument:
    def __init__(
        self,
        doc_id: str,
        title: str,
        content: str,
        source: str = "",
        author: str = "",
        date: str = "",
        genre: str = "",
        text_type: str = ""
    ):
        self.id = doc_id
        self.title = title
        self.content = content
        self.source = source
        self.author = author
        self.date = date
        self.genre = genre
        self.text_type = text_type
        self.created_at = datetime.now().isoformat()
        self.word_count = len(content.split())
        self.char_count = len(content)

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'metadata': {
                'source': self.source,
                'author': self.author,
                'date': self.date,
                'genre': self.genre,
                'text_type': self.text_type,
                'word_count': self.word_count,
                'char_count': self.char_count,
                'created_at': self.created_at
            }
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'TextDocument':
        meta = data.get('metadata', {})
        doc = cls(
            doc_id=data['id'],
            title=data['title'],
            content=data['content'],
            source=meta.get('source', ''),
            author=meta.get('author', ''),
            date=meta.get('date', ''),
            genre=meta.get('genre', ''),
            text_type=meta.get('text_type', '')
        )
        doc.word_count = meta.get('word_count', 0)
        doc.char_count = meta.get('char_count', 0)
        doc.created_at = meta.get('created_at', '')
        return doc


class CorpusManager:
    def __init__(self, data_dir: Path | str):
        self.data_dir = Path(data_dir)
        self.corpus_dir = self.data_dir / 'corpus'
        self.index_file = self.data_dir / 'index.json'
        
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        
        self.txt_parser = TxtParser()
        self.rtf_parser = RtfParser()
        self.morph = MorphAnalyzer()
        
        self.documents: dict[str, TextDocument] = {}
        self.load_index()

    def load_index(self):
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for doc_data in data.get('documents', []):
                    doc = TextDocument.from_dict(doc_data)
                    self.documents[doc.id] = doc

    def save_index(self):
        data = {
            'documents': [doc.to_dict() for doc in self.documents.values()],
            'total_documents': len(self.documents),
            'total_words': sum(doc.word_count for doc in self.documents.values())
        }
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_file(self, content: bytes, filename: str) -> TextDocument:
        ext = filename.split('.')[-1].lower() if '.' in filename else 'txt'
        
        if ext == 'rtf':
            text = self.rtf_parser.parse(content)
        else:
            text = self.txt_parser.parse(content)
        
        title = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        doc = TextDocument(
            doc_id=str(uuid.uuid4()),
            title=title,
            content=text,
            source=filename,
            text_type='кулинарный текст'
        )
        
        return doc

    def add_document(self, doc: TextDocument):
        self.documents[doc.id] = doc
        self.save_index()

    def get_document(self, doc_id: str) -> TextDocument | None:
        return self.documents.get(doc_id)

    def get_all_documents(self) -> list[dict[str, Any]]:
        return [
            {
                'id': doc.id,
                'title': doc.title,
                'word_count': doc.word_count,
                'metadata': doc.to_dict()['metadata']
            }
            for doc in self.documents.values()
        ]

    def update_document(self, doc_id: str, content: str) -> TextDocument | None:
        doc = self.documents.get(doc_id)
        if not doc:
            return None
        doc.content = content
        doc.word_count = len(content.split())
        doc.char_count = len(content)
        self.save_index()
        return doc

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            del self.documents[doc_id]
            self.save_index()
            return True
        return False

    def analyze_document(self, doc_id: str) -> list[dict[str, Any]]:
        doc = self.get_document(doc_id)
        if not doc:
            return []
        
        return self.morph.analyze_text(doc.content)

    def get_lemmas(self, doc_id: str) -> dict[str, int]:
        doc = self.get_document(doc_id)
        if not doc:
            return {}
        
        analysis = self.morph.analyze_text(doc.content)
        lemmas: dict[str, int] = {}
        
        for item in analysis:
            lemma = item['analysis']['lemma']
            lemmas[lemma] = lemmas.get(lemma, 0) + 1
        
        return lemmas

    def get_wordform_frequencies(self, doc_id: str | None = None) -> dict[str, int]:
        if doc_id:
            doc = self.get_document(doc_id)
            if not doc:
                return {}
            analysis = self.morph.analyze_text(doc.content)
        else:
            analysis = []
            for doc in self.documents.values():
                analysis.extend(self.morph.analyze_text(doc.content))
        
        frequencies: dict[str, int] = {}
        for item in analysis:
            word = item['token'].lower()
            frequencies[word] = frequencies.get(word, 0) + 1
        
        return frequencies

    def get_lemma_frequencies(self, doc_id: str | None = None) -> dict[str, int]:
        if doc_id:
            doc = self.get_document(doc_id)
            if not doc:
                return {}
            analysis = self.morph.analyze_text(doc.content)
        else:
            analysis = []
            for doc in self.documents.values():
                analysis.extend(self.morph.analyze_text(doc.content))
        
        frequencies: dict[str, int] = {}
        for item in analysis:
            lemma = item['analysis']['lemma']
            frequencies[lemma] = frequencies.get(lemma, 0) + 1
        
        return frequencies

    def get_pos_statistics(self, doc_id: str | None = None) -> dict[str, int]:
        if doc_id:
            doc = self.get_document(doc_id)
            if not doc:
                return {}
            analysis = self.morph.analyze_text(doc.content)
        else:
            analysis = []
            for doc in self.documents.values():
                analysis.extend(self.morph.analyze_text(doc.content))
        
        pos_stats: dict[str, int] = {}
        for item in analysis:
            pos = item['analysis']['pos']
            pos_stats[pos] = pos_stats.get(pos, 0) + 1
        
        return pos_stats

    def get_grammar_statistics(self, doc_id: str | None = None) -> dict[str, dict[str, int]]:
        if doc_id:
            doc = self.get_document(doc_id)
            if not doc:
                return {}
            analysis = self.morph.analyze_text(doc.content)
        else:
            analysis = []
            for doc in self.documents.values():
                analysis.extend(self.morph.analyze_text(doc.content))
        
        case_stats: dict[str, int] = {}
        number_stats: dict[str, int] = {}
        gender_stats: dict[str, int] = {}
        
        for item in analysis:
            grammemes = item['analysis']['grammemes']
            if 'падеж' in grammemes:
                case_stats[grammemes['падеж']] = case_stats.get(grammemes['падеж'], 0) + 1
            if 'число' in grammemes:
                number_stats[grammemes['число']] = number_stats.get(grammemes['число'], 0) + 1
            if 'род' in grammemes:
                gender_stats[grammemes['род']] = gender_stats.get(grammemes['род'], 0) + 1
        
        return {
            'падежи': case_stats,
            'числа': number_stats,
            'роды': gender_stats
        }

    def search(self, query: str, doc_id: str | None = None) -> list[dict[str, Any]]:
        query_lower = query.lower()
        results = []
        
        docs = [self.get_document(doc_id)] if doc_id else self.documents.values()
        
        for doc in docs:
            if not doc:
                continue
            
            content_lower = doc.content.lower()
            start = 0
            while True:
                pos = content_lower.find(query_lower, start)
                if pos == -1:
                    break
                
                context_start = max(0, pos - 50)
                context_end = min(len(doc.content), pos + len(query) + 50)
                
                results.append({
                    'document_id': doc.id,
                    'document_title': doc.title,
                    'position': pos,
                    'context': doc.content[context_start:context_end]
                })
                
                start = pos + 1
        
        return results

    def concordance(self, query: str, doc_id: str | None = None, context: int = 5) -> list[dict[str, Any]]:
        query_lower = query.lower()
        results = []
        
        docs = [self.get_document(doc_id)] if doc_id else self.documents.values()
        
        for doc in docs:
            if not doc:
                continue
            
            words = doc.content.split()
            for i, word in enumerate(words):
                word_clean = word.lower().strip('.,!?;:"()[]')
                if word_clean == query_lower:
                    start = max(0, i - context)
                    end = min(len(words), i + context + 1)
                    
                    left = ' '.join(words[start:i])
                    center = words[i]
                    right = ' '.join(words[i+1:end])
                    
                    results.append({
                        'document_id': doc.id,
                        'document_title': doc.title,
                        'position': i,
                        'left': left,
                        'keyword': center,
                        'right': right,
                        'full_context': f"{left} {center} {right}"
                    })
        
        return results
