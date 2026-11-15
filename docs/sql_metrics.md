# SQL metrics

The notebook views are the source of truth. `src/bp_metrics.py` repeats the same formulas for the app when Databricks credentials are not set. The Streamlit app does not calculate these columns itself.

Source table: `financial_analytics.clean.company_financials`  
Local file: `data/processed/company_financials_wide.csv` (33 company-years, fiscal 2021 onward)

Checked on the local copy with `python -m unittest tests.test_phase1_sql_metrics`.  
The same checks for the warehouse are in `tests/sql/phase1_identity_checks.sql`.

## What is calculated in SQL

Inputs that stay as reported facts: revenue, gross profit, operating income, net income, operating expenses, operating cash flow, capital expenditures, and the balance-sheet amounts. Everything below is calculated.

### `financial_analytics.analytics.growth_trend`

One row per company-year. First year has a null growth rate. The second year has a growth rate and a null growth differential.

| Column | Formula | Null when |
|---|---|---|
| Growth_Rate | (Revenue − prior Revenue) / prior Revenue | First year, or prior revenue is 0 |
| Prior_Growth_Rate | Prior year Growth_Rate | First two years |
| Growth_Differential | Growth_Rate − Prior_Growth_Rate, using the unrounded rates | First two years |
| Net_Income_Margin_pct | Net_Income / Revenue | Revenue is 0 |

Each ratio is rounded to 3 decimals after the subtraction, not before.

### `financial_analytics.analytics.performance`

One row per company-year. Joins `growth_trend` for the already rounded growth rate and net income margin.

| Column | Formula | Null when |
|---|---|---|
| Gross_Margin_pct | Gross_Profit / Revenue | Revenue is 0 |
| Operating_Margin_pct | Operating_Income / Revenue | Revenue is 0 |
| Operating_Income_Growth | (Operating_Income − prior) / prior | First year, or prior is 0 |
| Net_Income_Growth | (Net_Income − prior) / prior | First year, or prior is 0 |
| Operating_Expense_Growth | (Operating_Expenses − prior) / prior | Either year is missing, or prior is 0 |
| Operating_Expense_to_Revenue | Operating_Expenses / Revenue | Operating expenses missing, or revenue is 0 |
| Revenue_Growth_Minus_Opex_Growth | Rounded Growth_Rate − unrounded operating-expense growth, then rounded | Either input is null |
| Operating_Cash_Flow_Margin_pct | Operating cash flow / Revenue | Revenue is 0 |
| Operating_Cash_Flow_Growth | (Operating cash flow − prior) / prior | First year, or prior is 0 |
| Cash_Conversion_Ratio | Operating cash flow / Net_Income, raw ratio, rounded to 3 decimals | Net income is 0 |
| Cash_Conversion_Meaningful | False when net income is zero or negative, or when abs(operating cash flow / net income) is greater than 5. A ratio of exactly 5 stays true. Null inputs leave the flag null | Either input is null |
| Free_Cash_Flow | Operating cash flow − Capital_Expenditures | Capital expenditures missing |
| Free_Cash_Flow_Margin_pct | Free_Cash_Flow / Revenue | Free cash flow is null, or revenue is 0 |

`Revenue_Growth_Minus_Opex_Growth` subtracts the unrounded expense growth from the rounded revenue growth. The Python copy does the same.

### `financial_analytics.analytics.financial_health`

One row per company-year. Average returns lag by `Ticker`. In this set each company has one ticker, so that matches a lag by company.

| Column | Formula | Null when |
|---|---|---|
| Current_ratio | Total_Current_Assets / Total_Current_Liabilities | Current liabilities are 0 |
| Total_Debt | COALESCE(Short_Term_Debt, 0) + COALESCE(Long_Term_Debt, 0) | Never null. A missing piece becomes 0 |
| debt_to_equity_ratio | Total_Debt / Total_Stockholders_Equity | Equity is 0 |
| Short_Term_Debt_Reported | Short_Term_Debt is not null | Never. False when the source leg is null |
| Long_Term_Debt_Reported | Long_Term_Debt is not null | Never. False when the source leg is null |
| Liabilities_to_Assets | Total_Liabilities / Total_Assets | Liabilities missing, or assets are 0 |
| ROA_Ending | Net_Income / ending Total_Assets | Assets are 0 |
| ROE_Ending | Net_Income / ending Total_Stockholders_Equity | Equity is 0 |
| ROA_Avg | Net_Income / average of this year and prior Total_Assets | First year |
| ROE_Avg | Net_Income / average of this year and prior equity | First year |
| ROA_Uses_Ending_Balance | True when that ticker has no prior Total_Assets | Never |
| ROE_Uses_Ending_Balance | True when that ticker has no prior equity | Never |
| ROA | ROA_Avg, or ROA_Ending when there is no prior year | The balance used in the denominator is 0 |
| ROE | ROE_Avg, or ROE_Ending when there is no prior year | The balance used in the denominator is 0 |
| Total_Liabilities_Imputed | True only for AMD company-years with no Total_Liabilities fact in `sec_company_financials_clean` | Never |

Primary ROA and ROE are the columns used in peer ranking. The average is `(current + prior) / 2`, partitioned by ticker. Ending balances are the fallback only, and the flags say so. `ROA_Ending` and `ROE_Ending` stay available either way.

`Total_Liabilities_Imputed` does not look at whether `company_financials.Total_Liabilities` is null. The notebook UPDATE may already have replaced those nulls with assets minus equity. The flag stays true when the long facts table has no `Total_Liabilities` row. A reported fact is not imputed, even when the amount equals assets minus equity. If that facts table cannot be read, the flag is not inferred from the accounting identity.

