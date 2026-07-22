"""
Banking Analytics Intelligence Platform — Executive Decision-Support Dashboard.

Transforms banking analytics into a CEO/Board decision platform:
KPI ribbon, executive summary, action panels, chart-level recommendations,
scorecards, and prioritized management actions.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import dashboard_utils as du  # noqa: E402
from src import executive_bi as bi  # noqa: E402

du = importlib.reload(du)
bi = importlib.reload(bi)

st.set_page_config(
    page_title="Banking Executive BI Platform",
    page_icon=str(PROJECT_ROOT / "dashboards" / "assets" / "bank_icon.svg"),
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
    .block-container { padding-top: 1rem; max-width: 1220px; }

    /* ---------- Sidebar shell ---------- */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.25);
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 0.75rem;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 0.5rem;
    }

    .sidebar-brand {
        background: linear-gradient(145deg, #1f4e79 0%, #2e75b6 100%);
        color: #f8fafc;
        border-radius: 14px;
        padding: 1rem 1rem 0.95rem;
        margin: 0 0 1rem 0;
        box-shadow: 0 8px 20px rgba(31, 78, 121, 0.25);
    }
    .sidebar-brand .brand-kicker {
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        opacity: 0.85;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .sidebar-brand .brand-title {
        font-size: 1.15rem;
        font-weight: 700;
        line-height: 1.25;
        margin: 0;
    }
    .sidebar-brand .brand-sub {
        font-size: 0.8rem;
        opacity: 0.9;
        margin-top: 0.35rem;
        line-height: 1.35;
    }

    .sidebar-section-label {
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-weight: 700;
        color: #64748b;
        margin: 0.35rem 0 0.55rem 0;
    }

    .sidebar-card {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 12px;
        padding: 0.75rem 0.85rem;
        margin: 0.65rem 0 0.85rem 0;
        color: inherit;
    }
    .sidebar-card strong {
        display: block;
        margin-bottom: 0.35rem;
        font-size: 0.85rem;
    }
    .sidebar-card p, .sidebar-card li {
        font-size: 0.8rem;
        line-height: 1.45;
        margin: 0;
        opacity: 0.92;
    }

    /* Navigation buttons styled as sidebar nav items */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        justify-content: flex-start;
        text-align: left;
        font-weight: 500;
        transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: rgba(46, 117, 182, 0.14);
        border-color: rgba(46, 117, 182, 0.45);
        transform: translateX(2px);
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
        background: rgba(31, 78, 121, 0.22);
        border-color: #2e75b6;
        box-shadow: inset 3px 0 0 #1f4e79;
        font-weight: 600;
    }

    /* Legacy radio styles kept as fallback */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.45rem;
        display: flex;
        flex-direction: column;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 10px;
        padding: 0.7rem 0.85rem !important;
        margin: 0 !important;
        transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
        cursor: pointer;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(46, 117, 182, 0.14);
        border-color: rgba(46, 117, 182, 0.45);
        transform: translateX(2px);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: rgba(31, 78, 121, 0.18);
        border-color: #2e75b6;
        box-shadow: inset 3px 0 0 #1f4e79;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 0.92rem !important;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        display: none;
    }

    /* Metric cards: inherit theme colors so Light/Dark both stay readable */
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 10px;
        padding: 0.55rem 0.75rem 0.65rem;
        margin-bottom: 0.15rem;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.82rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        line-height: 1.2 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-size: 0.78rem !important;
    }

    .period-banner, .exec-summary, .insight-box, .action-box, .alert-card, .npl-callout, .app-footer {
        border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.85rem;
    }
    .period-banner {
        background: rgba(128, 128, 128, 0.12);
        border: 1px solid rgba(128, 128, 128, 0.25);
        color: inherit;
        line-height: 1.55;
    }
    .exec-summary {
        background: linear-gradient(90deg, #1f4e79, #2e75b6);
        color: #f8fafc;
        line-height: 1.55;
    }
    .insight-box {
        background: rgba(31, 78, 121, 0.14);
        border: 1px solid rgba(31, 78, 121, 0.35);
        color: inherit;
    }
    .action-box {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.25);
        color: inherit;
        border-left: 5px solid #1f4e79;
    }
    .success-box { border-left-color: #2e7d32; }
    .watch-box { border-left-color: #f9a825; }
    .action-box.rec { border-left-color: #c62828; }
    .badge {
        display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px;
        font-size: 0.75rem; font-weight: 700; margin-top: 0.25rem;
    }
    .badge-healthy { background: #e8f5e9; color: #1b5e20; }
    .badge-watch { background: #fff8e1; color: #f57f17; }
    .badge-attention { background: #ffebee; color: #b71c1c; }
    .badge-excellent { background: #e3f2fd; color: #0d47a1; }
    .badge-good { background: #e8f5e9; color: #2e7d32; }
    .score-card {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 10px;
        padding: 0.8rem;
        text-align: center;
        color: inherit;
    }
    .npl-callout {
        background: #ffebee;
        border: 1px solid #ef9a9a;
        color: #b71c1c;
        line-height: 1.5;
    }
    .alert-card {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-left: 5px solid #64748b;
        color: inherit;
        min-height: 9.5rem;
    }
    .alert-card.critical { border-left-color: #c62828; }
    .alert-card.positive { border-left-color: #2e7d32; }
    .alert-card.watch { border-left-color: #f9a825; }
    .alert-card .alert-area {
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.04em;
        text-transform: uppercase; color: #64748b; margin-bottom: 0.35rem;
    }
    .alert-card .alert-tone { font-weight: 700; margin-bottom: 0.35rem; }
    .alert-card .alert-rec { margin-top: 0.55rem; font-size: 0.9rem; }
    .app-footer {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.22);
        color: inherit;
        text-align: center;
        font-size: 0.85rem;
        line-height: 1.55;
        margin-top: 1.25rem;
    }
    .app-footer strong { display: block; margin-bottom: 0.25rem; }

    /* Sidebar filter section headers */
    section[data-testid="stSidebar"] h3 {
        font-size: 0.72rem !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-weight: 700 !important;
        color: #64748b !important;
        margin-top: 0.5rem !important;
    }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading H1 2026 banking datasets...")
def get_datasets():
    """Load datasets sliced to the closed Jan–Jun 2026 reporting window."""
    return du.load_data()


def status_badge_class(status: str) -> str:
    status_l = status.lower()
    if "excellent" in status_l:
        return "badge-excellent"
    if "healthy" in status_l or "good" in status_l:
        return "badge-healthy"
    if "watch" in status_l:
        return "badge-watch"
    return "badge-attention"


def format_mom(pct: float, is_pp: bool = False) -> str:
    """Format MoM change for executives: ↑ 4.0% vs previous period."""
    arrow = "↑" if pct >= 0 else "↓"
    unit = " pp" if is_pp else "%"
    return f"{arrow} {abs(pct):.1f}{unit} vs previous period"


def render_period_banner(data: dict) -> None:
    meta = du.reporting_period(data)
    st.markdown(
        f"""
        <div class="period-banner">
            <strong>Reporting period:</strong> {meta['period_label']}
            &nbsp;·&nbsp; <strong>Window:</strong> {meta['window_note']}
            &nbsp;·&nbsp; <strong>Currency:</strong> {meta['currency']}
            &nbsp;·&nbsp; <strong>Data layer:</strong> {meta['view_label']}
            &nbsp;·&nbsp; <strong>Customers:</strong> {meta['customer_count']}
            <br/><strong>Last refresh:</strong> {meta['last_refresh']}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_ribbon(ribbon: list[dict]) -> None:
    """CEO KPI ribbon with compact cards, MoM context, and status badges."""
    for start in (0, 4):
        cols = st.columns(4)
        for col, item in zip(cols, ribbon[start : start + 4]):
            mom = format_mom(item["mom_pct"], item.get("mom_is_pp", False))
            delta_color = "normal"
            if item["key"] == "npl_ratio" and item["mom_pct"] > 0:
                delta_color = "inverse"
            with col:
                st.metric(
                    f"{item.get('icon', '')} {item['label']}".strip(),
                    item["display"],
                    delta=mom,
                    delta_color=delta_color,
                    help=item.get("help"),
                )
                st.markdown(
                    f'<span class="badge {status_badge_class(item["status"])}">Status: {item["status"]}</span>',
                    unsafe_allow_html=True,
                )


