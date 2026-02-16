"use server"

import type { Developer } from "@/types"
import { createClient } from "@/lib/server"

export async function getDevelopers(id?: number): Promise<Developer[] | Developer | null> {
  const supabase = await createClient()

  if (id !== undefined) {
    const { data, error } = await supabase.from("developers").select("*").eq("id", id).single()

    if (error) {
      console.error("[v0] Error fetching developer:", error)
      return null
    }

    return {
      id: data.id,
      lastName: data.last_name,
      firstName: data.first_name,
      position: data.position,
      grade: data.grade,
      project: data.project,
    } as Developer
  }

  const { data, error } = await supabase.from("developers").select("*").order("id")

  if (error) {
    console.error("[v0] Error fetching developers:", error)
    return []
  }

  return data.map((d) => ({
    id: d.id,
    lastName: d.last_name,
    firstName: d.first_name,
    position: d.position,
    grade: d.grade,
    project: d.project,
  })) as Developer[]
}
