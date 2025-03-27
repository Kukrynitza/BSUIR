from hash_table import HashTable


def menu():
    ht = HashTable()

    while True:
        print("\n Меню:")
        print("1. Добавить запись")
        print("2. Найти запись")
        print("3. Удалить запись")
        print("4. Показать таблицу")
        print("5. Выйти")

        choice = input("Выберите действие: ")

        if choice == "1":
            key = input("Введите фамилию: ").strip()
            data = input("Введите данные (например, имя): ").strip()
            ht.insert(key, data)

        elif choice == "2":
            key = input("Введите фамилию для поиска: ").strip()
            ht.search(key)

        elif choice == "3":
            key = input("Введите фамилию для удаления: ").strip()
            ht.delete(key)

        elif choice == "4":
            ht.display()

        elif choice == "5":
            print(" Выход...")
            break

        else:
            print("Неверный ввод, попробуйте снова.")


menu()
