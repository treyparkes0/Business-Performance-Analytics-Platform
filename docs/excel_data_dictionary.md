# Excel columns

The workbook imports six CSV files from `excel/source`. Those files hold the historical numbers. The forecast on Financial Forecast, and the working sheet Calc, are the only calculations Excel adds.

`peer_metrics` is a join of the history views for the peer page. It is not its own SQL view. The other five files match `growth_trend`, `performance`, `financial_health`, `peer_benchmarking`, and `executive_summary`.

## Company identifiers

The six analysis tables key on `Company` text. They do not carry `Ticker` or `CIK`. `financial_health` uses `Ticker` only to lag assets and equity, then drops it. In this file each company has one ticker, so a lag by ticker matches a lag by company.

The company selector must use these `Company` strings exactly.

| Company | Ticker | CIK (text, 10 digits) | Fiscal years | Rows |
|---|---|---|---|---|
| AMD | AMD | 0000002488 | 2021–2025 | 5 |
| Adobe | ADBE | 0000796343 | 2021–2025 | 5 |
| Apple | AAPL | 0000320193 | 2021–2025 | 5 |
| CrowdStrike | CRWD | 0001535527 | 2021–2026 | 6 |
| Microsoft | MSFT | 0000789019 | 2021–2026 | 6 |
| NVIDIA | NVDA | 0001045810 | 2021–2026 | 6 |

33 company-years. FY2025 is the last year present for every company. Latest year is FY2025 for AMD, Adobe, and Apple, and FY2026 for CrowdStrike, Microsoft, and NVIDIA.

CIK is stored with leading zeros in the wide CSV. If a company list is imported, keep CIK as text. The views themselves do not include it.

## Where the actual values are

Historical dollars and ratios are on `growth_trend`, `performance`, and `financial_health`. `peer_metrics` is every fiscal year's underlying peer values, joined from those views with no new formula. `peer_benchmarking` is the FY2025 rank table: six rows, each of nine metrics stored next to its rank.

`peer_benchmarking` has no revenue, gross profit, operating expenses, net income, cash flow, capital expenditures, free cash flow, balance-sheet dollars, gross margin, growth differential, or liabilities-to-assets.

| Need | Source | Grain |
|---|---|---|
| Reported dollars and the ratios calculated from them, all years | `performance` for the income statement and cash flow; `financial_health` for the balance sheet, liquidity, leverage, and returns; `growth_trend` for revenue, net income, and growth | 33 company-years |
| Underlying peer values for every fiscal year | `peer_metrics` | 33 company-years |
| FY2025 comparison, value beside rank | `peer_benchmarking` | 6 companies, fiscal year 2025 only |
| One latest-year row per company, with FY2025 ranks attached by company | `executive_summary` | 6 companies |

When Databricks is the import path, query the five views. Build `peer_metrics` by selecting and joining those imported columns. Do not recalculate the ratios in Excel.

Columns only on `peer_metrics`, relative to `peer_benchmarking`: `Revenue`, `Growth_Differential`, `Gross_Margin_pct`, `Liabilities_to_Assets`.

Columns only on `peer_benchmarking`, relative to `peer_metrics`: the nine rank columns and `Average_Rank`.

## Units and Excel types

Dollar columns are US dollars, unscaled. Apple FY2025 revenue in the SEC check is 416,161,000,000. Do not divide by one million inside the import.

Columns whose names end in `_pct`, plus `Growth_Rate`, `Prior_Growth_Rate`, `Growth_Differential`, `Operating_Income_Growth`, `Net_Income_Growth`, `Operating_Expense_Growth`, `Revenue_Growth_Minus_Opex_Growth`, `ROA`, `ROE`, `ROA_Ending`, `ROE_Ending`, `ROA_Avg`, `ROE_Avg`, and `Liabilities_to_Assets`, are decimal ratios rounded to 3 decimal places. `0.149` means 14.9 percent. They are not already multiplied by 100. A percent format may display them. Do not divide or multiply them again.

`Current_ratio`, `debt_to_equity_ratio`, and `Cash_Conversion_Ratio` are multiples rounded to 3 decimal places. Show them as `0.000`, the same way the Streamlit app does. Do not format them as percents. Debt-to-equity of `0.167` is 0.167 dollars of debt per dollar of equity, not 16.7 percent. Cash conversion can be large or negative (CrowdStrike FY2025 is -90.659) and is paired with `Cash_Conversion_Meaningful`.

