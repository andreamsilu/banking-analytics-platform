"""
Banking Analytics Intelligence Platform — Streamlit Dashboard.

Board-ready views for bank owners: clear decisions, traffic-light KPIs,
and plain-language credit and payments insights.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import dashboard_utils as du  # noqa: E402

du = importlib.reload(du)

st.set_page_config(
    page_title="Banking Analytics Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

BANKING_CSS = """
<style>
    .block-container { padding-top: 1.1rem; max-width: 1180px; }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 0.85rem 1rem;
    }
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"],
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] p {
        color: #475569 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
        color: #1f4e79 !important;
    }

    .story-headline {
        font-size: 1.12rem;
        line-height: 1.55;
        color: #f8fafc;
        background: linear-gradient(90deg, #1f4e79 0%, #2e75b6 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin-bottom: 0.85rem;
    }
    .period-banner {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        color: #334155;
        margin-bottom: 0.9rem;
        font-size: 0.95rem;
    }
    .decision-card {
        border-radius: 10px;
        padding: 0.9rem 1rem;
        border: 1px solid #cbd5e1;
        background: #ffffff;
        color: #1e293b;
        min-height: 150px;
    }
    .decision-success { border-left: 5px solid #2e7d32; }
    .decision-risk { border-left: 5px solid #c62828; }
    .decision-action { border-left: 5px solid #1f4e79; }
    .decision-type {
        font-size: 0.75rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        font-weight: 700;
        color: #64748b;
        margin-bottom: 0.25rem;
    }
    h1, h2, h3 { color: #1f4e79; }
</style>
"""
st.markdown(BANKING_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading banking datasets...")
def get_datasets():
    """Cache processed datasets for responsive dashboard interactions."""
    return du.load_data()


def render_period_banner(data: dict) -> None:
    """Show reporting period and portfolio view for bank owners."""
    meta = du.reporting_period(data)
    disclaimer = (
        "Demo sample for portfolio presentation — not the full production book."
        if meta["is_sample"]
        else "Full synthetic portfolio for local analysis."
    )
    st.markdown(
        f"""
        <div class="period-banner">
            <strong>Reporting period:</strong> {meta['period_label']}
            &nbsp;·&nbsp; <strong>Currency:</strong> {meta['currency']}
            &nbsp;·&nbsp; <strong>View:</strong> {meta['view_label']}
            ({meta['customer_count']} customers)
            <br/><span style="color:#64748b;">{disclaimer}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_story_headline(text: str) -> None:
    """Display the page-level narrative hook."""
    st.markdown(f'<div class="story-headline">{text}</div>', unsafe_allow_html=True)


def render_board_decisions(decisions: list[dict]) -> None:
    """Render three board decisions: success, risk, action."""
    st.subheader("What the board should know this month")
    cols = st.columns(3)
    style_map = {
        "Success": "decision-success",
        "Risk": "decision-risk",
        "Action": "decision-action",
    }
    for column, decision in zip(cols, decisions):
        css = style_map.get(decision["type"], "")
        column.markdown(
            f"""
            <div class="decision-card {css}">
                <div class="decision-type">{decision['type']} · {decision['owner']}</div>
                <strong>{decision['title']}</strong>
                <p style="margin-top:0.45rem; margin-bottom:0; color:#334155;">{decision['detail']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metric_row(
    metrics: list[tuple[str, str]],
    help_texts: list[str] | None = None,
    deltas: list[str | None] | None = None,
) -> None:
    """Render KPI cards with optional status deltas."""
    columns = st.columns(len(metrics))
    for index, (column, (label, value)) in enumerate(zip(columns, metrics)):
        help_text = help_texts[index] if help_texts and index < len(help_texts) else None
        delta = deltas[index] if deltas and index < len(deltas) else None
        column.metric(label, value, delta=delta, help=help_text)


def status_delta(metric_key: str, value: float) -> str:
    """Format traffic-light status text for Streamlit metric deltas."""
    _, message = du.kpi_status(metric_key, value)
    return message


def multiselect_with_all(label: str, options: list, key: str) -> list:
    """Owner-friendly multiselect that defaults to All."""
    options = sorted(options)
    choice = st.sidebar.selectbox(
        label,
        ["All"] + options,
        key=f"{key}_mode",
    )
    if choice == "All":
        return options
    return [choice]


def page_board_overview(data: dict) -> None:
    """Board overview: decisions first, then a few proof metrics and charts."""
    story = du.build_executive_story(data)
    kpis = story["kpis"]
    decisions = du.build_board_decisions(data)

    st.title("Board Overview")
    render_period_banner(data)
    render_story_headline(story["headline"])
    render_board_decisions(decisions)

    st.divider()
    st.subheader("Performance snapshot")
    st.caption("Four numbers every bank owner should check first.")

    render_metric_row(
        [
            ("Customers", f"{kpis['total_customers']:,}"),
            ("Payment value", du.format_tzs(kpis["total_transaction_value"])),
            ("Loan book", du.format_tzs(kpis["total_loan_portfolio"])),
            ("% on phone/online", f"{kpis['digital_share']:.1f}%"),
        ],
        help_texts=[
            "Total customers in this portfolio view.",
            "Total money moved through transactions.",
            "Total lending exposure.",
            "Share of transactions on Mobile, USSD, or Internet Banking.",
        ],
        deltas=[None, None, None, status_delta("digital_share", kpis["digital_share"])],
    )

    render_metric_row(
        [
            ("On-time repayment", f"{kpis['on_time_rate']:.1f}%"),
            ("Watchlist (late)", f"{kpis['watchlist_rate']:.1f}%"),
            ("Default rate", f"{kpis['default_rate']:.1f}%"),
            ("Premium customers", f"{kpis['premium_share']:.1f}%"),
        ],
        help_texts=[
            "Loans currently repaying on schedule.",
            "Late loans — early warning, not yet default.",
            "Loans already in default status.",
            "Share of customers in the Premium service tier.",
        ],
        deltas=[
            status_delta("on_time_rate", kpis["on_time_rate"]),
            status_delta("watchlist_rate", kpis["watchlist_rate"]),
            status_delta("default_rate", kpis["default_rate"]),
            None,
        ],
    )

    with st.expander("Key takeaways and watchlist", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Key takeaways**")
            for bullet in story["bullets"]:
                st.markdown(f"- {bullet}")
        with col2:
            st.markdown("**Watchlist**")
            for bullet in story["watchouts"]:
                st.markdown(f"- {bullet}")

    st.divider()
    st.subheader("Two charts that explain the story")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(du.create_channel_usage_chart(data["transactions"]), use_container_width=True)
        st.caption(
            f"**Decision:** Protect {story['top_channel']} reliability — it already carries "
            f"{story['channel_share']:.0f}% of payments."
        )
    with col2:
        st.plotly_chart(
            du.create_loan_charts(
                data["loans"],
                data["loans"].merge(data["customers"][["customer_id", "region"]], on="customer_id", how="left"),
            )["repayment_status"],
            use_container_width=True,
        )
        st.caption(
            f"**Decision:** Keep collections focused — defaults are {kpis['default_rate']:.1f}% "
            f"and late loans are {kpis['watchlist_rate']:.1f}%."
        )


def page_customer_analytics(data: dict) -> None:
    """Customer story for growth and value concentration."""
    customers = data["customers"]
    accounts = data["accounts"]

    st.sidebar.subheader("Customer filters")
    selected_regions = multiselect_with_all("Region", customers["region"].unique().tolist(), "cust_region")
    selected_genders = multiselect_with_all("Gender", customers["gender"].unique().tolist(), "cust_gender")
    selected_types = multiselect_with_all(
        "Customer type", customers["customer_type"].unique().tolist(), "cust_type"
    )

    filtered_customers = du.filter_customers(
        customers, regions=selected_regions, genders=selected_genders, customer_types=selected_types
    )
    if filtered_customers.empty:
        st.warning("No customers match the selected filters.")
        return

    customer_ids = set(filtered_customers["customer_id"])
    filtered_accounts = accounts[accounts["customer_id"].isin(customer_ids)]
    customer_value = du.enrich_customer_value(filtered_customers, filtered_accounts)
    story = du.build_customer_story(filtered_customers, customer_value)
    customer_kpis = du.calculate_customer_kpis(filtered_customers)
    premium_share = (filtered_customers["customer_type"] == "Premium").mean() * 100
    premium_balance_share = (
        customer_value.loc[customer_value["customer_type"] == "Premium", "total_balance"].sum()
        / customer_value["total_balance"].sum()
        * 100
        if customer_value["total_balance"].sum()
        else 0.0
    )

    st.title("Customers")
    render_period_banner(data)
    render_story_headline(story["headline"])
    st.caption(
        f"Showing **{len(filtered_customers):,}** of **{len(customers):,}** customers after filters."
    )

    render_metric_row(
        [
            ("Customers shown", f"{customer_kpis['total_customers']:,}"),
            ("Average age", f"{customer_kpis['average_age']:.0f} years"),
            ("Premium share", f"{premium_share:.1f}%"),
            ("Premium balance share", f"{premium_balance_share:.1f}%"),
        ],
        help_texts=[
            "Customers after applying filters.",
            "Average age of customers in view.",
            "Share of Premium-tier customers.",
            "Share of total balances held by Premium customers.",
        ],
    )
    st.info(f"**Recommended action:** {story['action']}")

    charts = du.create_customer_charts(filtered_customers, customer_value)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts["region"], use_container_width=True)
        st.plotly_chart(charts["balance_by_type"], use_container_width=True)
        st.caption("**So what?** Grow Premium balances with targeted savings and investment offers.")
    with col2:
        st.plotly_chart(charts["age_group"], use_container_width=True)
        st.plotly_chart(charts["segment_distribution"], use_container_width=True)
        st.caption("**So what?** Assign relationship managers to Premium and High Activity segments.")


def page_transaction_analytics(data: dict) -> None:
    """Payments story for digital adoption and channel performance."""
    transactions = data["transactions"]
    min_date = transactions["transaction_date"].min().date()
    max_date = transactions["transaction_date"].max().date()

    st.sidebar.subheader("Payment filters")
    date_range = st.sidebar.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    selected_regions = multiselect_with_all(
        "Region", transactions["region"].dropna().unique().tolist(), "txn_region"
    )
    selected_channels = multiselect_with_all(
        "Channel", transactions["channel"].unique().tolist(), "txn_channel"
    )
    selected_types = multiselect_with_all(
        "Transaction type", transactions["transaction_type"].unique().tolist(), "txn_type"
    )

    parsed_range = None
    if isinstance(date_range, tuple) and len(date_range) == 2:
        parsed_range = (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))

    filtered_transactions = du.filter_transactions(
        transactions,
        date_range=parsed_range,
        regions=selected_regions,
        channels=selected_channels,
        transaction_types=selected_types,
    )
    if filtered_transactions.empty:
        st.warning("No transactions match the selected filters.")
        return

    story = du.build_transaction_story(filtered_transactions)
    tx_kpis = du.calculate_transaction_kpis(filtered_transactions)

    st.title("Payments")
    render_period_banner(data)
    render_story_headline(story["headline"])
    st.caption(
        f"Showing **{len(filtered_transactions):,}** of **{len(transactions):,}** transactions after filters."
    )

    render_metric_row(
        [
            ("Transactions", f"{tx_kpis['transaction_count']:,}"),
            ("Total value", du.format_tzs(tx_kpis["transaction_value"])),
            ("Average payment", du.format_tzs(tx_kpis["average_transaction_amount"])),
            ("Change vs last month", f"{story.get('tx_growth', 0.0):+.1f}%"),
        ],
        help_texts=[
            "Number of payments in the filtered view.",
            "Total money moved.",
            "Average amount per payment.",
            "Transaction count change versus the previous month.",
        ],
    )
    st.info(f"**Recommended action:** {story['action']}")

    charts = du.create_transaction_charts(filtered_transactions)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts["volume_trend"], use_container_width=True)
        st.plotly_chart(charts["transaction_type"], use_container_width=True)
    with col2:
        st.plotly_chart(charts["channel_performance"], use_container_width=True)
        st.caption(
            "**So what?** Invest first in channels that combine high volume with high value "
            "(usually Mobile App and Branch for large tickets)."
        )


def page_loan_analytics(data: dict) -> None:
    """Credit risk story for portfolio health."""
    loans = data["loans"]
    customers = data["customers"]

    st.sidebar.subheader("Credit filters")
    selected_regions = multiselect_with_all("Region", customers["region"].unique().tolist(), "loan_region")
    selected_loan_types = multiselect_with_all(
        "Loan type", loans["loan_type"].unique().tolist(), "loan_type"
    )
    selected_risk = multiselect_with_all(
        "Risk category", loans["risk_category"].unique().tolist(), "loan_risk"
    )

    filtered_loans, filtered_merged = du.filter_loans(
        loans,
        customers,
        regions=selected_regions,
        loan_types=selected_loan_types,
        risk_categories=selected_risk,
    )
    if filtered_loans.empty:
        st.warning("No loans match the selected filters.")
        return

    story = du.build_loan_story(filtered_loans, filtered_merged)
    loan_kpis = du.calculate_loan_kpis(filtered_loans)

    st.title("Credit Risk")
    render_period_banner(data)
    render_story_headline(story["headline"])
    st.caption(f"Showing **{len(filtered_loans):,}** of **{len(loans):,}** loans after filters.")

    st.subheader("Portfolio health")
    render_metric_row(
        [
            ("Loans shown", f"{loan_kpis['total_loans']:,}"),
            ("Portfolio value", du.format_tzs(loan_kpis["total_loan_amount"])),
            ("Average loan size", du.format_tzs(loan_kpis["average_loan_size"])),
            ("On-time repayment", f"{loan_kpis['on_time_rate']:.1f}%"),
        ],
        deltas=[None, None, None, status_delta("on_time_rate", loan_kpis["on_time_rate"])],
    )
    render_metric_row(
        [
            ("Watchlist (late)", f"{loan_kpis['watchlist_rate']:.1f}%"),
            ("Default rate", f"{loan_kpis['default_rate']:.1f}%"),
            ("At-risk (late + default)", f"{loan_kpis['at_risk_rate']:.1f}%"),
        ],
        help_texts=[
            "Late loans needing early collections outreach.",
            "Loans already in default.",
            "Combined late and default share — useful as a broad risk pulse.",
        ],
        deltas=[
            status_delta("watchlist_rate", loan_kpis["watchlist_rate"]),
            status_delta("default_rate", loan_kpis["default_rate"]),
            status_delta("at_risk_rate", loan_kpis["at_risk_rate"]),
        ],
    )
    st.info(f"**Recommended action:** {story['action']}")

    charts = du.create_loan_charts(filtered_loans, filtered_merged)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts["repayment_status"], use_container_width=True)
        st.plotly_chart(charts["default_by_region"], use_container_width=True)
        st.caption("**So what?** Put collections capacity in the highest-default regions first.")
    with col2:
        st.plotly_chart(charts["risk_distribution"], use_container_width=True)
        st.plotly_chart(charts["loan_products"], use_container_width=True)


def main() -> None:
    """Run the board-ready banking analytics dashboard."""
    st.sidebar.title("🏦 Banking Analytics")
    st.sidebar.markdown("**For bank owners & EXCO**")
    st.sidebar.caption("Start on Board Overview. Drill into Customers, Payments, or Credit Risk only when needed.")

    page = st.sidebar.radio(
        "Go to",
        [
            "📊 Board Overview",
            "👥 Customers",
            "💳 Payments",
            "🏦 Credit Risk",
        ],
    )

    st.sidebar.divider()
    st.sidebar.markdown("**How to read this**")
    st.sidebar.markdown(
        "1. **Board decisions** — what to do\n"
        "2. **Snapshot KPIs** — proof\n"
        "3. **Status tags** — on track / watch / needs attention\n"
        "4. **Charts** — where to act"
    )

    try:
        data = get_datasets()
    except du.DataLoadError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:  # pragma: no cover
        st.error(f"Unable to load dashboard data: {exc}")
        st.stop()

    if page == "📊 Board Overview":
        page_board_overview(data)
    elif page == "👥 Customers":
        page_customer_analytics(data)
    elif page == "💳 Payments":
        page_transaction_analytics(data)
    else:
        page_loan_analytics(data)


if __name__ == "__main__":
    main()
