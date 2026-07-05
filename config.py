"""
Configuration for the low-fertility correlates analysis.

Data source: World Bank World Development Indicators (WDI), accessed via wbgapi.
WDI is the standard harmonised cross-country panel used in demographic economics
(Eastwood & Lipton 2011; Myrskylä et al. 2009; OECD Family Database supplements).

Methodological note (read before interpreting charts):
    This module implements *descriptive* time-series tracking of variables that
    appear in fertility-decline frameworks (Second Demographic Transition, Becker
    household economics, gender-equity theory). Observed co-movement does NOT
    establish causal effects without identification strategy (IV, DiD, structural
    models). We report correlations only as exploratory summary statistics.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorSpec:
    """Metadata for one WDI indicator."""

    code: str
    label: str
    short_label: str
    theoretical_role: str
    direction_expected: str  # qualitative prior from literature


# ---------------------------------------------------------------------------
# Countries — USA has the longest, most complete WDI series among major
# low-fertility economies; GBR included for cross-check.
# ISO3 codes used by World Bank API.
# ---------------------------------------------------------------------------
# Primary time-series cases (long WDI panels for co-movement figures)
COUNTRIES: dict[str, str] = {
    "USA": "United States",
    "GBR": "United Kingdom",
}

# US/UK plus Israel — contrast case (high-income, above-replacement TFR)
CONTRAST_COUNTRIES: dict[str, str] = {
    "USA": "United States",
    "GBR": "United Kingdom",
    "ISR": "Israel",
}

# Bar-chart highlights in the cross-country snapshot
HIGHLIGHT_COUNTRIES: list[str] = ["USA", "GBR", "ISR"]

# High-income sample for cross-country level comparison (WDI ISO3 codes).
CROSS_COUNTRY_SAMPLE: dict[str, str] = {
    "USA": "United States",
    "GBR": "United Kingdom",
    "ISR": "Israel",
    "DEU": "Germany",
    "FRA": "France",
    "JPN": "Japan",
    "KOR": "Korea, Rep.",
    "ITA": "Italy",
    "ESP": "Spain",
    "SWE": "Sweden",
    "NOR": "Norway",
    "FIN": "Finland",
    "AUS": "Australia",
    "CAN": "Canada",
    "NLD": "Netherlands",
    "BEL": "Belgium",
    "CHE": "Switzerland",
    "AUT": "Austria",
    "DNK": "Denmark",
    "PRT": "Portugal",
    "IRL": "Ireland",
    "NZL": "New Zealand",
}

DEFAULT_COUNTRY = "USA"
COMPARISON_COUNTRY = "GBR"

# Analysis window — post-war demographic transition through latest WDI release
START_YEAR = 1960
END_YEAR = 2023

# Replacement-level fertility (UN/WB convention)
REPLACEMENT_TFR = 2.1

# ---------------------------------------------------------------------------
# Indicators mapped to causal/correlate frameworks discussed in the literature.
# All codes verified against WDI database (source id = 2).
# ---------------------------------------------------------------------------
INDICATORS: dict[str, IndicatorSpec] = {
    "SP.DYN.TFRT.IN": IndicatorSpec(
        code="SP.DYN.TFRT.IN",
        label="Total fertility rate (births per woman)",
        short_label="Total fertility rate",
        theoretical_role="Outcome — quantum of fertility",
        direction_expected="Declining in SDT countries",
    ),
    "SL.TLF.CACT.FE.ZS": IndicatorSpec(
        code="SL.TLF.CACT.FE.ZS",
        label="Labour force participation rate, female (% of female pop. 15+)",
        short_label="Female labour force participation",
        theoretical_role="Opportunity cost / gender role structure",
        direction_expected="Rising",
    ),
    "SE.TER.ENRR.FE": IndicatorSpec(
        code="SE.TER.ENRR.FE",
        label="School enrollment, tertiary, female (% gross)",
        short_label="Female tertiary enrollment",
        theoretical_role="Human capital / delayed childbearing",
        direction_expected="Rising",
    ),
    # WDI marriage-age series is sparse for USA/GBR; attainment is a standard proxy
    # for partnership/family formation delay (Rindfuss & Brewster 1996).
    "SE.SEC.CUAT.UP.FE.ZS": IndicatorSpec(
        code="SE.SEC.CUAT.UP.FE.ZS",
        label="Educational attainment, upper secondary+, female (% ages 25+)",
        short_label="Female upper-secondary attainment",
        theoretical_role="Human capital / delayed family formation",
        direction_expected="Rising",
    ),
    "NY.GDP.PCAP.PP.KD": IndicatorSpec(
        code="NY.GDP.PCAP.PP.KD",
        label="GDP per capita, PPP (constant 2017 international $)",
        short_label="GDP per capita (PPP)",
        theoretical_role="Income constraint / development",
        direction_expected="Rising",
    ),
    "SL.UEM.TOTL.ZS": IndicatorSpec(
        code="SL.UEM.TOTL.ZS",
        label="Unemployment, total (% of labour force)",
        short_label="Unemployment rate",
        theoretical_role="Economic insecurity",
        direction_expected="Ambiguous; often procyclical",
    ),
    "SP.URB.TOTL.IN.ZS": IndicatorSpec(
        code="SP.URB.TOTL.IN.ZS",
        label="Urban population (% of total)",
        short_label="Urbanisation share",
        theoretical_role="Urbanisation / lifestyle",
        direction_expected="Rising",
    ),
    "SI.POV.GINI": IndicatorSpec(
        code="SI.POV.GINI",
        label="Gini index (0 = perfect equality)",
        short_label="Gini index",
        theoretical_role="Income inequality / perceived child costs",
        direction_expected="Ambiguous",
    ),
    "SH.XPD.CHEX.PC.CD": IndicatorSpec(
        code="SH.XPD.CHEX.PC.CD",
        label="Current health expenditure per capita (current US$)",
        short_label="Health expenditure per capita",
        theoretical_role="Cost of child-rearing / welfare state proxy",
        direction_expected="Rising",
    ),
}

# Outcome vs explanatory grouping for plotting
OUTCOME_CODE = "SP.DYN.TFRT.IN"
EXPLANATORY_CODES = [k for k in INDICATORS if k != OUTCOME_CODE]

OUTPUT_DIR = "output"
PAPER_FIGURES_DIR = "paper/figures"

# ---------------------------------------------------------------------------
# Regional samples — Asia, Middle East & North Africa, Sub-Saharan Africa.
# TFR-only panels for global context (World Bank WDI ISO3 codes).
# ---------------------------------------------------------------------------
REGIONAL_SAMPLES: dict[str, dict[str, str]] = {
    "Asia": {
        "CHN": "China",
        "IND": "India",
        "JPN": "Japan",
        "KOR": "Korea, Rep.",
        "IDN": "Indonesia",
        "BGD": "Bangladesh",
        "PAK": "Pakistan",
        "PHL": "Philippines",
        "VNM": "Vietnam",
        "THA": "Thailand",
        "MMR": "Myanmar",
        "NPL": "Nepal",
    },
    "Middle East & North Africa": {
        "EGY": "Egypt, Arab Rep.",
        "IRN": "Iran, Islamic Rep.",
        "IRQ": "Iraq",
        "JOR": "Jordan",
        "MAR": "Morocco",
        "SAU": "Saudi Arabia",
        "TUR": "Turkey",
        "TUN": "Tunisia",
        "LBN": "Lebanon",
        "YEM": "Yemen",
        "DZA": "Algeria",
        "QAT": "Qatar",
    },
    "Sub-Saharan Africa": {
        "NER": "Niger",
        "NGA": "Nigeria",
        "ETH": "Ethiopia",
        "KEN": "Kenya",
        "ZAF": "South Africa",
        "GHA": "Ghana",
        "TZA": "Tanzania",
        "COD": "Congo, Dem. Rep.",
        "UGA": "Uganda",
        "SEN": "Senegal",
        "MLI": "Mali",
        "CMR": "Cameroon",
    },
}

# Representative countries for regional trajectory panels (1960--2023).
REGIONAL_TRAJECTORIES: dict[str, list[str]] = {
    "Asia": ["CHN", "IND", "JPN", "BGD"],
    "Middle East & North Africa": ["IRN", "EGY", "TUR", "MAR"],
    "Sub-Saharan Africa": ["NER", "NGA", "KEN", "ETH"],
}

# Highlight in regional bar charts (diverse fertility regimes).
REGIONAL_HIGHLIGHTS: frozenset[str] = frozenset(
    {"CHN", "IND", "JPN", "KOR", "IRN", "EGY", "NER", "NGA", "ETH", "ZAF"}
)


def all_regional_countries() -> dict[str, str]:
    """Flat ISO3 → name map across all regional samples."""
    merged: dict[str, str] = {}
    for sample in REGIONAL_SAMPLES.values():
        merged.update(sample)
    return merged
