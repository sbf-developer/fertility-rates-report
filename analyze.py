"""
Cross-country and within-country descriptive statistics.

Nothing here identifies causal effects. Outputs are limited to:
  - levels and changes we can measure directly
  - bivariate associations (with explicit non-causal interpretation)
"""

from __future__ import annotations

import pandas as pd

from config import EXPLANATORY_CODES, INDICATORS, OUTCOME_CODE


def latest_country_snapshot(wide: pd.DataFrame, year: int | None = None) -> pd.DataFrame:
    """
    One row per country: values in the latest year with non-missing TFR,
    or a specified year.
    """
    rows: list[dict] = []
    for cc, grp in wide.groupby("country_code"):
        grp = grp.sort_values("year")
        if year is not None:
            snap = grp.loc[grp["year"] == year]
            if snap.empty:
                continue
            row = snap.iloc[0].to_dict()
        else:
            valid = grp.dropna(subset=[OUTCOME_CODE])
            if valid.empty:
                continue
            row = valid.iloc[-1].to_dict()
        rows.append(row)
    return pd.DataFrame(rows)


def cross_country_correlations(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Pearson r(TFR, x) across countries at one point in time."""
    records: list[dict] = []
    for code in EXPLANATORY_CODES:
        if code not in snapshot.columns:
            continue
        pair = snapshot[[OUTCOME_CODE, code, "country_code"]].dropna()
        if len(pair) < 5:
            continue
        records.append(
            {
                "indicator_code": code,
                "indicator": INDICATORS[code].short_label,
                "n_countries": len(pair),
                "pearson_r": pair[OUTCOME_CODE].corr(pair[code]),
            }
        )
    return pd.DataFrame(records).sort_values("pearson_r")


def within_country_first_diff_correlations(wide: pd.DataFrame, country_code: str) -> pd.DataFrame:
    """Year-on-year changes — weak test, but less dominated by shared trends than levels."""
    sub = wide.loc[wide["country_code"] == country_code].sort_values("year")
    diff = sub[[OUTCOME_CODE] + EXPLANATORY_CODES].diff()
    records: list[dict] = []
    for code in EXPLANATORY_CODES:
        if code not in diff.columns:
            continue
        pair = diff[[OUTCOME_CODE, code]].dropna()
        if len(pair) < 10:
            continue
        records.append(
            {
                "indicator_code": code,
                "indicator": INDICATORS[code].short_label,
                "n_years": len(pair),
                "pearson_r": pair[OUTCOME_CODE].corr(pair[code]),
            }
        )
    return pd.DataFrame(records).sort_values("pearson_r")
