'use server'
import database from '@/modules/database'

interface Object {
  id: number
  name: string
  address: string
  type: string
  numberOfSeats: number
  date: string
  owner: {
    id: number,
    lastName: string
  }
  // open: string
}

export default async function insertObject(object: Object) {
  database
    .insertInto('objects')
    .values({
      name: object.name,
      address: object.address,
      type: object.type,
      date: new Date(object.date),
      numberOfSeats: object.numberOfSeats,
      owner: Number(object.owner.id),
      // open: object.open === 'true' ? true : false
    })
    .executeTakeFirst()
}
