"""Write country-level snapshot table for LaTeX (no correlation nonsense)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import OUTCOME_CODE


def build_snapshot(wide: pd.DataFrame, year: int) -> tuple[pd.DataFrame, int]:
    """One common year for all countries when possible."""
    snapshot = wide.loc[wide["year"] == year].copy()
    n_tfr = snapshot[OUTCOME_CODE].notna().sum()
    if n_tfr >= 5:
        return snapshot, year

    from analyze import latest_country_snapshot

    snapshot = latest_country_snapshot(wide)
    actual = int(snapshot["year"].median()) if not snapshot.empty else year
    return snapshot, actual


def write_latex_country_table(
    wide: pd.DataFrame,
    year: int,
    paper_dir: Path,
) -> int:
    """Country | TFR table for the paper. Returns snapshot year used."""
    snapshot, actual_year = build_snapshot(wide, year)
    df = snapshot[["country_name", "country_code", OUTCOME_CODE]].dropna()
    df = df.sort_values(OUTCOME_CODE, ascending=False)
    n_countries = len(df)
    above_replacement = (df[OUTCOME_CODE] >= 2.1).any()
    if above_replacement:
        caption_note = (
            f"Most countries remain below replacement (2.1); "
            f"Israel is a notable exception among high-income economies."
        )
    else:
        caption_note = "All values below replacement (2.1)."

    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "snapshot_meta.tex").write_text(
        f"\\newcommand{{\\SnapshotYear}}{{{actual_year}}}\n"
        f"\\newcommand{{\\SnapshotN}}{{{n_countries}}}\n",
        encoding="utf-8",
    )

    rows: list[str] = []
    for _, row in df.iterrows():
        name = str(row["country_name"]).replace("&", "\\&")
        tfr = row[OUTCOME_CODE]
        rows.append(f"    {name} & {tfr:.2f} \\\\")

    body = "\n".join(rows)
    table = f"""\\begin{{table}}[H]
  \\centering
  \\caption{{Total fertility rate by country (year~{actual_year}). {caption_note}}}
  \\label{{tab:countries}}
  \\small
  \\begin{{tabular}}{{lr}}
    \\toprule
    \\textbf{{Country}} & \\textbf{{TFR}} \\\\
    \\midrule
{body}
    \\bottomrule
  \\end{{tabular}}
\\end{{table}}
"""
    (paper_dir / "table_countries.tex").write_text(table, encoding="utf-8")
    return actual_year
