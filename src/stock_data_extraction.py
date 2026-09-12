"""
Twelve Data daily OHLCV extractor
=================================
Downloads ~3 years of daily bars for a small set of US stocks from the
official Twelve Data time_series API. The API key is loaded from a local
.env file and is never printed or written to disk.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# -----------------------------------------------------------------------------
# 2. Project path configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_PATH = PROJECT_ROOT / ".env"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_CSV = RAW_DATA_DIR / "stock_market_data_raw.csv"

OUTPUT_COLUMNS = ["Date", "Company", "Ticker", "Open", "High", "Low", "Close", "Volume"]


# -----------------------------------------------------------------------------
# 3–4. Environment variable loading and API key validation
# -----------------------------------------------------------------------------
load_dotenv(dotenv_path=ENV_PATH)

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "").strip()

TIME_SERIES_URL = "https://api.twelvedata.com/time_series"
REQUEST_TIMEOUT_SECONDS = 30
# Basic plans are often ~8 credits/minute. One time_series call = 1 credit.
# 8+ seconds between 6 symbols stays under that ceiling.
REQUEST_DELAY_SECONDS = 8.0
MAX_RATE_LIMIT_RETRIES = 3
RATE_LIMIT_WAIT_SECONDS = 15.0


def require_api_key() -> str:
    if not TWELVE_DATA_API_KEY:
        print(
            "STOPPED: TWELVE_DATA_API_KEY is missing.\n"
            f"Create or edit {ENV_PATH} with:\n"
            "  TWELVE_DATA_API_KEY=your_key_here\n"
            "Do not put the key in this Python file."
        )
        sys.exit(1)
    if TWELVE_DATA_API_KEY.upper() in {"YOUR_KEY", "YOUR_API_KEY", "MY_ACTUAL_API_KEY"}:
        print("STOPPED: Replace the placeholder in .env with your real Twelve Data key.")
        sys.exit(1)
    return TWELVE_DATA_API_KEY


# -----------------------------------------------------------------------------
# 5. Company configuration
# -----------------------------------------------------------------------------
COMPANIES: dict[str, str] = {
    "MSFT": "Microsoft",
    "AAPL": "Apple",
    "NVDA": "NVIDIA",
    "ADBE": "Adobe",
    "AMD": "AMD",
    "CRWD": "CrowdStrike",
}


# -----------------------------------------------------------------------------
# 6. Date configuration
# -----------------------------------------------------------------------------
START_DATE = date(2023, 9, 2)


def end_date_for_request() -> date:
    """Calendar today. The API returns the last available trading day."""
    return date.today()


# -----------------------------------------------------------------------------
# 7. API request function
# -----------------------------------------------------------------------------
def fetch_daily_time_series(ticker: str, api_key: str, start: date, end: date) -> list[dict]:
    """
    One official /time_series request for a single symbol.
    Does not scrape websites. Does not invent bars.
    """
    headers = {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json",
    }
    params = {
        "symbol": ticker,
        "interval": "1day",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "order": "asc",
        "format": "JSON",
        "country": "United States",
    }

    last_error: Exception | None = None
    for attempt in range(1, MAX_RATE_LIMIT_RETRIES + 1):
        try:
            response = requests.get(
                TIME_SERIES_URL,
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            if response.status_code == 429:
                print(
                    f"  WARNING: {ticker}: HTTP 429 rate limit "
                    f"(attempt {attempt}/{MAX_RATE_LIMIT_RETRIES}). Waiting."
                )
                time.sleep(RATE_LIMIT_WAIT_SECONDS * attempt)
                continue
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print(f"  ERROR: {ticker}: request timed out after {REQUEST_TIMEOUT_SECONDS}s.")
            return []
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            print(f"  ERROR: {ticker}: HTTP {status}.")
            return []
        except requests.exceptions.RequestException as exc:
            last_error = exc
            print(f"  ERROR: {ticker}: network error: {exc}")
            return []

        try:
            payload = response.json()
        except ValueError:
            print(f"  ERROR: {ticker}: response was not valid JSON.")
            return []

        if not isinstance(payload, dict):
            print(f"  ERROR: {ticker}: unexpected JSON type.")
            return []

        status = str(payload.get("status", "")).lower()
        if status == "error" or payload.get("code") in {400, 401, 403, 404, 414, 429, 500}:
            code = payload.get("code")
            message = payload.get("message", "No message from API.")
            if code == 429 or "run out of API credits" in str(message).lower():
                print(
                    f"  WARNING: {ticker}: API credit/rate limit "
                    f"(attempt {attempt}/{MAX_RATE_LIMIT_RETRIES}). Waiting."
                )
                time.sleep(RATE_LIMIT_WAIT_SECONDS * attempt)
                continue
            print(f"  ERROR: {ticker}: API error {code}: {message}")
            return []

        values = payload.get("values")
        if not values:
            print(f"  WARNING: {ticker}: empty time series (no values).")
            return []
        if not isinstance(values, list):
            print(f"  ERROR: {ticker}: 'values' was not a list.")
            return []
        return values

    print(f"  ERROR: {ticker}: exceeded rate-limit retries. {last_error or ''}".strip())
    return []


# -----------------------------------------------------------------------------
# 8. Data cleaning function
# -----------------------------------------------------------------------------
def values_to_frame(ticker: str, company: str, values: list[dict]) -> pd.DataFrame:
    if not values:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    frame = pd.DataFrame(values)
    if "datetime" not in frame.columns:
        print(f"  WARNING: {ticker}: API rows missing datetime. Skipping.")
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    frame["Date"] = pd.to_datetime(frame["datetime"], errors="coerce")
    frame["Company"] = company
    frame["Ticker"] = ticker

    for col in ["open", "high", "low", "close"]:
        if col not in frame.columns:
            frame[col] = pd.NA
    if "volume" not in frame.columns:
        frame["volume"] = pd.NA

    frame["Open"] = pd.to_numeric(frame["open"], errors="coerce")
    frame["High"] = pd.to_numeric(frame["high"], errors="coerce")
    frame["Low"] = pd.to_numeric(frame["low"], errors="coerce")
    frame["Close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame["Volume"] = pd.to_numeric(frame["volume"], errors="coerce")

    frame = frame.loc[frame["Date"].notna()].copy()
    frame["Date"] = frame["Date"].dt.normalize()

    start_ts = pd.Timestamp(START_DATE)
    frame = frame.loc[frame["Date"] >= start_ts].copy()

    frame = frame[OUTPUT_COLUMNS]
    frame = frame.drop_duplicates(subset=["Ticker", "Date"], keep="last")
    frame = frame.sort_values(["Ticker", "Date"], kind="mergesort").reset_index(drop=True)
    return frame


# -----------------------------------------------------------------------------
# 9. Validation function
# -----------------------------------------------------------------------------
def validate_company_data(ticker: str, frame: pd.DataFrame) -> None:
    if frame.empty:
        print(f"  WARNING: {ticker}: no usable rows after cleaning.")
        return
    min_date = frame["Date"].min().date()
    max_date = frame["Date"].max().date()
    print(f"  {ticker}: {len(frame)} trading days | {min_date} → {max_date}")


# -----------------------------------------------------------------------------
# 10–12. Combined dataset, CSV export, summary
# -----------------------------------------------------------------------------
def export_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    print(f"\nWrote {path} ({len(frame)} rows)")


def print_summary(frames: dict[str, pd.DataFrame], combined: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("STOCK DATA SUMMARY")
    print("=" * 72)
    print(f"Requested start: {START_DATE.isoformat()}")
    print(f"Requested end (calendar today): {end_date_for_request().isoformat()}")
    print("API returns the last available trading day if today is a weekend/holiday.\n")

    for ticker, company in COMPANIES.items():
        frame = frames.get(ticker, pd.DataFrame(columns=OUTPUT_COLUMNS))
        if frame.empty:
            print(f"  {company} ({ticker}): NO DATA")
            continue
        print(
            f"  {company} ({ticker}): {len(frame)} records | "
            f"{frame['Date'].min().date()} → {frame['Date'].max().date()}"
        )

    if combined.empty:
        print("\nCombined dataset is empty. No CSV rows were fabricated.")
        return

    dup = combined.duplicated(subset=["Ticker", "Date"]).sum()
    print(f"\nCombined rows: {len(combined)}")
    print(f"Duplicate Ticker+Date rows after cleanup: {int(dup)}")
    print("=" * 72)


def main() -> int:
    print("Twelve Data daily OHLCV extractor")
    print("Official endpoint:", TIME_SERIES_URL)
    print("Key source: local .env (value is not printed)\n")

    api_key = require_api_key()
    start = START_DATE
    end = end_date_for_request()
    if end < start:
        print("STOPPED: end date is before start date.")
        return 1

    frames: dict[str, pd.DataFrame] = {}
    tickers = list(COMPANIES.keys())

    for i, ticker in enumerate(tickers):
        company = COMPANIES[ticker]
        print(f"[{i + 1}/{len(tickers)}] {company} ({ticker})")
        values = fetch_daily_time_series(ticker, api_key, start, end)
        frame = values_to_frame(ticker, company, values)
        validate_company_data(ticker, frame)
        frames[ticker] = frame
        if i < len(tickers) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    nonempty = [f for f in frames.values() if not f.empty]
    combined = (
        pd.concat(nonempty, ignore_index=True)
        if nonempty
        else pd.DataFrame(columns=OUTPUT_COLUMNS)
    )
    if not combined.empty:
        combined = combined.drop_duplicates(subset=["Ticker", "Date"], keep="last")
        combined = combined.sort_values(["Ticker", "Date"], kind="mergesort").reset_index(drop=True)
        combined = combined[OUTPUT_COLUMNS]

    export_csv(combined, OUTPUT_CSV)
    print_summary(frames, combined)
    return 0


if __name__ == "__main__":
    sys.exit(main())
