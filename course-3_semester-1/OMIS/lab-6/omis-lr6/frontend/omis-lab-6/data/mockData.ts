import type { Developer, Task, Project, ProjectReport } from "@/types"

// Моковые данные для разработчиков
export const mockDevelopers: Developer[] = [
  {
    id: 1,
    lastName: "Иванов",
    firstName: "Иван",
    position: "Frontend Developer",
    grade: "Senior",
    project: 1,
  },
  {
    id: 2,
    lastName: "Петрова",
    firstName: "Анна",
    position: "Backend Developer",
    grade: "Middle",
    project: 1,
  },
  {
    id: 3,
    lastName: "Сидоров",
    firstName: "Петр",
    position: "Full Stack Developer",
    grade: "Senior",
    project: 2,
  },
  {
    id: 4,
    lastName: "Кузнецов",
    firstName: "Алексей",
    position: "Frontend Developer",
    grade: "Junior",
    project: null,
  },
  {
    id: 5,
    lastName: "Смирнова",
    firstName: "Мария",
    position: "QA Engineer",
    grade: "Middle",
    project: 1,
  },
]

// Моковые данные для проектов
export const mockProjects: Project[] = [
  {
    id: 1,
    name: "Интеллектуальная система управления проектами",
    description: "Система с элементами искусственного интеллекта для управления проектами и задачами",
  },
  {
    id: 2,
    name: "Портал для клиентов",
    description: "Веб-портал для взаимодействия с клиентами и обработки заявок",
  },
  {
    id: 3,
    name: "Мобильное приложение",
    description: "Кроссплатформенное мобильное приложение для iOS и Android",
  },
]

// Моковые данные для задач
export const mockTasks: Task[] = [
  {
    id: 1,
    state: 2,
    developer: 1,
    project: 1,
    description: "Разработать главную страницу с выбором роли пользователя",
    name: "Главная страница",
    time: new Date("2025-01-20"),
  },
  {
    id: 2,
    state: 5,
    developer: 2,
    project: 1,
    description: "Настроить подключение к базе данных PostgreSQL и создать миграции",
    name: "Настройка базы данных",
    time: new Date("2025-01-18"),
  },
  {
    id: 3,
    state: 0,
    developer: null,
    project: 1,
    description: "Реализовать REST API для работы с задачами",
    name: "API для задач",
    time: null,
  },
  {
    id: 4,
    state: 6,
    developer: 1,
    project: 1,
    description: "Создать компонент для отображения списка проектов",
    name: "Компонент списка проектов",
    time: new Date("2025-01-15"),
  },
  {
    id: 5,
    state: 3,
    developer: 5,
    project: 1,
    description: "Написать автоматические тесты для основных функций",
    name: "Автоматические тесты",
    time: new Date("2025-01-22"),
  },
  {
    id: 6,
    state: 1,
    developer: 3,
    project: 2,
    description: "Разработать систему авторизации и аутентификации",
    name: "Система авторизации",
    time: new Date("2025-01-25"),
  },
  {
    id: 7,
    state: 7,
    developer: 3,
    project: 2,
    description: "Настроить CI/CD pipeline",
    name: "CI/CD",
    time: new Date("2025-01-10"),
  },
]

// Функция для генерации отчета (мок)
export const generateMockReport = (projectId: number): ProjectReport => {
  const projectTasks = mockTasks.filter((t) => t.project === projectId)
  const completedTasks = projectTasks.filter((t) => t.state === 7)
  const completionPercentage = Math.round((completedTasks.length / projectTasks.length) * 100)

  const riskyTasks = projectTasks
    .filter((task) => {
      if (!task.time) return false
      const daysLeft = Math.ceil((task.time.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
      return daysLeft < 5 && task.state < 6
    })
    .map((task) => ({
      taskId: task.id,
      taskName: task.name,
      riskLevel: "Высокий",
      reason: "Приближается срок сдачи, задача не завершена",
    }))

  const developerStats = new Map<number, { completed: number; total: number }>()
  projectTasks.forEach((task) => {
    if (task.developer) {
      const stats = developerStats.get(task.developer) || { completed: 0, total: 0 }
      stats.total++
      if (task.state === 7) stats.completed++
      developerStats.set(task.developer, stats)
    }
  })

  const developerEfficiency = Array.from(developerStats.entries()).map(([devId, stats]) => {
    const dev = mockDevelopers.find((d) => d.id === devId)
    return {
      developerId: devId,
      developerName: dev ? `${dev.firstName} ${dev.lastName}` : "Неизвестно",
      efficiency: Math.round((stats.completed / stats.total) * 100),
      tasksCompleted: stats.completed,
      averageTime: Math.floor(Math.random() * 40) + 10,
    }
  })

  return {
    projectId,
    completionPercentage,
    riskyTasks,
    developerEfficiency,
  }
}
