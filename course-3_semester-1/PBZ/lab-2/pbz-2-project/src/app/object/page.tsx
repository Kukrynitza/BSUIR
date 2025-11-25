'use client'
import styles from "./page.module.css";
import { useEffect, useState } from "react";
import { useRouter } from 'next/navigation';
import CustomSelect from "@/companents/Select/select";
import selectOwnerLastNames from "@/actions/Owners/selectOwnersLastNames";
import selectObjects from "@/actions/Objects/selectObjects";
import insertObject from "@/actions/Objects/insertObject";
import deleteObject from "@/actions/Objects/deleteObject";
import updateObject from "@/actions/Objects/updateObject";
import { objectTypesOption } from "@/sorse/objectTypesOption";
import { openTypesOption } from "@/sorse/openTypesOption";

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

interface Option {
    value: string;
    label: string;
}

const open: Option[] = openTypesOption
const types: Option[] = objectTypesOption

export default function Page() {
  const router = useRouter();
  const currentDate = new Date()
  const [owners, setOwners] = useState<Option[]>([])
  const [objectData, setObjectData] = useState<Object[]>([])
  const [newObject, setNewObject] = useState<Object>({
  id: 0,
  name: '',
  address: '',
  type: 'Concert venue',
  numberOfSeats: 1,
  date: currentDate.toLocaleDateString('en-CA'),
  owner: {
    id: 0,
    lastName: 'Выберите владельца'
  },
  open: 'true'
  })
  const [isUpdateObject, setUpdateObject] = useState<boolean>(true)

  function handleTypeChange(id: number | undefined, newType: string) {
    if(id){
    setObjectData(prevObject => 
      prevObject?.map(object => 
        object.id === id 
          ? { ...object, type: newType }
          : object
      )
    );
  }
  else {
    setNewObject({...newObject, type: newType})
  }
  }
  function handleOpenChange(id: number | undefined, newOpen: string) {
    if(id){
    setObjectData(prevObject => 
      prevObject?.map(object => 
        object.id === id 
          ? { ...object, open: newOpen }
          : object
      )
    );
  }
  else {
    setNewObject({...newObject, open: newOpen})
  }
  }
    function handleOwnerChange(id: number | undefined, newOwner: string) {
    if(id){
    setObjectData(prevObject => 
      prevObject?.map(object => 
        object.id === id 
          ? { ...object, owner: {id: Number(newOwner), lastName: owners.find((element) => element.value === newOwner)?.label || 'Неизвестный'} }
          : object
      )
    );
  }
  else {
    setNewObject({...newObject, owner: {id: Number(newOwner), lastName: owners.find((element) => element.value === newOwner)?.label || 'Неизвестный'}})
  }
  }


  useEffect(() => 
  {
    async function updateObjects() {
      const dataOwner = await selectOwnerLastNames()
      if (dataOwner) {
        const dateToSet: Option[] = dataOwner.map((element) => ({
          value: String(element.id),
          label: element.lastName
        }))
        console.log(dateToSet)
        setOwners([...dateToSet, {value: '0', label: 'Выберите владельца'}])
      }
      const data = await selectObjects()
      setObjectData(
        data.map((element) => (
          {...element, owner: {
        id: element.owner,
        lastName: dataOwner.find((owner) => owner.id = element.owner)?.lastName || 'Нет'
      }}
    )
  ))
    }
    updateObjects()
  }, [isUpdateObject]
  )


  function nameChange(id:number, newName: string){
        if (newName.length === 0){
      return
    }
    setObjectData(prevObject =>
      prevObject?.map(object => 
        object.id === id
        ? {...object, name: newName}
        : object
      )
    )
  }

  function addressChange(id:number, newAddress: string){
        if (newAddress.length === 0){
      return
    }
    setObjectData(prevObject =>
      prevObject?.map(object => 
        object.id === id
        ? {...object, address: newAddress}
        : object
      )
    )
  }

    function dateChange(id:number, newDate: string){
        if (newDate.length === 0){
      return
    }
    setObjectData(prevObject =>
      prevObject?.map(object => 
        object.id === id
        ? {...object, date: newDate}
        : object
      )
    )
  }

    function numberOfSeatsChange(id:number, newNumberOfSeats: number){
    setObjectData(prevObject =>
      prevObject?.map(object => 
        object.id === id
        ? {...object, numberOfSeats: newNumberOfSeats}
        : object
      )
    )
  }
console.log(objectData)
  function addNewObject(){
    setObjectData(prevObject => [...prevObject, newObject])
    insertObject(newObject)
    setUpdateObject(isUpdate => !isUpdate)
    setNewObject({
  id: 0,
  name: '',
  address: '',
  date: currentDate.toLocaleDateString('en-CA'),
  type: 'Concert venue',
  numberOfSeats: 1,
  owner: {
    id: 0,
    lastName: 'Выберите владельца'
  },
  open: 'true'
  })
}
function buttonDeleteObject(id:number){
  setObjectData(prevObject => prevObject.filter((object) => object.id !== id))
  deleteObject(id)
}

function buttonUpdateObject(id: number){
  if (objectData){
  updateObject(objectData.find((object) => object.id === id))
  setUpdateObject(isUpdate => !isUpdate)
  }
}

function routeToHistory(id: number){
  router.push(`/sessions?object=${id}`);
}

  return (
    <div className={styles.page}>
      <main className={styles.main}>
          {objectData?.map((element) => (
            <ul className={styles.ul}  key={`${element.id}`} >
            <button className={styles.historyButton} onClick={() => routeToHistory(element.id)}> История объекта</button>
            <li className={styles.liCross}><button className={styles.cross} onClick={() => buttonDeleteObject(element.id)}><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="#fe6a1f" viewBox="0 0 256 256">
              <path d="M232,120h-8.34A96.14,96.14,0,0,0,136,32.34V24a8,8,0,0,0-16,0v8.34A96.14,96.14,0,0,0,32.34,120H24a8,8,0,0,0,0,16h8.34A96.14,96.14,0,0,0,120,223.66V232a8,8,0,0,0,16,0v-8.34A96.14,96.14,0,0,0,223.66,136H232a8,8,0,0,0,0-16Zm-96,87.6V200a8,8,0,0,0-16,0v7.6A80.15,80.15,0,0,1,48.4,136H56a8,8,0,0,0,0-16H48.4A80.15,80.15,0,0,1,120,48.4V56a8,8,0,0,0,16,0V48.4A80.15,80.15,0,0,1,207.6,120H200a8,8,0,0,0,0,16h7.6A80.15,80.15,0,0,1,136,207.6ZM128,88a40,40,0,1,0,40,40A40,40,0,0,0,128,88Zm0,64a24,24,0,1,1,24-24A24,24,0,0,1,128,152Z">
              </path>
            </svg>
            </button>
            </li>
            <li>Название: <input minLength={1} type="text" value={element.name} onChange={(event) => nameChange(element.id, event.target.value)} /></li>
            <li>Адрес: <input minLength={1} type="text" value={element.address} onChange={(event) => addressChange(element.id, event.target.value)}/></li>
            <li>Владелец: <CustomSelect options={owners} defaultValue={String(element.owner.id)} id={element.id} onValueChange = {handleOwnerChange}/></li>
            <li>Число мест: <input min={1} type="number" value={element.numberOfSeats} onChange={(event) => numberOfSeatsChange(element.id, Number(event.target.value))}/></li>
            <li>Тип: <CustomSelect options={types} defaultValue={element.type} id={element.id} onValueChange = {handleTypeChange}  /></li>
            <li>Открыт: <CustomSelect options={open} defaultValue={element.open} id={element.id} onValueChange = {handleOpenChange}  /></li>
            <li>Дата: <input type="date" value={element.date} onChange={(event) => dateChange(element.id, event.target.value)}/></li>  
              <button disabled={
              element.owner.id === 0
              }
              className={styles.button}
              onClick={() => buttonUpdateObject(element.id)}>Обновить</button>
          </ul>
          ))}
          <ul className={styles.ul}>
            <li>Название: <input type="text" value={newObject.name} onChange={(event) => setNewObject({...newObject, name: event.target.value})} /></li>
            <li>Адрес: <input type="text" value={newObject.address} onChange={(event) => setNewObject({...newObject, address: event.target.value})}/></li>
            <li>Владелец: <CustomSelect options={owners} defaultValue={String(newObject.owner.id)} id={undefined} onValueChange = {handleOwnerChange}/></li>
            <li>Число мест: <input min={1} type="number" value={newObject.numberOfSeats} onChange={(event) => setNewObject({...newObject, numberOfSeats: Number(event.target.value)})} /></li>
            <li>Тип: <CustomSelect options={types} defaultValue={newObject.type} id={undefined} onValueChange = {handleTypeChange}  /></li>
            {/* <li>Открыт: <CustomSelect options={open} defaultValue={newObject.open} id={undefined} onValueChange = {handleOpenChange}  /></li> */}
            <li>Дата: <input type="date" value={newObject.date} onChange={(event) => setNewObject({...newObject, date: event.target.value})}/></li>  
            <button className={styles.button} disabled={
              newObject.name.length < 1 
              || newObject.address.length < 1
              || newObject.owner.id === 0
            } 
              onClick={() => addNewObject()}>Создать</button>
          </ul>
      </main>
    </div>
  );
}
