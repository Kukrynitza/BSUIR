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

export default async function selectPopularity() {
  const result = await database
    .selectFrom('popularity')
    .select([
      'popularity.id',
      'popularity.object',
      'popularity.count',
      'popularity.date'
    ])
    .orderBy('popularity.count', 'desc')
    .execute()
    return result.map((element) => ({...element, date: element.date.toISOString().split('T')[0]}))
}
