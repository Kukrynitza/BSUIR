"use server"

import type { Developer } from "@/types"
import { createClient } from "@/lib/server"

export async function createDeveloper(data: Omit<Developer, "id">): Promise<Developer | null> {
  const supabase = await createClient()

  const { data: newDeveloper, error } = await supabase
    .from("developers")
    .insert({
      last_name: data.lastName,
      first_name: data.firstName,
      position: data.position,
      grade: data.grade,
      project: data.project,
    })
    .select()
    .single()

  if (error) {
    console.error("[v0] Error creating developer:", error)
    return null
  }

  return {
    id: newDeveloper.id,
    lastName: newDeveloper.last_name,
    firstName: newDeveloper.first_name,
    position: newDeveloper.position,
    grade: newDeveloper.grade,
    project: newDeveloper.project,
  } as Developer
}
