"""
Visualisation — publication figures for the fertility paper.

Design principles:
  - Native units only (no index rebasing).
  - One clear message per figure; small multiples for detail.
  - PDF output for LaTeX; PNG for quick preview.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import (
    CONTRAST_COUNTRIES,
    COUNTRIES,
    CROSS_COUNTRY_SAMPLE,
    HIGHLIGHT_COUNTRIES,
    INDICATORS,
    OUTCOME_CODE,
    PAPER_FIGURES_DIR,
    REPLACEMENT_TFR,
)
from stats_tex import build_snapshot

logger = logging.getLogger(__name__)

# LaTeX-friendly styling
plt.rcParams.update(
    {
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "font.family": "serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

PALETTE = sns.color_palette("colorblind", n_colors=12)

# Fixed order and colours: US always blue (0), UK always orange (1)
TIMESERIES_COUNTRY_ORDER = ["USA", "GBR"]
COUNTRY_COLORS: dict[str, tuple] = {
    "USA": PALETTE[0],
    "GBR": PALETTE[1],
    "ISR": PALETTE[2],
}


def _ordered_country_codes(country_codes: list[str] | pd.Index) -> list[str]:
    """Return country codes in a stable display order."""
    available = set(country_codes)
    ordered = [cc for cc in TIMESERIES_COUNTRY_ORDER if cc in available]
    ordered.extend(cc for cc in country_codes if cc not in ordered)
    return ordered

# Variables to test cross-country (not pre-judged as "drivers")
CROSS_COUNTRY_CODES = [
    "SE.TER.ENRR.FE",
    "SL.TLF.CACT.FE.ZS",
    "NY.GDP.PCAP.PP.KD",
    "SP.URB.TOTL.IN.ZS",
]


def _country_subset(wide: pd.DataFrame, country_code: str) -> pd.DataFrame:
    return wide.loc[wide["country_code"] == country_code].sort_values("year")


def _save(fig: plt.Figure, path: Path) -> None:
    """Save figure as PDF (for LaTeX) and PNG (for preview)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", path.with_suffix(".pdf"))


def _country_label(country_code: str, names: dict[str, str] | None = None) -> str:
    lookup = names or {**COUNTRIES, **CROSS_COUNTRY_SAMPLE, **CONTRAST_COUNTRIES}
    return lookup.get(country_code, country_code)


def plot_tfr_levels(
    wide: pd.DataFrame,
    country_codes: list[str],
    output_path: Path,
    country_names: dict[str, str] | None = None,
    title: str = "Total fertility rate",
    ylim: tuple[float, float] = (1.0, 4.0),
) -> None:
    """TFR time series — no annotations, no phase shading."""
    country_codes = _ordered_country_codes(country_codes)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))

    for cc in country_codes:
        sub = _country_subset(wide, cc)
        ax.plot(
            sub["year"],
            sub[OUTCOME_CODE],
            label=_country_label(cc, country_names),
            color=COUNTRY_COLORS.get(cc, PALETTE[0]),
            linewidth=2.2,
        )

    ax.axhline(REPLACEMENT_TFR, color="0.3", linestyle="--", linewidth=1.1)
    ax.set_xlabel("Year")
    ax.set_ylabel("Births per woman")
    ax.set_title(title)
    ax.set_ylim(*ylim)
    ax.set_xlim(1960, 2024)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.3, linewidth=0.5)
    fig.tight_layout()
    _save(fig, output_path)


def plot_correlates_timeseries(
    wide: pd.DataFrame,
    country_codes: list[str],
    output_path: Path,
) -> None:
    """Time series of selected correlates — explicitly not labelled as causes."""
    country_codes = _ordered_country_codes(country_codes)
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), sharex=True)
    axes = axes.flatten()

    for ax, code in zip(axes, CROSS_COUNTRY_CODES):
        spec = INDICATORS[code]
        for cc in country_codes:
            sub = _country_subset(wide, cc)
            if code not in sub.columns:
                continue
            series = sub[["year", code]].dropna(subset=[code])
            if series.empty:
                continue
            ax.plot(
                series["year"],
                series[code],
                label=COUNTRIES.get(cc, cc),
                color=COUNTRY_COLORS.get(cc, PALETTE[0]),
                linewidth=1.8,
            )
        ax.set_title(spec.short_label, fontweight="bold", fontsize=10)
        unit = spec.label.split("(")[-1].rstrip(")") if "(" in spec.label else ""
        ax.set_ylabel(unit)
        ax.grid(axis="y", alpha=0.25, linewidth=0.5)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.02))
    fig.suptitle("Selected correlates (time series, native units)", fontweight="bold", y=0.98)
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    _save(fig, output_path)


