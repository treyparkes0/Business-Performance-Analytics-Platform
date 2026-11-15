-- Profitability, operating efficiency, and cash conversion.
-- Cash_Conversion_Ratio keeps the raw OCF / Net Income value, rounded to 3 decimals, and is null when net income is 0.
-- Cash_Conversion_Meaningful is false when net income is zero or negative, or when
-- abs(OCF / Net Income) > 5. A ratio of exactly 5 stays meaningful.
-- The threshold comparison uses the unrounded ratio.
-- Revenue_Growth_Minus_Opex_Growth subtracts unrounded opex growth from the already rounded Growth_Rate.
-- Free_Cash_Flow = OCF - Capital Expenditures. Capex is a positive spend.
CREATE OR REPLACE VIEW financial_analytics.analytics.performance AS
WITH base AS (
    SELECT
        c.Company,
        c.Fiscal_Year,
        c.Revenue,
        c.Gross_Profit,
        c.Net_Income,
        c.Operating_Income,
        c.Operating_Expenses,
        c.Cash_Flow_from_Operating_Activities,
        c.Capital_Expenditures,
        LAG(c.Operating_Income) OVER (PARTITION BY c.Company ORDER BY c.Fiscal_Year) AS Prior_Operating_Income,
        LAG(c.Net_Income) OVER (PARTITION BY c.Company ORDER BY c.Fiscal_Year) AS Prior_Net_Income,
        LAG(c.Operating_Expenses) OVER (PARTITION BY c.Company ORDER BY c.Fiscal_Year) AS Prior_Opex,
        LAG(c.Cash_Flow_from_Operating_Activities) OVER (PARTITION BY c.Company ORDER BY c.Fiscal_Year) AS Prior_OCF
    FROM financial_analytics.clean.company_financials c
)
SELECT
    b.Company,
    b.Fiscal_Year,
    b.Revenue,
    b.Gross_Profit,
    b.Net_Income,
    b.Operating_Income,
    b.Operating_Expenses,
    b.Cash_Flow_from_Operating_Activities,
    b.Capital_Expenditures,
    gt.Growth_Rate,
    gt.Net_Income_Margin_pct,
    round(b.Gross_Profit / NULLIF(b.Revenue, 0), 3) AS Gross_Margin_pct,
    round(b.Operating_Income / NULLIF(b.Revenue, 0), 3) AS Operating_Margin_pct,
    round((b.Operating_Income - b.Prior_Operating_Income) / NULLIF(b.Prior_Operating_Income, 0), 3) AS Operating_Income_Growth,
    round((b.Net_Income - b.Prior_Net_Income) / NULLIF(b.Prior_Net_Income, 0), 3) AS Net_Income_Growth,
    round((b.Operating_Expenses - b.Prior_Opex) / NULLIF(b.Prior_Opex, 0), 3) AS Operating_Expense_Growth,
    round(b.Operating_Expenses / NULLIF(b.Revenue, 0), 3) AS Operating_Expense_to_Revenue,
    round(
        gt.Growth_Rate - ((b.Operating_Expenses - b.Prior_Opex) / NULLIF(b.Prior_Opex, 0)),
        3
    ) AS Revenue_Growth_Minus_Opex_Growth,
    round(b.Cash_Flow_from_Operating_Activities / NULLIF(b.Revenue, 0), 3) AS Operating_Cash_Flow_Margin_pct,
    round(
        (b.Cash_Flow_from_Operating_Activities - b.Prior_OCF) / NULLIF(b.Prior_OCF, 0),
        3
    ) AS Operating_Cash_Flow_Growth,
    round(b.Cash_Flow_from_Operating_Activities / NULLIF(b.Net_Income, 0), 3) AS Cash_Conversion_Ratio,
    CASE
        WHEN b.Net_Income IS NULL OR b.Cash_Flow_from_Operating_Activities IS NULL THEN NULL
        WHEN b.Net_Income <= 0 THEN FALSE
        WHEN abs(b.Cash_Flow_from_Operating_Activities / b.Net_Income) > 5 THEN FALSE
        ELSE TRUE
    END AS Cash_Conversion_Meaningful,
    round(b.Cash_Flow_from_Operating_Activities - b.Capital_Expenditures, 3) AS Free_Cash_Flow,
    round(
        round(b.Cash_Flow_from_Operating_Activities - b.Capital_Expenditures, 3) / NULLIF(b.Revenue, 0),
        3
    ) AS Free_Cash_Flow_Margin_pct
FROM base b
LEFT JOIN financial_analytics.analytics.growth_trend gt
    ON b.Company = gt.Company
    AND b.Fiscal_Year = gt.Fiscal_Year
