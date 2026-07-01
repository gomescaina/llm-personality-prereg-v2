"""Scoring for the three instruments.

PID-5: official APA worksheet (16 reverse items, 25 facets, 5 domains via the
3-facet-per-domain worksheet), with the AMPD full 25-facet->5-domain mapping as
an alternative. Proration follows the APA rule: if <=25% of items in a facet are
missing, prorate; if >25% missing the facet is not computable; if any
contributing facet is not computable the domain is not computable. Validity
scales VRIN/ORS/PRD with cutoffs.

IPIP-NEO-300: 148 reverse items via (6 - raw); facet raw = sum of 10 items
(range 10..50); domain raw = sum of six facets (range 60..300).

CSIV-64: octant means (0..4), AGENTIC/COMMUNAL vectors, AMP/ELE/R2/ANG, with
University of Idaho norms for optional z-scores.
"""
from instruments import pid5_key, ipip_key, csiv_key


# ----------------------------- PID-5 ---------------------------------------

def _reverse_pid5(responses):
    out = dict(responses)
    for n in pid5_key.REVERSE_ITEMS:
        if n in out and out[n] is not None:
            out[n] = 3 - out[n]
    return out


def score_pid5_facets(responses):
    """responses: {item_num: 0..3} (raw, pre-reverse).

    Returns {facet: {raw, n_items, n_missing, average_or_None, prorated}}.
    average is on the 0..3 metric.
    """
    rev = _reverse_pid5(responses)
    out = {}
    for facet, items in pid5_key.FACET_ITEMS.items():
        total = len(items)
        present = {n: rev[n] for n in items if n in rev and rev[n] is not None}
        n_ans = len(present)
        n_miss = total - n_ans
        if n_ans == 0:
            out[facet] = {"raw": None, "n_items": total, "n_missing": n_miss,
                          "average": None, "prorated": False, "computable": False}
            continue
        if n_miss == 0:
            raw = sum(present.values())
            out[facet] = {"raw": raw, "n_items": total, "n_missing": 0,
                          "average": raw / total, "prorated": False, "computable": True}
        elif n_miss / total <= 0.25:
            partial = sum(present.values())
            prorated_raw = round(partial * total / n_ans)
            out[facet] = {"raw": prorated_raw, "n_items": total, "n_missing": n_miss,
                          "average": prorated_raw / total, "prorated": True, "computable": True}
        else:
            out[facet] = {"raw": None, "n_items": total, "n_missing": n_miss,
                          "average": None, "prorated": False, "computable": False}
    return out


def score_pid5_domains(facet_scores, mapping="worksheet"):
    """Domain average = mean of the contributing facet averages (0..3 metric).

    mapping: 'worksheet' (3 facets per domain, APA primary) or 'full' (AMPD 25).
    Returns {domain: {average_or_None, facets_used, n_computable}}.
    """
    table = (pid5_key.DOMAIN_FACETS_WORKSHEET if mapping == "worksheet"
             else pid5_key.DOMAIN_FACETS_FULL)
    out = {}
    for domain, facets in table.items():
        avgs = [facet_scores[f]["average"] for f in facets
                if facet_scores.get(f, {}).get("computable")]
        if len(avgs) == len(facets):
            out[domain] = {"average": sum(avgs) / len(facets),
                           "facets_used": facets, "n_computable": len(avgs),
                           "computable": True}
        else:
            out[domain] = {"average": None, "facets_used": facets,
                           "n_computable": len(avgs), "computable": False}
    return out


