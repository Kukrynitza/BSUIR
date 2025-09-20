'use client'
import styles from "./page.module.css";
import { useEffect, useState } from "react";
import CustomSelect from "@/companents/Select/select";
import selectEvents from "@/actions/Event/selectEvents";
import insertEvent from "@/actions/Event/insertEvent";
import deleteEvent from "@/actions/Event/deleteEvent";
import updateEvent from "@/actions/Event/updateEvent";
import selectObjectNames from "@/actions/Objects/selectObjectNames";
import { eventTypesOption } from "@/sorse/eventTypesOption";

interface Event {
  id: number
  name: string
  date: string
  type: string
  object: {
    id: number
    name: string
  }
}

interface Option {
    value: string;
    label: string;
}

const eventTypes: Option[] = eventTypesOption

export default function Page() {
  const currentDate = new Date()
  const [objects, setObjects] = useState<Option[]>([])
  const [eventData, setEventData] = useState<Event[]>([])
  const [newEvent, setNewEvent] = useState<Event>({
  id: 0,
  name: '',
  date: currentDate.toLocaleDateString('en-CA'),
  type: 'Festival',
  object: {
    id: 0,
    name: 'Выберите объект'
  },
  })
  const [isUpdateEvent, setUpdateEvent] = useState<boolean>(true)

  function handleTypeChange(id: number | undefined, newType: string) {
    if(id){
    setEventData(prevEvent => 
      prevEvent?.map(event => 
        event.id === id 
          ? { ...event, type: newType }
          : event
      )
    );
  }
  else {
    setNewEvent({...newEvent, type: newType})
  }
  }

    function handleObjectChange(id: number | undefined, newObject: string) {
    if(id){
    setEventData(prevEvent => 
      prevEvent?.map(event => 
        event.id === id 
          ? { ...event, object: {id: Number(newObject), name: objects.find((element) => element.value === newObject)?.label || 'Неизвестный'} }
          : event
      )
    );
  }
  else {
    setNewEvent({...newEvent, object: {id: Number(newObject), name: objects.find((element) => element.value === newObject)?.label || 'Неизвестный'}})
  }
  }

  useEffect(() => 
  {
    async function updateEvent() {
      const dataObject = await selectObjectNames()
      if (dataObject) {
        const dateInSet: Option[] = dataObject.map((element) => ({
          value: String(element.id),
          label: element.name
        }))
        setObjects(objects => [ {value: '0', label: 'Выберите объект'}, ...dateInSet])
      }

      console.log("BLUAAAA")
      const data = await selectEvents()
      setEventData(
        data.map((element) => (
          {...element, object: {
        id: element.object,
        name: dataObject.find((object) => object.id = element.object)?.name || 'Нет'
      }}
    )
  ))
    }
    updateEvent()
  }, [isUpdateEvent]
  )


  function nameChange(id:number, newName: string){
        if (newName.length === 0){
      return
    }
    setEventData(prevOEvent =>
      prevOEvent?.map(event => 
        event.id === id
        ? {...event, name: newName}
        : event
      )
    )
  }

    function dateChange(id:number, newDate: string){
        if (newDate.length === 0){
      return
    }
    setEventData(prevOEvent =>
      prevOEvent?.map(event => 
        event.id === id
        ? {...event, date: newDate}
        : event
      )
    )
  }

  function addNewEvent(){
    setEventData(prevObject => [...prevObject, newEvent])
    insertEvent(newEvent)
    setUpdateEvent(isUpdate => !isUpdate)
    setNewEvent({
  id: 0,
  name: 'Выберите объект',
  date: currentDate.toLocaleDateString(),
  type: 'Festival',
  object: {
    id: 0,
    name: 'Выберите объект'
  }})
}
function buttonDeleteEvent(id:number){
  setEventData(prevEvent => prevEvent.filter((event) => event.id !== id))
  deleteEvent(id)
}

function buttonUpdateEvent(id: number){
  if (eventData){
  updateEvent(eventData.find((event) => event.id === id))
  setUpdateEvent(isUpdate => !isUpdate)
  }
}
  return (
    <div className={styles.page}>
      <main className={styles.main}>
          {eventData?.map((element) => (
          <ul className={styles.ul}  key={`${element.id}`} >
            <li className={styles.liCross}><button className={styles.cross} onClick={() => buttonDeleteEvent(element.id)}><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="#fe6a1f" viewBox="0 0 256 256">
              <path d="M232,120h-8.34A96.14,96.14,0,0,0,136,32.34V24a8,8,0,0,0-16,0v8.34A96.14,96.14,0,0,0,32.34,120H24a8,8,0,0,0,0,16h8.34A96.14,96.14,0,0,0,120,223.66V232a8,8,0,0,0,16,0v-8.34A96.14,96.14,0,0,0,223.66,136H232a8,8,0,0,0,0-16Zm-96,87.6V200a8,8,0,0,0-16,0v7.6A80.15,80.15,0,0,1,48.4,136H56a8,8,0,0,0,0-16H48.4A80.15,80.15,0,0,1,120,48.4V56a8,8,0,0,0,16,0V48.4A80.15,80.15,0,0,1,207.6,120H200a8,8,0,0,0,0,16h7.6A80.15,80.15,0,0,1,136,207.6ZM128,88a40,40,0,1,0,40,40A40,40,0,0,0,128,88Zm0,64a24,24,0,1,1,24-24A24,24,0,0,1,128,152Z">
              </path>
            </svg>
            </button>
            </li>
            <li>Название: <input minLength={1} type="text" value={element.name} onChange={(event) => nameChange(element.id, event.target.value)} /></li>
            <li>Дата: <input type="date" value={element.date} onChange={(event) => dateChange(element.id, event.target.value)}/></li>
            <li>Объект: <CustomSelect options={objects} defaultValue={String(element.object.id)} id={element.id} onValueChange = {handleObjectChange}  /></li>
            <li>Тип: <CustomSelect options={eventTypes} defaultValue={element.type} id={element.id} onValueChange = {handleTypeChange}  /></li>
              <button className={styles.button} disabled={
              element.object.id === 0
              }
              onClick={() => buttonUpdateEvent(element.id)}>Обновить</button>
          </ul>
          ))}
          <ul className={styles.ul}>
            <li>Название: <input type="text" value={newEvent.name} onChange={(event) => setNewEvent({...newEvent, name: event.target.value})} /></li>
            <li>Дата: <input min={1} type="date" value={newEvent.date} onChange={(event) => setNewEvent({...newEvent, date: event.target.value})} /></li>
            <li>Объект: <CustomSelect options={objects} defaultValue={String(newEvent.object.id)} id={undefined} onValueChange = {handleObjectChange}  /></li>
            <li>Тип: <CustomSelect options={eventTypes} defaultValue={newEvent.type} id={undefined} onValueChange = {handleTypeChange}  /></li>
            <button className={styles.button} disabled={
              newEvent.name.length < 1 
              || newEvent.object.id === 0
            } 
              onClick={() => addNewEvent()}>Создать</button>
          </ul>
      </main>
    </div>
  );
}
