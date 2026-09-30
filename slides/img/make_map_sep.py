"""Mapa comparable de luces nocturnas: septiembre 2012 vs septiembre 2025.

Correr con el python del entorno geo (h5py, rasterio, geopandas):
    <anaconda3>/envs/geo/python.exe make_map_sep.py

Por qué no una sola noche: una noche mezcla actividad con nubes (la capa gap-filled
rellena lo nublado con valores viejos), luna y resplandor del cielo. Aquí, para cada
año, se eligen las N noches de septiembre con más píxeles de buena calidad, se toma
la capa SIN relleno (DNB_BRDF-Corrected_NTL) sólo donde Mandatory_Quality_Flag == 0,
y se hace la mediana por píxel. La escala es logarítmica con piso en 0,5 nW, de modo
que el fondo (0-0,3 nW, que varía con la luna y el año) queda negro en ambos mapas.
"""
import os, datetime as dt
import numpy as np, h5py
import geopandas as gpd
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HF = os.path.join(ROOT, "hfiles")
NE = r"C:/Users/guerr/anaconda3/Lib/site-packages/geopandas/datasets/naturalearth_lowres/naturalearth_lowres.shp"
YEARS, N_NIGHTS, STEP = (2012, 2025), 5, 3
TILES = {"h11v09": (-70, 0), "h11v10": (-70, -10), "h11v11": (-70, -20), "h12v10": (-60, -10)}  # (west, north)
PX = 2400                        # pixels per 10-degree tile
F = "HDFEOS/GRIDS/VIIRS_Grid_DNB_2d/Data Fields"


def tile_file(tile, d):
    doy = d.timetuple().tm_yday
    pre = f"VNP46A2.A{d.year}{doy:03d}.{tile}."
    hits = [f for f in os.listdir(os.path.join(HF, tile)) if f.startswith(pre)]
    return os.path.join(HF, tile, hits[0]) if hits else None


def read(path):
    with h5py.File(path, "r") as h:
        g = h[F]
        q = g["Mandatory_Quality_Flag"][()]
        a = g["DNB_BRDF-Corrected_NTL"][()].astype("float32")
        fv = float(np.ravel(g["DNB_BRDF-Corrected_NTL"].attrs.get("_FillValue", [-999.9]))[0])
        sf = float(np.ravel(g["DNB_BRDF-Corrected_NTL"].attrs.get("scale_factor", [1]))[0])
    a[a == fv] = np.nan
    a *= sf
    a[q != 0] = np.nan           # sólo retrievals de alta calidad
    return a, float((q == 0).mean())


bol = gpd.read_file(NE)
bol = bol[bol["name"] == "Bolivia"].to_crs(4326)
west, south, east, north = bol.total_bounds
res = 10 / PX
CACHE = os.path.join(HERE, "_map_sep_cache.npz")      # compuestos ya calculados
if os.path.exists(CACHE):
    z = np.load(CACHE)
    comp = {y: (z[f"sub{y}"], int(z[f"n{y}"])) for y in YEARS}
    outside_mask = {y: z[f"out{y}"] for y in YEARS}
    c1, c2, r1, r2 = (int(z[k]) for k in ("c1", "c2", "r1", "r2"))
    print("compuestos leídos de", os.path.basename(CACHE), "(borrar para recalcular)")
else:
    comp, outside_mask = {}, {}
    for y in YEARS:
        days = [dt.date(y, 9, 1) + dt.timedelta(k) for k in range(0, 30, STEP)]
        clear = []
        for d in days:                                   # rank candidates on the core tile
            p = tile_file("h11v10", d)
            if p:
                clear.append((read(p)[1], d))
        best = sorted(clear, reverse=True)[:N_NIGHTS]
        nights = sorted(d for _, d in best)
        print(y, "noches:", [str(d) for d in nights], "calidad:", [f"{c:.0%}" for c, _ in sorted(best, key=lambda t: t[1])])
        # mosaic -70..-50 lon, 0..-30 lat
        mos = np.full((3 * PX, 2 * PX), np.nan, dtype="float32")
        for t, (w, n) in TILES.items():
            stack = [read(tile_file(t, d))[0] for d in nights if tile_file(t, d)]
            med = np.nanmedian(np.stack(stack), axis=0)
            r0, c0 = int((0 - n) / 10 * PX), int((w + 70) / 10 * PX)
            mos[r0:r0 + PX, c0:c0 + PX] = med
        # crop to Bolivia's bbox and mask outside the border
        r1, r2 = int((0 - north) / res), int((0 - south) / res) + 1
        c1, c2 = int((west + 70) / res), int((east + 70) / res) + 1
        sub = mos[r1:r2, c1:c2]
        tr = from_origin(-70 + c1 * res, 0 - r1 * res, res, res)
        outside = geometry_mask(bol.geometry, out_shape=sub.shape, transform=tr)
        sub = np.where(outside, np.nan, sub)
        comp[y] = (sub, len(nights))
        outside_mask[y] = outside
        lit = np.nansum(sub > 0.5 * 1.0) / np.isfinite(sub).sum()
        print(f"   píxeles >0,5 nW: {lit:.2%}   >5 nW: {np.nansum(sub > 5) / np.isfinite(sub).sum():.2%}")

    np.savez_compressed(CACHE, c1=c1, c2=c2, r1=r1, r2=r2,
                        **{f"sub{y}": comp[y][0] for y in YEARS},
                        **{f"n{y}": comp[y][1] for y in YEARS},
                        **{f"out{y}": outside_mask[y] for y in YEARS})

extent = (-70 + c1 * res, -70 + c2 * res, 0 - r2 * res, 0 - r1 * res)

