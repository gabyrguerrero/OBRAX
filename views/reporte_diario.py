"""Reporte diario de obra: avances, personal, horas, novedades y fotos."""
from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import flet as ft

from database.models import Asistencia, Avance, Foto, nuevo_id
from database.db import FOTOS
from . import componentes as base
from .componentes import fmt

CONDICIONES = ["Soleado", "Nublado", "Lluvia leve", "Lluvia fuerte", "Suspendida por clima"]


def construir(app):
    o = app.obra
    if o is None:
        return base.vacio(app)
    c = app.control()
    d = app.borrador
    if d is None or d.obra_id != o.id:
        d = app.borrador = app.cargar_borrador(date.today())
    abiertas = [a for a in c.hojas() if not a.cerrada]

    def cambiar_fecha(e):
        f = base.fecha(e.control.value)
        if f and f != app.borrador.fecha:
            app.borrador = app.cargar_borrador(f)
            app.refrescar()

    def poner_avance(act_id, texto):
        d.avances = [x for x in d.avances if x.actividad_id != act_id]
        if base.num(texto) > 0:
            d.avances.append(Avance(act_id, base.num(texto)))

    def marcar(t, valor):
        if valor:
            d.asistencias.append(Asistencia(t.id))
        else:
            d.asistencias = [x for x in d.asistencias if x.trabajador_id != t.id]
        app.refrescar()

    def alternar(p, act_id, valor):
        p.actividades = [x for x in p.actividades if x != act_id]
        if valor:
            p.actividades.append(act_id)

    # --- avances ---
    filas = [[a.nombre, a.unidad, fmt(a.cantidad), fmt(c.acum[a.id].cantidad),
              ft.TextField(value=str(next((x.cantidad for x in d.avances if x.actividad_id == a.id), "")), width=110,
                           on_change=lambda e, a=a: poner_avance(a.id, e.control.value))] for a in abiertas]

    # --- personal ---
    personal = []
    for t in c.trabajadores.values():
        p = next((x for x in d.asistencias if x.trabajador_id == t.id), None)
        fila = [ft.Checkbox(label=f"{t.nombre} · {t.cargo}", value=p is not None, on_change=lambda e, t=t: marcar(t, e.control.value))]
        bloque = [ft.Row(fila, wrap=True)]
        if p:
            fila += [ft.TextField(label="Horas", value=str(p.horas), width=90, on_change=lambda e, p=p: setattr(p, "horas", base.num(e.control.value))),
                     ft.TextField(label="Horas extra", value=str(p.horas_extra), width=110, on_change=lambda e, p=p: setattr(p, "horas_extra", base.num(e.control.value)))]
            bloque.append(ft.Row([ft.Text("Actividades:", color=base.GRIS)] + [
                ft.Checkbox(label=a.nombre, value=a.id in p.actividades, on_change=lambda e, a=a, p=p: alternar(p, a.id, e.control.value))
                for a in abiertas], wrap=True))
        personal.append(ft.Column(bloque, tight=True))

    # --- fotos ---
    foto_act = ft.Dropdown(label="Actividad de la foto", width=260, value=abiertas[0].id if abiertas else None,
                           options=[ft.DropdownOption(key=a.id, text=a.nombre) for a in c.hojas()])

    async def agregar_fotos(e):
        if not foto_act.value:
            return app.avisar("Elige la actividad de la foto.")
        archivos = await app.picker.pick_files(allow_multiple=True)
        for f in archivos or []:
            if f.path:
                destino = FOTOS / f"{nuevo_id()}{Path(f.path).suffix.lower()}"
                shutil.copy(f.path, destino)
                d.fotos.append(Foto(foto_act.value, str(destino)))
        app.refrescar()

    miniaturas = ft.Row([ft.Column([ft.Image(src=f.ruta, width=120, height=90),
                                    ft.Text(c.actividad(f.actividad_id).nombre if c.actividad(f.actividad_id) else "", size=11)], tight=True)
                         for f in d.fotos], wrap=True)

    def guardar(e):
        for p in d.asistencias:
            if not p.actividades:
                return app.avisar(f"Elige al menos una actividad para {c.trabajadores[p.trabajador_id].nombre}.")
        if not d.avances and not d.asistencias:
            return app.avisar("Registra al menos un avance o un trabajador.")
        app.repo.guardar_reporte(d)
        app.avisar("Reporte guardado.")
        app.refrescar()

    return base.pagina(
        base.titulo("Reporte diario de obra"),
        base.tarjeta(ft.Row([
            base.campo("Fecha (AAAA-MM-DD)", d.fecha.isoformat(), 190, on_submit=cambiar_fecha, on_blur=cambiar_fecha),
            ft.Dropdown(label="Condiciones de la jornada", width=240, value=d.condiciones,
                        options=[ft.DropdownOption(key=x, text=x) for x in CONDICIONES],
                        on_select=lambda e: setattr(d, "condiciones", e.control.value))], wrap=True)),
        base.tarjeta(base.subtitulo("Actividades ejecutadas"),
                     base.tabla(["Actividad", "Und", "Programado", "Acumulado guardado", "Cantidad de hoy"], filas, (2, 3))),
        base.tarjeta(base.subtitulo("Personal presente"), *(personal or [ft.Text("Registra trabajadores en la sección Personal.")]),
                     ft.Text("Si un trabajador participa en varias actividades, su costo se reparte entre ellas.", size=12, color=base.GRIS)),
        base.tarjeta(base.subtitulo("Novedades y observaciones"),
                     ft.TextField(label="Novedades del personal (ausencias, permisos, incapacidades)", value=d.novedades, multiline=True,
                                  min_lines=2, on_change=lambda e: setattr(d, "novedades", e.control.value)),
                     ft.TextField(label="Observaciones, dificultades, retrasos y reprocesos", value=d.observaciones, multiline=True,
                                  min_lines=2, on_change=lambda e: setattr(d, "observaciones", e.control.value))),
        base.tarjeta(base.subtitulo("Fotografías"),
                     ft.Row([foto_act, base.boton("Agregar fotos", agregar_fotos, ft.Icons.ADD_A_PHOTO)], wrap=True), miniaturas),
        base.boton("Guardar reporte del día", guardar, ft.Icons.SAVE))
