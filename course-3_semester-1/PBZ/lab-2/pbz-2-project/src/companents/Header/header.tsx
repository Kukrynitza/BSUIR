'use client'
import Link from "next/link"
import styles from "./header.module.css"
import { usePathname } from "next/navigation"

export default function Header(){
  const pathname = usePathname()
  return(
    <header className={styles.header}>
      <li className={styles.li}>
        <Link className={pathname === '/popularity' ? styles.linkActive : styles.link } href='/popularity'>Популярность</Link>
        <Link className={pathname === '/' ? styles.linkActive : styles.link } href='/'>Мероприятия</Link>
        <Link className={pathname === '/object' ? styles.linkActive : styles.link } href='/object'>Объекты</Link>
        <Link className={pathname === '/owner' ? styles.linkActive : styles.link } href='/owner'>Владельцы</Link>
      </li>
        <Link className={pathname === '/requests' ? styles.linkReqActive : styles.linkReq } href='/requests'>Запросы</Link>
    </header>
  )
}