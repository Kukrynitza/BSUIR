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
  open: string
}

export default async function updateObject(object: Object | undefined) {
  if (!object) {
    return
  }
    database
    .updateTable('objects')
      .set({
      name: object.name,
      address: object.address,
      type: object.type,
      date: new Date(object.date),
      numberOfSeats: object.numberOfSeats,
      owner: object.owner.id,
      open: object.open === 'true' ? true : false
    })
    .where('objects.id', '=', object.id)
    .executeTakeFirst()
}
