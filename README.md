# Household Spending Patterns in Western Mexico, 2016–2024

Exploratory analysis of how households in Jalisco, Colima, Nayarit, and Michoacán distribute their
spending across six categories (food, clothing and footwear, health, transport, education, leisure),
and how these patterns differ by household composition, income level, indigenous status, and the
education level of the household head.

## Data source

Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH), New Series, editions 2016, 2018, 2020,
2022, and 2024. Produced by INEGI (Mexico): https://www.inegi.org.mx/programas/enigh/
Access date: *[add date]*. Check INEGI's terms of use before redistributing the original files.

The ENIGH Seasonal 2020 is a different survey and is **not** used.

Only two tables per edition are used: `concentradohogar` (one row per household) and `poblacion`
(one row per person).

## Repository structure

```
├── README.md
├── requirements.txt
├── .gitignore
├── 02_limpiar.py        cleaning: reads the raw INEGI CSVs, filters the four states
├── 03_unir.py           merge and derived variables -> data/processed/hogares_2016_2024.csv
├── 05_eda.py            exploratory analysis: figures/ and tablas/
├── data/
│   ├── raw/             original INEGI files (not tracked by git)
│   ├── interim/         output of 02_limpiar.py (not tracked)
│   └── processed/       hogares_2016_2024.csv (one row per household-year)
├── docs/                INEGI data dictionaries and catalogs
├── figuras/             figures (one folder per year, plus the cross-year figures)
└── tablas/              tables behind each figure
```

## How to reproduce

1. Install dependencies: `pip install -r requirements.txt`
2. Download the five ENIGH New Series editions from INEGI (CSV format) and place the unzipped folders
   under `data/raw/` (or in the project root; the scripts find them by file name).
3. Run, in order:
   ```
   python 02_limpiar.py
   python 03_unir.py
   python 05_eda.py
   ```

## Main decisions

- **Region:** states 06 (Colima), 14 (Jalisco), 16 (Michoacán), and 18 (Nayarit).
- **Weighting:** all results use the survey expansion factor (`factor`).
- **Spending shares:** comparisons use the share of monetary current spending (`gasto_mon`) devoted to
  each category. Amounts are in current pesos of each year (not deflated), so they are not compared
  across years.
- **Leisure** = `esparci` + `paq_turist` (checked: `educa_espa` = `educacion` + `esparci` + `paq_turist`
  in every edition).
- **Income deciles** are computed with weighted current income (`ing_cor`) within each edition and
  the four states (regional deciles, not national).
- **Household composition:** INEGI household class; "Compuesto" and "Corresidente" are merged because of
  their small samples.
- **Education:** education level of the household head (`educa_jefe`), grouped into five levels by the
  highest level completed.
- **Indigenous household:** the household head or their partner self-identifies as indigenous (`etnia`).
- **Caveat:** the share of households identified as indigenous drops sharply between 2020 and 2022 in
  some states. The cause was not identified, so indigenous comparisons are read within each year only.

## Limitations

Repeated cross-sections (not a panel); only five biennial editions; no confidence intervals; results
describe associations, not causal effects.

## Main output

`data/processed/hogares_2016_2024.csv`: one row per household and edition, with the design variables
(`factor`, `upm`, `est_dis`), spending by category, income, household characteristics, and the derived
variables (`ocio`, `decil`, `clase_hogar_agr`, `escolaridad_jefe`, and the indigenous-household flags).

## Author

*[Your name]*
