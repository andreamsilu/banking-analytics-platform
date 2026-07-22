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
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
    .block-container { padding-top: 1rem; max-width: 1220px; }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
    }
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] p { color: #475569 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] * { color: #1f4e79 !important; }

    .period-banner, .exec-summary, .insight-box, .action-box {
        border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.85rem;
    }
    .period-banner { background:#f1f5f9; border:1px solid #cbd5e1; color:#334155; }
    .exec-summary { background:linear-gradient(90deg,#1f4e79,#2e75b6); color:#f8fafc; line-height:1.55; }
    .insight-box { background:#0f172a; border:1px solid #334155; color:#e2e8f0; }
    .action-box { background:#ffffff; border:1px solid #cbd5e1; color:#1e293b; border-left:5px solid #1f4e79; }
    .success-box { border-left-color:#2e7d32; }
    .watch-box { border-left-color:#f9a825; }
    .action-box.rec { border-left-color:#c62828; }
    .badge {
        display:inline-block; padding:0.15rem 0.55rem; border-radius:999px;
        font-size:0.75rem; font-weight:700; margin-top:0.35rem;
    }
    .badge-healthy { background:#e8f5e9; color:#1b5e20; }
    .badge-watch { background:#fff8e1; color:#f57f17; }
    .badge-attention { background:#ffebee; color:#b71c1c; }
    .badge-excellent { background:#e3f2fd; color:#0d47a1; }
    .badge-good { background:#e8f5e9; color:#2e7d32; }
    .score-card {
        background:#ffffff; border:1px solid #cbd5e1; border-radius:10px;
        padding:0.8rem; text-align:center; color:#1e293b;
    }
    h1,h2,h3 { color:#1f4e79; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading banking datasets...")
def get_datasets():
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
    arrow = "▲" if pct >= 0 else "▼"
    unit = " pp" if is_pp else "%"
    return f"{arrow} {abs(pct):.1f}{unit}"


def render_period_banner(data: dict) -> None:
    meta = du.reporting_period(data)
    note = (
        "Demo sample portfolio for executive presentation."
        if meta["is_sample"]
        else "Full synthetic portfolio (local analysis)."
    )
    st.markdown(
        f"""
        <div class="period-banner">
            <strong>Reporting period:</strong> {meta['period_label']}
            &nbsp;·&nbsp; <strong>Currency:</strong> {meta['currency']}
            &nbsp;·&nbsp; <strong>View:</strong> {meta['view_label']} ({meta['customer_count']} customers)
            <br/><span style="color:#64748b;">{note}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_ribbon(ribbon: list[dict]) -> None:
    """CEO KPI ribbon with value, MoM, and status badge."""
    # Two rows of 4 for readability on executive screens.
    for start in (0, 4):
        cols = st.columns(4)
        for col, item in zip(cols, ribbon[start : start + 4]):
            mom = format_mom(item["mom_pct"], item.get("mom_is_pp", False))
            # Streamlit delta: negative MoM for NPL is good visually if we invert?
            # Keep raw signed change; badge carries judgment.
            delta_color = "normal"
            if item["key"] in {"npl_ratio"} and item["mom_pct"] > 0:
                delta_color = "inverse"
            with col:
                st.metric(
                    item["label"],
                    item["display"],
                    delta=mom,
                    delta_color=delta_color,
                    help=item.get("help"),
                )
                st.markdown(
                    f'<span class="badge {status_badge_class(item["status"])}">Status: {item["status"]}</span>',
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
    panel = bi.build_action_panel(data, ribbon)
    scorecards = bi.build_scorecards(data, ribbon)
    actions = bi.build_management_actions(data)

    st.title("Executive Overview")
    st.caption("CEO / Board decision dashboard — what happened, why it matters, what to do next.")
    render_period_banner(data)

    st.subheader("KPI Ribbon")
    render_kpi_ribbon(ribbon)

    st.subheader("Executive Summary")
    st.markdown(f'<div class="exec-summary">{summary}</div>', unsafe_allow_html=True)

    st.subheader("Executive Action Panel")
    render_action_panel(panel)

    st.subheader("Executive Scorecards")
    render_scorecards(scorecards)

    st.divider()
    st.subheader("Evidence charts")
    col1, col2 = st.columns(2)
    txn_insights = bi.build_transaction_insights(data["transactions"])
    with col1:
        st.plotly_chart(bi.create_channel_chart_with_target(data["transactions"]), use_container_width=True)
        render_insight_block(
            finding=txn_insights["channel"]["finding"],
            impact=txn_insights["channel"]["impact"],
            recommendation=txn_insights["channel"]["recommendation"],
        )
    with col2:
        loans_customers = data["loans"].merge(
            data["customers"][["customer_id", "region"]], on="customer_id", how="left"
        )
        st.plotly_chart(bi.create_repayment_chart_with_target(data["loans"]), use_container_width=True)
        loan_insights = bi.build_loan_insights(data["loans"], loans_customers)
        render_insight_block(
            finding=loan_insights["repayment"]["finding"],
            impact=loan_insights["repayment"]["impact"],
            recommendation=loan_insights["repayment"]["recommendation"],
        )

    st.divider()
    render_management_actions(actions)


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
    c4.metric("NPL proxy (late+default)", f"{credit['at_risk_rate']:.1f}%")

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


def main() -> None:
    st.sidebar.title("🏦 Banking Executive BI")
    st.sidebar.markdown("**Decision-support platform**")
    st.sidebar.caption("Built for CEO · CFO · COO · Head of Retail · Head of Risk")

    page = st.sidebar.radio(
        "Navigate",
        [
            "📊 Executive Overview",
            "👥 Customer Analytics",
            "💳 Transaction Analytics",
            "🏦 Loan Portfolio Analytics",
        ],
    )

    st.sidebar.divider()
    st.sidebar.markdown("**Decision lens**")
    st.sidebar.markdown(
        "1. What happened?\n"
        "2. Why does it matter?\n"
        "3. What should management do next?"
    )

    try:
        data = get_datasets()
    except du.DataLoadError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:  # pragma: no cover
        st.error(f"Unable to load dashboard data: {exc}")
        st.stop()

    if page.startswith("📊"):
        page_executive_overview(data)
    elif page.startswith("👥"):
        page_customers(data)
    elif page.startswith("💳"):
        page_payments(data)
    else:
        page_credit(data)


if __name__ == "__main__":
    main()
