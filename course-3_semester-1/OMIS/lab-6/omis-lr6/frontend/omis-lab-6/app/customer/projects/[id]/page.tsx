"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getById } from "@/actions/projects/getById"
import { getTasks } from "@/actions/tasks/get"
import { createTask } from "@/actions/tasks/create"
import { getReport } from "@/actions/reports/getReport"
import type { Project, Task, ProjectReport } from "@/types"
import styles from "./project.module.css"

export default async function CustomerProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const projectId = Number.parseInt(id)

  const [project, setProject] = useState<Project | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [report, setReport] = useState<ProjectReport | null>(null)
  const [showReport, setShowReport] = useState(false)
  const [showAddTask, setShowAddTask] = useState(false)
  const [newTaskName, setNewTaskName] = useState("")
  const [newTaskDescription, setNewTaskDescription] = useState("")

  useEffect(() => {
    loadData()
  }, [projectId])

  async function loadData() {
    const projectData = await getById(projectId)
    setProject(projectData)

    const tasksData = await getTasks()
    const projectTasks = tasksData.filter((t) => t.project === projectId)
    setTasks(projectTasks)
  }

  async function handleLoadReport() {
        const [projects, developers] = await Promise.all([
          getProjects(),
          getDevelopers(),
        ])
        const projectDevelopers = developers.filter((d) => d.project === projectId)
    if (!showReport) {
      const reportData = await getReport(tasks, projectDevelopers)
      setReport(reportData)
    }
    setShowReport(!showReport)
  }

  async function handleAddTask() {
    if (newTaskName.trim() && newTaskDescription.trim()) {
      await createTask({projectId, newTaskName, newTaskDescription})
      setNewTaskName("")
      setNewTaskDescription("")
      setShowAddTask(false)
      loadData()
    }
  }

  if (!project) {
    return (
      <div className={styles.container}>
        <p>Загрузка...</p>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>{project.name}</h1>
          <p className={styles.description}>{project.description}</p>
        </div>
        <Link href="/customer" className={styles.backLink}>
          Назад к проектам
        </Link>
      </div>

      <div className={styles.content}>
        <div className={styles.actions}>
          <button onClick={() => setShowAddTask(!showAddTask)} className={styles.actionButton}>
            {showAddTask ? "Отменить" : "Добавить задачу"}
          </button>
          <button onClick={handleLoadReport} className={styles.actionButton}>
            {showReport ? "Скрыть отчет" : "Показать отчет"}
          </button>
        </div>

        {showAddTask && (
          <div className={styles.addTaskForm}>
            <h3>Новая задача</h3>
            <input
              type="text"
              placeholder="Название задачи"
              value={newTaskName}
              onChange={(e) => setNewTaskName(e.target.value)}
              className={styles.input}
            />
            <textarea
              placeholder="Описание задачи"
              value={newTaskDescription}
              onChange={(e) => setNewTaskDescription(e.target.value)}
              className={styles.textarea}
              rows={4}
            />
            <button onClick={handleAddTask} className={styles.submitButton}>
              Создать задачу
            </button>
          </div>
        )}
{showReport && report && (
  <div className={styles.report}>
    <h2 className={styles.reportTitle}>Отчет по проекту</h2>

    {/* Прогресс */}
    <div className={styles.reportSection}>
      <h3>Статус проекта</h3>
      <div className={styles.progressBar}>
        <div
          className={styles.progressFill}
          style={{ width: `${report.completion}%` }}
        />
      </div>
      <p className={styles.progressText}>Выполнено: {report.completion}%</p>
    </div>

    {/* Рискованные задачи */}
    {report.riskyTasks.length > 0 && (
      <div className={styles.reportSection}>
        <h3>Рискованные задачи</h3>
        {report.riskyTasks.map((task) => (
          <div key={task.id} className={styles.riskyTask}>
            <strong>{task.name}</strong>
            <p>Причина: {task.reason}</p>
            <p className={styles.riskLevel}>
              Уровень риска: {task.risk === "high" ? "Высокий" : "Средний"}
            </p>
          </div>
        ))}
      </div>
    )}

    {/* Эффективность разработчиков */}
    <div className={styles.reportSection}>
      <h3>Эффективность разработчиков</h3>
      {report.developerEfficiency.map((dev) => (
        <div key={dev.id} className={styles.devEfficiency}>
          <div className={styles.devInfo}>
            <strong>{dev.name}</strong>
            <span>
              Завершено: {dev.completedTasks} • В работе: {dev.inProgressTasks} • Грейд: {dev.grade}
            </span>
          </div>

          <div className={styles.efficiencyBar}>
            <div
              className={styles.efficiencyFill}
              style={{ width: `${dev.efficiency}%` }}
            />
          </div>

          <span className={styles.efficiencyText}>{dev.efficiency}%</span>
        </div>
      ))}
    </div>
  </div>
)}


        <div className={styles.tasksSection}>
          <h2>Задачи проекта</h2>
          {tasks.length === 0 ? (
            <p className={styles.noData}>Задач пока нет</p>
          ) : (
            <div className={styles.tasksList}>
              {tasks.map((task) => (
                <div key={task.id} className={styles.taskCard}>
                  <h4>{task.name}</h4>
                  <p>{task.description}</p>
                  <div className={styles.taskMeta}>
                    <span>Состояние: {task.state}/7</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
