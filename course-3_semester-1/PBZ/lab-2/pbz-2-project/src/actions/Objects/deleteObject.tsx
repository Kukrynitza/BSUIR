'use server'
import database from '@/modules/database'


export default async function deleteObject(id: number) {
  database
    .deleteFrom('objects')
    .where('objects.id', '=', id)
    .executeTakeFirst()
}