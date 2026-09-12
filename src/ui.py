"""Shared Streamlit presentation helpers. No financial formulas."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

PALETTE = ["#1F4E79", "#4F6F8F", "#3D6B51", "#8A6D3B", "#5C4E7A", "#6B7C8A"]
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Source Sans 3, Segoe UI, sans-serif", color="#1A2332", size=13),
    margin=dict(l=48, r=24, t=56, b=88),
    legend=dict(title_text="", orientation="h", yanchor="top", y=-0.22, x=0),
)

PCT_COLS = {
    "Growth_Rate",
    "Prior_Growth_Rate",
    "Growth_Differential",
    "Gross_Margin_pct",
    "Operating_Margin_pct",
    "Net_Income_Margin_pct",
    "Operating_Expense_to_Revenue",
    "Operating_Income_Growth",
    "Net_Income_Growth",
    "Operating_Expense_Growth",
    "Operating_Cash_Flow_Margin_pct",
    "Operating_Cash_Flow_Growth",
    "Free_Cash_Flow_Margin_pct",
    "Revenue_Growth_Minus_Opex_Growth",
    "ROA",
    "ROE",
    "Liabilities_to_Assets",
}
MONEY_COLS = {
    "Revenue",
    "Net_Income",
    "Operating_Income",
    "Operating_Expenses",
    "Cash_Flow_from_Operating_Activities",
    "Free_Cash_Flow",
    "Capital_Expenditures",
}
RATIO_COLS = {"Current_ratio", "debt_to_equity_ratio", "Cash_Conversion_Ratio"}

COLUMN_LABELS = {
    "Company": "Company",
    "Fiscal_Year": "Fiscal Year",
    "Revenue": "Revenue",
    "Growth_Rate": "Revenue Growth",
    "Prior_Growth_Rate": "Prior Growth Rate",
    "Growth_Differential": "Growth Rate Change",
    "Net_Income_Margin_pct": "Net Income Margin",
    "Gross_Margin_pct": "Gross Margin",
    "Operating_Margin_pct": "Operating Margin",
    "Net_Income_Growth": "Net Income Growth",
    "Operating_Income_Growth": "Operating Income Growth",
    "Operating_Expense_Growth": "Operating Expense Growth",
    "Operating_Expense_to_Revenue": "Operating Expense / Revenue",
    "Revenue_Growth_Minus_Opex_Growth": "Revenue Growth − Operating Expense Growth",
    "Cash_Flow_from_Operating_Activities": "Operating Cash Flow",
    "Operating_Cash_Flow_Margin_pct": "OCF Margin",
    "Operating_Cash_Flow_Growth": "OCF Growth",
    "Cash_Conversion_Ratio": "Cash Conversion Ratio",
    "Free_Cash_Flow": "Free Cash Flow",
    "Current_ratio": "Current Ratio",
    "debt_to_equity_ratio": "Debt-to-Equity",
    "Liabilities_to_Assets": "Liabilities-to-Assets",
    "ROA": "ROA",
    "ROE": "ROE",
    "Rank": "Rank",
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: "Source Sans 3", "Segoe UI", sans-serif; }
        .stApp { background: #F4F6F8; }
        [data-testid="stSidebar"] {
            background: #15233A;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] .brand,
        [data-testid="stSidebar"] .brand-title { color: #E8EEF5 !important; }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
            background-color: #243552 !important;
            color: #E8EEF5 !important;
            border-color: #3A4D6A !important;
        }
        [data-testid="stAppViewContainer"] [data-baseweb="select"] > div,
        [data-testid="stAppViewContainer"] [data-baseweb="input"] {
            background-color: #FFFFFF !important;
            color: #1A2332 !important;
            border-color: #C5CDD6 !important;
        }
        [data-testid="stAppViewContainer"] [data-baseweb="tag"] {
            background-color: #1F4E79 !important;
            color: #FFFFFF !important;
        }
        [data-testid="stAppViewContainer"] [data-baseweb="tag"] span {
            color: #FFFFFF !important;
        }
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] span {
            color: #1A2332;
        }
        div[data-testid="stCheckbox"] label p {
            color: #1A2332 !important;
            font-weight: 600 !important;
        }
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        [data-testid="stHeader"] button,
        [data-testid="stSidebarCollapsedControl"] button {
            color: #15233A !important;
        }
        [data-testid="stSidebar"] button {
            color: #E8EEF5 !important;
        }
        [data-testid="stSidebar"] [data-testid="stBaseButton-header"],
        [data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] {
            background: #243552 !important;
            border: 1px solid #3A4D6A !important;
            border-radius: 6px !important;
        }
        .brand { font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase;
                 color: #A8B8CC; margin-bottom: 0.25rem; }
        .brand-title { font-size: 1.05rem; font-weight: 700; line-height: 1.3; margin-bottom: 1.25rem; }
        h1 { font-size: 1.7rem !important; font-weight: 700 !important; color: #15233A !important; }
        .subtitle { color: #4B5563; margin-top: -0.6rem; margin-bottom: 1.25rem; }
        .kpi-label { font-size: 0.75rem; color: #5B6775; text-transform: uppercase; letter-spacing: 0.04em; }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E6EC;
            border-radius: 10px;
            padding: 12px 14px;
            box-shadow: 0 1px 2px rgba(21,35,58,0.04);
            width: 100%;
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] p {
            color: #5B6775 !important;
            white-space: nowrap !important;
            overflow: visible !important;
            font-size: 0.8rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
            display: flex !important;
            flex-wrap: nowrap !important;
            justify-content: center !important;
            gap: 12px !important;
        }
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > div[data-testid="stColumn"] {
            flex: 1 1 0 !important;
            min-width: 0 !important;
        }
        .section-label { font-size: 0.8rem; font-weight: 700; letter-spacing: 0.06em;
                         text-transform: uppercase; color: #1F4E79; margin: 1.2rem 0 0.4rem 0; }
        .interp { background: #FFFFFF; border-left: 3px solid #1F4E79; padding: 0.9rem 1.1rem;
                  border: 1px solid #E2E6EC; border-left-width: 3px; border-radius: 8px; color: #1A2332; }
        .alert { background: #FFFFFF; border: 1px solid #E2E6EC; border-radius: 10px;
                 padding: 1rem 1.1rem; margin-bottom: 0.85rem; }
        .alert-k { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: #5B6775; }
        .tag { display: inline-block; font-size: 0.7rem; font-weight: 600; padding: 2px 8px;
               border-radius: 999px; margin-left: 8px; }
        .tag-investigate { background: #F4E6E4; color: #7A3A32; }
        .tag-monitor { background: #F3EBD6; color: #6A5420; }
        .tag-mixed { background: #E7EEF6; color: #1F4E79; }
        .tag-positive { background: #E4EFE8; color: #2C5A3C; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def fmt_pct(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.1%}"


def fmt_ratio(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.2f}"


def fmt_money(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    abs_v = abs(float(value))
    sign = "-" if value < 0 else ""
    if abs_v >= 1e9:
        return f"{sign}${abs_v / 1e9:.1f}B"
    if abs_v >= 1e6:
        return f"{sign}${abs_v / 1e6:.1f}M"
    return f"{sign}${abs_v:,.0f}"


def kpi_cards(items: list[tuple[str, str]]) -> None:
    if not items:
        return
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def show_table(frame: pd.DataFrame, columns: list[str]) -> None:
    cols = [c for c in columns if c in frame.columns]
    show = frame[cols].copy()
    show = show.rename(columns={c: COLUMN_LABELS.get(c, c) for c in cols})
    fmt: dict[str, str] = {}
    for src in cols:
        label = COLUMN_LABELS.get(src, src)
        if src in PCT_COLS:
            fmt[label] = "{:.1%}"
        elif src in MONEY_COLS:
            fmt[label] = "{:,.0f}"
        elif src in RATIO_COLS:
            fmt[label] = "{:.2f}"
        elif src == "Rank":
            fmt[label] = "{:.0f}"
    st.dataframe(show.style.format(fmt, na_rep="—"), use_container_width=True, hide_index=True)


def line_chart(frame: pd.DataFrame, y: str, title: str, percent: bool = False) -> None:
    if frame.empty:
        st.info("No rows for the current filters.")
        return
    color = "Company" if frame["Company"].nunique() > 1 else None
    fig = px.line(
        frame,
        x="Fiscal_Year",
        y=y,
        color=color,
        markers=True,
        title=title,
        color_discrete_sequence=PALETTE,
    )
    if percent:
        fig.update_yaxes(tickformat=".0%")
    fig.update_layout(**CHART_LAYOUT)
    fig.update_xaxes(dtick=1, title="Fiscal Year")
    fig.update_yaxes(title=COLUMN_LABELS.get(y, y))
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(
    frame: pd.DataFrame,
    y: str,
    title: str,
    percent: bool = False,
    x: str = "Company",
    color: str | None = "Company",
    barmode: str = "relative",
    showlegend: bool = False,
) -> None:
    if frame.empty:
        st.info("No rows for the current filters.")
        return
    fig = px.bar(
        frame,
        x=x,
        y=y,
        title=title,
        color=color,
        barmode=barmode,
        color_discrete_sequence=PALETTE,
        text=y,
    )
    fig.update_layout(**CHART_LAYOUT, showlegend=showlegend)
    if percent:
        fig.update_traces(texttemplate="%{y:.1%}", textposition="outside", cliponaxis=False)
        fig.update_yaxes(tickformat=".0%")
    elif y in MONEY_COLS:
        fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside", cliponaxis=False)
    else:
        fig.update_traces(texttemplate="%{y:.2f}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(title=COLUMN_LABELS.get(y, y))
    fig.update_xaxes(title=COLUMN_LABELS.get(x, x))
    st.plotly_chart(fig, use_container_width=True)


def metric_chart(frame: pd.DataFrame, y: str, title: str, percent: bool = False, year_label: str = "All") -> None:
    if year_label == "All":
        line_chart(frame, y, title, percent=percent)
        return
    cleaned = title.replace(" trend", "").replace(" by fiscal year", "")
    suffix = "latest year" if year_label == "Latest" else f"FY{year_label}"
    bar_chart(frame, y, f"{cleaned} — {suffix}", percent=percent)


def interpretation_box(title: str, text: str) -> None:
    st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="interp">{text}</div>', unsafe_allow_html=True)


def show_data_notes(text: str, year_label) -> None:
    if year_label not in ("All", "Latest"):
        try:
            if int(year_label) < 2024:
                return
        except (TypeError, ValueError):
            return
    interpretation_box("What the data shows", text)


def page_intro(title: str, purpose: str, view_name: str) -> None:
    st.title(title)
    st.markdown(f'<p class="subtitle">{purpose}</p>', unsafe_allow_html=True)
    st.caption(f"Source view: `{view_name}`")