Rank columns are integers. Tied values share the best rank and the next rank is skipped (`RANK()`, pandas `method="min"`). Missing values rank last and tie with each other. `Average_Rank` and `FY2025_Average_Rank` are the equal-weight mean of the nine ranks, rounded to 3 decimal places. A lower average is better.

Boolean flags must stay boolean. Blank cells must stay blank. The only intentional zero-fill already applied upstream is `Total_Debt`, which uses `COALESCE` on a missing short-term or long-term leg. That result is not a source fact. `Short_Term_Debt_Reported` and `Long_Term_Debt_Reported` say whether the source leg was present. A reported zero stays reported. Seven source rows have short-term debt of exactly 0: AMD 2022, AMD 2024, Adobe 2021, Adobe 2023, Adobe 2025, NVIDIA 2022, NVIDIA 2025. Those are not the CrowdStrike gaps.

## Source gaps and flags

These nulls are source or lag gaps. Leave them null.

| Gap | Rows | What stays null | Flag that must travel with the import |
|---|---|---|---|
| No prior year | Every company, FY2021 | `Growth_Rate`, income and cash-flow growth rates, `ROA_Avg`, `ROE_Avg` | `ROA_Uses_Ending_Balance` and `ROE_Uses_Ending_Balance` are true. Primary `ROA` and `ROE` use the ending balance for that year only |
| No two prior years | Every company, FY2021 and FY2022 | `Prior_Growth_Rate`, `Growth_Differential` | None |
| Operating expenses missing from SEC `OperatingExpenses` | AMD 2021–2022, Microsoft 2021–2022 | `Operating_Expenses`, `Operating_Expense_to_Revenue`. Growth of that ratio is also null for AMD 2023 and Microsoft 2023 because the prior year is missing | None. Do not fill expenses |
| Capital expenditures missing | NVIDIA 2021 | `Capital_Expenditures`, `Free_Cash_Flow`, `Free_Cash_Flow_Margin_pct` | None |
| Short-term debt not reported | CrowdStrike FY2021–FY2026 | The source field is null. `Total_Debt` equals long-term debt because the missing leg is treated as 0 | `Short_Term_Debt_Reported` is false. `Long_Term_Debt_Reported` is true on every row in this file |
| Total liabilities not tagged | AMD FY2021–FY2025 | The wide CSV is null. The view fills `Total_Liabilities` with assets minus equity | `Total_Liabilities_Imputed` is true for those five AMD rows and false for every other company-year |

`Total_Liabilities_Imputed` follows provenance, not the current wide-table null. SQL left-joins `financial_analytics.clean.sec_company_financials_clean` and flags AMD company-years with no `Metric = 'Total_Liabilities'` row. A reported fact is not imputed, even when the amount equals assets minus equity. The extract in this repository, `data/processed/sec_company_financials_clean.csv`, has 1,657 rows and no AMD `Total_Liabilities` fact, so those five AMD years stay flagged. Excel must import the flag. It must not impute again.

`Cash_Conversion_Meaningful` is false when net income is zero or negative, or when the absolute unrounded operating-cash-flow / net-income ratio is greater than 5. A ratio of exactly 5 stays true. A null input would leave the flag null. In this file the flag is never null. It is false for all six CrowdStrike years:

| Company | Fiscal year | Cash conversion ratio | Why the flag is false |
|---|---:|---:|---|
| CrowdStrike | 2021 | -3.849 | Net income is negative |
| CrowdStrike | 2022 | -2.448 | Net income is negative |
| CrowdStrike | 2023 | -5.135 | Net income is negative, and the absolute ratio is also above 5 |
| CrowdStrike | 2024 | 16.157 | Absolute ratio is above 5 |
| CrowdStrike | 2025 | -90.659 | Net income is negative, and the absolute ratio is also above 5 |
| CrowdStrike | 2026 | -9.922 | Net income is negative, and the absolute ratio is also above 5 |

Primary `ROA` and `ROE` are the columns used in peer ranking. They use the average of the current and prior balance, `(current + prior) / 2`, when a prior year exists. `ROA_Ending` and `ROE_Ending` always use the ending balance. `ROA_Avg` and `ROE_Avg` are null when there is no prior year. Apple's high ROE is read next to ROA because buybacks reduce equity. That is a reading note, not an extra column.

