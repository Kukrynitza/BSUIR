'use server'
import database from '@/modules/database'
import { strict } from 'assert'

export interface Object {
  id: number
  name: string
  address: string
  type: string
  numberOfSeats: number
  owner: number
  open: boolean
}

export default async function selectOwnersLastName() {
  return database
    .selectFrom('owner')
    .select([
      'owner.lastName',
      'owner.id'
    ])
    .orderBy('owner.firstName', 'asc')
    .execute()
}
