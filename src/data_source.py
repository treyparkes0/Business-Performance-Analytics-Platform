"""Load the analytics views for the app.

Reads the five warehouse views when DATABRICKS_SERVER_HOSTNAME,
DATABRICKS_HTTP_PATH, and DATABRICKS_TOKEN are set. Otherwise builds
them from data/processed/company_financials_wide.csv.

peer_metrics is put together here from those views. It is not a warehouse table.
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
    try:
        from databricks import sql
    except ImportError as exc:
        raise ImportError(
            "Databricks credentials are set, but databricks-sql-connector is not installed. "
            "Install that package to read the warehouse. The app runs from "
            "data/processed/company_financials_wide.csv without it."
        ) from exc

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
