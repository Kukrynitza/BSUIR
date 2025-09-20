'use client'
import styles from "./page.module.css";
import { useEffect, useState } from "react";
import CustomSelect from "@/companents/Select/select";
import insertOwner from "@/actions/Owners/insertOwner";
import selectOwners from "@/actions/Owners/selectOwners";
import deleteOwner from "@/actions/Owners/deleteOwner";
import updateOwner from "@/actions/Owners/updateOwner";
import { number } from "valibot";

interface Owner {
  id: number;
  surname: string;
  firstName: string;
  lastName: string;
  type: string;
  number: string;
  objects?: string[];
}

interface Name{
  id: number;
  name: string | null;
}

interface Option {
    value: string;
    label: string;
}

const types: Option[] = [{value : 'Частное лицо', label : 'Частное лицо'}, {value : 'Юридическое лицо', label : 'Юридическое лицо'}]


export default function Page() {
  const [names, setNames] = useState<Name[]>([])
  const [ownersData, setOwnerData] = useState<Owner[]>([])
  const [newOwner, setNewOwner] = useState<Owner>({
  id: 99999999999999,
  surname: '',
  firstName: '',
  lastName: '',
  type: 'Частное лицо',
  number: '+375'
  })
  const [newName, setNewName] = useState<string | null>(null)
  const [isUpdateOwners, setUpdateOwners] = useState<boolean>(true)
  useEffect(() => 
  {
    async function update() {
      const data = await selectOwners()
      const allOwner: Owner[] = data.map((element) => {
        const {name, ...withoutName} = element
        return withoutName
      }) 
      const ownerNames: Name[] = data.map((element) =>({
        id: element.id,
        name: element.name
      }))
      setNames(ownerNames)
      setOwnerData(allOwner)
    }
    //     ([
    //   {
    //     id: 1,
    //     surname: 'Владимирович',
    //     firstName: 'Влад',
    //     lastName: 'Анушкин',
    //     type: 'Частное лицо',
    //     number: '+375332343124',
    //     objects: ['Юбилейная д.20', 'Центральная д.5'],
    //   },
    //   {
    //     id: 2,
    //     surname: 'Петров',
    //     firstName: 'Иван',
    //     lastName: 'Сергеевич',
    //     type: 'Юридическое лицо',
    //     number: '+375332312124',
    //     objects: ['Ленина д.15', 'Гагарина д.3'],
    //   },
    //   {
    //     id: 3,
    //     surname: 'Сидорова',
    //     firstName: 'Мария',
    //     lastName: 'Ивановна',
    //     type: 'Частное лицо',
    //     number: '+375333243124',
    //     objects: ['Садовая д.7'],
    //   }
    // ])
    update()
  }, [isUpdateOwners]
  )

  function handleTypeChange(ownerId: number | undefined, newType: string) {
    if(ownerId){
    setOwnerData(prevOwners => 
      prevOwners?.map(owner => 
        owner.id === ownerId 
          ? { ...owner, type: newType }
          : owner
      )
    );
    setNames(prevNames => prevNames?.map((name) => name.id === ownerId && ownersData.find((element) => element.id === name.id)?.type === 'Частное лицо'
      ? {id: name.id, name: null}
      : name))
  }
  else {
    setNewOwner({...newOwner, type: newType})
  }
  }

  function surnameChange(id:number, newSurname: string){
        if (newSurname.length === 0){
      return
    }
    setOwnerData(prevOwners =>
      prevOwners?.map(owner => 
        owner.id === id
        ? {...owner, surname: newSurname}
        : owner
      )
    )
  }
    function firstNameChange(id:number, newFirstName: string){
    if (newFirstName.length === 0){
      return
    }
    setOwnerData(prevOwners =>
      prevOwners?.map(owner => 
        owner.id === id
        ? {...owner, firstName: newFirstName}
        : owner
      )
    )
  }
    function lastNameChange(id:number, newLastName: string){
        if (newLastName.length === 0){
      return
    }
    setOwnerData(prevOwners =>
      prevOwners?.map(owner => 
        owner.id === id
        ? {...owner, lastName: newLastName}
        : owner
      )
    )
  }
    function numberChange(id:number, newNumber: string){
        if (newNumber.length === 0){
      return
    }
    setOwnerData(prevOwners =>
      prevOwners?.map(owner => 
        owner.id === id
        ? {...owner, number: newNumber}
        : owner
      )
    )
  }

      function nameChange(id:number, newName: string){
    if (newName.length === 0){
      return
    }
    setNames(prevNames =>
      prevNames?.map(name => 
        name.id === id
        ? {...name, name: newName}
        : name
      )
    )
  }

  function addNewOwner(){
    setOwnerData(prevOwners => [...prevOwners, newOwner])

    insertOwner(newOwner, newName)
    setUpdateOwners(isUpdate => !isUpdate)
    setNewOwner({
  id: 99999999999999,
  surname: '',
  firstName: '',
  lastName: '',
  type: 'Частное лицо',
  number: '+375'
  })
}

function buttonDeleteOwner(id:number){
  setOwnerData(prevOwners => prevOwners.filter((owner) => owner.id !== id))
  deleteOwner(id)
}

function buttonUpdateOwner(id: number){
  if (ownersData){
  updateOwner(ownersData.find((element) => element.id === id), names.find((element) => element.id === id)?.name)
  setUpdateOwners(isUpdate => !isUpdate)
  }
}

  return (
    <div className={styles.page}>
      <main className={styles.main}>
          {ownersData?.map((element) => (
          <ul className={styles.ul}  key={`${element.id}`} >
            <li className={styles.liCross}><button className={styles.cross} onClick={() => buttonDeleteOwner(element.id)}><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="#fe6a1f" viewBox="0 0 256 256">
              <path d="M232,120h-8.34A96.14,96.14,0,0,0,136,32.34V24a8,8,0,0,0-16,0v8.34A96.14,96.14,0,0,0,32.34,120H24a8,8,0,0,0,0,16h8.34A96.14,96.14,0,0,0,120,223.66V232a8,8,0,0,0,16,0v-8.34A96.14,96.14,0,0,0,223.66,136H232a8,8,0,0,0,0-16Zm-96,87.6V200a8,8,0,0,0-16,0v7.6A80.15,80.15,0,0,1,48.4,136H56a8,8,0,0,0,0-16H48.4A80.15,80.15,0,0,1,120,48.4V56a8,8,0,0,0,16,0V48.4A80.15,80.15,0,0,1,207.6,120H200a8,8,0,0,0,0,16h7.6A80.15,80.15,0,0,1,136,207.6ZM128,88a40,40,0,1,0,40,40A40,40,0,0,0,128,88Zm0,64a24,24,0,1,1,24-24A24,24,0,0,1,128,152Z">
              </path>
            </svg>
            </button>
            </li>
            {
            element.type === 'Юридическое лицо'
            ? <li>Название: <input minLength={1} type="text" value={names.find((findNames) => findNames.id === element.id)?.name || 'А'} onChange={(event) => nameChange(element.id, event.target.value)} /></li>   
            : <li>Название: ИП {element.lastName}</li>  
          }
            <li>Имя: <input minLength={1} type="text" value={element.firstName} onChange={(event) => firstNameChange(element.id, event.target.value)} /></li>
            <li>Фамилия: <input minLength={1} type="text" value={element.lastName} onChange={(event) => lastNameChange(element.id, event.target.value)}/></li>
            <li>Отчество: <input minLength={1} type="text" value={element.surname} onChange={(event) => surnameChange(element.id, event.target.value)} /></li>
            <li>Тип: <CustomSelect options={types} defaultValue={element.type} id={element.id} onValueChange = {handleTypeChange}  /></li>
            <li>Номер:<input minLength={1} type="tel" value={element.number} onChange={(event) => numberChange(element.id, event.target.value)} /></li>
            <li>Объекты:
              <ul className={styles.objects}>
              {element.objects && element.objects.map((object_name) => (
                <li key={object_name}>{object_name}</li>
              ))}
              </ul>
            </li>
              <button className={styles.button}
              onClick={() => buttonUpdateOwner(element.id)}>Обновить</button>
          </ul>
          ))}
          <ul className={styles.ul}>
            {
            newOwner.type === 'Юридическое лицо'
            ? <li>Название: <input minLength={1} type="text" value={newName || 'А'} onChange={(event) => setNewName(event.target.value)} /></li>  
            : <li>Название: ИП {newOwner.lastName}</li>   
            }
            <li>Имя: <input type="text" value={newOwner.firstName} onChange={(event) => setNewOwner({...newOwner, firstName: event.target.value})} /></li>
            <li>Фамилия: <input type="text" value={newOwner.lastName} onChange={(event) => setNewOwner({...newOwner, lastName: event.target.value})}/></li>
            <li>Отчество: <input type="text" value={newOwner.surname} onChange={(event) => setNewOwner({...newOwner,surname: event.target.value})} /></li>
            <li>Тип: <CustomSelect options={types} defaultValue={newOwner.type} id={undefined} onValueChange = {handleTypeChange}  /></li>
            <li>Номер:<input type="tel" value={newOwner.number} onChange={(event) => setNewOwner({...newOwner, number: event.target.value})} /></li>
            <button className={styles.button} disabled={
              newOwner.firstName.length < 1 
              || newOwner.lastName.length < 1 
              || newOwner.surname.length < 1} 
              onClick={() => addNewOwner()}>Сохранить</button>
          </ul>
      </main>
    </div>
  );
}
