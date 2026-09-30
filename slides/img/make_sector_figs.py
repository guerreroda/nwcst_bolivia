"""Figuras por sector para las diapositivas de luces nocturnas. Correr desde public/slides/img/:
    python make_sector_figs.py

ntl_sitios_mapa.png    mapa de Bolivia con las 90 ubicaciones de raw/Coordinates.xlsx
ntl_sectores_pib.png   variación interanual por sector vs PIB, y su correlación

Serie por sector: por cada sitio, mediana MENSUAL de DNBvalue3 (media 3x3 píxeles;
la mediana resiste noches nubladas o con incendios), promedio entre los sitios del
sector, promedio trimestral, fechado como el PIB (primer día del último mes).
"""
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NE = r"C:/Users/guerr/anaconda3/Lib/site-packages/geopandas/datasets/naturalearth_lowres/naturalearth_lowres.shp"  # viene con geopandas <1.0
INK, MUTED, RULE, BLUE = "#1A2330", "#5B6B7B", "#E3E8EE", "#005BAC"

# Paleta categórica de referencia (validada: CVD y visión normal). Orden fijo.
# Aeropuertos en naranja: el sector que se destaca.
SECTORS = [  # (clave en los datos, etiqueta, color, marcador)
    ("Oil & Gas",            "Petróleo y gas",          "#2a78d6", "s"),
    ("Airport",              "Aeropuertos",             "#eb6834", "o"),
    ("Mining",               "Minería",                 "#1baf7a", "^"),
    ("Hotel",                "Hoteles",                 "#eda100", "D"),
    ("Shopping Mall",        "Centros comerciales",     "#e87ba4", "v"),
    ("Industrial/Free Zone", "Industria / zona franca", "#008300", "P"),
]
LAB = {k: l for k, l, _, _ in SECTORS}

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 13, "text.color": INK,
    "axes.edgecolor": RULE, "axes.labelcolor": MUTED, "axes.titlesize": 15,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": RULE,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "figure.dpi": 150, "savefig.bbox": "tight",
})


def corr(a, b):
    """Pearson a mano (numpy.corrcoef falla en algunas consolas sin conda activado)."""
    x = pd.concat([a, b], axis=1).dropna()
    u, w = x.iloc[:, 0] - x.iloc[:, 0].mean(), x.iloc[:, 1] - x.iloc[:, 1].mean()
    return float((u * w).sum() / ((u ** 2).sum() * (w ** 2).sum()) ** 0.5)


# ---- 1. mapa de ubicaciones ---------------------------------------------------
coords = pd.read_excel(os.path.join(ROOT, "raw", "Coordinates.xlsx"))
bol = gpd.read_file(NE)
bol = bol[bol["name"] == "Bolivia"]
fig, ax = plt.subplots(figsize=(8.2, 9.4))
bol.plot(ax=ax, color="#F4F7FA", edgecolor="#9AA8B6", linewidth=1)
for key, lab, col, mk in SECTORS:
    s = coords[coords["sector"] == key]
    big = key == "Airport"
    ax.scatter(s["lon"], s["lat"], s=190 if big else 80, c=col, marker=mk,
               edgecolors="white", linewidths=1.2, zorder=4 if big else 3,
               label=f"{lab} ({len(s)})")
