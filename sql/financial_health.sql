-- Liquidity, leverage, and returns.
-- Total debt coalesces a missing short-term or long-term leg to 0. The reported flags stay false when the source was null.
-- CrowdStrike short-term debt is unreported for FY2021-FY2026 and is treated as 0.
-- AMD null Total_Liabilities are imputed as Total Assets - Total Stockholders' Equity because AMD companyfacts has no Total_Liabilities tag.
-- Other companies are not imputed. Total_Liabilities_Imputed is true only on the AMD rows this expression fills.
-- If a cleaning UPDATE already replaced those nulls, the flag is false because the null is gone. The dollar amount still matches assets minus equity.
-- Primary ROA and ROE use average balances, (current + prior) / 2, partitioned by ticker.
-- Ending balances are used only when there is no prior year. ROA_Ending and ROE_Ending always use the ending balance.
-- ROA_Avg and ROE_Avg are null when there is no prior year.
CREATE OR REPLACE VIEW financial_analytics.analytics.financial_health AS
WITH source AS (
    SELECT
        Company,
        Ticker,
        Fiscal_Year,
        Total_Assets,
        Total_Stockholders_Equity,
        Total_Current_Assets,
        Total_Current_Liabilities,
        Short_Term_Debt,
        Long_Term_Debt,
        Net_Income,
        Cash_Flow_from_Operating_Activities,
        CASE
            WHEN Company = 'AMD' AND Total_Liabilities IS NULL
                THEN Total_Assets - Total_Stockholders_Equity
            ELSE Total_Liabilities
        END AS Total_Liabilities,
        CASE
            WHEN Company = 'AMD' AND Total_Liabilities IS NULL THEN TRUE
            ELSE FALSE
        END AS Total_Liabilities_Imputed
    FROM financial_analytics.clean.company_financials
),
with_prior AS (
    SELECT
        source.*,
        LAG(Total_Assets) OVER (PARTITION BY Ticker ORDER BY Fiscal_Year) AS Prior_Total_Assets,
        LAG(Total_Stockholders_Equity) OVER (PARTITION BY Ticker ORDER BY Fiscal_Year) AS Prior_Total_Equity
    FROM source
)
SELECT
    Company,
    Fiscal_Year,
    Total_Assets,
    Total_Liabilities,
    Total_Liabilities_Imputed,
    Total_Stockholders_Equity,
    Total_Current_Assets,
    Total_Current_Liabilities,
    round(Total_Current_Assets / NULLIF(Total_Current_Liabilities, 0), 3) AS Current_ratio,
    COALESCE(Short_Term_Debt, 0) + COALESCE(Long_Term_Debt, 0) AS Total_Debt,
    (Short_Term_Debt IS NOT NULL) AS Short_Term_Debt_Reported,
    (Long_Term_Debt IS NOT NULL) AS Long_Term_Debt_Reported,
    round(
        (COALESCE(Short_Term_Debt, 0) + COALESCE(Long_Term_Debt, 0))
            / NULLIF(Total_Stockholders_Equity, 0),
        3
    ) AS debt_to_equity_ratio,
    round(Total_Liabilities / NULLIF(Total_Assets, 0), 3) AS Liabilities_to_Assets,
    round(Net_Income / NULLIF(Total_Assets, 0), 3) AS ROA_Ending,
    round(Net_Income / NULLIF(Total_Stockholders_Equity, 0), 3) AS ROE_Ending,
    round(
        Net_Income / NULLIF((Total_Assets + Prior_Total_Assets) / 2, 0),
        3
    ) AS ROA_Avg,
    round(
        Net_Income / NULLIF((Total_Stockholders_Equity + Prior_Total_Equity) / 2, 0),
        3
    ) AS ROE_Avg,
    CASE WHEN Prior_Total_Assets IS NULL THEN TRUE ELSE FALSE END AS ROA_Uses_Ending_Balance,
    CASE WHEN Prior_Total_Equity IS NULL THEN TRUE ELSE FALSE END AS ROE_Uses_Ending_Balance,
    round(
        CASE
            WHEN Prior_Total_Assets IS NULL THEN Net_Income / NULLIF(Total_Assets, 0)
            ELSE Net_Income / NULLIF((Total_Assets + Prior_Total_Assets) / 2, 0)
        END,
        3
    ) AS ROA,
    round(
        CASE
            WHEN Prior_Total_Equity IS NULL THEN Net_Income / NULLIF(Total_Stockholders_Equity, 0)
            ELSE Net_Income / NULLIF((Total_Stockholders_Equity + Prior_Total_Equity) / 2, 0)
        END,
        3
    ) AS ROE,
    Cash_Flow_from_Operating_Activities
FROM with_prior
