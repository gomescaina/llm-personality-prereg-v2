"""CSIV-64 scoring key (Locke, 2000).

Sources: CSIV Form.pdf (item stems + rating scale), CSIV - Scoring.pdf (SPSS
scoring program: octant item lists, AGENTIC/COMMUNAL vectors, AMP/ELE/R2/ANG,
and University of Idaho undergraduate norms N=1,200).

64 items, 8 items per octant, rated 0..4 (importance). No reverse items.
Octants: PA, BC, DE, FG, HI, JK, LM, NO.
"""
import csv, os, math

_CSV = os.path.join(os.path.dirname(__file__), "csiv_items.csv")

# Octant item lists (from CSIV - Scoring.pdf SPSS program).
OCTANT_ITEMS = {
    "PA": [1, 9, 17, 25, 33, 41, 49, 57],
    "BC": [4, 12, 20, 28, 36, 44, 52, 60],
    "DE": [7, 15, 23, 31, 39, 47, 55, 63],
    "FG": [2, 10, 18, 26, 34, 42, 50, 58],
    "HI": [5, 13, 21, 29, 37, 45, 53, 61],
    "JK": [8, 16, 24, 32, 40, 48, 56, 64],
    "LM": [3, 11, 19, 27, 35, 43, 51, 59],
    "NO": [6, 14, 22, 30, 38, 46, 54, 62],
}

OCTANT_ORDER = ["PA", "BC", "DE", "FG", "HI", "JK", "LM", "NO"]

OCTANT_LABELS = {
    "PA": "Agentic",
    "BC": "Agentic & Uncommunal",
    "DE": "Uncommunal",
    "FG": "Unagentic & Uncommunal",
    "HI": "Unagentic",
    "JK": "Unagentic & Communal",
    "LM": "Communal",
    "NO": "Agentic & Communal",
}

# Octant angular positions (degrees) on the interpersonal circumplex.
OCTANT_ANGLE = {"PA": 90, "BC": 135, "DE": 180, "FG": 225,
                "HI": 270, "JK": 315, "LM": 0, "NO": 45}

# University of Idaho undergraduate norms (N = 1,200).
NORMS = {
    "M": {"PA": 2.53, "BC": 1.38, "DE": 1.10, "FG": 1.66, "HI": 1.77,
          "JK": 2.67, "LM": 2.83, "NO": 2.93},
    "SD": {"PA": 0.63, "BC": 0.71, "DE": 0.70, "FG": 0.78, "HI": 0.75,
           "JK": 0.71, "LM": 0.69, "NO": 0.57},
    "M_AGENTIC": 0.30, "SD_AGENTIC": 0.65,
    "M_COMMUNAL": 1.46, "SD_COMMUNAL": 0.74,
}

ANCHORS_CSIV = {
    0: "not important to me",
    1: "mildly important to me",
    2: "moderately important to me",
    3: "very important to me",
    4: "extremely important to me",
}

# Verbatim master question (CSIV Form.pdf).
INSTRUCTION = (
    "For each item below, answer the following question: \"When I am in "
    "interpersonal situations (such as with close friends, with strangers, at "
    "work, at social gatherings, and so on), in general how important is it to me "
    "that I act or appear or am treated this way?\" Use the following rating "
    "scale: 0 = not important to me, 1 = mildly important to me, 2 = moderately "
    "important to me, 3 = very important to me, 4 = extremely important to me."
)

ITEM_NUM_TO_OCTANT = {n: o for o, nums in OCTANT_ITEMS.items() for n in nums}


def _load_items():
    rows = {}
    with open(_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[int(r["num"])] = {
                "octant": r["octant"],
                "stem": r["stem"],
                "item": r["item"],
            }
    return rows


ITEMS = _load_items()


def octant_score(octant, responses):
    """Mean of the 8 items for an octant (0..4). Returns None if any missing."""
    vals = [responses.get(n) for n in OCTANT_ITEMS[octant]]
    if any(v is None for v in vals):
        return None
    return sum(vals) / 8.0


def circumplex_metrics(octant_means):
    """Given {octant: mean 0..4}, return AGENTIC, COMMUNAL, AMP, ELE, R2, ANG."""
    o = octant_means
    if any(o[k] is None for k in OCTANT_ORDER):
        return None
    PA, BC, DE, FG, HI, JK, LM, NO = (o["PA"], o["BC"], o["DE"], o["FG"],
                                       o["HI"], o["JK"], o["LM"], o["NO"])
    SQ = 0.7071067811865476
    agentic = 0.25 * (PA - HI + SQ * (BC + NO - FG - JK))
    communal = 0.25 * (LM - DE + SQ * (NO + JK - FG - BC))
    amp = math.sqrt(agentic ** 2 + communal ** 2)
    ele = sum(o[k] for k in OCTANT_ORDER) / 8.0
    ss_tot = sum((o[k] - ele) ** 2 for k in OCTANT_ORDER)
    r2 = (4 * amp ** 2 / ss_tot) if ss_tot > 0 else 0.0
    # Angular displacement (degrees), following the SPSS quadrant logic.
    if communal == 0:
        slope = float("inf")
    else:
        slope = agentic / communal
    if agentic > 0 and communal > 0:
        ang = math.degrees(math.atan(slope))
    elif agentic > 0 and communal < 0:
        ang = 180 + math.degrees(math.atan(slope))
    elif agentic < 0 and communal > 0:
        ang = 360 + math.degrees(math.atan(slope))
    elif agentic < 0 and communal < 0:
        ang = 180 + math.degrees(math.atan(slope))
    elif agentic == 0 and communal > 0:
        ang = 0.0
    elif agentic == 0 and communal < 0:
        ang = 180.0
    elif communal == 0 and agentic > 0:
        ang = 90.0
    elif communal == 0 and agentic < 0:
        ang = 270.0
    else:
        ang = 0.0
    ang = ang % 360
    return {"AGENTIC": agentic, "COMMUNAL": communal, "AMP": amp,
            "ELE": ele, "R2": r2, "ANG": ang}
