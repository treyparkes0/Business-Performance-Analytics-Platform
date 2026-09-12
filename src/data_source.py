"""
Retrieve analytics views for the app.

Databricks SQL views are the source of truth. Local CSVs reproduce those
views from company_financials_wide.csv when a warehouse connection is
not configured. Python only filters, formats, and attaches interpretations.
"""

from __future__ import annotations

import os

import pandas as pd
from dotenv import load_dotenv

from src.bp_metrics import ROOT, build_views

load_dotenv(ROOT / ".env")

DATABRICKS_VIEWS = {
    "company_performance": "financial_analytics.analytics.growth_trend",
    "company_operations": "financial_analytics.analytics.performance",
    "company_cash_flow": "financial_analytics.analytics.performance",
    "company_financial_health": "financial_analytics.analytics.financial_health",
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
        return _load_from_databricks()
    return build_views()


def _load_from_databricks() -> dict[str, pd.DataFrame]:
    from databricks import sql

    conn = sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )
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
