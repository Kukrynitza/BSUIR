'use client'
import styles from "./page.module.css";
import { useEffect, useState } from "react";
import CustomSelect from "@/companents/Select/select";
import { objectTypesOption } from "@/sorse/objectTypesOption";
import selectOwnersLastName from "@/actions/Owners/selectOwnersLastNames";
import selectObjectsInType from "@/actions/Requests/selectObjectsInType";
import { openTypesOption } from "@/sorse/openTypesOption";
import selectObjectsInOpen from "@/actions/Requests/selectObjectsInOpen";
import selectEventsInTwoWeek from "@/actions/Requests/selectEventsInTwoWeek";
import { eventTypesOption } from "@/sorse/eventTypesOption";


interface Option {
    value: string;
    label: string;
}

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

interface Event {
  id: number
  name: string
  date: string
  type: string
  object: string
  address: string
}


export default function Page() {
  const objectTypes: Option[] = objectTypesOption
  const openTypes: Option[] = openTypesOption
  const eventTypes: Option[] = eventTypesOption
  const [objectInType, setObjectInType] = useState<Object[]>([])
  const [objectInOpen, setObjectInOpen] = useState<Object[]>([])
  const [eventsInTwoWeek, setEventsInTwoWeek] = useState<Event[]>([])
  const [currentObjectInType, setCurrentObjectInType] = useState<string>('Concert venue')

  useEffect(() => {
  async function updateObjects() {
    const data = await selectObjectsInOpen()
    setObjectInOpen(data)
  }
  updateObjects()
    }, []
  )

  useEffect(() => {
  async function updateObjects() {
    const eventData = await selectEventsInTwoWeek()
    setEventsInTwoWeek(eventData)
  }
  updateObjects()
    }, []
  )

  useEffect(() => 
  {
    async function updateObjects() {
      const dataOwner = await selectOwnersLastName()
      if (dataOwner) {
        const dateToSet: Option[] = dataOwner.map((element) => ({
          value: String(element.id),
          label: element.lastName
        }))
      }
      const data = await selectObjectsInType(currentObjectInType)
      setObjectInType(
        data.map((element) => (
          {...element, owner: {
        id: element.owner,
        lastName: dataOwner.find((owner) => owner.id = element.owner)?.lastName || 'Нет'
      }}
    )
  ))
    }
    updateObjects()
  }, [currentObjectInType]
  )


  function handleCurrentObjectTypeChange(id: number | undefined, newType: string) {
    setCurrentObjectInType(newType)
  }

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <li className={styles.mainLi}>
          <p>Просмотр списка объектов города на текущую дату</p>
          {objectInOpen?.map((element) => (
          <ul className={styles.ul}  key={`${element.id}`} >
            <li>Название: {element.name}</li>
            <li>Адрес: {element.address}</li>
            <li>Владелец: {element.owner.lastName}</li>
            <li>Число мест: {element.numberOfSeats}</li>
            <li>Тип: {objectTypes.find((objectType) => objectType.value === element.type)?.label}</li>
            <li>Открыт: {openTypes.find((openType) => openType.value === element.open)?.label}</li>
            <li>Дата: {element.date}</li>  
          </ul>
          ))}  
        </li>
        <li className={styles.mainLi}>
          <p className={styles.p}>Просмотр списка мероприятий, которые будут проводится в ближайшие 2 недели</p>
          {eventsInTwoWeek?.map((element) => (
          <ul className={styles.ul}  key={`${element.id}`} >
            <li>Название: {element.name}</li>
            <li>Дата: {element.date}</li>  
            <li>Тип: {eventTypes.find((eventType) => eventType.value === element.type)?.label}</li>
            <li>Объект: {element.object}</li>
            <li>Адрес: {element.address}</li>
          </ul>
          ))}  
        </li>
        <li className={styles.mainLiLast}>
          <p>Просмотр списка объектов заданного типа на текущую дату.</p>
          <CustomSelect options={objectTypes} defaultValue={currentObjectInType} id={undefined} onValueChange = {handleCurrentObjectTypeChange}  />
          {objectInType?.map((element) => (
          <ul className={styles.ul}  key={`${element.id}`} >
            <li>Название: {element.name}</li>
            <li>Адрес: {element.address}</li>
            <li>Владелец: {element.owner.lastName}</li>
            <li>Число мест: {element.numberOfSeats}</li>
            <li>Тип: {objectTypes.find((objectType) => objectType.value === element.type)?.label}</li>
            <li>Открыт: {openTypes.find((openType) => openType.value === element.open)?.label}</li>
            <li>Дата: {element.date}</li>  
          </ul>
          ))}  
        </li>
      </main>
    </div>
  );
}
