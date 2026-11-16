"""Liability imputation, debt reported flags, cash-conversion flag, and return basis."""

import pandas as pd

from app import cash_nm_labels, peer_snapshot
from src.bp_metrics import (
    CASH_CONVERSION_ABS_THRESHOLD,
    WIDE_CSV,
    cash_conversion_meaningful,
    financial_health,
    impute_amd_liabilities,
)
from src.glossary import (
    AMD_LIABILITIES_NOTE,
    APPLE_ROE_CAVEAT,
    CASH_CONVERSION_NOTE,
    CROWDSTRIKE_DEBT_NOTE,
    FREE_CASH_FLOW_NOTE,
    METHODOLOGY_NOTES,
    ROA_ROE_NOTE,
    TERMS,
)


def test_imputation_is_limited_to_amd_nulls():
    frame = pd.DataFrame(
        {
            "Company": ["AMD", "Apple", "AMD"],
            "Total_Assets": [100.0, 80.0, 50.0],
            "Total_Stockholders_Equity": [40.0, 30.0, 20.0],
            "Total_Liabilities": [pd.NA, pd.NA, 10.0],
        }
    )
    out = impute_amd_liabilities(frame)
    assert out.loc[0, "Total_Liabilities"] == 60
    assert bool(out.loc[0, "Total_Liabilities_Imputed"]) is True
    assert pd.isna(out.loc[1, "Total_Liabilities"])
    assert bool(out.loc[1, "Total_Liabilities_Imputed"]) is False
    assert out.loc[2, "Total_Liabilities"] == 10
    assert bool(out.loc[2, "Total_Liabilities_Imputed"]) is False
    again = impute_amd_liabilities(out)
    assert bool(again.loc[0, "Total_Liabilities_Imputed"]) is True
    assert again.loc[0, "Total_Liabilities"] == 60


def test_prefilled_wide_table_keeps_the_flag_when_the_fact_is_absent():
    """The Databricks UPDATE can fill AMD liabilities before the view runs."""
    frame = pd.DataFrame(
        {
            "Company": ["AMD", "Apple"],
            "Fiscal_Year": [2025, 2025],
            "Total_Assets": [100.0, 80.0],
            "Total_Stockholders_Equity": [40.0, 50.0],
            "Total_Liabilities": [60.0, 30.0],
        }
    )
    without_facts = impute_amd_liabilities(frame)
    assert bool(without_facts.loc[0, "Total_Liabilities_Imputed"]) is False
    assert without_facts.loc[0, "Total_Liabilities"] == 60

    reported = {("Apple", 2025)}
    with_facts = impute_amd_liabilities(frame, reported_keys=reported)
    assert bool(with_facts.loc[0, "Total_Liabilities_Imputed"]) is True
    assert with_facts.loc[0, "Total_Liabilities"] == 60
    assert bool(with_facts.loc[1, "Total_Liabilities_Imputed"]) is False


def test_reported_fact_is_not_inferred_from_the_accounting_identity():
    frame = pd.DataFrame(
        {
            "Company": ["AMD", "AMD"],
            "Fiscal_Year": [2024, 2025],
            "Total_Assets": [100.0, 100.0],
            "Total_Stockholders_Equity": [40.0, 40.0],
            "Total_Liabilities": [60.0, pd.NA],
        }
    )
    reported = {("AMD", 2024), ("AMD", 2025)}
    out = impute_amd_liabilities(frame, reported_keys=reported)
    assert bool(out.loc[0, "Total_Liabilities_Imputed"]) is False
    assert out.loc[0, "Total_Liabilities"] == 60
    assert bool(out.loc[1, "Total_Liabilities_Imputed"]) is False
    assert pd.isna(out.loc[1, "Total_Liabilities"])


def test_health_flag_follows_facts_after_the_wide_table_is_filled():
    wide = pd.read_csv(WIDE_CSV)
    amd = wide["Company"] == "AMD"
    wide.loc[amd, "Total_Liabilities"] = (
        wide.loc[amd, "Total_Assets"] - wide.loc[amd, "Total_Stockholders_Equity"]
    )
    assert wide.loc[amd, "Total_Liabilities"].notna().all()
    health = financial_health(wide, reported_keys={("Apple", 2025)})
    assert health.loc[health["Company"] == "AMD", "Total_Liabilities_Imputed"].map(bool).all()
    apple = health.loc[(health["Company"] == "Apple") & (health["Fiscal_Year"] == 2025)].iloc[0]
    assert bool(apple["Total_Liabilities_Imputed"]) is False
    reported_years = {(str(company), int(year)) for company, year in zip(wide["Company"], wide["Fiscal_Year"])}
    reported_health = financial_health(wide, reported_keys=reported_years)
    assert not reported_health["Total_Liabilities_Imputed"].map(bool).any()


