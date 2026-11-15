# Business Performance Analytics

Interactive review of operating performance for six technology companies: Microsoft, Apple, NVIDIA, Adobe, AMD, and CrowdStrike.

This is an end-to-end business performance analytics project using real SEC financial data. It compares growth, profitability, operating efficiency, cash generation, and financial health for six technology companies, and records where management attention should go. The numbers come from annual filings, prepared in Python and calculated with SQL. It is not a trading tool, a valuation model, or an investment recommendation.

AI-assisted development tools were used to support coding, debugging, and documentation. Project direction, analytical scope, metric selection, data validation, and interpretation were reviewed and guided throughout development.

Open the app: [Business Performance Analytics](https://business-performance-analytics-platform-bus97yysmxxf9p6kixffdi.streamlit.app/)

## Source

Annual Form 10-K facts from the [SEC Company Facts API](https://data.sec.gov/api/xbrl/companyfacts/), fiscal years 2021 onward. Each company keeps its own fiscal year. Microsoft, NVIDIA, and CrowdStrike report through FY2026. AMD, Adobe, and Apple stop at FY2025. FY2025 is the last year available for every company.

The metrics are defined in `Business Performance Analytics.ipynb` and repeated in `src/bp_metrics.py`. The Streamlit app reads the warehouse views when the three Databricks settings are set. Otherwise it builds them from `data/processed/company_financials_wide.csv`. Formulas, null rules, and accepted data gaps are in [docs/sql_metrics.md](docs/sql_metrics.md).

## Overview

![Business Performance Overview](docs/overview.png)

The picture is Overview for all six companies. Each company has its own row, and every number on that row is visible. The year on the row is that company's latest fiscal year.
