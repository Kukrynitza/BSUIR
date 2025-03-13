import flet as ft
from typing import List
from sorse.book import Book
from sorse.get_books import get_books
from components.list_of_books import list_of_books
from sorse.highlighted_books import HighlightedBooks
from components.pagination import pagination
from sorse.book_page import BookPage
from components.input_form import input_form


def find_menu(page: ft.Page, file_path: str):
    if file_path == '':
        return ft.Container(
            content=ft.Text('Добавьте файл', size=24, color='#FDD3E8'),
            alignment=ft.alignment.center,
            width=page.width
        )
    books: List[Book] = get_books(file_path)
    book_page: BookPage = BookPage()
    highlighted_books: HighlightedBooks = HighlightedBooks(books)
    out_books = ft.Column(
        controls=[
            list_of_books(page, highlighted_books.get_books(), book_page)
        ]
    )

    def update_list_of_book():
        out_books.controls.clear()
        out_books.controls.append(list_of_books(page, highlighted_books.get_books(), book_page))
        page.update()
    if highlighted_books.get_books():
        books_container = ft.Column(
            controls=[
                out_books,
                pagination(page, len(highlighted_books.get_books()), book_page, update_list_of_book)
            ]
        )
    else:
        books_container = ft.Column(
            controls=[
                out_books,
            ]
        )

    def update_highlighted_books():
        books_container.controls.clear()
        update_list_of_book()
        books_container.controls.append(out_books)
        if highlighted_books.get_books():
            books_container.controls.append(
                pagination(page, len(highlighted_books.get_books()), book_page, update_list_of_book))
        page.update()

    result_input_form = ft.Column(
        controls=[input_form(page, highlighted_books, update_highlighted_books)]
    )

    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Text('Поиск книг', size=24, color='#FDD3E8'),
                alignment=ft.alignment.center,
                width=page.width
            ),
            result_input_form,
            books_container
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER
    )
