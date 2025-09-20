'use client'
import styles from "./page.module.css";
import { useEffect, useState } from "react";
import CustomSelect from "@/companents/Select/select";
import selectObjectNames from "@/actions/Objects/selectObjectNames";
import updatePopularity from "@/actions/Popularity/updatePopularity";
import deletePopularity from "@/actions/Popularity/deletePopularity";
import selectPopularity from "@/actions/Popularity/selectPopularity";
import insertPopularity from "@/actions/Popularity/insertPopularity";

interface Popularity {
  id: number
  date: string
  object: {
    id: number
    name: string
  }
  count: number
}

interface Option {
    value: string;
    label: string;
}

export default function Page() {
  const currentDate = new Date()
  const [objects, setObjects] = useState<Option[]>([])
  const [popularityData, setPopularityData] = useState<Popularity[]>([])
  const [newPopularity, setNewPopularity] = useState<Popularity>({
  id: 0,
  count: 0,
  date: currentDate.toLocaleDateString('en-CA'),
  object: {
    id: 0,
    name: 'Выберите объект'
  },
  })
  const [isUpdatePopularity, setUpdatePopularity] = useState<boolean>(true)

    function handleObjectChange(id: number | undefined, newObject: string) {
    if(id){
    setPopularityData(prevPopularity => 
      prevPopularity?.map(popularity => 
        popularity.id === id 
          ? { ...popularity, object: {id: Number(newObject), name: objects.find((element) => element.value === newObject)?.label || 'Неизвестный'} }
          : popularity
      )
    );
  }
  else {
    setNewPopularity({...newPopularity, object: {id: Number(newObject), name: objects.find((element) => element.value === newObject)?.label || 'Неизвестный'}})
  }
  }

  useEffect(() => 
  {
    async function updatePopularity() {
      const dataObject = await selectObjectNames()
      if (dataObject) {
        const dateInSet: Option[] = dataObject.map((element) => ({
          value: String(element.id),
          label: element.name
        }))
        setObjects(objects => [ {value: '0', label: 'Выберите объект'}, ...dateInSet])
      }

      console.log("BLUAAAA")
      const data = await selectPopularity()
      setPopularityData(
        data.map((element) => (
          {...element, object: {
        id: element.object,
        name: dataObject.find((object) => object.id = element.object)?.name || 'Нет'
      }}
    )
  ))
    }
    updatePopularity()
  }, [isUpdatePopularity]
  )

    function dateChange(id:number, newDate: string){
        if (newDate.length === 0){
      return
    }
    setPopularityData(prevPopularity =>
      prevPopularity?.map(popularity => 
        popularity.id === id
        ? {...popularity, date: newDate}
        : popularity
      )
    )
  }

      function countChange(id:number, newCount: string){
        if(Number(newCount) < 0){
          return
        }
    setPopularityData(prevPopularity =>
      prevPopularity?.map(popularity => 
        popularity.id === id
        ? {...popularity, count: Number(newCount)}
        : popularity
      )
    )
  }

  function addNewPopularity(){
    setPopularityData(prevPopularity => [...prevPopularity, newPopularity])
    insertPopularity(newPopularity)
    setUpdatePopularity(isUpdate => !isUpdate)
    setNewPopularity({
  id: 0,
  count: 0,
  date: currentDate.toLocaleDateString('en-CA'),
  object: {
    id: 0,
    name: 'Выберите объект'
  }})
}
function buttonDeletePopularity(id:number){
  setPopularityData(prevPopularity => prevPopularity.filter((popularity) => popularity.id !== id))
  deletePopularity(id)
}

function buttonUpdatePopularity(id: number){
  if (popularityData){
  updatePopularity(popularityData.find((popularity) => popularity.id === id))
  setUpdatePopularity(isUpdate => !isUpdate)
  }
}

  return (
    <div className={styles.page}>
      <main className={styles.main}>
          {popularityData?.map((element) => (
          <ul className={styles.ul}  key={`${element.id}`} >
            <li className={styles.liCross}><button className={styles.cross} onClick={() => buttonDeletePopularity(element.id)}><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="#fe6a1f" viewBox="0 0 256 256">
              <path d="M232,120h-8.34A96.14,96.14,0,0,0,136,32.34V24a8,8,0,0,0-16,0v8.34A96.14,96.14,0,0,0,32.34,120H24a8,8,0,0,0,0,16h8.34A96.14,96.14,0,0,0,120,223.66V232a8,8,0,0,0,16,0v-8.34A96.14,96.14,0,0,0,223.66,136H232a8,8,0,0,0,0-16Zm-96,87.6V200a8,8,0,0,0-16,0v7.6A80.15,80.15,0,0,1,48.4,136H56a8,8,0,0,0,0-16H48.4A80.15,80.15,0,0,1,120,48.4V56a8,8,0,0,0,16,0V48.4A80.15,80.15,0,0,1,207.6,120H200a8,8,0,0,0,0,16h7.6A80.15,80.15,0,0,1,136,207.6ZM128,88a40,40,0,1,0,40,40A40,40,0,0,0,128,88Zm0,64a24,24,0,1,1,24-24A24,24,0,0,1,128,152Z">
              </path>
            </svg>
            </button>
            </li>
            <li>Количество: <input min={0} type="number" value={element.count} onChange={(event) => countChange(element.id, event.target.value)} /></li>
            <li>Дата: <input type="date" value={element.date} onChange={(event) => dateChange(element.id, event.target.value)}/></li>
            <li>Объект: <CustomSelect options={objects} defaultValue={String(element.object.id)} id={element.id} onValueChange = {handleObjectChange}  /></li>
              <button className={styles.button} disabled={
              element.object.id === 0
              }
              onClick={() => buttonUpdatePopularity(element.id)}>Обновить</button>
          </ul>
          ))}
          <ul className={styles.ul}>
            <li>Количество: <input min={0} type="number" value={newPopularity.count} onChange={(event) => setNewPopularity({...newPopularity, count: Number(event.target.value)})} /></li>
            <li>Дата: <input type="date" value={newPopularity.date} onChange={(event) => setNewPopularity({...newPopularity, date: event.target.value})} /></li>
            <li>Объект: <CustomSelect options={objects} defaultValue={String(newPopularity.object.id)} id={undefined} onValueChange = {handleObjectChange}  /></li>
            <button className={styles.button} disabled={
              newPopularity.object.id === 0
            } 
              onClick={() => addNewPopularity()}>Создать</button>
          </ul>
      </main>
    </div>
  );
}
