"""TEF Canada expression écrite scoring.

ONE SCALE: 0-450.

The TEF attestation issued since the 11 December 2023 revision shows a headline
figure on a 0-699 scale, but IRCC does not accept it. Express Entry, the PSTQ and
every other federal/provincial stream read the **"Équivalence ancien score"**
column — expression écrite out of 450 — and that is the only column the official
NCLC/CLB equivalency table is written against. Entering the /699 number in an
Express Entry profile is a documented cause of refusal.

So this module reports /450 and nothing else. An earlier version emitted a
150-700 curve that matched neither scale, and the version after it showed /699 as
the headline with /450 demoted to a footnote — both invite the candidate to read
the wrong number off the screen. The /699 figure is deliberately absent: no
authoritative rating-to-/699 mapping exists (third-party charts disagree with
each other by 35+ points at the NCLC 7 boundary), and a wrong number here is
worse than no number.

Section weighting is 40% Section A / 60% Section B, mirroring the exam's own
weighting of the short "transmettre des informations" task against the longer
argumentative one.

⚠️  CALIBRATION CAVEAT
The rating-to-score anchors below are a documented heuristic, not an official
mapping — Le français des affaires does not publish one, because human correctors
score against level descriptors rather than a 1-5 mean. Treat reported scores as
indicative, and read the NCLC level rather than the raw number: the level is what
IRCC acts on, and it is the part this mapping is built to get right.
"""

from bisect import bisect_right

TASK_A_WEIGHT = 0.4
TASK_B_WEIGHT = 0.6

SCALE_MAX = 450

# Official IRCC equivalency table for TEF Canada *expression écrite*, for tests
# taken on or after 10 December 2023. (lower_bound, upper_bound, nclc).
#
# IRCC stops at CLB/NCLC 10: everything from 393 up is "10 or more" and earns the
# same Express Entry points. Le français des affaires splits that band further
# (393-415 = NCLC 10, 416+ = NCLC 11-12), which matters for nothing IRCC does, so
# the table below follows IRCC and caps at 10.
NCLC_BANDS: list[tuple[int, int, int]] = [
    (181, 225, 4),
    (226, 270, 5),
    (271, 309, 6),
    (310, 348, 7),
    (349, 370, 8),
    (371, 392, 9),
    (393, SCALE_MAX, 10),
]

# NCLC 7 — the Express Entry / most-programs writing bar.
EXPRESS_ENTRY_THRESHOLD = 310
EXPRESS_ENTRY_NCLC = 7

# Rating (1-5) -> score anchors, interpolated linearly between points.
#
# Each anchor is the FLOOR of an NCLC band, so a half-point of rating maps onto
# exactly one NCLC level over the range that matters: a combined rating in
# [3.5, 4.0) is NCLC 7 and nothing else, [3.0, 3.5) is NCLC 6, and so on. The
# steps compress above 4.5 because the real NCLC 9 and 10 bands are themselves
# narrower (22 and 23 points wide, against 39 for NCLC 6).
#
# Below 2.0 the curve is a single straight segment down to 0. IRCC publishes no
# band under NCLC 4, so there is nothing to anchor against and the exact number
# there carries no meaning beyond "well short".
_ANCHORS: list[tuple[float, int]] = [
    (1.00, 0),
    (2.00, 181),   # NCLC 4
    (2.50, 226),   # NCLC 5
    (3.00, 271),   # NCLC 6
    (3.50, 310),   # NCLC 7 — Express Entry threshold
    (4.00, 349),   # NCLC 8
    (4.50, 371),   # NCLC 9
    (4.75, 393),   # NCLC 10
    (5.00, SCALE_MAX),
]

# Standard NCLC/CLB <-> CECRL alignment. Coarse and indicative: the CEFR band is
# shown to orient the candidate, never to drive a decision. NCLC is the number
# IRCC acts on.
_CEFR_BY_NCLC = {4: "A2", 5: "B1", 6: "B1", 7: "B2", 8: "B2", 9: "C1", 10: "C1"}


def rating_to_score(rating: float) -> int:
    """Piecewise-linear interpolation of a 1-5 rating onto the 0-450 scale."""
    rating = max(1.0, min(5.0, float(rating)))
    for (low_r, low_s), (high_r, high_s) in zip(_ANCHORS, _ANCHORS[1:]):
        if rating <= high_r:
            span = high_r - low_r
            fraction = 0.0 if span == 0 else (rating - low_r) / span
            return min(SCALE_MAX, round(low_s + fraction * (high_s - low_s)))
    return SCALE_MAX


def combined_rating(rating_a: float, rating_b: float) -> float:
    """Weight the two sections 40/60."""
    return round(rating_a * TASK_A_WEIGHT + rating_b * TASK_B_WEIGHT, 2)


def nclc_level(score: int) -> int:
    """NCLC/CLB writing level for a /450 score, per the IRCC table.

    Returns 0 below NCLC 4, the lowest band IRCC publishes.
    """
    floors = [floor for floor, _, _ in NCLC_BANDS]
    index = bisect_right(floors, score)
    return NCLC_BANDS[index - 1][2] if index else 0


def nclc_band(nclc: int) -> tuple[int, int] | None:
    """(floor, ceiling) of an NCLC level on the /450 scale, or None below 4."""
    for floor, ceiling, level in NCLC_BANDS:
        if level == nclc:
            return (floor, ceiling)
    return None


def cefr_level(nclc: int) -> str:
    """Indicative CECRL band for an NCLC writing level."""
    if nclc >= 10:
        return "C1"
    return _CEFR_BY_NCLC.get(nclc, "< A2")


def points_to_next_level(score: int) -> int | None:
    """Points still needed to reach the next NCLC band, or None at the ceiling."""
    for floor, _, _ in NCLC_BANDS:
        if score < floor:
            return floor - score
    return None


def section_report(rating: float) -> dict:
    """Indicative standalone breakdown for one section.

    The exam reports a single expression écrite score, not one per section, so
    this is a diagnostic: it answers "which of the two is holding me back?" by
    running each section's rating through the same curve as the whole test.
    """
    score = rating_to_score(rating)
    nclc = nclc_level(score)
    return {
        "rating": round(float(rating), 2),
        "score": score,
        "nclc": nclc,
        "cefr": cefr_level(nclc),
    }


def score_report(rating_a: float, rating_b: float) -> dict:
    """Full score breakdown for a submission. All scores are /450."""
    rating = combined_rating(rating_a, rating_b)
    score = rating_to_score(rating)
    nclc = nclc_level(score)
    band = nclc_band(nclc)
    return {
        "rating": rating,
        "score": score,
        "scoreMax": SCALE_MAX,
        "nclc": nclc,
        "cefr": cefr_level(nclc),
        "bandFloor": band[0] if band else None,
        "bandCeiling": band[1] if band else None,
        "pointsToNextLevel": points_to_next_level(score),
        "expressEntryEligible": score >= EXPRESS_ENTRY_THRESHOLD,
        "expressEntryThreshold": EXPRESS_ENTRY_THRESHOLD,
        "sectionA": section_report(rating_a),
        "sectionB": section_report(rating_b),
    }
