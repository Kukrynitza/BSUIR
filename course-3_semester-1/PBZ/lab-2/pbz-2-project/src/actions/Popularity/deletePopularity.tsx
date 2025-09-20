'use server'
import database from '@/modules/database'


export default async function deletePopularity(id: number) {
  database
    .deleteFrom('popularity')
    .where('popularity.id', '=', id)
    .executeTakeFirst()
}