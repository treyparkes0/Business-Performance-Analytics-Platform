"""Notebook view SQL keeps the ranking, cash-conversion, and AMD rules."""

import json

from src.bp_metrics import ROOT

NOTEBOOK = ROOT / "Business Performance Analytics.ipynb"
VIEW_NAMES = (
    "growth_trend",
    "performance",
    "financial_health",
    "peer_benchmarking",
    "executive_summary",
)


def notebook_views() -> dict[str, str]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    found = {}
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "CREATE OR REPLACE VIEW financial_analytics.analytics." not in source:
            continue
        body = source.split("%sql", 1)[-1].strip()
        for name in VIEW_NAMES:
            if f"CREATE OR REPLACE VIEW financial_analytics.analytics.{name} " in body or (
                f"financial_analytics.analytics.{name} AS" in body
            ):
                found[name] = body
    return found


def test_notebook_has_the_five_views():
    assert set(notebook_views()) == set(VIEW_NAMES)


def test_notebook_sql_documents_rank_and_threshold_rules():
    views = notebook_views()
    peer_sql = views["peer_benchmarking"]
    performance_sql = views["performance"]
    health_sql = views["financial_health"]
    summary_sql = views["executive_summary"]
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
    assert "both growth rates at full precision" in performance_sql
    assert "((b.Revenue - b.Prior_Revenue) / NULLIF(b.Prior_Revenue, 0))" in performance_sql
    assert "- ((b.Operating_Expenses - b.Prior_Opex) / NULLIF(b.Prior_Opex, 0))" in performance_sql
    assert "gt.Growth_Rate -" not in performance_sql


def test_repo_does_not_use_duckdb():
    assert "duckdb" not in (ROOT / "requirements.txt").read_text().lower()
    assert "duckdb" not in (ROOT / "app.py").read_text().lower()
    for path in (ROOT / "src").glob("*.py"):
        assert "duckdb" not in path.read_text(encoding="utf-8").lower()
