"""Ilustración de la unidad de radiancia (nW/cm²/sr). Correr desde public/slides/img/:
    python make_unidades.py
Dos paneles: (a) qué es un estereorradián; (b) qué mide la radiancia.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon, FancyArrowPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, BLUE, NAVY, AMBER, LIGHT = "#1A2330", "#5B6B7B", "#005BAC", "#003D73", "#F4A100", "#DCE8F5"
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 15, "text.color": INK})

fig, (a, b) = plt.subplots(1, 2, figsize=(13.5, 6.8), gridspec_kw={"wspace": 0.12})
for ax in (a, b):
    ax.set_aspect("equal"); ax.axis("off")

# ---- (a) estereorradián ------------------------------------------------------
R = 1.0
a.add_patch(plt.Circle((0, 0), R, fc="#F4F7FA", ec=MUTED, lw=1.6))
a.add_patch(Ellipse((0, 0), 2 * R, 0.5 * R, fc="none", ec=MUTED, lw=1, ls=(0, (4, 3))))
# casquete: ángulo medio ~33° -> área r² (1 sr) ; se dibuja como elipse sobre la esfera
th = np.radians(32.8)
cx, cy = R * np.cos(np.radians(40)), R * np.sin(np.radians(40))
cap_w, cap_h = 0.62, 0.36
cap = Ellipse((cx, cy), cap_w, cap_h, angle=-50, fc=AMBER, ec="#B87400", lw=1.4, alpha=.95, zorder=4)
a.add_patch(cap)
# cono desde el centro hasta el borde del casquete
ang = np.radians(-50)
u = np.array([np.cos(ang), np.sin(ang)])
p1 = np.array([cx, cy]) + u * cap_w / 2
p2 = np.array([cx, cy]) - u * cap_w / 2
a.add_patch(Polygon([(0, 0), p1, p2], closed=True, fc=AMBER, alpha=.25, ec="#B87400", lw=1.2, zorder=3))
a.plot([0], [0], "o", color=INK, ms=6, zorder=5)
a.text(-0.06, 0.07, "centro", ha="right", va="bottom", fontsize=18, color=MUTED)
# radio
a.annotate("", xy=(-R * 0.72, -R * 0.69), xytext=(0, 0),
           arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.6))
a.text(-0.26, -0.5, "r", fontsize=30, fontstyle="italic", color=NAVY)
a.annotate("área = r²", xy=(cx + 0.12, cy + 0.08), xytext=(1.05, 1.08), fontsize=20, fontweight="bold",
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
a.set_xlim(-1.35, 1.75); a.set_ylim(-1.35, 1.4)
a.set_title("Estereorradián (sr)", loc="left", fontsize=25, fontweight="bold", color=NAVY)
a.text(-1.3, -1.32, "El cono que corta un área r² sobre\nuna esfera de radio r abarca 1 sr.\n"
       "La esfera completa: 4π ≈ 12,6 sr.", fontsize=19, color=INK, va="top")

# ---- (b) radiancia -----------------------------------------------------------
# suelo
b.add_patch(Rectangle((-1.6, -1.25), 3.2, 0.18, fc="#E7ECF1", ec="none"))
b.plot([-1.6, 1.6], [-1.07, -1.07], color=MUTED, lw=1.2)
# parche de 1 cm²
b.add_patch(Polygon([(-0.28, -1.07), (0.28, -1.07), (0.18, -0.99), (-0.38, -0.99)],
                    fc=AMBER, ec="#B87400", lw=1.4, zorder=4))
b.annotate("1 cm² de suelo", xy=(-0.1, -1.04), xytext=(-1.55, -0.72), fontsize=20, fontweight="bold",
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
# cono de luz hacia el satélite
sat = np.array([0.35, 1.05])
b.add_patch(Polygon([(-0.05, -1.0), (0.05, -1.0), sat + [0.26, -0.05], sat + [-0.26, 0.05]], closed=True,
                    fc=AMBER, alpha=.22, ec="#B87400", lw=1.1, ls=(0, (4, 3)), zorder=2))
for dx in (-0.12, 0.0, 0.12):
    b.add_patch(FancyArrowPatch((0.0, -0.95), (sat[0] + dx * 1.6, sat[1] - 0.25),
                                arrowstyle="-|>", mutation_scale=16, color="#D17A00", lw=1.6, zorder=3))
# satélite
body = Rectangle((sat[0] - 0.13, sat[1] - 0.09), 0.26, 0.18, fc=NAVY, ec=NAVY, zorder=5)
b.add_patch(body)
for sgn in (-1, 1):
    b.add_patch(Rectangle((sat[0] + sgn * 0.17 - (0.36 if sgn < 0 else 0), sat[1] - 0.05), 0.36, 0.1,
                          fc=BLUE, ec="white", lw=1, zorder=5))
b.text(sat[0] + 0.62, sat[1] + 0.02, "VIIRS", fontsize=19, fontweight="bold", color=NAVY, va="center")
b.text(0.62, 0.05, "el cono de\ndirecciones\nhacia el sensor\n→ sr", fontsize=19, color=INK)
b.set_xlim(-1.6, 1.7); b.set_ylim(-1.75, 1.4)
b.set_title("Radiancia", loc="left", fontsize=25, fontweight="bold", color=NAVY)
b.text(-1.6, 0.35, "nW: potencia\nde la luz\n(10⁻⁹ vatios)", fontsize=19, color=INK, va="top")
b.text(-1.6, -1.32, "radiancia = potencia / (área × ángulo sólido)\n→ nW/cm²/sr", ha="left",
       va="top", fontsize=19, fontweight="bold", color=NAVY)

fig.savefig(os.path.join(HERE, "unidades_radiancia.png"), dpi=150, bbox_inches="tight", facecolor="white")
print("-> unidades_radiancia.png")
