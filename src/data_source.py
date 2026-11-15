"""
Retrieve analytics views for the app.

Databricks SQL views are the source of truth when a warehouse connection
is configured. Local CSVs reproduce those views from
company_financials_wide.csv otherwise.

Both paths return the same keys, column names, Company / Fiscal_Year
casing, and dtypes. peer_metrics is the underlying values for every
fiscal year. peer_benchmarking is the FY2025 rank table. performance is
the full performance view. company_operations and company_cash_flow are
the same column subsets of that view on both paths.
"""

from __future__ import annotations

import os

import pandas as pd
from dotenv import load_dotenv

from src.bp_metrics import ROOT, assemble_views, build_views

load_dotenv(ROOT / ".env")

DATABRICKS_VIEWS = {
    "growth_trend": "financial_analytics.analytics.growth_trend",
    "performance": "financial_analytics.analytics.performance",
    "financial_health": "financial_analytics.analytics.financial_health",
    "peer_benchmarking": "financial_analytics.analytics.peer_benchmarking",
    "executive_summary": "financial_analytics.analytics.executive_summary",
}


def databricks_configured() -> bool:
    return bool(
        os.getenv("DATABRICKS_SERVER_HOSTNAME", "").strip()
        and os.getenv("DATABRICKS_HTTP_PATH", "").strip()
        and os.getenv("DATABRICKS_TOKEN", "").strip()
    )


def load_views() -> dict[str, pd.DataFrame]:
    if databricks_configured():
        return assemble_views(_load_from_databricks())
    return build_views()


def _connect_databricks():
    from databricks import sql

    return sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )


def _load_from_databricks() -> dict[str, pd.DataFrame]:
    conn = _connect_databricks()
    out: dict[str, pd.DataFrame] = {}
    try:
        with conn.cursor() as cur:
            for key, table in DATABRICKS_VIEWS.items():
                cur.execute(f"SELECT * FROM {table}")
                rows = cur.fetchall()
                cols = [c[0] for c in cur.description]
                out[key] = pd.DataFrame(rows, columns=cols)
    finally:
        conn.close()
    return out
