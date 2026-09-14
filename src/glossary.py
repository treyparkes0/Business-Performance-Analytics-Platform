"""Column meanings for analytics views. Formulas match src/bp_metrics.py."""

from __future__ import annotations

# Views align with app navigation and source view names.
VIEW_COMPANY_PERFORMANCE = "Company Performance"
VIEW_OPERATIONS = "Operations"
VIEW_PROFITABILITY = "Profitability"
VIEW_CASH = "Cash Flow"
VIEW_HEALTH = "Financial Health"
VIEW_PEERS = "Peer Benchmarking"
VIEW_OVERVIEW = "Overview"

SOURCE = "Source"
CALCULATED = "Calculated"

ROUND = "Rounded to 3 decimal places."
PRIOR_CO = "Prior year is the previous fiscal year for the same company."
PRIOR_TICKER = "Prior year is the previous fiscal year for the same ticker."


def _term(
    column: str,
    label: str,
    meaning: str,
    kind: str,
    views: list[str],
    calculation: str = "—",
) -> dict[str, str | list[str]]:
    return {
        "column": column,
        "label": label,
        "meaning": meaning,
        "kind": kind,
        "views": views,
        "calculation": calculation,
    }


TERMS: list[dict[str, str | list[str]]] = [
    _term(
        "Company",
        "Company",
        "Company name used across all views.",
        SOURCE,
        [VIEW_OVERVIEW, VIEW_COMPANY_PERFORMANCE, VIEW_OPERATIONS, VIEW_PROFITABILITY, VIEW_CASH, VIEW_HEALTH, VIEW_PEERS],
    ),
    _term(
        "Fiscal_Year",
        "Fiscal Year",
        "Fiscal year of the reported financials (company fiscal calendar, not always calendar year).",
        SOURCE,
        [VIEW_OVERVIEW, VIEW_COMPANY_PERFORMANCE, VIEW_OPERATIONS, VIEW_PROFITABILITY, VIEW_CASH, VIEW_HEALTH, VIEW_PEERS],
    ),
    _term(
        "Ticker",
        "Ticker",
        "Stock ticker. Used to line up prior-year balance-sheet amounts for some health ratios.",
        SOURCE,
        [VIEW_HEALTH],
    ),
    _term(
        "Revenue",
        "Revenue",
        "Net sales / total revenue for the fiscal year.",
        SOURCE,
        [VIEW_OVERVIEW, VIEW_COMPANY_PERFORMANCE, VIEW_OPERATIONS, VIEW_CASH],
    ),
    _term(
        "Net_Income",
        "Net Income",
        "Bottom-line earnings after expenses and taxes.",
        SOURCE,
        [VIEW_COMPANY_PERFORMANCE, VIEW_PROFITABILITY, VIEW_CASH],
    ),
    _term(
        "Gross_Profit",
        "Gross Profit",
        "Revenue minus cost of revenue.",
        SOURCE,
        [VIEW_PROFITABILITY],
    ),
    _term(
        "Operating_Income",
        "Operating Income",
        "Profit from operations before interest and taxes (operating profit).",
        SOURCE,
        [VIEW_PROFITABILITY],
    ),
    _term(
        "Operating_Expenses",
        "Operating Expenses",
        "Operating costs for the year (for example R&D, sales, and administration where reported that way).",
        SOURCE,
        [VIEW_OPERATIONS],
    ),
    _term(
        "Cash_Flow_from_Operating_Activities",
        "Operating Cash Flow",
        "Cash generated (or used) by core operations, from the cash-flow statement.",
        SOURCE,
        [VIEW_OVERVIEW, VIEW_CASH, VIEW_HEALTH],
    ),
    _term(
        "Capital_Expenditures",
        "Capital Expenditures",
        "Cash spent on property, plant, and equipment (capex). Stored as a positive spend amount.",
        SOURCE,
        [VIEW_CASH],
    ),
    _term(
        "Total_Assets",
        "Total Assets",
        "Total assets on the balance sheet.",
        SOURCE,
        [VIEW_HEALTH],
    ),
    _term(
        "Total_Liabilities",
        "Total Liabilities",
        "Total liabilities on the balance sheet. If missing in the source file, it is filled as assets minus equity.",
        SOURCE,
        [VIEW_HEALTH],
        "If missing: Total Assets − Total Stockholders' Equity.",
    ),
    _term(
        "Total_Stockholders_Equity",
        "Stockholders' Equity",
        "Book value of equity (assets attributable to shareholders).",
        SOURCE,
        [VIEW_HEALTH],
    ),
    _term(
        "Total_Current_Assets",
        "Current Assets",
        "Assets expected to be converted to cash within a year.",
        SOURCE,
        [VIEW_HEALTH],
    ),
    _term(
        "Total_Current_Liabilities",
        "Current Liabilities",
        "Obligations due within a year.",
        SOURCE,
        [VIEW_HEALTH],
    ),
    _term(
        "Short_Term_Debt",
        "Short-Term Debt",
        "Debt due within a year. Missing values are treated as 0 when building total debt.",
        SOURCE,
        [VIEW_HEALTH],
    ),
    _term(
        "Long_Term_Debt",
        "Long-Term Debt",
        "Debt due after one year. Missing values are treated as 0 when building total debt.",
        SOURCE,
        [VIEW_HEALTH],
    ),
    _term(
        "Growth_Rate",
        "Revenue Growth",
        "Year-over-year change in revenue. Shows whether the top line is expanding or shrinking.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_COMPANY_PERFORMANCE, VIEW_OPERATIONS, VIEW_PEERS],
        f"(Revenue − prior-year Revenue) / prior-year Revenue. {PRIOR_CO} {ROUND}",
    ),
    _term(
        "Prior_Growth_Rate",
        "Prior Growth Rate",
        "Last year's revenue growth rate. Used to see whether growth is speeding up or slowing down.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_COMPANY_PERFORMANCE],
        f"Prior-year Growth Rate for the same company. {ROUND}",
    ),
    _term(
        "Growth_Differential",
        "Growth Rate Change",
        "Change in the growth rate itself (acceleration or deceleration), not the change in revenue dollars.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_COMPANY_PERFORMANCE, VIEW_PEERS],
        f"Growth Rate − Prior Growth Rate. {ROUND}",
    ),
    _term(
        "Net_Income_Margin_pct",
        "Net Income Margin",
        "Share of revenue that becomes net income.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_COMPANY_PERFORMANCE, VIEW_PROFITABILITY, VIEW_PEERS],
        f"Net Income / Revenue. {ROUND}",
    ),
    _term(
        "Gross_Margin_pct",
        "Gross Margin",
        "Share of revenue left after cost of revenue.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_PROFITABILITY],
        f"Gross Profit / Revenue. {ROUND}",
    ),
    _term(
        "Operating_Margin_pct",
        "Operating Margin",
        "Share of revenue left after operating costs (operating profit margin).",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_PROFITABILITY, VIEW_PEERS],
        f"Operating Income / Revenue. {ROUND}",
    ),
    _term(
        "Operating_Income_Growth",
        "Operating Income Growth",
        "Year-over-year change in operating income.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_PROFITABILITY],
        f"(Operating Income − prior-year Operating Income) / prior-year Operating Income. {PRIOR_CO} {ROUND}",
    ),
    _term(
        "Net_Income_Growth",
        "Net Income Growth",
        "Year-over-year change in net income.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_PROFITABILITY],
        f"(Net Income − prior-year Net Income) / prior-year Net Income. {PRIOR_CO} {ROUND}",
    ),
    _term(
        "Operating_Expense_Growth",
        "Operating Expense Growth",
        "Year-over-year change in operating expenses. Lower growth relative to revenue is usually better for efficiency.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_OPERATIONS, VIEW_PEERS],
        f"(Operating Expenses − prior-year Operating Expenses) / prior-year Operating Expenses. {PRIOR_CO} {ROUND}",
    ),
    _term(
        "Operating_Expense_to_Revenue",
        "Operating Expense / Revenue",
        "Operating expenses as a share of revenue. A lower ratio means costs are smaller relative to sales.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_OPERATIONS, VIEW_PEERS],
        f"Operating Expenses / Revenue. {ROUND}",
    ),
    _term(
        "Revenue_Growth_Minus_Opex_Growth",
        "Revenue Growth − Operating Expense Growth",
        "Whether revenue is growing faster than operating costs. Positive means sales are outpacing opex growth.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_OPERATIONS],
        f"Revenue Growth − Operating Expense Growth (opex growth is used before rounding). {ROUND}",
    ),
    _term(
        "Operating_Cash_Flow_Margin_pct",
        "OCF Margin",
        "Operating cash flow as a share of revenue (cash-generation efficiency).",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_CASH, VIEW_PEERS],
        f"Operating Cash Flow / Revenue. {ROUND}",
    ),
    _term(
        "Operating_Cash_Flow_Growth",
        "OCF Growth",
        "Year-over-year change in operating cash flow.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_CASH],
        f"(Operating Cash Flow − prior-year Operating Cash Flow) / prior-year Operating Cash Flow. {PRIOR_CO} {ROUND}",
    ),
    _term(
        "Cash_Conversion_Ratio",
        "Cash Conversion Ratio",
        "How much operating cash is generated per dollar of net income. Can be high when earnings are small or negative.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_CASH],
        f"Operating Cash Flow / Net Income. {ROUND}",
    ),
    _term(
        "Free_Cash_Flow",
        "Free Cash Flow",
        "Operating cash left after capital expenditures.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_CASH],
        f"Operating Cash Flow − Capital Expenditures. {ROUND}",
    ),
    _term(
        "Free_Cash_Flow_Margin_pct",
        "Free Cash Flow Margin",
        "Free cash flow as a share of revenue.",
        CALCULATED,
        [VIEW_CASH],
        f"Free Cash Flow / Revenue. {ROUND}",
    ),
    _term(
        "Total_Debt",
        "Total Debt",
        "Interest-bearing debt used in the debt-to-equity ratio.",
        CALCULATED,
        [VIEW_HEALTH],
        "Short-Term Debt (missing = 0) + Long-Term Debt (missing = 0).",
    ),
    _term(
        "Current_ratio",
        "Current Ratio",
        "Short-term liquidity: current assets covering current liabilities. Below 1.0 means current liabilities exceed current assets.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_HEALTH, VIEW_PEERS],
        f"Current Assets / Current Liabilities. {ROUND}",
    ),
    _term(
        "debt_to_equity_ratio",
        "Debt-to-Equity",
        "Leverage: total debt relative to book equity. Lower generally means less debt versus equity.",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_HEALTH, VIEW_PEERS],
        f"Total Debt / Stockholders' Equity. {ROUND}",
    ),
    _term(
        "Liabilities_to_Assets",
        "Liabilities-to-Assets",
        "Share of assets financed by liabilities (broader than interest-bearing debt only).",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_HEALTH, VIEW_PEERS],
        f"Total Liabilities / Total Assets. {ROUND}",
    ),
    _term(
        "ROA",
        "ROA",
        "Return on assets: earnings generated from the asset base (end-of-year assets).",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_HEALTH, VIEW_PEERS],
        f"Net Income / Total Assets. {ROUND}",
    ),
    _term(
        "ROE",
        "ROE",
        "Return on equity: earnings generated from book equity (end-of-year equity).",
        CALCULATED,
        [VIEW_OVERVIEW, VIEW_HEALTH, VIEW_PEERS],
        f"Net Income / Stockholders' Equity. {ROUND}",
    ),
    _term(
        "ROA_Avg",
        "ROA (Average Assets)",
        "Return on assets using average assets over two years, which smooths one-year balance-sheet swings.",
        CALCULATED,
        [VIEW_HEALTH],
        f"Net Income / ((Total Assets + prior-year Total Assets) / 2). {PRIOR_TICKER} {ROUND}",
    ),
    _term(
        "ROE_Avg",
        "ROE (Average Equity)",
        "Return on equity using average equity over two years.",
        CALCULATED,
        [VIEW_HEALTH],
        f"Net Income / ((Stockholders' Equity + prior-year Stockholders' Equity) / 2). {PRIOR_TICKER} {ROUND}",
    ),
    _term(
        "Growth_Rate_Rank",
        "Revenue Growth Rank",
        "Peer rank for revenue growth in the benchmark year (FY2025). Rank 1 is the highest growth.",
        CALCULATED,
        [VIEW_PEERS, VIEW_OVERVIEW],
        "Rank of Growth Rate among companies, highest first (method = min).",
    ),
    _term(
        "Growth_Differential_Rank",
        "Growth Rate Change Rank",
        "Peer rank for growth acceleration. Rank 1 is the largest (most positive) growth differential.",
        CALCULATED,
        [VIEW_PEERS],
        "Rank of Growth Rate Change among companies, highest first (method = min).",
    ),
    _term(
        "Operating_Margin_Rank",
        "Operating Margin Rank",
        "Peer rank for operating margin. Rank 1 is the highest margin.",
        CALCULATED,
        [VIEW_PEERS, VIEW_OVERVIEW],
        "Rank of Operating Margin among companies, highest first (method = min).",
    ),
    _term(
        "Net_Income_Margin_Rank",
        "Net Income Margin Rank",
        "Peer rank for net income margin. Rank 1 is the highest margin.",
        CALCULATED,
        [VIEW_PEERS, VIEW_OVERVIEW],
        "Rank of Net Income Margin among companies, highest first (method = min).",
    ),
    _term(
        "Operating_Cash_Flow_Margin_Rank",
        "OCF Margin Rank",
        "Peer rank for operating cash-flow margin. Rank 1 is the highest margin.",
        CALCULATED,
        [VIEW_PEERS, VIEW_OVERVIEW],
        "Rank of OCF Margin among companies, highest first (method = min).",
    ),
    _term(
        "Operating_Expense_Growth_Rank",
        "Operating Expense Growth Rank",
        "Peer rank for opex growth. Rank 1 is the lowest opex growth (costs rising more slowly).",
        CALCULATED,
        [VIEW_PEERS, VIEW_OVERVIEW],
        "Rank of Operating Expense Growth among companies, lowest first (method = min).",
    ),
    _term(
        "Current_Ratio_Rank",
        "Current Ratio Rank",
        "Peer rank for current ratio. Rank 1 is the highest liquidity.",
        CALCULATED,
        [VIEW_PEERS],
        "Rank of Current Ratio among companies, highest first (method = min).",
    ),
    _term(
        "Debt_to_Equity_Rank",
        "Debt-to-Equity Rank",
        "Peer rank for leverage. Rank 1 is the lowest debt-to-equity.",
        CALCULATED,
        [VIEW_PEERS],
        "Rank of Debt-to-Equity among companies, lowest first (method = min).",
    ),
    _term(
        "Liabilities_to_Assets_Rank",
        "Liabilities-to-Assets Rank",
        "Peer rank for liabilities vs assets. Rank 1 is the lowest ratio.",
        CALCULATED,
        [VIEW_PEERS],
        "Rank of Liabilities-to-Assets among companies, lowest first (method = min).",
    ),
    _term(
        "ROA_Rank",
        "ROA Rank",
        "Peer rank for return on assets. Rank 1 is the highest ROA.",
        CALCULATED,
        [VIEW_PEERS, VIEW_OVERVIEW],
        "Rank of ROA among companies, highest first (method = min).",
    ),
    _term(
        "ROE_Rank",
        "ROE Rank",
        "Peer rank for return on equity. Rank 1 is the highest ROE.",
        CALCULATED,
        [VIEW_PEERS, VIEW_OVERVIEW],
        "Rank of ROE among companies, highest first (method = min).",
    ),
    _term(
        "Average_Rank",
        "Average Rank",
        "Simple average of nine peer ranks. Lower average means stronger overall standing in that benchmark year.",
        CALCULATED,
        [VIEW_PEERS],
        "Average of Growth Rate, Growth Differential, Operating Margin, Net Income Margin, OCF Margin, Current Ratio, Debt-to-Equity, ROA, and ROE ranks. Operating Expense Growth Rank and Liabilities-to-Assets Rank are not in this average. "
        + ROUND,
    ),
    _term(
        "Rank",
        "Rank",
        "On the Peer Benchmarking page, rank for the metric you selected (not the nine-metric average).",
        CALCULATED,
        [VIEW_PEERS],
        "Rank of the selected metric in the chosen fiscal year. Higher-is-better metrics are ranked highest first; lower-is-better metrics (opex / revenue, debt-to-equity) are ranked lowest first (method = min).",
    ),
]


