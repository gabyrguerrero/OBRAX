"""Router: barra superior, menú lateral y cambio entre las vistas."""
from __future__ import annotations

from datetime import date

import flet as ft

from services.calculos import Control
from database.demo import cargar_demo
from database.models import Actividad, Capitulo, Obra, Reporte, Trabajador
from database.db import Repositorio
from views import componentes as base
from views import crear_obra, informes, panel_gerencial, programacion, reporte_diario

# (nombre, icono, vista, solo_residente)
SECCIONES = [
    ("Panel gerencial", ft.Icons.DASHBOARD, panel_gerencial, False),
    ("Crear obra", ft.Icons.CONSTRUCTION, crear_obra, True),
    ("Programación", ft.Icons.TIMELINE, programacion, False),
    ("Reporte diario", ft.Icons.EDIT_NOTE, reporte_diario, True),
    ("Informes", ft.Icons.ASSESSMENT, informes, False),
]


class Router:
    def __init__(self, page: ft.Page, repo: Repositorio | None = None):
        self.page, self.repo = page, repo or Repositorio()
        self.rol, self.indice = "residente", 0
        self.borrador: Reporte | None = None  # reporte del día que se está llenando
        self.filtro_bitacora, self.inf_tipo, self.inf_fecha = "", "diario", date.today()
        self.picker = ft.FilePicker()
        page.services.append(self.picker)
        page.title = "OBRAx · Gestión y control de obra"
        page.padding = 0
        page.theme = ft.Theme(color_scheme_seed=base.AMARILLO)

        self.nombre_obra = ft.Text("", color="#C3CAD2", expand=True)
        selector = ft.Dropdown(
            value=self.rol, width=190, on_select=self.cambiar_rol,
            options=[ft.DropdownOption(key="residente", text="Vista residente"),
                     ft.DropdownOption(key="gerente", text="Vista gerente")])
        barra = ft.Container(bgcolor="#2A2F37", padding=10, content=ft.Row([
            ft.Text("OBRA", size=26, weight=base.NEGRITA, color="white"),
            ft.Text("x", size=26, weight=base.NEGRITA, color=base.AMARILLO), self.nombre_obra, selector]))
        self.riel = ft.NavigationRail(
            selected_index=0, label_type=ft.NavigationRailLabelType.ALL, min_width=96,
            destinations=self.destinos(), on_change=lambda e: self.ir(e.control.selected_index))
        self.cuerpo = ft.Container(expand=True, padding=16)
        page.add(ft.Column([barra, ft.Row([self.riel, ft.VerticalDivider(width=1), self.cuerpo], expand=True)],
                           expand=True, spacing=0))
        self.refrescar()

    # --- datos ---
    @property
    def obra(self) -> Obra | None:
        obras = self.repo.listar(Obra)
        return obras[0] if obras else None

    def control(self) -> Control | None:
        o = self.obra
        if o is None:
            return None
        r = self.repo
        return Control(o, r.listar(Capitulo, obra_id=o.id), r.listar(Actividad, obra_id=o.id),
                       r.listar(Trabajador, obra_id=o.id), r.listar_reportes(o.id))

    def cargar_borrador(self, fecha: date) -> Reporte:
        return self.repo.reporte_de(self.obra.id, fecha) or Reporte(self.obra.id, fecha)

    def cargar_demo(self) -> None:
        cargar_demo(self.repo)
        self.ir_a("Panel gerencial")

    # --- navegación ---
    def secciones(self):
        return [s for s in SECCIONES if self.rol == "residente" or not s[3]]

    def destinos(self):
        return [ft.NavigationRailDestination(icon=icono, label=nombre) for nombre, icono, _, _ in self.secciones()]

    def cambiar_rol(self, e) -> None:
        self.rol, self.indice = e.control.value, 0
        self.riel.destinations = self.destinos()
        self.refrescar()

    def ir(self, indice: int) -> None:
        self.indice = indice
        self.refrescar()

    def ir_a(self, nombre: str) -> None:
        self.ir([s[0] for s in self.secciones()].index(nombre))

    def refrescar(self) -> None:
        o = self.obra
        self.nombre_obra.value = o.nombre if o else "Gestión y control de obra"
        self.riel.selected_index = self.indice
        vista = self.secciones()[self.indice][2]
        self.cuerpo.content = ft.Column([vista.construir(self)], scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.update()

    def avisar(self, texto: str) -> None:
        self.page.show_dialog(ft.SnackBar(content=ft.Text(texto)))
