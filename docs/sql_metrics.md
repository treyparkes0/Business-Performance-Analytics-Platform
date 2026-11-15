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
| Cash_Conversion_Ratio | Operating cash flow / Net_Income | Net income is 0 |
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
| Liabilities_to_Assets | Total_Liabilities / Total_Assets | Liabilities missing, or assets are 0 |
| ROE | Net_Income / Total_Stockholders_Equity | Equity is 0 |
| ROA | Net_Income / Total_Assets | Assets are 0 |
| ROA_Avg | Net_Income / average of this year and prior Total_Assets | First year |
| ROE_Avg | Net_Income / average of this year and prior equity | First year |

### `financial_analytics.analytics.peer_benchmarking`

Six rows, locked to fiscal year 2025. That is the last year present for every company. `RANK()` gives ties the same minimum rank.

Higher rank is better for growth rate, growth differential, operating margin, net income margin, operating cash flow margin, current ratio, ROA, and ROE.

Lower rank is better for operating expense growth, debt to equity, and liabilities to assets.

`Average_Rank` is the mean of 9 ranks: growth rate, growth differential, operating margin, net income margin, operating cash flow margin, current ratio, debt to equity, ROA, and ROE. Operating expense growth and liabilities to assets are shown and are not in the average.

NVIDIA FY2025 average rank is 1.778.

### `financial_analytics.analytics.executive_summary`

No new formulas. One row per company at that company's own latest fiscal year, joining the three views above.

Latest year is 2025 for AMD, Adobe, and Apple. It is 2026 for Microsoft, NVIDIA, and CrowdStrike. Peer ranks are FY2025 only, so the three FY2026 rows keep their own growth and margin figures and have null rank columns. That is the current behavior. The shared-year comparison stays on `peer_benchmarking`.

## Accepted data gaps

These are source gaps, not formula errors. Values were not filled in.

| Gap | Rows | Effect |
|---|---|---|
| Operating expenses missing from SEC `OperatingExpenses` | AMD 2021–2022, Microsoft 2021–2022 | Expense ratio and expense growth stay null. AMD 2023 and Microsoft 2023 have expenses, and expense growth is still null because the prior year is missing |
| Capital expenditures missing | NVIDIA 2021 | Free cash flow and its margin are null for that year |
| Short-term debt missing | CrowdStrike, every year | `Total_Debt` equals long-term debt only |
| Total liabilities not tagged | AMD, every year | Derived as Total_Assets − Total_Stockholders_Equity |

The AMD liabilities fill is in two places. The notebook runs `UPDATE ... SET Total_Liabilities = Total_Assets - Total_Stockholders_Equity` for AMD. `load_financials` applies the same fill when the column is null. The CSV on disk still has those five values null. Reloading the Databricks table from that CSV without the update would leave AMD `Liabilities_to_Assets` null until the update is run again.

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

- Growth, performance, health, peer ranks, the 9-rank average, the FY2025 peer filter, and the latest-year executive summary match `src/bp_metrics.py`.
- Both paths round to 3 decimals and guard zero denominators.
- The peer view aliases `company` and `fiscal_year` in lowercase. Spark resolves those names case-insensitively. The Python frames use `Company` and `Fiscal_Year`.
