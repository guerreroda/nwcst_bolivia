"""Figuras de la presentación de scraping. Correr desde public/slides/img/:
    python make_scraping_figs.py
Lee la hoja del INE guardada en _ine_T_02.01.xlsx (descargada el 2026-09-30 de
https://www.ine.gob.bo/referencia2017/pib_trimestral.html) y los CSV de ../../../raw.
No hace ninguna consulta a internet."""
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BLUE, AMBER, TEAL = "#005BAC", "#D17A00", "#00899C"
INK, MUTED, RULE, PANEL = "#1A2330", "#5B6B7B", "#E3E8EE", "#F4F7FA"

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 13, "text.color": INK,
    "axes.edgecolor": RULE, "axes.labelcolor": MUTED, "axes.titlesize": 15,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": RULE,
    "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.dpi": 150, "savefig.bbox": "tight",
})


def save(fig, name):
    fig.savefig(os.path.join(HERE, name), facecolor="white")
    plt.close(fig)
    print("->", name)


def col_letter(j):
    s = ""
    j += 1
    while j:
        j, r = divmod(j - 1, 26)
        s = chr(65 + r) + s
    return s


# ---- la hoja cruda, como la ve pd.read_excel(header=None) --------------------
raw = pd.read_excel(os.path.join(HERE, "_ine_T_02.01.xlsx"), header=None)

ROWS = list(range(6, 20)) + [None] + list(range(27, 31))     # None = fila de "…"
COLS = [1, 2, 3, 4, 5, 6, None, 34, 37]                       # None = columna de "…"
W = {1: 5.6}                                                  # ancho de la etiqueta
CW, RH = 1.05, 1.0


def cell_text(i, j):
    v = raw.iat[i, j]
    if pd.isna(v):
        return ""
    if isinstance(v, float):
        return f"{v:,.0f}".replace(",", ".")
    s = str(v)
    s = f"'{s}'" if j > 1 and i == 10 else s           # muestra el espacio final de 'I '
    return s if len(s) <= 40 else s[:38] + "…"


fig, ax = plt.subplots(figsize=(13.5, 7.2))
ax.set_axis_off()
xs, x = [], 0.9
for j in COLS:
    xs.append(x)
    x += W.get(j, CW) if j is not None else 0.5
width = x

# encabezados tipo Excel
for j, x0 in zip(COLS, xs):
    w = W.get(j, CW) if j is not None else 0.5
    ax.add_patch(Rectangle((x0, 0), w, RH, fc=PANEL, ec=RULE))
    ax.text(x0 + w / 2, RH / 2, col_letter(j) if j is not None else "…",
            ha="center", va="center", color=MUTED, fontsize=10)

highlight = {9: AMBER, 10: AMBER, 12: BLUE}                   # filas que se leen
for k, i in enumerate(ROWS, start=1):
    y = (k) * RH
    ax.add_patch(Rectangle((0, y), 0.9, RH, fc=PANEL, ec=RULE))
    ax.text(0.45, y + RH / 2, "" if i is None else str(i + 1), ha="center",
            va="center", color=MUTED, fontsize=10)
    for j, x0 in zip(COLS, xs):
        w = W.get(j, CW) if j is not None else 0.5
        fc = "white"
        if i in highlight and j is not None:
            fc = {AMBER: "#FCEBD0", BLUE: "#DCE9F6"}[highlight[i]]
        ax.add_patch(Rectangle((x0, y), w, RH, fc=fc, ec=RULE, lw=.8))
        if i is None or j is None:
            ax.text(x0 + w / 2, y + RH / 2, "…",
                    ha="center", va="center", color=MUTED, fontsize=10)
            continue
        t = cell_text(i, j)
        bold = i in (9, 12)
        ax.text(x0 + (0.08 if j == 1 else w - 0.08), y + RH / 2, t,
                ha="left" if j == 1 else "right", va="center", fontsize=9.5,
                color=INK, fontweight="bold" if bold else "normal", clip_on=True)

# notas al margen derecho
notes = [
    (6, 9,   MUTED, "título y unidades:\nno son datos"),
    (9, 11,  AMBER, "año en 1 de cada 4 celdas, con «(p)»\ntrimestre en romanos, con espacio"),
    (12, 13, BLUE,  "la serie que buscamos"),
    (15, 16, MUTED, "fila vacía de separación"),
    (27, 31, MUTED, "notas al pie: descartar"),
]


def ypos(i):
    return (ROWS.index(i) + 1) * RH


for i0, i1, c, txt in notes:
    y0 = ypos(i0)
    y1 = ypos(i1 - 1) + RH if (i1 - 1) in ROWS else y0 + RH
    ax.plot([width + .15, width + .15], [y0 + .1, y1 - .1], color=c, lw=3,
            solid_capstyle="butt")
    ax.text(width + .35, (y0 + y1) / 2, txt, va="center", fontsize=11, color=c
            if c != MUTED else INK)

ax.set_xlim(0, width + 4.3)
ax.set_ylim((len(ROWS) + 1) * RH + .1, -.1)
save(fig, "scr_hoja_ine.png")


# ---- comprobación: deflactor implícito ----------------------------------------
real = pd.read_csv(os.path.join(ROOT, "raw", "ine_gdp.csv"), index_col=0, parse_dates=True)["gdp"]
nom = pd.read_csv(os.path.join(ROOT, "raw", "ine_gdp_nominal.csv"), index_col=0,
                  parse_dates=True)["gdp"]
defl = (nom / real * 100).dropna()

fig, ax = plt.subplots(figsize=(11, 4.0))
ax.plot(defl.index, defl, color=BLUE, lw=2.4, marker="o", ms=4)
for d in (defl.index[0], defl.index[-1]):
    ax.annotate(f"{defl[d]:.1f}".replace(".", ","), xy=(d, defl[d]),
                xytext=(0, 10), textcoords="offset points", ha="center",
                fontsize=13, fontweight="bold", color=BLUE)
ax.set_title("Deflactor implícito del PIB = nominal ÷ real × 100")
ax.set_ylim(90, 155)
save(fig, "scr_deflactor.png")
