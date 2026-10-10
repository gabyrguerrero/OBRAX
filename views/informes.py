"""Informes (PDF, Excel, CSV) y bitácora con el registro fotográfico."""
from __future__ import annotations

import flet as ft

from database.db import INFORMES
from services import exportar as informes
from . import componentes as base


def _informe(app):
    c = app.control()
    if c is None:
        return base.vacio(app)
    inf = informes.construir(c, app.inf_tipo, app.inf_fecha)

    def cambiar_tipo(e):
        app.inf_tipo = e.control.value
        app.refrescar()

    def cambiar_fecha(e):
        f = base.fecha(e.control.value)
        if f and f != app.inf_fecha:
            app.inf_fecha = f
            app.refrescar()

    def exportar(extension, funcion):
        def accion(e):
            ruta = INFORMES / f"obrax-{app.inf_tipo}-{app.inf_fecha}.{extension}"
            try:
                funcion(inf, ruta)
                app.avisar(f"Informe guardado en {ruta}")
            except ImportError as error:
                app.avisar(f"Falta instalar: pip install {error.name}")
            except Exception as error:  # noqa: BLE001
                app.avisar(f"No se pudo exportar: {error}")
        return accion

    tablas = [base.tarjeta(base.subtitulo(t.titulo), base.tabla(t.encabezados, t.filas)) for t in inf.tablas]
    return base.pagina(
        base.titulo("Informes"),
        base.tarjeta(
            ft.Row([ft.Dropdown(label="Tipo de informe", width=200, value=app.inf_tipo, on_select=cambiar_tipo,
                                options=[ft.DropdownOption(key=k, text=k.capitalize()) for k in informes.TITULOS]),
                    base.campo("Fecha de referencia (AAAA-MM-DD)", app.inf_fecha.isoformat(), 270, on_submit=cambiar_fecha, on_blur=cambiar_fecha)], wrap=True),
            ft.Row([base.boton("PDF", exportar("pdf", informes.a_pdf), ft.Icons.PICTURE_AS_PDF),
                    base.boton("Excel", exportar("xlsx", informes.a_excel), ft.Icons.TABLE_CHART),
                    base.boton("CSV", exportar("csv", informes.a_csv), ft.Icons.DESCRIPTION, secundario=True)], wrap=True)),
        base.tarjeta(ft.Text(inf.titulo, size=20, weight=base.NEGRITA), ft.Text(inf.subtitulo, color=base.GRIS),
                     ft.Row([base.kpi(k, v) for k, v in inf.resumen], wrap=True, spacing=8)),
        *tablas)


def _bitacora(app):
    c = app.control()
    if c is None:
        return base.vacio(app)
    filtro = app.filtro_bitacora

    def cambiar(e):
        app.filtro_bitacora = "" if e.control.value == "todas" else e.control.value
        app.refrescar()

    selector = ft.Dropdown(label="Filtrar por actividad", width=300, value=filtro or "todas", on_select=cambiar,
                           options=[ft.DropdownOption(key="todas", text="Todas")]
                           + [ft.DropdownOption(key=a.id, text=a.nombre) for a in c.hojas()])
    tarjetas = []
    for r in reversed(c.reportes):
        if filtro and not any(x.actividad_id == filtro for x in r.avances + r.fotos):
            continue
        avances = " · ".join(f"{c.actividad(x.actividad_id).nombre}: {x.cantidad:g}" for x in r.avances if c.actividad(x.actividad_id))
        fotos = [f for f in r.fotos if not filtro or f.actividad_id == filtro]
        cuerpo = [base.subtitulo(f"{r.fecha:%d/%m/%Y} · {r.condiciones}"), ft.Text(avances or "Sin avances", color=base.GRIS)]
        cuerpo += [ft.Text(f"Novedades: {r.novedades}")] if r.novedades else []
        cuerpo += [ft.Text(f"Observaciones: {r.observaciones}")] if r.observaciones else []
        cuerpo.append(ft.Row([ft.Column([ft.Image(src=f.ruta, width=130, height=98), ft.Text(c.actividad(f.actividad_id).nombre, size=11)], tight=True)
                              for f in fotos if c.actividad(f.actividad_id)], wrap=True))
        tarjetas.append(base.tarjeta(*cuerpo))
    return base.pagina(base.titulo("Bitácora"), selector, *(tarjetas or [ft.Text("Aún no hay reportes.")]))


def construir(app):
    if app.control() is None:
        return base.vacio(app)
    return base.pagina(_informe(app), _bitacora(app))
