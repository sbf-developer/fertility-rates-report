"""
Published statistics for causal-evidence figures.

All values are from peer-reviewed sources (see SOURCE keys). These are not
estimated from WDI; they illustrate findings from micro-data and quasi-experiments.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentionsRow:
    country: str
    ideal: float
    intended: float | None
    period_tfr: float
    source: str


@dataclass(frozen=True)
class PolicyEffect:
    label: str
    effect: float
    unit: str
    lo: float | None
    hi: float | None
    study: str


@dataclass(frozen=True)
class IsraelGroup:
    group: str
    tfr: float
    source: str


# GGS-II women 18-49 (ideal, intended) — Bujard & Friedrich 2025, Table 1.
# Period TFR: World Bank WDI, approximate mean 2020-2022 for alignment with GGS fieldwork.
INTENTIONS_GAP: tuple[IntentionsRow, ...] = (
    IntentionsRow("Germany", 2.28, 1.82, 1.52, "GGS-II; WDI"),
    IntentionsRow("United Kingdom", 2.30, 1.98, 1.57, "GGS-II; WDI"),
    IntentionsRow("France", 2.50, 1.95, 1.81, "Sobotka & Beaujouan 2014; WDI"),
    IntentionsRow("Netherlands", 2.19, 1.91, 1.55, "GGS-II; WDI"),
    IntentionsRow("Norway", 2.38, 2.09, 1.48, "GGS-II; WDI"),
    IntentionsRow("Finland", 2.18, 1.82, 1.38, "GGS-II; WDI"),
    IntentionsRow("Italy", 1.95, 1.90, 1.24, "Sobotka & Beaujouan 2014; WDI"),
    IntentionsRow("Spain", 2.07, 1.85, 1.17, "Sobotka & Beaujouan 2014; WDI"),
    IntentionsRow("United States", 2.35, 2.20, 1.65, "GSS/Eurobarometer synthesis; WDI"),
)

# Israel Jewish women by religiosity — JPPI 2023 / Okun 2013 (ISS-linked vital rates).
ISRAEL_TFR_BY_GROUP: tuple[IsraelGroup, ...] = (
    IsraelGroup("Secular", 2.00, "JPPI 2023"),
    IsraelGroup("Traditional\n(less religious)", 2.34, "JPPI 2023"),
    IsraelGroup("Traditional\n(religious)", 2.82, "JPPI 2023"),
    IsraelGroup("Religious (Dati)", 3.88, "JPPI 2023"),
    IsraelGroup("Ultra-Orthodox\n(Haredi)", 6.45, "JPPI 2023"),
)

# Quasi-experimental / meta-analytic effect sizes (point estimates for visualization).
POLICY_EFFECTS: tuple[PolicyEffect, ...] = (
    PolicyEffect(
        "Quebec baby bonus\n(Milligan 2005)",
        16.9,
        "percent",
        12.0,
        22.0,
        "milligan2005",
    ),
    PolicyEffect(
        "Family policy packages\n(Luci-Greulich & Thévenon 2013)",
        0.20,
        "tfr",
        0.10,
        0.30,
        "luci2013",
    ),
)
