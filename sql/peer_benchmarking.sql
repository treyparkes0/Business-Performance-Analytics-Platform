-- FY2025 peer ranks. FY2025 is the last fiscal year present for every company.
-- The ranked set is exactly these nine metrics. Average_Rank is their equal-weight mean, rounded to 3 decimals.
-- Higher is better: revenue growth, operating margin, net income margin, OCF margin, current ratio, ROA, ROE.
-- Lower is better: operating expense / revenue, debt-to-equity.
-- Ties: RANK() shares the best rank and skips the next rank (pandas rank method='min').
-- Missing values: NULLS LAST, so a missing metric ranks after every reported value. Missing values tie with each other.
-- ROA and ROE are the primary returns (average balances, ending balance only when there is no prior year).
-- The value column sits next to its rank.
CREATE OR REPLACE VIEW financial_analytics.analytics.peer_benchmarking AS
WITH ranked_metrics AS (
    SELECT
        p.Company,
        p.Fiscal_Year,
        gt.Growth_Rate,
        p.Operating_Margin_pct,
        p.Net_Income_Margin_pct,
        p.Operating_Expense_to_Revenue,
        p.Operating_Cash_Flow_Margin_pct,
        fh.Current_ratio,
        fh.debt_to_equity_ratio,
        fh.ROA,
        fh.ROE,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY gt.Growth_Rate DESC NULLS LAST) AS Growth_Rate_Rank,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY p.Operating_Margin_pct DESC NULLS LAST) AS Operating_Margin_Rank,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY p.Net_Income_Margin_pct DESC NULLS LAST) AS Net_Income_Margin_Rank,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY p.Operating_Expense_to_Revenue ASC NULLS LAST) AS Operating_Expense_to_Revenue_Rank,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY p.Operating_Cash_Flow_Margin_pct DESC NULLS LAST) AS Operating_Cash_Flow_Margin_Rank,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY fh.Current_ratio DESC NULLS LAST) AS Current_Ratio_Rank,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY fh.debt_to_equity_ratio ASC NULLS LAST) AS Debt_to_Equity_Rank,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY fh.ROA DESC NULLS LAST) AS ROA_Rank,
        RANK() OVER (PARTITION BY p.Fiscal_Year ORDER BY fh.ROE DESC NULLS LAST) AS ROE_Rank
    FROM financial_analytics.analytics.performance p
    LEFT JOIN financial_analytics.analytics.financial_health fh
        ON p.Company = fh.Company
        AND p.Fiscal_Year = fh.Fiscal_Year
    LEFT JOIN financial_analytics.analytics.growth_trend gt
        ON p.Company = gt.Company
        AND p.Fiscal_Year = gt.Fiscal_Year
    WHERE p.Fiscal_Year = 2025
)
SELECT
    Company,
    Fiscal_Year,
    Growth_Rate,
    Growth_Rate_Rank,
    Operating_Margin_pct,
    Operating_Margin_Rank,
    Net_Income_Margin_pct,
    Net_Income_Margin_Rank,
    Operating_Expense_to_Revenue,
    Operating_Expense_to_Revenue_Rank,
    Operating_Cash_Flow_Margin_pct,
    Operating_Cash_Flow_Margin_Rank,
    Current_ratio,
    Current_Ratio_Rank,
    debt_to_equity_ratio,
    Debt_to_Equity_Rank,
    ROA,
    ROA_Rank,
    ROE,
    ROE_Rank,
    round((
        Growth_Rate_Rank
        + Operating_Margin_Rank
        + Net_Income_Margin_Rank
        + Operating_Expense_to_Revenue_Rank
        + Operating_Cash_Flow_Margin_Rank
        + Current_Ratio_Rank
        + Debt_to_Equity_Rank
        + ROA_Rank
        + ROE_Rank
    ) / 9.0, 3) AS Average_Rank
FROM ranked_metrics
