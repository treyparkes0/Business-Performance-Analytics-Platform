-- Phase 1 identity checks for the Databricks views.
-- Each query returns failing rows. An empty result is a pass.
-- Run in the same warehouse as Business Performance Analytics.ipynb.
--
-- Local copy of these checks: python -m unittest tests.test_phase1_sql_metrics

-- 1. Long clean file: no null values, one row per company-year-metric.
SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS value_nulls,
    COUNT(*) - COUNT(DISTINCT company, fiscal_year, Metric) AS duplicate_facts
FROM financial_analytics.clean.sec_company_financials_clean;
-- Pass: total_records = 1657, value_nulls = 0, duplicate_facts = 0.

-- 2. Company-year grain: 33 rows, no duplicate company-year, no internal year gap.
SELECT company, fiscal_year, COUNT(*) AS row_count
FROM financial_analytics.clean.company_financials
GROUP BY company, fiscal_year
HAVING COUNT(*) <> 1;

WITH bounds AS (
    SELECT company, MIN(fiscal_year) AS first_year, MAX(fiscal_year) AS last_year, COUNT(*) AS n_years
    FROM financial_analytics.clean.company_financials
    GROUP BY company
)
SELECT company, first_year, last_year, n_years
FROM bounds
WHERE first_year <> 2021
   OR last_year <> CASE
        WHEN company IN ('Microsoft', 'NVIDIA', 'CrowdStrike') THEN 2026
        ELSE 2025
      END
   OR n_years <> (last_year - first_year + 1);

-- 3. Missing operating expenses. These four rows are the accepted gap.
--    A different set of rows means the source changed.
SELECT company, fiscal_year
FROM financial_analytics.clean.company_financials
WHERE Operating_Expenses IS NULL
  AND NOT (
      (company = 'AMD' AND fiscal_year IN (2021, 2022))
      OR (company = 'Microsoft' AND fiscal_year IN (2021, 2022))
  );

SELECT COUNT(*) AS unexpected_missing_opex_count
FROM financial_analytics.clean.company_financials
WHERE Operating_Expenses IS NULL
  AND NOT (
      (company = 'AMD' AND fiscal_year IN (2021, 2022))
      OR (company = 'Microsoft' AND fiscal_year IN (2021, 2022))
  );
-- Pass: 0.

-- 4. AMD liabilities on the wide table equal assets minus equity after the notebook UPDATE.
--    Rows here mean that UPDATE has not been applied on this table.
--    The imputation flag does not use this null check. It uses the long facts table
--    (see the financial_health check below), so a filled wide value can still be flagged.
SELECT
    company,
    fiscal_year,
    Total_Liabilities,
    Total_Assets - Total_Stockholders_Equity AS derived_liabilities
FROM financial_analytics.clean.company_financials
WHERE company = 'AMD'
  AND NOT (Total_Liabilities <=> (Total_Assets - Total_Stockholders_Equity));

-- 5. growth_trend matches the lag formula. Differential is the difference of
--    the unrounded rates, then each column is rounded to 3 decimals.
WITH raw AS (
    SELECT
        company,
        fiscal_year,
        (Revenue - LAG(Revenue) OVER (PARTITION BY company ORDER BY fiscal_year))
            / NULLIF(LAG(Revenue) OVER (PARTITION BY company ORDER BY fiscal_year), 0) AS raw_growth
    FROM financial_analytics.clean.company_financials
),
expected AS (
    SELECT
        company,
        fiscal_year,
        ROUND(raw_growth, 3) AS expected_growth,
        ROUND(LAG(raw_growth) OVER (PARTITION BY company ORDER BY fiscal_year), 3) AS expected_prior,
        ROUND(
            raw_growth - LAG(raw_growth) OVER (PARTITION BY company ORDER BY fiscal_year),
            3
        ) AS expected_diff
    FROM raw
)
SELECT
    g.company,
    g.fiscal_year,
    g.Growth_Rate,
    e.expected_growth,
    g.Prior_Growth_Rate,
    e.expected_prior,
    g.Growth_Differential,
    e.expected_diff
