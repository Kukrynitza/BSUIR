import xml.etree.ElementTree as ET
from sorse.book import Book


def create_book(file_path: str, book: Book):
    try:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

        except FileNotFoundError:
            root = ET.Element("books")
            tree = ET.ElementTree(root)

        new_book = ET.Element('book')
        print(book)
        count = 0
        for key, value in book.items():
            count += 1
            element = ET.Element(key.replace('_v', 'V'))
            element.text = value
            new_book.append(element)
        root.insert(0, new_book)
        print(count)
        print(book)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
    except Exception as e:
        print(f"Ошибка: {e}")
