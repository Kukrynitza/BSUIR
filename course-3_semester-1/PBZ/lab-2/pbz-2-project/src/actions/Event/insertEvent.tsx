'use server'
import database from '@/modules/database'

interface Event {
  id: number
  name: string
  date: string
  type: string
  object: {
    id: number
    name: string
  }
}

export default async function insertEvent(event: Event) {
  database
    .insertInto('event')
    .values({
      name: event.name,
      type: event.type,
      object: event.object.id,
      date: new Date(event.date)
    })
    .executeTakeFirst()
}
