"""Rounding order and missing values that must stay null."""

import pandas as pd

from app import KPI_GROUPS, LEAD_LABELS
from src.bp_metrics import financial_health, performance
from src.interpretations import ALERTS


def _frame():
    return pd.DataFrame(
        [
            {
                "Company": "A",
                "Fiscal_Year": 2024,
                "Revenue": 1000.0,
                "Gross_Profit": 400.0,
                "Net_Income": 50.0,
                "Operating_Income": 80.0,
                "Operating_Expenses": 500.0,
                "Cash_Flow_from_Operating_Activities": 40.0,
                "Capital_Expenditures": 10.0,
            },
            {
                "Company": "A",
                "Fiscal_Year": 2025,
                "Revenue": 1064.4,
                "Gross_Profit": 420.0,
                "Net_Income": 55.0,
                "Operating_Income": 85.0,
                "Operating_Expenses": 540.8,
                "Cash_Flow_from_Operating_Activities": 42.0,
                "Capital_Expenditures": float("nan"),
            },
            {
                "Company": "B",
                "Fiscal_Year": 2024,
                "Revenue": 200.0,
                "Gross_Profit": 80.0,
                "Net_Income": 10.0,
                "Operating_Income": 20.0,
                "Operating_Expenses": float("nan"),
                "Cash_Flow_from_Operating_Activities": 12.0,
                "Capital_Expenditures": 3.0,
            },
            {
                "Company": "B",
                "Fiscal_Year": 2025,
                "Revenue": 220.0,
                "Gross_Profit": 90.0,
                "Net_Income": -4.0,
                "Operating_Income": -6.0,
                "Operating_Expenses": 100.0,
                "Cash_Flow_from_Operating_Activities": 30.0,
                "Capital_Expenditures": 0.0,
            },
        ]
    )


def _growth(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Company": frame["Company"],
            "Fiscal_Year": frame["Fiscal_Year"],
            "Growth_Rate": [float("nan"), 0.064, float("nan"), 0.100],
            "Net_Income_Margin_pct": [0.050, 0.052, 0.050, -0.018],
        }
    )


def test_efficiency_gap_uses_full_precision_then_rounds():
    out = performance(_frame(), _growth(_frame()))
    row = out.loc[(out["Company"] == "A") & (out["Fiscal_Year"] == 2025)].iloc[0]
    # 0.0644 - 0.0816 = -0.0172, which rounds to -0.017.
    # Rounding each rate first would produce 0.064 - 0.082 = -0.018.
    assert row["Operating_Expense_Growth"] == 0.082
    assert row["Revenue_Growth_Minus_Opex_Growth"] == -0.017
    assert row["Revenue_Growth_Minus_Opex_Growth"] != -0.018


def test_missing_capex_and_opex_stay_null():
    out = performance(_frame(), _growth(_frame()))
    missing_capex = out.loc[(out["Company"] == "A") & (out["Fiscal_Year"] == 2025)].iloc[0]
    assert pd.isna(missing_capex["Capital_Expenditures"])
    assert pd.isna(missing_capex["Free_Cash_Flow"])
    assert pd.isna(missing_capex["Free_Cash_Flow_Margin_pct"])

    missing_prior_opex = out.loc[(out["Company"] == "B") & (out["Fiscal_Year"] == 2025)].iloc[0]
    assert missing_prior_opex["Operating_Expenses"] == 100.0
    assert pd.isna(missing_prior_opex["Operating_Expense_Growth"])
    assert pd.isna(missing_prior_opex["Revenue_Growth_Minus_Opex_Growth"])
    assert missing_prior_opex["Free_Cash_Flow"] == 30.0


def test_negative_net_income_makes_cash_conversion_not_meaningful():
    out = performance(_frame(), _growth(_frame()))
    row = out.loc[(out["Company"] == "B") & (out["Fiscal_Year"] == 2025)].iloc[0]
    assert row["Net_Income"] < 0
    assert bool(row["Cash_Conversion_Meaningful"]) is False
    assert row["Cash_Conversion_Ratio"] == -7.5


def test_nvidia_fy2021_capex_is_missing_not_zero(views):
    row = views["performance"].loc[
        (views["performance"]["Company"] == "NVIDIA") & (views["performance"]["Fiscal_Year"] == 2021)
    ].iloc[0]
    assert pd.isna(row["Capital_Expenditures"])
    assert pd.isna(row["Free_Cash_Flow"])
    assert pd.isna(row["Free_Cash_Flow_Margin_pct"])
    assert row["Cash_Flow_from_Operating_Activities"] > 0


def test_missing_short_term_debt_is_not_marked_reported():
    frame = pd.DataFrame(
        [
            {
                "Company": "CrowdStrike",
                "Ticker": "CRWD",
                "Fiscal_Year": 2025,
                "Total_Assets": 1000.0,
                "Total_Stockholders_Equity": 400.0,
                "Total_Liabilities": 600.0,
                "Total_Current_Assets": 300.0,
                "Total_Current_Liabilities": 150.0,
                "Short_Term_Debt": float("nan"),
                "Long_Term_Debt": 80.0,
                "Net_Income": -5.0,
                "Cash_Flow_from_Operating_Activities": 20.0,
            }
        ]
    )
    health = financial_health(frame, reported_keys={("CrowdStrike", 2025)})
    row = health.iloc[0]
    assert bool(row["Short_Term_Debt_Reported"]) is False
    assert row["Total_Debt"] == 80.0
    assert bool(row["Total_Liabilities_Imputed"]) is False


def test_fcf_is_not_a_lead_kpi_and_each_company_has_one_alert():
    assert "Free Cash Flow" not in LEAD_LABELS
    assert "Free Cash Flow" not in KPI_GROUPS["Cash"]
    assert [alert["company"] for alert in ALERTS] == [
        "Microsoft",
        "Apple",
        "NVIDIA",
        "Adobe",
        "AMD",
        "CrowdStrike",
    ]
    for alert in ALERTS:
        assert alert["signal"]
        assert alert["why"]
        assert alert["trend"]
        assert alert["attention"]
        assert "continue monitoring financial performance" not in alert["attention"].lower()
