# Metric notes

Six companies: Microsoft, Apple, NVIDIA, Adobe, AMD, and CrowdStrike. 33 company-years. AMD, Adobe, and Apple stop at FY2025. Microsoft, NVIDIA, and CrowdStrike go through FY2026. FY2025 is the last year all six have.

ROA and ROE use the average of the current and prior balance. FY2021 uses the ending balance, because there is no prior year, and those six rows are flagged. `ROA_Avg` and `ROE_Avg` are blank in FY2021.

Net income growth and operating income growth are shown as a percent only when both years are profits. Otherwise the display is "loss widened," "loss narrowed," or "not meaningful." The calculated ratio is kept and is not plotted. CrowdStrike net income is "loss widened" in FY2022 and FY2026, "loss narrowed" in FY2023, and "not meaningful" in FY2024 and FY2025 because earnings changed sign. The FY2026 calculated ratio is 9.662. That percent is not a growth rate. The loss went from $15.2 million to $162.5 million.

Cash conversion is operating cash flow divided by net income, rounded to 3 decimals. It is not meaningful when net income is zero or negative, or when the absolute ratio is greater than 5. All six CrowdStrike years are not meaningful. The FY2025 ratio is -90.659.

CrowdStrike did not report short-term debt. Total debt is the long-term amount, and `Short_Term_Debt_Reported` is false. A reported zero is kept as zero.

AMD has no `Total_Liabilities` fact in `data/processed/sec_company_financials_clean.csv`. The amount is assets minus equity, and `Total_Liabilities_Imputed` is true for all five AMD years.

FY2025 average rank uses nine metrics, equal weight. Higher is better for revenue growth, operating margin, net income margin, operating-cash-flow margin, current ratio, ROA, and ROE. Lower is better for operating expense / revenue and debt-to-equity. Ties share the best rank. Missing values rank last.

| Company | Average rank |
|---|---|
| NVIDIA | 1.222 |
| Microsoft | 3.111 |
| AMD | 3.889 |
| Adobe | 3.889 |
| Apple | 4.000 |
| CrowdStrike | 4.889 |

Growth differential, operating-expense growth, and liabilities-to-assets are not in that average.
