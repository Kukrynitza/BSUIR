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
  state: number // 0-7
  developer: number | null
  project: number
  description: string
  name: string
  time: Date | null
}

export interface Project {
  id: number
  description: string
  name: string
}

export enum TaskState {
  NEW = 0,
  ASSIGNED = 1,
  IN_PROGRESS = 2,
  CODE_REVIEW = 3,
  TESTING = 4,
  FIXING = 5,
  READY = 6,
  COMPLETED = 7,
}

export interface ProjectReport {
  projectId: number
  completionPercentage: number
  riskyTasks: Array<{
    taskId: number
    taskName: string
    riskLevel: string
    reason: string
  }>
  developerEfficiency: Array<{
    developerId: number
    developerName: string
    efficiency: number
    tasksCompleted: number
    averageTime: number
  }>
}

export interface TaskAssignmentRecommendation {
  recommendedDeveloperId: number
  developerName: string
  estimatedTime: number // в часах
  reason: string
  confidence: number // 0-100
}

export type UserRole = "developer" | "manager" | "customer"

export const getTaskStateInfo = (state: number): { label: string; color: string } => {
  const states: Record<number, { label: string; color: string }> = {
    0: { label: "Новая", color: "#94a3b8" },
    1: { label: "Назначена", color: "#60a5fa" },
    2: { label: "В работе", color: "#fbbf24" },
    3: { label: "Code Review", color: "#a78bfa" },
    4: { label: "Тестирование", color: "#fb923c" },
    5: { label: "Исправления", color: "#f87171" },
    6: { label: "Готова", color: "#4ade80" },
    7: { label: "Завершена", color: "#22c55e" },
  }
  return states[state] || states[0]
}
