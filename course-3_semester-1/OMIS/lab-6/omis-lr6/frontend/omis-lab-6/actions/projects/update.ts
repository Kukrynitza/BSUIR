"use server"

import type { Project } from "@/types"
import { createClient } from "@/lib/server"

export async function updateProject(id: number, data: Partial<Project>): Promise<void> {
  const supabase = await createClient()

  const { error } = await supabase.from("projects").update(data).eq("id", id)

  if (error) {
    console.error("[v0] Error updating project:", error)
  }
}
