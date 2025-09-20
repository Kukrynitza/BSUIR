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

export default async function updateEvent(event: Event | undefined) {
  if (!event) {
    return
  }
    database
    .updateTable('event')
      .set({
      name: event.name,
      date: new Date(event.date),
      type: event.type,
      object: event.object.id
    })
    .where('event.id', '=', event.id)
    .executeTakeFirst()
}