## View profiles

Row counts from `build_views()`: `growth_trend` 33, `performance` 33, `financial_health` 33, `peer_benchmarking` 6, `executive_summary` 6, `peer_metrics` 33.

FY2025 `Average_Rank`, lower is better: NVIDIA 1.222, Microsoft 3.111, AMD 3.889, Adobe 3.889, Apple 4.000, CrowdStrike 4.889.

`executive_summary.Fiscal_Year` is the company's own latest year. `Benchmark_Fiscal_Year` is 2025 on every row. Rank columns are prefixed `FY2025_` and are attached on company alone, so the three FY2026 rows still carry FY2025 ranks. Their growth, margin, cash, and return values are FY2026 values.

### growth_trend

Warehouse: `financial_analytics.analytics.growth_trend`. One row per company-year.

| Column | Excel type | Nulls in this file |
|---|---|---|
| Company | text | 0 |
| Fiscal_Year | integer | 0 |
| Revenue | USD | 0 |
| Net_Income | USD | 0 |
| Growth_Rate | ratio, 3 dp | 6 (each company, FY2021) |
| Prior_Growth_Rate | ratio, 3 dp | 12 (each company, FY2021–FY2022) |
| Growth_Differential | ratio, 3 dp | 12 (each company, FY2021–FY2022) |
| Net_Income_Margin_pct | ratio, 3 dp | 0 |

`Growth_Differential` subtracts the unrounded growth rates, then rounds.

### performance

Warehouse: `financial_analytics.analytics.performance`. One row per company-year. Growth rate and net income margin are joined from `growth_trend` after that view has rounded them.

| Column | Excel type | Nulls in this file |
|---|---|---|
| Company | text | 0 |
| Fiscal_Year | integer | 0 |
| Revenue | USD | 0 |
| Gross_Profit | USD | 0 |
| Net_Income | USD | 0 |
| Operating_Income | USD | 0 |
| Operating_Expenses | USD | 4 (AMD 2021–2022, Microsoft 2021–2022) |
| Cash_Flow_from_Operating_Activities | USD | 0 |
| Capital_Expenditures | USD, positive spend | 1 (NVIDIA 2021) |
| Growth_Rate | ratio, 3 dp | 6 |
| Net_Income_Margin_pct | ratio, 3 dp | 0 |
| Gross_Margin_pct | ratio, 3 dp | 0 |
| Operating_Margin_pct | ratio, 3 dp | 0 |
| Operating_Income_Growth | ratio, 3 dp | 6 (FY2021) |
| Net_Income_Growth | ratio, 3 dp | 6 (FY2021) |
| Operating_Expense_Growth | ratio, 3 dp | 10 (the four missing expense years, plus AMD 2023, Microsoft 2023, and every FY2021) |
| Operating_Expense_to_Revenue | ratio, 3 dp | 4 |
| Revenue_Growth_Minus_Opex_Growth | ratio, 3 dp | 10 (same rows as expense growth) |
| Operating_Cash_Flow_Margin_pct | ratio, 3 dp | 0 |
| Operating_Cash_Flow_Growth | ratio, 3 dp | 6 (FY2021) |
| Cash_Conversion_Ratio | multiple, 3 dp | 0 |
| Cash_Conversion_Meaningful | boolean | 0 (false for six CrowdStrike rows) |
| Free_Cash_Flow | USD | 1 (NVIDIA 2021) |
| Free_Cash_Flow_Margin_pct | ratio, 3 dp | 1 (NVIDIA 2021) |

Free cash flow is operating cash flow minus capital expenditures. Capital expenditures are positive SEC payments.

`Revenue_Growth_Minus_Opex_Growth` subtracts unrounded expense growth from the already rounded `Growth_Rate`, then rounds.

### financial_health

Warehouse: `financial_analytics.analytics.financial_health`. One row per company-year.

