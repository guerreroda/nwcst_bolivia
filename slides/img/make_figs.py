"""Figuras de las diapositivas. Correr desde public/slides/img/:
    python make_figs.py
Lee los datos del proyecto (../../../data, ../../../raw) y escribe PNG aquí mismo."""
import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BLUE, AMBER, TEAL = "#005BAC", "#D17A00", "#00899C"    # validado: pasa CVD y contraste
INK, MUTED, RULE = "#1A2330", "#5B6B7B", "#E3E8EE"

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


# ---- luces nocturnas: diario vs promedio ------------------------------------
ntl = pd.read_csv(os.path.join(ROOT, "data", "ntl.csv"), index_col="date", parse_dates=True)
ntl = ntl.loc[ntl["ntl_tiles"] == 4, "ntl_mean"]
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.plot(ntl.index, ntl, ".", ms=2, color=BLUE, alpha=.25, label="diario")
ntl_q = ntl.resample("QS").mean()
ax.plot(ntl_q.index + pd.DateOffset(months=1, days=14), ntl_q, color=AMBER, lw=2.2,
        label="promedio trimestral")
ax.set_title("Bolivia: radiancia media diaria de luces nocturnas")
ax.set_ylabel("nW/cm²/sr")
ax.legend(loc="upper left", ncol=2, markerscale=5)
save(fig, "ntl_diario.png")

# ---- luces nocturnas vs PIB, variación interanual ---------------------------
gdp = pd.read_csv(os.path.join(ROOT, "data", "gdp.csv"), index_col="date", parse_dates=True)["gdp"]
nq = ntl_q.copy()
nq.index = nq.index + pd.DateOffset(months=2)
df = pd.concat([gdp.rename("PIB real"), nq.rename("Luces nocturnas")], axis=1).dropna()
yoy = (df.pct_change(4) * 100).dropna()
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.axvspan(pd.Timestamp("2020-02-01"), pd.Timestamp("2021-01-01"), color=RULE, alpha=.7, lw=0)
ax.axhline(0, color=MUTED, lw=.8)
ax.plot(yoy.index, yoy["PIB real"], color=BLUE, lw=2.2, marker="o", ms=5, label="PIB real")
ax.plot(yoy.index, yoy["Luces nocturnas"], color=AMBER, lw=2.2, marker="o", ms=5,
        label="Luces nocturnas")
ax.annotate("2020T2: PIB −25,9 %\nluces +8,4 %", xy=(pd.Timestamp("2020-06-01"), -25.9),
            xytext=(pd.Timestamp("2021-06-01"), -24), color=INK, fontsize=12,
            arrowprops=dict(arrowstyle="-", color=MUTED))
ax.set_title("Variación interanual (%), trimestral")
ax.legend(loc="upper left", ncol=2)
save(fig, "ntl_vs_pib.png")

# ---- Google Trends: tres términos ------------------------------------------
gt = pd.read_csv(os.path.join(ROOT, "raw", "gtrends.csv"), index_col="date", parse_dates=True)
gt = gt.iloc[:-1]                                # último mes: parcial
terms = [("gt_dolar_paralelo", "«dólar paralelo»", BLUE),
         ("gt_gasolina", "«gasolina»", AMBER),
         ("gt_trabajo", "«trabajo»", TEAL)]
terms = [t for t in terms if t[0] in gt.columns]
fig, axes = plt.subplots(1, len(terms), figsize=(12, 3.6), sharey=True)
for ax, (col, lab, c) in zip(axes, terms):
    ax.plot(gt.index, gt[col], color=c, lw=2)
    ax.set_title(lab, fontsize=14)
    ax.set_ylim(0, 105)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
axes[0].set_ylabel("índice 0–100")
fig.suptitle("Google Trends, Bolivia: interés de búsqueda mensual", x=0.01, ha="left",
             fontweight="bold", fontsize=15)
fig.tight_layout()
save(fig, "gt_terminos.png")

# ---- mapa (producido por act3_ntl) -------------------------------------------
src = os.path.join(ROOT, "output", "20260914", "20260914 act3 Fig ntl_map_before_after.png")
if os.path.exists(src):
    shutil.copy(src, os.path.join(HERE, "ntl_mapa.png"))
    print("-> ntl_mapa.png")
