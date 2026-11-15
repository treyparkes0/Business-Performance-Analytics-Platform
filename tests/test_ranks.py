"""Rank direction, ties, and missing values for the FY2025 peer set."""

import duckdb
import pandas as pd

from src.bp_metrics import RANKED_METRICS, peer_benchmarking, rank_values


def _frames():
    companies = ["A", "B", "C"]
    year = [2025, 2025, 2025]
    perf = pd.DataFrame(
        {
            "Company": companies,
            "Fiscal_Year": year,
            "Operating_Margin_pct": [0.2, 0.2, 0.2],
            "Net_Income_Margin_pct": [0.1, 0.1, 0.1],
            "Operating_Expense_to_Revenue": [0.4, 0.4, 0.4],
            "Operating_Cash_Flow_Margin_pct": [0.3, 0.3, 0.3],
        }
    )
    growth = pd.DataFrame({"Company": companies, "Fiscal_Year": year, "Growth_Rate": [0.1, 0.1, 0.1]})
    health = pd.DataFrame(
        {
            "Company": companies,
            "Fiscal_Year": year,
            "Current_ratio": [1.5, 1.5, 1.5],
            "debt_to_equity_ratio": [0.2, 0.2, 0.2],
            "ROA": [0.1, 0.1, 0.1],
            "ROE": [0.2, 0.2, 0.2],
        }
    )
    return perf, growth, health


def test_rank_ties_share_min_and_missing_is_last():
    values = pd.Series([10.0, 10.0, 8.0, None], index=["A", "B", "C", "D"])
    higher = rank_values(values, higher_is_better=True)
    lower = rank_values(values, higher_is_better=False)
    assert higher.tolist() == [1, 1, 3, 4]
    assert lower.tolist() == [2, 2, 1, 4]


def test_sql_rank_matches_pandas_ties_and_missing():
    connection = duckdb.connect()
    connection.execute("CREATE TABLE metric (company VARCHAR, metric DOUBLE)")
    connection.execute(
        "INSERT INTO metric VALUES ('A', 10), ('B', 10), ('C', 8), ('D', NULL)"
    )
    sql = connection.execute(
        """
        SELECT company,
               RANK() OVER (ORDER BY metric DESC NULLS LAST) AS rank_desc,
               RANK() OVER (ORDER BY metric ASC NULLS LAST) AS rank_asc
        FROM metric
        ORDER BY company
        """
    ).fetchdf()
    values = pd.Series([10.0, 10.0, 8.0, None], index=list("ABCD"))
    higher = rank_values(values, higher_is_better=True)
    lower = rank_values(values, higher_is_better=False)
    assert sql["rank_desc"].tolist() == [int(value) for value in higher.tolist()]
    assert sql["rank_asc"].tolist() == [int(value) for value in lower.tolist()]


def test_synthetic_direction_ties_and_missing():
    perf, growth, health = _frames()
    growth.loc[growth["Company"] == "C", "Growth_Rate"] = pd.NA
    growth.loc[growth["Company"].isin(["A", "B"]), "Growth_Rate"] = 0.2
    health.loc[health["Company"] == "A", "debt_to_equity_ratio"] = 0.5
    health.loc[health["Company"] == "C", "debt_to_equity_ratio"] = pd.NA
    perf.loc[perf["Company"] == "A", "Operating_Expense_to_Revenue"] = 0.8
    ranked = peer_benchmarking(perf, growth, health)
    by_company = ranked.set_index("Company")
    assert by_company.loc["A", "Growth_Rate_Rank"] == 1
    assert by_company.loc["B", "Growth_Rate_Rank"] == 1
    assert by_company.loc["C", "Growth_Rate_Rank"] == 3
    assert by_company.loc["B", "Debt_to_Equity_Rank"] == 1
    assert by_company.loc["A", "Debt_to_Equity_Rank"] == 2
    assert by_company.loc["C", "Debt_to_Equity_Rank"] == 3
    assert by_company.loc["B", "Operating_Expense_to_Revenue_Rank"] == 1
    assert by_company.loc["C", "Operating_Expense_to_Revenue_Rank"] == 1
    assert by_company.loc["A", "Operating_Expense_to_Revenue_Rank"] == 3
    assert "Growth_Differential_Rank" not in ranked.columns
    assert "Operating_Expense_Growth_Rank" not in ranked.columns
    assert "Liabilities_to_Assets_Rank" not in ranked.columns


def test_fy2025_direction_and_average(views):
    ranked = views["peer_benchmarking"]
    assert list(ranked["Fiscal_Year"].unique()) == [2025]
    assert len(ranked) == 6
    best_growth = ranked.loc[ranked["Growth_Rate"].idxmax(), "Growth_Rate_Rank"]
    assert int(best_growth) == 1
    highest_leverage = ranked["debt_to_equity_ratio"].idxmax()
    assert int(ranked.loc[highest_leverage, "Debt_to_Equity_Rank"]) == int(ranked["Debt_to_Equity_Rank"].max())
    leanest_opex = ranked["Operating_Expense_to_Revenue"].idxmin()
    assert int(ranked.loc[leanest_opex, "Operating_Expense_to_Revenue_Rank"]) == 1
    rank_cols = [rank_col for _value, _higher, rank_col in RANKED_METRICS]
    assert rank_cols == [
        "Growth_Rate_Rank",
        "Operating_Margin_Rank",
        "Net_Income_Margin_Rank",
        "Operating_Expense_to_Revenue_Rank",
        "Operating_Cash_Flow_Margin_Rank",
        "Current_Ratio_Rank",
        "Debt_to_Equity_Rank",
        "ROA_Rank",
        "ROE_Rank",
    ]
    expected = (ranked[rank_cols].sum(axis=1) / 9).round(3)
    diff = (expected - ranked["Average_Rank"]).abs()
    assert (diff <= 1e-9).all()
    value_cols = [value for value, _higher, _rank in RANKED_METRICS]
    for value_col, rank_col in zip(value_cols, rank_cols, strict=True):
        position = list(ranked.columns).index(rank_col)
        assert ranked.columns[position - 1] == value_col
