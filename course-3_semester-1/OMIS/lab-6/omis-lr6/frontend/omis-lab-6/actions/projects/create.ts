"use server"

import type { Project } from "@/types"
import { createClient } from "@/lib/server"

export async function createProject(data: Omit<Project, "id">): Promise<Project | null> {
  const supabase = await createClient()

  const { data: newProject, error } = await supabase
    .from("projects")
    .insert({
      name: data.name,
      description: data.description,
    })
    .select()
    .single()

  if (error) {
    console.error("[v0] Error creating project:", error)
    return null
  }

  return newProject as Project
}
