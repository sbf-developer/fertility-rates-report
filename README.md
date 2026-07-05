# Why Does Fertility Fall?

Research report and reproducible analysis of global fertility decline, with harmonised World Bank WDI data, literature synthesis, and a LaTeX book-style write-up.

**Author:** Scott Brodie Forsyth

## Contents

- `main.py` — fetch WDI data, generate figures and LaTeX tables
- `paper/` — report source (`main.tex`), bibliography, compiled PDF, figure PDFs
- `output/` — cached WDI CSV panels and preview figures

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

Compile the report from `paper/`:

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The compiled report is `paper/main.pdf`.

## Report structure

1. Introduction and evidence taxonomy  
2. High-income economies (US, UK, Israel)  
3. Asia, MENA, Sub-Saharan Africa  
4. Macroeconomic co-movement (US/UK)  
5. Proposed mechanisms  
6. Reversing fertility decline (policy evaluation)  
7. Data and methods  
8. Conclusion and open questions  

Data sources: [World Bank WDI](https://data.worldbank.org/) (via API), published survey summaries (GGS-II, JPPI), and peer-reviewed literature cited in `paper/references.bib`.
