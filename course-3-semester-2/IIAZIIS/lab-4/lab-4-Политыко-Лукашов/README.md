# Семантико-синтаксический анализ (DOCX)

Синтаксический пайплайн, семантические роли и связи, загрузка **DOCX**. Внешнее обогащение концептов через ConceptNet **по умолчанию выключено** (без сетевых запросов при анализе).

## Запуск

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Переменные окружения (опционально):

- `CONCEPTNET_ENABLED=1` — включить запросы к ConceptNet (иначе только правила / локальный fallback).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Прокси к API: `vite.config.ts` → `http://localhost:8001` (префикс `/api`).

## Проверка

1. Загрузить `.docx`, выполнить анализ документа.
2. В ответе анализа у предложений: `semantic_annotations`, `semantic_links`.
3. Вкладка «Деревья»: семантика по прямому тексту; для документа — таблицы после анализа.
4. `GET /api/documents/{id}/semantic-export` — JSON с семантикой.

## Замер быстродействия

В ответах есть `analysis_time_ms`. Пример:

```bash
cd backend
source .venv/bin/activate
python -c "
import time
from pathlib import Path
from core.corpus.manager import SyntaxManager
m = SyntaxManager(Path('data'))
text = 'Кот спит на диване. Собака гуляет во дворе.'
t0 = time.perf_counter()
r = m.analyze_text_trees(text)
print('sentences', len(r['dependency_trees']), 'ms', round((time.perf_counter()-t0)*1000, 2))
"
```

## Тесты

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -q
```

## Структура

- `backend/core/shared/parser/docx_parser.py` — текст из DOCX
- `backend/core/shared/semantic/` — семантика и адаптер знаний
- `frontend/src/components/SemanticPanel.tsx` — UI семантики (таблицы, фильтры, граф связей)
- `frontend/src/components/SemanticGraph.tsx` — SVG-визуализация проекции зависимостей
