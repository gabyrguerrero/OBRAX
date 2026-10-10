"""OBRAx · Gestión y control de obra.   Ejecuta:  python main.py"""
import flet as ft

from router import Router


def main(page: ft.Page) -> None:
    Router(page)


if __name__ == "__main__":
    ft.run(main)
