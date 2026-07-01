"""Official PID-5 Adult scoring key (APA, 2013; Krueger et al.).

Source: APA DSM-5-TR PID-5 Full Version Adult PDF (page 8, 'Personality Trait
Facet and Domain Scoring') for the 16 reverse items, the 25 facet->item maps,
and the 5 domain->3-facet worksheet. Validity-scale item lists (VRIN/ORS/PRD)
are from the 2024 PID-5 book (Markon et al.), Tables 4-1, 4-2, 4-3.

All item numbers are 1..220 and refer to the 220-item full version.
"""

REVERSE_ITEMS = [7, 30, 35, 58, 87, 90, 96, 97, 98, 131, 142, 155, 164, 177, 210, 215]

# facet name -> list of item numbers (R-suffix dropped; reverse membership is
# determined by REVERSE_ITEMS). Verbatim from the APA worksheet.
FACET_ITEMS = {
    "Anhedonia": [1, 23, 26, 30, 124, 155, 157, 189],
    "Anxiousness": [79, 93, 95, 96, 109, 110, 130, 141, 174],
    "Attention Seeking": [14, 43, 74, 111, 113, 173, 191, 211],
    "Callousness": [11, 13, 19, 54, 72, 73, 90, 153, 166, 183, 198, 200, 207, 208],
    "Deceitfulness": [41, 53, 56, 76, 126, 134, 142, 206, 214, 218],
    "Depressivity": [27, 61, 66, 81, 86, 104, 119, 148, 151, 163, 168, 169, 178, 212],
    "Distractibility": [6, 29, 47, 68, 88, 118, 132, 144, 199],
    "Eccentricity": [5, 21, 24, 25, 33, 52, 55, 70, 71, 152, 172, 185, 205],
    "Emotional Lability": [18, 62, 102, 122, 138, 165, 181],
    "Grandiosity": [40, 65, 114, 179, 187, 197],
    "Hostility": [28, 32, 38, 85, 92, 116, 158, 170, 188, 216],
    "Impulsivity": [4, 16, 17, 22, 58, 204],
    "Intimacy Avoidance": [89, 97, 108, 120, 145, 203],
    "Irresponsibility": [31, 129, 156, 160, 171, 201, 210],
    "Manipulativeness": [107, 125, 162, 180, 219],
    "Perceptual Dysregulation": [36, 37, 42, 44, 59, 77, 83, 154, 192, 193, 213, 217],
    "Perseveration": [46, 51, 60, 78, 80, 100, 121, 128, 137],
    "Restricted Affectivity": [8, 45, 84, 91, 101, 167, 184],
    "Rigid Perfectionism": [34, 49, 105, 115, 123, 135, 140, 176, 196, 220],
    "Risk Taking": [3, 7, 35, 39, 48, 67, 69, 87, 98, 112, 159, 164, 195, 215],
    "Separation Insecurity": [12, 50, 57, 64, 127, 149, 175],
    "Submissiveness": [9, 15, 63, 202],
    "Suspiciousness": [2, 103, 117, 131, 133, 177, 190],
    "Unusual Beliefs and Experiences": [94, 99, 106, 139, 143, 150, 194, 209],
    "Withdrawal": [10, 20, 75, 82, 136, 146, 147, 161, 182, 186],
}

# APA 3-facet-per-domain worksheet (primary domain score).
DOMAIN_FACETS_WORKSHEET = {
    "Negative Affect": ["Emotional Lability", "Anxiousness", "Separation Insecurity"],
    "Detachment": ["Withdrawal", "Anhedonia", "Intimacy Avoidance"],
    "Antagonism": ["Manipulativeness", "Deceitfulness", "Grandiosity"],
    "Disinhibition": ["Irresponsibility", "Impulsivity", "Distractibility"],
    "Psychoticism": ["Unusual Beliefs and Experiences", "Eccentricity", "Perceptual Dysregulation"],
}

# AMPD full 25-facet -> 5-domain mapping (2024 book, p. 8). Each facet belongs
# to exactly one domain. Used as the fuller alternative to the 3-facet worksheet.
DOMAIN_FACETS_FULL = {
    "Negative Affect": ["Emotional Lability", "Anxiousness", "Restricted Affectivity",
                        "Separation Insecurity", "Hostility", "Perseveration", "Submissiveness"],
    "Detachment": ["Withdrawal", "Anhedonia", "Depressivity", "Intimacy Avoidance", "Suspiciousness"],
    "Antagonism": ["Manipulativeness", "Deceitfulness", "Grandiosity", "Attention Seeking", "Callousness"],
    "Disinhibition": ["Irresponsibility", "Impulsivity", "Rigid Perfectionism", "Distractibility", "Risk Taking"],
    "Psychoticism": ["Unusual Beliefs and Experiences", "Eccentricity", "Perceptual Dysregulation"],
}

# Validity scales (2024 book Tables 4-1, 4-2, 4-3).
VRIN_PAIRS = [(79, 174), (109, 110), (102, 122), (138, 181), (38, 92), (80, 128),
              (50, 127), (148, 169), (89, 145), (74, 173), (191, 211), (153, 166),
              (125, 180), (105, 123), (132, 144), (21, 55), (24, 25), (52, 152),
              (70, 71), (172, 185)]
ORS_ITEMS = [2, 8, 39, 40, 44, 150, 166, 170, 171, 178]
PRD_ITEMS = [2, 11, 36, 38, 42, 47, 96, 98, 106, 119, 122, 136, 148, 154, 162,
             163, 168, 169, 183, 192, 198, 199]

# Cutoffs (2024 book).
VRIN_CUTOFF = 17      # >= 17 flags inconsistent responding
ORS_CUTOFF = 3        # >= 3 flags overreporting
PRD_UNDER = 11        # < 11 flags underreporting / positive impression management
PRD_GENUINE = 20      # > 20 genuine; 11..20 ambiguous

# Item-level response coding (0..3).
ANCHORS_PID5 = {
    0: "Very False or Often False",
    1: "Sometimes or Somewhat False",
    2: "Sometimes or Somewhat True",
    3: "Very True or Often True",
}


def assigned_items():
    """Return the set of item numbers 1..220 that appear in at least one facet."""
    s = set()
    for items in FACET_ITEMS.values():
        s.update(items)
    return s


def unassigned_items():
    """Items 1..220 not in any facet (left as 'unassigned (not in worksheet key)')."""
    return sorted(set(range(1, 221)) - assigned_items())
