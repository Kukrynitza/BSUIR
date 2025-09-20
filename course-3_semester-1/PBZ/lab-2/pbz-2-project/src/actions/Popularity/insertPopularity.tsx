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

export default async function insertPopularity(popularity: Popularity) {
  database
    .insertInto('popularity')
    .values({
      count: popularity.count,
      object: popularity.object.id,
      date: new Date(popularity.date)
    })
    .executeTakeFirst()
}
