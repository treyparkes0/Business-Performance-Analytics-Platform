# Phase 3 plan: Excel workbook

This plan covers the Excel workbook. Creating `excel/Business_Performance_Analysis.xlsx` and the Phase 4 forecast math come later.

Checked against `main` at `70cc19e` (`Merge pull request #2 from treyparkes0/cursor/phase-2-audit-corrections-4243`). Column names below are from the SQL files and `src/bp_metrics.py` on that commit.

## What this phase builds later

One workbook, `excel/Business_Performance_Analysis.xlsx`, that reads five downloadable CSVs through Excel Power Query. A live Databricks connection from Excel is out of scope: it could not be set up. The CSVs are the view results, one file per view. Excel filters, labels, and formats. It does not recompute growth, margins, cash conversion, free cash flow, returns, ranks, or `Average_Rank`.

The metric definitions stay in the SQL views. The files Excel opens are a download of those results, produced from `build_views()` in `src/bp_metrics.py`, which is the tested local copy of that SQL. Regenerating the five CSVs is how the workbook gets new history. Excel does not reach the warehouse.

Phase 4 fills the forecast. This phase leaves Financial Forecast and Assumptions as empty placeholders.

## Current data the workbook will read

### Grain

Source file: `/agent/repos/Business-Performance-Analytics-Platform/data/processed/company_financials_wide.csv`

Warehouse table: `financial_analytics.clean.company_financials`

33 company-years. Company names in the data, which the dropdown must match exactly:

| Company | Ticker | Fiscal years |
|---|---|---|
| Microsoft | MSFT | 2021–2026 |
| Apple | AAPL | 2021–2025 |
| NVIDIA | NVDA | 2021–2026 |
| Adobe | ADBE | 2021–2025 |
| AMD | AMD | 2021–2025 |
| CrowdStrike | CRWD | 2021–2026 |

FY2025 is the last year present for all six companies. Dollars in the extract are raw USD (Apple FY2025 revenue is 416,161,000,000). Ratio columns are already decimals rounded to 3 places (`0.149` is 14.9%). Excel percent formats can display them. A formula that multiplies by 100 would scale them twice.

AMD has no `Total_Liabilities` fact in the long extract for any year. The view fills the amount as assets minus equity and sets `Total_Liabilities_Imputed`. That flag follows the missing fact. A wide-table update that already stored assets minus equity does not clear it. In this repo the wide CSV still has those AMD liabilities blank, and `data/processed/sec_company_financials_clean.csv` is not present, so `build_views()` treats the blank wide value as the missing fact. CrowdStrike `Short_Term_Debt` is blank for FY2021–FY2026; total debt treats that leg as 0 and `Short_Term_Debt_Reported` is false.

### The five SQL views

Definitions on `origin/main`:

- `/agent/repos/Business-Performance-Analytics-Platform/sql/growth_trend.sql`
- `/agent/repos/Business-Performance-Analytics-Platform/sql/performance.sql`
- `/agent/repos/Business-Performance-Analytics-Platform/sql/financial_health.sql`
- `/agent/repos/Business-Performance-Analytics-Platform/sql/peer_benchmarking.sql`
- `/agent/repos/Business-Performance-Analytics-Platform/sql/executive_summary.sql`

The notebook `CREATE OR REPLACE VIEW` cells match these files (`tests/test_sql_reconciliation.py`). The app loads the same five objects in `/agent/repos/Business-Performance-Analytics-Platform/src/data_source.py`:

| Query name to use in Excel | Databricks object | Rows |
|---|---|---|
| `growth_trend` | `financial_analytics.analytics.growth_trend` | 33, one per company-year |
| `performance` | `financial_analytics.analytics.performance` | 33 |
| `financial_health` | `financial_analytics.analytics.financial_health` | 33 |
| `peer_benchmarking` | `financial_analytics.analytics.peer_benchmarking` | 6, `Fiscal_Year` = 2025 only |
| `executive_summary` | `financial_analytics.analytics.executive_summary` | 6, each company's own latest year |

