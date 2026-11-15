-- Revenue growth and net income margin.
-- Prior year is the previous fiscal year for the same company.
-- Growth_Differential uses the unrounded growth rates, then each result is rounded to 3 decimals.
CREATE OR REPLACE VIEW financial_analytics.analytics.growth_trend AS
WITH growth AS (
    SELECT
        Company,
        Fiscal_Year,
        Revenue,
        Net_Income,
        (Revenue - LAG(Revenue) OVER (PARTITION BY Company ORDER BY Fiscal_Year))
            / NULLIF(LAG(Revenue) OVER (PARTITION BY Company ORDER BY Fiscal_Year), 0) AS Growth_Rate
    FROM financial_analytics.clean.company_financials
),
growth_metrics AS (
    SELECT
        Company,
        Fiscal_Year,
        Revenue,
        Net_Income,
        Growth_Rate,
        LAG(Growth_Rate) OVER (PARTITION BY Company ORDER BY Fiscal_Year) AS Prior_Growth_Rate,
        Growth_Rate - LAG(Growth_Rate) OVER (PARTITION BY Company ORDER BY Fiscal_Year) AS Growth_Differential
    FROM growth
)
SELECT
    Company,
    Fiscal_Year,
    Revenue,
    Net_Income,
    round(Growth_Rate, 3) AS Growth_Rate,
    round(Prior_Growth_Rate, 3) AS Prior_Growth_Rate,
    round(Growth_Differential, 3) AS Growth_Differential,
    round(Net_Income / NULLIF(Revenue, 0), 3) AS Net_Income_Margin_pct
FROM growth_metrics
