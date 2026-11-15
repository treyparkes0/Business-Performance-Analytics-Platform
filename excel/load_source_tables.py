"""Export the six analytics frames to CSV and load them into the workbook.

Excel has no Databricks connector on this machine. The frames come from
src.bp_metrics.build_views, which repeats the SQL views. Nulls stay blank.
Power Query reads excel/source. The forecast is built by _write_phase4.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "excel"))

from build_phase3_foundation import build  # noqa: E402
from src.bp_metrics import (  # noqa: E402
    BOOL_COLUMNS,
    INT_COLUMNS,
    _is_rank_column,
    build_views,
)
from src.interpretations import ALERTS, CONCLUSION, EXECUTIVE, PEER  # noqa: E402

SOURCE_DIR = ROOT / "excel" / "source"
WORKBOOK = ROOT / "excel" / "Business_Performance_Analysis.xlsx"

EXPORTS = (
    ("growth_trend", "growth_trend.csv", "src_GrowthTrend", "tblGrowthTrend", 33),
    ("performance", "performance.csv", "src_Performance", "tblPerformance", 33),
    ("financial_health", "financial_health.csv", "src_FinancialHealth", "tblFinancialHealth", 33),
    ("peer_benchmarking", "peer_benchmarking.csv", "src_PeerBenchmarking", "tblPeerBenchmarking", 6),
    ("executive_summary", "executive_summary.csv", "src_ExecutiveSummary", "tblExecutiveSummary", 6),
    ("peer_metrics", "peer_metrics.csv", "src_PeerMetrics", "tblPeerMetrics", 33),
)

DOLLAR_COLUMNS = {
    "Revenue",
    "Net_Income",
    "Gross_Profit",
    "Operating_Income",
    "Operating_Expenses",
    "Cash_Flow_from_Operating_Activities",
    "Capital_Expenditures",
    "Free_Cash_Flow",
    "Total_Assets",
    "Total_Liabilities",
    "Total_Stockholders_Equity",
    "Total_Current_Assets",
    "Total_Current_Liabilities",
    "Total_Debt",
}
MULTIPLE_COLUMNS = {
    "Current_ratio",
    "Cash_Conversion_Ratio",
    "Average_Rank",
    "FY2025_Average_Rank",
}
COMPANIES = {"Microsoft", "Apple", "NVIDIA", "Adobe", "AMD", "CrowdStrike"}

NAVY = "0E2A47"
WHITE = "FFFFFF"
THIN = Border(
    left=Side(style="thin", color="D5DDE5"),
    right=Side(style="thin", color="D5DDE5"),
    top=Side(style="thin", color="D5DDE5"),
    bottom=Side(style="thin", color="D5DDE5"),
)


def _missing(value) -> bool:
    return value is None or pd.isna(value)


def csv_field(column: str, value) -> str:
    if _missing(value):
        return ""
    if column in BOOL_COLUMNS:
        return "TRUE" if bool(value) else "FALSE"
    if column in INT_COLUMNS or _is_rank_column(column):
        return str(int(value))
    if column == "Company":
        return str(value)
    number = float(value)
    if column in DOLLAR_COLUMNS:
        return str(int(round(number)))
    text = f"{number:.10f}".rstrip("0").rstrip(".")
    return text if text not in {"", "-0"} else "0"


def cell_value(column: str, value):
    if _missing(value):
        return None
    if column in BOOL_COLUMNS:
        return bool(value)
    if column in INT_COLUMNS or _is_rank_column(column):
        return int(value)
    if column == "Company":
        return str(value)
    return float(value)


def number_format(column: str) -> str | None:
    if column in DOLLAR_COLUMNS:
        return "#,##0"
    if column in MULTIPLE_COLUMNS:
        return "0.000"
    if column in INT_COLUMNS or _is_rank_column(column):
        return "0"
    if column in BOOL_COLUMNS or column == "Company":
        return None
    return "0.0%"


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(list(frame.columns))
        for record in frame.itertuples(index=False):
            writer.writerow(
                [csv_field(column, value) for column, value in zip(frame.columns, record, strict=True)]
            )


def add_source_sheet(workbook, frame: pd.DataFrame, sheet_name: str, table_name: str) -> None:
    worksheet = workbook.create_sheet(sheet_name)
    worksheet.sheet_properties.tabColor = "5E6B75"
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = None
    worksheet.page_setup.orientation = "landscape"
    worksheet.page_setup.fitToWidth = 1
    worksheet.page_setup.fitToHeight = 0
    worksheet.sheet_properties.pageSetUpPr.fitToPage = True
    worksheet.page_setup.paperSize = worksheet.PAPERSIZE_TABLOID
    worksheet.oddFooter.left.text = "Business Performance Analysis"
    worksheet.oddFooter.right.text = table_name
    headers = list(frame.columns) + ["Key"]
    for col_index, header in enumerate(headers, start=1):
        cell = worksheet.cell(1, col_index, header)
        cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = THIN
        worksheet.column_dimensions[get_column_letter(col_index)].width = min(max(len(header) + 2, 14), 36)
    worksheet.row_dimensions[1].height = 30
    for row_index, record in enumerate(frame.itertuples(index=False), start=2):
        worksheet.row_dimensions[row_index].height = 18
        for col_index, (column, value) in enumerate(zip(frame.columns, record, strict=True), start=1):
            cell = worksheet.cell(row_index, col_index, cell_value(column, value))
            cell.font = Font(name="Calibri", size=10, color="1C2833")
            cell.alignment = Alignment(vertical="center")
            cell.border = THIN
            fmt = number_format(column)
            if fmt:
                cell.number_format = fmt
        key_cell = worksheet.cell(row_index, len(headers), f'=A{row_index}&"|"&TEXT(B{row_index},"0")')
        key_cell.font = Font(name="Calibri", size=10, color="1C2833")
        key_cell.alignment = Alignment(vertical="center")
        key_cell.border = THIN
    last_column = get_column_letter(len(headers))
    last_row = len(frame) + 1
    table = Table(displayName=table_name, ref=f"A1:{last_column}{last_row}")
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True, showColumnStripes=False)
    worksheet.add_table(table)


INK = "1C2833"
SECTION = "E6EEF5"
GOLD = "C4A35A"
CREAM = "FFF8E8"
WHITE_FILL = PatternFill("solid", fgColor="FFFFFF")
SECTION_FILL = PatternFill("solid", fgColor=SECTION)
HEADER_FILL = PatternFill("solid", fgColor=NAVY)
INPUT_FILL = PatternFill("solid", fgColor=CREAM)
LABEL_FONT = Font(name="Calibri", size=11, bold=True, color=NAVY)
BODY = Font(name="Calibri", size=11, color=INK)
HEADER_FONT = Font(name="Calibri", size=10, bold=True, color=WHITE)
SECTION_FONT = Font(name="Calibri", size=13, bold=True, color=NAVY)
YEARS = (2021, 2022, 2023, 2024, 2025, 2026)
COMPANY_ORDER = ["Microsoft", "Apple", "NVIDIA", "Adobe", "AMD", "CrowdStrike"]


def _kept(expression: str) -> str:
    """Blank stays blank. A real zero stays zero. XLOOKUP turns a blank into 0, so the check stays."""
    return f'LET(x,{expression},IF(x="","",x))'


def _lookup(table: str, column: str, key_expr: str) -> str:
    return _kept(f'XLOOKUP({key_expr},{table}[Key],{table}[{column}],"")')


def _lookup_company(table: str, column: str) -> str:
    return _kept(f'XLOOKUP(Selected_Company,{table}[Company],{table}[{column}],"")')


def _peer(column: str, row_number: int) -> str:
    return _kept(f"INDEX(tblPeerBenchmarking[{column}],{row_number})")


def _reset_body(worksheet, last_col: int = 14) -> None:
    for merged in list(worksheet.merged_cells.ranges):
        if merged.min_row >= 5:
            worksheet.unmerge_cells(str(merged))
    last_row = max(worksheet.max_row, 5)
    last_used = max(worksheet.max_column, last_col)
    for row in worksheet.iter_rows(min_row=5, max_row=last_row, max_col=last_used):
        for cell in row:
            cell.value = None
            cell.fill = WHITE_FILL
            cell.font = BODY
            cell.border = Border()
            cell.alignment = Alignment(vertical="center", indent=1)
            cell.number_format = "General"
    worksheet.freeze_panes = "A8"
    for col in range(1, last_col + 1):
        worksheet.column_dimensions[get_column_letter(col)].width = 18
    worksheet.column_dimensions["A"].width = 32


def _section(worksheet, row: int, title: str, width: int) -> int:
    worksheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=width)
    worksheet.row_dimensions[row].height = 24
    for col in range(1, width + 1):
        cell = worksheet.cell(row, col, title if col == 1 else None)
        cell.font = SECTION_FONT
        cell.fill = SECTION_FILL
        cell.alignment = Alignment(vertical="center", indent=1)
        cell.border = Border(bottom=Side(style="thin", color=GOLD))
    return row + 1


def _headers(worksheet, row: int, labels: list[str]) -> int:
    worksheet.row_dimensions[row].height = 22
    for col, label in enumerate(labels, start=1):
        cell = worksheet.cell(row, col, label)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        cell.border = THIN
    return row + 1


def _year_block(worksheet, row: int, title: str, table: str, columns: list[tuple[str, str, str | None]]) -> int:
    width = len(columns) + 1
    row = _section(worksheet, row, title, width)
    row = _headers(worksheet, row, ["Fiscal year", *[label for label, _field, _fmt in columns]])
    for year in YEARS:
        worksheet.row_dimensions[row].height = 18
        year_cell = worksheet.cell(row, 1, year)
        year_cell.font = BODY
        year_cell.number_format = "0"
        year_cell.border = THIN
        year_cell.alignment = Alignment(vertical="center", indent=1)
        key = f'Selected_Company&"|"&A{row}'
        for col, (_label, field, fmt) in enumerate(columns, start=2):
            cell = worksheet.cell(row, col, "=" + _lookup(table, field, key))
            cell.font = BODY
            cell.border = THIN
            cell.alignment = Alignment(vertical="center")
            if fmt:
                cell.number_format = fmt
        row += 1
    return row + 1


def _metric_list(worksheet, row: int, title: str, table: str, columns: list[tuple[str, str, str | None]]) -> int:
    row = _section(worksheet, row, title, 2)
    row = _headers(worksheet, row, ["Metric", "Value"])
    for label, field, fmt in columns:
        worksheet.row_dimensions[row].height = 18
        label_cell = worksheet.cell(row, 1, label)
        label_cell.font = BODY
        label_cell.border = THIN
        value = worksheet.cell(row, 2, "=" + _lookup_company(table, field))
        value.font = BODY
        value.border = THIN
        value.alignment = Alignment(vertical="center")
        if fmt:
            value.number_format = fmt
        row += 1
    return row + 1


def _company_banner(worksheet, row: int, editable: bool) -> int:
    worksheet.row_dimensions[row].height = 22
    label = worksheet.cell(row, 1, "Company")
    label.font = LABEL_FONT
    label.alignment = Alignment(vertical="center", indent=1)
    value = worksheet.cell(row, 2, "Microsoft" if editable else "=Selected_Company")
    value.font = Font(name="Calibri", size=14, bold=True, color=NAVY)
    value.fill = INPUT_FILL if editable else WHITE_FILL
    value.alignment = Alignment(vertical="center", indent=1)
    value.border = Border(
        left=Side(style="medium", color=NAVY),
        right=Side(style="medium", color=NAVY),
        top=Side(style="medium", color=NAVY),
        bottom=Side(style="medium", color=NAVY),
    )
    note = worksheet.cell(
        row,
        3,
        "Pick a company. The peer sheet still shows all six."
        if editable
        else "Same company as the dashboard.",
    )
    note.font = Font(name="Calibri", size=10, italic=True, color="5E6A75")
    worksheet.merge_cells(start_row=row, start_column=3, end_row=row, end_column=6)
    return row + 2


def _peer_block(worksheet, row: int, title: str, columns: list[tuple[str, str, str | None]]) -> int:
    width = len(columns) + 1
    row = _section(worksheet, row, title, width)
    row = _headers(worksheet, row, ["Company", *[label for label, _field, _fmt in columns]])
    first = row
    for offset in range(1, 7):
        worksheet.row_dimensions[row].height = 18
        company = worksheet.cell(row, 1, f"=INDEX(tblPeerBenchmarking[Company],{offset})")
        company.font = LABEL_FONT
        company.border = THIN
        for col, (_label, field, fmt) in enumerate(columns, start=2):
            cell = worksheet.cell(row, col, "=" + _peer(field, offset))
            cell.font = BODY
            cell.border = THIN
            if fmt:
                cell.number_format = fmt
        row += 1
    return row + 1, first


def _clear_from(worksheet, start: int, last_col: int = 12) -> None:
    for merged in list(worksheet.merged_cells.ranges):
        if merged.min_row >= start:
            worksheet.unmerge_cells(str(merged))
    last_row = max(worksheet.max_row, start)
    last_used = max(worksheet.max_column, last_col)
    for row in worksheet.iter_rows(min_row=start, max_row=last_row, max_col=last_used):
        for cell in row:
            cell.value = None
            cell.fill = WHITE_FILL
            cell.font = BODY
            cell.border = Border()
            cell.alignment = Alignment(vertical="center")
            cell.number_format = "General"


def _define(workbook, name: str, ref: str) -> None:
    if name in set(workbook.defined_names):
        del workbook.defined_names[name]
    workbook.defined_names.add(DefinedName(name=name, attr_text=ref))


def _input_cell(cell, value, fmt: str) -> None:
    cell.value = value
    cell.font = Font(name="Calibri", size=11, bold=True, color=NAVY)
    cell.fill = INPUT_FILL
    cell.number_format = fmt
    cell.alignment = Alignment(vertical="center")
    cell.border = Border(
        left=Side(style="medium", color=NAVY),
        right=Side(style="medium", color=NAVY),
        top=Side(style="medium", color=NAVY),
        bottom=Side(style="medium", color=NAVY),
    )


def _text(cell, value, font=None) -> None:
    cell.value = value
    cell.font = font or BODY
    cell.alignment = Alignment(wrap_text=True, vertical="center", indent=1)


def _formula(cell, formula: str, fmt: str | None = None) -> None:
    cell.value = formula
    cell.font = BODY
    cell.border = THIN
    cell.alignment = Alignment(vertical="center")
    if fmt:
        cell.number_format = fmt


def _latest(column: str, company_cell: str) -> str:
    return _kept(
        f'XLOOKUP({company_cell},tblExecutiveSummary[Company],tblExecutiveSummary[{column}],"")'
    )


def _write_phase4(workbook, forecast) -> None:
    """Three-year forecast from the latest reported year. Shocks are the only typed inputs."""
    if forecast["A10"].value != "Fiscal year" or forecast["A11"].value != "Revenue":
        raise RuntimeError("Forecast baseline moved. Phase 4 cell references would be wrong.")

    assumptions = workbook["Assumptions"]
    _clear_from(assumptions, 16, 12)
    assumptions.column_dimensions["A"].width = 34
    for col in range(2, 12):
        assumptions.column_dimensions[get_column_letter(col)].width = 18

    _section(assumptions, 16, "Scenario shocks", 4)
    assumptions.row_dimensions[17].height = 36
    assumptions.merge_cells("A17:F17")
    _text(
        assumptions["A17"],
        "Base is the latest reported year. Downside and upside add the shaded shocks. Change a shock to run a different case.",
    )
    _headers(assumptions, 18, ["Driver", "Downside", "Upside"])
    for row, label, down, up, fmt in (
        (19, "Revenue growth", -0.05, 0.05, "0.0%"),
        (20, "Operating margin", -0.02, 0.02, "0.0%"),
        (21, "Cash conversion", -0.10, 0.10, "0.000"),
    ):
        assumptions.row_dimensions[row].height = 20
        _text(assumptions.cell(row, 1), label)
        assumptions.cell(row, 1).border = THIN
        _input_cell(assumptions.cell(row, 2), down, fmt)
        _input_cell(assumptions.cell(row, 3), up, fmt)
    for row, label in ((19, "Base"), (20, "Downside"), (21, "Upside")):
        _text(assumptions.cell(row, 6), label)

    _section(assumptions, 23, "Latest-year seeds", 11)
    assumptions.row_dimensions[24].height = 32
    assumptions.merge_cells("A24:K24")
    _text(
        assumptions["A24"],
        "Pulled from the latest reported year. Cash conversion is used only when Meaningful is TRUE.",
    )
    _headers(
        assumptions,
        25,
        [
            "Company",
            "Fiscal year",
            "Revenue growth",
            "Operating margin",
            "Net margin",
            "Net income / operating income",
            "Cash conversion",
            "Meaningful",
            "OCF margin",
            "CapEx / revenue",
            "Expense to revenue",
        ],
    )
    for offset, company in enumerate(COMPANY_ORDER):
        row = 26 + offset
        assumptions.row_dimensions[row].height = 18
        _text(assumptions.cell(row, 1), company, LABEL_FONT)
        assumptions.cell(row, 1).border = THIN
        _formula(assumptions.cell(row, 2), "=" + _latest("Fiscal_Year", f"A{row}"), "0")
        _formula(assumptions.cell(row, 3), "=" + _latest("Growth_Rate", f"A{row}"), "0.0%")
        _formula(assumptions.cell(row, 4), "=" + _latest("Operating_Margin_pct", f"A{row}"), "0.0%")
        _formula(assumptions.cell(row, 5), "=" + _latest("Net_Income_Margin_pct", f"A{row}"), "0.0%")
        key = f'A{row}&"|"&B{row}'
        _formula(
            assumptions.cell(row, 6),
            "=LET("
            f'k,{key},'
            'oi,XLOOKUP(k,tblPerformance[Key],tblPerformance[Operating_Income],""),'
            'ni,XLOOKUP(k,tblPerformance[Key],tblPerformance[Net_Income],""),'
            'IF(OR(oi="",oi=0,ni=""),"",ni/oi))',
            "0.000",
        )
        _formula(assumptions.cell(row, 7), "=" + _latest("Cash_Conversion_Ratio", f"A{row}"), "0.000")
        _formula(assumptions.cell(row, 8), "=" + _latest("Cash_Conversion_Meaningful", f"A{row}"))
        _formula(assumptions.cell(row, 9), "=" + _latest("Operating_Cash_Flow_Margin_pct", f"A{row}"), "0.0%")
        _formula(
            assumptions.cell(row, 10),
            "=LET("
            f'k,{key},'
            'rev,XLOOKUP(k,tblPerformance[Key],tblPerformance[Revenue],""),'
            'capex,XLOOKUP(k,tblPerformance[Key],tblPerformance[Capital_Expenditures],""),'
            'IF(OR(rev="",rev=0,capex=""),"",capex/rev))',
            "0.0%",
        )
        _formula(
            assumptions.cell(row, 11),
            "=" + _latest("Operating_Expense_to_Revenue", f"A{row}"),
            "0.0%",
        )

    _define(workbook, "Shock_Down_Growth", "Assumptions!$B$19")
    _define(workbook, "Shock_Up_Growth", "Assumptions!$C$19")
    _define(workbook, "Shock_Down_Margin", "Assumptions!$B$20")
    _define(workbook, "Shock_Up_Margin", "Assumptions!$C$20")
    _define(workbook, "Shock_Down_Conversion", "Assumptions!$B$21")
    _define(workbook, "Shock_Up_Conversion", "Assumptions!$C$21")
    _define(workbook, "Scenario_List", "Assumptions!$F$19:$F$21")

    _clear_from(forecast, 20, 12)
    spots = _write_calc(workbook)
    _section(forecast, 20, "Drivers", 4)
    forecast.row_dimensions[21].height = 22
    _text(forecast["A21"], "Scenario", LABEL_FONT)
    forecast["A21"].border = THIN
    _input_cell(forecast["B21"], "Base", "General")
    forecast.merge_cells("C21:F21")
    _text(forecast["C21"], "Base, downside, or upside.")

    def picked(column: str) -> str:
        return (
            f'IF($B$21="","",INDEX(Calc!{column}$9:{column}$11,MATCH($B$21,Calc!$A$9:$A$11,0)))'
        )

    for row, label in (
        (22, "Revenue growth"),
        (23, "Operating margin"),
        (24, "Cash method"),
        (25, "Cash conversion"),
        (26, "OCF margin"),
        (27, "Net income / operating income"),
        (28, "Net margin"),
        (29, "CapEx / revenue"),
    ):
        _text(forecast.cell(row, 1), label)
        forecast.cell(row, 1).border = THIN
    _formula(forecast["B22"], "=" + picked("B"), "0.0%")
    _formula(forecast["B23"], "=" + picked("C"), "0.0%")
    _formula(forecast["B24"], '=IF(Calc!E5="","",IF(Calc!E5,"Cash conversion","OCF margin"))')
    _formula(forecast["B25"], f'=IF(B24<>"Cash conversion","",{picked("D")})', "0.000")
    _formula(forecast["B26"], "=Calc!F5", "0.0%")
    _formula(forecast["B27"], "=Calc!G5", "0.000")
    _formula(forecast["B28"], "=Calc!H5", "0.0%")
    _formula(forecast["B29"], "=Calc!I5", "0.0%")
    _text(forecast.cell(30, 1), "Expense to revenue")
    forecast.cell(30, 1).border = THIN
    _formula(forecast["B30"], "=Calc!J5", "0.0%")

    _section(forecast, 31, "Forecast", 8)
    _headers(
        forecast,
        32,
        ["Fiscal year", "Revenue", "Operating income", "Net income", "Operating cash flow", "CapEx", "Free cash flow", "Operating expenses"],
    )
    for index, row in enumerate((33, 34, 35)):
        if index == 0:
            _formula(forecast.cell(row, 1), '=IF($B$10="","",$B$10+1)', "0")
            revenue = '=IF(OR($B$11="",$B$22=""),"",$B$11*(1+$B$22))'
        else:
            _formula(forecast.cell(row, 1), f'=IF(A{row - 1}="","",A{row - 1}+1)', "0")
            revenue = f'=IF(OR(B{row - 1}="",$B$22=""),"",B{row - 1}*(1+$B$22))'
        _formula(forecast.cell(row, 2), revenue, "#,##0")
        _formula(forecast.cell(row, 3), f'=IF(OR(B{row}="",$B$23=""),"",B{row}*$B$23)', "#,##0")
        _formula(
            forecast.cell(row, 4),
            f'=IF(B{row}="","",IF($B$27="",IF($B$28="","",B{row}*$B$28),C{row}*$B$27))',
            "#,##0",
        )
        _formula(
            forecast.cell(row, 5),
            f'=IF(B{row}="","",IF($B$24="Cash conversion",IF(OR(D{row}="",$B$25=""),"",D{row}*$B$25),IF($B$26="","",B{row}*$B$26)))',
            "#,##0",
        )
        _formula(forecast.cell(row, 6), f'=IF(OR(B{row}="",$B$29=""),"",B{row}*$B$29)', "#,##0")
        _formula(forecast.cell(row, 7), f'=IF(OR(E{row}="",F{row}=""),"",E{row}-F{row})', "#,##0")
        _formula(forecast.cell(row, 8), f'=IF(OR(B{row}="",$B$30=""),"",B{row}*$B$30)', "#,##0")

    forecast.row_dimensions[36].height = 48
    forecast.merge_cells("A36:H36")
    _formula(
        forecast["A36"],
        '=IF(OR(B23="",B13=""),"",IF(ABS(B23-B13)<0.0000001,'
        '"Operating margin is held at the latest reported year, so operating income grows with revenue. '
        'The expense ratio is also held. This is not an expansion of operating leverage.",'
        '"The scenario operating margin is "&IF(B23>B13,"higher than","lower than")'
        '&" the latest reported year, so operating income grows "&IF(B23>B13,"faster than","slower than")'
        '&" revenue. The expense ratio stays at the latest year."))',
    )
    forecast["A36"].alignment = Alignment(wrap_text=True, vertical="center", indent=1)

    _section(forecast, 37, "Year 3 comparison", 4)
    _text(forecast["A38"], "Year 3 under each case.")
    _headers(forecast, 39, ["Metric", "Base", "Downside", "Upside"])
    base_row = spots["base_y3"]
    down_row = spots["down_y3"]
    up_row = spots["up_y3"]
    for row, label, column in (
        (40, "Revenue", "D"),
        (41, "Operating income", "E"),
        (42, "Free cash flow", "I"),
    ):
        _text(forecast.cell(row, 1), label)
        forecast.cell(row, 1).border = THIN
        _formula(forecast.cell(row, 2), f"=Calc!{column}{base_row}", "#,##0")
        _formula(forecast.cell(row, 3), f"=Calc!{column}{down_row}", "#,##0")
        _formula(forecast.cell(row, 4), f"=Calc!{column}{up_row}", "#,##0")

    _define(workbook, "Selected_Scenario", "'Financial Forecast'!$B$21")
    validation = DataValidation(type="list", formula1="=Scenario_List", allow_blank=False)
    validation.error = "Choose Base, Downside, or Upside."
    validation.errorTitle = "Scenario"
    validation.add(forecast["B21"])
    forecast.add_data_validation(validation)
    _write_forecast_support(forecast, spots["companies"])


def _attention(company: str) -> str:
    parts = []
    for alert in ALERTS:
        if alert["company"] != company:
            continue
        parts.append(
            f"{alert['kind'].capitalize()}: {alert['signal']} {alert['why']} {alert['attention']}"
        )
    return " ".join(parts)


def _shock(down_name: str, up_name: str) -> str:
    return f'IF(Selected_Scenario="Downside",{down_name},IF(Selected_Scenario="Upside",{up_name},0))'


def _calc_label(cell, value: str) -> None:
    cell.value = value
    cell.font = Font(name="Calibri", size=10, bold=True, color=NAVY)


def _write_calc(workbook) -> dict[str, int]:
    """Working area for the three cases and the six-company year-3 block."""
    if "Calc" in workbook.sheetnames:
        del workbook["Calc"]
    calc = workbook.create_sheet("Calc", workbook.sheetnames.index("Assumptions") + 1)
    calc.sheet_properties.tabColor = "7F8C8D"
    calc.page_setup.orientation = "landscape"
    calc.page_setup.fitToWidth = 1
    calc.page_setup.fitToHeight = 0
    calc.sheet_properties.pageSetUpPr.fitToPage = True
    calc.page_setup.paperSize = calc.PAPERSIZE_TABLOID
    calc.oddFooter.left.text = "Business Performance Analysis"
    calc.oddFooter.right.text = "Calc"
    calc.freeze_panes = "A5"
    calc.column_dimensions["A"].width = 24
    for col in range(2, 13):
        calc.column_dimensions[get_column_letter(col)].width = 18
    calc["A1"] = "Calc"
    calc["A1"].font = Font(name="Calibri", size=16, bold=True, color=NAVY)
    calc["A2"] = "Working sheet. The forecast and the company notes read these cells."
    calc["A2"].font = Font(name="Calibri", size=11, italic=True, color="5E6A75")
    calc.merge_cells("A2:F2")

    for col, label in enumerate(
        ["Company", "Growth", "Margin", "Conversion", "Meaningful", "OCF margin", "NI / OI", "Net margin", "CapEx / revenue", "Expense ratio", "Year", "Revenue"],
        start=1,
    ):
        _calc_label(calc.cell(4, col), label)
    pulled = {2: "C", 3: "D", 4: "G", 5: "H", 6: "I", 7: "F", 8: "E", 9: "J", 10: "K", 11: "B"}
    formats = {2: "0.0%", 3: "0.0%", 4: "0.000", 6: "0.0%", 7: "0.000", 8: "0.0%", 9: "0.0%", 10: "0.0%", 11: "0", 12: "#,##0"}
    _formula(calc["A5"], "=Selected_Company")
    for col, letter in pulled.items():
        _formula(
            calc.cell(5, col),
            "=" + _kept(f'XLOOKUP(Selected_Company,Assumptions!$A$26:$A$31,Assumptions!${letter}$26:${letter}$31,"")'),
            formats.get(col),
        )
    _formula(calc["L5"], "=" + _latest("Revenue", "Selected_Company"), "#,##0")

    calc["A7"] = "Scenario rates"
    calc["A7"].font = LABEL_FONT
    for col, label in enumerate(["Scenario", "Growth", "Margin", "Conversion"], start=1):
        _calc_label(calc.cell(8, col), label)
    for row, name, growth, margin, conversion in (
        (9, "Base", None, None, None),
        (10, "Downside", "Shock_Down_Growth", "Shock_Down_Margin", "Shock_Down_Conversion"),
        (11, "Upside", "Shock_Up_Growth", "Shock_Up_Margin", "Shock_Up_Conversion"),
    ):
        _text(calc.cell(row, 1), name, LABEL_FONT)
        if growth is None:
            _formula(calc.cell(row, 2), '=IF(B5="","",B5)', "0.0%")
            _formula(calc.cell(row, 3), '=IF(C5="","",C5)', "0.0%")
            _formula(calc.cell(row, 4), '=IF(D5="","",D5)', "0.000")
        else:
            _formula(calc.cell(row, 2), f'=IF(B5="","",B5+{growth})', "0.0%")
            _formula(calc.cell(row, 3), f'=IF(C5="","",C5+{margin})', "0.0%")
            _formula(calc.cell(row, 4), f'=IF(D5="","",D5+{conversion})', "0.000")

    calc["A13"] = "All three cases"
    calc["A13"].font = LABEL_FONT
    for col, label in enumerate(
        ["Scenario", "Year", "Fiscal year", "Revenue", "Operating income", "Net income", "Operating cash flow", "CapEx", "Free cash flow"],
        start=1,
    ):
        _calc_label(calc.cell(14, col), label)
    face = "'Financial Forecast'"
    year3 = {}
    for name, rate_row, first in (("Base", 9, 15), ("Downside", 10, 18), ("Upside", 11, 21)):
        year3[name] = first + 2
        for offset, row in enumerate(range(first, first + 3)):
            prior = row - 1
            _text(calc.cell(row, 1), name)
            _formula(calc.cell(row, 2), f"={offset + 1}", "0")
            _formula(calc.cell(row, 3), f'=IF({face}!$B$10="","",{face}!$B$10+B{row})', "0")
            if offset == 0:
                revenue = f'=IF(OR({face}!$B$11="",$B${rate_row}=""),"",{face}!$B$11*(1+$B${rate_row}))'
            else:
                revenue = f'=IF(OR(D{prior}="",$B${rate_row}=""),"",D{prior}*(1+$B${rate_row}))'
            _formula(calc.cell(row, 4), revenue, "#,##0")
            _formula(calc.cell(row, 5), f'=IF(OR(D{row}="",$C${rate_row}=""),"",D{row}*$C${rate_row})', "#,##0")
            _formula(
                calc.cell(row, 6),
                f'=IF(D{row}="","",IF({face}!$B$27="",IF({face}!$B$28="","",D{row}*{face}!$B$28),E{row}*{face}!$B$27))',
                "#,##0",
            )
            _formula(
                calc.cell(row, 7),
                f'=IF(D{row}="","",IF({face}!$B$24="Cash conversion",IF(OR(F{row}="",$D${rate_row}=""),"",F{row}*$D${rate_row}),IF({face}!$B$26="","",D{row}*{face}!$B$26)))',
                "#,##0",
            )
            _formula(calc.cell(row, 8), f'=IF(OR(D{row}="",{face}!$B$29=""),"",D{row}*{face}!$B$29)', "#,##0")
            _formula(calc.cell(row, 9), f'=IF(OR(G{row}="",H{row}=""),"",G{row}-H{row})', "#,##0")

    calc["A25"] = "Shock added for every company"
    calc["A25"].font = LABEL_FONT
    for col, label in enumerate(["Growth", "Margin", "Conversion"], start=2):
        _calc_label(calc.cell(26, col), label)
    _formula(calc["B27"], "=" + _shock("Shock_Down_Growth", "Shock_Up_Growth"), "0.0%")
    _formula(calc["C27"], "=" + _shock("Shock_Down_Margin", "Shock_Up_Margin"), "0.0%")
    _formula(calc["D27"], "=" + _shock("Shock_Down_Conversion", "Shock_Up_Conversion"), "0.000")

    for col, label in enumerate(
        ["Company", "Year 3", "Latest revenue", "Growth", "Margin", "Revenue", "Operating income", "Net income", "Conversion", "Operating cash flow", "CapEx", "Free cash flow"],
        start=1,
    ):
        _calc_label(calc.cell(28, col), label)
    first_company = 29
    for offset in range(6):
        row = first_company + offset
        src = 26 + offset
        _formula(calc.cell(row, 1), f"=Assumptions!A{src}")
        _formula(calc.cell(row, 2), f'=IF(Assumptions!B{src}="","",Assumptions!B{src}+3)', "0")
        _formula(calc.cell(row, 3), "=" + _latest("Revenue", f"A{row}"), "#,##0")
        _formula(calc.cell(row, 4), f'=IF(Assumptions!C{src}="","",Assumptions!C{src}+$B$27)', "0.0%")
        _formula(calc.cell(row, 5), f'=IF(Assumptions!D{src}="","",Assumptions!D{src}+$C$27)', "0.0%")
        _formula(calc.cell(row, 6), f'=IF(OR(C{row}="",D{row}=""),"",C{row}*(1+D{row})^3)', "#,##0")
        _formula(calc.cell(row, 7), f'=IF(OR(F{row}="",E{row}=""),"",F{row}*E{row})', "#,##0")
        _formula(
            calc.cell(row, 8),
            f'=IF(F{row}="","",IF(Assumptions!F{src}="",IF(Assumptions!E{src}="","",F{row}*Assumptions!E{src}),G{row}*Assumptions!F{src}))',
            "#,##0",
        )
        _formula(calc.cell(row, 9), f'=IF(Assumptions!G{src}="","",Assumptions!G{src}+$D$27)', "0.000")
        _formula(
            calc.cell(row, 10),
            f'=IF(OR(F{row}="",Assumptions!H{src}=""),"",IF(Assumptions!H{src},IF(OR(H{row}="",I{row}=""),"",H{row}*I{row}),IF(Assumptions!I{src}="","",F{row}*Assumptions!I{src})))',
            "#,##0",
        )
        _formula(calc.cell(row, 11), f'=IF(OR(F{row}="",Assumptions!J{src}=""),"",F{row}*Assumptions!J{src})', "#,##0")
        _formula(calc.cell(row, 12), f'=IF(OR(J{row}="",K{row}=""),"",J{row}-K{row})', "#,##0")
    _guard_formula_length(calc, 40, 12)
    return {"base_y3": year3["Base"], "down_y3": year3["Downside"], "up_y3": year3["Upside"], "companies": first_company}


def _guard_formula_length(worksheet, last_row: int, last_col: int) -> None:
    for row in worksheet.iter_rows(min_row=1, max_row=last_row, max_col=last_col):
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("=") and len(cell.value) > 8000:
                raise RuntimeError(f"{worksheet.title}!{cell.coordinate} formula is {len(cell.value)} characters")


def _write_forecast_support(forecast, company_row: int) -> None:
    """Short note, revenue chart, and the six-company year-3 links."""
    _section(forecast, 44, "Notes", 4)
    notes = [
        "Starts from the latest reported year above. Historical ratios are left as imported.",
        "Base keeps that year's growth and margin. Downside and upside add the shocks on Assumptions.",
        "Expenses follow the latest expense ratio and are not shocked. If cash conversion is not meaningful, cash flow uses the operating-cash-flow margin.",
    ]
    for offset, line in enumerate(notes):
        row = 45 + offset
        forecast.row_dimensions[row].height = 22
        forecast.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        _text(forecast.cell(row, 1), line)

    _section(forecast, 49, "Revenue", 3)
    _headers(forecast, 50, ["Fiscal year", "Reported", "Forecast"])
    for offset, year in enumerate(range(2021, 2030)):
        row = 51 + offset
        year_cell = forecast.cell(row, 1, year)
        year_cell.font = BODY
        year_cell.number_format = "0"
        year_cell.border = THIN
        year_cell.alignment = Alignment(vertical="center")
        _formula(
            forecast.cell(row, 2),
            f'=LET(x,XLOOKUP(Selected_Company&"|"&A{row},tblPerformance[Key],tblPerformance[Revenue],""),IF(x="",NA(),x))',
            "#,##0",
        )
        _formula(
            forecast.cell(row, 3),
            f'=LET(hit,COUNTIF($A$33:$A$35,A{row}),picked,IF(hit=0,NA(),INDEX($B$33:$B$35,MATCH(A{row},$A$33:$A$35,0))),IF(OR(hit=0,picked=""),NA(),picked))',
            "#,##0",
        )
    forecast.merge_cells("A60:C60")
    _text(forecast["A60"], "The line breaks where a year is missing.")
    chart = LineChart()
    chart.title = "Revenue"
    chart.y_axis.numFmt = "#,##0"
    chart.x_axis.numFmt = "0"
    chart.height = 7
    chart.width = 15
    chart.display_blanks = "gap"
    chart.legend.position = "b"
    chart.add_data(Reference(forecast, min_col=2, min_row=50, max_col=3, max_row=59), titles_from_data=True)
    chart.set_categories(Reference(forecast, min_col=1, min_row=51, max_row=59))
    forecast.add_chart(chart, "E49")

    _section(forecast, 68, "Year-3 free cash flow", 5)
    forecast.row_dimensions[69].height = 22
    forecast.merge_cells("A69:E69")
    _text(forecast["A69"], "Same case as the dropdown. Each company keeps its own latest year.")
    _headers(forecast, 70, ["Company", "Year", "Revenue", "Operating income", "Free cash flow"])
    for offset in range(6):
        src = company_row + offset
        row = 71 + offset
        _formula(forecast.cell(row, 1), f"=Calc!A{src}")
        _formula(forecast.cell(row, 2), f"=Calc!B{src}", "0")
        _formula(forecast.cell(row, 3), f"=Calc!F{src}", "#,##0")
        _formula(forecast.cell(row, 4), f"=Calc!G{src}", "#,##0")
        _formula(forecast.cell(row, 5), f"=Calc!L{src}", "#,##0")
    _guard_formula_length(forecast, 80, 8)


NOTE_TOPICS = (
    ("Revenue growth trend", "Growth", "B"),
    ("Profitability", "Profitability", "C"),
    ("Operating expense efficiency", "Operations", "D"),
    ("Cash generation", "Cash Flow", "E"),
    ("Financial health", "Financial Health", "F"),
    ("Strengths and risks", "Attention", "H"),
    ("Management consideration", "Management Attention", "G"),
)


def _write_management(workbook, analysis, row: int) -> None:
    calc = workbook["Calc"]
    calc["A35"] = "Notes"
    calc["A35"].font = LABEL_FONT
    for col, label in enumerate(
        ["Company", "Growth", "Profitability", "Operations", "Cash Flow", "Financial Health", "Management Attention", "Attention"],
        start=1,
    ):
        _calc_label(calc.cell(36, col), label)
    for offset, company in enumerate(COMPANY_ORDER):
        source_row = 37 + offset
        notes = EXECUTIVE[company]
        calc.cell(source_row, 1, company)
        calc.cell(source_row, 2, notes["Growth"])
        calc.cell(source_row, 3, notes["Profitability"])
        calc.cell(source_row, 4, notes["Operations"])
        calc.cell(source_row, 5, notes["Cash Flow"])
        calc.cell(source_row, 6, notes["Financial Health"])
        calc.cell(source_row, 7, notes["Management Attention"])
        calc.cell(source_row, 8, _attention(company))
    if row < 20:
        raise RuntimeError(f"Management section starts at row {row}")
    row = _section(analysis, row, "Management considerations", 7)
    for label, _key, column in NOTE_TOPICS:
        analysis.row_dimensions[row].height = 64
        _text(analysis.cell(row, 1), label, LABEL_FONT)
        analysis.cell(row, 1).border = THIN
        analysis.merge_cells(start_row=row, start_column=2, end_row=row, end_column=7)
        _formula(
            analysis.cell(row, 2),
            f'=IF(Selected_Company="","",XLOOKUP(Selected_Company,Calc!$A$37:$A$42,Calc!{column}$37:{column}$42,""))',
        )
        analysis.cell(row, 2).alignment = Alignment(wrap_text=True, vertical="center", indent=1)
        row += 1
    analysis.row_dimensions[row].height = 36
    _text(analysis.cell(row, 1), "Apple ROE", LABEL_FONT)
    analysis.cell(row, 1).border = THIN
    analysis.merge_cells(start_row=row, start_column=2, end_row=row, end_column=7)
    _formula(
        analysis.cell(row, 2),
        '=IF(Selected_Company="Apple","Read ROE next to ROA. Buybacks reduce equity, which lifts ROE.","")',
    )
    analysis.cell(row, 2).alignment = Alignment(wrap_text=True, vertical="center", indent=1)


def _write_competition(peer, row: int) -> None:
    row = _section(peer, row, "What the differences mean", 6)
    peer.row_dimensions[row].height = 32
    peer.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    _text(
        peer.cell(row, 1),
        "Rank 1 is strongest. Rank 6 is weakest. The average weights the nine FY2025 metrics equally.",
    )
    row += 2
    _text(peer.cell(row, 1), "Lowest average rank", LABEL_FONT)
    peer.cell(row, 1).border = THIN
    _formula(peer.cell(row, 2), "=INDEX(tblPeerBenchmarking[Company],1)")
    _formula(peer.cell(row, 3), "=" + _kept("INDEX(tblPeerBenchmarking[Average_Rank],1)"), "0.000")
    row += 1
    _text(peer.cell(row, 1), "Highest average rank", LABEL_FONT)
    peer.cell(row, 1).border = THIN
    _formula(peer.cell(row, 2), "=INDEX(tblPeerBenchmarking[Company],6)")
    _formula(peer.cell(row, 3), "=" + _kept("INDEX(tblPeerBenchmarking[Average_Rank],6)"), "0.000")
    row += 2
    peer.row_dimensions[row].height = 72
    peer.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    _text(peer.cell(row, 1), PEER)
    row += 1
    peer.row_dimensions[row].height = 96
    peer.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    _text(peer.cell(row, 1), CONCLUSION)


def apply_company_selector(workbook) -> None:
    assumptions = workbook["Assumptions"]
    found = [
        row
        for row in range(1, 40)
        if assumptions.cell(row, 1).value in COMPANY_ORDER
    ]
    names = [assumptions.cell(row, 1).value for row in found]
    if names != COMPANY_ORDER:
        raise RuntimeError(f"Company_List cells are {names}")
    list_ref = f"Assumptions!$A${found[0]}:$A${found[-1]}"

    driven = [
        "Executive Dashboard",
        "Financial Forecast",
        "Operating Performance",
        "Cash Flow Analysis",
        "Financial Health",
        "Company Analysis",
        "Peer Benchmarking",
    ]
    for name in driven:
        _reset_body(workbook[name], 14)

    dashboard = workbook["Executive Dashboard"]
    _company_banner(dashboard, 6, editable=True)
    row = _metric_list(
        dashboard,
        8,
        "KPI areas",
        "tblExecutiveSummary",
        [
            ("Fiscal year", "Fiscal_Year", "0"),
            ("Revenue", "Revenue", "#,##0"),
            ("Revenue growth", "Growth_Rate", "0.0%"),
            ("Operating margin", "Operating_Margin_pct", "0.0%"),
            ("Net income margin", "Net_Income_Margin_pct", "0.0%"),
            ("Free cash flow", "Free_Cash_Flow", "#,##0"),
            ("ROA", "ROA", "0.0%"),
            ("ROE", "ROE", "0.0%"),
            ("FY2025 average rank", "FY2025_Average_Rank", "0.000"),
        ],
    )
    row = _year_block(
        dashboard,
        row,
        "Historical performance",
        "tblPerformance",
        [
            ("Revenue", "Revenue", "#,##0"),
            ("Revenue growth", "Growth_Rate", "0.0%"),
            ("Operating margin", "Operating_Margin_pct", "0.0%"),
            ("Free cash flow", "Free_Cash_Flow", "#,##0"),
        ],
    )
    row = _section(dashboard, row, "Key observations", 2)
    dashboard.row_dimensions[row].height = 32
    dashboard.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    note = dashboard.cell(
        row,
        1,
        '=IF(Selected_Company="Apple","Read ROE next to ROA. Buybacks reduce equity, which lifts ROE.","")',
    )
    note.font = BODY
    note.alignment = Alignment(wrap_text=True, vertical="center", indent=1)

    forecast = workbook["Financial Forecast"]
    _company_banner(forecast, 6, editable=False)
    row = _metric_list(
        forecast,
        8,
        "Historical baseline",
        "tblExecutiveSummary",
        [
            ("Fiscal year", "Fiscal_Year", "0"),
            ("Revenue", "Revenue", "#,##0"),
            ("Revenue growth", "Growth_Rate", "0.0%"),
            ("Operating margin", "Operating_Margin_pct", "0.0%"),
            ("Free cash flow", "Free_Cash_Flow", "#,##0"),
            ("ROA", "ROA", "0.0%"),
            ("ROE", "ROE", "0.0%"),
        ],
    )
    income_row = row
    forecast.row_dimensions[income_row].height = 18
    forecast.cell(income_row, 1, "Net income").font = BODY
    forecast.cell(income_row, 1).border = THIN
    income = forecast.cell(income_row, 2, "=" + _lookup("tblGrowthTrend", "Net_Income", 'Selected_Company&"|"&B10'))
    income.font = BODY
    income.border = THIN
    income.number_format = "#,##0"
    _write_phase4(workbook, forecast)

    operating = workbook["Operating Performance"]
    _company_banner(operating, 6, editable=False)
    row = 8
    row = _year_block(operating, row, "Revenue", "tblPerformance", [
        ("Revenue", "Revenue", "#,##0"),
        ("Revenue growth", "Growth_Rate", "0.0%"),
    ])
    row = _year_block(operating, row, "Operating expenses", "tblPerformance", [
        ("Operating expenses", "Operating_Expenses", "#,##0"),
        ("Expense growth", "Operating_Expense_Growth", "0.0%"),
        ("Expense to revenue", "Operating_Expense_to_Revenue", "0.0%"),
    ])
    row = _year_block(operating, row, "Margins", "tblPerformance", [
        ("Gross margin", "Gross_Margin_pct", "0.0%"),
        ("Operating margin", "Operating_Margin_pct", "0.0%"),
        ("Net income margin", "Net_Income_Margin_pct", "0.0%"),
    ])
    _year_block(operating, row, "Operating leverage", "tblPerformance", [
        ("Revenue growth minus expense growth", "Revenue_Growth_Minus_Opex_Growth", "0.0%"),
        ("Operating income growth", "Operating_Income_Growth", "0.0%"),
    ])

    cash = workbook["Cash Flow Analysis"]
    _company_banner(cash, 6, editable=False)
    row = 8
    row = _year_block(cash, row, "Net income", "tblPerformance", [
        ("Net income", "Net_Income", "#,##0"),
    ])
    row = _year_block(cash, row, "Operating cash flow", "tblPerformance", [
        ("Operating cash flow", "Cash_Flow_from_Operating_Activities", "#,##0"),
        ("Margin", "Operating_Cash_Flow_Margin_pct", "0.0%"),
        ("Growth", "Operating_Cash_Flow_Growth", "0.0%"),
    ])
    row = _year_block(cash, row, "CapEx", "tblPerformance", [
        ("Capital expenditures", "Capital_Expenditures", "#,##0"),
    ])
    row = _year_block(cash, row, "Free cash flow", "tblPerformance", [
        ("Free cash flow", "Free_Cash_Flow", "#,##0"),
        ("Margin", "Free_Cash_Flow_Margin_pct", "0.0%"),
    ])
    _year_block(cash, row, "Cash conversion", "tblPerformance", [
        ("Cash conversion ratio", "Cash_Conversion_Ratio", "0.000"),
        ("Meaningful", "Cash_Conversion_Meaningful", None),
    ])

    health = workbook["Financial Health"]
    _company_banner(health, 6, editable=False)
    row = 8
    row = _year_block(health, row, "Liquidity", "tblFinancialHealth", [
        ("Current ratio", "Current_ratio", "0.000"),
        ("Current assets", "Total_Current_Assets", "#,##0"),
        ("Current liabilities", "Total_Current_Liabilities", "#,##0"),
    ])
    row = _year_block(health, row, "Leverage", "tblFinancialHealth", [
        ("Total debt", "Total_Debt", "#,##0"),
        ("Debt to equity", "debt_to_equity_ratio", "0.0%"),
        ("Liabilities to assets", "Liabilities_to_Assets", "0.0%"),
        ("Liabilities imputed", "Total_Liabilities_Imputed", None),
        ("Short-term debt reported", "Short_Term_Debt_Reported", None),
        ("Long-term debt reported", "Long_Term_Debt_Reported", None),
    ])
    row = _year_block(health, row, "ROA", "tblFinancialHealth", [
        ("ROA", "ROA", "0.0%"),
        ("ROA average", "ROA_Avg", "0.0%"),
        ("ROA ending", "ROA_Ending", "0.0%"),
        ("Uses ending balance", "ROA_Uses_Ending_Balance", None),
    ])
    _year_block(health, row, "ROE", "tblFinancialHealth", [
        ("ROE", "ROE", "0.0%"),
        ("ROE average", "ROE_Avg", "0.0%"),
        ("ROE ending", "ROE_Ending", "0.0%"),
        ("Uses ending balance", "ROE_Uses_Ending_Balance", None),
    ])

    analysis = workbook["Company Analysis"]
    _company_banner(analysis, 6, editable=False)
    row = 8
    for title, columns in (
        ("Growth", [
            ("Fiscal year", "Fiscal_Year", "0"),
            ("Revenue", "Revenue", "#,##0"),
            ("Revenue growth", "Growth_Rate", "0.0%"),
            ("Prior growth", "Prior_Growth_Rate", "0.0%"),
            ("Growth differential", "Growth_Differential", "0.0%"),
        ]),
        ("Profitability", [
            ("Gross margin", "Gross_Margin_pct", "0.0%"),
            ("Operating margin", "Operating_Margin_pct", "0.0%"),
            ("Net income margin", "Net_Income_Margin_pct", "0.0%"),
        ]),
        ("Operating efficiency", [
            ("Expense to revenue", "Operating_Expense_to_Revenue", "0.0%"),
            ("Expense growth", "Operating_Expense_Growth", "0.0%"),
            ("Revenue growth minus expense growth", "Revenue_Growth_Minus_Opex_Growth", "0.0%"),
        ]),
        ("Cash flow", [
            ("Free cash flow", "Free_Cash_Flow", "#,##0"),
            ("Free cash flow margin", "Free_Cash_Flow_Margin_pct", "0.0%"),
            ("Cash conversion", "Cash_Conversion_Ratio", "0.000"),
            ("Meaningful", "Cash_Conversion_Meaningful", None),
        ]),
        ("Financial health", [
            ("Current ratio", "Current_ratio", "0.000"),
            ("Debt to equity", "debt_to_equity_ratio", "0.0%"),
            ("ROA", "ROA", "0.0%"),
            ("ROE", "ROE", "0.0%"),
            ("Liabilities imputed", "Total_Liabilities_Imputed", None),
            ("Short-term debt reported", "Short_Term_Debt_Reported", None),
        ]),
    ):
        row = _metric_list(analysis, row, title, "tblExecutiveSummary", columns)
    _write_management(workbook, analysis, row)

    peer = workbook["Peer Benchmarking"]
    peer.row_dimensions[6].height = 22
    peer.merge_cells(start_row=6, start_column=1, end_row=6, end_column=6)
    peer_note = peer.cell(6, 1, "All six companies for FY2025. This sheet does not use Selected_Company. A lower average rank is better.")
    peer_note.font = Font(name="Calibri", size=11, italic=True, color="5E6A75")
    peer_note.alignment = Alignment(vertical="center", indent=1)
    value_columns = [
        ("Fiscal year", "Fiscal_Year", "0"),
        ("Revenue growth", "Growth_Rate", "0.0%"),
        ("Operating margin", "Operating_Margin_pct", "0.0%"),
        ("Net income margin", "Net_Income_Margin_pct", "0.0%"),
        ("Expense to revenue", "Operating_Expense_to_Revenue", "0.0%"),
        ("Operating cash flow margin", "Operating_Cash_Flow_Margin_pct", "0.0%"),
        ("Current ratio", "Current_ratio", "0.000"),
        ("Debt to equity", "debt_to_equity_ratio", "0.0%"),
        ("ROA", "ROA", "0.0%"),
        ("ROE", "ROE", "0.0%"),
    ]
    row, _values_start = _peer_block(peer, 8, "Actual metric values", value_columns)
    rank_columns = [
        ("Revenue growth", "Growth_Rate_Rank", "0"),
        ("Operating margin", "Operating_Margin_Rank", "0"),
        ("Net income margin", "Net_Income_Margin_Rank", "0"),
        ("Expense to revenue", "Operating_Expense_to_Revenue_Rank", "0"),
        ("Operating cash flow margin", "Operating_Cash_Flow_Margin_Rank", "0"),
        ("Current ratio", "Current_Ratio_Rank", "0"),
        ("Debt to equity", "Debt_to_Equity_Rank", "0"),
        ("ROA", "ROA_Rank", "0"),
        ("ROE", "ROE_Rank", "0"),
        ("Average rank", "Average_Rank", "0.000"),
    ]
    row, _rank_start = _peer_block(peer, row, "Rankings", rank_columns)
    _write_competition(peer, row)

    existing = set(workbook.defined_names)
    for name in ("Company_List", "Selected_Company"):
        if name in existing:
            del workbook.defined_names[name]
    workbook.defined_names.add(DefinedName(name="Company_List", attr_text=list_ref))
    workbook.defined_names.add(DefinedName(name="Selected_Company", attr_text="'Executive Dashboard'!$B$6"))
    validation = DataValidation(type="list", formula1="=Company_List", allow_blank=False)
    validation.error = "Choose one of the six companies."
    validation.errorTitle = "Company"
    validation.prompt = "Select a company"
    validation.promptTitle = "Company"
    validation.add(dashboard["B6"])
    dashboard.add_data_validation(validation)


def _m_type(column: str) -> str:
    if column in BOOL_COLUMNS:
        return "type logical"
    if column in DOLLAR_COLUMNS or column in INT_COLUMNS or _is_rank_column(column):
        return "Int64.Type"
    if column == "Company":
        return "type text"
    return "type number"


def _query_formula(path: Path, columns: list[str]) -> str:
    pairs = ", ".join(f'{{"{column}", {_m_type(column)}}}' for column in columns)
    location = str(path.resolve())
    return (
        "let\n"
        f'    Source = Csv.Document(File.Contents("{location}"), '
        '[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
        "    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n"
        "    CleanNames = Table.TransformColumnNames(Promoted, "
        'each Text.Trim(Text.Replace(_, Character.FromNumber(65279), ""))),\n'
        "    BlankToNull = Table.ReplaceValue(CleanNames, \"\", null, Replacer.ReplaceValue, "
        "Table.ColumnNames(CleanNames)),\n"
        f"    Typed = Table.TransformColumnTypes(BlankToNull, {{{pairs}}}),\n"
        "    WithKey = Table.AddColumn(Typed, \"Key\", "
        "each if [Company] = null or [Fiscal_Year] = null then null "
        "else [Company] & \"|\" & Text.From([Fiscal_Year]), type text)\n"
        "in\n"
        "    WithKey"
    )


def _table_lookup(list_object, company: str, year: int, column: str):
    headers = [
        list_object.HeaderRowRange.Cells(1, col).Value
        for col in range(1, list_object.ListColumns.Count + 1)
    ]
    body = list_object.DataBodyRange.Value
    company_at = headers.index("Company")
    year_at = headers.index("Fiscal_Year")
    value_at = headers.index(column)
    for record in body:
        if record[company_at] == company and int(record[year_at]) == year:
            return record[value_at]
    raise RuntimeError(f"{company} {year} {column} is not in {list_object.Name}")


def _apply_source_formats(list_object) -> None:
    for index in range(1, list_object.ListColumns.Count + 1):
        column = list_object.ListColumns(index)
        fmt = number_format(str(column.Name))
        if fmt and column.DataBodyRange is not None:
            column.DataBodyRange.NumberFormat = fmt


def _formula_grid(worksheet) -> list[tuple[str, str]]:
    """Cell formulas on one sheet. Deleting a table turns structured refs into #REF!."""
    used = worksheet.UsedRange
    rows = used.Rows.Count
    cols = used.Columns.Count
    grid = used.Formula
    if rows == 1 and cols == 1:
        grid = ((grid,),)
    found = []
    for row_offset in range(rows):
        for col_offset in range(cols):
            value = grid[row_offset][col_offset]
            if isinstance(value, str) and value.startswith("="):
                cell = worksheet.Cells(used.Row + row_offset, used.Column + col_offset)
                found.append((cell.Address, value))
    return found