Import these five only. The app also exposes `company_performance`, `company_operations`, `company_cash_flow`, `company_financial_health`, and `peer_metrics`. Those are Python shapes of the five views (`assemble_views` in `src/bp_metrics.py`). They are not separate warehouse objects. Sheet formulas can take column subsets. They should not be a second import, and they should not be recalculated.

`docs/sql_metrics.md` matches this commit: nine-metric `Average_Rank`, NVIDIA FY2025 average 1.222, and the AMD flag tied to a missing liabilities fact. Follow that note, the SQL files, and the column lists below.

### Columns that matter

Names and order match `GROWTH_COLUMNS`, `PERFORMANCE_COLUMNS`, `HEALTH_COLUMNS`, `PEER_COLUMNS`, and `EXECUTIVE_COLUMNS` in `src/bp_metrics.py`. Keep this casing. `Current_ratio` and `debt_to_equity_ratio` are lowercase after the first word. Rank columns use `Rank`.

**growth_trend** — history of revenue growth. First year: `Growth_Rate` is blank. First two years: `Prior_Growth_Rate` and `Growth_Differential` are blank.

`Company`, `Fiscal_Year`, `Revenue`, `Net_Income`, `Growth_Rate`, `Prior_Growth_Rate`, `Growth_Differential`, `Net_Income_Margin_pct`

**performance** — profitability, efficiency, and cash. Joins the already-rounded `Growth_Rate` and `Net_Income_Margin_pct` from `growth_trend`. `Capital_Expenditures` is a positive spend. `Free_Cash_Flow` is operating cash flow minus that spend.

`Company`, `Fiscal_Year`, `Revenue`, `Gross_Profit`, `Net_Income`, `Operating_Income`, `Operating_Expenses`, `Cash_Flow_from_Operating_Activities`, `Capital_Expenditures`, `Growth_Rate`, `Net_Income_Margin_pct`, `Gross_Margin_pct`, `Operating_Margin_pct`, `Operating_Income_Growth`, `Net_Income_Growth`, `Operating_Expense_Growth`, `Operating_Expense_to_Revenue`, `Revenue_Growth_Minus_Opex_Growth`, `Operating_Cash_Flow_Margin_pct`, `Operating_Cash_Flow_Growth`, `Cash_Conversion_Ratio`, `Cash_Conversion_Meaningful`, `Free_Cash_Flow`, `Free_Cash_Flow_Margin_pct`

`Cash_Conversion_Ratio` is operating cash flow / net income, rounded to 3 decimals, blank when net income is 0. `Cash_Conversion_Meaningful` is false when net income is zero or negative, or when the absolute unrounded ratio is greater than 5. A ratio of exactly 5 stays meaningful. In this extract, CrowdStrike is false for every year FY2021–FY2026, including FY2025. Display `n/m` when the flag is false. Keep the raw ratio available. Do not recompute the flag.

**financial_health** — liquidity, leverage, and returns.

`Company`, `Fiscal_Year`, `Total_Assets`, `Total_Liabilities`, `Total_Liabilities_Imputed`, `Total_Stockholders_Equity`, `Total_Current_Assets`, `Total_Current_Liabilities`, `Current_ratio`, `Total_Debt`, `Short_Term_Debt_Reported`, `Long_Term_Debt_Reported`, `debt_to_equity_ratio`, `Liabilities_to_Assets`, `ROA_Ending`, `ROE_Ending`, `ROA_Avg`, `ROE_Avg`, `ROA_Uses_Ending_Balance`, `ROE_Uses_Ending_Balance`, `ROA`, `ROE`, `Cash_Flow_from_Operating_Activities`

`ROA` and `ROE` are the primary returns: average of the current and prior balance, lagged by ticker. Ending balances are used only when there is no prior year. That is each company's FY2021 here, and both `*_Uses_Ending_Balance` flags are true on those rows. `ROA_Avg` and `ROE_Avg` are blank when there is no prior year. `ROA_Ending` and `ROE_Ending` always use the ending balance. FY2025 ranks use `ROA` and `ROE`, so they use the average. Apple FY2025 primary ROE is high because buybacks shrink equity; read it next to ROA.

