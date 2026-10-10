"""Cálculos de avance, costos y rendimiento (sin dependencias de interfaz)."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

from database.models import Actividad, Capitulo, Obra, Reporte, Trabajador


class Estado(str, Enum):
    TERMINADA = "Terminada"
    PENDIENTE = "Pendiente"
    EN_CURSO = "En curso"
    ATRASADA = "Atrasada"


@dataclass
class Acumulado:
    cantidad: float = 0.0
    horas: float = 0.0
    costo: float = 0.0

    @property
    def costo_unitario(self) -> float | None:
        return self.costo / self.cantidad if self.cantidad else None

    @property
    def rendimiento(self) -> float | None:  # unidades por hora
        return self.cantidad / self.horas if self.horas else None


@dataclass
class Dia:
    fecha: date
    costo: float = 0.0
    horas: float = 0.0
    personas: int = 0


def _media(valores) -> float:
    valores = list(valores)
    return sum(valores) / len(valores) if valores else 0.0


def periodo(reportes: list[Reporte], tipo: str, ref: date) -> list[Reporte]:
    if tipo == "diario":
        return [r for r in reportes if r.fecha == ref]
    if tipo == "semanal":
        return [r for r in reportes if ref - timedelta(days=6) <= r.fecha <= ref]
    if tipo == "mensual":
        return [r for r in reportes if (r.fecha.year, r.fecha.month) == (ref.year, ref.month)]
    return list(reportes)  # final


class Control:
    def __init__(self, obra: Obra, capitulos: list[Capitulo], actividades: list[Actividad],
                 trabajadores: list[Trabajador], reportes: list[Reporte]):
        self.obra, self.capitulos, self.actividades = obra, capitulos, actividades
        self.trabajadores = {t.id: t for t in trabajadores}
        self.reportes = sorted(reportes, key=lambda r: r.fecha)
        self.por_id = {a.id: a for a in actividades}
        self._hijos: dict[str, list[Actividad]] = defaultdict(list)
        for a in actividades:
            if a.padre_id:
                self._hijos[a.padre_id].append(a)
        self.acum, self.dias = self.calcular(self.reportes)

    # --- costos y cantidades ---
    def calcular(self, reportes: list[Reporte]):
        """Acumula cantidades, horas y costo por actividad y por día.

        El costo de un trabajador se reparte en partes iguales entre las
        actividades en las que participó, así no se duplica.
        """
        acum = {a.id: Acumulado() for a in self.actividades}
        dias: dict[date, Dia] = {}
        recargo = 1 + self.obra.recargo_extra / 100
        for r in reportes:
            dia = dias.setdefault(r.fecha, Dia(r.fecha))
            for av in r.avances:
                if av.actividad_id in acum:
                    acum[av.actividad_id].cantidad += av.cantidad
            for p in r.asistencias:
                t = self.trabajadores.get(p.trabajador_id)
                if t is None:
                    continue
                horas = p.horas + p.horas_extra
                costo = t.valor_hora * (p.horas + p.horas_extra * recargo)
                dia.costo += costo
                dia.horas += horas
                dia.personas += 1
                destino = [i for i in p.actividades if i in acum]
                for i in destino:
                    acum[i].horas += horas / len(destino)
                    acum[i].costo += costo / len(destino)
        return acum, dias

    @property
    def costo_total(self) -> float:
        return sum(d.costo for d in self.dias.values())

    # --- estructura ---
    def actividad(self, id: str) -> Actividad | None:
        return self.por_id.get(id)

    def hijos(self, a: Actividad) -> list[Actividad]:
        return self._hijos.get(a.id, [])

    def hojas(self, a: Actividad | None = None) -> list[Actividad]:
        if a is None:
            return [x for x in self.actividades if not self.hijos(x)]
        h = self.hijos(a)
        return [a] if not h else [x for k in h for x in self.hojas(k)]

    def arbol(self):
        def rec(cap, padre, nivel):
            for a in self.actividades:
                if a.capitulo_id == cap.id and a.padre_id == padre:
                    yield a, nivel
                    yield from rec(cap, a.id, nivel + 1)
        return [(c, list(rec(c, "", 0))) for c in self.capitulos]

    def total(self, a: Actividad) -> Acumulado:
        t = Acumulado()
        for h in self.hojas(a):
            x = self.acum[h.id]
            t.cantidad += x.cantidad
            t.horas += x.horas
            t.costo += x.costo
        return t

    # --- avance ---
    def porcentaje(self, a: Actividad) -> float:
        h = self.hijos(a)
        if h:
            return _media(self.porcentaje(x) for x in h)
        if a.cerrada:
            return 100.0
        return min(100.0, self.acum[a.id].cantidad / a.cantidad * 100) if a.cantidad > 0 else 0.0

    def programado(self, a: Actividad, hoy: date) -> float:
        h = self.hijos(a)
        if h:
            return _media(self.programado(x, hoy) for x in h)
        if hoy < a.inicio:
            return 0.0
        if hoy > a.fin:
            return 100.0
        return ((hoy - a.inicio).days + 1) / ((a.fin - a.inicio).days + 1) * 100

    def estado(self, a: Actividad, hoy: date) -> Estado:
        real = self.porcentaje(a)
        if real >= 99.95:
            return Estado.TERMINADA
        if hoy < a.inicio:
            return Estado.PENDIENTE
        if self.programado(a, hoy) - real > 10 or hoy > a.fin:
            return Estado.ATRASADA
        return Estado.EN_CURSO

    def avance_obra(self) -> float:
        return _media(self.porcentaje(a) for a in self.hojas())

    def programado_obra(self, hoy: date) -> float:
        return _media(self.programado(a, hoy) for a in self.hojas())

    def avance_capitulo(self, cap: Capitulo, hoy: date) -> tuple[float, float]:
        h = [a for a in self.hojas() if a.capitulo_id == cap.id]
        return _media(self.porcentaje(a) for a in h), _media(self.programado(a, hoy) for a in h)
