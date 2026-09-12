"""
SEC EDGAR Company Facts extractor
=================================
Retrieves standardized annual (Form 10-K) financial statement metrics from the
official U.S. SEC Company Facts API for a small set of public companies.

Official endpoint only: https://data.sec.gov/api/xbrl/companyfacts/
One request per company. Does not scrape filing HTML. Does not fabricate values.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests

# =============================================================================
# 1. Configuration
# =============================================================================
COMPANIES: list[dict[str, str]] = [
    {"company": "Microsoft", "ticker": "MSFT", "cik": "0000789019"},
    {"company": "Apple", "ticker": "AAPL", "cik": "0000320193"},
    {"company": "NVIDIA", "ticker": "NVDA", "cik": "0001045810"},
    {"company": "Adobe", "ticker": "ADBE", "cik": "0000796343"},
    {"company": "AMD", "ticker": "AMD", "cik": "0000002488"},
    {"company": "CrowdStrike", "ticker": "CRWD", "cik": "0001535527"},
]

COMPANY_FACTS_BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts/"
REQUEST_TIMEOUT_SECONDS = 30
REQUEST_DELAY_SECONDS = 1.0
MIN_FISCAL_YEAR = 2021
ANNUAL_PERIOD_MIN_DAYS = 330
ANNUAL_PERIOD_MAX_DAYS = 400
ALLOWED_FORMS = {"10-K", "10-K/A"}
PREFERRED_TAXONOMY = "us-gaap"
SKIP_TAXONOMIES = {"dei"}

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MARKET_DATA_DIR = PROJECT_ROOT / "data" / "market data"
MARKET_PROCESSED_DIR = MARKET_DATA_DIR / "processed"
RAW_CSV = RAW_DIR / "sec_company_financials_raw.csv"
CLEAN_CSV = PROCESSED_DIR / "sec_company_financials_clean.csv"
WIDE_CSV = PROCESSED_DIR / "company_financials_wide.csv"
MARKET_RAW_CSV = MARKET_DATA_DIR / "sec_company_financials_raw.csv"
MARKET_CLEAN_CSV = MARKET_DATA_DIR / "sec_company_financials_clean.csv"
MARKET_WIDE_CSV = MARKET_PROCESSED_DIR / "company_financials_wide.csv"

OUTPUT_COLUMNS = [
    "Company",
    "Ticker",
    "CIK",
    "Statement",
    "Metric",
    "SEC_Tag",
    "Fiscal_Year",
    "Fiscal_Period",
    "Period_Start",
    "Period_End",
    "Filed_Date",
    "Form",
    "Accession_Number",
    "Unit",
    "Value",
    "Source",
]
WIDE_ID_COLUMNS = ["Company", "Ticker", "CIK", "Fiscal_Year"]

STATEMENT_LABEL = {
    "income": "Income Statement",
    "balance": "Balance Sheet",
    "cashflow": "Cash Flow Statement",
}

SEC_CONTACT_NAME = "Thomas Parkes"
SEC_CONTACT_EMAIL = "treyparkespa@gmail.com"
REQUEST_HEADERS = {
    "User-Agent": (
        f"Financial Performance Risk Analytics Portfolio "
        f"{SEC_CONTACT_NAME} {SEC_CONTACT_EMAIL}"
    ),
    "Accept-Encoding": "gzip, deflate",
}

USD = ["USD"]
EPS_UNITS = ["USD/shares", "USD-per-shares"]
SHARE_UNITS = ["shares", "pure"]

CORE_WARN_METRICS = {
    "Revenue": "Revenue",
    "Net_Income": "Net Income",
    "Total_Assets": "Total Assets",
    "Cash_Flow_from_Operating_Activities": "Operating Cash Flow",
}

# =============================================================================
# 3. Metric mapping
# =============================================================================
METRIC_MAP: dict[str, dict[str, Any]] = {
    "Revenue": {
        "statement": "income",
        "preferred_units": USD,
        "tags": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "SalesRevenueNet",
            "Revenues",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
        ],
    },
    "Cost_of_Revenue": {
        "statement": "income",
        "preferred_units": USD,
        "tags": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"],
    },
    "Gross_Profit": {
        "statement": "income",
        "preferred_units": USD,
        "tags": ["GrossProfit"],
    },
    "Research_and_Development": {
        "statement": "income",
        "preferred_units": USD,
        "tags": [
            "ResearchAndDevelopmentExpense",
            "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        ],
    },
    "Sales_and_Marketing": {
        "statement": "income",
        "preferred_units": USD,
        "tags": [
            "SellingAndMarketingExpense",
            "MarketingAndAdvertisingExpense",
            "SellingExpense",
        ],
    },
    "General_and_Administrative": {
        "statement": "income",
        "preferred_units": USD,
        "tags": ["GeneralAndAdministrativeExpense", "GeneralAndAdministrativeExpenses"],
    },
    "Operating_Expenses": {
        "statement": "income",
        "preferred_units": USD,
        "tags": ["OperatingExpenses", "OperatingCostsAndExpenses"],
    },
    "Operating_Income": {
        "statement": "income",
        "preferred_units": USD,
        "tags": ["OperatingIncomeLoss"],
    },
    "Interest_Income": {
        "statement": "income",
        "preferred_units": USD,
        "tags": [
            "InterestIncomeOperating",
            "InvestmentIncomeInterest",
            "InterestAndDividendIncomeOperating",
            "InterestAndOtherIncome",
        ],
    },
    "Interest_Expense": {
        "statement": "income",
        "preferred_units": USD,
        "tags": ["InterestExpense", "InterestExpenseDebt", "InterestExpenseNonoperating"],
    },
    "Other_Income_Expense": {
        "statement": "income",
        "preferred_units": USD,
        "tags": ["OtherNonoperatingIncomeExpense", "NonoperatingIncomeExpense", "OtherIncome"],
    },
    "Income_Before_Taxes": {
        "statement": "income",
        "preferred_units": USD,
        "tags": [
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
            "PretaxIncomeLoss",
        ],
    },
    "Income_Tax_Expense": {
        "statement": "income",
        "preferred_units": USD,
        "tags": ["IncomeTaxExpenseBenefit"],
    },
    "Net_Income": {
        "statement": "income",
        "preferred_units": USD,
        "tags": [
            "NetIncomeLoss",
            "ProfitLoss",
            "NetIncomeLossAvailableToCommonStockholdersBasic",
        ],
    },
    "Basic_EPS": {
        "statement": "income",
        "preferred_units": EPS_UNITS,
        "tags": ["EarningsPerShareBasic"],
    },
    "Diluted_EPS": {
        "statement": "income",
        "preferred_units": EPS_UNITS,
        "tags": ["EarningsPerShareDiluted"],
    },
    "Weighted_Average_Shares_Basic": {
        "statement": "income",
        "preferred_units": SHARE_UNITS,
        "tags": [
            "WeightedAverageNumberOfSharesOutstandingBasic",
            "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        ],
    },
    "Weighted_Average_Shares_Diluted": {
        "statement": "income",
        "preferred_units": SHARE_UNITS,
        "tags": [
            "WeightedAverageNumberOfDilutedSharesOutstanding",
            "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
        ],
    },
    "Cash_and_Cash_Equivalents": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["CashAndCashEquivalentsAtCarryingValue"],
    },
    "Short_Term_Investments": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": [
            "ShortTermInvestments",
            "MarketableSecuritiesCurrent",
            "AvailableForSaleSecuritiesCurrent",
            "DebtSecuritiesCurrent",
            "EquitySecuritiesFvNiCurrent",
        ],
    },
    "Accounts_Receivable": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["AccountsReceivableNetCurrent", "AccountsReceivableNet"],
    },
    "Inventory": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["InventoryNet"],
    },
    "Other_Current_Assets": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["OtherAssetsCurrent", "OtherCurrentAssets"],
    },
    "Total_Current_Assets": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["AssetsCurrent"],
    },
    "Property_Plant_and_Equipment_Net": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["PropertyPlantAndEquipmentNet"],
    },
    "Goodwill": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["Goodwill"],
    },
    "Intangible_Assets_Net": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["IntangibleAssetsNetExcludingGoodwill", "FiniteLivedIntangibleAssetsNet"],
    },
    "Other_Noncurrent_Assets": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["OtherAssetsNoncurrent", "OtherNoncurrentAssets"],
    },
    "Total_Assets": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["Assets"],
    },
    "Accounts_Payable": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["AccountsPayableCurrent"],
    },
    "Short_Term_Debt": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": [
            "DebtCurrent",
            "LongTermDebtAndCapitalLeaseObligationsCurrent",
            "LongTermDebtCurrent",
            "ShortTermBorrowings",
            "CommercialPaper",
        ],
    },
    "Other_Current_Liabilities": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["OtherLiabilitiesCurrent", "OtherCurrentLiabilities"],
    },
    "Total_Current_Liabilities": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["LiabilitiesCurrent"],
    },
    "Long_Term_Debt": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": [
            "LongTermDebtNoncurrent",
            "LongTermDebt",
            "LongTermDebtAndCapitalLeaseObligations",
        ],
    },
    "Other_Noncurrent_Liabilities": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["OtherLiabilitiesNoncurrent", "OtherNoncurrentLiabilities"],
    },
    "Total_Liabilities": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["Liabilities"],
    },
    "Common_Stock_and_APIC": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": [
            "CommonStocksIncludingAdditionalPaidInCapital",
            "AdditionalPaidInCapital",
            "CommonStockValue",
            "CommonStockValueOutstanding",
        ],
    },
    "Retained_Earnings": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["RetainedEarningsAccumulatedDeficit"],
    },
    "Total_Stockholders_Equity": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ],
    },
    "Total_Liabilities_and_Equity": {
        "statement": "balance",
        "preferred_units": USD,
        "tags": ["LiabilitiesAndStockholdersEquity"],
    },
    "CF_Net_Income": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["NetIncomeLoss", "ProfitLoss"],
    },
    "Depreciation_and_Amortization": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": [
            "DepreciationDepletionAndAmortization",
            "DepreciationAndAmortization",
            "DepreciationAmortizationAndAccretionNet",
        ],
    },
    "Stock_Based_Compensation": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
    },
    "Change_in_Working_Capital": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["IncreaseDecreaseInOperatingCapital", "IncreaseDecreaseInWorkingCapital"],
    },
    "Cash_Flow_from_Operating_Activities": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["NetCashProvidedByUsedInOperatingActivities"],
    },
    "Capital_Expenditures": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    },
    "Acquisitions": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": [
            "PaymentsToAcquireBusinessesNetOfCashAcquired",
            "PaymentsToAcquireBusinessesAndInterestInAffiliates",
        ],
    },
    "Purchases_of_Investments": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": [
            "PaymentsToAcquireMarketableSecurities",
            "PaymentsToAcquireAvailableForSaleSecuritiesDebt",
            "PaymentsToAcquireInvestments",
            "PaymentsToAcquireAvailableForSaleSecurities",
        ],
    },
    "Proceeds_from_Investments": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": [
            "ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities",
            "ProceedsFromSaleAndMaturityOfMarketableSecurities",
            "ProceedsFromSaleOfAvailableForSaleSecuritiesDebt",
            "ProceedsFromSaleOfAvailableForSaleSecurities",
        ],
    },
    "Cash_Flow_from_Investing_Activities": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["NetCashProvidedByUsedInInvestingActivities"],
    },
    "Debt_Issuance": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": [
            "ProceedsFromIssuanceOfLongTermDebt",
            "ProceedsFromIssuanceOfDebt",
            "ProceedsFromDebtNetOfIssuanceCosts",
        ],
    },
    "Debt_Repayment": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": [
            "RepaymentsOfLongTermDebt",
            "RepaymentsOfDebt",
            "RepaymentsOfLongTermDebtAndCapitalSecurities",
        ],
    },
    "Share_Repurchases": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["PaymentsForRepurchaseOfCommonStock"],
    },
    "Dividends_Paid": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
    },
    "Stock_Issuance": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["ProceedsFromIssuanceOfCommonStock", "ProceedsFromStockOptionsExercised"],
    },
    "Cash_Flow_from_Financing_Activities": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": ["NetCashProvidedByUsedInFinancingActivities"],
    },
    "Effect_of_Exchange_Rate": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": [
            "EffectOfExchangeRateOnCashAndCashEquivalents",
            "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        ],
    },
    "Net_Change_in_Cash": {
        "statement": "cashflow",
        "preferred_units": USD,
        "tags": [
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
            "CashAndCashEquivalentsPeriodIncreaseDecrease",
            "CashPeriodIncreaseDecrease",
        ],
    },
    "Ending_Cash": {
        "statement": "cashflow",
        "preferred_units": USD,
        "instant_as_cf": True,
        "tags": [
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            "CashAndCashEquivalentsAtCarryingValue",
        ],
    },
    "Beginning_Cash": {
        "statement": "cashflow",
        "preferred_units": USD,
        "instant_as_cf": True,
        "tags": [
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            "CashAndCashEquivalentsAtCarryingValue",
        ],
    },
}


def pad_cik(cik: str) -> str:
    return str(cik).strip().zfill(10)


def parse_date(value: Any) -> datetime | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d")
    except ValueError:
        return None


def format_date(value: datetime | None) -> str | None:
    return None if value is None else value.strftime("%Y-%m-%d")


def period_length_days(start: datetime | None, end: datetime | None) -> int | None:
    if start is None or end is None:
        return None
    return (end - start).days


def fiscal_year_from_end_date(end: datetime | None) -> int | None:
    return None if end is None else end.year


def choose_unit(units: dict[str, Any], preferred_units: list[str]) -> str | None:
    if not units:
        return None
    for unit in preferred_units:
        if unit in units:
            return unit
    for unit in units:
        if unit.replace("-per-", "/") in preferred_units or unit in preferred_units:
            return unit
    return None


def is_annual_form(form: Any) -> bool:
    return str(form).strip() in ALLOWED_FORMS


def is_annual_fiscal_period(fp: Any) -> bool:
    if fp is None or (isinstance(fp, float) and pd.isna(fp)):
        return True
    return str(fp).strip().upper() == "FY"


def user_agent_is_configured() -> bool:
    placeholder_name = SEC_CONTACT_NAME.strip() in {"", "YOUR NAME"}
    placeholder_email = (
        not SEC_CONTACT_EMAIL
        or "YOUR_EMAIL" in SEC_CONTACT_EMAIL
        or SEC_CONTACT_EMAIL.endswith("@example.com")
    )
    return not (placeholder_name or placeholder_email)


# =============================================================================
# 2. SEC request
# =============================================================================
def download_company_facts(cik: str) -> dict[str, Any] | None:
    padded = pad_cik(cik)
    url = f"{COMPANY_FACTS_BASE_URL}CIK{padded}.json"
    print(f"  GET {url}")
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.Timeout:
        print(f"  ERROR: timeout for CIK {padded}.")
        return None
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        print(f"  ERROR: HTTP {status} for CIK {padded}.")
        return None
    except (requests.exceptions.RequestException, ValueError) as exc:
        print(f"  ERROR: request/JSON failed for CIK {padded}: {exc}")
        return None
    if not isinstance(payload, dict) or "facts" not in payload:
        print(f"  ERROR: unexpected JSON for CIK {padded}.")
        return None
    return payload


def iter_taxonomies(facts_root: dict[str, Any]) -> list[str]:
    names = [PREFERRED_TAXONOMY] if PREFERRED_TAXONOMY in facts_root else []
    for name in facts_root:
        if name not in names and name not in SKIP_TAXONOMIES:
            names.append(name)
    return names


def fact_is_usable(fact: dict[str, Any], statement_type: str, instant_as_cf: bool) -> bool:
    if not is_annual_form(fact.get("form")) or not is_annual_fiscal_period(fact.get("fp")):
        return False
    if fact.get("val") is None:
        return False
    start = parse_date(fact.get("start"))
    end = parse_date(fact.get("end"))
    if end is None:
        return False
    if statement_type == "balance" or instant_as_cf:
        if start is not None and start != end:
            length = period_length_days(start, end)
            if length is not None and length > 1:
                return False
        return True
    length = period_length_days(start, end)
    return length is not None and ANNUAL_PERIOD_MIN_DAYS <= length <= ANNUAL_PERIOD_MAX_DAYS


def source_label(taxonomy: str) -> str:
    if taxonomy == "us-gaap":
        return "SEC Company Facts (us-gaap)"
    return f"SEC Company Facts ({taxonomy})"


def build_record(
    company_meta: dict[str, str],
    metric_name: str,
    statement_type: str,
    tag: str,
    taxonomy: str,
    unit_key: str,
    fact: dict[str, Any],
    fiscal_year: int | None,
    period_start: str | None,
    period_end: str | None,
) -> dict[str, Any]:
    return {
        "Company": company_meta["company"],
        "Ticker": company_meta["ticker"],
        "CIK": pad_cik(company_meta["cik"]),
        "Statement": STATEMENT_LABEL[statement_type],
        "Metric": metric_name,
        "SEC_Tag": tag,
        "Fiscal_Year": fiscal_year,
        "Fiscal_Period": fact.get("fp") or "FY",
        "Period_Start": period_start,
        "Period_End": period_end,
        "Filed_Date": fact.get("filed"),
        "Form": fact.get("form"),
        "Accession_Number": fact.get("accn"),
        "Unit": unit_key,
        "Value": fact.get("val"),
        "Source": source_label(taxonomy),
    }


# =============================================================================
# 4-5. XBRL extraction and annual fact selection
# =============================================================================
def extract_metric_records(
    company_meta: dict[str, str],
    facts_json: dict[str, Any],
    metric_name: str,
    metric_cfg: dict[str, Any],
) -> tuple[list[dict[str, Any]], str | None]:
    """
    For each fiscal year, use the first candidate tag that has a usable annual fact.
    Keep every 10-K observation for that tag/year (raw file); cleaning de-dupes later.

    Do not lock the whole company onto an old tag that only exists for earlier years
    (NVIDIA: ASC 606 revenue tag historically, us-gaap:Revenues in recent 10-Ks).
    """
    facts_root = facts_json.get("facts") or {}
    statement_type = metric_cfg["statement"]
    instant_as_cf = bool(metric_cfg.get("instant_as_cf"))
    observations: dict[tuple[str, int], list[dict[str, Any]]] = {}
    tag_order: list[str] = []

    for taxonomy in iter_taxonomies(facts_root):
        concepts = facts_root.get(taxonomy) or {}
        for tag in metric_cfg["tags"]:
            concept = concepts.get(tag)
            if not concept:
                continue
            unit_key = choose_unit(concept.get("units") or {}, metric_cfg["preferred_units"])
            if unit_key is None:
                continue
            if tag not in tag_order:
                tag_order.append(tag)
            for fact in concept["units"].get(unit_key) or []:
                if not fact_is_usable(fact, statement_type, instant_as_cf):
                    continue
                end = parse_date(fact.get("end"))
                start = parse_date(fact.get("start"))
                fy = fiscal_year_from_end_date(end)
                if fy is None:
                    continue
                if statement_type == "balance" or instant_as_cf:
                    period_start = None
                    period_end = format_date(end)
                else:
                    period_start = format_date(start)
                    period_end = format_date(end)
                observations.setdefault((tag, fy), []).append(
                    build_record(
                        company_meta,
                        metric_name,
                        statement_type,
                        tag,
                        taxonomy,
                        unit_key,
                        fact,
                        fy,
                        period_start,
                        period_end,
                    )
                )

    chosen_tag_by_year: dict[int, str] = {}
    for tag in tag_order:
        years = {fy for (t, fy) in observations if t == tag}
        for fy in years:
            chosen_tag_by_year.setdefault(fy, tag)

    records: list[dict[str, Any]] = []
    for fy, tag in chosen_tag_by_year.items():
        records.extend(observations.get((tag, fy), []))
    if not records:
        return [], None
    latest = max(chosen_tag_by_year)
    return records, chosen_tag_by_year.get(latest)


def extract_beginning_cash(
    company_meta: dict[str, str],
    facts_json: dict[str, Any],
    duration_records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Beginning cash is the instant cash fact on the annual CF period start date.
    Values are SEC facts, not computed from ending cash minus net change.
    """
    cfg = METRIC_MAP["Beginning_Cash"]
    anchors: dict[int, str] = {}
    for row in duration_records:
        if row["Statement"] != "Cash Flow Statement":
            continue
        if not row.get("Period_Start") or row.get("Fiscal_Year") is None:
            continue
        fy = int(row["Fiscal_Year"])
        anchors.setdefault(fy, str(row["Period_Start"]))
    if not anchors:
        return [], None

    facts_root = facts_json.get("facts") or {}
    out: list[dict[str, Any]] = []
    selected_tag: str | None = None
    used_years: set[int] = set()
    for taxonomy in iter_taxonomies(facts_root):
        concepts = facts_root.get(taxonomy) or {}
        for tag in cfg["tags"]:
            concept = concepts.get(tag)
            if not concept:
                continue
            unit_key = choose_unit(concept.get("units") or {}, cfg["preferred_units"])
            if unit_key is None:
                continue
            for fact in concept["units"].get(unit_key) or []:
                if not fact_is_usable(fact, "cashflow", True):
                    continue
                end = format_date(parse_date(fact.get("end")))
                for fy, period_start in anchors.items():
                    if fy in used_years or end != period_start:
                        continue
                    used_years.add(fy)
                    selected_tag = tag
                    out.append(
                        build_record(
                            company_meta,
                            "Beginning_Cash",
                            "cashflow",
                            tag,
                            taxonomy,
                            unit_key,
                            fact,
                            fy,
                            None,
                            end,
                        )
                    )
            if out:
                return out, selected_tag
    return out, selected_tag


