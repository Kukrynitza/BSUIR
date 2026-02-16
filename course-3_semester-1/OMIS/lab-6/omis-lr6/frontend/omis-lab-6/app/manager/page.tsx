"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getProjects } from "@/actions/projects/get"
import { createProject } from "@/actions/projects/create"
import { deleteProject } from "@/actions/projects/delete"
import type { Project } from "@/types"
import styles from "./styles.module.css"

export default function ManagerPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [showModal, setShowModal] = useState(false)
  const [newProject, setNewProject] = useState({ name: "", description: "" })

  useEffect(() => {
    loadProjects()
  }, [])

  async function loadProjects() {
    const data = await getProjects()
    setProjects(data)
  }

  async function handleCreateProject() {
    if (!newProject.name.trim()) return

    await createProject({ name: newProject.name, description: newProject.description })
    setNewProject({ name: "", description: "" })
    setShowModal(false)
    loadProjects()
  }

  async function handleDeleteProject(id: number) {
    if (confirm("Вы уверены, что хотите удалить проект?")) {
      await deleteProject(id)
      loadProjects()
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Управление проектами</h1>
        <Link href="/" className={styles.backLink}>
          ← Вернуться на главную
        </Link>
      </div>

      <div className={styles.content}>
        <div className={styles.projectsGrid}>
          <div className={styles.createCard} onClick={() => setShowModal(true)}>
            <div className={styles.createIcon}>+</div>
            <h3>Создать новый проект</h3>
          </div>

          {projects.map((project) => (
            <div key={project.id} className={styles.projectCard}>
              <Link href={`/manager/projects/${project.id}`} style={{ textDecoration: "none", color: "inherit" }}>
                <h3 className={styles.projectName}>{project.name}</h3>
                <p className={styles.projectDescription}>{project.description}</p>
              </Link>
              <div className={styles.projectActions}>
                <Link href={`/manager/projects/${project.id}`}>
                  <button className={`${styles.button} ${styles.buttonPrimary}`}>Открыть</button>
                </Link>
                <button
                  className={`${styles.button} ${styles.buttonDanger}`}
                  onClick={() => handleDeleteProject(project.id)}
                >
                  Удалить
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showModal && (
        <div className={styles.modal} onClick={() => setShowModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2 className={styles.modalTitle}>Создать новый проект</h2>

            <div className={styles.formGroup}>
              <label className={styles.label}>Название проекта</label>
              <input
                type="text"
                className={styles.input}
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                placeholder="Введите название проекта"
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Описание</label>
              <textarea
                className={styles.textarea}
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                placeholder="Введите описание проекта"
              />
            </div>

            <div className={styles.modalActions}>
              <button className={`${styles.button} ${styles.buttonSecondary}`} onClick={() => setShowModal(false)}>
                Отмена
              </button>
              <button className={`${styles.button} ${styles.buttonPrimary}`} onClick={handleCreateProject}>
                Создать
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
