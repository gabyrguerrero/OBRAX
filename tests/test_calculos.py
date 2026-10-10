import unittest
from datetime import date

from services.calculos import Control, Estado
from database.models import Actividad, Asistencia, Avance, Capitulo, Obra, Reporte, Trabajador
from database.db import Repositorio


class PruebasCalculos(unittest.TestCase):
    def setUp(self):
        self.hoy = date(2026, 3, 10)
        self.obra = Obra("Casa", inicio=date(2026, 3, 1), fin=date(2026, 3, 31), recargo_extra=25)
        self.cap = Capitulo(self.obra.id, "Cimientos")
        self.a1 = Actividad(self.obra.id, self.cap.id, "Excavación", "m³", 100, date(2026, 3, 1), date(2026, 3, 5))
        self.a2 = Actividad(self.obra.id, self.cap.id, "Relleno", "m³", 50, date(2026, 3, 6), date(2026, 3, 20))
        self.t = Trabajador(self.obra.id, "Ana", "Oficial", 2_400_000, 50)  # hora = 15.000
        r = Reporte(self.obra.id, date(2026, 3, 4))
        r.avances = [Avance(self.a1.id, 50)]
        r.asistencias = [Asistencia(self.t.id, 8, 2, [self.a1.id, self.a2.id])]
        self.c = Control(self.obra, [self.cap], [self.a1, self.a2], [self.t], [r])

    def test_valor_hora(self):
        self.assertAlmostEqual(self.t.valor_hora, 15_000)

    def test_costo_se_reparte_sin_duplicar(self):
        total = 15_000 * (8 + 2 * 1.25)  # 157.500
        self.assertAlmostEqual(self.c.costo_total, total)
        self.assertAlmostEqual(self.c.acum[self.a1.id].costo, total / 2)
        self.assertAlmostEqual(self.c.acum[self.a1.id].costo + self.c.acum[self.a2.id].costo, total)

    def test_avance_y_estado(self):
        self.assertAlmostEqual(self.c.porcentaje(self.a1), 50)
        self.assertEqual(self.c.estado(self.a1, self.hoy), Estado.ATRASADA)  # ya pasó su fecha fin
        self.assertEqual(self.c.estado(self.a2, self.hoy), Estado.ATRASADA)  # 33 % programado y 0 % real
        self.assertEqual(self.c.estado(self.a2, date(2026, 3, 6)), Estado.EN_CURSO)
        self.assertEqual(self.c.estado(self.a2, date(2026, 3, 1)), Estado.PENDIENTE)

    def test_costo_unitario_y_rendimiento(self):
        x = self.c.acum[self.a1.id]
        self.assertAlmostEqual(x.costo_unitario, 78_750 / 50)
        self.assertAlmostEqual(x.rendimiento, 50 / 5)  # 10 h repartidas en 2 actividades

    def test_repositorio_guarda_y_lee(self):
        repo = Repositorio(":memory:")
        for obj in (self.obra, self.cap, self.a1, self.a2, self.t):
            repo.guardar(obj)
        repo.guardar_reporte(self.c.reportes[0])
        self.assertEqual(repo.listar(Actividad, obra_id=self.obra.id)[0], self.a1)
        self.assertEqual(repo.listar(Trabajador)[0], self.t)
        self.assertEqual(repo.listar_reportes(self.obra.id)[0], self.c.reportes[0])
        repo.eliminar_capitulo(self.cap.id)
        self.assertEqual(repo.listar(Actividad), [])


if __name__ == "__main__":
    unittest.main()
