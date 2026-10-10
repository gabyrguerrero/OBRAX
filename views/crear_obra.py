import flet as ft


def main(page: ft.Page):
    page.title = "OBRAx"
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0

    def elegir_rol(rol):
        # Por ahora solo muestra un aviso; luego aquí navegas a la vista del rol
        page.snack_bar = ft.SnackBar(ft.Text(f"Entraste como {rol}"))
        page.snack_bar.open = True
        page.update()

    # Esquina superior izquierda: nombre de la app
    encabezado = ft.Container(
        content=ft.Text(
            "OBRAx", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE
        ),
        padding=20,
    )

    # Botón centrado que despliega las dos opciones
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

    cuerpo = ft.Container(
        content=boton_rol,
        expand=True,  # ocupa todo el espacio restante
        alignment=ft.Alignment(0, 0),  # centra el botón
    )

    page.add(ft.Column([encabezado, cuerpo], expand=True, spacing=0))


ft.app(target=main)
