"""Render the Databricks notebook inside the Streamlit app."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


def _cell_source(cell: dict) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(source)
    return str(source)


def _code_language(source: str) -> str:
    text = source.lstrip()
    head = text[:120].upper()
    if text.startswith("%sql") or "CREATE " in head or head.startswith("SELECT") or "FROM FINANCIAL_ANALYTICS" in head:
        return "sql"
    return "python"


def _join_text(value) -> str:
    if isinstance(value, list):
        return "".join(str(part) for part in value)
    return str(value or "")


def _databricks_table(output: dict) -> pd.DataFrame | None:
    meta = output.get("metadata", {}).get("application/vnd.databricks.v1+output", {})
    data = meta.get("data")
    schema = meta.get("schema")
    if not data or not schema:
        return None
    columns = []
    for col in schema:
        if isinstance(col, dict):
            columns.append(col.get("name") or col.get("field") or "")
        else:
            columns.append(str(col))
    try:
        return pd.DataFrame(data, columns=columns or None)
    except ValueError:
        return pd.DataFrame(data)


def render_notebook(path: Path) -> None:
    if not path.exists():
        st.error(f"Notebook not found: {path.name}")
        return
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for cell in notebook.get("cells", []):
        kind = cell.get("cell_type")
        source = _cell_source(cell).strip()
        if kind == "markdown":
            if source:
                st.markdown(source)
            continue
        if kind != "code" or not source:
            continue
        st.code(source, language=_code_language(source))
        for output in cell.get("outputs", []):
            table = _databricks_table(output)
            if table is not None and not table.empty:
                st.dataframe(table, use_container_width=True, hide_index=True)
                continue
            text = _join_text(output.get("text"))
            if text.strip():
                st.text(text)
                continue
            data = output.get("data") or {}
            plain = _join_text(data.get("text/plain"))
            if plain.strip() and "<table" not in plain:
                st.text(plain)
