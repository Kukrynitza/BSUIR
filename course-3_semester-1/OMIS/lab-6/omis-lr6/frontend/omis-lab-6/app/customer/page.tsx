"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getProjects } from "@/actions/projects/get"
import type { Project } from "@/types"
import styles from "./customer.module.css"

export default function CustomerPage() {
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    loadProjects()
  }, [])

  async function loadProjects() {
    const data = await getProjects()
    setProjects(data)
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Выбор проекта</h1>
        <Link href="/" className={styles.backLink}>
          ← Вернуться на главную
        </Link>
      </div>

      <div className={styles.content}>
        <div className={styles.projectsGrid}>
          {projects.map((project) => (
            <Link key={project.id} href={`/customer/${project.id}`} className={styles.projectCard}>
              <h3 className={styles.projectName}>{project.name}</h3>
              <p className={styles.projectDescription}>{project.description}</p>
              <div className={styles.projectArrow}>Открыть проект →</div>
            </Link>
          ))}

          {projects.length === 0 && (
            <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: "3rem", color: "#64748b" }}>
              <p>Проектов пока нет</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
