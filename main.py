#!/usr/bin/env python3
"""Run: python main.py"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from config import (
    COMPARISON_COUNTRY,
    CONTRAST_COUNTRIES,
    COUNTRIES,
    CROSS_COUNTRY_SAMPLE,
    DEFAULT_COUNTRY,
    OUTCOME_CODE,
    OUTPUT_DIR,
    PAPER_FIGURES_DIR,
    all_regional_countries,
)
from fetch_data import fetch_wdi_panel, save_panel, to_wide_panel
from stats_tex import build_snapshot, write_latex_country_table
from evidence_viz import generate_evidence_figures
from regional_viz import generate_regional_figures
from visualize import generate_all_figures, generate_paper_figures

SNAPSHOT_YEAR = 2019

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def print_summary(wide_ts, wide_cross) -> None:
    sep = "-" * 72
    print(f"\n{sep}\nDESCRIPTIVE SUMMARY\n{sep}")

    for cc in [DEFAULT_COUNTRY, COMPARISON_COUNTRY]:
        sub = wide_ts.loc[wide_ts["country_code"] == cc].sort_values("year")
        tfr = sub[OUTCOME_CODE].dropna()
        print(
            f"{COUNTRIES[cc]}: TFR {tfr.iloc[0]:.2f} ({int(sub.loc[tfr.index[0], 'year'])})"
            f" -> {tfr.iloc[-1]:.2f} ({int(sub.loc[tfr.index[-1], 'year'])})"
        )

    snap, yr = build_snapshot(wide_cross, SNAPSHOT_YEAR)
    print(f"\nTFR by country ({yr}), high-income sample:")
    for _, row in snap.sort_values(OUTCOME_CODE)[["country_name", OUTCOME_CODE]].dropna().iterrows():
        print(f"  {row['country_name']:<22} {row[OUTCOME_CODE]:.2f}")

    print(f"\nFigures: ./{OUTPUT_DIR}/  and  ./{PAPER_FIGURES_DIR}/\n{sep}")


def main() -> int:
    try:
        long_ts = fetch_wdi_panel(country_codes=list(COUNTRIES.keys()))
        long_cross = fetch_wdi_panel(
            country_codes=list(CROSS_COUNTRY_SAMPLE.keys()),
            country_names=CROSS_COUNTRY_SAMPLE,
        )
        long_contrast = fetch_wdi_panel(
            country_codes=list(CONTRAST_COUNTRIES.keys()),
            country_names=CONTRAST_COUNTRIES,
        )
        regional_names = all_regional_countries()
        long_regional = fetch_wdi_panel(
            country_codes=list(regional_names.keys()),
            country_names=regional_names,
            indicator_codes=[OUTCOME_CODE],
        )
    except Exception as exc:
        logger.error("World Bank API fetch failed: %s", exc)
        return 1

    output_dir = Path(OUTPUT_DIR)
    save_panel(long_ts, output_dir / "wdi_fertility_panel.csv")
    save_panel(long_cross, output_dir / "wdi_cross_country_panel.csv")
    save_panel(long_regional, output_dir / "wdi_regional_tfr_panel.csv")

    wide_ts = to_wide_panel(long_ts)
    wide_cross = to_wide_panel(long_cross)
    wide_contrast = to_wide_panel(long_contrast)
    wide_regional = to_wide_panel(long_regional)

    generate_all_figures(wide_ts, output_dir)
    actual_year = write_latex_country_table(wide_cross, SNAPSHOT_YEAR, Path("paper"))
    generate_paper_figures(wide_ts, wide_cross, wide_contrast, snapshot_year=actual_year)
    regional_year = generate_regional_figures(wide_regional, Path(PAPER_FIGURES_DIR))
    Path("paper/regional_meta.tex").write_text(
        f"\\newcommand{{\\RegionalYear}}{{{regional_year}}}\n",
        encoding="utf-8",
    )
    generate_evidence_figures(Path(PAPER_FIGURES_DIR))
    print_summary(wide_ts, wide_cross)
    return 0


if __name__ == "__main__":
    sys.exit(main())