def attach_power_query(views: dict[str, pd.DataFrame]) -> None:
    """Replace the pasted source tables with Power Query loads of the same CSVs."""
    import win32com.client

    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.AskToUpdateLinks = False
    excel.ScreenUpdating = False
    workbook = None
    try:
        workbook = excel.Workbooks.Open(str(WORKBOOK.resolve()))
        formulas = {
            worksheet.Name: _formula_grid(worksheet)
            for worksheet in workbook.Worksheets
        }
        for key, filename, sheet_name, table_name, expected_rows in EXPORTS:
            frame = views[key]
            formula = _query_formula(SOURCE_DIR / filename, list(frame.columns))
            workbook.Queries.Add(key, formula)
            connection_string = (
                "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;"
                f'Location={key};Extended Properties=""'
            )
            connection = workbook.Connections.Add2(
                f"Query - {key}",
                f"Power Query load of excel/source/{filename}.",
                connection_string,
                f"SELECT * FROM [{key}]",
                2,
            )
            worksheet = workbook.Worksheets(sheet_name)
            if worksheet.ListObjects.Count:
                worksheet.ListObjects(1).Delete()
            worksheet.UsedRange.Clear()
            list_object = worksheet.ListObjects.Add(
                SourceType=0,
                Source=connection,
                LinkSource=False,
                XlListObjectHasHeaders=1,
                Destination=worksheet.Range("A1"),
            )
            list_object.Name = table_name
            list_object.TableStyle = "TableStyleMedium2"
            query_table = list_object.QueryTable
            query_table.CommandType = 2
            query_table.CommandText = f"SELECT * FROM [{key}]"
            query_table.BackgroundQuery = False
            query_table.Refresh(False)
            if list_object.ListRows.Count != expected_rows:
                raise RuntimeError(
                    f"{table_name} loaded {list_object.ListRows.Count} rows, expected {expected_rows}"
                )
            headers = [
                list_object.HeaderRowRange.Cells(1, col).Value
                for col in range(1, list_object.ListColumns.Count + 1)
            ]
            if headers[0] != "Company" or headers[-1] != "Key":
                raise RuntimeError(f"{table_name} headers are {headers[:3]} ... {headers[-1]}")
            _apply_source_formats(list_object)
            worksheet.Tab.Color = 0x756B5E
            worksheet.Activate()
            excel.ActiveWindow.FreezePanes = False
            worksheet.Range("A2").Select()
            excel.ActiveWindow.FreezePanes = True

        _prove_refresh(workbook, views)
        for sheet_name, cells in formulas.items():
            worksheet = workbook.Worksheets(sheet_name)
            for address, formula in cells:
                worksheet.Range(address).Formula = formula
        excel.CalculateFull()
        _prove_formulas(excel, workbook)
        workbook.Save()
    finally:
        if workbook is not None:
            workbook.Close(SaveChanges=False)
        excel.Quit()


