'use client'
import styles from "./page.module.css";
import { useEffect, useState } from "react";
import { useSearchParams } from 'next/navigation';
import selectSessions from "@/actions/Requests/selectSessions";
import { openTypesOption } from "@/sorse/openTypesOption";


interface Session {
  id: number
  createdAt: Date
  name: number
  open: boolean
}


export default function Page() {
  const openTypes = openTypesOption
  const [sessions, setSessions] = useState<Session[]>([])
  const searchParams = useSearchParams();
useEffect(() => {
  async function getSessions() {
    const objectId = searchParams.get('object') | undefined;
    if (objectId){
    const data = await selectSessions(objectId)
    setSessions(data)
  }
}
getSessions()
}, []
)

  return (
    <div className={styles.page}>
      <main className={styles.main}>
          <p className={styles.mainP}>История объекта</p>
          <li className={styles.mainLi}>
          {sessions?.map((element) => (
          <ul className={styles.ul}  key={`${element.id}`} >
            <li>Дата: {element.createdAt}</li>  
            <li>Открыт: {element.open}  {openTypes.find((openType) => openType.value === String(element.open))?.label}</li>
          </ul>
          ))}
          </li>
      </main>
    </div>
  );
}