def plot_tfr_by_country(
    snapshot: pd.DataFrame,
    output_path: Path,
    snapshot_year: int,
    highlight_codes: list[str] | None = None,
) -> None:
    """
    Horizontal bar chart: TFR for each country, fully labelled.

    This replaces cross-country scatter/correlation plots — comparing 21 dots
    with a regression line is not informative and n is far too small.
    """
    highlight_codes = highlight_codes or HIGHLIGHT_COUNTRIES
    highlight_colors = {code: PALETTE[i] for i, code in enumerate(highlight_codes)}
    df = snapshot[["country_code", "country_name", OUTCOME_CODE]].dropna()
    df = df.sort_values(OUTCOME_CODE, ascending=True)

    fig, ax = plt.subplots(figsize=(8, 7.5))
    colors = [highlight_colors.get(cc, "0.75") for cc in df["country_code"]]
    ax.barh(df["country_name"], df[OUTCOME_CODE], color=colors, edgecolor="0.3", linewidth=0.4)
    ax.axvline(REPLACEMENT_TFR, color="0.25", linestyle="--", linewidth=1.2, label="Replacement (2.1)")

    for _, row in df.iterrows():
        ax.text(
            row[OUTCOME_CODE] + 0.03,
            row["country_name"],
            f"{row[OUTCOME_CODE]:.2f}",
            va="center",
            fontsize=8,
        )

    ax.set_xlabel("Total fertility rate (births per woman)")
    ax.set_title(f"TFR by country ({snapshot_year})", fontweight="bold")
    ax.set_xlim(0.8, max(df[OUTCOME_CODE].max() + 0.3, 2.3))
    ax.legend(loc="lower right", frameon=False)
    ax.grid(axis="x", alpha=0.25, linewidth=0.5)
    fig.tight_layout()
    _save(fig, output_path)


def plot_tfr_decades(
    wide: pd.DataFrame,
    country_codes: list[str],
    output_path: Path,
) -> None:
    """
    Figure 2 — Decadal average TFR (bar chart).

    Smooths year-to-year noise so a lay reader can see the direction of change
    at a glance. Standard descriptive device in demographic briefs.
    """
    country_codes = _ordered_country_codes(country_codes)
    records: list[dict] = []
    for cc in country_codes:
        sub = _country_subset(wide, cc)
        sub = sub.dropna(subset=[OUTCOME_CODE])
        sub["decade"] = (sub["year"] // 10) * 10
        for decade, grp in sub.groupby("decade"):
            records.append(
                {
                    "country": COUNTRIES.get(cc, cc),
                    "decade": decade,
                    "tfr": grp[OUTCOME_CODE].mean(),
                }
            )

    df = pd.DataFrame(records)
    decades = sorted(df["decade"].unique())
    x = np.arange(len(decades))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    for i, cc in enumerate(country_codes):
        name = COUNTRIES.get(cc, cc)
        sub = df.loc[df["country"] == name].set_index("decade").reindex(decades)
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, sub["tfr"], width, label=name, color=COUNTRY_COLORS.get(cc, PALETTE[i]), alpha=0.9)
        # Label the most recent bar only — avoids clutter
        last = sub["tfr"].iloc[-1]
        if pd.notna(last):
            ax.text(
                x[-1] + offset,
                last + 0.05,
                f"{last:.2f}",
                ha="center",
                fontsize=8,
                fontweight="bold",
            )

    ax.axhline(REPLACEMENT_TFR, color="0.3", linestyle="--", linewidth=1.0)
    ax.text(len(decades) - 0.5, REPLACEMENT_TFR + 0.04, "Replacement (2.1)", fontsize=8, color="0.3")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(d)}s" for d in decades])
    ax.set_xlabel("Decade")
    ax.set_ylabel("Average births per woman")
    ax.set_title("Average fertility by decade")
    ax.legend(frameon=False)
    ax.set_ylim(0, 4.0)
    ax.grid(axis="y", alpha=0.3, linewidth=0.5)

    fig.tight_layout()
    _save(fig, output_path)



