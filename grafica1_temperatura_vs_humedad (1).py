"""
Grafica 1 - Scatter: Temperatura vs Humedad Relativa
Dataset: Estaciones Hidrometeorologicas CAM
Fuente: https://www.datos.gov.co/resource/2jrp-f4m5.csv

Instalacion:
    pip install bokeh pandas requests

Ejecucion:
    python grafica1_temperatura_vs_humedad.py
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, ColorBar
from bokeh.transform import linear_cmap
from bokeh.palettes import Turbo256

# --------------------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------------------

URL = "https://www.datos.gov.co/resource/2jrp-f4m5.csv?$limit=2000"

try:
    df = pd.read_csv(URL)
    print(f"Datos descargados: {df.shape[0]} filas, {df.shape[1]} columnas")
except Exception as e:
    print(f"Sin conexion ({e}). Usando datos sinteticos.")
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        "estacion":              np.random.choice(["Est. Norte", "Est. Sur", "Est. Centro", "Est. Oriente", "Est. Occidente"], n),
        "temperatura_(c)":      np.random.normal(18, 5, n),
        "humedad_relativa_(%)": np.random.uniform(40, 98, n),
        "precipitacion_(mm)":   np.abs(np.random.exponential(5, n)),
    })

# --------------------------------------------------------------
# LIMPIEZA
# --------------------------------------------------------------

df.columns = [c.lower().strip() for c in df.columns]

col_temp   = [c for c in df.columns if "temperatura" in c][0]
col_hum    = [c for c in df.columns if "humedad" in c][0]
col_precip = [c for c in df.columns if "precipitacion" in c][0]
col_est    = [c for c in df.columns if "estacion" in c][0] if any("estacion" in c for c in df.columns) else None

for col in [col_temp, col_hum, col_precip]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=[col_temp, col_hum, col_precip])
print(f"Registros validos: {len(df)}")

# --------------------------------------------------------------
# GRAFICA
# --------------------------------------------------------------

source = ColumnDataSource(df)

mapper = linear_cmap(
    field_name=col_precip,
    palette=Turbo256,
    low=float(df[col_precip].min()),
    high=float(df[col_precip].quantile(0.95)),
)

p = figure(
    title="Temperatura vs Humedad Relativa | Color = Precipitacion",
    x_axis_label="Temperatura (C)",
    y_axis_label="Humedad Relativa (%)",
    width=900,
    height=480,
    tools="pan,wheel_zoom,box_zoom,reset,save",
)

p.scatter(
    x=col_temp,
    y=col_hum,
    source=source,
    size=8,
    color=mapper,
    alpha=0.75,
    line_color=None,
)

color_bar = ColorBar(
    color_mapper=mapper["transform"],
    width=14,
    label_standoff=10,
    title="Precip. (mm)",
)
p.add_layout(color_bar, "right")

tooltips = [("Temperatura", f"@{{{col_temp}}}{{0.1f}} C"),
            ("Humedad",     f"@{{{col_hum}}}{{0.1f}} %"),
            ("Precipitacion", f"@{{{col_precip}}}{{0.2f}} mm")]
if col_est:
    tooltips.insert(0, ("Estacion", f"@{col_est}"))

p.add_tools(HoverTool(tooltips=tooltips))

p.title.text_font_size  = "14pt"
p.xaxis.axis_label_text_font_size = "11pt"
p.yaxis.axis_label_text_font_size = "11pt"

# --------------------------------------------------------------
# EXPORTAR
# --------------------------------------------------------------

output_file("grafica1_temperatura_vs_humedad.html", title="Temperatura vs Humedad Relativa")
show(p)
print("Archivo generado: grafica1_temperatura_vs_humedad.html")
