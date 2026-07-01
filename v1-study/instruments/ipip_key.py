"""IPIP-NEO-300 scoring key, loaded from the extracted item bank CSV.

The CSV (ipip_neo_300_items.csv) was extracted from
'IPIP-NEO-300 scoring tool_2.xlsx' (Johnson & Twomey), sheet 'Input'.
Columns: num, sign, key, facet, domain, reverse, item.
- 300 items, 148 reverse-keyed (sign starts with '-').
- 30 facets (6 per domain), 5 domains (60 items each).
- Items rated 1..5; reverse scoring via (6 - raw).
- Domain raw = sum of six facets; facet raw = sum of 10 items.
"""
import csv, os

_DOMAINS = ["N", "E", "O", "A", "C"]
_DOMAIN_NAMES = {"N": "Neuroticism", "E": "Extraversion", "O": "Openness",
                 "A": "Agreeableness", "C": "Conscientiousness"}

_CSV = os.path.join(os.path.dirname(__file__), "ipip_neo_300_items.csv")


def _load():
    rows = []
    with open(_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "num": int(r["num"]),
                "key": r["key"].strip(),
                "facet": r["facet"].strip(),
                "domain": r["domain"].strip(),
                "reverse": int(r["reverse"]) == 1,
                "item": r["item"].strip(),
            })
    return rows


ITEMS = _load()
BY_NUM = {r["num"]: r for r in ITEMS}

REVERSE_ITEMS = sorted(r["num"] for r in ITEMS if r["reverse"])

# facet -> list of item numbers (in order)
FACET_ITEMS = {}
for r in ITEMS:
    FACET_ITEMS.setdefault(r["facet"], []).append(r["num"])

# domain -> list of facets (in order)
DOMAIN_FACETS = {d: [] for d in _DOMAINS}
seen = set()
for r in ITEMS:
    f = r["facet"]
    if f not in seen:
        DOMAIN_FACETS[r["domain"]].append(f)
        seen.add(f)

# domain -> list of item numbers
DOMAIN_ITEMS = {d: [] for d in _DOMAINS}
for r in ITEMS:
    DOMAIN_ITEMS[r["domain"]].append(r["num"])

# UK-Ireland normative means/SDs are sheet-specific (three age bands) and not
# embedded here; T-scoring is optional and loaded from the xlsx at analysis time
# if needed. Facet/domain raw scoring does not require norms.

ANCHORS_IPIP = {
    1: "Very Inaccurate",
    2: "Moderately Inaccurate",
    3: "Neither Accurate Nor Inaccurate",
    4: "Moderately Accurate",
    5: "Very Accurate",
}

# Verbatim canonical IPIP-NEO instruction (Goldberg IPIP site / Johnson scoring
# tool wording). This is the administration instruction used in the study.
INSTRUCTION = (
    "The following pages contain phrases describing people's behaviors. Please "
    "use the rating scale next to each phrase to describe how accurately each "
    "statement describes you. Describe yourself as you generally are now, not as "
    "you wish to be in the future. Describe yourself as you honestly see yourself, "
    "in relation to other people you know of the same sex as you are, and roughly "
    "your same age. So that you can describe yourself in an honest manner, your "
    "responses will be kept in absolute confidence. Indicate for each statement "
    "whether it is 1 = Very Inaccurate, 2 = Moderately Inaccurate, 3 = Neither "
    "Accurate Nor Inaccurate, 4 = Moderately Accurate, or 5 = Very Accurate as a "
    "description of you."
)
