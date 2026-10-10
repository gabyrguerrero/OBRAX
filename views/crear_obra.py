"""Crear obra: datos generales, capítulos, actividades, subactividades y personal."""
from __future__ import annotations

from datetime import date

import flet as ft

from database.models import Actividad, Capitulo, Obra, Trabajador
from . import componentes as base
from .componentes import dinero, fmt


def _obra(app):
    repo, o = app.repo, app.obra or Obra()
    nombre = base.campo("Nombre de la obra", o.nombre, 300)
    cliente, ubicacion = base.campo("Cliente", o.cliente), base.campo("Ubicación", o.ubicacion)
    inicio = base.campo("Inicio (AAAA-MM-DD)", o.inicio.isoformat(), 190)
    fin = base.campo("Fin (AAAA-MM-DD)", o.fin.isoformat(), 190)
    recargo = base.campo("Recargo horas extra (%)", o.recargo_extra, 190)

    def guardar_obra(e):
        i, f = base.fecha(inicio.value), base.fecha(fin.value)
        if not nombre.value.strip() or not i or not f or f < i:
            return app.avisar("Escribe el nombre y fechas válidas (AAAA-MM-DD).")
        o.nombre, o.cliente, o.ubicacion = nombre.value.strip(), cliente.value, ubicacion.value
        o.inicio, o.fin, o.recargo_extra = i, f, base.num(recargo.value)
        repo.guardar(o)
        app.refrescar()

    datos = base.tarjeta(base.subtitulo("Datos generales"), ft.Row([nombre, cliente, ubicacion], wrap=True),
                         ft.Row([inicio, fin, recargo], wrap=True), base.boton("Guardar obra", guardar_obra, ft.Icons.SAVE))
    if app.obra is None:
        return base.pagina(base.titulo("Obra"), datos)

    c, hoy = app.control(), date.today()
    nuevo_cap = base.campo("Nuevo capítulo", "", 260)

    def agregar_cap(e):
        if not nuevo_cap.value.strip():
            return app.avisar("Escribe el nombre del capítulo.")
        repo.guardar(Capitulo(o.id, nuevo_cap.value.strip()))
        app.refrescar()

    cap = ft.Dropdown(label="Capítulo", width=230, value=c.capitulos[0].id if c.capitulos else None,
                      options=[ft.DropdownOption(key=k.id, text=k.nombre) for k in c.capitulos])
    padre = ft.Dropdown(label="Subactividad de", width=250, value="ninguna",
                        options=[ft.DropdownOption(key="ninguna", text="— ninguna (es actividad) —")]
                        + [ft.DropdownOption(key=a.id, text=a.nombre) for a in c.actividades if not a.padre_id])
    nom, und = base.campo("Nombre de la actividad", "", 260), base.campo("Unidad (m², kg, m³, ml)", "", 170)
    cant = base.campo("Cantidad programada", "", 170)
    ini, fin_a = base.campo("Inicio (AAAA-MM-DD)", o.inicio.isoformat(), 190), base.campo("Fin (AAAA-MM-DD)", "", 190)

    def agregar_act(e):
        i, f, q = base.fecha(ini.value), base.fecha(fin_a.value), base.num(cant.value)
        if not cap.value or not nom.value.strip() or q <= 0 or not i or not f or f < i:
            return app.avisar("Elige capítulo y completa nombre, cantidad y fechas válidas.")
        p = "" if padre.value in (None, "ninguna") else padre.value
        cap_id = c.actividad(p).capitulo_id if p else cap.value
        repo.guardar(Actividad(o.id, cap_id, nom.value.strip(), und.value.strip() or "und", q, i, f, p))
        app.refrescar()

    def alternar(a):
        a.cerrada = not a.cerrada
        repo.guardar(a)
        app.refrescar()

    def borrar_act(a):
        repo.eliminar_actividad(a.id)
        app.refrescar()

    def borrar_cap(k):
        repo.eliminar_capitulo(k.id)
        app.refrescar()

    filas = []
    for k, lista in c.arbol():
        filas.append([ft.Text(k.nombre, weight=base.NEGRITA), "", "", "", "", "",
                      base.accion_icono(ft.Icons.DELETE_OUTLINE, "Eliminar capítulo", lambda e, k=k: borrar_cap(k))])
        for a, nivel in lista:
            hoja = not c.hijos(a)
            acciones = ft.Row([
                base.accion_icono(ft.Icons.REPLAY if a.cerrada else ft.Icons.CHECK_CIRCLE_OUTLINE,
                                  "Reabrir" if a.cerrada else "Finalizar", lambda e, a=a: alternar(a)) if hoja else ft.Container(),
                base.accion_icono(ft.Icons.DELETE_OUTLINE, "Eliminar", lambda e, a=a: borrar_act(a))], spacing=0)
            filas.append(["    " * nivel + a.nombre, a.unidad, fmt(a.cantidad), a.inicio.strftime("%d/%m/%Y"),
                          a.fin.strftime("%d/%m/%Y"), base.estado_texto(c.estado(a, hoy)), acciones])

    def pedir_cierre(e):
        if any(c.estado(a, hoy).value != "Terminada" for a in c.hojas()):
            return app.avisar("Aún hay actividades sin finalizar.")
        o.cierre = "solicitado"
        repo.guardar(o)
        app.refrescar()

    estado_cierre = {"aprobado": "Cierre aprobado por gerencia. El historial queda guardado.",
                     "solicitado": "Cierre solicitado. Esperando la aprobación del gerente."}.get(o.cierre)
    cierre = ft.Text(estado_cierre) if estado_cierre else ft.Column([
        ft.Text("Finaliza todas las actividades y solicita el cierre para revisión del gerente.", color=base.GRIS),
        base.boton("Solicitar cierre de obra", pedir_cierre, ft.Icons.LOCK_OUTLINE)])

    return base.pagina(
        base.titulo("Obra"), datos,
        base.tarjeta(base.subtitulo("Capítulos y actividades"),
                     ft.Row([nuevo_cap, base.boton("Agregar capítulo", agregar_cap, ft.Icons.ADD)], wrap=True),
                     ft.Row([cap, padre, nom, und, cant, ini, fin_a], wrap=True),
                     base.boton("Agregar actividad", agregar_act, ft.Icons.ADD)),
        base.tarjeta(base.tabla(["Capítulo / actividad", "Und", "Cant.", "Inicio", "Fin", "Estado", ""], filas, (2,))),
        base.tarjeta(base.subtitulo("Cierre de obra"), cierre))


