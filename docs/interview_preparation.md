# Interview preparation

These are the 15 questions most worth being able to answer about this project. Each one says what the interviewer is usually testing, where the decision lives in the repository, and which concepts need to be solid before answering.

The notes are not a script. The goal is to explain the choice from the code and the data, including where a result does not prove a cause.

## 1. How did you get the financial data?

**What they are testing.** Whether the data is a real filing source, and whether the request follows the SEC's access rules.

**Where to review.** `extract_sec_company_facts.py`: `COMPANY_FACTS_BASE_URL`, `COMPANIES`, `REQUEST_HEADERS`, `download_company_facts`, and `user_agent_is_configured`.

**Concepts.** The SEC Company Facts API returns XBRL facts already extracted from filings. One request is made per company. The SEC expects a descriptive User-Agent with a contact name and email. The contact values in the script should be confirmed before a fresh extract. The project does not scrape filing HTML and does not fill in numbers that the API did not return.

## 2. How does the Python extract decide which fact to keep?

**What they are testing.** Whether annual results can be distinguished from quarterly facts, and what happens when the same metric appears more than once.

**Where to review.** `fact_is_usable`, `is_annual_form`, `is_annual_fiscal_period`, `METRIC_MAP`, and `resolve_duplicates`.

**Concepts.** Income and cash-flow facts have to cover about one year, between 330 and 400 days. Balance-sheet facts are a point in time. Allowed forms are 10-K and 10-K/A. When duplicates remain, an original 10-K is kept ahead of a 10-K/A, `us-gaap` is preferred, and the latest filed date is the remaining tie-break. The result is one row per company, fiscal year, and metric. `Fiscal_Year` comes from the period end year.

## 3. What cleaning happens after the raw extract?

**What they are testing.** The path from a long fact table to a company-year table, and which checks were actually run.

**Where to review.** `keep_fiscal_years_from`, `to_wide_format`, `print_accounting_checks`, and the Data Preparation section of `Business Performance Analytics.ipynb`.

**Concepts.** The raw file keeps the candidate facts. The clean file is the resolved annual set, 1,657 rows in the current extract. The wide file pivots metrics into one row per company-year. Provenance stays on the clean file: tag, form, accession number, period dates, filed date, and source. Accounting checks cover gross profit and the cash roll-forward within the larger of $1 million or 2%. They are checks, not permission to overwrite a reported fact.

## 4. How are missing financial values treated?

**What they are testing.** Whether blanks were silently turned into zeros, and whether an imputed amount can be told apart from a reported one.

**Where to review.** `docs/sql_metrics.md`, section "Accepted data gaps"; `impute_amd_liabilities` and `financial_health` in `src/bp_metrics.py`; `tests/test_flags.py` and `tests/test_rounding_and_gaps.py`.

**Concepts.** Four gaps matter. AMD and Microsoft are missing operating expenses in FY2021 and FY2022, so the expense ratio and expense growth stay null. AMD has no total-liabilities fact, so liabilities are assets minus equity and `Total_Liabilities_Imputed` stays true even after the wide value is filled. CrowdStrike short-term debt is unreported for every year in the extract. Total debt treats that missing leg as zero, and `Short_Term_Debt_Reported` is false. A reported zero would stay reported. NVIDIA FY2021 capital expenditures are missing, so free cash flow is null rather than equal to operating cash flow.

## 5. What do the five SQL views do?

**What they are testing.** Whether SQL is doing the analytical work, and whether each view has one job.

**Where to review.** The `CREATE OR REPLACE VIEW` cells in `Business Performance Analytics.ipynb` for `growth_trend`, `performance`, `financial_health`, `peer_benchmarking`, and `executive_summary`. The same definitions are summarized in `docs/sql_metrics.md`.

**Concepts.** `growth_trend` is revenue growth, the prior growth rate, and the change between them. `performance` is margins, expense efficiency, operating cash flow, cash conversion, and free cash flow. `financial_health` is liquidity, leverage, and returns. `peer_benchmarking` is six FY2025 rows. `executive_summary` is one latest-year row per company, with the FY2025 ranks attached on company rather than on year. No extra views were added to make the warehouse look larger.

## 6. How do the Python calculations relate to the SQL?

**What they are testing.** Whether the local path can drift away from the warehouse, and whether Python is recomputing something the SQL already defined differently.

