import xml.etree.ElementTree as ET
from sorse.book import Book
from typing import List


def get_books(file_path: str) -> List[Book]:
    books: List[Book] | List = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        for book in root.findall('book'):
            book_data = {
                'title': book.find('title').text,
                'author': book.find('author').text,
                'publisher': book.find('publisher').text,
                'volumes': book.find('volumes').text,
                'copies': book.find('copies').text,
                'total_volumes': book.find('totalVolumes').text
            }
            books.append(book_data)
    except FileNotFoundError:
        print(f"Ошибка: файл '{file_path}' не найден.")
    except ET.ParseError:
        print(f"Ошибка: некорректный XML-файл '{file_path}'.")
    except Exception as e:
        print(f"Произошла неизвестная ошибка: {e}")

    return books