def test_source_flags(views):
    health = views["financial_health"]
    amd = health.loc[health["Company"] == "AMD"]
    assert amd["Total_Liabilities_Imputed"].map(bool).all()
    assert not health.loc[health["Company"] != "AMD", "Total_Liabilities_Imputed"].map(bool).any()
    amd_2025 = amd.loc[amd["Fiscal_Year"] == 2025].iloc[0]
    assert amd_2025["Total_Liabilities"] == amd_2025["Total_Assets"] - amd_2025["Total_Stockholders_Equity"]

    crowd = health.loc[health["Company"] == "CrowdStrike"]
    assert set(crowd["Fiscal_Year"].astype(int)) == {2021, 2022, 2023, 2024, 2025, 2026}
    assert not crowd["Short_Term_Debt_Reported"].map(bool).any()
    assert crowd["Long_Term_Debt_Reported"].map(bool).all()

    amd_2022 = amd.loc[amd["Fiscal_Year"] == 2022].iloc[0]
    assert bool(amd_2022["Short_Term_Debt_Reported"]) is True
    assert amd_2022["Total_Debt"] == 2467000000

    crowd_2025 = crowd.loc[crowd["Fiscal_Year"] == 2025].iloc[0]
    assert crowd_2025["Total_Debt"] == 743983000

    first = health.loc[health["Fiscal_Year"] == 2021]
    assert first["ROA_Uses_Ending_Balance"].map(bool).all()
    assert first["ROE_Uses_Ending_Balance"].map(bool).all()
    later = health.loc[health["Fiscal_Year"] == 2025]
    assert not later["ROA_Uses_Ending_Balance"].map(bool).any()
    assert not later["ROE_Uses_Ending_Balance"].map(bool).any()
    nvidia = later.loc[later["Company"] == "NVIDIA"].iloc[0]
    assert nvidia["ROA"] == nvidia["ROA_Avg"]
    assert nvidia["ROA"] != nvidia["ROA_Ending"]
    apple = later.loc[later["Company"] == "Apple"].iloc[0]
    assert apple["ROE"] == apple["ROE_Avg"]
    assert apple["ROE"] != apple["ROE_Ending"]

    summary = views["executive_summary"]
    assert summary["Benchmark_Fiscal_Year"].astype(int).eq(2025).all()
    latest = summary.loc[summary["Fiscal_Year"] == 2026]
    assert set(latest["Company"]) == {"CrowdStrike", "Microsoft", "NVIDIA"}
    assert latest["FY2025_Average_Rank"].notna().all()
    peers = views["peer_benchmarking"][["Company", "Average_Rank"]]
    joined = latest.merge(peers, on="Company")
    assert (joined["FY2025_Average_Rank"] - joined["Average_Rank"]).abs().max() < 1e-9


def test_cash_conversion_threshold_and_display(views):
    net_income = pd.Series([100.0, 100.0, 100.0, -5.0, 0.0, None])
    cash_flow = pd.Series([500.0, 500.01, 100.0, 10.0, 10.0, 10.0])
    flag = cash_conversion_meaningful(net_income, cash_flow)
    assert CASH_CONVERSION_ABS_THRESHOLD == 5
    assert bool(flag.iloc[0]) is True
    assert bool(flag.iloc[1]) is False
    assert bool(flag.iloc[2]) is True
    assert bool(flag.iloc[3]) is False
    assert bool(flag.iloc[4]) is False
    assert pd.isna(flag.iloc[5])

    perf = views["performance"]
    crowd_2025 = perf.loc[(perf["Company"] == "CrowdStrike") & (perf["Fiscal_Year"] == 2025)].iloc[0]
    assert crowd_2025["Cash_Conversion_Ratio"] == -90.659
    assert bool(crowd_2025["Cash_Conversion_Meaningful"]) is False
    crowd_2024 = perf.loc[(perf["Company"] == "CrowdStrike") & (perf["Fiscal_Year"] == 2024)].iloc[0]
    assert crowd_2024["Cash_Conversion_Ratio"] == 16.157
    assert bool(crowd_2024["Cash_Conversion_Meaningful"]) is False
    adobe_2025 = perf.loc[(perf["Company"] == "Adobe") & (perf["Fiscal_Year"] == 2025)].iloc[0]
    assert bool(adobe_2025["Cash_Conversion_Meaningful"]) is True

    shown = perf.loc[perf["Company"] == "CrowdStrike", ["Company", "Fiscal_Year", "Cash_Conversion_Ratio", "Cash_Conversion_Meaningful"]].copy()
    from app import attach_cash_conversion_display

    displayed = attach_cash_conversion_display(shown)
    fy2025 = displayed.loc[displayed["Fiscal_Year"] == 2025].iloc[0]
    assert fy2025["Cash_Conversion_Display"] == "n/m"
    assert fy2025["Cash_Conversion_Ratio"] == -90.659
    assert "CrowdStrike FY2025" in cash_nm_labels(displayed)


