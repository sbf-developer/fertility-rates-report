"""
Fetch harmonised country-year panels from the World Bank WDI API.

Uses wbgapi (https://github.com/tgherzog/wbgapi) — a thin Python wrapper around
https://api.worldbank.org/v2/ — no API key required.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd
import wbgapi as wb

from config import (
    COUNTRIES,
    END_YEAR,
    INDICATORS,
    OUTPUT_DIR,
    START_YEAR,
)

logger = logging.getLogger(__name__)

_YEAR_RE = re.compile(r"(\d{4})")


def _parse_year(time_value: object) -> int:
    """World Bank API returns years as 'YR2023', 2023, or '2023'."""
    if isinstance(time_value, int):
        return time_value
    text = str(time_value)
    match = _YEAR_RE.search(text)
    if not match:
        raise ValueError(f"Cannot parse year from {time_value!r}")
    return int(match.group(1))


def fetch_wdi_panel(
    country_codes: list[str] | None = None,
    indicator_codes: list[str] | None = None,
    start_year: int = START_YEAR,
    end_year: int = END_YEAR,
    country_names: dict[str, str] | None = None,
) -> pd.DataFrame:
    """
    Download WDI indicators and return a tidy long-format DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: country_code, country_name, year, indicator_code,
                 indicator_label, value
    """
    country_codes = country_codes or list(COUNTRIES.keys())
    indicator_codes = indicator_codes or list(INDICATORS.keys())
    names = country_names or COUNTRIES

    logger.info(
        "Fetching %d indicators for %s (%d–%d) from World Bank WDI…",
        len(indicator_codes),
        ", ".join(country_codes),
        start_year,
        end_year,
    )

    records: list[dict] = []
    for row in wb.data.fetch(
        indicator_codes,
        economy=country_codes,
        time=range(start_year, end_year + 1),
        skipBlanks=True,
    ):
        spec = INDICATORS.get(row["series"])
        records.append(
            {
                "country_code": row["economy"],
                "country_name": names.get(row["economy"], row["economy"]),
                "year": _parse_year(row["time"]),
                "indicator_code": row["series"],
                "indicator_label": spec.label if spec else row["series"],
                "value": float(row["value"]),
            }
        )

    df = pd.DataFrame.from_records(records)
    df = df.sort_values(["country_code", "indicator_code", "year"]).reset_index(drop=True)

    logger.info("Retrieved %d country-year-indicator observations.", len(df))
    return df


def to_wide_panel(long_df: pd.DataFrame) -> pd.DataFrame:
    """Pivot to country × year with one column per indicator code."""
    wide = long_df.pivot_table(
        index=["country_code", "country_name", "year"],
        columns="indicator_code",
        values="value",
        aggfunc="first",
    ).reset_index()
    return wide


def save_panel(long_df: pd.DataFrame, path: Path | None = None) -> Path:
    """Persist raw tidy panel to CSV for reproducibility."""
    path = path or Path(OUTPUT_DIR) / "wdi_fertility_panel.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    long_df.to_csv(path, index=False)
    logger.info("Saved panel to %s", path)
    return path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    panel = fetch_wdi_panel()
    save_panel(panel)
    print(panel.groupby(["country_code", "indicator_code"]).size().unstack(fill_value=0))
