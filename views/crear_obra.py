import flet as ft


def main(page: ft.Page):
    page.title = "OBRAx"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0

    def elegir_rol(rol):
        print(f"Entraste como {rol}")  # por ahora solo en la terminal

    encabezado = ft.Container(
        content=ft.Text(
            "OBRAx", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE
        ),
        padding=20,
    )

    boton_rol = ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Text("Ingresar como", color=ft.Colors.WHITE, size=16),
            bgcolor=ft.Colors.BLUE,
            padding=ft.padding.symmetric(horizontal=30, vertical=14),
            border_radius=8,
        ),
        items=[
            ft.PopupMenuItem(
                text="Trabajador", on_click=lambda e: elegir_rol("Trabajador")
            ),
            ft.PopupMenuItem(text="Gerente", on_click=lambda e: elegir_rol("Gerente")),
        ],
    )

    cuerpo = ft.Column(
        [boton_rol],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(encabezado, cuerpo)


ft.app(target=main)
