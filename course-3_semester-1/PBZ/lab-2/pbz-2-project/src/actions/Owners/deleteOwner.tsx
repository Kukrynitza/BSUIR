'use server'
import database from '@/modules/database'


export default async function deleteOwner(id: number) {
  database
    .deleteFrom('owner')
    .where('owner.id', '=', id)
    .executeTakeFirst()
}