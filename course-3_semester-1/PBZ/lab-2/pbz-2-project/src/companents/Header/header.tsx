import Link from "next/link"
import styles from "./header.module.css"

export default function Header(){
  return(
    <header className={styles.header}>
      <li className={styles.li}>
        <Link className={styles.link} href='/popularity'>Популярность</Link>
        <Link className={styles.link} href='/'>Мероприятия</Link>
        <Link className={styles.link} href='/object'>Объекты</Link>
        <Link className={styles.link} href='/owner'>Владельцы</Link>
      </li>
        <Link className={styles.linkReq} href='/requests'>Запросы</Link>
    </header>
  )
}