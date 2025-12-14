import flet as ft
from components.header import header
from src.main_menu import main_menu
from sorse.get_books import get_books
from src.find_menu import find_menu
from src.delete_menu import delete_menu
from src.create_menu import create_menu


def main(page: ft.Page):
    page.title = "ППОИС-лабораторная-2"
    page.theme_mode = 'black'
    file_path: str = ''

    main_content = ft.Row()

    def show_main_menu(e=None):
        main_content.controls.clear()
        main_content.controls.append(main_menu(page, file_path))
        page.update()

    def show_create_menu(e):
        main_content.controls.clear()
        main_content.controls.append(create_menu(page, file_path))
        page.update()

    def show_delete_menu(e):
        main_content.controls.clear()
        main_content.controls.append(delete_menu(page, file_path))
        page.update()

    def show_find_menu(e):
        main_content.controls.clear()
        main_content.controls.append(find_menu(page, file_path))
        page.update()

    def handle_file_selected(origin_file_path: str):
        nonlocal file_path
        file_path = origin_file_path
        books = get_books(file_path)
        show_main_menu()
        page.update()

    page.appbar = header(
        page,
        show_main_menu,
        show_create_menu,
        show_delete_menu,
        handle_file_selected,
        show_find_menu)

    main_content.controls.append(main_menu(page, file_path))
    page.add(main_content)


ft.app(target=main)
