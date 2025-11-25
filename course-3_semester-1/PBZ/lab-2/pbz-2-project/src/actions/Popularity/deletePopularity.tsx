'use server'

import database from '@/modules/database'
import { sql } from 'kysely'

export default async function deletePopularity(id: number) {
  const compiled = sql`CALL delete_popularity(${id})`.compile(database)

  await database.executeQuery(compiled)

  return { success: true }
}