`Total_Liabilities_Imputed` is true for AMD company-years with no `Total_Liabilities` fact. A reported fact is not imputed, even when the amount equals assets minus equity. The sheet should display the flag from the view.

**peer_benchmarking** — six rows, FY2025 only. Value column sits next to its rank. Sorted by `Average_Rank`, then company.

`Company`, `Fiscal_Year`, `Growth_Rate`, `Growth_Rate_Rank`, `Operating_Margin_pct`, `Operating_Margin_Rank`, `Net_Income_Margin_pct`, `Net_Income_Margin_Rank`, `Operating_Expense_to_Revenue`, `Operating_Expense_to_Revenue_Rank`, `Operating_Cash_Flow_Margin_pct`, `Operating_Cash_Flow_Margin_Rank`, `Current_ratio`, `Current_Ratio_Rank`, `debt_to_equity_ratio`, `Debt_to_Equity_Rank`, `ROA`, `ROA_Rank`, `ROE`, `ROE_Rank`, `Average_Rank`

Nine ranks, equal weight, mean rounded to 3 decimals. Higher is better for growth, operating margin, net income margin, operating-cash-flow margin, current ratio, ROA, and ROE. Lower is better for operating expense / revenue and debt-to-equity. Ties use `RANK()` (shared best rank, next rank skipped). Missing values rank last and tie with each other. Growth differential, operating-expense growth, and liabilities-to-assets are not in this view and are not in `Average_Rank`.

Python check on the CSV path, for a refresh sanity check after the views exist. Do not paste these in as values:

| Company | Average_Rank |
|---|---|
| NVIDIA | 1.222 |
| Microsoft | 3.111 |
| AMD | 3.889 |
| Adobe | 3.889 |
| Apple | 4.000 |
| CrowdStrike | 4.889 |

**executive_summary** — one row per company at that company's latest fiscal year. Ranks join on company only, so Microsoft, NVIDIA, and CrowdStrike at FY2026 still carry the FY2025 ranks. `Benchmark_Fiscal_Year` is 2025 on every row. Rank columns are prefixed `FY2025_`. The row's own `ROA` and `ROE` are that latest year, not a substitute for the FY2025 benchmark.

`Company`, `Fiscal_Year`, `Benchmark_Fiscal_Year`, `Revenue`, `Growth_Rate`, `Prior_Growth_Rate`, `Growth_Differential`, `Gross_Margin_pct`, `Operating_Margin_pct`, `Net_Income_Margin_pct`, `Operating_Income_Growth`, `Net_Income_Growth`, `Operating_Expense_Growth`, `Operating_Expense_to_Revenue`, `Revenue_Growth_Minus_Opex_Growth`, `Operating_Cash_Flow_Margin_pct`, `Operating_Cash_Flow_Growth`, `Cash_Conversion_Ratio`, `Cash_Conversion_Meaningful`, `Free_Cash_Flow`, `Free_Cash_Flow_Margin_pct`, `Current_ratio`, `debt_to_equity_ratio`, `Liabilities_to_Assets`, `ROA`, `ROE`, `ROA_Ending`, `ROE_Ending`, `ROA_Avg`, `ROE_Avg`, `ROA_Uses_Ending_Balance`, `ROE_Uses_Ending_Balance`, `Total_Liabilities_Imputed`, `Short_Term_Debt_Reported`, `Long_Term_Debt_Reported`, `FY2025_Growth_Rate_Rank`, `FY2025_Operating_Margin_Rank`, `FY2025_Net_Income_Margin_Rank`, `FY2025_Operating_Expense_to_Revenue_Rank`, `FY2025_Operating_Cash_Flow_Margin_Rank`, `FY2025_Current_Ratio_Rank`, `FY2025_Debt_to_Equity_Rank`, `FY2025_ROA_Rank`, `FY2025_ROE_Rank`, `FY2025_Average_Rank`