# ---- dibujo -------------------------------------------------------------------
# Un píxel VIIRS mide ~460 m: Bolivia son ~3.000 x 3.200 píxeles y el mapa se ve
# a ~600 px. Reducir tomando 1 de cada k píxeles borra casi todas las luces (son
# puntos aislados), así que se reduce por el MÁXIMO de cada bloque k x k.
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
NOCHE, SINDATO, ROJO = "#143A68", "#7A8896", "#E0242F"     # fondo azul marino, no negro
cmap = LinearSegmentedColormap.from_list(
    "noche", [NOCHE, "#2A63A6", "#F4A100", "#FFE7A3", "#FFFFFF"])
cmap.set_under(NOCHE)
norm = LogNorm(vmin=0.6, vmax=30)     # piso sobre el brillo del cielo (0,3-0,5 nW en 2025)
ZOOM = (-68.6, -62.6, -18.6, -16.2)          # eje La Paz - Cochabamba - Santa Cruz
SCZ = (-63.45, -62.9, -18.05, -17.5)         # caja de Santa Cruz para la luz nueva
URB = 5.0                                    # nW: umbral de luz urbana


def pool_max(a, k):
    h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    b = a[:h, :w].reshape(h // k, k, w // k, k)
    with np.errstate(all="ignore"):
        return np.nanmax(np.nanmax(b, axis=3), axis=1)


def draw(ax, sub, out, k, ext, window=None):
    img = sub
    ins = ~out
    if window is not None:                   # recorte en coordenadas
        x0, x1, y0, y1 = window
        cc = slice(int((x0 - ext[0]) / res), int((x1 - ext[0]) / res))
        rr = slice(int((ext[3] - y1) / res), int((ext[3] - y0) / res))
        img, ins, ext = img[rr, cc], ins[rr, cc], (x0, x1, y0, y1)
    if k > 1:
        img = pool_max(np.where(np.isnan(img), -1, img), k)
        img = np.where(img < 0, np.nan, img)
        ins = pool_max(ins.astype(float), k) > 0
    nodata = ins & np.isnan(img)
    ax.set_facecolor("white")
    ax.imshow(np.where(ins, 0.0, np.nan), extent=ext, cmap=LinearSegmentedColormap.from_list("f", [NOCHE, NOCHE]),
              interpolation="nearest")
    ax.imshow(np.where(nodata, 1.0, np.nan), extent=ext,
              cmap=LinearSegmentedColormap.from_list("g", [SINDATO, SINDATO]), interpolation="nearest")
    im = ax.imshow(np.where(ins, img, np.nan), extent=ext, cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_axis_off()
    return im


fig = plt.figure(figsize=(13, 9.2), facecolor="white")
gs = fig.add_gridspec(2, 2, height_ratios=[3.05, 1], hspace=0.14, wspace=0.04)
for col, y in enumerate(YEARS):
    sub, n = comp[y]
    out = outside_mask[y]
    a = fig.add_subplot(gs[0, col])
    im = draw(a, sub, out, 4, extent)
    bol.boundary.plot(ax=a, color="#9CC7EC", linewidth=0.7)
    a.add_patch(Rectangle((ZOOM[0], ZOOM[2]), ZOOM[1] - ZOOM[0], ZOOM[3] - ZOOM[2],
                          fill=False, ec="white", lw=1.1, ls="--"))
    a.set_title(f"Septiembre {y}", loc="left", fontsize=20, fontweight="bold", color="#1A2330")
    z = fig.add_subplot(gs[1, col])
    draw(z, sub, out, 1, extent, window=ZOOM)
    z.set_title("Acercamiento: La Paz – Cochabamba – Santa Cruz", loc="left", fontsize=12,
                color="#5B6B7B", pad=4)
    if y == YEARS[-1]:
        # luz urbana nueva en Santa Cruz: > URB nW en 2025 y no en 2012
        old, new = comp[YEARS[0]][0], sub
        with np.errstate(invalid="ignore"):
            nueva = (new > URB) & ~(old > URB)
        cc = np.arange(sub.shape[1]) * res + extent[0]
        rr = extent[3] - np.arange(sub.shape[0]) * res
        caja = ((cc >= SCZ[0]) & (cc <= SCZ[1]))[None, :] & ((rr >= SCZ[2]) & (rr <= SCZ[3]))[:, None]
        nueva &= caja
        x0, x1, y0, y1 = ZOOM
        cz = slice(int((x0 - extent[0]) / res), int((x1 - extent[0]) / res))
        rz = slice(int((extent[3] - y1) / res), int((extent[3] - y0) / res))
        z.imshow(np.where(nueva[rz, cz], 1.0, np.nan), extent=ZOOM,
                 cmap=LinearSegmentedColormap.from_list("r", [ROJO, ROJO]), interpolation="nearest")
        z.text(1.0, -0.04, "■ luz urbana nueva en Santa Cruz (2012 → 2025)", transform=z.transAxes,
               ha="right", va="top", fontsize=13, fontweight="bold", color=ROJO)
cb = fig.colorbar(im, ax=fig.axes, orientation="horizontal", fraction=0.03, pad=0.06,
                  extend="both", aspect=45)
cb.set_ticks([0.6, 1, 3, 10, 30]); cb.set_ticklabels(["0,6", "1", "3", "10", "30"])
cb.set_label("radiancia, nW/cm²/sr (escala logarítmica) · gris: sin dato de buena calidad",
             color="#5B6B7B", fontsize=11)
cb.outline.set_visible(False)
out_png = os.path.join(HERE, "ntl_mapa_sep.png")
fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="white")
print("->", out_png)