def score_pid5_validity(responses):
    """VRIN, ORS, PRD with flags. responses are raw (pre-reverse) 0..3.

    VRIN: sum of |raw_a - raw_b| over the 20 pairs (2024 book Table 4-1; the
    book states 'summing the absolute values of the differences between the
    participant's raw answers for each set of paired items'). The 'b' marker in
    Table 4-1 denotes pairs also included in the PID-5-INC-S, NOT reverse-scoring,
    so raw responses are correct for VRIN.

    ORS: recode each ORS item so 1 = 'very true or often true' (rating 3) and
    0 = any other response; ORS = sum. None of the ORS items are in
    REVERSE_ITEMS, so raw responses are used.

    PRD: sum of the 22 PRD item responses (range 0..66). Per Table 4-3 footnote
    'b', items 96 and 98 are reverse-scored, so PRD uses the reverse-scored
    values (rev) for those two and raw for the other 20.
    """
    rev = _reverse_pid5(responses)
    vrin = 0
    for a, b in pid5_key.VRIN_PAIRS:
        va = responses.get(a)
        vb = responses.get(b)
        if va is None or vb is None:
            continue
        vrin += abs(va - vb)
    ors = sum(1 for n in pid5_key.ORS_ITEMS if responses.get(n) == 3)
    prd_vals = [rev.get(n) for n in pid5_key.PRD_ITEMS]
    prd = sum(v for v in prd_vals if v is not None)
    n_prd = sum(1 for v in prd_vals if v is not None)
    flags = {
        "VRIN_inconsistent": vrin >= pid5_key.VRIN_CUTOFF,
        "ORS_overreporting": ors >= pid5_key.ORS_CUTOFF,
        "PRD_underreporting": (n_prd == len(pid5_key.PRD_ITEMS) and
                               prd < pid5_key.PRD_UNDER),
        "PRD_ambiguous": (n_prd == len(pid5_key.PRD_ITEMS) and
                          pid5_key.PRD_UNDER <= prd <= pid5_key.PRD_GENUINE),
    }
    return {"VRIN": vrin, "ORS": ors, "PRD": prd, "PRD_n": n_prd, "flags": flags}


def score_pid5(responses):
    facets = score_pid5_facets(responses)
    domains_ws = score_pid5_domains(facets, "worksheet")
    domains_full = score_pid5_domains(facets, "full")
    validity = score_pid5_validity(responses)
    return {"facets": facets, "domains_worksheet": domains_ws,
            "domains_full": domains_full, "validity": validity}


# --------------------------- IPIP-NEO-300 ----------------------------------

def score_ipip(responses):
    """responses: {item_num: 1..5} raw. Returns facets and domains."""
    rev = {}
    for n, v in responses.items():
        if v is None:
            continue
        rev[n] = (6 - v) if n in ipip_key.REVERSE_ITEMS else v
    facets = {}
    for facet, items in ipip_key.FACET_ITEMS.items():
        vals = [rev.get(n) for n in items if rev.get(n) is not None]
        if len(vals) == len(items):
            facets[facet] = {"raw": sum(vals), "n": len(items),
                             "average": sum(vals) / len(items), "computable": True}
        else:
            facets[facet] = {"raw": None, "n": len(items),
                             "average": None, "computable": False,
                             "n_missing": len(items) - len(vals)}
    domains = {}
    for dom, facets_list in ipip_key.DOMAIN_FACETS.items():
        raws = [facets[f]["raw"] for f in facets_list if facets[f]["computable"]]
        if len(raws) == len(facets_list):
            domains[dom] = {"raw": sum(raws), "n_facets": len(facets_list),
                            "computable": True}
        else:
            domains[dom] = {"raw": None, "n_facets": len(facets_list),
                            "computable": False}
    return {"facets": facets, "domains": domains}


# ------------------------------ CSIV-64 ------------------------------------

def score_csiv(responses):
    """responses: {item_num: 0..4}. Returns octant means + circumplex metrics."""
    octants = {}
    for o in csiv_key.OCTANT_ORDER:
        octants[o] = csiv_key.octant_score(o, responses)
    metrics = csiv_key.circumplex_metrics(octants)
    z = {}
    if metrics and all(octants[k] is not None for k in csiv_key.OCTANT_ORDER):
        z = {f"z{o}": (octants[o] - csiv_key.NORMS["M"][o]) / csiv_key.NORMS["SD"][o]
             for o in csiv_key.OCTANT_ORDER}
        z["zAGENTIC"] = (metrics["AGENTIC"] - csiv_key.NORMS["M_AGENTIC"]) / csiv_key.NORMS["SD_AGENTIC"]
        z["zCOMMUNAL"] = (metrics["COMMUNAL"] - csiv_key.NORMS["M_COMMUNAL"]) / csiv_key.NORMS["SD_COMMUNAL"]
    return {"octants": octants, "metrics": metrics, "z": z}