def _prove_refresh(workbook, views: dict[str, pd.DataFrame]) -> None:
    """Change one CSV value, refresh, confirm it arrived, then restore the file."""
    list_object = workbook.Worksheets("src_GrowthTrend").ListObjects("tblGrowthTrend")
    original = _table_lookup(list_object, "Microsoft", 2026, "Revenue")
    expected = int(views["growth_trend"].loc[
        (views["growth_trend"]["Company"] == "Microsoft")
        & (views["growth_trend"]["Fiscal_Year"] == 2026),
        "Revenue",
    ].iloc[0])
    if int(original) != expected:
        raise RuntimeError(f"Microsoft FY2026 revenue loaded as {original}, expected {expected}")

    path = SOURCE_DIR / "growth_trend.csv"
    sentinel = 111
    text = path.read_text(encoding="utf-8-sig")
    needle = f"Microsoft,2026,{expected},"
    if needle not in text:
        raise RuntimeError("Microsoft FY2026 revenue was not found in growth_trend.csv")
    path.write_text(text.replace(needle, f"Microsoft,2026,{sentinel},", 1), encoding="utf-8-sig")
    try:
        list_object.QueryTable.Refresh(False)
        loaded = _table_lookup(list_object, "Microsoft", 2026, "Revenue")
        if int(loaded) != sentinel:
            raise RuntimeError(f"Refresh All did not read the updated CSV. Revenue is {loaded}")
    finally:
        write_csv(views["growth_trend"], path)
    list_object.QueryTable.Refresh(False)
    restored = _table_lookup(list_object, "Microsoft", 2026, "Revenue")
    if int(restored) != expected:
        raise RuntimeError(f"Restored CSV did not refresh. Revenue is {restored}")
    blank = _table_lookup(list_object, "AMD", 2021, "Growth_Rate")
    if blank not in (None, ""):
        raise RuntimeError(f"AMD FY2021 growth loaded as {blank!r}")
    expenses = _table_lookup(
        workbook.Worksheets("src_Performance").ListObjects("tblPerformance"),
        "AMD",
        2021,
        "Operating_Expenses",
    )
    if expenses not in (None, ""):
        raise RuntimeError(f"AMD FY2021 operating expenses loaded as {expenses!r}")