def test_earnings_growth_is_not_meaningful_when_prior_year_is_not_positive(views):
    from app import attach_earnings_growth_display, earnings_nm_labels

    performance = views["performance"]
    shown = attach_earnings_growth_display(performance, performance)
    crowd = shown.loc[shown["Company"] == "CrowdStrike"].set_index("Fiscal_Year")
    assert crowd.loc[2021, "Net_Income_Growth_Display"] == "—"
    assert crowd.loc[2022, "Net_Income_Growth_Display"] == "loss widened"
    assert crowd.loc[2023, "Net_Income_Growth_Display"] == "loss narrowed"
    assert crowd.loc[2024, "Net_Income_Growth_Display"] == "not meaningful"
    assert crowd.loc[2025, "Net_Income_Growth_Display"] == "not meaningful"
    assert crowd.loc[2026, "Net_Income_Growth_Display"] == "loss widened"
    assert crowd.loc[2026, "Operating_Income_Growth_Display"] == "loss widened"
    assert pd.isna(crowd.loc[2025, "Net_Income_Growth_Chart"])
    assert pd.isna(crowd.loc[2026, "Net_Income_Growth_Chart"])
    assert crowd.loc[2026, "Net_Income_Growth"] == performance.loc[
        (performance["Company"] == "CrowdStrike") & (performance["Fiscal_Year"] == 2026),
        "Net_Income_Growth",
    ].iloc[0]
    assert crowd.loc[2026, "Net_Income_Growth"] == 9.662
    apple = shown.loc[(shown["Company"] == "Apple") & (shown["Fiscal_Year"] == 2025)].iloc[0]
    assert apple["Net_Income_Growth_Display"] == "19.5%"
    labels = earnings_nm_labels(shown)
    assert "CrowdStrike FY2026 (loss widened)" in labels
    assert "CrowdStrike FY2023 (loss narrowed)" in labels
    assert "Apple FY2025" not in labels


def test_latest_peer_year_is_not_mixed(views):
    snapshot, label = peer_snapshot(views["peer_metrics"], "Latest")
    assert snapshot["Fiscal_Year"].nunique() == 1
    assert int(snapshot["Fiscal_Year"].iloc[0]) == 2025
    assert label == "FY2025"
    assert set(snapshot["Company"]) == set(views["peer_metrics"]["Company"])


def test_glossary_states_the_decisions():
    text = " ".join(str(term["meaning"]) + " " + str(term["calculation"]) for term in TERMS)
    text += " " + " ".join(METHODOLOGY_NOTES)
    assert "n/m" in text
    assert "CrowdStrike" in CROWDSTRIKE_DEBT_NOTE and "FY2021" in CROWDSTRIKE_DEBT_NOTE
    assert "Total_Liabilities" in AMD_LIABILITIES_NOTE
    assert "Buybacks inflate Apple" in APPLE_ROE_CAVEAT
    assert "average balances" in ROA_ROE_NOTE
    assert "greater than 5" in CASH_CONVERSION_NOTE
    assert "NVIDIA FY2021" in FREE_CASH_FLOW_NOTE
    assert "not filled with zero" in FREE_CASH_FLOW_NOTE
    assert FREE_CASH_FLOW_NOTE in text
    assert "NULLS LAST" in text
    assert "method='min'" in text
    for note in (ROA_ROE_NOTE, APPLE_ROE_CAVEAT, CASH_CONVERSION_NOTE, CROWDSTRIKE_DEBT_NOTE, AMD_LIABILITIES_NOTE):
        assert note in text