## Workbook structure

File to create later: `excel/Business_Performance_Analysis.xlsx` in the repo. It does not exist yet. The file holds no warehouse credentials.

Nine sheets, in this order:

1. Executive Dashboard
2. Financial Forecast
3. Operating Performance
4. Cash Flow Analysis
5. Financial Health
6. Peer Benchmarking
7. Company Analysis
8. Assumptions
9. Data Connections

### Company dropdown

One named cell, `SelectedCompany`, on the Executive Dashboard (and repeated as a linked cell on the company sheets so the choice is visible). Data validation list, in this order:

Microsoft, Apple, NVIDIA, Adobe, AMD, CrowdStrike

Store that list on Data Connections as a named range `CompanyList`. The validation source is `=CompanyList`. Values must equal the `Company` column. Tickers are not the selector.

Changing `SelectedCompany` must update the individual-company sheets immediately, through `FILTER` / `XLOOKUP` (or `CHOOSECOLS`) against the loaded tables. It must not require a Power Query refresh. Refresh is for new source data only.

Sheets that follow the dropdown:

- Executive Dashboard. One company, the row from `executive_summary` for `SelectedCompany`.
- Financial Forecast
- Operating Performance
- Cash Flow Analysis
- Financial Health
- Company Analysis
- Assumptions, for the company label on the placeholder

The sheet that always shows all six companies is Peer Benchmarking. It ignores the dropdown. FY2025 only, because that filter is already inside the view. The raw tables on Data Connections also keep every company, so the dropdown can filter them. The Executive Dashboard does not list the other five.

## Sheet-by-sheet layout

Data Connections holds the five Excel tables. Every analytical number on the other sheets is a formula pointing at those tables or at another sheet's formula. No typed historical numbers. No Power Query `M` that divides, ranks, or imputes.

Suggested table names: `tblGrowth`, `tblPerformance`, `tblHealth`, `tblPeers`, `tblExecutive`.

Display: dollars in billions via a custom format or a display formula that only scales (`value/1e9`) and is labeled `$ billions`. Ratios use a percent format on the stored decimal. Ranks are integers. `Average_Rank` shows 3 decimals. Blank stays blank. Early-year growth blanks are not zeros.

### 1. Executive Dashboard

Header: `SelectedCompany`.

Selected-company block, one row from `tblExecutive` where `Company` equals `SelectedCompany`:

