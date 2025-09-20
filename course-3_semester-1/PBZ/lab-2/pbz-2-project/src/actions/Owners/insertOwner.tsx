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

export default async function insertOwners(owner: Owner, nameName: string | null | undefined) {
  if(nameName === undefined){
return
  }
  database
    .insertInto('owner')
    .values({
      name: nameName,
      surname: owner.surname,
      lastName: owner.lastName,
      firstName: owner.firstName,
      type: owner.type,
      number: owner.number
    })
    .executeTakeFirst()
}
