'use server'
import database from '@/modules/database'

interface Owner {
  id: number;
  surname: string;
  firstName: string;
  lastName: string;
  type: string;
  number: string;
}

export default async function updateOwner(owner: Owner | undefined, nameName: string | null | undefined) {
  if (!owner || nameName === undefined) {
    return
  }
    database
    .updateTable('owner')
      .set({
      name: nameName,
      surname: owner.surname,
      lastName: owner.lastName,
      firstName: owner.firstName,
      type: owner.type,
      number: owner.number
    })
    .where('owner.id', '=', owner.id)
    .executeTakeFirst()
}
