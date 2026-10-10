"""Panel de control gerencial."""
from __future__ import annotations

from collections import Counter
from datetime import date

import flet as ft

from services.calculos import Estado
from . import componentes as base
from .componentes import dinero, fmt


def grafico_costos(c) -> ft.Control:
    dias = sorted(c.dias)[-14:]
    if not dias:
        return ft.Text("Se mostrará cuando haya reportes diarios.", color=base.GRIS)
    mayor = max(c.dias[d].costo for d in dias) or 1
    return ft.Row([
        ft.Column([ft.Container(width=24, height=max(2, 110 * c.dias[d].costo / mayor), bgcolor=base.AMARILLO,
                                tooltip=dinero(c.dias[d].costo)),
                   ft.Text(d.strftime("%d"), size=11)], spacing=2, tight=True,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        for d in dias], vertical_alignment=ft.CrossAxisAlignment.END, spacing=6)


def construir(app):
    c = app.control()
    if c is None:
        return base.vacio(app)
    o, hoy = c.obra, date.today()
    real, prog = c.avance_obra(), c.programado_obra(hoy)
    n = Counter(c.estado(a, hoy) for a in c.hojas())
    dias = sorted(c.dias)
    ult = c.dias[dias[-1]] if dias else None
    dif = real - prog

    kpis = ft.Row([
        base.kpi("Avance real", f"{fmt(real)}%"),
        base.kpi("Avance programado", f"{fmt(prog)}%"),
        base.kpi("Diferencia", f"{fmt(dif)}%", base.ROJO if dif < -5 else base.VERDE),
        base.kpi("Terminadas", str(n[Estado.TERMINADA])),
        base.kpi("Pendientes / en curso", str(n[Estado.PENDIENTE] + n[Estado.EN_CURSO])),
        base.kpi("Atrasadas", str(n[Estado.ATRASADA]), base.ROJO if n[Estado.ATRASADA] else None),
        base.kpi("Costo MO último día", dinero(ult.costo if ult else 0)),
        base.kpi("Costo MO acumulado", dinero(c.costo_total)),
        base.kpi("Personal último día", str(ult.personas if ult else 0)),
    ], wrap=True, spacing=8, run_spacing=8)

    filas = []
    for cap, lista in c.arbol():
        r, p = c.avance_capitulo(cap, hoy)
        filas.append([ft.Text(cap.nombre, weight=base.NEGRITA), "", "", "", base.avance(r, p), "", "", "", ""])
        for a, nivel in lista:
            t, hoja = c.total(a), not c.hijos(a)
            filas.append([
                "    " * nivel + a.nombre, a.unidad, fmt(a.cantidad) if hoja else "", fmt(t.cantidad) if hoja else "",
                base.avance(c.porcentaje(a), c.programado(a, hoy)), base.estado_texto(c.estado(a, hoy)), dinero(t.costo),
                dinero(t.costo_unitario) if hoja and t.costo_unitario else "—",
                fmt(t.rendimiento, 2) if hoja and t.rendimiento else "—"])

    por_fecha = {r.fecha: r for r in c.reportes}
    personal = [[d.strftime("%d/%m/%Y"),
                 ", ".join(c.trabajadores[p.trabajador_id].nombre for p in por_fecha[d].asistencias if p.trabajador_id in c.trabajadores) or "—",
                 fmt(c.dias[d].horas), dinero(c.dias[d].costo)] for d in reversed(dias[-7:])]

    bloques = [ft.Text(o.nombre, size=26, weight=base.NEGRITA), kpis]
    if o.cierre == "solicitado" and app.rol == "gerente":
        def decidir(nuevo):
            def accion(e):
                o.cierre = nuevo
                app.repo.guardar(o)
                app.refrescar()
            return accion
        bloques.append(base.tarjeta(ft.Text("El residente solicitó el cierre de la obra.", weight=base.NEGRITA),
                                    ft.Row([base.boton("Aprobar cierre", decidir("aprobado"), ft.Icons.CHECK),
                                            base.boton("Devolver", decidir(""), secundario=True)])))
    if o.cierre == "aprobado":
        bloques.append(base.tarjeta(ft.Text("Obra cerrada y aprobada. El historial completo queda disponible.")))
    bloques += [
        base.tarjeta(base.subtitulo("Costo diario de mano de obra"), grafico_costos(c)),
        base.tarjeta(base.subtitulo("Actividades: avance, costos y rendimiento"),
                     base.tabla(["Actividad", "Und", "Cant.", "Ejecutado", "Real vs programado", "Estado", "Costo MO",
                                 "$/unidad", "Rend. (und/h)"], filas, (2, 3, 6, 7, 8))),
        base.tarjeta(base.subtitulo("Personal por día"), base.tabla(["Día", "Trabajaron", "Horas", "Costo"], personal, (2, 3))),
    ]
    if dias:
        r = por_fecha[dias[-1]]
        ultimo = [base.subtitulo(f"Último reporte ({r.fecha:%d/%m/%Y}) · {r.condiciones}")]
        ultimo += [ft.Text(f"Novedades: {r.novedades}")] if r.novedades else []
        ultimo += [ft.Text(f"Observaciones: {r.observaciones}")] if r.observaciones else []
        ultimo.append(ft.Row([ft.Column([ft.Image(src=f.ruta, width=120, height=90), ft.Text(c.actividad(f.actividad_id).nombre, size=11)], tight=True)
                              for f in r.fotos if c.actividad(f.actividad_id)], wrap=True))
        bloques.append(base.tarjeta(*ultimo))
    return base.pagina(*bloques)
