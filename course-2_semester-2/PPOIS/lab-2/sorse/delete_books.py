import xml.etree.ElementTree as ET
from sorse.book import Book
from typing import List


def delete_books(file_path: str, list_of_books: List[Book]):
    try:
        # print(list_of_books)
        tree = ET.parse(file_path)
        root = tree.getroot()
        deleted = False
        if list_of_books:
            print(1)
            for deleted_book in list_of_books:
                for book in root.findall('book'):
                    title_book = book.find("title").text
                    author_book = book.find("author").text
                    publisher_book = book.find("publisher").text
                    if (
                            title_book == deleted_book["title"] and
                            author_book == deleted_book["author"] and
                            publisher_book == deleted_book["publisher"]
                    ):
                        root.remove(book)
                        deleted = True
            if deleted:
                tree.write(file_path, encoding="utf-8", xml_declaration=True)
                print("Файл успешно обновлен!")
            else:
                print("Книги для удаления не найдены.")
    except FileNotFoundError:
        print(f"Ошибка: файл '{file_path}' не найден.")
    except ET.ParseError:
        print(f"Ошибка: некорректный XML-файл '{file_path}'.")
