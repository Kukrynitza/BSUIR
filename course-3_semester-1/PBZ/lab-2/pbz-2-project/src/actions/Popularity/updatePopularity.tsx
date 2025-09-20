'use server'
import database from '@/modules/database'

interface Popularity {
  id: number
  date: string
  object: {
    id: number
    name: string
  }
  count: number
}

export default async function updatePopularity(popularity: Popularity | undefined) {
  if (!popularity) {
    return
  }
    database
    .updateTable('popularity')
      .set({
      count: popularity.count,
      date: new Date(popularity.date),
      object: popularity.object.id
    })
    .where('popularity.id', '=', popularity.id)
    .executeTakeFirst()
}