FROM financial_analytics.analytics.growth_trend g
JOIN expected e
    ON g.company = e.company
   AND g.fiscal_year = e.fiscal_year
WHERE NOT (g.Growth_Rate <=> e.expected_growth)
   OR NOT (g.Prior_Growth_Rate <=> e.expected_prior)
   OR NOT (g.Growth_Differential <=> e.expected_diff);

-- 6. performance margins and free cash flow.
SELECT
    p.company,
    p.fiscal_year,
    p.Gross_Margin_pct,
    ROUND(c.Gross_Profit / NULLIF(c.Revenue, 0), 3) AS expected_gross_margin,
    p.Operating_Margin_pct,
    ROUND(c.Operating_Income / NULLIF(c.Revenue, 0), 3) AS expected_operating_margin,
    p.Free_Cash_Flow,
    ROUND(c.Cash_Flow_from_Operating_Activities - c.Capital_Expenditures, 3) AS expected_fcf
FROM financial_analytics.analytics.performance p
JOIN financial_analytics.clean.company_financials c
    ON p.company = c.company
   AND p.fiscal_year = c.fiscal_year
WHERE NOT (p.Gross_Margin_pct <=> ROUND(c.Gross_Profit / NULLIF(c.Revenue, 0), 3))
   OR NOT (p.Operating_Margin_pct <=> ROUND(c.Operating_Income / NULLIF(c.Revenue, 0), 3))
   OR NOT (
        p.Free_Cash_Flow <=> ROUND(
            c.Cash_Flow_from_Operating_Activities - c.Capital_Expenditures,
            3
        )
   );

-- 7. financial_health. Primary ROA and ROE use average balances.
--    Ending balances are a separate calculation and are used for the primary
--    ratio only when that ticker has no prior year. The flags record that case.
--    Current ratio still uses the ending current balances.
WITH lagged AS (
    SELECT
        company,
        fiscal_year,
        Net_Income,
        Total_Assets,
        Total_Stockholders_Equity,
        Total_Current_Assets,
        Total_Current_Liabilities,
        LAG(Total_Assets) OVER (PARTITION BY Ticker ORDER BY fiscal_year) AS prior_assets,
        LAG(Total_Stockholders_Equity) OVER (PARTITION BY Ticker ORDER BY fiscal_year) AS prior_equity
    FROM financial_analytics.clean.company_financials
),
expected_returns AS (
    SELECT
        company,
        fiscal_year,
        ROUND(Total_Current_Assets / NULLIF(Total_Current_Liabilities, 0), 3) AS expected_current,
        ROUND(Net_Income / NULLIF(Total_Assets, 0), 3) AS expected_roa_ending,
        ROUND(Net_Income / NULLIF(Total_Stockholders_Equity, 0), 3) AS expected_roe_ending,
        ROUND(Net_Income / NULLIF((Total_Assets + prior_assets) / 2, 0), 3) AS expected_roa_avg,
        ROUND(Net_Income / NULLIF((Total_Stockholders_Equity + prior_equity) / 2, 0), 3) AS expected_roe_avg,
        CASE WHEN prior_assets IS NULL THEN TRUE ELSE FALSE END AS expected_roa_uses_ending,
        CASE WHEN prior_equity IS NULL THEN TRUE ELSE FALSE END AS expected_roe_uses_ending,
        ROUND(
            CASE
                WHEN prior_assets IS NULL THEN Net_Income / NULLIF(Total_Assets, 0)
                ELSE Net_Income / NULLIF((Total_Assets + prior_assets) / 2, 0)
            END,
            3
        ) AS expected_roa,
        ROUND(
            CASE
                WHEN prior_equity IS NULL THEN Net_Income / NULLIF(Total_Stockholders_Equity, 0)
                ELSE Net_Income / NULLIF((Total_Stockholders_Equity + prior_equity) / 2, 0)
            END,
            3
        ) AS expected_roe
    FROM lagged
)
SELECT
    h.company,
    h.fiscal_year,
    h.ROA,
    e.expected_roa,
    h.ROE,
    e.expected_roe,
    h.ROA_Ending,
    e.expected_roa_ending,
    h.ROE_Ending,
    e.expected_roe_ending,
    h.ROA_Uses_Ending_Balance,
    e.expected_roa_uses_ending,
    h.ROE_Uses_Ending_Balance,
    e.expected_roe_uses_ending
