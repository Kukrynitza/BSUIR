"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getTasks } from "@/actions/tasks/get"
import { updateTask } from "@/actions/tasks/update"
import { getTaskStateInfo } from "@/types"
import { calculateTaskSpeed } from "@/utils/taskSpeed"
import type { Task } from "@/types"
import styles from "../../developer.module.css"

export default async function TaskDetailPage({ params }: { params: Promise<{ id: string; taskId: string }> }) {
  const resolvedParams = await params
  const developerId = Number.parseInt(resolvedParams.id)
  const taskId = Number.parseInt(resolvedParams.taskId)

  return <TaskDetailPageClient developerId={developerId} taskId={taskId} />
}

function TaskDetailPageClient({ developerId, taskId }: { developerId: number; taskId: number }) {
  const [task, setTask] = useState<Task | null>(null)

  useEffect(() => {
    loadTask()
  }, [taskId])

  async function loadTask() {
    const allTasks = await getTasks()
    const taskData = allTasks.find((t) => t.id === taskId)
    setTask(taskData || null)
  }

  async function handleUpdateState(newState: number) {
    if (!task) return
    await updateTask(taskId, { ...task, state: newState })
    loadTask()
  }

  if (!task) return <div className={styles.container}>Загрузка...</div>

  const stateInfo = getTaskStateInfo(task.state)
  const speedInfo = calculateTaskSpeed(task)

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>{task.name}</h1>
        <Link href={`/developer/${developerId}`} className={styles.backLink}>
          ← К моим задачам
        </Link>
      </div>

      <div className={styles.content}>
        <div className={styles.infoSection}>
          <h2 className={styles.sectionTitle}>Описание задачи</h2>
          <p style={{ color: "#64748b", lineHeight: 1.6, fontSize: "1rem" }}>{task.description}</p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", marginBottom: "2rem" }}>
          <div className={styles.infoSection}>
            <h2 className={styles.sectionTitle}>Текущее состояние</h2>
            <div style={{ textAlign: "center", padding: "2rem" }}>
              <span
                className={styles.stateBadge}
                style={{ backgroundColor: stateInfo.color, fontSize: "1.1rem", padding: "0.75rem 1.5rem" }}
              >
                {stateInfo.label}
              </span>
            </div>
          </div>

          {task.time && (
            <div className={styles.infoSection}>
              <h2 className={styles.sectionTitle}>Срок выполнения</h2>
              <div style={{ textAlign: "center", padding: "2rem" }}>
                <div style={{ fontSize: "1.5rem", fontWeight: 600, color: "#1e293b" }}>
                  {new Date(task.time).toLocaleDateString("ru-RU", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })}
                </div>
                <div style={{ marginTop: "0.5rem", color: "#64748b" }}>Осталось дней: {speedInfo.daysLeft}</div>
              </div>
            </div>
          )}
        </div>

        {task.time && (
          <div
            className={styles.infoSection}
            style={{
              background:
                speedInfo.status === "critical"
                  ? "#fee2e2"
                  : speedInfo.status === "behind"
                    ? "#fef3c7"
                    : speedInfo.status === "on-track"
                      ? "#dbeafe"
                      : "#dcfce7",
              border: "2px solid",
              borderColor:
                speedInfo.status === "critical"
                  ? "#ef4444"
                  : speedInfo.status === "behind"
                    ? "#f59e0b"
                    : speedInfo.status === "on-track"
                      ? "#3b82f6"
                      : "#22c55e",
            }}
          >
            <h2 className={styles.sectionTitle}>Анализ скорости работы</h2>
            <div style={{ marginBottom: "1rem" }}>
              <strong>Прогресс:</strong> {speedInfo.currentProgress}% завершено
            </div>
            <div style={{ marginBottom: "1rem" }}>
              <strong>Необходимая скорость:</strong> {speedInfo.requiredSpeed.toFixed(2)}% работы в день
            </div>
            <div
              style={{
                padding: "1rem",
                background: "white",
                borderRadius: "8px",
                fontWeight: 600,
                color:
                  speedInfo.status === "critical"
                    ? "#dc2626"
                    : speedInfo.status === "behind"
                      ? "#d97706"
                      : speedInfo.status === "on-track"
                        ? "#2563eb"
                        : "#16a34a",
              }}
            >
              {speedInfo.message}
            </div>
          </div>
        )}

        <div className={styles.infoSection}>
          <h2 className={styles.sectionTitle}>Изменить состояние задачи</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "0.75rem" }}>
            {[0, 1, 2, 3, 4, 5, 6, 7].map((state) => {
              const info = getTaskStateInfo(state)
              return (
                <button
                  key={state}
                  onClick={() => handleUpdateState(state)}
                  className={styles.button}
                  style={{
                    background: task.state === state ? info.color : "#f1f5f9",
                    color: task.state === state ? "white" : "#475569",
                    border: task.state === state ? `2px solid ${info.color}` : "2px solid #e2e8f0",
                    fontWeight: task.state === state ? 600 : 500,
                  }}
                >
                  {info.label}
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
