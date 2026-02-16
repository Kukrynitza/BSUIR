"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getProjects } from "@/actions/projects/get"
import { getReport } from "@/actions/reports/getReport"
import { getTasks } from "@/actions/tasks/get"
import { getDevelopers } from "@/actions/developers/get"
import type { Task, Developer, Project, ProjectReport } from "@/types"
import styles from "../../../styles.module.css"

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params
  const projectId = Number.parseInt(resolvedParams.id)
  return <ReportPageClient projectId={projectId} />
}

function ReportPageClient({ projectId }: { projectId: number }) {
  const [project, setProject] = useState<Project | null>(null)
  const [report, setReport] = useState<ProjectReport | null>(null)

  async function loadData() {
    const [projects, tasks, developers] = await Promise.all([
      getProjects(),
      getTasks(),
      getDevelopers(),
    ])

    const projectData = projects.find((p) => p.id === projectId) || null
    const projectTasks = tasks.filter((t) => t.project === projectId)
    const projectDevelopers = developers.filter((d) => d.project === projectId)

    const reportData = await getReport(projectTasks, projectDevelopers)
    console.log(reportData)
    setProject(projectData)
    setReport(reportData)
  }

  useEffect(() => {
    loadData()
  }, [projectId])

  if (!project || !report) {
    return <div className={styles.container}>Загрузка...</div>
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Отчет: {project.name}</h1>
        <Link href={`/manager/projects/${projectId}`} className={styles.backLink}>
          ← К проекту
        </Link>
      </div>

      <div className={styles.content}>
        {/* Прогресс */}
        <div className={styles.reportSection}>
          <h2 className={styles.reportTitle}>Прогресс проекта</h2>
          <div className={styles.completionBar}>
            <div
              className={styles.completionFill}
              style={{ width: `${report.completion}%` }}
            >
              {report.completion}%
            </div>
          </div>
        </div>

        {/* Риски */}
        <div className={styles.reportSection}>
          <h2 className={styles.reportTitle}>Рискованные задачи</h2>
          <div className={styles.riskList}>
            {report.riskyTasks.map((task) => (
              <div
                key={task.id}
                className={`${styles.riskItem} ${
                  task.risk === "high" ? styles.riskHigh : styles.riskMedium
                }`}
              >
                <div className={styles.riskItemTitle}>{task.name}</div>
                <div className={styles.riskItemReason}>{task.reason}</div>
              </div>
            ))}

            {report.riskyTasks.length === 0 && (
              <div style={{ textAlign: "center", padding: "2rem", color: "#64748b" }}>
                Рискованных задач не обнаружено
              </div>
            )}
          </div>
        </div>

        {/* Эффективность */}
        <div className={styles.reportSection}>
          <h2 className={styles.reportTitle}>Эффективность разработчиков</h2>
          <div className={styles.efficiencyList}>
            {report.developerEfficiency.map((dev) => (
              <div key={dev.id} className={styles.efficiencyItem}>
                <div className={styles.efficiencyInfo}>
                  <h4>{dev.name}</h4>
                  <div className={styles.efficiencyStats}>
                    Завершено: {dev.completedTasks} • В работе: {dev.inProgressTasks} • Грейд: {dev.grade}
                  </div>
                </div>
                <div className={styles.efficiencyScore}>{dev.efficiency}%</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
