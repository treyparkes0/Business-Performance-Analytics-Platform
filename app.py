"""Internal Strategy & Operations analytics application."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.bp_metrics import rank_selected_metric
from src.data_source import load_views
from src import glossary as glossary_notes
from src import interpretations as notes
from src.ui import (
    CHART_LAYOUT,
    PALETTE,
    bar_chart,
    fmt_money,
    fmt_pct,
    fmt_ratio,
    inject_css,
    kpi_cards,
    metric_chart,
    page_intro,
    show_data_notes,
    show_table,
)

st.set_page_config(
    page_title="Business Performance Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = [
    "Overview",
    "Company Performance",
    "Operations",
    "Profitability",
    "Cash Flow",
    "Financial Health",
    "Peer Benchmarking",
    "Management Attention",
    "Glossary",
]

KPI_GROUPS = {
    "All": [
        "Revenue Growth",
        "Operating Margin",
        "Net Income Margin",
        "Operating Cash Flow Margin",
        "Current Ratio",
    ],
    "Growth": ["Revenue Growth", "Growth Rate Change", "Net Income Margin"],
    "Profitability": ["Gross Margin", "Operating Margin", "Net Income Margin", "Net Income Growth"],
    "Operations": [
        "Revenue Growth",
        "Operating Expense Growth",
        "Operating Expense / Revenue",
        "Revenue Growth − OpEx Growth",
    ],
    "Cash": ["Operating Cash Flow", "Operating Cash Flow Margin", "Operating Cash Flow Growth"],
    "Financial Health": ["Current Ratio", "Debt-to-Equity", "Liabilities-to-Assets", "ROA"],
}

OVERVIEW_TABLES = {
    "All": [
        "Company",
        "Fiscal_Year",
        "Revenue",
        "Growth_Rate",
        "Operating_Margin_pct",
        "Net_Income_Margin_pct",
        "Operating_Expense_to_Revenue",
        "Operating_Cash_Flow_Margin_pct",
        "Current_ratio",
        "debt_to_equity_ratio",
        "ROA",
    ],
    "Growth": [
        "Company",
        "Fiscal_Year",
        "Revenue",
        "Growth_Rate",
        "Prior_Growth_Rate",
        "Growth_Differential",
        "Net_Income_Margin_pct",
    ],
    "Profitability": [
        "Company",
        "Fiscal_Year",
        "Gross_Margin_pct",
        "Operating_Margin_pct",
        "Net_Income_Margin_pct",
        "Net_Income_Growth",
        "Operating_Income_Growth",
    ],
    "Operations": [
        "Company",
        "Fiscal_Year",
        "Revenue",
        "Growth_Rate",
        "Operating_Expense_Growth",
        "Operating_Expense_to_Revenue",
        "Revenue_Growth_Minus_Opex_Growth",
    ],
    "Cash": [
        "Company",
        "Fiscal_Year",
        "Revenue",
        "Cash_Flow_from_Operating_Activities",
        "Operating_Cash_Flow_Margin_pct",
        "Operating_Cash_Flow_Growth",
        "Cash_Conversion_Ratio",
        "Free_Cash_Flow",
    ],
    "Financial Health": [
        "Company",
        "Fiscal_Year",
        "Current_ratio",
        "debt_to_equity_ratio",
        "Liabilities_to_Assets",
        "ROA",
        "ROE",
    ],
}

OVERVIEW_VIEW_KEYS = {
    "Growth": "company_performance",
    "Operations": "company_operations",
    "Cash": "company_cash_flow",
    "Financial Health": "company_financial_health",
    "Profitability": "performance",
}

PEER_METRICS = {
    "Revenue Growth": ("Growth_Rate", True, True),
    "Operating Margin": ("Operating_Margin_pct", True, True),
    "Net Income Margin": ("Net_Income_Margin_pct", True, True),
    "Operating Expense / Revenue": ("Operating_Expense_to_Revenue", False, True),
    "OCF Margin": ("Operating_Cash_Flow_Margin_pct", True, True),
    "Current Ratio": ("Current_ratio", True, False),
    "Debt-to-Equity": ("debt_to_equity_ratio", False, False),
    "ROA": ("ROA", True, True),
}


@st.cache_data(show_spinner="Loading operating views…")
def cached_views() -> dict[str, pd.DataFrame]:
    return load_views()


def slice_company(frame: pd.DataFrame, company: str) -> pd.DataFrame:
    if company == "All Companies" or frame.empty:
        return frame.copy()
    return frame.loc[frame["Company"] == company].copy()


def latest_year_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    latest = frame.groupby("Company")["Fiscal_Year"].transform("max")
    return frame.loc[frame["Fiscal_Year"] == latest].copy()


def slice_year(frame: pd.DataFrame, year_label: str) -> pd.DataFrame:
    if frame.empty or year_label == "All":
        return frame.copy()
    if year_label == "Latest":
        return latest_year_rows(frame)
    return frame.loc[frame["Fiscal_Year"] == int(year_label)].copy()


def _drop_overlapping(frame: pd.DataFrame, extra: pd.DataFrame) -> pd.DataFrame:
    overlap = [
        c
        for c in extra.columns
        if c not in ("Company", "Fiscal_Year") and c in frame.columns
    ]
    return extra.drop(columns=overlap, errors="ignore")


def overview_source(views: dict[str, pd.DataFrame], category: str, company: str, year_label: str) -> pd.DataFrame:
    if category == "All":
        frame = views["company_performance"].copy()
        extras = [
            views.get("performance"),
            views["company_operations"],
            views["company_cash_flow"],
            views["company_financial_health"],
        ]
        for extra in extras:
            if extra is None:
                continue
            frame = frame.merge(
                _drop_overlapping(frame, extra),
                on=["Company", "Fiscal_Year"],
                how="left",
            )
    else:
        key = OVERVIEW_VIEW_KEYS[category]
        if key not in views:
            key = "company_operations"
        frame = views[key].copy()
    frame = slice_year(slice_company(frame, company), year_label)
    return frame.sort_values(["Company", "Fiscal_Year"])


def kpi_source(views: dict[str, pd.DataFrame], company: str, year_label: str) -> pd.DataFrame:
    perf = views.get("performance", views["company_operations"])
    health = views["company_financial_health"]
    merged = perf.merge(health, on=["Company", "Fiscal_Year"], how="left", suffixes=("", "_h"))
    growth = views.get("company_performance")
    if growth is not None:
        merged = merged.merge(
            _drop_overlapping(merged, growth),
            on=["Company", "Fiscal_Year"],
            how="left",
        )
    merged = slice_company(merged, company)
    if year_label == "All":
        return merged
    if year_label == "Latest":
        return latest_year_rows(merged)
    return merged.loc[merged["Fiscal_Year"] == int(year_label)]


def is_single_snapshot(company: str, year_label: str) -> bool:
    return company != "All Companies" and year_label != "All"


def maybe_show_table(frame: pd.DataFrame, columns: list[str], company: str, year_label: str) -> None:
    if is_single_snapshot(company, year_label):
        return
    show_table(frame, columns)


def kpi_value(frame: pd.DataFrame, col: str, kind: str) -> str:
    series = frame[col].dropna() if col in frame.columns else pd.Series(dtype=float)
    if series.empty:
        return "—"
    value = series.median() if len(series) > 1 else series.iloc[0]
    if kind == "pct":
        return fmt_pct(value)
    if kind == "money":
        return fmt_money(value)
    return fmt_ratio(value)


def render_kpis(frame: pd.DataFrame, labels: list[str]) -> None:
    catalog = {
        "Revenue Growth": ("Growth_Rate", "pct"),
        "Growth Rate Change": ("Growth_Differential", "pct"),
        "Gross Margin": ("Gross_Margin_pct", "pct"),
        "Operating Margin": ("Operating_Margin_pct", "pct"),
        "Net Income Margin": ("Net_Income_Margin_pct", "pct"),
        "Net Income Growth": ("Net_Income_Growth", "pct"),
        "Operating Cash Flow Margin": ("Operating_Cash_Flow_Margin_pct", "pct"),
        "Current Ratio": ("Current_ratio", "ratio"),
        "Debt-to-Equity": ("debt_to_equity_ratio", "ratio"),
        "Operating Expense Growth": ("Operating_Expense_Growth", "pct"),
        "Operating Expense / Revenue": ("Operating_Expense_to_Revenue", "pct"),
        "Revenue Growth − OpEx Growth": ("Revenue_Growth_Minus_Opex_Growth", "pct"),
        "Operating Cash Flow": ("Cash_Flow_from_Operating_Activities", "money"),
        "Operating Cash Flow Growth": ("Operating_Cash_Flow_Growth", "pct"),
        "Liabilities-to-Assets": ("Liabilities_to_Assets", "pct"),
        "ROA": ("ROA", "pct"),
    }
    items = []
    for label in labels:
        col, kind = catalog[label]
        items.append((label, kpi_value(frame, col, kind)))
    kpi_cards(items)


def executive_page(views: dict[str, pd.DataFrame], company: str, year_label: str) -> None:
    st.title("Business Performance Overview")
    st.markdown(
        '<p class="subtitle">Cross-company analysis of growth, profitability, '
        "operating efficiency, cash generation, and financial health.</p>",
        unsafe_allow_html=True,
    )
    category = st.selectbox("Metric category", list(KPI_GROUPS.keys()), index=0, key="metric_category")
    frame = kpi_source(views, company, year_label)
    caption = (
        "Each company's most recent fiscal year."
        if company == "All Companies" and year_label == "Latest"
        else "All fiscal years across companies."
        if company == "All Companies" and year_label == "All"
        else "Values update with the company and fiscal-year filters."
    )
    st.caption(caption)
    render_kpis(frame, KPI_GROUPS[category])
    table = overview_source(views, category, company, year_label)
    maybe_show_table(table, OVERVIEW_TABLES[category], company, year_label)


def performance_page(views: dict[str, pd.DataFrame], company: str, year_label: str) -> None:
    page_intro(
        "Company Performance",
        "Evaluate whether the company is growing and whether growth is accelerating or slowing.",
        "company_performance",
    )
    data = slice_year(
        slice_company(views["company_performance"], company).sort_values(["Company", "Fiscal_Year"]),
        year_label,
    )
    snapshot = is_single_snapshot(company, year_label)
    if snapshot:
        render_kpis(kpi_source(views, company, year_label), KPI_GROUPS["Growth"])
    if not snapshot:
        c1, c2 = st.columns(2)
        with c1:
            metric_chart(data, "Growth_Rate", "Revenue growth by fiscal year", percent=True, year_label=year_label)
            compare = data.melt(
                id_vars=["Company", "Fiscal_Year"],
                value_vars=["Growth_Rate", "Prior_Growth_Rate"],
                var_name="Series",
                value_name="Rate",
            )
            compare["Series"] = compare["Series"].map(
                {"Growth_Rate": "Revenue growth", "Prior_Growth_Rate": "Prior growth rate"}
            )
            if year_label != "All":
                x_col = "Company" if company == "All Companies" else "Series"
                bar_title = (
                    "Growth rate vs prior growth rate — latest year"
                    if year_label == "Latest"
                    else f"Growth rate vs prior growth rate — FY{year_label}"
                )
                bar_chart(
                    compare,
                    "Rate",
                    bar_title,
                    percent=True,
                    x=x_col,
                    color="Series",
                    barmode="group",
                    showlegend=company == "All Companies",
                )
            elif company == "All Companies":
                metric_chart(data, "Prior_Growth_Rate", "Prior growth rate", percent=True, year_label=year_label)
            else:
                fig = px.line(
                    compare,
                    x="Fiscal_Year",
                    y="Rate",
                    color="Series",
                    markers=True,
                    title="Growth rate vs prior growth rate",
                    color_discrete_sequence=PALETTE,
                )
                fig.update_yaxes(tickformat=".0%", title="Rate")
                fig.update_xaxes(dtick=1, title="Fiscal Year")
                fig.update_layout(**CHART_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            metric_chart(
                data, "Growth_Differential", "Growth rate change (percentage points)", percent=True, year_label=year_label
            )
            metric_chart(data, "Net_Income_Margin_pct", "Net income margin trend", percent=True, year_label=year_label)

    show_table(
        data,
        [
            "Company",
            "Fiscal_Year",
            "Revenue",
            "Growth_Rate",
            "Prior_Growth_Rate",
            "Growth_Differential",
            "Net_Income_Margin_pct",
        ],
    )
    show_data_notes(notes.notes_for(notes.GROWTH, company), year_label)


def operations_page(views: dict[str, pd.DataFrame], company: str, year_label: str) -> None:
    page_intro(
        "Operating Efficiency & Cost Management",
        "Determine whether the company is scaling efficiently.",
        "company_operations",
    )
    data = slice_year(
        slice_company(views["company_operations"], company).sort_values(["Company", "Fiscal_Year"]),
        year_label,
    )
    kpi_frame = kpi_source(views, company, year_label)
    render_kpis(
        kpi_frame,
        [
            "Revenue Growth",
            "Operating Expense Growth",
            "Operating Expense / Revenue",
            "Revenue Growth − OpEx Growth",
        ],
    )
    st.caption(
        "Revenue growth − operating expense growth is a percentage-point difference, not an efficiency percentage."
    )
    if not is_single_snapshot(company, year_label):
        c1, c2 = st.columns(2)
        with c1:
            metric_chart(data, "Growth_Rate", "Revenue growth", percent=True, year_label=year_label)
            metric_chart(data, "Operating_Expense_Growth", "Operating expense growth", percent=True, year_label=year_label)
        with c2:
            metric_chart(
                data, "Operating_Expense_to_Revenue", "Operating expense / revenue trend", percent=True, year_label=year_label
            )
            metric_chart(
                data,
                "Revenue_Growth_Minus_Opex_Growth",
                "Revenue growth − operating expense growth (percentage points)",
                percent=True,
                year_label=year_label,
            )
    maybe_show_table(
        data,
        [
            "Company",
            "Fiscal_Year",
            "Revenue",
            "Growth_Rate",
            "Operating_Expense_Growth",
            "Operating_Expense_to_Revenue",
            "Revenue_Growth_Minus_Opex_Growth",
        ],
        company,
        year_label,
    )
    show_data_notes(notes.notes_for(notes.OPERATIONS, company), year_label)


def profitability_page(views: dict[str, pd.DataFrame], company: str, year_label: str) -> None:
    page_intro(
        "Profitability",
        "Determine whether revenue is translating into operating and net income.",
        "performance",
    )
    data = slice_year(
        slice_company(views.get("performance", views["company_operations"]), company).sort_values(
            ["Company", "Fiscal_Year"]
        ),
        year_label,
    )
    render_kpis(kpi_source(views, company, year_label), KPI_GROUPS["Profitability"])
    if not is_single_snapshot(company, year_label):
        c1, c2 = st.columns(2)
        with c1:
            metric_chart(data, "Gross_Margin_pct", "Gross margin trend", percent=True, year_label=year_label)
            metric_chart(data, "Net_Income_Margin_pct", "Net income margin trend", percent=True, year_label=year_label)
        with c2:
            metric_chart(data, "Operating_Margin_pct", "Operating margin trend", percent=True, year_label=year_label)
            metric_chart(data, "Net_Income_Growth", "Net income growth", percent=True, year_label=year_label)
    maybe_show_table(
        data,
        [
            "Company",
            "Fiscal_Year",
            "Gross_Margin_pct",
            "Operating_Margin_pct",
            "Net_Income_Margin_pct",
            "Net_Income_Growth",
        ],
        company,
        year_label,
    )
    show_data_notes(notes.notes_for(notes.PROFITABILITY, company), year_label)


def cash_page(views: dict[str, pd.DataFrame], company: str, year_label: str) -> None:
    page_intro(
        "Cash Flow & Cash Conversion",
        "Determine whether business performance is translating into operating cash generation.",
        "company_cash_flow",
    )
    data = slice_year(
        slice_company(views["company_cash_flow"], company).sort_values(["Company", "Fiscal_Year"]),
        year_label,
    )
    render_kpis(
        kpi_source(views, company, year_label),
        ["Operating Cash Flow", "Operating Cash Flow Margin", "Operating Cash Flow Growth"],
    )
    st.caption(
        "Positive operating cash flow does not automatically mean profitability is strong. "
        "Compare cash trends with net income on this page."
    )
    if not is_single_snapshot(company, year_label):
        c1, c2 = st.columns(2)
        with c1:
            metric_chart(data, "Cash_Flow_from_Operating_Activities", "Operating cash flow trend", year_label=year_label)
            metric_chart(data, "Operating_Cash_Flow_Growth", "Operating cash flow growth", percent=True, year_label=year_label)
        with c2:
            metric_chart(
                data, "Operating_Cash_Flow_Margin_pct", "Operating cash flow margin trend", percent=True, year_label=year_label
            )
            metric_chart(data, "Net_Income", "Net income (for comparison with cash)", year_label=year_label)
    maybe_show_table(
        data,
        [
            "Company",
            "Fiscal_Year",
            "Revenue",
            "Cash_Flow_from_Operating_Activities",
            "Operating_Cash_Flow_Margin_pct",
            "Operating_Cash_Flow_Growth",
        ],
        company,
        year_label,
    )
    show_data_notes(notes.notes_for(notes.CASH, company), year_label)


def health_page(views: dict[str, pd.DataFrame], company: str, year_label: str) -> None:
    page_intro(
        "Financial Health & Risk",
        "Evaluate liquidity, leverage, and financial flexibility.",
        "company_financial_health",
    )
    data = slice_year(
        slice_company(views["company_financial_health"], company).sort_values(["Company", "Fiscal_Year"]),
        year_label,
    )
    render_kpis(
        kpi_source(views, company, year_label),
        ["Current Ratio", "Debt-to-Equity", "Liabilities-to-Assets", "ROA"],
    )
    st.caption(
        "A current ratio below 1.0 is a signal that may warrant attention, not automatically a financial crisis."
    )
    if not is_single_snapshot(company, year_label):
        c1, c2 = st.columns(2)
        with c1:
            metric_chart(data, "Current_ratio", "Current ratio trend", year_label=year_label)
            metric_chart(data, "Liabilities_to_Assets", "Liabilities-to-assets trend", percent=True, year_label=year_label)
        with c2:
            metric_chart(data, "debt_to_equity_ratio", "Debt-to-equity trend", year_label=year_label)
            metric_chart(data, "ROA", "ROA trend", percent=True, year_label=year_label)
    maybe_show_table(
        data,
        [
            "Company",
            "Fiscal_Year",
            "Current_ratio",
            "debt_to_equity_ratio",
            "Liabilities_to_Assets",
            "ROA",
        ],
        company,
        year_label,
    )
    show_data_notes(notes.notes_for(notes.HEALTH, company), year_label)


def rankable_peer_metrics(frame: pd.DataFrame, fiscal_year: int) -> dict:
    subset = frame.loc[frame["Fiscal_Year"] == fiscal_year]
    return {
        label: spec
        for label, spec in PEER_METRICS.items()
        if spec[0] in subset.columns and subset[spec[0]].notna().any()
    }


def peer_page(views: dict[str, pd.DataFrame], company: str) -> None:
    page_intro(
        "Peer Performance Benchmarking",
        "Compare companies against each other on a selected operating or financial metric.",
        "peer_metrics",
    )
    frame = views["peer_metrics"]
    years = sorted(frame["Fiscal_Year"].dropna().unique().tolist(), reverse=True)
    default_year = 2025 if 2025 in years else years[0]
    c1, c2 = st.columns(2)
    year = c1.selectbox("Fiscal year", years, index=years.index(default_year))
    available = rankable_peer_metrics(frame, int(year))
    if not available:
        c2.selectbox("Metric", ["No rankable metrics"], disabled=True)
        st.info("No supporting data to rank companies for this fiscal year.")
        return
    metric_label = c2.selectbox("Metric", list(available.keys()), key=f"peer_metric_{int(year)}")
    companies = sorted(frame["Company"].unique().tolist())
    st.markdown("**Companies**")
    company_cols = st.columns(len(companies))
    selected = [
        name
        for i, name in enumerate(companies)
        if company_cols[i].checkbox(name, value=True, key=f"peer_company_{name}")
    ]
    if not selected:
        st.info("Select at least one company.")
        return
    col, higher_is_better, _pct = available[metric_label]
    ranked = rank_selected_metric(frame, int(year), col, higher_is_better)
    ranked = ranked.loc[ranked["Company"].isin(selected)]
    if ranked.empty:
        st.info("No supporting data to rank the selected companies on this metric.")
        return
    show_table(ranked, ["Rank", "Company", "Fiscal_Year", col])
    bar_chart(ranked, col, f"{metric_label} — FY{year}", percent=_pct)
    show_data_notes(notes.PEER, year)
    st.caption("Companies are ranked on the selected metric only. There is no composite winner score.")


def glossary_page() -> None:
    st.title("Glossary")
    st.markdown(
        '<p class="subtitle">Meanings for columns used in the analytics views. '
        "Calculated metrics show the same formulas as the app.</p>",
        unsafe_allow_html=True,
    )
    view_options = ["All views"] + glossary_notes.APP_VIEWS
    f1, f2, f3 = st.columns(3)
    with f1:
        view = st.selectbox("View", view_options, index=0, key="glossary_view")
    with f2:
        kind = st.selectbox("Metric type", ["All", "Source", "Calculated"], index=0, key="glossary_kind")
    scoped = glossary_notes.filter_terms(view=view, kind=kind)
    labels = ["All metrics"] + glossary_notes.metric_labels(scoped)
    if st.session_state.get("glossary_metric") not in labels:
        st.session_state["glossary_metric"] = "All metrics"
    with f3:
        metric = st.selectbox("Metric", labels, key="glossary_metric")
    search = st.text_input("Search", placeholder="Growth, margin, cash, rank…", key="glossary_search")

    rows = glossary_notes.filter_terms(view=view, kind=kind, search=search, metric=metric)
    st.caption(f"{len(rows)} metric{'s' if len(rows) != 1 else ''} match the filters.")
    if not rows:
        st.info("No metrics match these filters.")
        return

    if metric != "All metrics" and len(rows) == 1:
        item = rows[0]
        st.markdown(f"**{item['label']}**")
        st.write(item["meaning"])
        st.markdown(f"**Type:** {item['kind']}")
        st.markdown(f"**How it is calculated:** {item['calculation']}")

    st.dataframe(
        glossary_notes.terms_frame(rows),
        use_container_width=True,
        hide_index=True,
        height=min(720, 52 + 38 * max(len(rows), 4)),
    )


def attention_page(company: str) -> None:
    page_intro(
        "Management Attention",
        "Surface issues that would cause management to investigate, monitor, or ask a follow-up question. "
        "Favorable trends are noted for continued monitoring — they are not forced into problems.",
        "notebook interpretations",
    )
    alerts = notes.alerts_for(company)
    if not alerts:
        st.info("No management-attention items are recorded for this company.")
        return
    for alert in alerts:
        tag = alert["kind"]
        st.markdown(
            f"""
            <div class="alert">
              <div><strong>{alert["company"]} — {alert["area"]}</strong>
              <span class="tag tag-{tag}">{tag}</span></div>
              <p class="alert-k">Signal</p>
              <p>{alert["signal"]}</p>
              <p class="alert-k">Why it matters</p>
              <p>{alert["why"]}</p>
              <p class="alert-k">Management attention</p>
              <p>{alert["attention"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    inject_css()
    st.sidebar.markdown('<div class="brand">Internal analytics</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="brand-title">Business Performance Analytics</div>',
        unsafe_allow_html=True,
    )
    page = st.sidebar.radio("Navigation", PAGES, index=0)

    try:
        views = cached_views()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    if page == "Glossary":
        st.sidebar.caption("Filter metrics on the glossary page. Company and year do not apply here.")
        glossary_page()
        return

    companies = ["All Companies"] + sorted(
        views["company_performance"]["Company"].dropna().unique().tolist()
    )
    years = sorted(views["company_performance"]["Fiscal_Year"].dropna().unique().tolist())
    company = st.sidebar.selectbox("Company", companies, index=0)
    year_label = st.sidebar.selectbox(
        "Fiscal year",
        ["All"] + ["Latest"] + [str(y) for y in reversed(years)],
        index=0,
    )
    st.sidebar.caption("Operating review of six technology companies. Not a trading or investment tool.")

    if page == "Overview":
        executive_page(views, company, year_label)
    elif page == "Company Performance":
        performance_page(views, company, year_label)
    elif page == "Operations":
        operations_page(views, company, year_label)
    elif page == "Profitability":
        profitability_page(views, company, year_label)
    elif page == "Cash Flow":
        cash_page(views, company, year_label)
    elif page == "Financial Health":
        health_page(views, company, year_label)
    elif page == "Peer Benchmarking":
        peer_page(views, company)
    else:
        attention_page(company)


if __name__ == "__main__":
    main()