| Column | Excel type | Nulls in this file |
|---|---|---|
| Company | text | 0 |
| Fiscal_Year | integer | 0 |
| Total_Assets | USD | 0 |
| Total_Liabilities | USD | 0 after the AMD fill. Source wide CSV is null for AMD 2021–2025 |
| Total_Liabilities_Imputed | boolean | 0. True for AMD 2021–2025 only |
| Total_Stockholders_Equity | USD | 0 |
| Total_Current_Assets | USD | 0 |
| Total_Current_Liabilities | USD | 0 |
| Current_ratio | multiple, 3 dp | 0 |
| Total_Debt | USD | 0. Missing debt leg becomes 0 |
| Short_Term_Debt_Reported | boolean | 0. False for CrowdStrike 2021–2026 only |
| Long_Term_Debt_Reported | boolean | 0. True on every row |
| debt_to_equity_ratio | multiple, 3 dp | 0 |
| Liabilities_to_Assets | ratio, 3 dp | 0 |
| ROA_Ending | ratio, 3 dp | 0 |
| ROE_Ending | ratio, 3 dp | 0 |
| ROA_Avg | ratio, 3 dp | 6 (FY2021) |
| ROE_Avg | ratio, 3 dp | 6 (FY2021) |
| ROA_Uses_Ending_Balance | boolean | 0. True for every company in FY2021 |
| ROE_Uses_Ending_Balance | boolean | 0. True for every company in FY2021 |
| ROA | ratio, 3 dp | 0. Average balance, or ending balance when the flag is true |
| ROE | ratio, 3 dp | 0. Same rule as ROA |
| Cash_Flow_from_Operating_Activities | USD | 0 |

### peer_benchmarking

Warehouse: `financial_analytics.analytics.peer_benchmarking`. Six rows, `Fiscal_Year = 2025` only. No nulls in this file. Sorted by `Average_Rank`, then `Company`.

Higher is better, so rank 1 is the largest value: `Growth_Rate`, `Operating_Margin_pct`, `Net_Income_Margin_pct`, `Operating_Cash_Flow_Margin_pct`, `Current_ratio`, `ROA`, `ROE`.

Lower is better, so rank 1 is the smallest value: `Operating_Expense_to_Revenue`, `debt_to_equity_ratio`.

`Average_Rank` uses those nine ranks only. Growth differential, operating-expense growth, and liabilities to assets are not in this view.

| Column | Excel type |
|---|---|
| Company | text |
| Fiscal_Year | integer, always 2025 |
| Growth_Rate | ratio, 3 dp |
| Growth_Rate_Rank | integer |
| Operating_Margin_pct | ratio, 3 dp |
| Operating_Margin_Rank | integer |
| Net_Income_Margin_pct | ratio, 3 dp |
| Net_Income_Margin_Rank | integer |
| Operating_Expense_to_Revenue | ratio, 3 dp |
| Operating_Expense_to_Revenue_Rank | integer |
| Operating_Cash_Flow_Margin_pct | ratio, 3 dp |
| Operating_Cash_Flow_Margin_Rank | integer |
| Current_ratio | multiple, 3 dp |
| Current_Ratio_Rank | integer |
| debt_to_equity_ratio | multiple, 3 dp |
| Debt_to_Equity_Rank | integer |
| ROA | ratio, 3 dp. Primary return |
| ROA_Rank | integer |
| ROE | ratio, 3 dp. Primary return |
| ROE_Rank | integer |
| Average_Rank | decimal, 3 dp |

### executive_summary

Warehouse: `financial_analytics.analytics.executive_summary`. Six rows, one per company, sorted by `Company`. No nulls in this file. Values are the company's latest fiscal year. Ranks are FY2025.

