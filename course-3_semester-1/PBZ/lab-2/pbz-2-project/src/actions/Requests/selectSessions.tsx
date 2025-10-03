'use server'
import database from '@/modules/database'
import { sql } from 'kysely';

export default async function selectSessions(objectId:number) {
  const result = await database
    .selectFrom('sessions')
    .selectAll()
    .where('sessions.name', '=', objectId)
    .orderBy('sessions.createdAt', 'asc')
    .execute()
    return result.map((element) => ({...element, createdAt: element.createdAt.toISOString().split('T')[0]}))
}
