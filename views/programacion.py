"""Cronograma: avance programado vs avance real."""
from __future__ import annotations

from datetime import date

import flet as ft

from . import componentes as base
from .componentes import fmt

ANCHO = 420  # píxeles de la línea de tiempo


def construir(app):
    c = app.control()
    if c is None or not c.actividades:
        return base.vacio(app) if c is None else base.pagina(base.titulo("Cronograma"), ft.Text("Agrega actividades en la sección Obra."))
    hoy = date.today()
    t0, t1 = min(a.inicio for a in c.actividades), max(a.fin for a in c.actividades)
    total = (t1 - t0).days + 1
    px = lambda dias: dias / total * ANCHO  # noqa: E731

    filas = []
    for cap, lista in c.arbol():
        filas.append([ft.Text(cap.nombre, weight=base.NEGRITA), "", "", "", "", ""])
        for a, nivel in lista:
            real, prog = c.porcentaje(a), c.programado(a, hoy)
            largo = max(3, px((a.fin - a.inicio).days + 1))
            hecho = largo * real / 100
            linea = ft.Row([ft.Container(width=px((a.inicio - t0).days)),
                            ft.Container(width=hecho, height=14, bgcolor=base.AMARILLO),
                            ft.Container(width=largo - hecho, height=14, bgcolor="#C9CED4")], spacing=0, width=ANCHO + 10)
            filas.append(["    " * nivel + a.nombre, f"{a.inicio:%d/%m} - {a.fin:%d/%m}", linea,
                          f"{fmt(prog)}%", f"{fmt(real)}%", base.estado_texto(c.estado(a, hoy))])

    return base.pagina(
        base.titulo("Cronograma"),
        base.tarjeta(ft.Text(f"Del {t0:%d/%m/%Y} al {t1:%d/%m/%Y} · hoy {hoy:%d/%m/%Y}. Amarillo: avance real. Gris: lo que falta de la duración programada.",
                             size=12, color=base.GRIS),
                     base.tabla(["Actividad", "Fechas", "Línea de tiempo", "Programado", "Real", "Estado"], filas, (3, 4))))
