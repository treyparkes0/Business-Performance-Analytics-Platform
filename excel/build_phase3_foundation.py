"""Build the Phase 3 workbook foundation.

Nine worksheets, section locations, and connection status only.
No imported financial values, no company selector, and no forecast formulas.
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

OUT = Path(__file__).resolve().parent / "Business_Performance_Analysis.xlsx"

NAVY = "0E2A47"
GOLD = "C4A35A"
SECTION = "E6EEF5"
INK = "1C2833"
MUTED = "5E6A75"
LINE = "D5DDE5"
WHITE = "FFFFFF"
BAND = "F4F7FA"
STATUS = "F7F1DE"

LAST_COL = 8
THIN = Border(
    left=Side(style="thin", color=LINE),
    right=Side(style="thin", color=LINE),
    top=Side(style="thin", color=LINE),
    bottom=Side(style="thin", color=LINE),
)
BOTTOM = Border(bottom=Side(style="thin", color=LINE))

TITLE_FONT = Font(name="Calibri", size=20, bold=True, color=WHITE)
SUB_FONT = Font(name="Calibri", size=11, color="D6E0EA")
STATUS_FONT = Font(name="Calibri", size=10, italic=True, color="6B5420")
SECTION_FONT = Font(name="Calibri", size=13, bold=True, color=NAVY)
BODY_FONT = Font(name="Calibri", size=11, color=INK)
MUTED_FONT = Font(name="Calibri", size=11, color=MUTED)
HEADER_FONT = Font(name="Calibri", size=10, bold=True, color=WHITE)
LABEL_FONT = Font(name="Calibri", size=11, bold=True, color=NAVY)

WRAP = Alignment(wrap_text=True, vertical="center")
LEFT = Alignment(vertical="center", indent=1)


def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def _merge(ws, row: int, start: int, end: int) -> None:
    ws.merge_cells(start_row=row, start_column=start, end_row=row, end_column=end)


def _banner(ws, title: str, subtitle: str) -> None:
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 110
    ws.freeze_panes = "A5"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_setup.paperSize = ws.PAPERSIZE_TABLOID
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.horizontalCentered = True
    ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.6, bottom=0.55, header=0.25, footer=0.25)
    ws.print_title_rows = "1:3"
    ws.page_setup.scale = 100
    ws.oddFooter.left.text = "Business Performance Analysis"
    ws.oddFooter.center.text = ""
    ws.oddFooter.right.text = "Page &P"
    ws.oddFooter.left.font = "Calibri"
    ws.sheet_properties.tabColor = NAVY

    ws.row_dimensions[1].height = 34
    ws.row_dimensions[2].height = 22
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 8

    for row, value, font, fill in (
        (1, title, TITLE_FONT, _fill(NAVY)),
        (2, subtitle, SUB_FONT, _fill(NAVY)),
    ):
        _merge(ws, row, 1, LAST_COL)
        cell = ws.cell(row, 1, value)
        cell.font = font
        cell.alignment = LEFT
        cell.fill = fill
        for col in range(1, LAST_COL + 1):
            ws.cell(row, col).fill = fill
            ws.cell(row, col).border = Border(bottom=Side(style="thin", color=NAVY))
    ws.row_dimensions[3].height = 10

    widths = {"A": 34, "B": 28, "C": 38, "D": 28, "E": 24, "F": 24, "G": 28, "H": 22}
    for letter, width in widths.items():
        ws.column_dimensions[letter].width = width
    ws.auto_filter.ref = None
    ws.sheet_view.view = "normal"
    ws.print_options.horizontalCentered = True
    ws.page_setup.fitToWidth = 1
    ws.sheet_format.defaultRowHeight = 18


def _section(ws, row: int, title: str) -> int:
    ws.row_dimensions[row].height = 24
    _merge(ws, row, 1, LAST_COL)
    cell = ws.cell(row, 1, title)
    cell.font = SECTION_FONT
    cell.alignment = LEFT
    cell.fill = _fill(SECTION)
    for col in range(1, LAST_COL + 1):
        ws.cell(row, col).fill = _fill(SECTION)
        ws.cell(row, col).border = Border(bottom=Side(style="thin", color=GOLD))
    return row + 1


def _lines(ws, row: int, lines: list[str]) -> int:
    for line in lines:
        ws.row_dimensions[row].height = 32
        _merge(ws, row, 1, LAST_COL)
        cell = ws.cell(row, 1, line)
        cell.font = BODY_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center", indent=1)
        return_row_fill = _fill(WHITE)
        for col in range(1, LAST_COL + 1):
            ws.cell(row, col).fill = return_row_fill
        row += 1
    return row + 1


def _table(ws, row: int, headers: list[str], records: list[list[str]]) -> int:
    ws.row_dimensions[row].height = 22
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row, col, header)
        cell.font = HEADER_FONT
        cell.fill = _fill(NAVY)
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="left", indent=1)
        cell.border = THIN
    row += 1
    for record in records:
        ws.row_dimensions[row].height = 30
        for col, value in enumerate(record, start=1):
            cell = ws.cell(row, col, value)
            cell.font = BODY_FONT
            cell.alignment = Alignment(wrap_text=True, vertical="center", indent=1)
            cell.border = THIN
            cell.fill = _fill(WHITE if row % 2 else BAND)
        row += 1
    return row + 1


def build() -> Path:
    wb = Workbook()
    specs = [
        (
            "Executive Dashboard",
            "Selected-company view of historical performance.",
            [
                (
                    "Company selector",
                    [
                        "The selector is not active yet. The next task adds the named range Company_List and the named input Selected_Company.",
                        "Companies, matched to the Company field: Microsoft, Apple, NVIDIA, Adobe, AMD, CrowdStrike.",
                    ],
                ),
                (
                    "KPI areas",
                    [
                        "Reserved for the latest-year revenue, growth, margins, cash flow, and returns.",
                        "tblExecutiveSummary is loaded on src_ExecutiveSummary. This section is not linked yet.",
                    ],
                ),
                (
                    "Historical performance",
                    [
                        "Reserved for the company-year history.",
                        "Sources after import: tblGrowthTrend, tblPerformance, and tblFinancialHealth, filtered to Selected_Company.",
                    ],
                ),
                (
                    "Key observations",
                    [
                        "Reserved for narrative. No observations are written in this foundation.",
                        "Apple ROE is read next to ROA. That note is not a calculation.",
                    ],
                ),
            ],
        ),
        (
            "Financial Forecast",
            "Three-year forecast from each company's latest reported year.",
            [
                (
                    "Historical baseline",
                    ["The last reported year will be linked from the imported views. No baseline amounts are entered."],
                ),
                (
                    "Assumption area",
                    ["Drivers will be read from the Assumptions sheet. No driver values are entered."],
                ),
                (
                    "Forecast sections",
                    ["Locations are reserved for the income statement, cash flow, and returns. Formulas are not built."],
                ),
                (
                    "Scenario comparison area",
                    ["Locations are reserved for base, downside, and upside. No scenario values are entered."],
                ),
            ],
        ),
        (
            "Operating Performance",
            "Revenue, cost, margin, and operating leverage for the selected company.",
            [
                (
                    "Revenue",
                    ["Source after import: tblPerformance.Revenue and tblGrowthTrend.Growth_Rate. No amounts are entered."],
                ),
                (
                    "Operating expenses",
                    ["Source after import: Operating_Expenses, Operating_Expense_Growth, and Operating_Expense_to_Revenue. Source nulls stay blank."],
                ),
                (
                    "Margins",
                    ["Source after import: Gross_Margin_pct, Operating_Margin_pct, and Net_Income_Margin_pct. Ratios stay decimals."],
                ),
                (
                    "Operating leverage",
                    ["Source after import: Revenue_Growth_Minus_Opex_Growth and Operating_Income_Growth. No leverage formula is added in Excel."],
                ),
            ],
        ),
        (
            "Cash Flow Analysis",
            "Cash generation for the selected company.",
            [
                (
                    "Net income",
                    ["Source after import: tblPerformance.Net_Income. No amounts are entered."],
                ),
                (
                    "Operating cash flow",
                    ["Source after import: Cash_Flow_from_Operating_Activities, Operating_Cash_Flow_Margin_pct, and Operating_Cash_Flow_Growth."],
                ),
                (
                    "CapEx",
                    ["Source after import: Capital_Expenditures. The stored amount is a positive spend. NVIDIA FY2021 stays blank."],
                ),
                (
                    "Free cash flow",
                    ["Source after import: Free_Cash_Flow and Free_Cash_Flow_Margin_pct. Excel does not recalculate free cash flow."],
                ),
                (
                    "Cash conversion",
                    ["Source after import: Cash_Conversion_Ratio and Cash_Conversion_Meaningful. The ratio is a multiple, not a percent."],
                ),
            ],
        ),
        (
            "Financial Health",
            "Liquidity, leverage, and returns for the selected company.",
            [
                (
                    "Liquidity",
                    ["Source after import: Current_ratio, Total_Current_Assets, and Total_Current_Liabilities from tblFinancialHealth."],
                ),
                (
                    "Leverage",
                    ["Source after import: Total_Debt, debt_to_equity_ratio, Liabilities_to_Assets, and the debt-reported and liability-imputed flags."],
                ),
                (
                    "ROA",
                    ["Primary ROA is the average-balance return. ROA_Ending, ROA_Avg, and ROA_Uses_Ending_Balance stay beside it."],
                ),
                (
                    "ROE",
                    ["Primary ROE is the average-balance return. Read it next to ROA. Ending and average columns stay beside it."],
                ),
            ],
        ),
        (
            "Peer Benchmarking",
            "All six companies. This sheet does not follow the company selector.",
            [
                (
                    "Six-company comparison",
                    [
                        "Companies shown together: Microsoft, Apple, NVIDIA, Adobe, AMD, CrowdStrike.",
                        "Comparison year: FY2025, the last year present for every company. Rank order is applied after import.",
                    ],
                ),
                (
                    "Actual metric values",
                    [
                        "FY2025 values for the nine ranked measures come from tblPeerBenchmarking.",
                        "All-year peer values, including revenue, gross margin, growth differential, and liabilities to assets, come from tblPeerMetrics.",
                        "Dollar statement lines stay on tblPerformance and tblFinancialHealth.",
                    ],
                ),
                (
                    "Rankings",
                    [
                        "Ranks and Average_Rank come from tblPeerBenchmarking. A lower average is better.",
                        "The nine ranks are growth, operating margin, net income margin, operating expense to revenue, operating-cash-flow margin, current ratio, debt to equity, ROA, and ROE.",
                    ],
                ),
            ],
        ),
        (
            "Company Analysis",
            "One company across the historical views. The selector is not active yet.",
            [
                (
                    "Growth",
                    ["Source after import: tblGrowthTrend for the selected company."],
                ),
                (
                    "Profitability",
                    ["Source after import: margin and profit columns on tblPerformance."],
                ),
                (
                    "Operating efficiency",
                    ["Source after import: operating-expense ratio, expense growth, and revenue growth minus expense growth."],
                ),
                (
                    "Cash flow",
                    ["Source after import: the cash columns on tblPerformance, including the meaningfulness flag."],
                ),
                (
                    "Financial health",
                    ["Source after import: tblFinancialHealth, including imputation and reported-debt flags."],
                ),
                (
                    "Management considerations",
                    ["Reserved for narrative. No considerations are written in this foundation."],
                ),
            ],
        ),
    ]

    first = wb.active
    first.title = specs[0][0]
    for name, subtitle, sections in specs:
        ws = first if name == specs[0][0] else wb.create_sheet(name)
        _banner(ws, name, subtitle)
        row = 5
        for title, lines in sections:
            row = _section(ws, row, title)
            row = _lines(ws, row, lines)

    assumptions = wb.create_sheet("Assumptions")
    _banner(assumptions, "Assumptions", "Company list, latest-year forecast seeds, and editable scenario shocks.")
    row = _section(assumptions, 5, "Company list")
    row = _lines(
        assumptions,
        row,
        ["These six names are the named range Company_List. The input cell Selected_Company is on Executive Dashboard."],
    )
    row = _table(
        assumptions,
        row,
        ["Company", "Ticker", "Role"],
        [
            ["Microsoft", "MSFT", "Selector value"],
            ["Apple", "AAPL", "Selector value"],
            ["NVIDIA", "NVDA", "Selector value"],
            ["Adobe", "ADBE", "Selector value"],
            ["AMD", "AMD", "Selector value"],
            ["CrowdStrike", "CRWD", "Selector value"],
        ],
    )
    row = _section(assumptions, row, "Future forecast drivers")
    row = _lines(
        assumptions,
        row,
        ["Reserved for Phase 4. No driver names or values are entered."],
    )
    row = _section(assumptions, row, "Scenario inputs")
    _lines(
        assumptions,
        row,
        ["Reserved for base, downside, and upside. No scenario values are entered."],
    )

    connections = wb.create_sheet("Data Connections")
    _banner(connections, "Data Connections", "Power Query reads the six local CSV exports. No warehouse login is stored.")
    row = _section(connections, 5, "Imported source information")
    row = _lines(
        connections,
        row,
        [
            "Excel on this machine has no Databricks connector, so the tables come from the CSV files in excel/source.",
            "Data, Refresh All re-reads those files. If the metrics change, run excel/load_source_tables.py and refresh again.",
            "Leave blanks blank. The ratios and ranks are already in the files. Do not put a warehouse login in this workbook.",
        ],
    )
    _table(
        connections,
        row,
        ["Excel table", "Sheet", "File", "What it is"],
        [
            ["tblGrowthTrend", "src_GrowthTrend", "growth_trend.csv", "Company-year growth, 33 rows"],
            ["tblPerformance", "src_Performance", "performance.csv", "Company-year margins and cash flow, 33 rows"],
            ["tblFinancialHealth", "src_FinancialHealth", "financial_health.csv", "Company-year balance sheet and returns, 33 rows"],
            ["tblPeerBenchmarking", "src_PeerBenchmarking", "peer_benchmarking.csv", "FY2025 ranks, 6 companies"],
            ["tblExecutiveSummary", "src_ExecutiveSummary", "executive_summary.csv", "Latest year for each company"],
            ["tblPeerMetrics", "src_PeerMetrics", "peer_metrics.csv", "Company-year metrics without ranks, 33 rows"],
        ],
    )

    wb.properties.title = "Business Performance Analysis"
    wb.properties.subject = "Business performance analysis"
    wb.properties.creator = "Trey"
    wb.properties.description = (
        "Historical results load through Power Query from the local CSV files. "
        "The three-year forecast is formulas. No warehouse login is stored."
    )
    wb.active = 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
