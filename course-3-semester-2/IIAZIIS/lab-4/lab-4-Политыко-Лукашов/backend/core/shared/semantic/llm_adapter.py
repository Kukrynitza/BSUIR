import os
import json
import logging
import httpx
import re
from typing import Any

logger = logging.getLogger(__name__)

class LLMAdapter:
    
    def __init__(self):
        self.model = os.environ.get("OLLAMA_MODEL", "llama3")
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.enabled = True

    def _parse_llm_response(self, text: str) -> list[dict[str, Any]]:
        results = []
        
        try:
            match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'token_id' in item:
                            results.append({
                                "token_id": int(item['token_id']), 
                                "concept_label": str(item.get('concept_label', ''))
                            })
                    if results: return results
                elif isinstance(data, dict):
                    if 'token_id' in data:
                        return [{"token_id": int(data['token_id']), "concept_label": str(data.get('concept_label', ''))}]
                    else:
                        for k, v in data.items():
                            try:
                                results.append({"token_id": int(k), "concept_label": str(v)})
                            except ValueError: continue
                        if results: return results
        except Exception:
            pass

        lines = text.split('\n')
        for line in lines:
            match = re.search(r'(?:ID\s*)?(\d+)[:\)]\s*(.+)', line)
            if match:
                tid = int(match.group(1))
                label = match.group(2).strip()
                label = label.rstrip(',. ')
                results.append({"token_id": tid, "concept_label": label})

        return results

    async def analyze_semantics(self, sentence_text: str, tokens_info: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.enabled:
            return []

        tokens_desc = "\n".join([
            f"ID {t['id']}: \"{t['text']}\" ({t['pos']})"
            for t in tokens_info
        ])

        system_prompt = (
            "Ты профессиональный лингвист. Твоя единственная задача — дать краткое определение (concept_label) "
            "на РУССКОМ языке для каждого токена, исходя из контекста предложения. "
            "Определение должно быть существительным или словосочетанием, описывающим сущность. "
            "ЗАПРЕЩЕНО писать части речи (NOUN, VERB и т.д.) в качестве определения.\n\n"
            "ПРИМЕРЫ:\n"
            "Предложение: \"Кот спит на ковре.\"\n"
            "Токены: ID 1: Кот (NOUN), ID 2: спит (VERB), ID 3: на (PREP), ID 4: ковре (NOUN)\n"
            "Ответ: 1: домашнее животное, 2: процесс сна, 3: предлог места, 4: ковровое покрытие\n\n"
            "Верни ответ в формате 'ID: определение'. Один токен на строку. Без вступлений."
        )

        user_prompt = (
            f"Предложение: \"{sentence_text}\"\n\n"
            f"Токены:\n{tokens_desc}\n\n"
            "Ответ:"
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                    },
                )
                response.raise_for_status()
                result_text = response.json().get("message", {}).get("content", "")
                
                return self._parse_llm_response(result_text)

        except Exception as e:
            logger.error(f"Ollama Analysis Error: {e}")
            return []


        tokens_desc = "\n".join([
            f"ID {t['id']}: \"{t['text']}\" ({t['pos']})"
            for t in tokens_info
        ])

        system_prompt = (
            "Ты профессиональный лингвист. Твоя единственная задача — дать краткое определение (concept_label) "
            "на РУССКОМ языке для каждого токена, исходя из контекста предложения. "
            "Определение должно быть существительным или словосочетанием, описывающим сущность. "
            "ЗАПРЕЩЕНО писать части речи (NOUN, VERB и т.д.) в качестве определения.\n\n"
            "ПРИМЕРЫ:\n"
            "Предложение: \"Кот спит на ковре.\"\n"
            "Токены: ID 1: Кот (NOUN), ID 2: спит (VERB), ID 3: на (PREP), ID 4: ковре (NOUN)\n"
            "Ответ: 1: домашнее животное, 2: процесс сна, 3: предлог места, 4: ковровое покрытие\n\n"
            "Верни ответ в формате 'ID: определение'. Один токен на строку. Без вступлений."
        )

        user_prompt = (
            f"Предложение: \"{sentence_text}\"\n\n"
            f"Токены:\n{tokens_desc}\n\n"
            "Ответ:"
        )

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                    },
                )
                response.raise_for_status()
                result_text = response.json().get("message", {}).get("content", "")
                
                return self._parse_llm_response(result_text)

        except Exception as e:
            logger.error(f"Ollama Analysis Error: {e}")
            return []
