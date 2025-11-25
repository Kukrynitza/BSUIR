'use server'
import database from '@/modules/database'

export default async function selectObjectsInType(type: string) {
  const currentDate = new Date()
  const result = await database
    .selectFrom('objects')
    .select([
      'objects.id',
      'objects.name',
      'objects.address',
      'objects.type',
      'objects.numberOfSeats',
      'objects.owner',
      'objects.date',
            (eb) => eb
      .selectFrom('sessions')
      .select('sessions.open')
      .whereRef('sessions.name', '=', 'objects.id')
      .orderBy('sessions.id', 'desc')
      .limit(1)
      .as('open')
    ])
    .where('objects.type', '=', type)
    .where('objects.date', '<=', currentDate)
    .orderBy('objects.name', 'asc')
    .execute()
    return result
    .filter((element) => element.open === true)
    .map((element) => ({...element, date: element.date.toISOString().split('T')[0], open: String(element.open)}))
}
