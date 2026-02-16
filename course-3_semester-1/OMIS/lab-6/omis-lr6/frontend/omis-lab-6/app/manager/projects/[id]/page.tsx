"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getProjects } from "@/actions/projects/get"
import { getTasks } from "@/actions/tasks/get"
import { createTask } from "@/actions/tasks/create"
import { deleteTask } from "@/actions/tasks/delete"
import { updateTask } from "@/actions/tasks/update"
import { getDevelopers } from "@/actions/developers/get"
import { getRecommendation } from "@/actions/recommendations/getRecommendation"
import { getTaskStateInfo } from "@/types"
import type { Project, Task, Developer } from "@/types"
import styles from "../../styles.module.css"

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params
  const projectId = Number.parseInt(resolvedParams.id)

  return <ProjectPageClient projectId={projectId} />
}

function ProjectPageClient({ projectId }: { projectId: number }) {
  const [project, setProject] = useState<Project | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [developers, setDevelopers] = useState<Developer[]>([])
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [showTimeModal, setShowTimeModal] = useState(false) // Добавил showTimeModal в состояние
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null)
  const [aiRecommendation, setAiRecommendation] = useState<{
    confidence: number
    developerId: number
    developerName: string
    estimatedDays: number
    reason: string
  } | null>(null)
  const [newTask, setNewTask] = useState({ name: "", description: "" })
  const [newTime, setNewTime] = useState("") // Изменил тип newTime на string вместо string | null

  useEffect(() => {
    loadData()
  }, [projectId])

  async function loadData() {
    const [allProjects, allTasks, allDevs] = await Promise.all([getProjects(), getTasks(), getDevelopers()])
    const projectData = allProjects.find((p) => p.id === projectId)
    const tasksData = allTasks.filter((t) => t.project === projectId)
    const devsData = allDevs.filter((d) => d.project === projectId)

    setProject(projectData || null)
    setTasks(tasksData)
    setDevelopers(devsData)
  }

  async function handleCreateTask() {
    if (!newTask.name.trim()) return

    await createTask({
      name: newTask.name,
      description: newTask.description,
      project: projectId,
      state: 0,
      developer: null,
      time: null,
    })
    setNewTask({ name: "", description: "" })
    setShowTaskModal(false)
    loadData()
  }

  async function handleDeleteTask(taskId: number) {
    if (confirm("Вы уверены, что хотите удалить задачу?")) {
      await deleteTask(taskId)
      loadData()
    }
  }

  async function handleAssignDeveloper(taskId: number, developerId: number | null) {
    const task = tasks.find((t) => t.id === taskId)
    if (!task) return
    await updateTask(taskId, { ...task, developer: developerId })
    setShowAssignModal(false)
    setSelectedTaskId(null)
    setAiRecommendation(null)
    loadData()
  }

  async function handleGetRecommendation(taskId: number) {
    setSelectedTaskId(taskId)
    console.log(developers)
    console.log(tasks)
    const recommendation = await getRecommendation(developers, tasks, taskId)
    console.log(recommendation)
    setAiRecommendation(recommendation)
    setShowAssignModal(true)
  }

  async function handleSetTime(taskId: number) {
    if (!newTime) return
    const task = tasks.find((t) => t.id === taskId)
    if (!task) return
    await updateTask(taskId, { ...task, time: new Date(newTime) })
    setShowTimeModal(false)
    setSelectedTaskId(null)
    setNewTime("")
    loadData()
  }

  if (!project) return <div className={styles.container}>Загрузка...</div>

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>{project.name}</h1>
        <Link href="/manager" className={styles.backLink}>
          ← К списку проектов
        </Link>
      </div>

      <div className={styles.content}>
        <div style={{ marginBottom: "2rem", display: "flex", gap: "1rem" }}>
          <button className={`${styles.button} ${styles.buttonPrimary}`} onClick={() => setShowTaskModal(true)}>
            Создать задачу
          </button>
          <Link href={`/manager/projects/${projectId}/team`}>
            <button className={`${styles.button} ${styles.buttonSecondary}`}>Управление командой</button>
          </Link>
          <Link href={`/manager/projects/${projectId}/report`}>
            <button className={`${styles.button} ${styles.buttonSecondary}`}>Отчет по проекту</button>
          </Link>
        </div>

        <div className={styles.tasksList}>
          {tasks.map((task) => {
            const stateInfo = getTaskStateInfo(task.state)
            const assignedDev = developers.find((d) => d.id === task.developer)

            return (
              <div key={task.id} className={styles.taskCard} style={{ borderLeftColor: stateInfo.color }}>
                <div className={styles.taskHeader}>
                  <div className={styles.taskInfo}>
                    <h3 className={styles.taskName}>{task.name}</h3>
                    <p className={styles.taskDescription}>{task.description}</p>

                    <div className={styles.taskMeta}>
                      <div className={styles.taskMetaItem}>
                        <span className={styles.stateBadge} style={{ backgroundColor: stateInfo.color }}>
                          {stateInfo.label}
                        </span>
                      </div>
                      <div className={styles.taskMetaItem}>
                        👤 {assignedDev ? `${assignedDev.firstName} ${assignedDev.lastName}` : "Не назначена"}
                      </div>
                      {task.time && (
                        <div className={styles.taskMetaItem}>⏱️ {new Date(task.time).toLocaleDateString()}</div>
                      )}
                    </div>
                  </div>

                  <div className={styles.actionButtons}>
                    <button
                      className={styles.iconButton}
                      onClick={() => {
                        setSelectedTaskId(task.id)
                        setShowAssignModal(true)
                        setAiRecommendation(null)
                      }}
                      title="Назначить разработчика"
                    >
                      👤
                    </button>
                    <button
                      className={styles.iconButton}
                      onClick={() => handleGetRecommendation(task.id)}
                      title="Получить AI рекомендацию"
                    >
                      🤖
                    </button>
                    <button
                      className={styles.iconButton}
                      onClick={() => {
                        setSelectedTaskId(task.id)
                        setShowTimeModal(true)
                      }}
                      title="Установить срок"
                    >
                      ⏱️
                    </button>
                    <button
                      className={`${styles.iconButton} ${styles.iconButtonDanger}`}
                      onClick={() => handleDeleteTask(task.id)}
                      title="Удалить задачу"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            )
          })}

          {tasks.length === 0 && (
            <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>
              <p>Задач пока нет. Создайте первую задачу для проекта.</p>
            </div>
          )}
        </div>
      </div>

      {showTaskModal && (
        <div className={styles.modal} onClick={() => setShowTaskModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2 className={styles.modalTitle}>Создать новую задачу</h2>

            <div className={styles.formGroup}>
              <label className={styles.label}>Название задачи</label>
              <input
                type="text"
                className={styles.input}
                value={newTask.name}
                onChange={(e) => setNewTask({ ...newTask, name: e.target.value })}
                placeholder="Введите название задачи"
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Описание</label>
              <textarea
                className={styles.textarea}
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                placeholder="Введите описание задачи"
              />
            </div>

            <div className={styles.modalActions}>
              <button className={`${styles.button} ${styles.buttonSecondary}`} onClick={() => setShowTaskModal(false)}>
                Отмена
              </button>
              <button className={`${styles.button} ${styles.buttonPrimary}`} onClick={handleCreateTask}>
                Создать
              </button>
            </div>
          </div>
        </div>
      )}

      {showAssignModal && selectedTaskId && (
        <div className={styles.modal} onClick={() => setShowAssignModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2 className={styles.modalTitle}>Назначить разработчика</h2>

            {aiRecommendation && (
              <div className={styles.aiRecommendation}>
                <div className={styles.aiTitle}>
                  <span>🤖</span> AI Рекомендация
                </div>
                <div className={styles.aiContent}>
                  <strong>Рекомендуется:</strong> {aiRecommendation.developerName}
                  <br />
                  <strong>Оценка времени:</strong> {aiRecommendation.estimatedDays} дней
                  <br />
                  <strong>Обоснование:</strong> {aiRecommendation.reason}
                  <div className={styles.confidence}>Уверенность: {aiRecommendation.confidence}%</div>
                </div>
              </div>
            )}

            <div className={styles.formGroup}>
              <label className={styles.label}>Выберите разработчика</label>
              <select
                className={styles.select}
                defaultValue=""
                onChange={(e) => {
                  const devId = e.target.value ? Number.parseInt(e.target.value) : null
                  handleAssignDeveloper(selectedTaskId, devId)
                }}
              >
                <option value="">-- Выберите разработчика --</option>
                {developers.map((dev) => (
                  <option key={dev.id} value={dev.id}>
                    {dev.firstName} {dev.lastName} ({dev.position}, {dev.grade})
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.modalActions}>
              <button
                className={`${styles.button} ${styles.buttonSecondary}`}
                onClick={() => {
                  setShowAssignModal(false)
                  setAiRecommendation(null)
                  setSelectedTaskId(null)
                }}
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {showTimeModal && selectedTaskId && (
        <div className={styles.modal} onClick={() => setShowTimeModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2 className={styles.modalTitle}>Установить срок выполнения</h2>

            <div className={styles.formGroup}>
              <label className={styles.label}>Дата завершения</label>
              <input
                type="date"
                className={styles.input}
                value={newTime}
                onChange={(e) => setNewTime(e.target.value)}
              />
            </div>

            <div className={styles.modalActions}>
              <button
                className={`${styles.button} ${styles.buttonSecondary}`}
                onClick={() => {
                  setShowTimeModal(false)
                  setSelectedTaskId(null)
                  setNewTime("")
                }}
              >
                Отмена
              </button>
              <button
                className={`${styles.button} ${styles.buttonPrimary}`}
                onClick={() => handleSetTime(selectedTaskId)}
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
