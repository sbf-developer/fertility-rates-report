"""Regional TFR figures — Asia, Middle East & North Africa, Sub-Saharan Africa."""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import (
    OUTCOME_CODE,
    PAPER_FIGURES_DIR,
    REGIONAL_HIGHLIGHTS,
    REGIONAL_SAMPLES,
    REGIONAL_TRAJECTORIES,
    REPLACEMENT_TFR,
    all_regional_countries,
)
from stats_tex import build_snapshot
from visualize import PALETTE, _country_label, _country_subset, _save

logger = logging.getLogger(__name__)

_REGION_SHORT = {
    "Middle East & North Africa": "Middle East & N. Africa",
    "Sub-Saharan Africa": "Sub-Saharan Africa",
}


def _region_title(name: str) -> str:
    return _REGION_SHORT.get(name, name)


def plot_regional_tfr_snapshot(
    wide: pd.DataFrame,
    output_path: Path,
    snapshot_year: int = 2022,
) -> int:
    """Three-panel horizontal bar chart: latest TFR by country within each region."""
    snapshot, actual_year = build_snapshot(wide, snapshot_year)
    regions = list(REGIONAL_SAMPLES.keys())
    n_regions = len(regions)

    fig, axes = plt.subplots(n_regions, 1, figsize=(10.5, 4.4 * n_regions), sharex=False)
    axes = np.atleast_1d(axes)

    for ax, region in zip(axes, regions):
        codes = set(REGIONAL_SAMPLES[region])
        df = snapshot.loc[snapshot["country_code"].isin(codes), ["country_code", "country_name", OUTCOME_CODE]]
        df = df.dropna().sort_values(OUTCOME_CODE, ascending=True)
        if df.empty:
            ax.set_visible(False)
            continue

        colors = [
            PALETTE[0] if cc in REGIONAL_HIGHLIGHTS else "0.78"
            for cc in df["country_code"]
        ]
        ax.barh(df["country_name"], df[OUTCOME_CODE], height=0.72, color=colors, edgecolor="0.3", linewidth=0.35)
        ax.axvline(REPLACEMENT_TFR, color="0.3", linestyle="--", linewidth=1.0)

        for _, row in df.iterrows():
            ax.text(
                row[OUTCOME_CODE] + 0.04,
                row["country_name"],
                f"{row[OUTCOME_CODE]:.2f}",
                va="center",
                fontsize=9,
            )

        ax.set_title(_region_title(region), fontweight="bold", fontsize=11, loc="left", pad=8)
        ax.set_xlabel("TFR (births per woman)", fontsize=10)
        ax.set_xlim(0, max(df[OUTCOME_CODE].max() + 0.5, 2.5))
        ax.tick_params(axis="y", labelsize=9.5)
        ax.tick_params(axis="x", labelsize=9)
        ax.grid(axis="x", alpha=0.25, linewidth=0.5)

    fig.suptitle(f"Total fertility rate by country ({actual_year})", fontweight="bold", fontsize=12, y=0.995)
    fig.text(
        0.01,
        0.002,
        "Highlighted bars: major illustrative cases. Dashed line: replacement (2.1). Source: World Bank WDI.",
        fontsize=8.5,
        color="0.35",
    )
    fig.subplots_adjust(hspace=0.38, top=0.96, bottom=0.04)
    _save(fig, output_path)
    return actual_year


def plot_regional_trajectories(wide: pd.DataFrame, output_path: Path) -> None:
    """Three-panel line charts: selected country trajectories 1960--2023."""
    names = all_regional_countries()
    regions = list(REGIONAL_TRAJECTORIES.keys())

    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2), sharey=True)

    for ax, region in zip(axes, regions):
        codes = REGIONAL_TRAJECTORIES[region]
        for j, cc in enumerate(codes):
            sub = _country_subset(wide, cc)
            if sub.empty or OUTCOME_CODE not in sub.columns:
                continue
            series = sub[["year", OUTCOME_CODE]].dropna()
            if series.empty:
                continue
            ax.plot(
                series["year"],
                series[OUTCOME_CODE],
                label=_country_label(cc, names),
                color=PALETTE[j],
                linewidth=2.0,
            )

        ax.axhline(REPLACEMENT_TFR, color="0.35", linestyle="--", linewidth=0.9)
        ax.set_title(_region_title(region), fontweight="bold", fontsize=10)
        ax.set_xlabel("Year")
        ax.set_xlim(1960, 2024)
        ax.grid(axis="y", alpha=0.25, linewidth=0.5)
        ax.legend(frameon=False, fontsize=8, loc="upper right")

    axes[0].set_ylabel("Births per woman")
    axes[0].set_ylim(0.5, 8.5)
    fig.suptitle("Fertility trajectories: selected countries, 1960--2023", fontweight="bold", y=1.03)
    fig.tight_layout()
    _save(fig, output_path)


def generate_regional_figures(
    wide_regional: pd.DataFrame,
    paper_dir: Path | None = None,
    snapshot_year: int = 2022,
) -> int:
    paper_dir = paper_dir or Path(PAPER_FIGURES_DIR)
    actual_year = plot_regional_tfr_snapshot(
        wide_regional, paper_dir / "fig10_regional_snapshot", snapshot_year
    )
    plot_regional_trajectories(wide_regional, paper_dir / "fig11_regional_trajectories")
    logger.info("Saved regional figures to %s", paper_dir)
    return actual_year
