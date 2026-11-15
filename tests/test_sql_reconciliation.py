"""Databricks view SQL matches the notebook. The view SQL is not executed here."""

import json

from src.bp_metrics import ROOT

SQL_DIR = ROOT / "sql"
SQL_FILES = (
    "growth_trend.sql",
    "performance.sql",
    "financial_health.sql",
    "peer_benchmarking.sql",
    "executive_summary.sql",
)
NOTEBOOK = ROOT / "Business Performance Analytics.ipynb"


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
    assert "sec_company_financials_clean" in health_sql
    assert "Metric = 'Total_Liabilities'" in health_sql
    assert "WHEN c.Company = 'AMD' AND r.Company IS NULL" in health_sql
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


def test_repo_does_not_use_duckdb():
    assert "duckdb" not in (ROOT / "requirements.txt").read_text().lower()
    assert not (SQL_DIR / "duckdb").exists()