def _excel_error(value) -> bool:
    return isinstance(value, int) and value < -2_000_000_000


def _label_row(worksheet, label: str) -> int:
    for row in range(1, 140):
        if worksheet.Cells(row, 1).Value == label:
            return row
    raise RuntimeError(f"{label} was not found on {worksheet.Name}")


def _prove_formulas(excel, workbook) -> None:
    dashboard = workbook.Worksheets("Executive Dashboard")
    forecast = workbook.Worksheets("Financial Forecast")
    assumptions = workbook.Worksheets("Assumptions")
    analysis = workbook.Worksheets("Company Analysis")
    peer = workbook.Worksheets("Peer Benchmarking")
    if forecast.ChartObjects().Count < 1:
        raise RuntimeError("Actual-versus-forecast chart is missing")
    if forecast.Range("B21").Value != "Base":
        raise RuntimeError(f"Selected_Scenario is {forecast.Range('B21').Value}")
    try:
        for index, company in enumerate(COMPANY_ORDER):
            dashboard.Range("B6").Value = company
            excel.Calculate()
            seed = 26 + index
            if assumptions.Range(f"A{seed}").Value != company:
                raise RuntimeError(f"Seed row {seed} is {assumptions.Range(f'A{seed}').Value}")
            latest = forecast.Range("B11").Value
            growth = assumptions.Range(f"C{seed}").Value
            projected = forecast.Range("B33").Value
            ratio = forecast.Range("B30").Value
            expenses = forecast.Range("H33").Value
            if _excel_error(latest) or _excel_error(projected) or latest in (None, "") or growth in (None, ""):
                raise RuntimeError(f"{company} forecast did not calculate")
            expected = float(latest) * (1 + float(growth))
            if abs(float(projected) - expected) > 1:
                raise RuntimeError(f"{company} year-1 revenue is {projected}, expected {expected}")
            if ratio in (None, "") or _excel_error(expenses):
                raise RuntimeError(f"{company} expense forecast did not calculate")
            if abs(float(expenses) - float(projected) * float(ratio)) > 1:
                raise RuntimeError(f"{company} operating expenses are {expenses}")
            year3_row = _label_row(forecast, "Year-3 free cash flow") + 3
            free_cash = forecast.Cells(year3_row + index, 5).Value
            if _excel_error(free_cash) or free_cash in (None, ""):
                raise RuntimeError(f"{company} year-3 free cash flow is {free_cash}")
            if company == "AMD":
                operating = workbook.Worksheets("Operating Performance")
                fy2021 = [
                    row
                    for row in range(1, 80)
                    if operating.Cells(row, 1).Value == 2021
                ]
                if operating.Cells(fy2021[0], 3).Value not in (None, ""):
                    raise RuntimeError(f"AMD FY2021 growth is {operating.Cells(fy2021[0], 3).Value!r}")
                if operating.Cells(fy2021[1], 2).Value not in (None, ""):
                    raise RuntimeError(f"AMD FY2021 operating expenses are {operating.Cells(fy2021[1], 2).Value!r}")
                growth_2022 = operating.Cells(fy2021[0] + 1, 3).Value
                if abs(float(growth_2022) - 0.436) > 0.001:
                    raise RuntimeError(f"AMD FY2022 growth is {growth_2022}")
            note_row = _label_row(analysis, "Revenue growth trend")
            note = analysis.Cells(note_row, 2).Value
            if not isinstance(note, str) or len(note) < 20:
                raise RuntimeError(f"{company} management note is {note!r}")
        dashboard.Range("B6").Value = "CrowdStrike"
        excel.Calculate()
        if forecast.Range("B24").Value != "OCF margin":
            raise RuntimeError(f"CrowdStrike cash method is {forecast.Range('B24').Value}")
        dashboard.Range("B6").Value = "Microsoft"
        forecast.Range("B21").Value = "Downside"
        assumptions.Range("B19").Value = -0.06
        excel.Calculate()
        if "lower than" not in str(forecast.Range("A36").Value):
            raise RuntimeError(f"Downside leverage note is {forecast.Range('A36').Value}")
        downside = forecast.Range("B33").Value
        growth = forecast.Range("B22").Value
        latest = forecast.Range("B11").Value
        shocked = float(assumptions.Range("C26").Value) - 0.06
        if abs(float(growth) - shocked) > 0.000001:
            raise RuntimeError(f"Downside growth is {growth}, expected {shocked}")
        expected = float(latest) * (1 + float(growth))
        if abs(float(downside) - expected) > 1:
            raise RuntimeError(f"Downside revenue is {downside}, expected {expected}")
        low_row = _label_row(peer, "Lowest average rank")
        high_row = _label_row(peer, "Highest average rank")
        if peer.Cells(low_row, 2).Value != "NVIDIA" or round(float(peer.Cells(low_row, 3).Value), 3) != 1.222:
            raise RuntimeError("Lowest average rank is not NVIDIA 1.222")
        if peer.Cells(high_row, 2).Value != "CrowdStrike" or round(float(peer.Cells(high_row, 3).Value), 3) != 4.889:
            raise RuntimeError("Highest average rank is not CrowdStrike 4.889")
        dashboard.Range("B6").Value = "Apple"
        excel.Calculate()
        apple_row = _label_row(analysis, "Apple ROE")
        if "Buybacks" not in str(analysis.Cells(apple_row, 2).Value):
            raise RuntimeError("Apple ROE note did not appear")
    finally:
        assumptions.Range("B19").Value = -0.05
        forecast.Range("B21").Value = "Base"
        dashboard.Range("B6").Value = "Microsoft"
        excel.Calculate()
    latest = forecast.Range("B11").Value
    projected = forecast.Range("B33").Value
    if int(latest) != 331839000000:
        raise RuntimeError(f"Forecast baseline revenue is {latest}")
    if int(round(projected)) != 390906342000:
        raise RuntimeError(f"Base year-1 revenue is {projected}")
    if "held at the latest" not in str(forecast.Range("A36").Value):
        raise RuntimeError(f"Base leverage note is {forecast.Range('A36').Value}")
    peers = workbook.Worksheets("src_PeerBenchmarking").ListObjects("tblPeerBenchmarking")
    rank = _table_lookup(peers, "NVIDIA", 2025, "Average_Rank")
    if round(float(rank), 3) != 1.222:
        raise RuntimeError(f"NVIDIA average rank is {rank}")
    health = workbook.Worksheets("src_FinancialHealth").ListObjects("tblFinancialHealth")
    imputed = _table_lookup(health, "AMD", 2025, "Total_Liabilities_Imputed")
    if imputed is not True:
        raise RuntimeError(f"AMD FY2025 imputed flag is {imputed!r}")


def load() -> None:
    views = build_views()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for key, filename, _sheet, _table, expected_rows in EXPORTS:
        frame = views[key]
        if len(frame) != expected_rows:
            raise RuntimeError(f"{key} has {len(frame)} rows, expected {expected_rows}")
        if set(frame["Company"].astype(str)) != COMPANIES:
            raise RuntimeError(f"{key} companies are {sorted(set(frame['Company']))}")
        write_csv(frame, SOURCE_DIR / filename)
    build()
    from openpyxl import load_workbook

    workbook = load_workbook(WORKBOOK)
    for key, _filename, sheet_name, table_name, _expected in EXPORTS:
        add_source_sheet(workbook, views[key], sheet_name, table_name)
    apply_company_selector(workbook)
    workbook.calculation.fullCalcOnLoad = True
    workbook.active = 0
    workbook.save(WORKBOOK)
    attach_power_query(views)


if __name__ == "__main__":
    load()
    print(WORKBOOK)
