'use server'
import database from '@/modules/database'


export default async function deleteEvent(id: number) {
  database
    .deleteFrom('event')
    .where('event.id', '=', id)
    .executeTakeFirst()
}