**Where to review.** `src/bp_metrics.py`, especially `growth_trend`, `performance`, `financial_health`, `peer_benchmarking`, and `executive_summary`. `tests/test_sql_reconciliation.py` checks that the notebook SQL still contains the ranking, threshold, AMD, and full-precision rules.

**Concepts.** The Python functions are the local copy of the view formulas, not a second methodology. Growth rates are rounded to 3 decimals after a difference is taken, not before. Revenue growth minus operating-expense growth subtracts the full-precision rates and then rounds. A live comparison of the five warehouse views with the local frames matched on the current data. That comparison requires Databricks credentials and is not part of `pytest`.

## 7. How are the main ratios defined?

**What they are testing.** Whether a ratio can be stated precisely, including the denominator and the rounding.

**Where to review.** `docs/sql_metrics.md` and `src/glossary.py`. The application glossary is the same set of definitions.

**Concepts.** Margins divide by revenue. The expense ratio divides operating expenses by revenue. The current ratio divides current assets by current liabilities. Debt-to-equity divides total debt by equity. A zero denominator becomes null. Ratios used in the views are rounded to 3 decimals. Be ready to say which figures are source facts and which are calculated.

## 8. Why do ROA and ROE use an average balance?

**What they are testing.** Whether the return matches the period of the earnings to the balance sheet that supported them.

**Where to review.** `_average_or_ending` and `financial_health` in `src/bp_metrics.py`. The financial-health SQL uses the same fallback. The notebook flags the six FY2021 rows.

**Concepts.** Net income is earned across the year. Ending assets or ending equity are the balance on the last day. The primary return divides net income by the average of the current and prior balance. When a company has no prior year in this extract, the ending balance is the only available denominator, `ROA_Uses_Ending_Balance` or `ROE_Uses_Ending_Balance` is true, and `ROA_Avg` or `ROE_Avg` is blank. Ending-balance columns remain on the view so the two denominators can be compared. NVIDIA's FY2026 write-up uses both on purpose: average-balance ROA and ending-balance ROA are not the same number.

## 9. How should operating cash flow be read?

**What they are testing.** Whether cash is being confused with profit, and whether a ratio is being shown when it is not meaningful.

**Where to review.** `cash_conversion_meaningful` in `src/bp_metrics.py`, the Cash Flow page in `app.py`, `CASH` in `src/interpretations.py`, and `CASH_CONVERSION_NOTE` in `src/glossary.py`.

**Concepts.** Operating cash flow is the cash metric in the company reads. Positive operating cash flow does not mean the company is profitable. CrowdStrike is the example: operating and net margins are negative, and operating cash flow stays positive. Stock-based compensation was $1.097 billion in FY2026, about 68% of operating cash flow, and operating cash flow exceeded net income by more than that amount, so compensation is not the whole difference. Cash conversion is operating cash flow divided by net income. It is `n/m` when net income is zero or negative, or when the absolute ratio is greater than 5. A ratio of exactly 5 would still count as meaningful. CrowdStrike FY2025 is about -90.7, which is not a comparable conversion rate. Net income growth is not shown as a percent when that percent would misread a loss. CrowdStrike FY2026 is labeled "loss widened." Free cash flow is calculated as operating cash flow minus capital expenditures and is not used as a lead finding. It is null when capital expenditures are missing, including NVIDIA FY2021.

## 10. What does the peer ranking mean, and what does it not mean?

**What they are testing.** Whether a rank is being treated as a verdict about which company is best.

**Where to review.** `RANKED_METRICS`, `rank_values`, and `peer_benchmarking` in `src/bp_metrics.py`. The peer-benchmarking SQL and the Peer Benchmarking section of the notebook. `tests/test_ranks.py`.

**Concepts.** The rank table is FY2025 only. Nine metrics are weighted equally. Higher is better for seven of them. Lower is better for the expense ratio and debt-to-equity. Ties use the SQL `RANK()` rule: the tied companies share the best rank and the next rank is skipped. Missing values rank last and tie with each other. AMD and Adobe share an average rank of 3.889. NVIDIA's average is 1.222 and CrowdStrike's is 4.889. The companies are in different technology subsectors. The average is context for the company reads, not a winner score. Growth differential, operating-expense growth, and liabilities-to-assets are not in the average.

## 11. Can FY2025 results be compared directly across these companies?

**What they are testing.** Whether "the same fiscal year" is being confused with the same months.

