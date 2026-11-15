-- Latest fiscal year for each company.
-- FY2025 benchmark ranks are attached on Company alone, including when the latest year is FY2026.
-- Rank columns are labeled FY2025_. Benchmark_Fiscal_Year is 2025 on every row.
-- ROA and ROE are the primary average-balance returns.
CREATE OR REPLACE VIEW financial_analytics.analytics.executive_summary AS
WITH latest AS (
    SELECT Company, MAX(Fiscal_Year) AS Latest_Fiscal_Year
    FROM financial_analytics.analytics.performance
    GROUP BY Company
)
SELECT
    p.Company,
    p.Fiscal_Year,
    2025 AS Benchmark_Fiscal_Year,
    gt.Revenue,
    gt.Growth_Rate,
    gt.Prior_Growth_Rate,
    gt.Growth_Differential,
    p.Gross_Margin_pct,
    p.Operating_Margin_pct,
    p.Net_Income_Margin_pct,
    p.Operating_Income_Growth,
    p.Net_Income_Growth,
    p.Operating_Expense_Growth,
    p.Operating_Expense_to_Revenue,
    p.Revenue_Growth_Minus_Opex_Growth,
    p.Operating_Cash_Flow_Margin_pct,
    p.Operating_Cash_Flow_Growth,
    p.Cash_Conversion_Ratio,
    p.Cash_Conversion_Meaningful,
    p.Free_Cash_Flow,
    p.Free_Cash_Flow_Margin_pct,
    fh.Current_ratio,
    fh.debt_to_equity_ratio,
    fh.Liabilities_to_Assets,
    fh.ROA,
    fh.ROE,
    fh.ROA_Ending,
    fh.ROE_Ending,
    fh.ROA_Avg,
    fh.ROE_Avg,
    fh.ROA_Uses_Ending_Balance,
    fh.ROE_Uses_Ending_Balance,
    fh.Total_Liabilities_Imputed,
    fh.Short_Term_Debt_Reported,
    fh.Long_Term_Debt_Reported,
    pb.Growth_Rate_Rank AS FY2025_Growth_Rate_Rank,
    pb.Operating_Margin_Rank AS FY2025_Operating_Margin_Rank,
    pb.Net_Income_Margin_Rank AS FY2025_Net_Income_Margin_Rank,
    pb.Operating_Expense_to_Revenue_Rank AS FY2025_Operating_Expense_to_Revenue_Rank,
    pb.Operating_Cash_Flow_Margin_Rank AS FY2025_Operating_Cash_Flow_Margin_Rank,
    pb.Current_Ratio_Rank AS FY2025_Current_Ratio_Rank,
    pb.Debt_to_Equity_Rank AS FY2025_Debt_to_Equity_Rank,
    pb.ROA_Rank AS FY2025_ROA_Rank,
    pb.ROE_Rank AS FY2025_ROE_Rank,
    pb.Average_Rank AS FY2025_Average_Rank
FROM financial_analytics.analytics.performance p
INNER JOIN latest
    ON p.Company = latest.Company
    AND p.Fiscal_Year = latest.Latest_Fiscal_Year
LEFT JOIN financial_analytics.analytics.growth_trend gt
    ON p.Company = gt.Company
    AND p.Fiscal_Year = gt.Fiscal_Year
LEFT JOIN financial_analytics.analytics.financial_health fh
    ON p.Company = fh.Company
    AND p.Fiscal_Year = fh.Fiscal_Year
LEFT JOIN financial_analytics.analytics.peer_benchmarking pb
    ON p.Company = pb.Company
