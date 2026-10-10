"""Datos de ejemplo para explorar la aplicación."""
from __future__ import annotations

from datetime import date, timedelta

from .models import Actividad, Asistencia, Avance, Capitulo, Obra, Reporte, Trabajador
from .db import Repositorio


def cargar_demo(repo: Repositorio) -> Obra:
    hoy = date.today()
    d = lambda n: hoy + timedelta(days=n)  # noqa: E731
    obra = Obra("Edificio Torres del Parque", "Constructora Andina", "Bogotá", d(-10), d(60))
    repo.guardar(obra)
    for c in (Capitulo(obra.id, "Cimentación", "c1"), Capitulo(obra.id, "Estructura", "c2")):
        repo.guardar(c)
    acts = [
        Actividad(obra.id, "c1", "Excavación", "m³", 120, d(-10), d(-3), id="a1"),
        Actividad(obra.id, "c1", "Concreto de limpieza", "m²", 80, d(-4), d(2), id="a2"),
        Actividad(obra.id, "c1", "Acero de refuerzo", "kg", 3200, d(-3), d(8), id="a3"),
        Actividad(obra.id, "c1", "Figurado", "kg", 1600, d(-3), d(4), padre_id="a3", id="a3a"),
        Actividad(obra.id, "c1", "Armado", "kg", 1600, d(-2), d(8), padre_id="a3", id="a3b"),
        Actividad(obra.id, "c2", "Columnas nivel 1", "m³", 40, d(5), d(25), id="a4"),
    ]
    for a in acts:
        repo.guardar(a)
    for id_, nombre, cargo, sal in [("w1", "Carlos Ruiz", "Oficial", 2_200_000), ("w2", "Luis Pérez", "Ayudante", 1_600_000),
                                    ("w3", "Marta Gómez", "Maestra de obra", 2_800_000), ("w4", "Jorge Díaz", "Ayudante", 1_600_000)]:
        repo.guardar(Trabajador(obra.id, nombre, cargo, sal, id=id_))
    for i in range(-9, 1):
        r = Reporte(obra.id, d(i), "Lluvia leve" if i == -5 else "Soleado")
        if i == -5:
            r.observaciones = "Lluvia en la tarde; se suspendió 2 horas el trabajo."
        if i == -6:
            r.novedades = "Jorge Díaz llegó 1 hora tarde."
        if i <= -3:
            r.avances.append(Avance("a1", 17))
            r.asistencias += [Asistencia("w1", 8, 0 if i % 3 else 2, ["a1"]), Asistencia("w2", 8, 0, ["a1"]), Asistencia("w4", 8, 0, ["a1"])]
        else:
            r.asistencias += [Asistencia("w1", 8, 0, ["a2", "a3a"]), Asistencia("w2", 8, 2 if i == 0 else 0, ["a2"]), Asistencia("w3", 8, 0, ["a3a", "a3b"])]
        if i >= -4:
            r.avances.append(Avance("a2", 12))
        if i >= -3:
            r.avances.append(Avance("a3a", 300))
        if i >= -2:
            r.avances.append(Avance("a3b", 150))
        repo.guardar_reporte(r)
    return obra
