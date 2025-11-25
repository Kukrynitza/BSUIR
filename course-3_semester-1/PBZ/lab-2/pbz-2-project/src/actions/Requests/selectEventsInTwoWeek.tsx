'use server'

import { sql } from 'kysely'
import database from '@/modules/database'

export default async function selectEventsInTwoWeek() {
  const compiled = sql`SELECT * FROM select_events_in_two_week()`.compile(database)
  const result = await database.executeQuery(compiled)
  return result.rows.map((row: any) => ({
    ...row,
    date: row.date.toISOString().split('T')[0],
  }))
}
