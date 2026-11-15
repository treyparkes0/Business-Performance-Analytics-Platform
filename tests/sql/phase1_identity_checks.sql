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

-- 4. AMD liabilities are derived. The wide CSV stores them as null.
--    The notebook UPDATE sets Total_Liabilities = Total_Assets - Total_Stockholders_Equity.
--    Rows here mean that UPDATE has not been applied on this table.
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

-- 7. financial_health ratios. Debt treats a missing component as zero.
SELECT
    h.company,
    h.fiscal_year,
    h.Current_ratio,
    ROUND(c.Total_Current_Assets / NULLIF(c.Total_Current_Liabilities, 0), 3) AS expected_current,
    h.ROE,
    ROUND(c.Net_Income / NULLIF(c.Total_Stockholders_Equity, 0), 3) AS expected_roe,
    h.ROA,
    ROUND(c.Net_Income / NULLIF(c.Total_Assets, 0), 3) AS expected_roa
FROM financial_analytics.analytics.financial_health h
JOIN financial_analytics.clean.company_financials c
    ON h.company = c.company
   AND h.fiscal_year = c.fiscal_year
WHERE NOT (h.Current_ratio <=> ROUND(c.Total_Current_Assets / NULLIF(c.Total_Current_Liabilities, 0), 3))
   OR NOT (h.ROE <=> ROUND(c.Net_Income / NULLIF(c.Total_Stockholders_Equity, 0), 3))
   OR NOT (h.ROA <=> ROUND(c.Net_Income / NULLIF(c.Total_Assets, 0), 3));

-- 8. Peer set is the shared year, FY2025, one row per company.
SELECT fiscal_year, COUNT(*) AS company_count
FROM financial_analytics.analytics.peer_benchmarking
GROUP BY fiscal_year
HAVING fiscal_year <> 2025 OR COUNT(*) <> 6;

-- 9. Average_Rank is 9 of the 11 ranks. Operating expense growth and
--    liabilities to assets are displayed and excluded from the average.
SELECT
    company,
    Average_Rank,
    ROUND((
        Growth_Rate_Rank
        + Growth_Differential_Rank
        + Operating_Margin_Rank
        + Net_Income_Margin_Rank
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
        + Growth_Differential_Rank
        + Operating_Margin_Rank
        + Net_Income_Margin_Rank
        + Operating_Cash_Flow_Margin_Rank
        + Current_Ratio_Rank
        + Debt_to_Equity_Rank
        + ROA_Rank
        + ROE_Rank
    ) / 9.0, 3)
);

-- NVIDIA FY2025 anchor from the notebook result.
SELECT company, fiscal_year, Average_Rank
FROM financial_analytics.analytics.peer_benchmarking
WHERE company = 'NVIDIA'
  AND NOT (Average_Rank <=> 1.778);

-- 10. Executive summary is each company's own latest year.
--     Peer ranks attach only when that year is 2025.
SELECT company, fiscal_year, Growth_Rate, Growth_Rate_Rank
FROM financial_analytics.analytics.executive_summary
WHERE (
        company IN ('AMD', 'Adobe', 'Apple')
        AND (fiscal_year <> 2025 OR Growth_Rate_Rank IS NULL)
      )
   OR (
        company IN ('Microsoft', 'NVIDIA', 'CrowdStrike')
        AND (fiscal_year <> 2026 OR Growth_Rate_Rank IS NOT NULL OR Growth_Rate IS NULL)
      );
