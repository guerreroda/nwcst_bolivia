"""
config.py -- every notebook reads its settings from this file.
Edit here, not in the notebooks.
"""

import os
from datetime import date

# ============================================================================
#  CREDENTIALS
# ============================================================================
# NASA token, expires after 60 days. Get one at
# https://ladsweb.modaps.eosdis.nasa.gov -> My Account -> Generate Token
NASA_TOKEN = ""

# FRED API key, free at https://fredaccount.stlouisfed.org/apikeys
FRED_API_KEY = ""

# ============================================================================
#  COUNTRY
# ============================================================================
COUNTRY = "Bolivia"                 # must be a key of COUNTRIES

COUNTRIES = {
    "Bolivia": dict(iso2="BO", iso3="BOL", bbox=(-69.65, -22.91, -57.45, -9.67),
                    tiles=["h11v09", "h11v10", "h12v10", "h11v11", "h12v11"]),
}

if COUNTRY not in COUNTRIES:
    raise KeyError(f"{COUNTRY!r} is not in COUNTRIES. Known: {sorted(COUNTRIES)}")

_C = COUNTRIES[COUNTRY]
CODE      = _C["iso2"]              # "BO"
CODE_LC   = CODE.lower()            # "bo"
GADM_ISO3 = _C["iso3"]              # "BOL"
BBOX      = _C["bbox"]              # (lon_min, lat_min, lon_max, lat_max)

# ---- Night-time light tiles (VIIRS Black Marble) ---------------------------
TILES = list(_C["tiles"])
TILES_OVERRIDE = ["h11v09", "h11v10", "h12v10", "h11v11"]   # None = use TILES
if TILES_OVERRIDE:                                           # (h12v11 is 0.02% of Bolivia)
    TILES = list(TILES_OVERRIDE)
DOWNLOAD_TILES = None               # subset of TILES to download; None = all

# ---- File names ------------------------------------------------------------
GDP_TICKER       = "RGDP0000"
CPI_TICKER       = "MCPI0000"
CPI_BASE_YEAR    = 2016
COORDINATES_XLSX = "Coordinates.xlsx"   # NTL sites (lat/lon), in raw/
NTL_OUTPUT_CSV   = "ntl_data.csv"       # daily NTL per site, in raw/
NTL_SHAPE_CSV    = "ntl_shape.csv"      # daily NTL, country mean, in raw/
DATA_CSV         = "data.csv"
METADATA_CSV     = "meta.csv"

# ============================================================================
#  NIGHT-TIME LIGHTS (act3_ntl)
# ============================================================================
# Window to download and analyse. About 4 files (~100 MB) per day.
#   "2026-01-01 2026-01-09"  -> from - to
#   "2026-01-01"             -> from that date to the latest available
#   None                     -> from NTL_FIRST_DATE to the latest available
NTL_DATE_RANGE = "2026-01-01 2026-01-09"

# Safety limits, applied even when NTL_DATE_RANGE is None.
NTL_FIRST_DATE = "2016-11-01"       # never download anything earlier
NTL_MAX_FILES  = 4000               # refuse a run above this (~100 GB); None = no limit

# Event marked on the series and centred in the before/after maps.
NTL_EVENT_DATE   = "2026-01-04"     # e.g. "2026-01-20"; None = first/last day of the window
NTL_EVENT_LABEL  = "Ejemplo"        # e.g. "paro de combustible"
NTL_EVENT_WINDOW = 2                # days before/after the event shown on the maps

NTL_DRAW_MAPS = True                # False = skip the maps (they re-open the .h5 tiles)


def ntl_window():
    """(start, end) of the NTL window as datetimes; end None = latest available."""
    from datetime import datetime

    floor = datetime.strptime(NTL_FIRST_DATE, "%Y-%m-%d") if NTL_FIRST_DATE else None
    if not NTL_DATE_RANGE:
        return floor, None

    parts = NTL_DATE_RANGE.split()
    if len(parts) == 1:
        start, end = datetime.strptime(parts[0], "%Y-%m-%d"), None
    elif len(parts) == 2:
        start = datetime.strptime(parts[0], "%Y-%m-%d")
        end   = datetime.strptime(parts[1], "%Y-%m-%d")
    else:
        raise ValueError("NTL_DATE_RANGE must be None, one date, or two dates "
                         "separated by a space; got %r" % (NTL_DATE_RANGE,))

    if floor and start < floor:
        start = floor
    return start, end

# ============================================================================
#  NOWCAST
# ============================================================================
DESIRED_DATE = "2026-06-01"                      # quarter to nowcast (last month of the quarter)
DATE_STR     = date.today().strftime("%Y%m%d")   # results go to output/<DATE_STR>/

TRAIN_START  = "2015-03-01"         # training sample start
TEST_START   = "2023-06-01"         # test sample start
LAGS         = list(range(-2, 3))   # vintages -2..+2 (backcast .. forecast)
LARS_FACTORS = 1                    # PCA components in the LARS benchmark

SEASONAL_FILTER = 0                 # 0 = classical (fast), 1 = X-13ARIMA-SEATS (slow)
X13_PATH        = None              # folder with x13as; None = look on PATH

RUN = {                             # models to fit: 1 = on, 0 = off
    "ols": 1, "olsr": 1, "enet": 1, "lasso": 1,
    "gbt": 1, "dt": 1, "rf": 1, "lstm": 1,
}

