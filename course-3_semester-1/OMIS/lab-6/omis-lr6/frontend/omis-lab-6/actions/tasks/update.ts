"use server"

import type { Task } from "@/types"
import { createClient } from "@/lib/server"

export async function updateTask(id: number, data: Partial<Task>): Promise<void> {
  const supabase = await createClient()

  const { data: oldTask } = await supabase.from("tasks").select("*").eq("id", id).single()

  const { error } = await supabase.from("tasks").update(data).eq("id", id)

  if (error) {
    console.error("[v0] Error updating task:", error)
    return
  }

  if (data.state !== undefined && oldTask && oldTask.developer) {
    const oldState = oldTask.state

    // Задача выполнена (state = 7)
    if (data.state === 7 && oldState !== 7) {
      const isOverdue = oldTask.time && new Date(oldTask.time) < new Date()

      const { data: developer } = await supabase.from("developers").select("grade").eq("id", oldTask.developer).single()

      if (developer) {
        const currentGrade = Number.parseInt(developer.grade) || 0
        const newGrade = isOverdue ? Math.max(0, currentGrade - 30) : currentGrade + 5

        await supabase.from("developers").update({ grade: newGrade.toString() }).eq("id", oldTask.developer)
      }
    }
  }
}
