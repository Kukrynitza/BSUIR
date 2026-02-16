import type { Task } from "@/types"

export interface TaskSpeedInfo {
  daysLeft: number
  currentProgress: number
  requiredSpeed: number
  status: "ahead" | "on-track" | "behind" | "critical"
  message: string
}

export function calculateTaskSpeed(task: Task): TaskSpeedInfo {
  if (!task.time) {
    return {
      daysLeft: 0,
      currentProgress: 0,
      requiredSpeed: 0,
      status: "on-track",
      message: "Срок выполнения не установлен",
    }
  }

  const now = new Date()
  const deadline = new Date(task.time)
  const daysLeft = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

  // Прогресс задачи в процентах (state от 0 до 7)
  const currentProgress = Math.round((task.state / 7) * 100)

  // Требуемая скорость: сколько процентов нужно делать в день
  const requiredSpeed = daysLeft > 0 ? (100 - currentProgress) / daysLeft : 100

  let status: "ahead" | "on-track" | "behind" | "critical"
  let message: string

  if (daysLeft < 0) {
    status = "critical"
    message = `Просрочена на ${Math.abs(daysLeft)} дней! Требуется срочное завершение.`
  } else if (daysLeft === 0) {
    status = "critical"
    message = "Срок истекает сегодня! Необходимо завершить задачу."
  } else if (currentProgress >= 100) {
    status = "ahead"
    message = "Задача завершена досрочно!"
  } else if (requiredSpeed > 20) {
    status = "critical"
    message = `Критическое отставание! Необходимо завершать ${requiredSpeed.toFixed(1)}% работы в день.`
  } else if (requiredSpeed > 14) {
    status = "behind"
    message = `Отставание от графика. Требуется ${requiredSpeed.toFixed(1)}% работы в день.`
  } else if (requiredSpeed > 10) {
    status = "on-track"
    message = `В рамках графика. Требуется ${requiredSpeed.toFixed(1)}% работы в день.`
  } else {
    status = "ahead"
    message = `Опережение графика! Достаточно ${requiredSpeed.toFixed(1)}% работы в день.`
  }

  return {
    daysLeft,
    currentProgress,
    requiredSpeed,
    status,
    message,
  }
}
