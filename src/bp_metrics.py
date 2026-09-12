"""
Analytics views matching the Databricks notebook.

Source table: data/processed/company_financials_wide.csv
(same grain as financial_analytics.clean.company_financials)

Views:
  growth_trend, performance, financial_health, peer_benchmarking,
  executive_summary

SQL is not re-derived in a different way. Rounding (3 decimals),
column names, FY2025 peer filter, and latest-year executive summary
follow the notebook CREATE VIEW cells.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
WIDE_CSV = ROOT / "data" / "processed" / "company_financials_wide.csv"
PEER_YEAR = 2025


def _r3(series: pd.Series) -> pd.Series:
    return series.round(3)


def _div(numer: pd.Series, denom: pd.Series) -> pd.Series:
    return numer / denom.replace(0, pd.NA)


def load_financials(path: Path | None = None) -> pd.DataFrame:
    csv_path = path or WIDE_CSV
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Missing {csv_path}. Run extract_sec_company_facts.py first."
        )
    df = pd.read_csv(csv_path)
    df["Fiscal_Year"] = pd.to_numeric(df["Fiscal_Year"], errors="coerce").astype("Int64")
    df = df.sort_values(["Company", "Fiscal_Year"]).reset_index(drop=True)
    if "Total_Liabilities" in df.columns:
        missing = df["Total_Liabilities"].isna()
        if missing.any():
            df.loc[missing, "Total_Liabilities"] = (
                df.loc[missing, "Total_Assets"] - df.loc[missing, "Total_Stockholders_Equity"]
            )
    return df


def growth_trend(df: pd.DataFrame) -> pd.DataFrame:
    g = df[["Company", "Fiscal_Year", "Revenue", "Net_Income"]].copy()
    prior_rev = g.groupby("Company", sort=False)["Revenue"].shift(1)
    g["Growth_Rate"] = _div(g["Revenue"] - prior_rev, prior_rev)
    g["Prior_Growth_Rate"] = g.groupby("Company", sort=False)["Growth_Rate"].shift(1)
    g["Growth_Differential"] = g["Growth_Rate"] - g["Prior_Growth_Rate"]
    g["Net_Income_Margin_pct"] = _r3(_div(g["Net_Income"], g["Revenue"]))
    g["Growth_Rate"] = _r3(g["Growth_Rate"])
    g["Prior_Growth_Rate"] = _r3(g["Prior_Growth_Rate"])
    g["Growth_Differential"] = _r3(g["Growth_Differential"])
    return g


def performance(df: pd.DataFrame, gt: pd.DataFrame) -> pd.DataFrame:
    b = df[
        [
            "Company",
            "Fiscal_Year",
            "Revenue",
            "Gross_Profit",
            "Net_Income",
            "Operating_Income",
            "Operating_Expenses",
            "Cash_Flow_from_Operating_Activities",
            "Capital_Expenditures",
        ]
    ].copy()
    grp = b.groupby("Company", sort=False)
    b["Prior_Operating_Income"] = grp["Operating_Income"].shift(1)
    b["Prior_Net_Income"] = grp["Net_Income"].shift(1)
    b["Prior_Opex"] = grp["Operating_Expenses"].shift(1)
    b["Prior_OCF"] = grp["Cash_Flow_from_Operating_Activities"].shift(1)

    opex_growth = _div(b["Operating_Expenses"] - b["Prior_Opex"], b["Prior_Opex"])
    p = b.merge(
        gt[["Company", "Fiscal_Year", "Growth_Rate", "Net_Income_Margin_pct"]],
        on=["Company", "Fiscal_Year"],
        how="left",
    )
    p["Gross_Margin_pct"] = _r3(_div(p["Gross_Profit"], p["Revenue"]))
    p["Operating_Margin_pct"] = _r3(_div(p["Operating_Income"], p["Revenue"]))
    p["Operating_Income_Growth"] = _r3(
        _div(p["Operating_Income"] - p["Prior_Operating_Income"], p["Prior_Operating_Income"])
    )
    p["Net_Income_Growth"] = _r3(_div(p["Net_Income"] - p["Prior_Net_Income"], p["Prior_Net_Income"]))
    p["Operating_Expense_Growth"] = _r3(opex_growth)
    p["Operating_Expense_to_Revenue"] = _r3(_div(p["Operating_Expenses"], p["Revenue"]))
    p["Revenue_Growth_Minus_Opex_Growth"] = _r3(p["Growth_Rate"] - opex_growth)
    p["Operating_Cash_Flow_Margin_pct"] = _r3(
        _div(p["Cash_Flow_from_Operating_Activities"], p["Revenue"])
    )
    p["Operating_Cash_Flow_Growth"] = _r3(
        _div(
            p["Cash_Flow_from_Operating_Activities"] - p["Prior_OCF"],
            p["Prior_OCF"],
        )
    )
    p["Cash_Conversion_Ratio"] = _r3(
        _div(p["Cash_Flow_from_Operating_Activities"], p["Net_Income"])
    )
    p["Free_Cash_Flow"] = _r3(
        p["Cash_Flow_from_Operating_Activities"] - p["Capital_Expenditures"]
    )
    p["Free_Cash_Flow_Margin_pct"] = _r3(_div(p["Free_Cash_Flow"], p["Revenue"]))
    return p.drop(columns=["Prior_Operating_Income", "Prior_Net_Income", "Prior_Opex", "Prior_OCF"])


def financial_health(df: pd.DataFrame) -> pd.DataFrame:
    h = df.copy()
    ticker_grp = h.groupby("Ticker", sort=False)
    prior_assets = ticker_grp["Total_Assets"].shift(1)
    prior_equity = ticker_grp["Total_Stockholders_Equity"].shift(1)
    h["Current_ratio"] = _r3(_div(h["Total_Current_Assets"], h["Total_Current_Liabilities"]))
    h["Total_Debt"] = h["Short_Term_Debt"].fillna(0) + h["Long_Term_Debt"].fillna(0)
    h["debt_to_equity_ratio"] = _r3(_div(h["Total_Debt"], h["Total_Stockholders_Equity"]))
    h["Liabilities_to_Assets"] = _r3(_div(h["Total_Liabilities"], h["Total_Assets"]))
    h["ROE"] = _r3(_div(h["Net_Income"], h["Total_Stockholders_Equity"]))
    h["ROA"] = _r3(_div(h["Net_Income"], h["Total_Assets"]))
    h["ROA_Avg"] = _r3(_div(h["Net_Income"], (h["Total_Assets"] + prior_assets) / 2))
    h["ROE_Avg"] = _r3(_div(h["Net_Income"], (h["Total_Stockholders_Equity"] + prior_equity) / 2))
    return h[
        [
            "Company",
            "Fiscal_Year",
            "Total_Assets",
            "Total_Liabilities",
            "Total_Stockholders_Equity",
            "Total_Current_Assets",
            "Total_Current_Liabilities",
            "Current_ratio",
            "Total_Debt",
            "debt_to_equity_ratio",
            "Liabilities_to_Assets",
            "ROE",
            "ROA",
            "ROA_Avg",
            "ROE_Avg",
            "Cash_Flow_from_Operating_Activities",
        ]
    ]


def peer_benchmarking(
    perf: pd.DataFrame, gt: pd.DataFrame, health: pd.DataFrame, fiscal_year: int = PEER_YEAR
) -> pd.DataFrame:
    p = perf.merge(health, on=["Company", "Fiscal_Year"], how="left", suffixes=("", "_h"))
    p = p.merge(
        gt[["Company", "Fiscal_Year", "Growth_Rate", "Growth_Differential"]],
        on=["Company", "Fiscal_Year"],
        how="left",
        suffixes=("", "_gt"),
    )
    p = p.loc[p["Fiscal_Year"] == fiscal_year].copy()

    def rank_desc(col: str) -> pd.Series:
        return p[col].rank(ascending=False, method="min")

    def rank_asc(col: str) -> pd.Series:
        return p[col].rank(ascending=True, method="min")

    p["Growth_Rate_Rank"] = rank_desc("Growth_Rate")
    p["Growth_Differential_Rank"] = rank_desc("Growth_Differential")
    p["Operating_Margin_Rank"] = rank_desc("Operating_Margin_pct")
    p["Net_Income_Margin_Rank"] = rank_desc("Net_Income_Margin_pct")
    p["Operating_Cash_Flow_Margin_Rank"] = rank_desc("Operating_Cash_Flow_Margin_pct")
    p["Operating_Expense_Growth_Rank"] = rank_asc("Operating_Expense_Growth")
    p["Current_Ratio_Rank"] = rank_desc("Current_ratio")
    p["Debt_to_Equity_Rank"] = rank_asc("debt_to_equity_ratio")
    p["Liabilities_to_Assets_Rank"] = rank_asc("Liabilities_to_Assets")
    p["ROA_Rank"] = rank_desc("ROA")
    p["ROE_Rank"] = rank_desc("ROE")
    p["Average_Rank"] = _r3(
        (
            p["Growth_Rate_Rank"]
            + p["Growth_Differential_Rank"]
            + p["Operating_Margin_Rank"]
            + p["Net_Income_Margin_Rank"]
            + p["Operating_Cash_Flow_Margin_Rank"]
            + p["Current_Ratio_Rank"]
            + p["Debt_to_Equity_Rank"]
            + p["ROA_Rank"]
            + p["ROE_Rank"]
        )
        / 9.0
    )
    cols = [
        "Company",
        "Fiscal_Year",
        "Growth_Rate_Rank",
        "Growth_Differential_Rank",
        "Operating_Margin_Rank",
        "Net_Income_Margin_Rank",
        "Operating_Cash_Flow_Margin_Rank",
        "Operating_Expense_Growth_Rank",
        "Current_Ratio_Rank",
        "Debt_to_Equity_Rank",
        "Liabilities_to_Assets_Rank",
        "ROA_Rank",
        "ROE_Rank",
        "Average_Rank",
    ]
    return p[cols].sort_values("Average_Rank").reset_index(drop=True)


def executive_summary(
    perf: pd.DataFrame, gt: pd.DataFrame, health: pd.DataFrame, peers: pd.DataFrame
) -> pd.DataFrame:
    latest = perf.groupby("Company")["Fiscal_Year"].transform("max")
    p = perf.loc[perf["Fiscal_Year"] == latest].copy()
    out = (
        p.merge(
            gt[
                [
                    "Company",
                    "Fiscal_Year",
                    "Revenue",
                    "Growth_Rate",
                    "Prior_Growth_Rate",
                    "Growth_Differential",
                ]
            ],
            on=["Company", "Fiscal_Year"],
            how="left",
            suffixes=("", "_gt"),
        )
        .merge(health, on=["Company", "Fiscal_Year"], how="left", suffixes=("", "_h"))
        .merge(peers, on=["Company", "Fiscal_Year"], how="left")
    )
    keep = [
        "Company",
        "Fiscal_Year",
        "Revenue",
        "Growth_Rate",
        "Prior_Growth_Rate",
        "Growth_Differential",
        "Gross_Margin_pct",
        "Operating_Margin_pct",
        "Net_Income_Margin_pct",
        "Operating_Income_Growth",
        "Net_Income_Growth",
        "Operating_Expense_Growth",
        "Operating_Expense_to_Revenue",
        "Revenue_Growth_Minus_Opex_Growth",
        "Operating_Cash_Flow_Margin_pct",
        "Operating_Cash_Flow_Growth",
        "Cash_Conversion_Ratio",
        "Free_Cash_Flow",
        "Free_Cash_Flow_Margin_pct",
        "Current_ratio",
        "debt_to_equity_ratio",
        "Liabilities_to_Assets",
        "ROA",
        "ROE",
        "ROA_Avg",
        "ROE_Avg",
        "Growth_Rate_Rank",
        "Operating_Margin_Rank",
        "Net_Income_Margin_Rank",
        "Operating_Expense_Growth_Rank",
        "Operating_Cash_Flow_Margin_Rank",
        "ROA_Rank",
        "ROE_Rank",
    ]
    present = [c for c in keep if c in out.columns]
    return out[present].sort_values("Company").reset_index(drop=True)


def company_performance(gt: pd.DataFrame) -> pd.DataFrame:
    """Notebook growth_trend as the company_performance view."""
    return gt.copy()


def company_operations(perf: pd.DataFrame) -> pd.DataFrame:
    """Efficiency columns from the performance view."""
    cols = [
        "Company",
        "Fiscal_Year",
        "Revenue",
        "Growth_Rate",
        "Operating_Expense_Growth",
        "Operating_Expense_to_Revenue",
        "Revenue_Growth_Minus_Opex_Growth",
        "Operating_Expenses",
    ]
    return perf[[c for c in cols if c in perf.columns]].copy()


def company_cash_flow(perf: pd.DataFrame) -> pd.DataFrame:
    """Cash columns from the performance view."""
    cols = [
        "Company",
        "Fiscal_Year",
        "Revenue",
        "Net_Income",
        "Cash_Flow_from_Operating_Activities",
        "Operating_Cash_Flow_Margin_pct",
        "Operating_Cash_Flow_Growth",
        "Cash_Conversion_Ratio",
        "Capital_Expenditures",
        "Free_Cash_Flow",
        "Free_Cash_Flow_Margin_pct",
    ]
    return perf[[c for c in cols if c in perf.columns]].copy()


def company_financial_health(health: pd.DataFrame) -> pd.DataFrame:
    return health.copy()


def peer_metric_frame(gt: pd.DataFrame, perf: pd.DataFrame, health: pd.DataFrame) -> pd.DataFrame:
    """Join existing view metrics for ranking. No new financial formulas."""
    frame = gt[
        ["Company", "Fiscal_Year", "Revenue", "Growth_Rate", "Growth_Differential", "Net_Income_Margin_pct"]
    ].merge(
        perf[
            [
                "Company",
                "Fiscal_Year",
                "Operating_Margin_pct",
                "Operating_Expense_to_Revenue",
                "Operating_Cash_Flow_Margin_pct",
                "Gross_Margin_pct",
            ]
        ],
        on=["Company", "Fiscal_Year"],
        how="left",
    ).merge(
        health[
            [
                "Company",
                "Fiscal_Year",
                "Current_ratio",
                "debt_to_equity_ratio",
                "Liabilities_to_Assets",
                "ROA",
            ]
        ],
        on=["Company", "Fiscal_Year"],
        how="left",
    )
    return frame


def rank_selected_metric(frame: pd.DataFrame, fiscal_year: int, metric: str, higher_is_better: bool) -> pd.DataFrame:
    subset = frame.loc[frame["Fiscal_Year"] == fiscal_year, ["Company", "Fiscal_Year", metric]].copy()
    subset = subset.dropna(subset=[metric])
    subset["Rank"] = subset[metric].rank(ascending=not higher_is_better, method="min")
    return subset.sort_values("Rank").reset_index(drop=True)


def build_views(path: Path | None = None) -> dict[str, pd.DataFrame]:
    df = load_financials(path)
    gt = growth_trend(df)
    perf = performance(df, gt)
    health = financial_health(df)
    peers = peer_benchmarking(perf, gt, health)
    summary = executive_summary(perf, gt, health, peers)
    return {
        "company_financials": df,
        "growth_trend": gt,
        "performance": perf,
        "financial_health": health,
        "peer_benchmarking": peers,
        "executive_summary": summary,
        "company_performance": company_performance(gt),
        "company_operations": company_operations(perf),
        "company_cash_flow": company_cash_flow(perf),
        "company_financial_health": company_financial_health(health),
        "peer_metrics": peer_metric_frame(gt, perf, health),
    }