FROM financial_analytics.analytics.financial_health h
JOIN expected_returns e
    ON h.company = e.company
   AND h.fiscal_year = e.fiscal_year
WHERE NOT (h.Current_ratio <=> e.expected_current)
   OR NOT (h.ROA <=> e.expected_roa)
   OR NOT (h.ROE <=> e.expected_roe)
   OR NOT (h.ROA_Ending <=> e.expected_roa_ending)
   OR NOT (h.ROE_Ending <=> e.expected_roe_ending)
   OR NOT (h.ROA_Avg <=> e.expected_roa_avg)
   OR NOT (h.ROE_Avg <=> e.expected_roe_avg)
   OR NOT (h.ROA_Uses_Ending_Balance <=> e.expected_roa_uses_ending)
   OR NOT (h.ROE_Uses_Ending_Balance <=> e.expected_roe_uses_ending);

-- 7b. AMD imputation follows the long facts table.
--     No Total_Liabilities fact means the flag is true, including after the wide UPDATE.
--     A fact means the flag is false. Other companies are never imputed.
SELECT
    c.company,
    c.fiscal_year,
    h.Total_Liabilities,
    h.Total_Liabilities_Imputed,
    f.company AS reported_company
FROM financial_analytics.clean.company_financials c
LEFT JOIN (
    SELECT DISTINCT company, fiscal_year
    FROM financial_analytics.clean.sec_company_financials_clean
    WHERE Metric = 'Total_Liabilities'
) f
    ON c.company = f.company
   AND c.fiscal_year = f.fiscal_year
JOIN financial_analytics.analytics.financial_health h
    ON c.company = h.company
   AND c.fiscal_year = h.fiscal_year
WHERE (c.company = 'AMD' AND f.company IS NULL AND h.Total_Liabilities_Imputed <> TRUE)
   OR (
        c.company = 'AMD'
        AND f.company IS NULL
        AND c.Total_Liabilities IS NULL
        AND NOT (h.Total_Liabilities <=> (c.Total_Assets - c.Total_Stockholders_Equity))
      )
   OR (f.company IS NOT NULL AND h.Total_Liabilities_Imputed <> FALSE)
   OR (c.company <> 'AMD' AND h.Total_Liabilities_Imputed <> FALSE);

-- 7c. Debt reported flags match the source nulls. A missing leg is still 0 in the ratio.
--     CrowdStrike short-term debt is unreported for FY2021-FY2026.
SELECT
    h.company,
    h.fiscal_year,
    h.Short_Term_Debt_Reported,
    c.Short_Term_Debt IS NOT NULL AS expected_short_reported,
    h.Long_Term_Debt_Reported,
    c.Long_Term_Debt IS NOT NULL AS expected_long_reported
FROM financial_analytics.analytics.financial_health h
JOIN financial_analytics.clean.company_financials c
    ON h.company = c.company
   AND h.fiscal_year = c.fiscal_year
WHERE h.Short_Term_Debt_Reported <> (c.Short_Term_Debt IS NOT NULL)
   OR h.Long_Term_Debt_Reported <> (c.Long_Term_Debt IS NOT NULL)
   OR (
        h.company = 'CrowdStrike'
        AND (
            h.Short_Term_Debt_Reported <> FALSE
            OR h.Long_Term_Debt_Reported <> TRUE
        )
      );