| Column | Excel type | Notes |
|---|---|---|
| Company | text | |
| Fiscal_Year | integer | 2025 or 2026, as in the coverage table |
| Benchmark_Fiscal_Year | integer | 2025 on every row |
| Revenue | USD | Latest year |
| Growth_Rate | ratio, 3 dp | Latest year |
| Prior_Growth_Rate | ratio, 3 dp | Latest year |
| Growth_Differential | ratio, 3 dp | Latest year |
| Gross_Margin_pct | ratio, 3 dp | |
| Operating_Margin_pct | ratio, 3 dp | |
| Net_Income_Margin_pct | ratio, 3 dp | |
| Operating_Income_Growth | ratio, 3 dp | |
| Net_Income_Growth | ratio, 3 dp | |
| Operating_Expense_Growth | ratio, 3 dp | |
| Operating_Expense_to_Revenue | ratio, 3 dp | |
| Revenue_Growth_Minus_Opex_Growth | ratio, 3 dp | |
| Operating_Cash_Flow_Margin_pct | ratio, 3 dp | |
| Operating_Cash_Flow_Growth | ratio, 3 dp | |
| Cash_Conversion_Ratio | multiple, 3 dp | |
| Cash_Conversion_Meaningful | boolean | False for CrowdStrike FY2026 |
| Free_Cash_Flow | USD | |
| Free_Cash_Flow_Margin_pct | ratio, 3 dp | |
| Current_ratio | multiple, 3 dp | |
| debt_to_equity_ratio | multiple, 3 dp | |
| Liabilities_to_Assets | ratio, 3 dp | |
| ROA | ratio, 3 dp | Primary |
| ROE | ratio, 3 dp | Primary |
| ROA_Ending | ratio, 3 dp | |
| ROE_Ending | ratio, 3 dp | |
| ROA_Avg | ratio, 3 dp | Present on these latest-year rows |
| ROE_Avg | ratio, 3 dp | Present on these latest-year rows |
| ROA_Uses_Ending_Balance | boolean | False on every latest-year row |
| ROE_Uses_Ending_Balance | boolean | False on every latest-year row |
| Total_Liabilities_Imputed | boolean | True for AMD only |
| Short_Term_Debt_Reported | boolean | False for CrowdStrike only |
| Long_Term_Debt_Reported | boolean | True on every row |
| FY2025_Growth_Rate_Rank | integer | FY2025 rank, including on FY2026 rows |
| FY2025_Operating_Margin_Rank | integer | |
| FY2025_Net_Income_Margin_Rank | integer | |
| FY2025_Operating_Expense_to_Revenue_Rank | integer | |
| FY2025_Operating_Cash_Flow_Margin_Rank | integer | |
| FY2025_Current_Ratio_Rank | integer | |
| FY2025_Debt_to_Equity_Rank | integer | |
| FY2025_ROA_Rank | integer | |
| FY2025_ROE_Rank | integer | |
| FY2025_Average_Rank | decimal, 3 dp | Same six values as `peer_benchmarking.Average_Rank` |

### peer_metrics

Not a warehouse object. Python selects these columns from `growth_trend`, `performance`, and `financial_health` for every company-year. No rank columns and no imputation flags.

| Column | Excel type | Nulls in this file | Taken from |
|---|---|---|---|
| Company | text | 0 | growth_trend |
| Fiscal_Year | integer | 0 | growth_trend |
| Revenue | USD | 0 | growth_trend |
| Growth_Rate | ratio, 3 dp | 6 | growth_trend |
| Growth_Differential | ratio, 3 dp | 12 | growth_trend |
| Net_Income_Margin_pct | ratio, 3 dp | 0 | growth_trend |
| Operating_Margin_pct | ratio, 3 dp | 0 | performance |
| Operating_Expense_to_Revenue | ratio, 3 dp | 4 | performance |
| Operating_Cash_Flow_Margin_pct | ratio, 3 dp | 0 | performance |
| Gross_Margin_pct | ratio, 3 dp | 0 | performance |
| Current_ratio | multiple, 3 dp | 0 | financial_health |
| debt_to_equity_ratio | multiple, 3 dp | 0 | financial_health |
| Liabilities_to_Assets | ratio, 3 dp | 0 | financial_health |
| ROA | ratio, 3 dp | 0 | financial_health, primary |
| ROE | ratio, 3 dp | 0 | financial_health, primary |

## Refresh

`excel/load_source_tables.py` rewrites the six CSVs. Power Query reads the folder in `tblSourceFolder` on Data Connections. If the workbook moves, paste the new `excel/source` path into that cell and use Data, Refresh All.

Table names: `tblGrowthTrend`, `tblPerformance`, `tblFinancialHealth`, `tblPeerBenchmarking`, `tblExecutiveSummary`, `tblPeerMetrics`.

Leave blanks blank. Keep the flags: `Total_Liabilities_Imputed`, `Short_Term_Debt_Reported`, `Long_Term_Debt_Reported`, `Cash_Conversion_Meaningful`, `ROA_Uses_Ending_Balance`, and `ROE_Uses_Ending_Balance`. No warehouse login goes in the file.