ITER       = 10                     # ensemble size for DT / RF / GBT (production: 100)
ITER_LSTM  = 10                     # LSTM ensemble size
EPOCH_LSTM = 50                     # LSTM training epochs

# ---- Advanced options: all off for a plain nowcast -------------------------
SCALE_LINEAR     = 1                # scale predictors for Ridge / ENET / LASSO (keep on)
SHOCK_FEATURES   = 0
ROLLING_LARS     = 0
SELECTION_CV     = 0
REGIME_ENSEMBLE  = 0
WATCHLIST        = 0
DISPERSION_BANDS = 0

SAMPLE_WEIGHT_DECAY = None
NWCST_SEED          = 42
NWCST_FILL          = "mean"        # ragged-edge fill: "mean" or "ffill"
RIDGE_ALPHAS        = [0.1, 1, 10, 50, 100]
MAX_WORKERS         = None          # None = based on the number of CPUs

SHOCK_WINSOR_Z   = 3.0
SHOCK_BREAK_Z    = -3.0
SHOCK_MIN_BROKEN = 4

ROLLING_MAX_VARS = 99
CV_MIN_TRAIN     = 16
CV_STEP          = 2
CV_EVAL_SIZE     = 4
LARS_SIZE_RANGE  = (10, 50)

SHOCK_DATES       = []
LOO_SHOCK_DATES   = []
SHOCK_TARGET_DATE = None

ORACLE_KS              = []
ORACLE_ESTIMATORS      = ["ENET", "LASSO"]
ORACLE_VINTAGE         = 1
ORACLE_KS_TREE         = []
ORACLE_TREE_ESTIMATORS = ["DT", "RF", "GBT"]
ORACLE_TREE_VINTAGE    = 2

# ============================================================================
#  PATHS AND HELPERS -- normally no need to edit below
# ============================================================================
GADM_ZIP     = "gadm41_" + GADM_ISO3 + "_shp.zip"
PROJECT_ROOT = ".."                 # project root, relative to this file
NL_ROOT      = None                 # folder with the .h5 tiles; None = <root>/hfiles


def tiles_from_bbox(bbox=None):
    """VIIRS tiles touched by a bounding box (first guess for a new country)."""
    import math
    lo, la, hi, ha = bbox or BBOX
    h0, h1 = math.floor((lo + 180) / 10), math.floor((hi + 180) / 10)
    v0, v1 = math.floor((90 - ha) / 10), math.floor((90 - la) / 10)
    return [f"h{h:02d}v{v:02d}" for v in range(v0, v1 + 1) for h in range(h0, h1 + 1)]


def refresh_registry(shape_dir=None, countries=None):
    """Recompute bbox + tiles from the GADM border; prints lines for COUNTRIES.

        conda run -n geo python -c "import config; config.refresh_registry()"
    """
    import urllib.request
    import geopandas as gpd
    from shapely.geometry import box

    shape_dir = shape_dir or os.path.join(os.getcwd(), "shapes")
    os.makedirs(shape_dir, exist_ok=True)
    out = {}
    for name in (countries or COUNTRIES):
        iso3 = COUNTRIES[name]["iso3"]
        zp = os.path.join(shape_dir, f"gadm41_{iso3}_shp.zip")
        if not os.path.exists(zp):
            urllib.request.urlretrieve(
                f"https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{iso3}_shp.zip", zp)
        g = gpd.read_file(f"zip://{zp}!gadm41_{iso3}_0.shp")
        geom = g.geometry.union_all() if hasattr(g.geometry, "union_all") else g.geometry.unary_union
        b = geom.bounds
        cand = tiles_from_bbox(b)
        exact = [t for t in cand
                 if geom.intersects(box(10 * int(t[1:3]) - 180,
                                        90 - 10 * int(t[4:6]) - 10,
                                        10 * int(t[1:3]) - 170,
                                        90 - 10 * int(t[4:6])))]
        out[name] = (b, exact)
        drop = set(cand) - set(exact)
        print(f'    {name!r:24}: dict(iso2="{COUNTRIES[name]["iso2"]}", iso3="{iso3}", '
              f'bbox=({b[0]:.2f}, {b[1]:.2f}, {b[2]:.2f}, {b[3]:.2f}),')
        print(f'{"":30}tiles={exact}),'
              + (f'   # bbox rule also suggested {sorted(drop)} -- not touched' if drop else ""))
    return out


def download_tiles():
    """Tiles to download: DOWNLOAD_TILES if set, else TILES."""
    return list(DOWNLOAD_TILES) if DOWNLOAD_TILES else list(TILES)


def derive_paths(d, make=True):
    """Project folders, given d = the folder holding this file. Creates missing ones."""
    d = os.path.abspath(d)
    root = os.path.abspath(os.path.join(d, PROJECT_ROOT))
    up = lambda *p: os.path.join(root, *p)
    P = {
        "code":    d,
        "raw":     up("raw"),
        "data":    up("data"),
        "output":  up("output"),
        "ntl_tmp": up("ntl_tmp"),
        "nl_root": os.path.abspath(os.path.join(d, NL_ROOT)) if NL_ROOT else up("hfiles"),
    }
    if make:
        for k, p in P.items():
            if k != "code":
                os.makedirs(p, exist_ok=True)
    return P