### `financial_analytics.analytics.peer_benchmarking`

Six rows, locked to fiscal year 2025. That is the last year present for every company. Each ranked metric is stored next to its rank.

`RANK()` matches pandas `rank(method="min")`. Ties share the best rank and the next rank is skipped. Missing values use `NULLS LAST` (`na_option="bottom"`): they rank after every reported value, tie with each other, and still count in the average.

Higher is better for revenue growth, operating margin, net income margin, operating cash flow margin, current ratio, ROA, and ROE.

Lower is better for operating expense / revenue and debt-to-equity.

`Average_Rank` is the equal-weight mean of those nine ranks, rounded to 3 decimals. The nine are `Growth_Rate_Rank`, `Operating_Margin_Rank`, `Net_Income_Margin_Rank`, `Operating_Expense_to_Revenue_Rank`, `Operating_Cash_Flow_Margin_Rank`, `Current_Ratio_Rank`, `Debt_to_Equity_Rank`, `ROA_Rank`, and `ROE_Rank`. Growth differential, operating expense growth, and liabilities to assets are not ranks and are not in the average. ROA and ROE here are the primary average-balance returns.

NVIDIA FY2025 average rank is 1.222.

### `financial_analytics.analytics.executive_summary`

No new formulas. One row per company at that company's own latest fiscal year, joining growth, performance, and financial health.

Latest year is 2025 for AMD, Adobe, and Apple. It is 2026 for Microsoft, NVIDIA, and CrowdStrike. FY2025 peer ranks are attached on company alone, so the FY2026 rows keep their own growth and margin figures and still carry the FY2025 ranks. Those columns are prefixed `FY2025_`. `Benchmark_Fiscal_Year` is 2025 on every row. The shared-year comparison stays on `peer_benchmarking`.

## Accepted data gaps

These are source gaps, not formula errors. Values were not filled in.

| Gap | Rows | Effect |
|---|---|---|
| Operating expenses missing from SEC `OperatingExpenses` | AMD 2021–2022, Microsoft 2021–2022 | Expense ratio and expense growth stay null. AMD 2023 and Microsoft 2023 have expenses, and expense growth is still null because the prior year is missing |
| Capital expenditures missing | NVIDIA 2021 | Free cash flow and its margin are null for that year |
| Short-term debt missing | CrowdStrike, FY2021–FY2026 | `Total_Debt` treats the missing leg as 0, so it equals long-term debt. `Short_Term_Debt_Reported` is false. A reported zero would stay reported |
| Total liabilities not tagged | AMD, every year | No `Total_Liabilities` fact. The amount is Total_Assets − Total_Stockholders_Equity. `Total_Liabilities_Imputed` stays true even if the wide table was already filled |

The notebook still runs `UPDATE ... SET Total_Liabilities = Total_Assets - Total_Stockholders_Equity` for AMD nulls so the wide table's dollar check can pass. The view does not use that null as the flag. It left-joins `sec_company_financials_clean` and flags AMD company-years with no `Metric = 'Total_Liabilities'` row. Local Python does the same when that extract is present. The wide CSV in this repository still has those AMD values null, and the long extract file is not committed, so the local path treats a null wide value as the provenance. It does not infer imputation from assets minus equity.

Accounting identities on the wide file, using the extractor tolerance (the larger of $1 million or 2%), produced no gross-profit or cash-rollforward warnings. Assets versus liabilities plus equity could not be checked for AMD until the derived liabilities were applied. After that fill, the identity holds.

## SEC check

`extract_sec_company_facts.py` keeps annual 10-K facts from the SEC Company Facts API, fiscal years 2021 onward. Duplicate facts collapse to one row per company, year, and metric: original 10-K before 10-K/A, `us-gaap` preferred, then the latest filed date. All 1,657 clean rows are `10-K` and `us-gaap`. The wide file matches those values for the metrics the views use.

Live Company Facts values matched the stored facts for:

| Company | Year | Tag | Value |
|---|---|---|---|
| Apple | 2025 | RevenueFromContractWithCustomerExcludingAssessedTax | 416,161,000,000 |
| AMD | 2025 | RevenueFromContractWithCustomerExcludingAssessedTax | 34,639,000,000 |
| CrowdStrike | 2025 | RevenueFromContractWithCustomerIncludingAssessedTax | 3,953,624,000 |
| Microsoft | 2026 | NetIncomeLoss | 133,749,000,000 |
| NVIDIA | 2021 | Assets | 28,791,000,000 |

CrowdStrike revenue uses the tag that includes assessed tax because the excluding-tax tag is not in its facts. Capital expenditures are stored as positive SEC payments, and free cash flow subtracts them from operating cash flow.

Copies under `data/raw/` and `data/market data/` match `data/processed/` byte for byte. The app and these tests read `data/processed/`.

## Python copy versus the notebook

Reviewed against the `CREATE OR REPLACE VIEW` cells in `Business Performance Analytics.ipynb`.

- Growth, performance, health, the nine-metric FY2025 ranks, and the executive summary match `src/bp_metrics.py` and `sql/`.
- Both paths round to 3 decimals and guard zero denominators.
- View SQL uses `Company` and `Fiscal_Year`. The loader accepts either casing from a warehouse cursor and returns `Company` and `Fiscal_Year`.
- The five views were not executed on a live Databricks warehouse in this audit. `tests/sql/phase1_identity_checks.sql` is the warehouse script. Local pytest checks the Python copy and that the notebook cells match `sql/`.
