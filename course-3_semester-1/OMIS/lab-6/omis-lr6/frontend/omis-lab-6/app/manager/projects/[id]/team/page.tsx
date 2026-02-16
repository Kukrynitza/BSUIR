"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getProjects } from "@/actions/projects/get"
import { getDevelopers } from "@/actions/developers/get"
import { createDeveloper } from "@/actions/developers/create"
import { updateDeveloper } from "@/actions/developers/update"
import type { Project, Developer } from "@/types"
import styles from "../../../styles.module.css"

export default async function TeamPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params
  const projectId = Number.parseInt(resolvedParams.id)

  return <TeamPageClient projectId={projectId} />
}

function TeamPageClient({ projectId }: { projectId: number }) {
  const [project, setProject] = useState<Project | null>(null)
  const [teamDevelopers, setTeamDevelopers] = useState<Developer[]>([])
  const [availableDevelopers, setAvailableDevelopers] = useState<Developer[]>([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newDeveloper, setNewDeveloper] = useState({
    firstName: "",
    lastName: "",
    position: "",
    grade: "",
  })

  useEffect(() => {
    loadData()
  }, [projectId])

  async function loadData() {
    const [allProjects, allDevs] = await Promise.all([getProjects(), getDevelopers()])

    const projectData = allProjects.find((p) => p.id === projectId)
    setProject(projectData || null)
    const team = allDevs.filter((d) => d.project === projectId)
    const available = allDevs.filter((d) => d.project === null)
    setTeamDevelopers(team)
    setAvailableDevelopers(available)
  }

  async function handleAddExistingDeveloper(developerId: number) {
    const dev = availableDevelopers.find((d) => d.id === developerId)
    if (!dev) return
    await updateDeveloper(developerId, { ...dev, project: projectId })
    setShowAddModal(false)
    loadData()
  }

  async function handleRemoveDeveloper(developerId: number) {
    if (confirm("Вы уверены, что хотите удалить разработчика из команды?")) {
      const dev = teamDevelopers.find((d) => d.id === developerId)
      if (!dev) return
      await updateDeveloper(developerId, { ...dev, project: null })
      loadData()
    }
  }

  async function handleCreateDeveloper() {
    if (!newDeveloper.firstName.trim() || !newDeveloper.lastName.trim()) return

    const newDev = await createDeveloper({
      firstName: newDeveloper.firstName,
      lastName: newDeveloper.lastName,
      position: newDeveloper.position,
      grade: newDeveloper.grade,
      project: projectId,
    })
    setNewDeveloper({ firstName: "", lastName: "", position: "", grade: "" })
    setShowCreateModal(false)
    loadData()
  }

  if (!project) return <div className={styles.container}>Загрузка...</div>

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Команда: {project.name}</h1>
        <Link href={`/manager/projects/${projectId}`} className={styles.backLink}>
          ← К проекту
        </Link>
      </div>

      <div className={styles.content}>
        <div style={{ marginBottom: "2rem", display: "flex", gap: "1rem" }}>
          <button className={`${styles.button} ${styles.buttonPrimary}`} onClick={() => setShowAddModal(true)}>
            Добавить существующего
          </button>
          <button className={`${styles.button} ${styles.buttonSecondary}`} onClick={() => setShowCreateModal(true)}>
            Создать нового
          </button>
        </div>

        <div className={styles.teamGrid}>
          {teamDevelopers.map((dev) => (
            <div key={dev.id} className={styles.developerCard}>
              <button
                className={`${styles.iconButton} ${styles.iconButtonDanger} ${styles.removeButton}`}
                onClick={() => handleRemoveDeveloper(dev.id)}
                title="Удалить из команды"
              >
                ✕
              </button>

              <h3 className={styles.developerName}>
                {dev.firstName} {dev.lastName}
              </h3>
              <div className={styles.developerInfo}>
                <div>
                  <strong>Должность:</strong> {dev.position}
                </div>
                <div>
                  <strong>Уровень:</strong> {dev.grade}
                </div>
              </div>
            </div>
          ))}

          {teamDevelopers.length === 0 && (
            <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: "3rem", color: "#64748b" }}>
              <p>В команде пока нет разработчиков. Добавьте первого участника.</p>
            </div>
          )}
        </div>
      </div>

      {showAddModal && (
        <div className={styles.modal} onClick={() => setShowAddModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2 className={styles.modalTitle}>Добавить существующего разработчика</h2>

            <div style={{ maxHeight: "400px", overflowY: "auto" }}>
              {availableDevelopers.map((dev) => (
                <div
                  key={dev.id}
                  style={{
                    padding: "1rem",
                    border: "2px solid #e2e8f0",
                    borderRadius: "8px",
                    marginBottom: "0.75rem",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                  onClick={() => handleAddExistingDeveloper(dev.id)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = "#3b82f6"
                    e.currentTarget.style.backgroundColor = "#f0f9ff"
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = "#e2e8f0"
                    e.currentTarget.style.backgroundColor = "transparent"
                  }}
                >
                  <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>
                    {dev.firstName} {dev.lastName}
                  </div>
                  <div style={{ fontSize: "0.9rem", color: "#64748b" }}>
                    {dev.position} • {dev.grade}
                  </div>
                </div>
              ))}

              {availableDevelopers.length === 0 && (
                <div style={{ textAlign: "center", padding: "2rem", color: "#64748b" }}>
                  <p>Нет доступных разработчиков</p>
                </div>
              )}
            </div>

            <div className={styles.modalActions}>
              <button className={`${styles.button} ${styles.buttonSecondary}`} onClick={() => setShowAddModal(false)}>
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className={styles.modal} onClick={() => setShowCreateModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2 className={styles.modalTitle}>Создать нового разработчика</h2>

            <div className={styles.formGroup}>
              <label className={styles.label}>Имя</label>
              <input
                type="text"
                className={styles.input}
                value={newDeveloper.firstName}
                onChange={(e) => setNewDeveloper({ ...newDeveloper, firstName: e.target.value })}
                placeholder="Введите имя"
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Фамилия</label>
              <input
                type="text"
                className={styles.input}
                value={newDeveloper.lastName}
                onChange={(e) => setNewDeveloper({ ...newDeveloper, lastName: e.target.value })}
                placeholder="Введите фамилию"
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Должность</label>
              <input
                type="text"
                className={styles.input}
                value={newDeveloper.position}
                onChange={(e) => setNewDeveloper({ ...newDeveloper, position: e.target.value })}
                placeholder="Например: Frontend Developer"
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Уровень</label>
              <select
                className={styles.select}
                value={newDeveloper.grade}
                onChange={(e) => setNewDeveloper({ ...newDeveloper, grade: e.target.value })}
              >
                <option value="">-- Выберите уровень --</option>
                <option value="5">Junior</option>
                <option value="15">Middle</option>
                <option value="30">Senior</option>
                <option value="60">Lead</option>
              </select>
            </div>

            <div className={styles.modalActions}>
              <button
                className={`${styles.button} ${styles.buttonSecondary}`}
                onClick={() => setShowCreateModal(false)}
              >
                Отмена
              </button>
              <button className={`${styles.button} ${styles.buttonPrimary}`} onClick={handleCreateDeveloper}>
                Создать
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