callouts = {  # aeropuertos que se nombran en la diapositiva
    "El Alto International Airport (LPB)":         ("El Alto (LPB)",     (-0.25, 0.9)),
    "Viru Viru International Airport (VVI)":       ("Viru Viru (VVI)",   (0.35, 0.8)),
    "Jorge Wilstermann International Airport (CBB)": ("Cochabamba (CBB)", (-2.6, -0.9)),
}
for loc, (txt, (dx, dy)) in callouts.items():
    r = coords[coords["location"] == loc].iloc[0]
    ax.annotate(txt, (r["lon"], r["lat"]), xytext=(r["lon"] + dx, r["lat"] + dy),
                fontsize=17, fontweight="bold", color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
ax.set_axis_off()
ax.legend(loc="upper center", fontsize=16, handletextpad=0.4, borderaxespad=0, ncol=2,
          bbox_to_anchor=(0.5, -0.01), columnspacing=1.2, labelspacing=0.7)
fig.savefig(os.path.join(HERE, "ntl_sitios_mapa.png"), facecolor="white")
plt.close(fig)
print("-> ntl_sitios_mapa.png")

# ---- 2. series por sector vs PIB ---------------------------------------------------
d = pd.read_csv(os.path.join(ROOT, "raw", "ntl_data.csv"), parse_dates=["date"])
v = "DNBvalue3"
d = d[(d[v] >= 0) & (d[v] < 1000)]                     # valores de relleno y picos absurdos
m = (d.set_index("date").groupby(["sector", "location"])[v].resample("MS").median()
       .reset_index())
sec = m.groupby(["sector", "date"])[v].mean().unstack(0)
q = sec.resample("QS").mean()
q.index = q.index + pd.DateOffset(months=2)
gdp = pd.read_csv(os.path.join(ROOT, "data", "gdp.csv"), index_col="date", parse_dates=True)["gdp"]
nat = pd.read_csv(os.path.join(ROOT, "data", "ntl.csv"), index_col="date", parse_dates=True)
# mismo método que la diapositiva anterior (promedio trimestral de los días completos)
nat = nat[nat["ntl_tiles"] == 4]["ntl_mean"].resample("QS").mean()
nat.index = nat.index + pd.DateOffset(months=2)
df = q.join(gdp, how="inner").join(nat.rename("nacional"), how="left")
yoy = (df.pct_change(4) * 100).loc["2018":]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.75, 1]})
a1.axvspan(pd.Timestamp("2020-02-01"), pd.Timestamp("2021-01-01"), color=RULE, alpha=.7, lw=0)
a1.axhline(0, color=MUTED, lw=.8)
for key, lab, col, _ in SECTORS:
    if key != "Airport":
        a1.plot(yoy.index, yoy[key], color="#C5CDD6", lw=1.2, zorder=2)
a1.plot([], [], color="#C5CDD6", lw=1.2, label="otros sectores")
a1.plot(yoy.index, yoy["gdp"], color=BLUE, lw=2.4, marker="o", ms=4, label="PIB real", zorder=4)
a1.plot(yoy.index, yoy["Airport"], color="#eb6834", lw=2.4, marker="o", ms=4,
        label="Aeropuertos", zorder=5)
a1.set_ylim(-40, 60)
a1.set_title("Variación interanual (%)")
a1.legend(loc="upper left", ncol=3, fontsize=11)

rows = [(LAB[k], corr(yoy[k], yoy["gdp"]), c if k == "Airport" else "#C5CDD6") for k, _, c, _ in SECTORS]
rows.append(("Nacional (polígono)", corr(yoy["nacional"], yoy["gdp"]), "#8A9AAB"))
rows.sort(key=lambda r: r[1])
a2.barh([r[0] for r in rows], [r[1] for r in rows], color=[r[2] for r in rows], height=.62)
a2.axvline(0, color=MUTED, lw=.8)
for i, (_, val, _) in enumerate(rows):
    a2.text(val + (0.02 if val >= 0 else -0.02), i, f"{val:+.2f}".replace(".", ","),
            va="center", ha="left" if val >= 0 else "right", fontsize=11, color=INK)
a2.set_xlim(-0.6, 0.6)
a2.set_axisbelow(True)
a2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}".replace(".", ",").replace("-", "−")))
a2.grid(axis="y", visible=False)
a2.set_title("Correlación con el PIB")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "ntl_sectores_pib.png"), facecolor="white")
plt.close(fig)
print("-> ntl_sectores_pib.png")
print((yoy.loc["2020-06-01", ["gdp", "Airport", "nacional"]]).round(1).to_string())
print({r[0]: round(r[1], 2) for r in rows})
