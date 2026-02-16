"use server"
import { createClient } from "@/lib/server"

export async function deleteProject(id: number): Promise<void> {
  const supabase = await createClient()

  const { error } = await supabase.from("projects").delete().eq("id", id)

  if (error) {
    console.error("[v0] Error deleting project:", error)
  }
}