**Where to review.** Period end dates on the revenue rows in `data/processed/sec_company_financials_clean.csv`. `PEER_YEAR` and `executive_summary` in `src/bp_metrics.py`. The coverage table in `README.md`.

**Concepts.** `Fiscal_Year` is the year the period ended. Microsoft's year ends June 30. Apple's ends in late September. NVIDIA's and CrowdStrike's end in late January. Adobe's and AMD's end near the calendar year, on 52/53-week dates. FY2025 is the last label all six have, so it is the common benchmark. It is not one shared calendar period. Latest-year commentary stays on each company's own latest year, which is FY2026 for three companies. Those FY2026 rows still carry the FY2025 ranks, in columns prefixed `FY2025_`, and the rank is labeled as the FY2025 comparison.

## 12. What is the Databricks path, and what has to exist before the app can use it?

**What they are testing.** Whether the warehouse is understood as a query layer over prepared data, not as the place the SEC extract happens.

**Where to review.** `src/data_source.py`: `DATABRICKS_VIEWS`, `databricks_configured`, and `_load_from_databricks`. The view-creation cells in the notebook. There is no upload step in the notebook. The warehouse tables are copies of the prepared files.

**Concepts.** The application reads five views when `DATABRICKS_SERVER_HOSTNAME`, `DATABRICKS_HTTP_PATH`, and `DATABRICKS_TOKEN` are all set. `peer_metrics` is assembled in Python from those views. It is not a sixth warehouse table. The notebook is where the views are created. The application does not create them. Credentials stay in the local environment or `.env`, and `.env` is gitignored.

## 13. What happens if Databricks is unavailable?

**What they are testing.** Whether the project can be reviewed and run without a live warehouse.

**Where to review.** `load_views` and `build_views`. `tests/test_loader_contract.py`, especially the test that clears the three Databricks variables and then compares a mocked warehouse cursor with the local frames.

**Concepts.** If any of the three settings is missing or blank, the loader never opens a connection. It builds the five views from `data/processed/company_financials_wide.csv` and uses `data/processed/sec_company_financials_clean.csv` for the AMD liability flag. The loader then aligns column names and dtypes so a warehouse cursor and the CSV path return the same contract. The processed files are part of the project so a reviewer does not have to call the SEC API or Databricks to open the app.

## 14. How is the Streamlit application organized?

**What they are testing.** Whether the interface is a view of the analysis or a separate set of calculations, and whether the pages match the business questions.

**Where to review.** `PAGES` and `main` in `app.py`. Page functions: `executive_page`, `performance_page`, `operations_page`, `profitability_page`, `cash_page`, `health_page`, `peer_page`, `attention_page`, and `glossary_page`.

**Concepts.** The pages are Overview, Company Performance, Operations, Profitability, Cash Flow, Financial Health, Peer Benchmarking, Management Attention, and Glossary. Filters are company and fiscal year. The peer page does not mix FY2025 and FY2026 when the year filter is "All". It ranks the last year present for every company. Company interpretations come from `src/interpretations.py`, which follows the notebook. Dollar amounts in those notes are escaped before display because Streamlit markdown would otherwise treat `$...$` as math. The glossary matches the columns the pages use. Free cash flow is explained there and is not a lead KPI.

## 15. How did a financial result become a management recommendation?

**What they are testing.** Whether the recommendation is tied to a measured change, and whether the language claims a cause the statements do not establish.

**Where to review.** The executive summary, individual company sections, cross-company comparison, and management attention table in the notebook. `EXECUTIVE` and `ALERTS` in `src/interpretations.py`. The Management Attention page.

**Concepts.** Each company has one priority. The note has a signal, why it matters, the direction of the trend, a recommended action, and the KPIs to monitor. Microsoft's item is a higher operating margin and stronger cash generation beside a slightly lower gross margin. Apple's is earnings up and operating cash flow down. The receivables, inventory, payables, stock-based compensation, and depreciation already in the file do not close that gap. NVIDIA's is slower growth with margins that are still high. Adobe's is better operating efficiency with a current ratio just under 1, lower cash, and higher long-term debt. AMD's is faster growth lifting an operating margin that is still comparatively low. CrowdStrike's is a wider operating loss while operating cash flow stays positive. Research and development and general and administrative grew faster than revenue, and stock-based compensation is a large part of the cash result without being the whole explanation. A slower growth rate is not described as a decline in revenue. None of the notes claims to have identified a single cause.
