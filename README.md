

Aplicación de escritorio para que el **residente** cree la obra, programe actividades y llene el
reporte diario (avances, personal, horas, fotos y novedades), y para que el **gerente** supervise
avance, costos de mano de obra, rendimientos y atrasos.



```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
sudo apt install -y zenity      # necesario en Linux para el selector de fotos
python main.py                  # o:  flet run
```

## Estructura

| Carpeta / archivo | Qué contiene |
|---|---|
| `main.py` | Punto de entrada |
| `obrax/modelos.py` | Dataclasses: `Obra`, `Capitulo`, `Actividad`, `Trabajador`, `Reporte`, `Avance`, `Asistencia`, `Foto` |
| `obrax/calculos.py` | Avance, cronograma, costos, rendimientos (sin Flet; se prueba solo) |
| `obrax/repositorio.py` | SQLite generado a partir de las dataclasses |
| `obrax/informes.py` | Informes diario/semanal/mensual/final en CSV, Excel y PDF |
| `obrax/vistas/` | Una pantalla por archivo |
| `tests/` | Pruebas: `python -m unittest discover -s tests -t .` |
| `datos/` | Se crea al ejecutar: `obrax.db`, `fotos/`, `informes/` |

## Cómo se calcula el costo

- Valor hora = salario × (1 + costo laboral %) ÷ 240.
- Hora extra = valor hora × (1 + recargo %).
- Si un trabajador participa en varias actividades, su costo del día se reparte en partes iguales entre ellas.
- Costo por unidad = costo de mano de obra de la actividad ÷ cantidad ejecutada. Rendimiento = cantidad ÷ horas.

## Compartir con el gerente

La base SQLite es local. Para que el gerente vea los datos desde otro equipo, ejecuta la app en un
servidor con `flet run --web` (o migra `repositorio.py` a PostgreSQL).
