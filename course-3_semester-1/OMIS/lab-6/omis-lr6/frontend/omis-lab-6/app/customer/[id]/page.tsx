"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getProjects } from "@/actions/projects/get"
import { getTasks } from "@/actions/tasks/get"
import { getDevelopers } from "@/actions/developers/get"
import { createTask } from "@/actions/tasks/create"
import { getReport } from "@/actions/reports/getReport"
import { getTaskStateInfo } from "@/types"
import type { Project, Task, ProjectReport, Developer } from "@/types"
import styles from './project.module.css'

export default function CustomerProjectPage({ params }: { params: { id: string } }) {
  const projectId = Number(params.id)
  return <CustomerProjectPageClient projectId={projectId} />
}

function CustomerProjectPageClient({ projectId }: { projectId: number }) {
  const [project, setProject] = useState<Project | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [report, setReport] = useState<ProjectReport | null>(null)
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [showReport, setShowReport] = useState(false)
  const [newTask, setNewTask] = useState({ name: "", description: "" })

  useEffect(() => {
    loadData()
  }, [projectId])

  async function loadData() {
    const [allProjects, allTasks] = await Promise.all([
      getProjects(),
      getTasks(),
    ])

    setProject(allProjects.find(p => p.id === projectId) || null)
    setTasks(allTasks.filter(t => t.project === projectId))
  }

  async function handleToggleReport() {
    if (showReport) {
      setShowReport(false)
      return
    }

    const developers = await getDevelopers()
    const projectDevelopers = developers.filter(d => d.project === projectId)

    const reportData = await getReport(tasks, projectDevelopers)
    setReport(reportData)
    setShowReport(true)
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

  if (!project) return <div className={styles.container}>Загрузка...</div>

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>{project.name}</h1>
        <Link href="/customer" className={styles.backLink}>
          ← К списку проектов
        </Link>
      </div>

      <div className={styles.content}>
        <div style={{ marginBottom: "2rem", display: "flex", gap: "1rem", justifyContent: "center" }}>
          <button className={`${styles.button} ${styles.buttonPrimary}`} onClick={() => setShowTaskModal(true)}>
            Добавить задачу
          </button>
          <button className={`${styles.button} ${styles.buttonSecondary}`} onClick={handleToggleReport}>
            {showReport ? "Скрыть отчет" : "Посмотреть отчет"}
          </button>
        </div>

        {showReport && report && (
          <div className={styles.reportSection}>
            <h2 className={styles.reportTitle}>Отчет по проекту</h2>

            <div style={{ marginBottom: "3rem" }}>
              <h3>Прогресс выполнения</h3>
              <div className={styles.completionBar}>
                <div className={styles.completionFill} style={{ width: `${report.completion}%` }}>
                  {report.completion}%
                </div>
              </div>
            </div>

            {report.riskyTasks.length > 0 && (
              <div style={{ marginBottom: "3rem" }}>
                <h3>Рискованные задачи</h3>
                <div className={styles.riskList}>
                  {report.riskyTasks.map(task => (
                    <div
                      key={task.id}
                      className={`${styles.riskItem} ${styles[`risk${task.risk === "high" ? "High" : "Medium"}`]}`}
                    >
                      <div className={styles.riskItemTitle}>{task.name}</div>
                      <div className={styles.riskItemReason}>{task.reason}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div>
              <h3>Эффективность команды</h3>
              <div className={styles.efficiencyList}>
                {report.developerEfficiency.map(dev => (
                  <div key={dev.id} className={styles.efficiencyItem}>
                    <div className={styles.efficiencyInfo}>
                      <h4>{dev.name}</h4>
                      <div className={styles.efficiencyStats}>
                        Завершено: {dev.completedTasks} | В работе: {dev.inProgressTasks}
                      </div>
                    </div>
                    <div className={styles.efficiencyScore}>{dev.efficiency}%</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className={styles.infoSection}>
          <h2>Задачи проекта</h2>
          <div className={styles.tasksList}>
            {tasks.map(task => {
              const stateInfo = getTaskStateInfo(task.state)
              return (
                <div key={task.id} className={styles.taskCard} style={{ borderLeftColor: stateInfo.color }}>
                  <h3>{task.name}</h3>
                  <p>{task.description}</p>
                  <span style={{ backgroundColor: stateInfo.color }} className={styles.stateBadge}>
                    {stateInfo.label}
                  </span>
                </div>
              )
            })}

            {tasks.length === 0 && <p style={{ textAlign: "center" }}>Задач пока нет</p>}
          </div>
        </div>
      </div>

      {showTaskModal && (
        <div className={styles.modal} onClick={() => setShowTaskModal(false)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <h2>Добавить задачу</h2>

            <input
              value={newTask.name}
              onChange={e => setNewTask({ ...newTask, name: e.target.value })}
              placeholder="Название задачи"
              className={styles.input}
            />

            <textarea
              value={newTask.description}
              onChange={e => setNewTask({ ...newTask, description: e.target.value })}
              placeholder="Описание задачи"
              className={styles.textarea}
            />

            <div className={styles.modalActions}>
              <button onClick={() => setShowTaskModal(false)}>Отмена</button>
              <button onClick={handleCreateTask}>Добавить</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
