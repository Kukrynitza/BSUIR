'use server'
import database from '@/modules/database'

export default async function selectEvents() {
  const result = await database
    .selectFrom('event')
    .select([
      'event.id',
      'event.name',
      'event.object',
      'event.type',
      'event.date'
    ])
    .orderBy('event.name', 'asc')
    .execute()
    return result.map((element) => ({...element, date: element.date.toISOString().split('T')[0]}))
}
