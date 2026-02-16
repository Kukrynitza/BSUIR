"use server"

import type { Task } from "@/types"
import { createClient } from "@/lib/server"

export async function createTask(data: Omit<Task, "id">): Promise<Task | null> {
  const supabase = await createClient()

  const { data: newTask, error } = await supabase
    .from("tasks")
    .insert({
      state: data.state,
      developer: data.developer,
      project: data.project,
      description: data.description,
      name: data.name,
      time: data.time,
    })
    .select()
    .single()

  if (error) {
    console.error("[v0] Error creating task:", error)
    return null
  }

  return {
    id: newTask.id,
    state: newTask.state,
    developer: newTask.developer,
    project: newTask.project,
    description: newTask.description,
    name: newTask.name,
    time: newTask.time ? new Date(newTask.time) : null,
  } as Task
}