- `Fiscal_Year` (that company's latest year) and `Benchmark_Fiscal_Year` (always 2025)
- `Revenue`, `Growth_Rate`, `Growth_Differential`
- `Gross_Margin_pct`, `Operating_Margin_pct`, `Net_Income_Margin_pct`
- `Operating_Cash_Flow_Margin_pct`, `Free_Cash_Flow`, `Free_Cash_Flow_Margin_pct`
- Cash conversion display: `n/m` when `Cash_Conversion_Meaningful` is false, otherwise `Cash_Conversion_Ratio`
- `Current_ratio`, `debt_to_equity_ratio`, `ROA`, `ROE`
- `FY2025_Average_Rank`

Caption under the block: ranks are the FY2025 peer ranks even when `Fiscal_Year` is 2026. Microsoft, NVIDIA, and CrowdStrike are FY2026 on this row. AMD, Adobe, and Apple are FY2025.

This sheet shows that one company. The other five stay on Peer Benchmarking and in the Data Connections tables. Do not add an all-company strip here.

### 2. Financial Forecast

Placeholder. Title bound to `SelectedCompany`. No driver math, no projected values, no growth-rate formulas.

Layout to leave empty for Phase 4:

- A line that shows the company's latest actual `Fiscal_Year` from `tblExecutive` (a read-only label, so the model knows the last historical year).
- Three blank columns headed `Year 1`, `Year 2`, `Year 3`. Do not lock those to 2026–2028 or to latest+1 until the horizon decision in Phase 4.
- A short note: historical metrics stay on the Power Query tables. This sheet will hold forecast outputs only.

### 3. Operating Performance

Follows the dropdown. All fiscal years for that company, sorted by `Fiscal_Year`. Three stacked tables, still formulas:

Growth, from `tblGrowth`: `Fiscal_Year`, `Revenue`, `Net_Income`, `Growth_Rate`, `Prior_Growth_Rate`, `Growth_Differential`, `Net_Income_Margin_pct`

Profitability, from `tblPerformance`: `Fiscal_Year`, `Gross_Profit`, `Gross_Margin_pct`, `Operating_Income`, `Operating_Margin_pct`, `Net_Income`, `Net_Income_Margin_pct`, `Operating_Income_Growth`, `Net_Income_Growth`

Efficiency, from `tblPerformance`: `Fiscal_Year`, `Revenue`, `Growth_Rate`, `Operating_Expenses`, `Operating_Expense_Growth`, `Operating_Expense_to_Revenue`, `Revenue_Growth_Minus_Opex_Growth`

`Growth_Differential` is only on `growth_trend`. Do not derive it from the rounded rates on the sheet.

### 4. Cash Flow Analysis

Follows the dropdown. All years from `tblPerformance`:

`Fiscal_Year`, `Revenue`, `Net_Income`, `Cash_Flow_from_Operating_Activities`, `Operating_Cash_Flow_Margin_pct`, `Operating_Cash_Flow_Growth`, `Cash_Conversion_Ratio`, `Cash_Conversion_Meaningful`, a display column that shows `n/m` when the flag is false, `Capital_Expenditures`, `Free_Cash_Flow`, `Free_Cash_Flow_Margin_pct`

Note on the sheet: capex is a positive spend, and free cash flow is already computed. A chart of the raw CrowdStrike conversion ratio will swamp the axis; chart the display column or omit the ratio from the chart.

### 5. Financial Health

Follows the dropdown. All years from `tblHealth`:

`Fiscal_Year`, `Total_Assets`, `Total_Liabilities`, `Total_Liabilities_Imputed`, `Total_Stockholders_Equity`, `Total_Current_Assets`, `Total_Current_Liabilities`, `Current_ratio`, `Total_Debt`, `Short_Term_Debt_Reported`, `Long_Term_Debt_Reported`, `debt_to_equity_ratio`, `Liabilities_to_Assets`, `ROA`, `ROE`, `ROA_Avg`, `ROE_Avg`, `ROA_Ending`, `ROE_Ending`, `ROA_Uses_Ending_Balance`, `ROE_Uses_Ending_Balance`

Static notes, not formulas: primary `ROA` and `ROE` use average balances except FY2021; Apple ROE next to ROA; AMD liabilities imputed only when the flag is true; CrowdStrike short-term debt is unreported and treated as 0.

### 6. Peer Benchmarking

Always all six companies. Source is `tblPeers` with no company filter. `Fiscal_Year` is 2025 on every row. Column order is the view order above, value beside rank. Sort is the view's sort (`Average_Rank`, then company). Do not run `RANK` in Excel.

A one-line direction key: higher is better for the seven growth, margin, cash, liquidity, and return metrics; lower is better for operating expense / revenue and debt-to-equity. `Average_Rank` is the equal-weight mean of those nine ranks.

### 7. Company Analysis

Follows the dropdown. One company, composed from the other sheets so there is a single filter:

- Identity from `tblExecutive`: company, latest `Fiscal_Year`, `Benchmark_Fiscal_Year`
- Latest-year snapshot: the same fields as the Executive Dashboard selected block
- FY2025 rank card from `tblPeers` for that company, including `Average_Rank`. Show this card even when the latest year is 2026. Do not copy those ranks onto every historical year.
- History: links to the Operating Performance, Cash Flow Analysis, and Financial Health rows for `SelectedCompany`

No second set of calculations.

### 8. Assumptions

Placeholder. Company label linked to `SelectedCompany`. An empty input grid with headers `Driver`, `Year 1`, `Year 2`, `Year 3`, and several blank rows. Do not name the drivers and do not put historical actuals in the input cells. A note: Phase 4 fills this grid; historical metrics are read from the views.

### 9. Data Connections

The five tables, plus `CompanyList`, plus the refresh write-up below. Hide the tables from casual printing if needed; do not hide them so thoroughly that a refresh cannot be checked. A small status area with query name, CSV file name, expected row count (33, 33, 33, 6, 6), and a manual "last checked" cell is enough. Power Query's refresh timestamp can sit beside it.

## Downloadable CSVs

Excel does not connect to Databricks. There is no Azure Databricks connector, no ODBC DSN, and no token in the workbook.

Five files, one per view. They are not `company_financials_wide.csv`. Pointing Power Query at that wide extract and calculating ratios would re-implement SQL. Five files also keep each sheet on the view that already owns those columns. One combined download would force Excel to split and recompute.

Later export location, not created in this planning step:

- `excel/exports/growth_trend.csv`
- `excel/exports/performance.csv`
- `excel/exports/financial_health.csv`
- `excel/exports/peer_benchmarking.csv`
- `excel/exports/executive_summary.csv`

Headers must match the column lists above, including order and casing. Produce them from `build_views()` in `src/bp_metrics.py`. That function reads `data/processed/company_financials_wide.csv` and, when the file exists, `data/processed/sec_company_financials_clean.csv` for the AMD liabilities flag. It applies the same formulas as the SQL files. Ship the five CSVs next to the workbook so someone can download the set and open it without a warehouse login.

A later Databricks SQL-editor download can replace a file only when its header matches the list. Until the notebook `CREATE OR REPLACE VIEW` cells have been run, a warehouse download is still the pre-Phase-2 view. Do not use that download. The Python export is the Phase 2 result the workbook should load.

Power Query, in Microsoft 365 Excel desktop: Data, Get Data, From File, From Text/CSV. One query per file, named `growth_trend`, `performance`, `financial_health`, `peer_benchmarking`, and `executive_summary`. Load each to the matching table on Data Connections. Set types only enough to keep company as text, year and ranks as whole numbers, flags as boolean, and metrics as decimal. CSV flags arrive as `True` / `False` text; type them as logical values. Do not add calculated columns. Do not add a Databricks source beside these queries.

SQL `ROUND` and Python rounding were not compared on a live warehouse in Phase 2. These CSVs are the Python result. A later warehouse download could differ by 0.001 on a half value. Do not correct either one inside Excel.

## How refresh works

1. Regenerate the five CSVs from `build_views()` after the metric definitions change, and replace the files in `excel/exports/`. Leave the file names the same.
2. Open the workbook in Excel desktop.
3. Data, Refresh All. That re-reads the CSVs. Replacing a file without Refresh All leaves the old table in the workbook. There is no warehouse sign-in.
4. Check row counts: 33, 33, 33, 6, 6.
5. Check `tblPeers` is entirely `Fiscal_Year` 2025, has `Operating_Expense_to_Revenue_Rank`, and does not have `Growth_Differential_Rank`.
6. Check `tblExecutive` has `Benchmark_Fiscal_Year` 2025 and `FY2025_Average_Rank` on all six rows, including the three companies whose `Fiscal_Year` is 2026.
7. Check `tblHealth` has `ROA`, `ROE`, `ROA_Avg`, `ROE_Avg`, `ROA_Ending`, `ROE_Ending`, and the flag columns.
8. Compare `Average_Rank` order to the table above (NVIDIA, Microsoft, AMD and Adobe at 3.889, Apple, CrowdStrike). Investigate a mismatch in the export. Do not overwrite the query with typed ranks.
9. Change `SelectedCompany` and confirm Operating Performance, Cash Flow Analysis, Financial Health, Company Analysis, and the dashboard's selected block change without another refresh. Peer Benchmarking stays at six companies.

The dropdown and Refresh All do different jobs. The dropdown filters tables already loaded. Refresh All re-reads the five CSVs.

## Left for Phase 4

Three-year driver-based forecast. This plan does not choose drivers, formulas, or scenarios.

Phase 4 fills Financial Forecast and Assumptions. It may read historical metrics from the tables as anchors. It must not re-implement those metrics. Forecast outputs live on the forecast sheet. They are not written back into the five views.

Placeholder columns stay `Year 1`, `Year 2`, `Year 3` so this phase does not freeze the horizon. Phase 4 still has to decide whether those years are three years after each company's own latest year (Microsoft 2027–2029, Apple 2026–2028) or one shared set of years. A shared 2026–2028 window overlaps reported years for Microsoft, NVIDIA, and CrowdStrike.

## Risks

- Excel never reads the warehouse. The live Databricks views stay stale until the notebook cells are run, so a CSV downloaded from the SQL editor before that run is the old rank set. Generate the workbook files with `build_views()` instead. The column check in the refresh steps catches an old header if one is swapped in later.
- `Total_Liabilities_Imputed` follows a missing AMD liabilities fact, not a blank cell in the wide table. The local export has no long facts file, so a blank wide value is what sets the flag. After someone adds `sec_company_financials_clean.csv`, regenerate the health CSV. Trust the flag column. Do not re-impute in Excel.
- Python and SQL can differ by 0.001 on a value that lands on a half. Phase 2 did not execute the view SQL. The workbook shows the Python export. Do not reconcile that inside Excel.
- The workbook holds no Databricks token. Keep it that way. `.gitignore` already covers `.env` and Streamlit `secrets.toml`.
- `executive_summary` mixes FY2026 and FY2025 on purpose. Ranking "latest year" across the history tables would rebuild the mixed-year comparison Phase 2 removed. Peer Benchmarking must stay on `tblPeers`.
- Copying `FY2025_*` ranks onto every year of a company history would mislabel FY2021–FY2024 and FY2026.
- Blank growth and blank cash-conversion flags are real. Excel averages and charts that treat blanks as zero will distort the first year.
- CrowdStrike's raw cash-conversion ratio is about -90.7 in FY2025. Chart the `n/m` display, not the raw ratio.
- CSV years, ranks, and `True` / `False` flags arrive as text. Set the Power Query types. Do not recompute the metric to force a type.
- This environment has no Excel desktop. The build phase has to be verified in Excel itself: dropdown, Refresh All, and the column checks above.

## Decisions

**Settled.** Excel cannot connect to Databricks. The workbook loads five downloadable CSVs through Power Query, exported from `build_views()`. No live warehouse connection in the file.

**Settled.** The Executive Dashboard shows the selected company only. Peer Benchmarking is the all-company sheet and stays unfiltered at FY2025.

Phase 4 still chooses the forecast horizon. Year labels on the placeholder stay `Year 1`, `Year 2`, `Year 3`. The shared-year versus latest-plus-three choice is not part of this build.

## Build sequence

1. Export the five frames from `build_views()` to `excel/exports/`. Do not export the wide file as a substitute, and do not download the views from Databricks until those notebook cells have been run.
2. Create the workbook with the nine sheet tabs, `CompanyList`, and `SelectedCompany` data validation.
3. Add the five From Text/CSV queries. Load to `tblGrowth`, `tblPerformance`, `tblHealth`, `tblPeers`, `tblExecutive` on Data Connections. No metric steps in M.
4. Peer Benchmarking from `tblPeers`, unfiltered.
5. Operating Performance, Cash Flow Analysis, and Financial Health with `FILTER` on `SelectedCompany`.
6. Display rules only: percent formats, billions labels, `n/m` from `Cash_Conversion_Meaningful`.
7. Executive Dashboard as the one selected-company row from `tblExecutive`. No all-company strip.
8. Company Analysis as links to those sheets plus the FY2025 rank card.
9. Empty Financial Forecast and Assumptions placeholders.
10. Write the refresh steps on Data Connections. Run Refresh All. Run the column and row-count checks. Change the dropdown across all six companies, including a FY2026 company (Microsoft) and a FY2025 company (Apple). Confirm the dashboard follows the company and Peer Benchmarking does not change.
11. Stop. Phase 4 fills the forecast.