def _personal(app):
    o = app.obra
    if o is None:
        return base.vacio(app)
    nom, cargo = base.campo("Nombre", "", 240), base.campo("Cargo", "", 200)
    salario, laboral = base.campo("Salario mensual ($)", "", 200), base.campo("Costo laboral sobre el salario (%)", 52, 260)

    def agregar(e):
        if not nom.value.strip() or base.num(salario.value) <= 0:
            return app.avisar("Escribe el nombre y el salario mensual.")
        app.repo.guardar(Trabajador(o.id, nom.value.strip(), cargo.value.strip(), base.num(salario.value), base.num(laboral.value)))
        app.refrescar()

    def quitar(t):
        app.repo.eliminar(Trabajador, t.id)
        app.refrescar()

    filas = [[t.nombre, t.cargo, dinero(t.salario), f"{t.costo_laboral:g}%", dinero(t.valor_hora),
              base.accion_icono(ft.Icons.DELETE_OUTLINE, "Quitar", lambda e, t=t: quitar(t))]
             for t in app.repo.listar(Trabajador, obra_id=o.id)]
    return base.pagina(
        base.titulo("Personal"),
        base.tarjeta(base.subtitulo("Registrar trabajador"), ft.Row([nom, cargo, salario, laboral], wrap=True),
                     base.boton("Registrar", agregar, ft.Icons.PERSON_ADD)),
        base.tarjeta(base.tabla(["Nombre", "Cargo", "Salario", "Costo laboral", "Valor hora", ""], filas, (2, 3, 4)),
                     ft.Text("Valor hora = salario × (1 + costo laboral) ÷ 240 h. La hora extra usa el recargo de la obra.",
                             size=12, color=base.GRIS)))


def construir(app):
    if app.obra is None:
        return _obra(app)
    return base.pagina(_obra(app), _personal(app))
