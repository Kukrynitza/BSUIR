"use server"

import type { Project } from "@/types"
import { createClient } from "@/lib/server"

export async function getProjects(id?: number): Promise<Project[] | Project | null> {
  const supabase = await createClient()

  if (id !== undefined) {
    const { data, error } = await supabase.from("projects").select("*").eq("id", id).single()

    if (error) {
      console.error("[v0] Error fetching project:", error)
      return null
    }
    return data as Project
  }

  const { data, error } = await supabase.from("projects").select("*").order("id")

  if (error) {
    console.error("[v0] Error fetching projects:", error)
    return []
  }
  return data as Project[]
}
