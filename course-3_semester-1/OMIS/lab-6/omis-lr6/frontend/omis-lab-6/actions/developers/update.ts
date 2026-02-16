"use server"

import type { Developer } from "@/types"
import { createClient } from "@/lib/server"

export async function updateDeveloper(id: number, data: Partial<Developer>): Promise<void> {
  const supabase = await createClient()

  const updateData: Record<string, unknown> = {}
  if (data.lastName !== undefined) updateData.last_name = data.lastName
  if (data.firstName !== undefined) updateData.first_name = data.firstName
  if (data.position !== undefined) updateData.position = data.position
  if (data.grade !== undefined) updateData.grade = data.grade
  if (data.project !== undefined) updateData.project = data.project

  const { error } = await supabase.from("developers").update(updateData).eq("id", id)

  if (error) {
    console.error("[v0] Error updating developer:", error)
  }
}
