'use server'
import database from '@/modules/database'

export default async function selectObjectNames() {
  return database
    .selectFrom('objects')
    .select([
      'objects.id',
      'objects.name',
    ])
    .orderBy('objects.name', 'asc')
    .execute()
}
