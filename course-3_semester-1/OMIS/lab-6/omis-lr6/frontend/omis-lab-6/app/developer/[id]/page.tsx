"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getDevelopers } from "@/actions/developers/get"
import { getProjects } from "@/actions/projects/get"
import { getTasks } from "@/actions/tasks/get"
import { getTaskStateInfo } from "@/types"
import type { Developer, Task, Project } from "@/types"
import styles from "../developer.module.css"

export default async function DeveloperDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params
  const developerId = Number.parseInt(resolvedParams.id)

  return <DeveloperDetailPageClient developerId={developerId} />
}

function DeveloperDetailPageClient({ developerId }: { developerId: number }) {
  const [developer, setDeveloper] = useState<Developer | null>(null)
  const [project, setProject] = useState<Project | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [rating, setRating] = useState<number>(0)

  useEffect(() => {
    loadData()
  }, [developerId])

  async function loadData() {
    const allDevs = await getDevelopers()
    const devData = allDevs.find((d) => d.id === developerId)
    setDeveloper(devData || null)

    if (devData?.project) {
      const [allProjects, allTasks] = await Promise.all([getProjects(), getTasks()])
      const projectData = allProjects.find((p) => p.id === devData.project)
      const tasksData = allTasks.filter((t) => t.developer === developerId)
      setProject(projectData || null)
      setTasks(tasksData)
    }

    // Rating calculation - сумма grade разработчика
    setRating(Number.parseFloat(devData?.grade || "0"))
  }

  if (!developer) return <div className={styles.container}>Загрузка...</div>

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          {developer.firstName} {developer.lastName}
        </h1>
        <Link href="/developer" className={styles.backLink}>
          ← К списку разработчиков
        </Link>
      </div>

      <div className={styles.content}>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "2rem", marginBottom: "2rem" }}>
          <div className={styles.infoSection}>
            <h2 className={styles.sectionTitle}>Информация</h2>
            <div className={styles.infoGrid}>
              <div className={styles.infoItem}>
                <div className={styles.infoLabel}>Должность</div>
                <div className={styles.infoValue}>{developer.position}</div>
              </div>
              <div className={styles.infoItem}>
                <div className={styles.infoLabel}>Уровень</div>
                <div className={styles.infoValue}>{developer.grade}</div>
              </div>
              {project && (
                <div className={styles.infoItem}>
                  <div className={styles.infoLabel}>Проект</div>
                  <div className={styles.infoValue}>{project.name}</div>
                </div>
              )}
            </div>
          </div>

          <div className={styles.ratingCard}>
            <div className={styles.ratingValue}>{rating.toFixed(1)}</div>
            <div className={styles.ratingLabel}>Рейтинг разработчика</div>
          </div>
        </div>

        {project && (
          <div className={styles.infoSection}>
            <h2 className={styles.sectionTitle}>Описание проекта</h2>
            <p style={{ color: "#64748b", lineHeight: 1.6 }}>{project.description}</p>
          </div>
        )}

        <div className={styles.infoSection}>
          <h2 className={styles.sectionTitle}>Мои задачи</h2>
          <div className={styles.tasksList}>
            {tasks.map((task) => {
              const stateInfo = getTaskStateInfo(task.state)

              return (
                <Link
                  key={task.id}
                  href={`/developer/${developerId}/${task.id}`}
                  className={styles.taskCard}
                  style={{ borderLeftColor: stateInfo.color }}
                >
                  <h3 className={styles.taskName}>{task.name}</h3>
                  <p className={styles.taskDescription}>{task.description}</p>
                  <div className={styles.taskMeta}>
                    <div className={styles.taskMetaItem}>
                      <span className={styles.stateBadge} style={{ backgroundColor: stateInfo.color }}>
                        {stateInfo.label}
                      </span>
                    </div>
                    {task.time && (
                      <div className={styles.taskMetaItem}>⏱️ {new Date(task.time).toLocaleDateString()}</div>
                    )}
                  </div>
                </Link>
              )
            })}

            {tasks.length === 0 && (
              <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>
                <p>Задач пока нет</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
