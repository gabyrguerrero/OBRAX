# OBRAx · Gestión y Control de Obra

Aplicación de escritorio hecha con **Flet + Python (dataclasses)**. El **residente** crea la obra,
programa actividades y llena el reporte diario; el **gerente** supervisa avance, costos y atrasos.

## Ejecutar (Ubuntu)

```bash
source venv/bin/activate
pip install -r requirements.txt
sudo apt install -y zenity        # selector de fotos en Linux
python main.py
```

En la primera pantalla elige **Cargar datos de ejemplo** para ver todo funcionando.

## Estructura

| Archivo | Para qué sirve |
|---|---|
| `main.py` | Punto de entrada |
| `router.py` | Barra superior, menú lateral, vista residente/gerente y cambio de pantallas |
| `database/models.py` | Dataclasses: Obra, Capitulo, Actividad, Trabajador, Reporte, Avance, Asistencia, Foto |
| `database/db.py` | SQLite generado a partir de las dataclasses (`datos/obrax.db`) |
| `database/demo.py` | Datos de ejemplo |
| `services/calculos.py` | Avance, cronograma, costos y rendimientos |
| `services/exportar.py` | Informes diario, semanal, mensual y final en PDF, Excel y CSV |
| `views/crear_obra.py` | Obra, capítulos, actividades, subactividades, personal y cierre |
| `views/programacion.py` | Cronograma: programado vs real |
| `views/reporte_diario.py` | Reporte diario: avances, personal, horas, fotos y novedades |
| `views/panel_gerencial.py` | Panel del gerente |
| `views/informes.py` | Informes y bitácora fotográfica |
| `tests/` | `python -m unittest discover -s tests -t .` |

## Costos

- Valor hora = salario × (1 + costo laboral %) ÷ 240.
- Hora extra = valor hora × (1 + recargo %).
- Si un trabajador participa en varias actividades, su costo del día se reparte en partes iguales entre ellas.
- Costo por unidad = costo de mano de obra ÷ cantidad ejecutada. Rendimiento = cantidad ÷ horas.
