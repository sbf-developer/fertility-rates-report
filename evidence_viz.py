"""Figures from published causal and survey evidence (not WDI)."""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from config import PAPER_FIGURES_DIR, REPLACEMENT_TFR
from evidence_data import INTENTIONS_GAP, ISRAEL_TFR_BY_GROUP, POLICY_EFFECTS
from visualize import PALETTE, _save

logger = logging.getLogger(__name__)


def plot_intentions_gap(output_path: Path) -> None:
    """Ideal fertility (surveys) vs period TFR — the intentions gap."""
    countries = [r.country for r in INTENTIONS_GAP]
    ideal = [r.ideal for r in INTENTIONS_GAP]
    tfr = [r.period_tfr for r in INTENTIONS_GAP]

    y = np.arange(len(countries))
    height = 0.35

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(y + height / 2, ideal, height, label="Ideal family size (survey)", color=PALETTE[0], alpha=0.9)
    ax.barh(y - height / 2, tfr, height, label="Period TFR (vital stats)", color=PALETTE[3], alpha=0.9)
    ax.axvline(REPLACEMENT_TFR, color="0.35", linestyle="--", linewidth=1.0)

    for i, row in enumerate(INTENTIONS_GAP):
        gap = row.ideal - row.period_tfr
        ax.text(max(row.ideal, row.period_tfr) + 0.05, i, f"gap {gap:.2f}", va="center", fontsize=8, color="0.35")

    ax.set_yticks(y)
    ax.set_yticklabels(countries)
    ax.set_xlabel("Children per woman")
    ax.set_title("Stated ideals vs achieved period fertility", fontweight="bold")
    ax.set_xlim(0.9, 2.8)
    ax.legend(loc="lower right", frameon=False)
    ax.grid(axis="x", alpha=0.25, linewidth=0.5)
    fig.text(
        0.01,
        -0.03,
        "Ideals: GGS-II (2020-2023) where available; Eurobarometer/GSS for FR, IT, ES, US. "
        "TFR: World Bank WDI (~2020-2022).",
        fontsize=7.5,
        color="0.35",
    )
    fig.tight_layout()
    _save(fig, output_path)


def plot_israel_groups(output_path: Path) -> None:
    """Israeli TFR by religiosity — compositional heterogeneity."""
    groups = [g.group for g in ISRAEL_TFR_BY_GROUP]
    tfrs = [g.tfr for g in ISRAEL_TFR_BY_GROUP]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [PALETTE[3] if "Secular" in g else PALETTE[0] if "Haredi" in g else "0.55" for g in groups]
    ax.bar(groups, tfrs, color=colors, edgecolor="0.3", linewidth=0.4)
    ax.axhline(REPLACEMENT_TFR, color="0.25", linestyle="--", linewidth=1.1, label="Replacement (2.1)")

    for x, val in enumerate(tfrs):
        ax.text(x, val + 0.12, f"{val:.2f}", ha="center", fontsize=9, fontweight="bold")

    ax.set_ylabel("Period TFR (births per woman)")
    ax.set_title("Israel: fertility by religiosity (Jewish women)", fontweight="bold")
    ax.set_ylim(0, 7.5)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25, linewidth=0.5)
    fig.text(0.01, -0.06, "Source: JPPI Annual Assessment 2023 (Israel Social Survey / CBS-linked rates).", fontsize=8, color="0.35")
    fig.tight_layout()
    _save(fig, output_path)


def plot_policy_effects(output_path: Path) -> None:
    """Forest-style plot of published quasi-experimental effect sizes."""
    pct = [p for p in POLICY_EFFECTS if p.unit == "percent"]
    tfr = [p for p in POLICY_EFFECTS if p.unit == "tfr"]

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))

    ax = axes[0]
    for i, p in enumerate(pct):
        lo, hi = p.lo or p.effect, p.hi or p.effect
        ax.errorbar(p.effect, i, xerr=[[p.effect - lo], [hi - p.effect]], fmt="o", color=PALETTE[0], capsize=4)
        ax.text(hi + 1, i, f"+{p.effect:.0f}%", va="center", fontsize=9)
    ax.set_yticks(range(len(pct)))
    ax.set_yticklabels([p.label for p in pct], fontsize=9)
    ax.set_xlabel("Change in birth probability (%)")
    ax.set_title("Cash transfer (DiD)", fontsize=10, fontweight="bold")
    ax.grid(axis="x", alpha=0.25, linewidth=0.5)

    ax = axes[1]
    for i, p in enumerate(tfr):
        lo, hi = p.lo or p.effect, p.hi or p.effect
        ax.errorbar(p.effect, i, xerr=[[p.effect - lo], [hi - p.effect]], fmt="o", color=PALETTE[2], capsize=4)
        ax.text(hi + 0.02, i, f"+{p.effect:.2f}", va="center", fontsize=9)
    ax.set_yticks(range(len(tfr)))
    ax.set_yticklabels([p.label for p in tfr], fontsize=9)
    ax.set_xlabel("Change in TFR (children per woman)")
    ax.set_title("Policy meta-review", fontsize=10, fontweight="bold")
    ax.grid(axis="x", alpha=0.25, linewidth=0.5)

    fig.suptitle("Illustrative fertility-policy effect sizes (published estimates)", fontweight="bold", y=1.05)
    fig.text(
        0.01,
        -0.05,
        "Left: Milligan (2005), +C$1,000 first-year Quebec benefit. "
        "Right: Luci-Greulich & Thévenon (2013) range for combined family-policy packages.",
        fontsize=7.5,
        color="0.35",
    )
    fig.tight_layout()
    _save(fig, output_path)


def generate_evidence_figures(paper_dir: Path | None = None) -> None:
    paper_dir = paper_dir or Path(PAPER_FIGURES_DIR)
    plot_intentions_gap(paper_dir / "fig6_intentions_gap")
    plot_israel_groups(paper_dir / "fig7_israel_groups")
    plot_policy_effects(paper_dir / "fig8_policy_effects")
    logger.info("Saved evidence figures to %s", paper_dir)
