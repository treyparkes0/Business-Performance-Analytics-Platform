"""Execute the view SQL in DuckDB and compare it to the Python views."""

import json
from pathlib import Path

import duckdb
import pandas as pd

from src.bp_metrics import (
    BOOL_COLUMNS,
    INT_COLUMNS,
    ROOT,
    SOURCE_VIEW_COLUMNS,
    WIDE_CSV,
    _is_rank_column,
)

SQL_DIR = ROOT / "sql"
SQL_FILES = (
    "growth_trend.sql",
    "performance.sql",
    "financial_health.sql",
    "peer_benchmarking.sql",
    "executive_summary.sql",
)
NOTEBOOK = ROOT / "Business Performance Analytics.ipynb"


def _execute_views() -> duckdb.DuckDBPyConnection:
    connection = duckdb.connect()
    connection.execute(
        f"""
        CREATE TABLE company_financials AS
        SELECT * FROM read_csv_auto('{WIDE_CSV.as_posix()}', header=true)
        """
    )
    for name in SQL_FILES:
        statement = (SQL_DIR / name).read_text()
        statement = statement.replace("financial_analytics.clean.company_financials", "company_financials")
        statement = statement.replace("financial_analytics.analytics.", "")
        connection.execute(statement)
    return connection


def test_sql_matches_python_within_rounding(views):
    connection = _execute_views()
    for key, columns in SOURCE_VIEW_COLUMNS.items():
        sql_frame = connection.execute(f"SELECT * FROM {key}").fetchdf()
        assert set(sql_frame.columns) == set(columns)
        python_frame = views[key]
        merged = python_frame.assign(
            Company=python_frame["Company"].astype(str),
            Fiscal_Year=python_frame["Fiscal_Year"].astype(int),
        ).merge(
            sql_frame.assign(
                Company=sql_frame["Company"].astype(str),
                Fiscal_Year=sql_frame["Fiscal_Year"].astype(int),
            ),
            on=["Company", "Fiscal_Year"],
            suffixes=("_py", "_sql"),
            how="outer",
            indicator=True,
        )
        assert (merged["_merge"] == "both").all(), key
        for column in columns:
            if column in {"Company", "Fiscal_Year"}:
                continue
            mismatches = []
            for company, year, py_value, sql_value in zip(
                merged["Company"],
                merged["Fiscal_Year"],
                merged[f"{column}_py"],
                merged[f"{column}_sql"],
                strict=True,
            ):
                if column in BOOL_COLUMNS:
                    ok = (pd.isna(py_value) and pd.isna(sql_value)) or (
                        not pd.isna(py_value)
                        and not pd.isna(sql_value)
                        and bool(py_value) == bool(sql_value)
                    )
                elif _is_rank_column(column) or column in INT_COLUMNS or column == "Benchmark_Fiscal_Year":
                    ok = (pd.isna(py_value) and pd.isna(sql_value)) or int(py_value) == int(sql_value)
                else:
                    ok = (pd.isna(py_value) and pd.isna(sql_value)) or abs(float(py_value) - float(sql_value)) <= 0.0011
                if not ok:
                    mismatches.append((company, int(year), py_value, sql_value))
            assert not mismatches, (key, column, mismatches[:5])


def test_sql_documents_rank_and_threshold_rules():
    peer_sql = (SQL_DIR / "peer_benchmarking.sql").read_text()
    performance_sql = (SQL_DIR / "performance.sql").read_text()
    health_sql = (SQL_DIR / "financial_health.sql").read_text()
    summary_sql = (SQL_DIR / "executive_summary.sql").read_text()
    assert "NULLS LAST" in peer_sql
    assert "method='min'" in peer_sql
    assert "Operating_Expense_to_Revenue ASC NULLS LAST" in peer_sql
    assert "Growth_Differential_Rank" not in peer_sql
    assert "abs(b.Cash_Flow_from_Operating_Activities / b.Net_Income) > 5" in performance_sql
    assert "Company = 'AMD' AND Total_Liabilities IS NULL" in health_sql
    assert "Short_Term_Debt IS NOT NULL" in health_sql
    assert "ON p.Company = pb.Company" in summary_sql
    assert "p.Fiscal_Year = pb.Fiscal_Year" not in summary_sql
    assert "FY2025_Average_Rank" in summary_sql


def test_notebook_sql_matches_files():
    notebook = json.loads(NOTEBOOK.read_text())
    found = set()
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "CREATE OR REPLACE VIEW financial_analytics.analytics." not in source:
            continue
        body = source.split("%sql", 1)[-1].strip()
        for name in SQL_FILES:
            marker = name.removesuffix(".sql")
            if f"CREATE OR REPLACE VIEW financial_analytics.analytics.{marker} " in body or (
                f"financial_analytics.analytics.{marker} AS" in body
            ):
                expected = (SQL_DIR / name).read_text().strip()
                assert body == expected, name
                found.add(name)
    assert found == set(SQL_FILES)
