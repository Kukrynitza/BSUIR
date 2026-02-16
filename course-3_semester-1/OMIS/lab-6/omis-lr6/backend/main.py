import json
import asyncio
import re
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq


app = FastAPI(title="Team AI Planner with Groq")

client = Groq(api_key="GROQ_API_KEY")


class Developer(BaseModel):
    id: int
    lastName: str
    firstName: str
    position: str
    grade: str
    project: Optional[int]


class Task(BaseModel):
    id: int
    state: int
    developer: Optional[int]
    project: int
    description: str
    name: str
    time: Optional[str]


class RecommendRequest(BaseModel):
    developers: List[Developer]
    tasks: List[Task]
    currentTask: Task


class RecommendResponse(BaseModel):
    developerId: Optional[int]
    developerName: str
    estimatedDays: float
    confidence: float
    reason: str


class RiskyTask(BaseModel):
    id: int
    name: str
    risk: str 
    reason: str


class DeveloperEfficiency(BaseModel):
    id: int
    name: str
    completedTasks: int
    inProgressTasks: int
    efficiency: float
    grade: str


class ReportResponse(BaseModel):
    completion: float
    riskyTasks: List[RiskyTask]
    developerEfficiency: List[DeveloperEfficiency]


class ReportRequest(BaseModel):
    developers: List[Developer]
    tasks: List[Task]


RECOMMEND_PROMPT = """
Ты — AI-планировщик команды разработки.

На входе JSON с developers, tasks и currentTask.
Проанализируй загруженность, опыт, роль и важность задачи.

Верни СТРОГО JSON:

{
  "developerId": number | null,
  "developerName": string,
  "estimatedDays": number,
  "confidence": number,
  "reason": string
}

Никакого текста вне JSON.
""".strip()


REPORT_PROMPT = """
Ты — AI-аналитик проекта.

На входе JSON с developers и tasks.

Правила:
- completion = процент завершённых задач и находящихся на последних этапах
- riskyTasks:
    - не назначены на developer
    - или state < 6 и долго в работе
- developerEfficiency:
    - completedTasks
    - inProgressTasks
    - efficiency
    - grade

Верни СТРОГО JSON:

{
  "completion": number,
  "riskyTasks": [
    { "id": number, "name": string, "risk": "high" | "medium", "reason": string }
  ],
  "developerEfficiency": [
    {
      "id": number,
      "name": string,
      "completedTasks": number,
      "inProgressTasks": number,
      "efficiency": number,
      "grade": string
    }
  ]
}

Никакого текста вне JSON.
""".strip()


async def call_groq(prompt: str, data: dict):
    def sync_call():
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt + "\n\n" + json.dumps(data, ensure_ascii=False),
                }
            ],
        )
        return response.choices[0].message.content

    text = (await asyncio.to_thread(sync_call)).strip()

    if not text:
        raise HTTPException(500, "Groq вернул пустой ответ")

    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE).strip()

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise HTTPException(500, f"Groq вернул не JSON: {text}")

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        raise HTTPException(500, f"Groq вернул невалидный JSON: {json_text}")


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    return await call_groq(RECOMMEND_PROMPT, req.dict())


@app.post("/report", response_model=ReportResponse)
async def report(req: ReportRequest):
    return await call_groq(REPORT_PROMPT, req.dict())
