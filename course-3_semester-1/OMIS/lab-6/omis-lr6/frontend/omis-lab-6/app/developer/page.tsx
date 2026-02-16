"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { getDevelopers } from "@/actions/developers/get"
import { createDeveloper } from "@/actions/developers/create"
import type { Developer } from "@/types"
import styles from "./developer.module.css"

export default function DeveloperPage() {
  const [developers, setDevelopers] = useState<Developer[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newDeveloper, setNewDeveloper] = useState({
    firstName: "",
    lastName: "",
    position: "",
    grade: "",
  })

  useEffect(() => {
    loadDevelopers()
  }, [])

  async function loadDevelopers() {
    const data = await getDevelopers()
    setDevelopers(data)
  }

  async function handleCreateDeveloper() {
    if (!newDeveloper.firstName.trim() || !newDeveloper.lastName.trim()) return

    await createDeveloper({
      firstName: newDeveloper.firstName,
      lastName: newDeveloper.lastName,
      position: newDeveloper.position,
      grade: newDeveloper.grade,
      project: null,
    })
    setNewDeveloper({ firstName: "", lastName: "", position: "", grade: "" })
    setShowCreateModal(false)
    loadDevelopers()
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Выбор разработчика</h1>
        <Link href="/" className={styles.backLink}>
          ← Вернуться на главную
        </Link>
      </div>

      <div className={styles.content}>
        <div className={styles.developersGrid}>
          <div className={styles.createCard} onClick={() => setShowCreateModal(true)}>
            <div className={styles.createIcon}>+</div>
            <h3>Создать нового разработчика</h3>
          </div>

          {developers.map((dev) => (
            <Link key={dev.id} href={`/developer/${dev.id}`} className={styles.developerCard}>
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
                {dev.project && <div className={styles.projectBadge}>В проекте #{dev.project}</div>}
                {!dev.project && <div className={styles.availableBadge}>Свободен</div>}
              </div>
            </Link>
          ))}
        </div>
      </div>

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