def extract_company_records(
    company_meta: dict[str, str],
    facts_json: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, str | None]]:
    all_records: list[dict[str, Any]] = []
    selected: dict[str, str | None] = {}
    for metric_name, metric_cfg in METRIC_MAP.items():
        if metric_name == "Beginning_Cash":
            continue
        records, tag = extract_metric_records(company_meta, facts_json, metric_name, metric_cfg)
        selected[metric_name] = tag
        if tag is None:
            print(
                f"  WARNING: {company_meta['ticker']}: '{metric_name}' "
                "not found with usable annual 10-K facts."
            )
        all_records.extend(records)

    begin, begin_tag = extract_beginning_cash(company_meta, facts_json, all_records)
    selected["Beginning_Cash"] = begin_tag
    if begin_tag is None:
        print(
            f"  WARNING: {company_meta['ticker']}: 'Beginning_Cash' "
            "not found with usable annual 10-K facts."
        )
    all_records.extend(begin)
    return all_records, selected


def keep_fiscal_years_from(
    records: list[dict[str, Any]],
    min_year: int = MIN_FISCAL_YEAR,
) -> list[dict[str, Any]]:
    if not records:
        return records
    df = pd.DataFrame(records)
    fy = pd.to_numeric(df["Fiscal_Year"], errors="coerce")
    return df.loc[fy >= min_year].to_dict(orient="records")


