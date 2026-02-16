"use server"

export interface AIRecommendation {
  developerId: number | null
  developerName: string
  estimatedDays: number
  confidence: number
  reason: string
}

export interface Developer {
  id: number
  lastName: string
  firstName: string
  position: string
  grade: string
  project: number | null
}

export interface Task {
  id: number
  state: number
  developer: number | null
  project: number
  description: string
  name: string
  time: Date | null
}

const AI_API_URL = "http://localhost:8000/recommend"

export async function getRecommendation(
  developers: Developer[],
  tasks: Task[],
  taskId: number
): Promise<AIRecommendation> {
  const currentTask = tasks.find((t) => t.id === taskId)

  if (!currentTask) {
    return {
      developerId: null,
      developerName: "Задача не найдена",
      estimatedDays: 0,
      confidence: 0,
      reason: "Передан некорректный taskId",
    }
  }

  const payload = {
    developers,
    tasks: tasks.map((t) => ({
      ...t,
      time: t.time ? t.time.toISOString() : null,
    })),
    currentTask: {
      ...currentTask,
      time: currentTask.time ? currentTask.time.toISOString() : null,
    },
  }

  const res = await fetch(AI_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`AI error ${res.status}: ${text}`)
  }

  return res.json()
}
