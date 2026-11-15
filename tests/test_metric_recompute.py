"""Recompute margins, cash flow, leverage, and returns from the raw CSV."""

import pandas as pd

from src.bp_metrics import CASH_CONVERSION_ABS_THRESHOLD, WIDE_CSV


def _r3(series: pd.Series) -> pd.Series:
    return series.round(3)


def _raw() -> pd.DataFrame:
    frame = pd.read_csv(WIDE_CSV)
    frame["Fiscal_Year"] = pd.to_numeric(frame["Fiscal_Year"]).astype(int)
    return frame.sort_values(["Ticker", "Fiscal_Year"], kind="mergesort").reset_index(drop=True)


def _close(actual: pd.Series, expected: pd.Series, atol: float = 1e-9) -> None:
    both_missing = actual.isna() & expected.isna()
    diff = (actual.astype(float) - expected.astype(float)).abs()
    assert (both_missing | (diff <= atol)).all()


def test_margins_fcf_de_returns_and_cash_flag(views):
    raw = _raw()
    perf = views["performance"].copy()
    health = views["financial_health"].copy()
    perf["Fiscal_Year"] = perf["Fiscal_Year"].astype(int)
    health["Fiscal_Year"] = health["Fiscal_Year"].astype(int)
    raw["Company"] = raw["Company"].astype(str)
    perf["Company"] = perf["Company"].astype(str)
    health["Company"] = health["Company"].astype(str)

    revenue = raw["Revenue"].replace(0, pd.NA)
    gross = _r3(raw["Gross_Profit"] / revenue)
    operating = _r3(raw["Operating_Income"] / revenue)
    net_margin = _r3(raw["Net_Income"] / revenue)
    ocf_margin = _r3(raw["Cash_Flow_from_Operating_Activities"] / revenue)
    opex_ratio = _r3(raw["Operating_Expenses"] / revenue)
    free_cash = _r3(raw["Cash_Flow_from_Operating_Activities"] - raw["Capital_Expenditures"])
    free_cash_margin = _r3(free_cash / revenue)
    raw_conversion = raw["Cash_Flow_from_Operating_Activities"] / raw["Net_Income"].replace(0, pd.NA)
    conversion = _r3(raw_conversion)
    known = raw["Net_Income"].notna() & raw["Cash_Flow_from_Operating_Activities"].notna()
    meaningful = pd.Series(pd.NA, index=raw.index, dtype="boolean")
    meaningful = meaningful.mask(known, True)
    meaningful = meaningful.mask(known & (raw["Net_Income"] <= 0), False)
    meaningful = meaningful.mask(known & raw_conversion.abs().gt(CASH_CONVERSION_ABS_THRESHOLD).fillna(False), False)

    prior_assets = raw.groupby("Ticker", sort=False)["Total_Assets"].shift(1)
    prior_equity = raw.groupby("Ticker", sort=False)["Total_Stockholders_Equity"].shift(1)
    roa_ending = _r3(raw["Net_Income"] / raw["Total_Assets"].replace(0, pd.NA))
    roe_ending = _r3(raw["Net_Income"] / raw["Total_Stockholders_Equity"].replace(0, pd.NA))
    roa_avg = _r3(raw["Net_Income"] / ((raw["Total_Assets"] + prior_assets) / 2).replace(0, pd.NA))
    roe_avg = _r3(raw["Net_Income"] / ((raw["Total_Stockholders_Equity"] + prior_equity) / 2).replace(0, pd.NA))
    roa = roa_avg.where(prior_assets.notna(), roa_ending)
    roe = roe_avg.where(prior_equity.notna(), roe_ending)
    total_debt = raw["Short_Term_Debt"].fillna(0) + raw["Long_Term_Debt"].fillna(0)
    debt_to_equity = _r3(total_debt / raw["Total_Stockholders_Equity"].replace(0, pd.NA))

    expected = raw[["Company", "Fiscal_Year"]].copy()
    expected["Gross_Margin_pct"] = gross
    expected["Operating_Margin_pct"] = operating
    expected["Net_Income_Margin_pct"] = net_margin
    expected["Operating_Cash_Flow_Margin_pct"] = ocf_margin
    expected["Operating_Expense_to_Revenue"] = opex_ratio
    expected["Free_Cash_Flow"] = free_cash
    expected["Free_Cash_Flow_Margin_pct"] = free_cash_margin
    expected["Cash_Conversion_Ratio"] = conversion
    expected["Cash_Conversion_Meaningful"] = meaningful
    expected["ROA_Ending"] = roa_ending
    expected["ROE_Ending"] = roe_ending
    expected["ROA_Avg"] = roa_avg
    expected["ROE_Avg"] = roe_avg
    expected["ROA"] = roa
    expected["ROE"] = roe
    expected["debt_to_equity_ratio"] = debt_to_equity

    merged = expected.merge(perf, on=["Company", "Fiscal_Year"], suffixes=("_exp", "_view"))
    health_merged = expected.merge(health, on=["Company", "Fiscal_Year"], suffixes=("_exp", "_view"))
    for column in [
        "Gross_Margin_pct",
        "Operating_Margin_pct",
        "Net_Income_Margin_pct",
        "Operating_Cash_Flow_Margin_pct",
        "Operating_Expense_to_Revenue",
        "Free_Cash_Flow",
        "Free_Cash_Flow_Margin_pct",
        "Cash_Conversion_Ratio",
    ]:
        _close(merged[f"{column}_exp"], merged[f"{column}_view"])
    for column in ["ROA_Ending", "ROE_Ending", "ROA_Avg", "ROE_Avg", "ROA", "ROE", "debt_to_equity_ratio"]:
        _close(health_merged[f"{column}_exp"], health_merged[f"{column}_view"])

    view_flag = merged["Cash_Conversion_Meaningful_view"].map(lambda value: pd.NA if pd.isna(value) else bool(value))
    exp_flag = merged["Cash_Conversion_Meaningful_exp"].map(lambda value: pd.NA if pd.isna(value) else bool(value))
    assert view_flag.astype("string").equals(exp_flag.astype("string"))