# =============================================================================
# 7. Data cleaning
# =============================================================================
def resolve_duplicates(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    if raw_df.empty:
        return raw_df.copy(), 0
    ranked = raw_df.copy()
    ranked["_form_rank"] = ranked["Form"].map({"10-K": 0, "10-K/A": 1}).fillna(2)
    ranked["_has_fy"] = ranked["Fiscal_Year"].notna().astype(int)
    ranked["_has_end"] = ranked["Period_End"].notna().astype(int)
    ranked["_gaap"] = ranked["Source"].fillna("").str.contains("us-gaap").astype(int)
    ranked["_filed"] = pd.to_datetime(ranked["Filed_Date"], errors="coerce")
    ranked["Value"] = pd.to_numeric(ranked["Value"], errors="coerce")
    ranked = ranked.sort_values(
        by=[
            "Company",
            "Fiscal_Year",
            "Metric",
            "_form_rank",
            "_gaap",
            "_has_fy",
            "_has_end",
            "_filed",
        ],
        ascending=[True, True, True, True, False, False, False, False],
        kind="mergesort",
    )
    clean = ranked.drop_duplicates(subset=["Company", "Fiscal_Year", "Metric"], keep="first")
    n_removed = int(len(ranked) - len(clean))
    clean = clean.drop(columns=["_form_rank", "_has_fy", "_has_end", "_gaap", "_filed"])
    return clean[OUTPUT_COLUMNS].reset_index(drop=True), n_removed


# =============================================================================
# 8. Wide table
# =============================================================================
def to_wide_format(clean_df: pd.DataFrame) -> pd.DataFrame:
    if clean_df.empty:
        return pd.DataFrame(columns=WIDE_ID_COLUMNS)
    pivoted = clean_df.pivot_table(
        index=WIDE_ID_COLUMNS,
        columns="Metric",
        values="Value",
        aggfunc="first",
    ).reset_index()
    pivoted.columns.name = None
    metric_cols = [c for c in pivoted.columns if c not in WIDE_ID_COLUMNS]
    nonempty = [c for c in metric_cols if pivoted[c].notna().any()]
    return (
        pivoted[WIDE_ID_COLUMNS + nonempty]
        .sort_values(["Company", "Fiscal_Year"])
        .reset_index(drop=True)
    )


# =============================================================================
# 9. Validation
# =============================================================================
def lookup(wide: pd.DataFrame, company: str, year: int, metric: str) -> float | None:
    if metric not in wide.columns:
        return None
    hit = wide.loc[(wide["Company"] == company) & (wide["Fiscal_Year"] == year), metric]
    if hit.empty or pd.isna(hit.iloc[0]):
        return None
    return float(hit.iloc[0])


def approx_equal(left: float, right: float) -> bool:
    scale = max(abs(left), abs(right), 1.0)
    return abs(left - right) <= max(1_000_000.0, 0.02 * scale)


def print_accounting_checks(wide: pd.DataFrame) -> None:
    print("\nAccounting identity checks (warnings only; values not changed):")
    if wide.empty:
        print("  (skipped)")
        return
    any_warn = False
    for _, row in wide.iterrows():
        company = str(row["Company"])
        year = int(row["Fiscal_Year"])
        rev = lookup(wide, company, year, "Revenue")
        cor = lookup(wide, company, year, "Cost_of_Revenue")
        gp = lookup(wide, company, year, "Gross_Profit")
        if rev is not None and cor is not None and gp is not None and not approx_equal(gp, rev - cor):
            print(f"  WARNING: {company} FY{year}: Gross Profit vs Revenue - COGS differs beyond tolerance.")
            any_warn = True
        assets = lookup(wide, company, year, "Total_Assets")
        liab = lookup(wide, company, year, "Total_Liabilities")
        equity = lookup(wide, company, year, "Total_Stockholders_Equity")
        if (
            assets is not None
            and liab is not None
            and equity is not None
            and not approx_equal(assets, liab + equity)
        ):
            print(f"  WARNING: {company} FY{year}: Assets vs Liabilities + Equity differs beyond tolerance.")
            any_warn = True
        begin = lookup(wide, company, year, "Beginning_Cash")
        change = lookup(wide, company, year, "Net_Change_in_Cash")
        end = lookup(wide, company, year, "Ending_Cash")
        if (
            begin is not None
            and change is not None
            and end is not None
            and not approx_equal(begin + change, end)
        ):
            print(
                f"  WARNING: {company} FY{year}: Beginning cash + net change vs ending cash "
                "differs beyond tolerance."
            )
            any_warn = True
    if not any_warn:
        print("  No material identity breaks detected (or components missing).")


def print_quality_report(
    download_status: dict[str, bool],
    raw_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    wide_df: pd.DataFrame,
    n_removed: int,
    tags_by_company: dict[str, dict[str, str | None]],
) -> None:
    print("\n" + "=" * 72)
    print("DATA QUALITY SUMMARY")
    print("=" * 72)
    print(f"\nCompanies downloaded: {sum(download_status.values())} / {len(COMPANIES)}")
    all_metrics = list(METRIC_MAP.keys())

    print(f"\n1. Records extracted per company (raw, FY{MIN_FISCAL_YEAR}+):")
    if raw_df.empty:
        print("   (none)")
    else:
        for (name, ticker), n in raw_df.groupby(["Company", "Ticker"]).size().items():
            print(f"   - {name} ({ticker}): {n}")

    print("\n2-3. Metrics found by statement (clean unique metric names):")
    print(f"\n{'Company':<14} | {'Income':>7} | {'Balance':>8} | {'CashFlow':>8} | {'Total':>5}")
    print("-" * 56)
    missing_by_company: dict[str, list[str]] = {}
    for company in COMPANIES:
        ticker = company["ticker"]
        subset = clean_df.loc[clean_df["Ticker"] == ticker] if not clean_df.empty else clean_df
        found = set(subset["Metric"].unique()) if not subset.empty else set()
        missing_by_company[ticker] = [m for m in all_metrics if m not in found]
        n_is = len([m for m in found if METRIC_MAP[m]["statement"] == "income"])
        n_bs = len([m for m in found if METRIC_MAP[m]["statement"] == "balance"])
        n_cf = len([m for m in found if METRIC_MAP[m]["statement"] == "cashflow"])
        print(f"{company['company']:<14} | {n_is:7d} | {n_bs:8d} | {n_cf:8d} | {len(found):5d}")
        used = {m: t for m, t in tags_by_company.get(ticker, {}).items() if t}
        if used:
            print("     tags used:")
            for metric, tag in used.items():
                print(f"       {metric}: {tag}")

    print("\n4. Missing standardized metrics by company:")
    for company in COMPANIES:
        missing = missing_by_company.get(company["ticker"], all_metrics)
        print(f"   - {company['company']}: {', '.join(missing) if missing else 'none'}")
        for key, label in CORE_WARN_METRICS.items():
            if key in missing:
                print(f"     WARNING: {label} is missing.")

    print(f"\n5. Duplicate records removed (raw -> clean): {n_removed}")
    print("\n6. Fiscal years (clean):")
    if clean_df.empty:
        print("   (none)")
    else:
        for company in COMPANIES:
            sub = clean_df.loc[clean_df["Ticker"] == company["ticker"]]
            years = sorted(sub["Fiscal_Year"].dropna().unique().tolist()) if not sub.empty else []
            print(
                f"   - {company['company']}: "
                f"{', '.join(str(int(y)) for y in years) if years else 'none'}"
            )

    dups = (
        int(clean_df.duplicated(subset=["Company", "Fiscal_Year", "Metric"]).sum())
        if not clean_df.empty
        else 0
    )
    print(f"\n7. Duplicate Company+FY+Metric in clean: {dups}")
    print(f"   Rows: raw={len(raw_df)} clean={len(clean_df)} wide={len(wide_df)}")
    print_accounting_checks(wide_df)
    print("=" * 72)


# =============================================================================
# 10-11. Export and main
# =============================================================================
def main() -> int:
    print("SEC EDGAR Company Facts extractor")
    print("Official API:", COMPANY_FACTS_BASE_URL)
    if not user_agent_is_configured():
        print("STOPPED: set SEC_CONTACT_NAME and SEC_CONTACT_EMAIL.")
        return 1

    download_status: dict[str, bool] = {}
    tags_by_company: dict[str, dict[str, str | None]] = {}
    extracted: list[dict[str, Any]] = []

    for i, company in enumerate(COMPANIES):
        ticker = company["ticker"]
        print(f"[{i + 1}/{len(COMPANIES)}] {company['company']} ({ticker})")
        payload = download_company_facts(company["cik"])
        download_status[ticker] = payload is not None
        if payload is not None:
            records, selected = extract_company_records(company, payload)
            tags_by_company[ticker] = selected
            extracted.extend(records)
            print(f"  Extracted {len(records)} annual candidate records.")
        else:
            tags_by_company[ticker] = {m: None for m in METRIC_MAP}
        if i < len(COMPANIES) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    extracted = keep_fiscal_years_from(extracted)
    raw_df = pd.DataFrame(extracted, columns=OUTPUT_COLUMNS)
    if not raw_df.empty:
        raw_df = raw_df.sort_values(
            ["Company", "Fiscal_Year", "Metric", "Filed_Date"],
            kind="mergesort",
        ).reset_index(drop=True)

    clean_df, n_removed = resolve_duplicates(raw_df)
    wide_df = to_wide_format(clean_df)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MARKET_DATA_DIR.mkdir(parents=True, exist_ok=True)
    MARKET_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    destinations = [
        (raw_df, RAW_CSV),
        (clean_df, CLEAN_CSV),
        (clean_df, RAW_DIR / "sec_company_financials_clean.csv"),
        (wide_df, WIDE_CSV),
        (raw_df, MARKET_RAW_CSV),
        (clean_df, MARKET_CLEAN_CSV),
        (wide_df, MARKET_WIDE_CSV),
    ]
    for frame, path in destinations:
        frame.to_csv(path, index=False)
        print(f"Wrote {path} ({len(frame)} rows)")
    print_quality_report(download_status, raw_df, clean_df, wide_df, n_removed, tags_by_company)
    return 0


if __name__ == "__main__":
    sys.exit(main())
