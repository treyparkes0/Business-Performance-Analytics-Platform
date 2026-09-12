"""
Stock market data cleaning
==========================
Reads the Twelve Data raw CSV (no new API calls) and produces cleaned
long and wide files the same way the SEC extractor produces clean + wide
outputs.

Does not fill missing trading days or invent prices.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


# -----------------------------------------------------------------------------
# 1–2. Paths
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "stock_market_data_raw.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CLEAN_CSV = PROCESSED_DIR / "stock_market_data_clean.csv"
WIDE_CSV = PROCESSED_DIR / "stock_prices_wide.csv"

LONG_COLUMNS = ["Date", "Company", "Ticker", "Open", "High", "Low", "Close", "Volume", "Daily_Return"]
PRICE_COLS = ["Open", "High", "Low", "Close"]


def load_raw(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"STOPPED: Raw file not found:\n  {path}")
        print("Run src/stock_data_extraction.py first.")
        sys.exit(1)
    return pd.read_csv(path)


def clean_stock_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Parallel to SEC duplicate resolution:
      one final row per Ticker + Date.
    """
    stats = {
        "raw_rows": int(len(raw)),
        "dropped_missing_key": 0,
        "dropped_nonpositive_price": 0,
        "dropped_ohlc_inconsistent": 0,
        "dropped_negative_volume": 0,
        "duplicates_removed": 0,
    }

    df = raw.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in PRICE_COLS + ["Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()
    df["Company"] = df["Company"].astype(str).str.strip()

    before = len(df)
    df = df.loc[df["Date"].notna() & df["Ticker"].ne("") & df["Ticker"].ne("NAN")].copy()
    stats["dropped_missing_key"] = int(before - len(df))

    before = len(df)
    price_ok = (df[PRICE_COLS] > 0).all(axis=1)
    df = df.loc[price_ok].copy()
    stats["dropped_nonpositive_price"] = int(before - len(df))

    before = len(df)
    ohlc_ok = (
        (df["High"] >= df["Low"])
        & (df["High"] >= df["Open"])
        & (df["High"] >= df["Close"])
        & (df["Low"] <= df["Open"])
        & (df["Low"] <= df["Close"])
    )
    df = df.loc[ohlc_ok].copy()
    stats["dropped_ohlc_inconsistent"] = int(before - len(df))

    before = len(df)
    df = df.loc[df["Volume"].fillna(-1) >= 0].copy()
    stats["dropped_negative_volume"] = int(before - len(df))

    before = len(df)
    df = df.sort_values(["Ticker", "Date"], kind="mergesort")
    df = df.drop_duplicates(subset=["Ticker", "Date"], keep="last")
    stats["duplicates_removed"] = int(before - len(df))

    df = df.sort_values(["Ticker", "Date"], kind="mergesort").reset_index(drop=True)
    df["Daily_Return"] = df.groupby("Ticker")["Close"].pct_change()

    return df[LONG_COLUMNS], stats


def to_wide_close(clean: pd.DataFrame) -> pd.DataFrame:
    """One row per trading date; closing prices as ticker columns."""
    if clean.empty:
        return pd.DataFrame(columns=["Date"])
    wide = clean.pivot_table(index="Date", columns="Ticker", values="Close", aggfunc="first")
    wide = wide.sort_index().reset_index()
    wide.columns.name = None
    return wide


def print_quality_report(clean: pd.DataFrame, wide: pd.DataFrame, stats: dict[str, int]) -> None:
    print("\n" + "=" * 72)
    print("STOCK CLEANING SUMMARY")
    print("=" * 72)
    print(f"Raw rows: {stats['raw_rows']}")
    print(f"Dropped missing Date/Ticker: {stats['dropped_missing_key']}")
    print(f"Dropped non-positive prices: {stats['dropped_nonpositive_price']}")
    print(f"Dropped inconsistent OHLC: {stats['dropped_ohlc_inconsistent']}")
    print(f"Dropped negative volume: {stats['dropped_negative_volume']}")
    print(f"Duplicate Ticker+Date rows removed: {stats['duplicates_removed']}")
    print(f"Clean rows: {len(clean)}")
    print(f"Wide rows (one per date): {len(wide)}")

    print("\nRecords and date range by company:")
    if clean.empty:
        print("  (no rows)")
        print("=" * 72)
        return

    for ticker, group in clean.groupby("Ticker", sort=True):
        company = group["Company"].iloc[0]
        print(
            f"  {company} ({ticker}): {len(group)} days | "
            f"{group['Date'].min().date()} -> {group['Date'].max().date()}"
        )

    dups = int(clean.duplicated(subset=["Ticker", "Date"]).sum())
    missing_close = int(clean["Close"].isna().sum())
    print(f"\nDuplicate Ticker+Date in clean file: {dups}")
    print(f"Missing Close values: {missing_close}")
    print("Daily_Return is Close-to-Close percent change (first day per ticker is blank).")
    print("Missing trading days are left missing; they are not filled.")
    print("=" * 72)


def main() -> int:
    print("Stock data cleaning (local CSV only; no API requests)")
    raw = load_raw(RAW_CSV)
    clean, stats = clean_stock_data(raw)
    wide = to_wide_close(clean)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN_CSV, index=False)
    wide.to_csv(WIDE_CSV, index=False)
    print(f"Wrote {CLEAN_CSV} ({len(clean)} rows)")
    print(f"Wrote {WIDE_CSV} ({len(wide)} rows)")

    print_quality_report(clean, wide, stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