APP_VIEWS = [
    VIEW_OVERVIEW,
    VIEW_COMPANY_PERFORMANCE,
    VIEW_OPERATIONS,
    VIEW_PROFITABILITY,
    VIEW_CASH,
    VIEW_HEALTH,
    VIEW_PEERS,
]


def filter_terms(
    view: str = "All views",
    kind: str = "All",
    search: str = "",
    metric: str = "All metrics",
) -> list[dict[str, str | list[str]]]:
    rows = TERMS
    if view != "All views":
        rows = [t for t in rows if view in t["views"]]
    if kind != "All":
        rows = [t for t in rows if t["kind"] == kind]
    needle = search.strip().lower()
    if needle:
        rows = [
            t
            for t in rows
            if needle in str(t["label"]).lower()
            or needle in str(t["column"]).lower()
            or needle in str(t["meaning"]).lower()
        ]
    if metric != "All metrics":
        rows = [t for t in rows if t["label"] == metric]
    return rows


def metric_labels(rows: list[dict[str, str | list[str]]] | None = None) -> list[str]:
    source = rows if rows is not None else TERMS
    return sorted({str(t["label"]) for t in source})


def terms_frame(rows: list[dict[str, str | list[str]]]):
    import pandas as pd

    records = []
    for t in rows:
        records.append(
            {
                "Metric": t["label"],
                "Type": t["kind"],
                "What it means": t["meaning"],
                "How it is calculated": t["calculation"],
            }
        )
    return pd.DataFrame(records)
