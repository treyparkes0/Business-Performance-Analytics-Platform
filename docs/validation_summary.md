# Validation summary

Checked locally on 15 November 2026 against commit `70cc19e` (`Merge pull request #2`). Databricks credentials are not set, so the app and the tests rebuild the five views from `data/processed/company_financials_wide.csv`. Formulas stay in `docs/sql_metrics.md`, `sql/`, and `src/bp_metrics.py`. This note records that those definitions agree.

`python -m pytest -q` — 30 passed in 4.16s.

The six companies are Microsoft, Apple, NVIDIA, Adobe, AMD, and CrowdStrike. AMD is the sixth company in the extract, the tests, and the app. Coverage is 33 company-years: AMD, Adobe, and Apple for FY2021–FY2025, and Microsoft, NVIDIA, and CrowdStrike for FY2021–FY2026. FY2025 is the last year present for every company. `extract_sec_company_facts.py` sends an SEC User-Agent with a name and email. Source extracts stay separate from the wide file the views read.

## What was checked

Primary ROA and ROE use the average of the current and prior balance. Ending balances are used only for FY2021, and `ROA_Uses_Ending_Balance` and `ROE_Uses_Ending_Balance` are true on those six rows. `ROA_Ending` and `ROE_Ending` remain available. `ROA_Avg` and `ROE_Avg` are blank in FY2021.

Cash conversion is operating cash flow divided by net income, rounded to 3 decimals. `Cash_Conversion_Meaningful` is false when net income is zero or negative, or when the absolute unrounded ratio is greater than 5. It is false for all six CrowdStrike years. The FY2025 ratio is -90.659.

CrowdStrike short-term debt is unreported for FY2021–FY2026. `Short_Term_Debt_Reported` is false on those rows, and `Total_Debt` equals long-term debt. A reported zero stays distinct from a missing value.

`Total_Liabilities_Imputed` is true for all five AMD years and false for every other company-year. The flag follows a missing `Total_Liabilities` fact. The long extract `data/processed/sec_company_financials_clean.csv` is on this machine and is not in git. A clean clone fails `test_clean_file_matches_wide_inputs` until that file is present. The local run passed because the file is here. Missing values elsewhere are left blank.

Peer ranking uses nine FY2025 metrics. Higher is better for revenue growth, operating margin, net income margin, operating-cash-flow margin, current ratio, ROA, and ROE. Lower is better for operating expense / revenue and debt-to-equity. Ties share the best rank. Missing values rank last and still count in the average. `Average_Rank` is the equal-weight mean of those nine ranks, rounded to 3 decimals.

| Company | Average rank |
|---|---|
| NVIDIA | 1.222 |
| Microsoft | 3.111 |
| AMD | 3.889 |
| Adobe | 3.889 |
| Apple | 4.000 |
| CrowdStrike | 4.889 |

Growth differential, operating-expense growth, and liabilities-to-assets are not in the average. The same nine ranks and the average-balance returns are in `tests/sql/phase1_identity_checks.sql`. That script was not executed in a database. Pytest checks the Python copy and that the notebook SQL matches the files in `sql/`.

## App check

The Streamlit app was started locally with no Databricks connection and opened at `http://localhost:8501`. Overview listed all six companies at each company's own latest year. Selecting Microsoft left one card, FY2026, with revenue growth 17.8%, operating margin 46.8%, and the history table limited to Microsoft FY2021–FY2026. Company Performance, Operations, Profitability, Cash Flow, and Financial Health each opened for Microsoft and named their source view. Peer Benchmarking, still on Microsoft, ranked all six companies for FY2025. Revenue-growth order was NVIDIA, AMD, CrowdStrike, Microsoft, Adobe, Apple, matching the nine-metric rank table. The page states that the company filter does not change the peer set. No page raised an exception. No credential is stored for the warehouse.
