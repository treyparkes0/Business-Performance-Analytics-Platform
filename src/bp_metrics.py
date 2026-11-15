"""
Analytics views for the local CSV path.

Source table: data/processed/company_financials_wide.csv
(same grain as financial_analytics.clean.company_financials).

The Databricks view definitions in sql/ use the same formulas. Python
filters, ranks, and shapes the loader contract. It does not retune
Fiscal_Year: that column is already the filing period end year.

Ranking
    Ties use SQL RANK(), which matches pandas rank(method="min"):
    tied values share the best (lowest) rank and the next rank is skipped.
    Missing values rank last (SQL NULLS LAST, pandas na_option="bottom").
    They receive the worst ranks, and missing values tie with each other.

Peer year
    peer_benchmarking is FY2025 only, the last year present for every
    company. Average_Rank is the equal-weight mean of nine ranks:
    revenue growth, operating margin, net income margin, operating
    expense / revenue (lower is better), OCF margin, current ratio,
    debt-to-equity (lower is better), ROA, and ROE.

Returns
    Primary ROA and ROE use average balances, (current + prior) / 2.
    Ending balances are used only when that company has no prior year,
    and those rows are flagged. Ending-balance columns stay on the view.

Cash conversion
    The raw ratio is operating cash flow / net income.
    Cash_Conversion_Meaningful is false when net income is zero or
    negative, or when the absolute ratio is greater than
    CASH_CONVERSION_ABS_THRESHOLD (5). A ratio of exactly 5 stays
    meaningful. CrowdStrike FY2025 is the case the app labels n/m.

Debt
    Total debt still coalesces a missing leg to 0. Reported flags record
    whether the source field was present. CrowdStrike short-term debt is
    unreported for FY2021–FY2026 and is treated as 0.

Liabilities
    Only AMD null Total_Liabilities are replaced with assets minus equity,
    because AMD companyfacts has no Total_Liabilities tag.
    Total_Liabilities_Imputed marks those rows.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
WIDE_CSV = ROOT / "data" / "processed" / "company_financials_wide.csv"
PEER_YEAR = 2025
CASH_CONVERSION_ABS_THRESHOLD = 5

RANK_TIE_RULE = (
    "Ties use SQL RANK(), which matches pandas rank(method='min'): "
    "tied values share the best (lowest) rank and the next rank is skipped."
)
RANK_MISSING_RULE = (
    "Missing values rank last (SQL NULLS LAST, pandas na_option='bottom'). "
    "They receive the worst ranks, and missing values tie with each other."
)

# (value column, higher is better, rank column)
RANKED_METRICS: tuple[tuple[str, bool, str], ...] = (
    ("Growth_Rate", True, "Growth_Rate_Rank"),
    ("Operating_Margin_pct", True, "Operating_Margin_Rank"),
    ("Net_Income_Margin_pct", True, "Net_Income_Margin_Rank"),
    ("Operating_Expense_to_Revenue", False, "Operating_Expense_to_Revenue_Rank"),
    ("Operating_Cash_Flow_Margin_pct", True, "Operating_Cash_Flow_Margin_Rank"),
    ("Current_ratio", True, "Current_Ratio_Rank"),
    ("debt_to_equity_ratio", False, "Debt_to_Equity_Rank"),
    ("ROA", True, "ROA_Rank"),
    ("ROE", True, "ROE_Rank"),
)

GROWTH_COLUMNS = [
    "Company",
    "Fiscal_Year",
    "Revenue",
    "Net_Income",
    "Growth_Rate",
    "Prior_Growth_Rate",
    "Growth_Differential",
    "Net_Income_Margin_pct",
]

PERFORMANCE_COLUMNS = [
    "Company",
    "Fiscal_Year",
    "Revenue",
    "Gross_Profit",
    "Net_Income",
    "Operating_Income",
    "Operating_Expenses",
    "Cash_Flow_from_Operating_Activities",
    "Capital_Expenditures",
    "Growth_Rate",
    "Net_Income_Margin_pct",
    "Gross_Margin_pct",
    "Operating_Margin_pct",
    "Operating_Income_Growth",
    "Net_Income_Growth",
    "Operating_Expense_Growth",
    "Operating_Expense_to_Revenue",
    "Revenue_Growth_Minus_Opex_Growth",
    "Operating_Cash_Flow_Margin_pct",
    "Operating_Cash_Flow_Growth",
    "Cash_Conversion_Ratio",
    "Cash_Conversion_Meaningful",
    "Free_Cash_Flow",
    "Free_Cash_Flow_Margin_pct",
]

HEALTH_COLUMNS = [
    "Company",
    "Fiscal_Year",
    "Total_Assets",
    "Total_Liabilities",
    "Total_Liabilities_Imputed",
    "Total_Stockholders_Equity",
    "Total_Current_Assets",
    "Total_Current_Liabilities",
    "Current_ratio",
    "Total_Debt",
    "Short_Term_Debt_Reported",
    "Long_Term_Debt_Reported",
    "debt_to_equity_ratio",
    "Liabilities_to_Assets",
    "ROA_Ending",
    "ROE_Ending",
    "ROA_Avg",
    "ROE_Avg",
    "ROA_Uses_Ending_Balance",
    "ROE_Uses_Ending_Balance",
    "ROA",
    "ROE",
    "Cash_Flow_from_Operating_Activities",
]

OPERATIONS_COLUMNS = [
    "Company",
    "Fiscal_Year",
    "Revenue",
    "Growth_Rate",
    "Operating_Expense_Growth",
    "Operating_Expense_to_Revenue",
    "Revenue_Growth_Minus_Opex_Growth",
    "Operating_Expenses",
]

CASH_FLOW_COLUMNS = [
    "Company",
    "Fiscal_Year",
    "Revenue",
    "Net_Income",
    "Cash_Flow_from_Operating_Activities",
    "Operating_Cash_Flow_Margin_pct",
    "Operating_Cash_Flow_Growth",
    "Cash_Conversion_Ratio",
    "Cash_Conversion_Meaningful",
    "Capital_Expenditures",
    "Free_Cash_Flow",
    "Free_Cash_Flow_Margin_pct",
]

PEER_METRIC_COLUMNS = [
    "Company",
    "Fiscal_Year",
    "Revenue",
    "Growth_Rate",
    "Growth_Differential",
    "Net_Income_Margin_pct",
    "Operating_Margin_pct",
    "Operating_Expense_to_Revenue",
    "Operating_Cash_Flow_Margin_pct",
    "Gross_Margin_pct",
    "Current_ratio",
    "debt_to_equity_ratio",
    "Liabilities_to_Assets",
    "ROA",
    "ROE",
]


def _peer_columns() -> list[str]:
    cols = ["Company", "Fiscal_Year"]
    for value_col, _higher, rank_col in RANKED_METRICS:
        cols.extend([value_col, rank_col])
    cols.append("Average_Rank")
    return cols


PEER_COLUMNS = _peer_columns()

EXECUTIVE_COLUMNS = [
    "Company",
    "Fiscal_Year",
    "Benchmark_Fiscal_Year",
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
    "Cash_Conversion_Meaningful",
    "Free_Cash_Flow",
    "Free_Cash_Flow_Margin_pct",
    "Current_ratio",
    "debt_to_equity_ratio",
    "Liabilities_to_Assets",
    "ROA",
    "ROE",
    "ROA_Ending",
    "ROE_Ending",
    "ROA_Avg",
    "ROE_Avg",
    "ROA_Uses_Ending_Balance",
    "ROE_Uses_Ending_Balance",
    "Total_Liabilities_Imputed",
    "Short_Term_Debt_Reported",
    "Long_Term_Debt_Reported",
    "FY2025_Growth_Rate_Rank",
    "FY2025_Operating_Margin_Rank",
    "FY2025_Net_Income_Margin_Rank",
    "FY2025_Operating_Expense_to_Revenue_Rank",
    "FY2025_Operating_Cash_Flow_Margin_Rank",
    "FY2025_Current_Ratio_Rank",
    "FY2025_Debt_to_Equity_Rank",
    "FY2025_ROA_Rank",
    "FY2025_ROE_Rank",
    "FY2025_Average_Rank",
]

CONTRACT_KEYS = (
    "growth_trend",
    "performance",
    "financial_health",
    "peer_benchmarking",
    "executive_summary",
    "company_performance",
    "company_operations",
    "company_cash_flow",
    "company_financial_health",
    "peer_metrics",
)

SOURCE_VIEW_COLUMNS = {
    "growth_trend": GROWTH_COLUMNS,
    "performance": PERFORMANCE_COLUMNS,
    "financial_health": HEALTH_COLUMNS,
    "peer_benchmarking": PEER_COLUMNS,
    "executive_summary": EXECUTIVE_COLUMNS,
}

BOOL_COLUMNS = {
    "Total_Liabilities_Imputed",
    "Short_Term_Debt_Reported",
    "Long_Term_Debt_Reported",
    "Cash_Conversion_Meaningful",
    "ROA_Uses_Ending_Balance",
    "ROE_Uses_Ending_Balance",
}
INT_COLUMNS = {"Fiscal_Year", "Benchmark_Fiscal_Year"}


def _is_rank_column(name: str) -> bool:
    return name.endswith("_Rank") and not name.endswith("Average_Rank")


def _r3(series: pd.Series) -> pd.Series:
    return series.round(3)


def _div(numer: pd.Series, denom: pd.Series) -> pd.Series:
    return numer / denom.replace(0, pd.NA)


def rank_values(series: pd.Series, *, higher_is_better: bool) -> pd.Series:
    """Rank a metric. See RANK_TIE_RULE and RANK_MISSING_RULE."""
    ranked = series.rank(
        ascending=not higher_is_better,
        method="min",
        na_option="bottom",
    )
    return ranked.round().astype("Int64")


def cash_conversion_meaningful(net_income: pd.Series, operating_cash_flow: pd.Series) -> pd.Series:
    """False when net income is <= 0 or the absolute raw ratio exceeds the threshold.

    A null input leaves the flag null. Net income of exactly 0 is not meaningful
    and the ratio itself is null. A ratio of exactly the threshold stays meaningful.
    """
    raw = operating_cash_flow / net_income.replace(0, pd.NA)
    known = net_income.notna() & operating_cash_flow.notna()
    extreme = raw.abs().gt(CASH_CONVERSION_ABS_THRESHOLD).fillna(False)
    flag = pd.Series(pd.NA, index=net_income.index, dtype="boolean")
    flag = flag.mask(known, True)
    flag = flag.mask(known & (net_income <= 0), False)
    flag = flag.mask(known & extreme, False)
    return flag.astype("boolean")


def impute_amd_liabilities(df: pd.DataFrame) -> pd.DataFrame:
    """Fill AMD null total liabilities with assets minus equity. Leave every other company alone."""
    out = df.copy()
    if "Total_Liabilities" not in out.columns:
        out["Total_Liabilities_Imputed"] = False
        return out
    imputed = (out["Company"] == "AMD") & out["Total_Liabilities"].isna()
    out.loc[imputed, "Total_Liabilities"] = (
        out.loc[imputed, "Total_Assets"] - out.loc[imputed, "Total_Stockholders_Equity"]
    )
    if "Total_Liabilities_Imputed" in df.columns:
        already = df["Total_Liabilities_Imputed"].fillna(False).astype(bool)
        out["Total_Liabilities_Imputed"] = already | imputed
    else:
        out["Total_Liabilities_Imputed"] = imputed
    return out


def load_financials(path: Path | None = None) -> pd.DataFrame:
    csv_path = path or WIDE_CSV
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Missing {csv_path}. Run extract_sec_company_facts.py first."
        )
    df = pd.read_csv(csv_path)
    df["Fiscal_Year"] = pd.to_numeric(df["Fiscal_Year"], errors="coerce").astype("Int64")
    df = df.sort_values(["Company", "Fiscal_Year"], kind="mergesort").reset_index(drop=True)
    return impute_amd_liabilities(df)


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
    return g[GROWTH_COLUMNS]


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
    raw_conversion = _div(p["Cash_Flow_from_Operating_Activities"], p["Net_Income"])
    p["Cash_Conversion_Ratio"] = _r3(raw_conversion)
    p["Cash_Conversion_Meaningful"] = cash_conversion_meaningful(
        p["Net_Income"], p["Cash_Flow_from_Operating_Activities"]
    )
    p["Free_Cash_Flow"] = _r3(
        p["Cash_Flow_from_Operating_Activities"] - p["Capital_Expenditures"]
    )
    p["Free_Cash_Flow_Margin_pct"] = _r3(_div(p["Free_Cash_Flow"], p["Revenue"]))
    return p[PERFORMANCE_COLUMNS]


def _average_or_ending(net_income: pd.Series, ending: pd.Series, prior: pd.Series):
    ending_ratio = _div(net_income, ending)
    average_ratio = _div(net_income, (ending + prior) / 2)
    uses_ending = prior.isna()
    primary = average_ratio.where(~uses_ending, ending_ratio)
    return (
        _r3(ending_ratio),
        _r3(average_ratio),
        _r3(primary),
        uses_ending.astype("boolean"),
    )


def financial_health(df: pd.DataFrame) -> pd.DataFrame:
    h = impute_amd_liabilities(df)
    ticker_grp = h.groupby("Ticker", sort=False)
    prior_assets = ticker_grp["Total_Assets"].shift(1)
    prior_equity = ticker_grp["Total_Stockholders_Equity"].shift(1)
    h["Current_ratio"] = _r3(_div(h["Total_Current_Assets"], h["Total_Current_Liabilities"]))
    h["Short_Term_Debt_Reported"] = h["Short_Term_Debt"].notna()
    h["Long_Term_Debt_Reported"] = h["Long_Term_Debt"].notna()
    h["Total_Debt"] = h["Short_Term_Debt"].fillna(0) + h["Long_Term_Debt"].fillna(0)
    h["debt_to_equity_ratio"] = _r3(_div(h["Total_Debt"], h["Total_Stockholders_Equity"]))
    h["Liabilities_to_Assets"] = _r3(_div(h["Total_Liabilities"], h["Total_Assets"]))
    h["ROA_Ending"], h["ROA_Avg"], h["ROA"], h["ROA_Uses_Ending_Balance"] = _average_or_ending(
        h["Net_Income"], h["Total_Assets"], prior_assets
    )
    h["ROE_Ending"], h["ROE_Avg"], h["ROE"], h["ROE_Uses_Ending_Balance"] = _average_or_ending(
        h["Net_Income"], h["Total_Stockholders_Equity"], prior_equity
    )
    return h[HEALTH_COLUMNS]


def peer_benchmarking(
    perf: pd.DataFrame,
    gt: pd.DataFrame,
    health: pd.DataFrame,
    fiscal_year: int = PEER_YEAR,
) -> pd.DataFrame:
    """FY peer ranks. Values are kept beside each rank. Average uses RANKED_METRICS only."""
    frame = perf[
        [
            "Company",
            "Fiscal_Year",
            "Operating_Margin_pct",
            "Net_Income_Margin_pct",
            "Operating_Expense_to_Revenue",
            "Operating_Cash_Flow_Margin_pct",
        ]
    ].merge(
        gt[["Company", "Fiscal_Year", "Growth_Rate"]],
        on=["Company", "Fiscal_Year"],
        how="left",
    ).merge(
        health[
            [
                "Company",
                "Fiscal_Year",
                "Current_ratio",
                "debt_to_equity_ratio",
                "ROA",
                "ROE",
            ]
        ],
        on=["Company", "Fiscal_Year"],
        how="left",
    )
    frame = frame.loc[frame["Fiscal_Year"] == fiscal_year].copy().reset_index(drop=True)
    for value_col, higher, rank_col in RANKED_METRICS:
        frame[rank_col] = rank_values(frame[value_col], higher_is_better=higher)
    rank_cols = [rank_col for _value, _higher, rank_col in RANKED_METRICS]
    frame["Average_Rank"] = _r3(frame[rank_cols].sum(axis=1) / float(len(rank_cols)))
    ordered = frame[PEER_COLUMNS].sort_values(["Average_Rank", "Company"], kind="mergesort")
    return ordered.reset_index(drop=True)


def executive_summary(
    perf: pd.DataFrame, gt: pd.DataFrame, health: pd.DataFrame, peers: pd.DataFrame
) -> pd.DataFrame:
    """One latest-year row per company, with FY2025 ranks attached even when the latest year is 2026."""
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
    )
    rank_cols = [rank_col for _value, _higher, rank_col in RANKED_METRICS] + ["Average_Rank"]
    fy_ranks = peers[["Company"] + rank_cols].rename(
        columns={col: f"FY2025_{col}" for col in rank_cols}
    )
    out = out.merge(fy_ranks, on="Company", how="left")
    out["Benchmark_Fiscal_Year"] = PEER_YEAR
    present = [col for col in EXECUTIVE_COLUMNS if col in out.columns]
    return out[present].sort_values("Company", kind="mergesort").reset_index(drop=True)


def peer_metric_frame(gt: pd.DataFrame, perf: pd.DataFrame, health: pd.DataFrame) -> pd.DataFrame:
    """Underlying peer values for every fiscal year, including primary ROA and ROE."""
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
                "ROE",
            ]
        ],
        on=["Company", "Fiscal_Year"],
        how="left",
    )
    return frame[PEER_METRIC_COLUMNS]


def canonicalize_columns(frame: pd.DataFrame, expected: list[str]) -> pd.DataFrame:
    """Match warehouse casing to the local contract and drop unexpected columns."""
    lookup = {str(col).casefold(): col for col in expected}
    rename: dict[str, str] = {}
    used: set[str] = set()
    for col in frame.columns:
        key = str(col).casefold()
        target = lookup.get(key)
        if target and target not in used:
            rename[col] = target
            used.add(target)
    out = frame.rename(columns=rename)
    missing = [col for col in expected if col not in out.columns]
    if missing:
        raise KeyError(f"View is missing contract columns: {missing}")
    return out.loc[:, list(expected)].copy()


def _as_bool(series: pd.Series) -> pd.Series:
    def one(value):
        if value is None or value is pd.NA:
            return pd.NA
        try:
            if pd.isna(value):
                return pd.NA
        except (TypeError, ValueError):
            pass
        return bool(value)

    return series.map(one).astype("boolean")


def align_dtypes(frame: pd.DataFrame) -> pd.DataFrame:
    """Cast to the dtypes the CSV path and the warehouse path both return."""
    out = frame.copy()
    for col in out.columns:
        if col == "Company":
            out[col] = out[col].astype("string")
        elif col in INT_COLUMNS or _is_rank_column(col):
            out[col] = pd.to_numeric(out[col], errors="coerce").round().astype("Int64")
        elif col in BOOL_COLUMNS:
            out[col] = _as_bool(out[col])
        else:
            out[col] = pd.to_numeric(out[col], errors="coerce").astype("float64")
    return out


def _sort_frame(frame: pd.DataFrame, kind: str) -> pd.DataFrame:
    if kind == "peers":
        return frame.sort_values(["Average_Rank", "Company"], kind="mergesort").reset_index(drop=True)
    if kind == "summary":
        return frame.sort_values(["Company"], kind="mergesort").reset_index(drop=True)
    return frame.sort_values(["Company", "Fiscal_Year"], kind="mergesort").reset_index(drop=True)


def assemble_views(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Shape source views into the shared loader contract.

    company_operations and company_cash_flow are column subsets of performance.
    peer_metrics is every fiscal year's underlying values, not the rank table.
    """
    gt = align_dtypes(canonicalize_columns(raw["growth_trend"], GROWTH_COLUMNS))
    perf = align_dtypes(canonicalize_columns(raw["performance"], PERFORMANCE_COLUMNS))
    health = align_dtypes(canonicalize_columns(raw["financial_health"], HEALTH_COLUMNS))
    peers = align_dtypes(canonicalize_columns(raw["peer_benchmarking"], PEER_COLUMNS))
    summary = align_dtypes(canonicalize_columns(raw["executive_summary"], EXECUTIVE_COLUMNS))
    gt = _sort_frame(gt, "year")
    perf = _sort_frame(perf, "year")
    health = _sort_frame(health, "year")
    peers = _sort_frame(peers, "peers")
    summary = _sort_frame(summary, "summary")
    metrics = align_dtypes(peer_metric_frame(gt, perf, health))
    metrics = _sort_frame(metrics, "year")
    return {
        "growth_trend": gt,
        "performance": perf,
        "financial_health": health,
        "peer_benchmarking": peers,
        "executive_summary": summary,
        "company_performance": gt.copy(),
        "company_operations": perf.loc[:, OPERATIONS_COLUMNS].reset_index(drop=True),
        "company_cash_flow": perf.loc[:, CASH_FLOW_COLUMNS].reset_index(drop=True),
        "company_financial_health": health.copy(),
        "peer_metrics": metrics,
    }


def build_views(path: Path | None = None) -> dict[str, pd.DataFrame]:
    df = load_financials(path)
    gt = growth_trend(df)
    perf = performance(df, gt)
    health = financial_health(df)
    peers = peer_benchmarking(perf, gt, health)
    summary = executive_summary(perf, gt, health, peers)
    return assemble_views(
        {
            "growth_trend": gt,
            "performance": perf,
            "financial_health": health,
            "peer_benchmarking": peers,
            "executive_summary": summary,
        }
    )
