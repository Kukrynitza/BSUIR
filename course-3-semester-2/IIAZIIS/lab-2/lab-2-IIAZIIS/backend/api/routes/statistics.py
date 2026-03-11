from fastapi import APIRouter, Query
from core.dependencies import corpus

router = APIRouter(tags=["Статистика"])


@router.get("/stats/wordforms")
async def get_wordform_frequencies(
    doc_id: str | None = Query(None, description="ID документа (опционально)"),
    limit: int = Query(50, description="Количество слов в топе")
):
    frequencies = corpus.get_wordform_frequencies(doc_id)
    
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    top = sorted_freq[:limit]
    
    return {
        "type": "wordforms",
        "total_unique": len(frequencies),
        "total_tokens": sum(frequencies.values()),
        "frequencies": [{"word": w, "count": c} for w, c in top]
    }


@router.get("/stats/lemmas")
async def get_lemma_frequencies(
    doc_id: str | None = Query(None, description="ID документа (опционально)"),
    limit: int = Query(50, description="Количество лемм в топе")
):
    frequencies = corpus.get_lemma_frequencies(doc_id)
    
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    top = sorted_freq[:limit]
    
    return {
        "type": "lemmas",
        "total_unique": len(frequencies),
        "total_tokens": sum(frequencies.values()),
        "frequencies": [{"lemma": l, "count": c} for l, c in top]
    }


@router.get("/stats/pos")
async def get_pos_statistics(
    doc_id: str | None = Query(None, description="ID документа (опционально)")
):
    pos_stats = corpus.get_pos_statistics(doc_id)
    
    total = sum(pos_stats.values())
    percentages = {
        pos: round((count / total * 100), 2) if total > 0 else 0
        for pos, count in pos_stats.items()
    }
    
    return {
        "type": "parts_of_speech",
        "total": total,
        "statistics": [
            {"pos": pos, "count": count, "percentage": percentages[pos]}
            for pos, count in sorted(pos_stats.items(), key=lambda x: x[1], reverse=True)
        ]
    }


@router.get("/stats/grammars")
async def get_grammar_statistics(
    doc_id: str | None = Query(None, description="ID документа (опционально)")
):
    grammar_stats = corpus.get_grammar_statistics(doc_id)
    
    result = {"type": "grammatical_categories"}
    
    for category, stats in grammar_stats.items():
        total = sum(stats.values())
        percentages = {
            val: round((count / total * 100), 2) if total > 0 else 0
            for val, count in stats.items()
        }
        result[category] = {
            "total": total,
            "values": [
                {"value": v, "count": c, "percentage": percentages[v]}
                for v, c in sorted(stats.items(), key=lambda x: x[1], reverse=True)
            ]
        }
    
    return result


@router.get("/stats/overview")
async def get_overview():
    total_docs = len(corpus.documents)
    total_words = sum(doc.word_count for doc in corpus.documents.values())
    
    wordform_freq = corpus.get_wordform_frequencies()
    lemma_freq = corpus.get_lemma_frequencies()
    pos_stats = corpus.get_pos_statistics()
    
    return {
        "total_documents": total_docs,
        "total_words": total_words,
        "unique_wordforms": len(wordform_freq),
        "unique_lemmas": len(lemma_freq),
        "parts_of_speech": len(pos_stats)
    }
