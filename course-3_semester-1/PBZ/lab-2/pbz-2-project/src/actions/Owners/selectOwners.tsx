'use server'
import database from '@/modules/database'
import { strict } from 'assert'

export interface Object {
  id: number
  brandId: number
  name: string
  address: string
  type: string
  numberOfSeats: number
  owner: number
  open: boolean
}

export default async function selectOwners() {
  return database
    .selectFrom('owner')
    .select([
      'owner.id',
      'owner.surname',
      'owner.firstName',
      'owner.lastName',
      'owner.type',
      'owner.number',
      'owner.name',
      (eb) => eb
      .selectFrom('objects')
      .select(eb.fn('array_agg', ['objects.address']).as('objects'))
      .whereRef('objects.owner', '=', 'owner.id')
      .as('objects')
    ])
    .orderBy('owner.firstName', 'asc')
    .execute()
}
