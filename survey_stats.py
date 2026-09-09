"""Scoring and confidence-interval maths for the SCCWRP staff survey explorer.

Kept separate from the UI so the numbers can be tested and reused without
starting Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import pandas as pd

LIKERT_COLS = [
    "1 Strongly disagree",
    "2 Somewhat disagree",
    "3 Neither agree/disagree",
    "4 Somewhat agree",
    "5 Strongly agree",
]

# Two-sided 95% t critical values by degrees of freedom. Beyond df=100 the
# value is flat enough that the normal approximation is fine.
_T975 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
    15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080,
    22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048,
    29: 2.045, 30: 2.042, 31: 2.040, 32: 2.037, 33: 2.035, 34: 2.032, 35: 2.030,
    36: 2.028, 37: 2.026, 38: 2.024, 39: 2.023, 40: 2.021,
}


def t_critical(df: int) -> float:
    """Two-sided 95% t multiplier for ``df`` degrees of freedom."""
    if df < 1:
        return 0.0
    if df <= 40:
        return _T975[df]
    for cutoff, value in ((45, 2.014), (50, 2.009), (60, 2.000), (80, 1.990), (100, 1.984)):
        if df <= cutoff:
            return value
    return 1.960


@dataclass(frozen=True)
class Estimate:
    """A group's mean on one question, with both flavours of interval."""

    n: int
    mean: float
    lo: float          # standard 95% interval
    hi: float
    lo_adj: float      # after the finite population correction
    hi_adj: float
    fpc: float

    def bounds(self, adjusted: bool) -> tuple[float, float]:
        return (self.lo_adj, self.hi_adj) if adjusted else (self.lo, self.hi)


def _clamp(value: float, low: float = 1.0, high: float = 5.0) -> float:
    return max(low, min(high, value))


def estimate(counts: Sequence[int], population: float) -> Estimate | None:
    """Mean and 95% intervals for one group's answers to one question.

    ``counts`` are the five Likert tallies, lowest to highest. ``population``
    is how many staff that group actually has, which drives the finite
    population correction: a group where nearly everyone answered has little
    room left to be wrong.
    """
    counts = [int(c) for c in counts]
    n = sum(counts)
    if n == 0:
        return None

    mean = sum(c * (i + 1) for i, c in enumerate(counts)) / n
    if n < 2:
        return Estimate(n, mean, mean, mean, mean, mean, 0.0)

    ss = sum(c * (i + 1 - mean) ** 2 for i, c in enumerate(counts))
    se = (ss / (n - 1)) ** 0.5 / n**0.5
    moe = t_critical(n - 1) * se

    if population > 1:
        fpc = max((population - n) / (population - 1), 0.0) ** 0.5
    else:
        fpc = 0.0
    moe_adj = moe * fpc

    return Estimate(
        n=n,
        mean=mean,
        lo=_clamp(mean - moe),
        hi=_clamp(mean + moe),
        lo_adj=_clamp(mean - moe_adj),
        hi_adj=_clamp(mean + moe_adj),
        fpc=fpc,
    )


def group_populations(
    respondents: dict[str, int],
    overrides: dict[str, int | None],
    total_staff: int,
) -> dict[str, float]:
    """Work out how many staff sit in each job class.

    A class with an override uses that number as given. Whatever staff are
    left over get split among the remaining classes in proportion to how many
    of them responded. No class is ever assigned fewer staff than the number
    of people who actually answered.
    """
    fixed = {k: float(v) for k, v in overrides.items() if v is not None}
    free = [k for k in respondents if k not in fixed]

    pops: dict[str, float] = dict(fixed)
    if not free:
        return pops

    free_responses = sum(respondents[k] for k in free)
    remaining = max(total_staff - sum(fixed.values()), free_responses)
    for k in free:
        share = respondents[k] / free_responses
        pops[k] = max(respondents[k], share * remaining)
    return pops


def pool(frame: pd.DataFrame, classes: Iterable[str]) -> list[int]:
    """Sum the Likert tallies across several job classes."""
    subset = frame[frame["Job Class"].isin(list(classes))]
    return [int(subset[col].sum()) for col in LIKERT_COLS]


def load_survey(path_or_buffer) -> pd.DataFrame:
    """Read the tidy survey CSV and make sure the columns we rely on exist."""
    frame = pd.read_csv(path_or_buffer)
    required = {
        "Section_num", "Section", "Question_num", "Question",
        "Short label", "Job Class", *LIKERT_COLS,
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            "This file is missing columns the app needs: " + ", ".join(sorted(missing))
        )
    frame[LIKERT_COLS] = frame[LIKERT_COLS].fillna(0).astype(int)
    return frame
