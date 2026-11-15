"""Loader contract: local CSV and a mocked Databricks cursor return the same views."""

from decimal import Decimal

import pandas as pd

from app import PEER_METRICS, fiscal_year_options
from src.bp_metrics import (
    CASH_FLOW_COLUMNS,
    CONTRACT_KEYS,
    OPERATIONS_COLUMNS,
    PEER_COLUMNS,
    PEER_METRIC_COLUMNS,
    PERFORMANCE_COLUMNS,
    SOURCE_VIEW_COLUMNS,
    build_views,
)
from src.data_source import DATABRICKS_VIEWS, load_views


def _warehouse_cell(value):
    if value is None or value is pd.NA:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, (int,)) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return Decimal(str(value))
    return value


def _warehouse_shape(frame: pd.DataFrame) -> pd.DataFrame:
    """Lowercase names and Decimal numbers, the way a SQL cursor often returns a view."""
    shaped = pd.DataFrame(
        {
            column.lower(): [_warehouse_cell(value) for value in frame[column].tolist()]
            for column in frame.columns
        }
    )
    return shaped


class _Cursor:
    def __init__(self, frames: dict[str, pd.DataFrame]):
        self.frames = frames
        self.queries: list[str] = []
        self.description = None
        self._frame = None

    def execute(self, query: str) -> None:
        self.queries.append(query)
        matched = None
        for table, frame in sorted(self.frames.items(), key=lambda item: len(item[0]), reverse=True):
            if table in query:
                matched = frame
                break
        if matched is None:
            raise AssertionError(query)
        self._frame = matched
        self.description = [(column,) for column in matched.columns]

    def fetchall(self):
        return list(self._frame.itertuples(index=False, name=None))

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> bool:
        return False


class _Connection:
    def __init__(self, cursor: _Cursor):
        self._cursor = cursor
        self.closed = False

    def cursor(self) -> _Cursor:
        return self._cursor

    def close(self) -> None:
        self.closed = True


def test_local_contract_keys_columns_and_dtypes(views):
    assert tuple(views) == CONTRACT_KEYS
    for key, columns in SOURCE_VIEW_COLUMNS.items():
        assert list(views[key].columns) == list(columns)
    assert list(views["company_performance"].columns) == list(views["growth_trend"].columns)
    assert list(views["company_financial_health"].columns) == list(views["financial_health"].columns)
    assert list(views["company_operations"].columns) == OPERATIONS_COLUMNS
    assert list(views["company_cash_flow"].columns) == CASH_FLOW_COLUMNS
    assert list(views["performance"].columns) == PERFORMANCE_COLUMNS
    assert OPERATIONS_COLUMNS != PERFORMANCE_COLUMNS
    assert CASH_FLOW_COLUMNS != PERFORMANCE_COLUMNS
    assert list(views["peer_metrics"].columns) == PEER_METRIC_COLUMNS
    assert list(views["peer_benchmarking"].columns) == PEER_COLUMNS
    assert views["peer_metrics"]["Fiscal_Year"].nunique() > 1
    assert set(views["peer_benchmarking"]["Fiscal_Year"]) == {2025}
    for label, (column, _higher, _pct) in PEER_METRICS.items():
        assert column in views["peer_metrics"].columns, label
    sample = views["peer_metrics"]
    assert str(sample["Company"].dtype) == "string"
    assert str(sample["Fiscal_Year"].dtype) == "Int64"
    assert str(sample["Growth_Rate"].dtype) == "float64"
    assert str(views["performance"]["Cash_Conversion_Meaningful"].dtype) == "boolean"
    assert str(views["peer_benchmarking"]["Growth_Rate_Rank"].dtype) == "Int64"
    assert str(views["peer_benchmarking"]["Average_Rank"].dtype) == "float64"


def test_year_options_do_not_mix_latest():
    assert fiscal_year_options([2024, 2025, 2026]) == ["All", "2026", "2025", "2024"]
    assert "Latest" not in fiscal_year_options([2025, 2026])


def test_databricks_cursor_matches_local_contract(monkeypatch, views):
    for name in ("DATABRICKS_SERVER_HOSTNAME", "DATABRICKS_HTTP_PATH", "DATABRICKS_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    local = load_views()
    pd.testing.assert_frame_equal(local["peer_metrics"], views["peer_metrics"])

    raw = {key: _warehouse_shape(views[key]) for key in DATABRICKS_VIEWS}
    cursor = _Cursor({DATABRICKS_VIEWS[key]: raw[key] for key in DATABRICKS_VIEWS})
    connection = _Connection(cursor)
    monkeypatch.setenv("DATABRICKS_SERVER_HOSTNAME", "warehouse.example.com")
    monkeypatch.setenv("DATABRICKS_HTTP_PATH", "/sql/warehouses/test")
    monkeypatch.setenv("DATABRICKS_TOKEN", "test-token")
    monkeypatch.setattr("src.data_source._connect_databricks", lambda: connection)

    loaded = load_views()
    assert connection.closed
    assert len(cursor.queries) == len(DATABRICKS_VIEWS)
    for table in DATABRICKS_VIEWS.values():
        assert any(table in query for query in cursor.queries)
    assert tuple(loaded) == CONTRACT_KEYS
    for key in CONTRACT_KEYS:
        pd.testing.assert_frame_equal(loaded[key], local[key], check_dtype=True, check_exact=False, rtol=1e-6, atol=1e-4)
        assert list(loaded[key].columns) == list(local[key].columns)
        assert list(loaded[key].dtypes.astype(str)) == list(local[key].dtypes.astype(str))
