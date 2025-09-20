import { CamelCasePlugin, type GeneratedAlways, Kysely, PostgresDialect } from 'kysely'
import { Pool } from 'pg'

export interface OwnerTable {
  id: GeneratedAlways<number>
  name: string | null
  firstName: string
  lastName: string
  surname: string
  type: string
  number: string
}

export interface PopularityTable {
  id: GeneratedAlways<number>
  date: Date
  object: number
  count: number
}

export interface EventTable {
  id: GeneratedAlways<number>
  name: string
  date: Date
  type: string
  object: number
}

export interface ObjectsTable {
  id: GeneratedAlways<number>
  name: string
  address: string
  type: string
  numberOfSeats: number
  owner: number
  open: boolean
  date: Date
}

export interface Database {
  objects: ObjectsTable
  event: EventTable
  owner: OwnerTable
  popularity: PopularityTable
}

const database = new Kysely<Database>({
  dialect: new PostgresDialect({
    pool: new Pool({
      connectionString: process.env.DATABASE_CONNECTION_STRING
    })
  }),
  plugins: [
    new CamelCasePlugin({
      maintainNestedObjectKeys: true
    })
  ]
})

export default database
