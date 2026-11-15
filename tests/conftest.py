import pytest

from src.bp_metrics import build_views


@pytest.fixture(scope="session")
def views():
    return build_views()