-- 7d. Cash conversion keeps the raw ratio. The flag is false when net income is
--     zero or negative, or when abs(operating cash flow / net income) > 5.
SELECT
    p.company,
    p.fiscal_year,
    p.Cash_Conversion_Ratio,
    p.Cash_Conversion_Meaningful
FROM financial_analytics.analytics.performance p
JOIN financial_analytics.clean.company_financials c
    ON p.company = c.company
   AND p.fiscal_year = c.fiscal_year
WHERE NOT (
        p.Cash_Conversion_Ratio <=> ROUND(
            c.Cash_Flow_from_Operating_Activities / NULLIF(c.Net_Income, 0),
            3
        )
      )
   OR NOT (
        p.Cash_Conversion_Meaningful <=> CASE
            WHEN c.Net_Income IS NULL OR c.Cash_Flow_from_Operating_Activities IS NULL THEN NULL
            WHEN c.Net_Income <= 0 THEN FALSE
            WHEN abs(c.Cash_Flow_from_Operating_Activities / c.Net_Income) > 5 THEN FALSE
            ELSE TRUE
        END
      );

-- 8. Peer set is the shared year, FY2025, one row per company.
SELECT fiscal_year, COUNT(*) AS company_count
FROM financial_analytics.analytics.peer_benchmarking
GROUP BY fiscal_year
HAVING fiscal_year <> 2025 OR COUNT(*) <> 6;

-- 9. Average_Rank is the mean of exactly these nine ranks.
--    Higher is better: growth rate, operating margin, net income margin,
--    OCF margin, current ratio, ROA, ROE.
--    Lower is better: operating expense / revenue, debt-to-equity.
--    Ties use RANK() (shared best rank, next rank skipped).
--    Missing values sort NULLS LAST and still count in the average.
--    ROA and ROE in this average are the primary average-balance returns.
SELECT
    company,
    Average_Rank,
    ROUND((
        Growth_Rate_Rank
        + Operating_Margin_Rank
        + Net_Income_Margin_Rank
        + Operating_Expense_to_Revenue_Rank
        + Operating_Cash_Flow_Margin_Rank
        + Current_Ratio_Rank
        + Debt_to_Equity_Rank
        + ROA_Rank
        + ROE_Rank
    ) / 9.0, 3) AS expected_average
FROM financial_analytics.analytics.peer_benchmarking
WHERE NOT (
    Average_Rank <=> ROUND((
        Growth_Rate_Rank
        + Operating_Margin_Rank
        + Net_Income_Margin_Rank
        + Operating_Expense_to_Revenue_Rank
        + Operating_Cash_Flow_Margin_Rank
        + Current_Ratio_Rank
        + Debt_to_Equity_Rank
        + ROA_Rank
        + ROE_Rank
    ) / 9.0, 3)
);

-- NVIDIA FY2025 anchor for the nine-metric average.
SELECT company, fiscal_year, Average_Rank
FROM financial_analytics.analytics.peer_benchmarking
WHERE company = 'NVIDIA'
  AND NOT (Average_Rank <=> 1.222);

-- 10. Executive summary is each company's own latest year.
--     FY2025 ranks are attached by company, including on FY2026 rows.
--     Benchmark_Fiscal_Year is 2025 on every row.
SELECT company, fiscal_year, Growth_Rate, Benchmark_Fiscal_Year, FY2025_Growth_Rate_Rank, FY2025_Average_Rank
FROM financial_analytics.analytics.executive_summary
WHERE Benchmark_Fiscal_Year <> 2025
   OR FY2025_Growth_Rate_Rank IS NULL
   OR FY2025_Average_Rank IS NULL
   OR (
        company IN ('AMD', 'Adobe', 'Apple')
        AND fiscal_year <> 2025
      )
   OR (
        company IN ('Microsoft', 'NVIDIA', 'CrowdStrike')
        AND (fiscal_year <> 2026 OR Growth_Rate IS NULL)
      );