def plot_key_drivers(
    wide: pd.DataFrame,
    country_codes: list[str],
    output_path: Path,
) -> None:
    """Alias kept for output/ folder compatibility."""
    plot_correlates_timeseries(wide, country_codes, output_path)


def plot_small_multiples(
    wide: pd.DataFrame,
    country_codes: list[str],
    output_path: Path,
) -> None:
    """Appendix figure — full indicator set in native units."""
    country_codes = _ordered_country_codes(country_codes)
    codes = list(INDICATORS.keys())
    ncols = 3
    nrows = int(np.ceil(len(codes) / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(10, 3.2 * nrows), sharex=True)
    axes = np.atleast_1d(axes).flatten()

    for ax, code in zip(axes, codes):
        spec = INDICATORS[code]
        has_data = False
        for cc in country_codes:
            sub = _country_subset(wide, cc)
            if code not in sub.columns:
                continue
            series = sub[["year", code]].dropna(subset=[code])
            if series.empty:
                continue
            has_data = True
            ax.plot(
                series["year"],
                series[code],
                label=COUNTRIES.get(cc, cc),
                color=COUNTRY_COLORS.get(cc, PALETTE[0]),
                linewidth=1.6,
            )
        if not has_data:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        elif code == OUTCOME_CODE:
            ax.axhline(REPLACEMENT_TFR, color="0.45", linestyle="--", linewidth=0.9)
        ax.set_title(spec.short_label, fontsize=9, fontweight="bold")
        unit = spec.label.split("(")[-1].rstrip(")") if "(" in spec.label else ""
        if unit:
            ax.set_ylabel(unit, fontsize=8)
        ax.grid(axis="y", alpha=0.25, linewidth=0.5)
        ax.tick_params(labelsize=8)

    for ax in axes[len(codes) :]:
        ax.set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.02))
    fig.suptitle("All indicators over time (native units)", fontweight="bold", y=0.98)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    _save(fig, output_path)


def generate_all_figures(wide: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    country_codes = list(wide["country_code"].unique())
    plot_tfr_levels(wide, country_codes, output_dir / "tfr_levels")
    plot_tfr_decades(wide, country_codes, output_dir / "tfr_decades")
    plot_correlates_timeseries(wide, country_codes, output_dir / "correlates_timeseries")
    plot_small_multiples(wide, country_codes, output_dir / "small_multiples")


def generate_paper_figures(
    wide_ts: pd.DataFrame,
    wide_cross: pd.DataFrame,
    wide_contrast: pd.DataFrame | None = None,
    snapshot_year: int = 2019,
    paper_dir: Path | None = None,
) -> None:
    """Figures for the LaTeX paper (PDF + PNG)."""
    paper_dir = paper_dir or Path(PAPER_FIGURES_DIR)
    ts_countries = _ordered_country_codes(wide_ts["country_code"].unique())

    plot_tfr_levels(wide_ts, ts_countries, paper_dir / "fig1_tfr_timeline")
    plot_tfr_decades(wide_ts, ts_countries, paper_dir / "fig2_tfr_decades")
    plot_correlates_timeseries(wide_ts, ts_countries, paper_dir / "fig3_correlates_timeseries")
    plot_small_multiples(wide_ts, ts_countries, paper_dir / "figA_small_multiples")

    if wide_contrast is not None:
        contrast_codes = list(CONTRAST_COUNTRIES.keys())
        plot_tfr_levels(
            wide_contrast,
            contrast_codes,
            paper_dir / "fig5_tfr_contrast",
            country_names=CONTRAST_COUNTRIES,
            title="Total fertility rate: US, UK, and Israel",
            ylim=(1.0, 4.5),
        )

    snapshot, actual_year = build_snapshot(wide_cross, snapshot_year)
    plot_tfr_by_country(snapshot, paper_dir / "fig4_tfr_by_country", actual_year)
