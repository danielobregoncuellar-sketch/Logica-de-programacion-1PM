"""
Grafica 2 - Barras: Precipitacion promedio por Departamento
Dataset: Estaciones Hidrometeorologicas CAM
Fuente: https://www.datos.gov.co/resource/2jrp-f4m5.csv
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues8

# --------------------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------------------

URL = "https://www.datos.gov.co/resource/2jrp-f4m5.csv?$limit=2000"

try:
    df = pd.read_csv(URL)
    print(f"Datos descargados: {df.shape[0]} filas, {df.shape[1]} columnas")
except Exception as e:
    print(f"Sin conexion ({e}). Usando datos sinteticos.")
    np.random.seed(7)
    n = 600
    deptos = ["Cundinamarca", "Antioquia", "Valle del Cauca", "Boyaca",
              "Narino", "Cauca", "Huila", "Tolima", "Meta", "Caldas"]
    df = pd.DataFrame({
        "departamento":       np.random.choice(deptos, n),
        "precipitacion_(mm)": np.abs(np.random.exponential(8, n)),})

# --------------------------------------------------------------
# LIMPIEZA
# --------------------------------------------------------------

df.columns = [c.lower().strip() for c in df.columns]

col_precip = [c for c in df.columns if "precipitacion" in c][0]
col_depto  = [c for c in df.columns if "departamento" in c][0]

df[col_precip] = pd.to_numeric(df[col_precip], errors="coerce")
df = df.dropna(subset=[col_precip, col_depto])
print(f"Registros validos: {len(df)}")

# --------------------------------------------------------------
# AGRUPACION
# --------------------------------------------------------------

resumen = (
    df.groupby(col_depto)[col_precip]
    .agg(precip_mean="mean", precip_max="max", n_registros="count")
    .reset_index()
    .rename(columns={col_depto: "departamento"})
    .sort_values("precip_mean", ascending=False)
    .head(10))

deptos_ord = resumen["departamento"].tolist()

palette = list(reversed(Blues8))
palette = (palette * 2)[:len(deptos_ord)]

source = ColumnDataSource(resumen)

# --------------------------------------------------------------
# GRAFICA
# --------------------------------------------------------------

p = figure(
    title="Precipitacion Promedio por Departamento | Top 10",
    x_range=deptos_ord,
    x_axis_label="Departamento",
    y_axis_label="Precipitacion promedio (mm)",
    width=900,
    height=480,
    tools="pan,wheel_zoom,reset,save",)

p.vbar(
    x="departamento",
    top="precip_mean",
    source=source,
    width=0.65,
    color=factor_cmap("departamento", palette=palette, factors=deptos_ord),
    alpha=0.88,
    line_color="white",
    line_width=0.8,)

p.add_tools(HoverTool(tooltips=[
    ("Departamento",     "@departamento"),
    ("Precip. promedio", "@precip_mean{0.2f} mm"),
    ("Precip. maxima",   "@precip_max{0.2f} mm"),
    ("Registros",        "@n_registros"),]))

p.y_range.start = 0
p.xaxis.major_label_orientation = 0.55
p.xgrid.grid_line_color = None
p.title.text_font_size  = "14pt"
p.xaxis.axis_label_text_font_size = "11pt"
p.yaxis.axis_label_text_font_size = "11pt"
