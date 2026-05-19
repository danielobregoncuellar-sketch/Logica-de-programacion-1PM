"""
Grafica 3 - Serie de Tiempo: Temperatura Media Diaria y Radiacion Solar
Dataset: Estaciones Hidrometeorologicas CAM
Fuente: https://www.datos.gov.co/resource/2jrp-f4m5.csv
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, LinearAxis, Range1d

# --------------------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------------------

URL = "https://www.datos.gov.co/resource/2jrp-f4m5.csv?$limit=2000"

try:
    df = pd.read_csv(URL)
    print(f"Datos descargados: {df.shape[0]} filas, {df.shape[1]} columnas")
except Exception as e:
    print(f"Sin conexion ({e}). Usando datos sinteticos.")
    np.random.seed(99)
    n = 720
    fechas = pd.date_range("2024-01-01", periods=n, freq="3h")
    df = pd.DataFrame({
        "fecha_hora":             fechas,
        "temperatura_(c)":        np.random.normal(18, 4, n) + 3 * np.sin(np.linspace(0, 6 * np.pi, n)),
        "radiacion_solar_(w/m2)": np.abs(np.random.normal(280, 120, n)),})

# --------------------------------------------------------------
# LIMPIEZA
# --------------------------------------------------------------

df.columns = [c.lower().strip() for c in df.columns]

col_fecha = [c for c in df.columns if "fecha" in c][0]
col_temp  = [c for c in df.columns if "temperatura" in c][0]
col_rad   = [c for c in df.columns if "radiacion" in c][0] if any("radiacion" in c for c in df.columns) else None

df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
df[col_temp]  = pd.to_numeric(df[col_temp], errors="coerce")
if col_rad:
    df[col_rad] = pd.to_numeric(df[col_rad], errors="coerce")

df = df.dropna(subset=[col_fecha, col_temp])
print(f"Registros validos: {len(df)}")

# --------------------------------------------------------------
# AGRUPACION DIARIA
# --------------------------------------------------------------

df["fecha"] = df[col_fecha].dt.normalize()

agg_dict = {
    col_temp: ["mean", "max", "min"]}
if col_rad:
    agg_dict[col_rad] = ["mean"]

daily = df.groupby("fecha").agg(agg_dict).reset_index()
daily.columns = ["fecha", "temp_mean", "temp_max", "temp_min"] + (["rad_mean"] if col_rad else [])
daily = daily.sort_values("fecha")

if not col_rad:
    daily["rad_mean"] = np.nan

source = ColumnDataSource(daily)

# --------------------------------------------------------------
# GRAFICA
# --------------------------------------------------------------

p = figure(
    title="Temperatura Media Diaria y Radiacion Solar | Serie de Tiempo",
    x_axis_type="datetime",
    x_axis_label="Fecha",
    y_axis_label="Temperatura (C)",
    width=900,
    height=480,
    tools="pan,wheel_zoom,box_zoom,reset,save",)

rad_max = float(daily["rad_mean"].max()) * 1.15 if daily["rad_mean"].notna().any() else 800
p.extra_y_ranges = {"rad": Range1d(start=0, end=rad_max)}
p.add_layout(
    LinearAxis(
        y_range_name="rad",
        axis_label="Radiacion solar (W/m2)",
        axis_label_text_color="#E65100",
        major_label_text_color="#E65100",),
    "right",)

p.varea(
    x="fecha",
    y1="temp_min",
    y2="temp_max",
    source=source,
    fill_alpha=0.18,
    fill_color="#1565C0",
    legend_label="Rango Temp. (min-max)",)

p.line(
    "fecha", "temp_mean",
    source=source,
    line_width=2.8,
    color="#1565C0",
    legend_label="Temp. media",)

if col_rad:
    p.line(
        "fecha", "rad_mean",
        source=source,
        line_width=1.8,
        color="#E65100",
        alpha=0.75,
        line_dash="dashed",
        y_range_name="rad",
        legend_label="Rad. solar media",)

p.add_tools(HoverTool(
    tooltips=[
        ("Fecha",      "@fecha{%Y-%m-%d}"),
        ("Temp. media","@temp_mean{0.1f} C"),
        ("Temp. max",  "@temp_max{0.1f} C"),
        ("Temp. min",  "@temp_min{0.1f} C"),
        ("Rad. solar", "@rad_mean{0.0f} W/m2"),
    ],
    formatters={"@fecha": "datetime"},
    mode="vline",))

p.legend.location      = "top_left"
p.legend.click_policy  = "hide"
p.legend.label_text_font_size = "10pt"
p.title.text_font_size = "14pt"
p.xaxis.axis_label_text_font_size = "11pt"
p.yaxis.axis_label_text_font_size = "11pt"

output_file("grafica3_serie_temperatura_diaria.html", title="Serie de Tiempo - Temperatura Diaria")
show(p)
print("Archivo generado: grafica3_serie_temperatura_diaria.html")
