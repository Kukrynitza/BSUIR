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
      'objects.open',
      'objects.date'
    ])
    .where('objects.type', '=', type)
    .where('objects.open', '=', true)
    .where('objects.date', '<=', currentDate)
    .orderBy('objects.name', 'asc')
    .execute()
    return result.map((element) => ({...element, date: element.date.toISOString().split('T')[0], open: String(element.open)}))
}
