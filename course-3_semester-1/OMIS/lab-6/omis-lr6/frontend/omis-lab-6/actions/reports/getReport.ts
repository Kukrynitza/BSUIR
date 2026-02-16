"use server"

export interface ProjectReport {
  completion: number
  riskyTasks: Array<{
    id: number
    name: string
    risk: "high" | "medium"
    reason: string
  }>
  developerEfficiency: Array<{
    id: number
    name: string
    completedTasks: number
    inProgressTasks: number
    efficiency: number
    grade: string
  }>
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

const AI_REPORT_URL = "http://localhost:8000/report"

export async function getReport(
  tasks: Task[],
  developers: Developer[]
): Promise<ProjectReport> {
  const payload = {
    developers,
    tasks: tasks.map((t) => ({
      ...t,
      time: t.time ? t.time.toISOString() : null,
    })),
  }

  const res = await fetch(AI_REPORT_URL, {
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
    throw new Error(`AI report error ${res.status}: ${text}`)
  }

  return res.json()
}