def render_npl_callout(ribbon: list[dict]) -> None:
    """Surface NPL threshold breach with an explicit management action."""
    npl = next((item for item in ribbon if item["key"] == "npl_ratio"), None)
    if not npl:
        return
    threshold = npl.get("threshold", bi.TARGET_NPL_RATIO)
    if npl["value"] <= threshold:
        return
    st.markdown(
        f"""
        <div class="npl-callout">
            <strong>NPL Ratio {npl['display']}</strong> — above recommended threshold of {threshold:.0f}%.<br/>
            <strong>Action:</strong> {npl.get('action', 'Strengthen credit monitoring and collection strategies.')}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_business_alerts(alerts: list[dict]) -> None:
    cols = st.columns(len(alerts))
    for col, alert in zip(cols, alerts):
        with col:
            st.markdown(
                f"""
                <div class="alert-card {alert['severity']}">
                    <div class="alert-area">{alert['area']}</div>
                    <div class="alert-tone">{alert['tone']}</div>
                    <div>{alert['headline']}</div>
                    <div class="alert-rec"><strong>Recommendation:</strong> {alert['recommendation']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_app_footer() -> None:
    st.markdown(
        """
        <div class="app-footer">
            <strong>Tanzania Banking Intelligence Platform</strong>
            Built with Python · Pandas · Streamlit · Plotly<br/>
            Executive analytics for customer, payments, and credit portfolio monitoring
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_block(finding: str, impact: str | None, recommendation: str) -> None:
    impact_html = f"<br/><strong>Business impact:</strong> {impact}" if impact else ""
    st.markdown(
        f"""
        <div class="insight-box">
            <strong>Finding:</strong> {finding}{impact_html}<br/>
            <strong>Recommended action:</strong> {recommendation}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_panel(panel: dict[str, list[str]]) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="action-box success-box"><strong>SUCCESS</strong></div>', unsafe_allow_html=True)
        for item in panel["success"]:
            st.markdown(f"- {item}")
    with c2:
        st.markdown('<div class="action-box watch-box"><strong>WATCHLIST</strong></div>', unsafe_allow_html=True)
        for item in panel["watchlist"]:
            st.markdown(f"- {item}")
    with c3:
        st.markdown('<div class="action-box rec"><strong>RECOMMENDED ACTIONS</strong></div>', unsafe_allow_html=True)
        for item in panel["actions"]:
            st.markdown(f"- {item}")


def render_scorecards(scorecards: list[dict[str, str]]) -> None:
    cols = st.columns(len(scorecards))
    for col, card in zip(cols, scorecards):
        with col:
            st.markdown(
                f"""
                <div class="score-card">
                    <div style="color:#64748b;font-size:0.8rem;font-weight:700;">{card['area']}</div>
                    <div style="margin-top:0.35rem;">
                        <span class="badge {status_badge_class(card['status'])}">{card['status']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_management_actions(actions: list[dict[str, str]]) -> None:
    st.subheader("Top 5 Recommended Actions")
    st.caption("Prioritized for CEO, CFO, COO, Head of Retail, and Head of Risk.")
    rows = []
    for action in actions:
        rows.append(
            {
                "Priority": action["priority"],
                "Business Area": action["area"],
                "Recommendation": action["recommendation"],
                "Expected Benefit": action["benefit"],
                "Timeline": action["timeline"],
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def multiselect_all(label: str, options: list, key: str) -> list:
    options = sorted(options)
    mode = st.sidebar.selectbox(label, ["All"] + options, key=f"{key}_mode")
    return options if mode == "All" else [mode]


def page_executive_overview(data: dict) -> None:
    ribbon = bi.build_kpi_ribbon(data)
    summary = bi.build_executive_summary_text(data, ribbon)
    alerts = bi.build_business_alerts(data, ribbon)
    actions = bi.build_management_actions(data)
    trend_fig = bi.create_monthly_performance_trend(data)

    st.title("Executive Overview")
    st.caption(
        "CEO / Board decision dashboard for H1 2026 (1 Jan – 30 Jun) — "
        "what happened, why it matters, what to do next."
    )
    render_period_banner(data)

    st.subheader("KPI Ribbon")
    render_kpi_ribbon(ribbon)
    render_npl_callout(ribbon)

    st.subheader("Business Health Summary")
    st.markdown(f'<div class="exec-summary">{summary}</div>', unsafe_allow_html=True)

    st.subheader("Monthly Performance Trend")
    st.plotly_chart(trend_fig, use_container_width=True)

    st.subheader("Critical Business Alerts")
    render_business_alerts(alerts)

    render_management_actions(actions)
    render_app_footer()


def page_customers(data: dict) -> None:
    customers = data["customers"]
    accounts = data["accounts"]

    st.sidebar.subheader("Customer filters")
    regions = multiselect_all("Region", customers["region"].unique().tolist(), "c_region")
    genders = multiselect_all("Gender", customers["gender"].unique().tolist(), "c_gender")
    types = multiselect_all("Customer type", customers["customer_type"].unique().tolist(), "c_type")

    filtered = du.filter_customers(customers, regions=regions, genders=genders, customer_types=types)
    if filtered.empty:
        st.warning("No customers match the selected filters.")
        return

    ids = set(filtered["customer_id"])
    filtered_accounts = accounts[accounts["customer_id"].isin(ids)]
    profile = du.enrich_customer_value(filtered, filtered_accounts)
    insights = bi.build_customer_insights(filtered, filtered_accounts)
    charts = du.create_customer_charts(filtered, profile)

    st.title("Customer Analytics")
    render_period_banner(data)
    st.caption(f"Showing **{len(filtered):,}** of **{len(customers):,}** customers.")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts["region"], use_container_width=True)
        render_insight_block(insights["region"]["finding"], insights["region"]["impact"], insights["region"]["recommendation"])
        st.plotly_chart(charts["age_group"], use_container_width=True)
        render_insight_block(insights["age"]["finding"], insights["age"]["impact"], insights["age"]["recommendation"])
    with col2:
        st.plotly_chart(charts["segment_distribution"], use_container_width=True)
        render_insight_block(insights["segment"]["finding"], insights["segment"]["impact"], insights["segment"]["recommendation"])
        st.plotly_chart(charts["occupation"], use_container_width=True)
        render_insight_block(insights["occupation"]["finding"], insights["occupation"]["impact"], insights["occupation"]["recommendation"])

    st.plotly_chart(charts["balance_by_type"], use_container_width=True)
    render_insight_block(insights["value"]["finding"], insights["value"]["impact"], insights["value"]["recommendation"])

    st.divider()
    render_management_actions(bi.build_management_actions(data))


def page_payments(data: dict) -> None:
    transactions = data["transactions"]
    min_date = transactions["transaction_date"].min().date()
    max_date = transactions["transaction_date"].max().date()

    st.sidebar.subheader("Payment filters")
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    regions = multiselect_all("Region", transactions["region"].dropna().unique().tolist(), "p_region")
    channels = multiselect_all("Channel", transactions["channel"].unique().tolist(), "p_channel")
    types = multiselect_all("Transaction type", transactions["transaction_type"].unique().tolist(), "p_type")

    parsed = None
    if isinstance(date_range, tuple) and len(date_range) == 2:
        parsed = (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))

    filtered = du.filter_transactions(
        transactions, date_range=parsed, regions=regions, channels=channels, transaction_types=types
    )
    if filtered.empty:
        st.warning("No transactions match the selected filters.")
        return

    insights = bi.build_transaction_insights(filtered)
    charts = du.create_transaction_charts(filtered)

    # Regional value chart
    regional_value = (
        filtered.groupby("region", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    )
    region_fig = du.apply_chart_theme(
        px.bar(
            regional_value,
            x="region",
            y="amount",
            color="region",
            title="Which regions generate the most transaction value?",
            labels={"amount": "Transaction Value (TZS)"},
        ),
        subtitle="Concentration of payment value across Tanzania regions.",
    )
    region_fig = bi.annotate_bar_extremes(region_fig, regional_value, "region", "amount")

    st.title("Transaction Analytics")
    render_period_banner(data)
    st.caption(f"Showing **{len(filtered):,}** of **{len(transactions):,}** transactions.")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(bi.create_channel_chart_with_target(filtered), use_container_width=True)
        render_insight_block(insights["channel"]["finding"], insights["channel"]["impact"], insights["channel"]["recommendation"])
        st.plotly_chart(charts["volume_trend"], use_container_width=True)
        render_insight_block(insights["trend"]["finding"], insights["trend"]["impact"], insights["trend"]["recommendation"])
    with col2:
        st.plotly_chart(charts["transaction_type"], use_container_width=True)
        render_insight_block(insights["type"]["finding"], insights["type"]["impact"], insights["type"]["recommendation"])
        st.plotly_chart(charts["channel_performance"], use_container_width=True)
        render_insight_block(
            insights["value_channel"]["finding"],
            insights["value_channel"]["impact"],
            insights["value_channel"]["recommendation"],
        )

    st.plotly_chart(region_fig, use_container_width=True)
    render_insight_block(insights["region"]["finding"], insights["region"]["impact"], insights["region"]["recommendation"])

    st.divider()
    render_management_actions(bi.build_management_actions(data))


def page_credit(data: dict) -> None:
    loans = data["loans"]
    customers = data["customers"]

    st.sidebar.subheader("Credit filters")
    regions = multiselect_all("Region", customers["region"].unique().tolist(), "l_region")
    loan_types = multiselect_all("Loan type", loans["loan_type"].unique().tolist(), "l_type")
    risks = multiselect_all("Risk category", loans["risk_category"].unique().tolist(), "l_risk")

    filtered, merged = du.filter_loans(
        loans, customers, regions=regions, loan_types=loan_types, risk_categories=risks
    )
    if filtered.empty:
        st.warning("No loans match the selected filters.")
        return

    insights = bi.build_loan_insights(filtered, merged)
    charts = du.create_loan_charts(filtered, merged)

    st.title("Loan Portfolio Analytics")
    render_period_banner(data)
    st.caption(f"Showing **{len(filtered):,}** of **{len(loans):,}** loans.")

    credit = du.calculate_credit_health(filtered)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("On-time repayment", f"{credit['on_time_rate']:.1f}%")
    c2.metric("Watchlist (late)", f"{credit['watchlist_rate']:.1f}%")
    c3.metric("Default rate", f"{credit['default_rate']:.1f}%")
    c4.metric("NPL ratio (late+default)", f"{credit['at_risk_rate']:.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts["loan_products"], use_container_width=True)
        render_insight_block(insights["products"]["finding"], insights["products"]["impact"], insights["products"]["recommendation"])
        st.plotly_chart(bi.create_repayment_chart_with_target(filtered), use_container_width=True)
        render_insight_block(insights["repayment"]["finding"], insights["repayment"]["impact"], insights["repayment"]["recommendation"])
    with col2:
        st.plotly_chart(charts["risk_distribution"], use_container_width=True)
        render_insight_block(insights["risk"]["finding"], insights["risk"]["impact"], insights["risk"]["recommendation"])
        st.plotly_chart(bi.create_default_by_region_chart(merged), use_container_width=True)
        render_insight_block(insights["region"]["finding"], insights["region"]["impact"], insights["region"]["recommendation"])

    st.plotly_chart(charts["loan_amount_distribution"], use_container_width=True)
    render_insight_block(insights["size"]["finding"], insights["size"]["impact"], insights["size"]["recommendation"])

    st.divider()
    render_management_actions(bi.build_management_actions(data))


NAV_PAGES = [
    {
        "key": "executive",
        "label": "Executive Overview",
        "icon": ":material/monitoring:",
    },
    {
        "key": "customers",
        "label": "Customer Analytics",
        "icon": ":material/groups:",
    },
    {
        "key": "transactions",
        "label": "Transaction Analytics",
        "icon": ":material/payments:",
    },
    {
        "key": "loans",
        "label": "Loan Portfolio Analytics",
        "icon": ":material/account_balance:",
    },
]


def render_sidebar_nav() -> str:
    """Render Material-icon sidebar navigation and return the selected page key."""
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "executive"

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-kicker">Tanzania Banking Intelligence</div>
            <p class="brand-title">Executive BI Platform</p>
            <div class="brand-sub">H1 2026 · Decision support for CEO · CFO · COO · Retail · Risk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)

    for item in NAV_PAGES:
        is_active = st.session_state.nav_page == item["key"]
        clicked = st.sidebar.button(
            item["label"],
            key=f"nav_{item['key']}",
            icon=item["icon"],
            type="primary" if is_active else "secondary",
            use_container_width=True,
        )
        if clicked:
            st.session_state.nav_page = item["key"]
            st.rerun()

    st.sidebar.markdown('<div class="sidebar-section-label">Quick guide</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        """
        <div class="sidebar-card">
            <strong>Decision lens</strong>
            <p>1. KPI monitoring<br/>2. Business health summary<br/>3. Alerts &amp; recommended actions</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        """
        <div class="sidebar-card">
            <strong>Theme</strong>
            <p>Switch Light / Dark via the app menu → Settings → Theme.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.session_state.nav_page


def main() -> None:
    page = render_sidebar_nav()

    try:
        data = get_datasets()
    except du.DataLoadError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:  # pragma: no cover
        st.error(f"Unable to load dashboard data: {exc}")
        st.stop()

    if page == "executive":
        page_executive_overview(data)
    elif page == "customers":
        page_customers(data)
    elif page == "transactions":
        page_payments(data)
    else:
        page_credit(data)

    if page != "executive":
        render_app_footer()


if __name__ == "__main__":
    main()
