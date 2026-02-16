"use server"
import { createClient } from "@/lib/server"

export async function deleteTask(id: number): Promise<void> {
  const supabase = await createClient()

  const { error } = await supabase.from("tasks").delete().eq("id", id)

  if (error) {
    console.error("[v0] Error deleting task:", error)
  }
}
