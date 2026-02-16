'use client'
import Link from "next/link"
import styles from "./home.module.css"

export default function HomePage() {
  const roles = [
    {
      title: "Разработчик",
      description: "Управление задачами и отслеживание прогресса",
      href: "/developer",
    },
    {
      title: "Менеджер",
      description: "Координация команды и управление проектами",
      href: "/manager",
    },
    {
      title: "Заказчик",
      description: "Мониторинг состояния проектов и добавление задач",
      href: "/customer",
    },
  ]

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Система управления проектами</h1>
        <p className={styles.subtitle}>Интеллектуальная платформа с элементами искусственного интеллекта</p>
      </div>

      <div className={styles.content}>
        <h2 className={styles.sectionTitle}>Выберите роль</h2>
        <div className={styles.rolesGrid}>
          {roles.map((role) => (
            <Link key={role.href} href={role.href} className={styles.roleCard}>
              <h3 className={styles.roleTitle}>{role.title}</h3>
              <p className={styles.roleDescription}>{role.description}</p>
              <div className={styles.arrow}>→</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
