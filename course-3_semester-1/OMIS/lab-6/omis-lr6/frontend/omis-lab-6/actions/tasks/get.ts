"use server"

import type { Task } from "@/types"
import { createClient } from "@/lib/server"

export async function getTasks(params?: {
  id?: number
  projectId?: number
  developerId?: number
}): Promise<Task[] | Task | null> {
  const supabase = await createClient()

  if (!params) {
    const { data, error } = await supabase.from("tasks").select("*").order("id")
    if (error) {
      console.error("[v0] Error fetching tasks:", error)
      return []
    }
    return data.map((t) => ({
      id: t.id,
      state: t.state,
      developer: t.developer,
      project: t.project,
      description: t.description,
      name: t.name,
      time: t.time ? new Date(t.time) : null,
    })) as Task[]
  }

  if (params.id !== undefined) {
    const { data, error } = await supabase.from("tasks").select("*").eq("id", params.id).single()
    if (error) {
      console.error("[v0] Error fetching task:", error)
      return null
    }
    return {
      id: data.id,
      state: data.state,
      developer: data.developer,
      project: data.project,
      description: data.description,
      name: data.name,
      time: data.time ? new Date(data.time) : null,
    } as Task
  }

  if (params.projectId !== undefined) {
    const { data, error } = await supabase.from("tasks").select("*").eq("project", params.projectId).order("id")
    if (error) {
      console.error("[v0] Error fetching tasks by project:", error)
      return []
    }
    return data.map((t) => ({
      id: t.id,
      state: t.state,
      developer: t.developer,
      project: t.project,
      description: t.description,
      name: t.name,
      time: t.time ? new Date(t.time) : null,
    })) as Task[]
  }

  if (params.developerId !== undefined) {
    const { data, error } = await supabase.from("tasks").select("*").eq("developer", params.developerId).order("id")
    if (error) {
      console.error("[v0] Error fetching tasks by developer:", error)
      return []
    }
    return data.map((t) => ({
      id: t.id,
      state: t.state,
      developer: t.developer,
      project: t.project,
      description: t.description,
      name: t.name,
      time: t.time ? new Date(t.time) : null,
    })) as Task[]
  }

  return []
}
