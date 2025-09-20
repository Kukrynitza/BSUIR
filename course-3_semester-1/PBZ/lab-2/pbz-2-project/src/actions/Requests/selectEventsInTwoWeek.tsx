'use server'
import database from '@/modules/database'
import { sql } from 'kysely';

export default async function selectEventsInTwoWeek() {
  const currentDate = new Date()
  const twoWeeksLater = new Date();
  twoWeeksLater.setDate(currentDate.getDate() + 14);
  const result = await database
    .selectFrom('event')
    .select([
      'event.id',
      'event.name',
      'event.date',
      'event.type',
      (eb) => eb
        .selectFrom('objects')
        .select('objects.name')
        .whereRef('objects.id', '=', 'event.object')
        .as('object'),
      (eb) => eb
        .selectFrom('objects')
        .select('objects.address')
        .whereRef('objects.id', '=', 'event.object')
        .as('address')
    ])
    .where('event.date', '>=', currentDate)
    .where('event.date', '<=', twoWeeksLater)
    .orderBy('event.name', 'asc')
    .execute()
    return result.map((element) => ({...element, date: element.date.toISOString().split('T')[0]}))
}
