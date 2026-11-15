"""Identity checks for the SQL views, run against the local Python copy.

The Databricks definitions live in Business Performance Analytics.ipynb.
src/bp_metrics.py repeats those formulas. These tests lock the copy:
grain, fiscal-year gaps, known missing inputs, and the rounded ratios.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bp_metrics import RANKED_METRICS, build_views, impute_amd_liabilities  # noqa: E402

WIDE = ROOT / "data" / "processed" / "company_financials_wide.csv"
CLEAN = ROOT / "data" / "processed" / "sec_company_financials_clean.csv"

MISSING_OPEX = {
    ("AMD", 2021),
    ("AMD", 2022),
    ("Microsoft", 2021),
    ("Microsoft", 2022),
}
LATEST_YEAR = {
    "AMD": 2025,
    "Adobe": 2025,
    "Apple": 2025,
    "CrowdStrike": 2026,
    "Microsoft": 2026,
    "NVIDIA": 2026,
}
# Average_Rank is the equal-weight mean of these nine ranks. Nothing else.
AVERAGE_RANK_COLUMNS = [rank_col for _value, _higher, rank_col in RANKED_METRICS]


def _r3(series: pd.Series) -> pd.Series:
    return series.round(3)


def _close(left: pd.Series, right: pd.Series, tol: float = 0.0005) -> pd.Series:
    both_null = left.isna() & right.isna()
    return both_null | ((left - right).abs() <= tol)


class Phase1SqlMetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wide = pd.read_csv(WIDE)
        cls.views = build_views(WIDE)
        cls.base = impute_amd_liabilities(cls.wide.copy())
        cls.growth = cls.views["growth_trend"]
        cls.perf = cls.views["performance"]
        cls.health = cls.views["financial_health"]
        cls.peers = cls.views["peer_benchmarking"]
        cls.summary = cls.views["executive_summary"]

    def test_clean_file_matches_wide_inputs(self) -> None:
        self.assertTrue(
            CLEAN.exists(),
            f"Missing {CLEAN}. The AMD liabilities flag is read from this extract.",
        )
        clean = pd.read_csv(CLEAN)
        self.assertEqual(len(clean), 1657)
        self.assertEqual(int(clean["Value"].isna().sum()), 0)
        self.assertEqual(
            int(clean.duplicated(["Company", "Fiscal_Year", "Metric"]).sum()),
            0,
        )
        keys = [
            "Revenue",
            "Net_Income",
            "Total_Assets",
            "Cash_Flow_from_Operating_Activities",
            "Operating_Expenses",
            "Capital_Expenditures",
        ]
        raw = self.wide.copy()
        for metric in keys:
            facts = clean.loc[clean["Metric"] == metric, ["Company", "Fiscal_Year", "Value"]]
            merged = facts.merge(raw, on=["Company", "Fiscal_Year"], how="left")
            self.assertTrue(
                _close(merged["Value"], merged[metric], tol=1.0).all(),
                metric,
            )

    def test_company_year_grain_and_fiscal_alignment(self) -> None:
        self.assertEqual(len(self.base), 33)
        self.assertEqual(int(self.base.duplicated(["Company", "Fiscal_Year"]).sum()), 0)
        self.assertEqual(self.base.groupby("Company")["Ticker"].nunique().max(), 1)
        for company, expected_last in LATEST_YEAR.items():
            years = sorted(self.base.loc[self.base["Company"] == company, "Fiscal_Year"].tolist())
            self.assertEqual(years[0], 2021)
            self.assertEqual(years[-1], expected_last)
            self.assertEqual(years, list(range(2021, expected_last + 1)))

    def test_known_missing_inputs_are_only_the_recorded_rows(self) -> None:
        opex_missing = {
            (row.Company, int(row.Fiscal_Year))
            for row in self.wide.loc[self.wide["Operating_Expenses"].isna()].itertuples()
        }
        self.assertEqual(opex_missing, MISSING_OPEX)
        capex_missing = {
            (row.Company, int(row.Fiscal_Year))
            for row in self.wide.loc[self.wide["Capital_Expenditures"].isna()].itertuples()
        }
        self.assertEqual(capex_missing, {("NVIDIA", 2021)})
        self.assertEqual(int((self.base["Total_Stockholders_Equity"] <= 0).sum()), 0)
        self.assertEqual(int((self.base["Total_Current_Liabilities"] == 0).sum()), 0)

    def test_amd_liabilities_are_derived_from_assets_minus_equity(self) -> None:
        stored = self.wide.loc[self.wide["Company"] == "AMD", "Total_Liabilities"]
        self.assertTrue(stored.isna().all())
        amd = self.base.loc[self.base["Company"] == "AMD"]
        derived = amd["Total_Assets"] - amd["Total_Stockholders_Equity"]
        self.assertTrue(_close(amd["Total_Liabilities"], derived, tol=1.0).all())

    def test_growth_trend_identity(self) -> None:
        ordered = self.base.sort_values(["Company", "Fiscal_Year"])
        prior = ordered.groupby("Company")["Revenue"].shift(1)
        expected_growth = _r3((ordered["Revenue"] - prior) / prior.replace(0, pd.NA))
        prior_growth = expected_growth.groupby(ordered["Company"]).shift(1)
        # Differential uses the unrounded rates, then rounds. Match the view.
        raw_growth = (ordered["Revenue"] - prior) / prior.replace(0, pd.NA)
        raw_prior = raw_growth.groupby(ordered["Company"]).shift(1)
        expected_diff = _r3(raw_growth - raw_prior)
        expected_margin = _r3(ordered["Net_Income"] / ordered["Revenue"].replace(0, pd.NA))
        got = self.growth.merge(
            ordered.assign(
                expected_growth=expected_growth,
                expected_prior=prior_growth,
                expected_diff=expected_diff,
                expected_margin=expected_margin,
            )[
                [
                    "Company",
                    "Fiscal_Year",
                    "expected_growth",
                    "expected_prior",
                    "expected_diff",
                    "expected_margin",
                ]
            ],
            on=["Company", "Fiscal_Year"],
        )
        self.assertTrue(_close(got["Growth_Rate"], got["expected_growth"]).all())
        self.assertTrue(_close(got["Prior_Growth_Rate"], got["expected_prior"]).all())
        self.assertTrue(_close(got["Growth_Differential"], got["expected_diff"]).all())
        self.assertTrue(_close(got["Net_Income_Margin_pct"], got["expected_margin"]).all())
        first = got.sort_values(["Company", "Fiscal_Year"]).groupby("Company").head(1)
        self.assertTrue(first["Growth_Rate"].isna().all())
        second = got.sort_values(["Company", "Fiscal_Year"]).groupby("Company").nth(1)
        self.assertTrue(second["Growth_Rate"].notna().all())
        self.assertTrue(second["Growth_Differential"].isna().all())

    def test_performance_identities(self) -> None:
        ordered = self.base.sort_values(["Company", "Fiscal_Year"])
        prior_oi = ordered.groupby("Company")["Operating_Income"].shift(1)
        prior_opex = ordered.groupby("Company")["Operating_Expenses"].shift(1)
        raw_opex_growth = (ordered["Operating_Expenses"] - prior_opex) / prior_opex.replace(0, pd.NA)
        raw_rev_growth = (
            ordered["Revenue"] - ordered.groupby("Company")["Revenue"].shift(1)
        ) / ordered.groupby("Company")["Revenue"].shift(1).replace(0, pd.NA)
        expected = ordered.assign(
            gross=_r3(ordered["Gross_Profit"] / ordered["Revenue"].replace(0, pd.NA)),
            operating=_r3(ordered["Operating_Income"] / ordered["Revenue"].replace(0, pd.NA)),
            oi_growth=_r3(
                (ordered["Operating_Income"] - prior_oi) / prior_oi.replace(0, pd.NA)
            ),
            opex_growth=_r3(raw_opex_growth),
            opex_ratio=_r3(ordered["Operating_Expenses"] / ordered["Revenue"].replace(0, pd.NA)),
            rev_minus_opex=_r3(raw_rev_growth - raw_opex_growth),
            fcf=_r3(
                ordered["Cash_Flow_from_Operating_Activities"] - ordered["Capital_Expenditures"]
            ),
            cash_conversion=_r3(
                ordered["Cash_Flow_from_Operating_Activities"]
                / ordered["Net_Income"].replace(0, pd.NA)
            ),
        )
        got = self.perf.merge(
            expected[
                [
                    "Company",
                    "Fiscal_Year",
                    "gross",
                    "operating",
                    "oi_growth",
                    "opex_growth",
                    "opex_ratio",
                    "rev_minus_opex",
                    "fcf",
                    "cash_conversion",
                ]
            ],
            on=["Company", "Fiscal_Year"],
        )
        pairs = [
            ("Gross_Margin_pct", "gross"),
            ("Operating_Margin_pct", "operating"),
            ("Operating_Income_Growth", "oi_growth"),
            ("Operating_Expense_Growth", "opex_growth"),
            ("Operating_Expense_to_Revenue", "opex_ratio"),
            ("Revenue_Growth_Minus_Opex_Growth", "rev_minus_opex"),
            ("Free_Cash_Flow", "fcf"),
            ("Cash_Conversion_Ratio", "cash_conversion"),
        ]
        for actual, expect in pairs:
            tol = 1.0 if actual == "Free_Cash_Flow" else 0.0005
            self.assertTrue(_close(got[actual], got[expect], tol=tol).all(), actual)
        fcf_null = {
            (row.Company, int(row.Fiscal_Year))
            for row in got.loc[got["Free_Cash_Flow"].isna()].itertuples()
        }
        self.assertEqual(fcf_null, {("NVIDIA", 2021)})
        # Prior opex is missing, so the first year that has opex still has null growth.
        for company, year in (("AMD", 2023), ("Microsoft", 2023)):
            row = got.loc[(got["Company"] == company) & (got["Fiscal_Year"] == year)].iloc[0]
            self.assertTrue(pd.notna(row["Operating_Expenses"]))
            self.assertTrue(pd.isna(row["Operating_Expense_Growth"]))

    def test_financial_health_identities(self) -> None:
        ordered = self.base.sort_values(["Ticker", "Fiscal_Year"])
        prior_assets = ordered.groupby("Ticker")["Total_Assets"].shift(1)
        prior_equity = ordered.groupby("Ticker")["Total_Stockholders_Equity"].shift(1)
        debt = ordered["Short_Term_Debt"].fillna(0) + ordered["Long_Term_Debt"].fillna(0)
        expected = ordered.assign(
            current=_r3(
                ordered["Total_Current_Assets"]
                / ordered["Total_Current_Liabilities"].replace(0, pd.NA)
            ),
            debt=debt,
            de=_r3(debt / ordered["Total_Stockholders_Equity"].replace(0, pd.NA)),
            la=_r3(ordered["Total_Liabilities"] / ordered["Total_Assets"].replace(0, pd.NA)),
            roa_ending_raw=ordered["Net_Income"] / ordered["Total_Assets"].replace(0, pd.NA),
            roe_ending_raw=ordered["Net_Income"]
            / ordered["Total_Stockholders_Equity"].replace(0, pd.NA),
            roa_avg_raw=ordered["Net_Income"] / ((ordered["Total_Assets"] + prior_assets) / 2),
            roe_avg_raw=ordered["Net_Income"]
            / ((ordered["Total_Stockholders_Equity"] + prior_equity) / 2),
            roa_uses_ending=prior_assets.isna(),
            roe_uses_ending=prior_equity.isna(),
        )
        expected["roa_ending"] = _r3(expected["roa_ending_raw"])
        expected["roe_ending"] = _r3(expected["roe_ending_raw"])
        expected["roa_avg"] = _r3(expected["roa_avg_raw"])
        expected["roe_avg"] = _r3(expected["roe_avg_raw"])
        expected["roa"] = _r3(
            expected["roa_avg_raw"].where(~expected["roa_uses_ending"], expected["roa_ending_raw"])
        )
        expected["roe"] = _r3(
            expected["roe_avg_raw"].where(~expected["roe_uses_ending"], expected["roe_ending_raw"])
        )
        got = self.health.merge(
            expected[
                [
                    "Company",
                    "Fiscal_Year",
                    "current",
                    "debt",
                    "de",
                    "la",
                    "roe_ending",
                    "roa_ending",
                    "roa_avg",
                    "roe_avg",
                    "roa",
                    "roe",
                    "roa_uses_ending",
                    "roe_uses_ending",
                ]
            ],
            on=["Company", "Fiscal_Year"],
        )
        pairs = [
            ("Current_ratio", "current"),
            ("Total_Debt", "debt"),
            ("debt_to_equity_ratio", "de"),
            ("Liabilities_to_Assets", "la"),
            ("ROE_Ending", "roe_ending"),
            ("ROA_Ending", "roa_ending"),
            ("ROA_Avg", "roa_avg"),
            ("ROE_Avg", "roe_avg"),
            ("ROA", "roa"),
            ("ROE", "roe"),
        ]
        for actual, expect in pairs:
            tol = 1.0 if actual == "Total_Debt" else 0.0005
            self.assertTrue(_close(got[actual], got[expect], tol=tol).all(), actual)
        self.assertTrue(got["ROA_Uses_Ending_Balance"].eq(got["roa_uses_ending"]).all())
        self.assertTrue(got["ROE_Uses_Ending_Balance"].eq(got["roe_uses_ending"]).all())
        self.assertTrue(self.wide.loc[self.wide["Company"] == "CrowdStrike", "Short_Term_Debt"].isna().all())
        crwd = got.loc[got["Company"] == "CrowdStrike", ["Fiscal_Year", "Total_Debt"]].merge(
            self.base.loc[self.base["Company"] == "CrowdStrike", ["Fiscal_Year", "Long_Term_Debt"]],
            on="Fiscal_Year",
        )
        self.assertTrue(_close(crwd["Total_Debt"], crwd["Long_Term_Debt"], tol=1.0).all())

    def test_peer_benchmark_is_fy2025_and_average_uses_nine_ranks(self) -> None:
        self.assertEqual(len(self.peers), 6)
        self.assertTrue((self.peers["Fiscal_Year"] == 2025).all())
        rank_cols = [c for c in self.peers.columns if c.endswith("_Rank") and c != "Average_Rank"]
        self.assertEqual(rank_cols, AVERAGE_RANK_COLUMNS)
        self.assertEqual(len(rank_cols), 9)
        for obsolete in (
            "Growth_Differential_Rank",
            "Operating_Expense_Growth_Rank",
            "Liabilities_to_Assets_Rank",
        ):
            self.assertNotIn(obsolete, self.peers.columns)
        for col in rank_cols:
            self.assertTrue(self.peers[col].between(1, 6).all(), col)
        expected_avg = _r3(self.peers[AVERAGE_RANK_COLUMNS].sum(axis=1) / 9.0)
        self.assertTrue(_close(self.peers["Average_Rank"], expected_avg).all())
        nvidia = self.peers.loc[self.peers["Company"] == "NVIDIA"].iloc[0]
        self.assertEqual(float(nvidia["Average_Rank"]), 1.222)
        self.assertEqual(float(nvidia["Operating_Expense_to_Revenue_Rank"]), 1.0)
        self.assertEqual(float(nvidia["Debt_to_Equity_Rank"]), 2.0)

    def test_executive_summary_keeps_fy2025_ranks_on_later_rows(self) -> None:
        self.assertEqual(len(self.summary), 6)
        years = dict(zip(self.summary["Company"], self.summary["Fiscal_Year"].astype(int)))
        self.assertEqual(years, LATEST_YEAR)
        self.assertTrue(self.summary["Benchmark_Fiscal_Year"].astype(int).eq(2025).all())
        self.assertTrue(self.summary["FY2025_Growth_Rate_Rank"].notna().all())
        self.assertTrue(self.summary["FY2025_Average_Rank"].notna().all())
        later = self.summary["Company"].isin(["Microsoft", "NVIDIA", "CrowdStrike"])
        self.assertTrue(self.summary.loc[later, "Fiscal_Year"].astype(int).eq(2026).all())
        self.assertTrue(self.summary.loc[later, "Growth_Rate"].notna().all())


if __name__ == "__main__":
    unittest.main()
