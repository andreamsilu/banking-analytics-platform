"""
Banking Analytics Intelligence Platform — Streamlit Dashboard.

Presents customer, transaction, and loan analytics as a guided data story
for banking executives and analysts.
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

# Ensure utility updates are picked up without restarting Streamlit manually.
du = importlib.reload(du)

st.set_page_config(
    page_title="Banking Analytics Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

BANKING_CSS = """
<style>
    .block-container { padding-top: 1.2rem; max-width: 1200px; }

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
        font-size: 1.15rem;
        line-height: 1.6;
        color: #e2e8f0;
        background: linear-gradient(90deg, #1f4e79 0%, #2e75b6 100%);
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .story-section-label {
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
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


def render_story_headline(text: str) -> None:
    """Display the page-level narrative hook."""
    st.markdown(f'<div class="story-headline">{text}</div>', unsafe_allow_html=True)


def render_story_section(label: str, title: str, body: str | None = None) -> None:
    """Open a story section with context for the reader."""
    st.markdown(f'<p class="story-section-label">{label}</p>', unsafe_allow_html=True)
    st.subheader(title)
    if body:
        st.caption(body)


def render_insight_list(title: str, bullets: list[str], icon: str = "💡") -> None:
    """Render key takeaways as a scannable insight block."""
    st.markdown(f"**{icon} {title}**")
    for bullet in bullets:
        st.markdown(f"- {bullet}")


def render_metric_row(metrics: list[tuple[str, str]], help_texts: list[str] | None = None) -> None:
    """Render a row of KPI cards with optional context tooltips."""
    columns = st.columns(len(metrics))
    for index, (column, (label, value)) in enumerate(zip(columns, metrics)):
        help_text = help_texts[index] if help_texts and index < len(help_texts) else None
        column.metric(label, value, help=help_text)


def page_executive_overview(data: dict) -> None:
    """Executive story: portfolio health at a glance."""
    story = du.build_executive_story(data)
    kpis = story["kpis"]

    st.title("Executive Overview")
    render_story_headline(story["headline"])

    render_story_section(
        "Act 1 — The big picture",
        "How is the bank performing overall?",
        "Start with scale and health across customers, money flow, and lending.",
    )
    render_metric_row(
        [
            ("Total Customers", f"{kpis['total_customers']:,}"),
            ("Active Accounts", f"{kpis['active_accounts']:,}"),
            ("Premium Customers", f"{kpis['premium_customers']:,}"),
            ("Digital Share", f"{story['digital_share']:.1f}%"),
        ],
        help_texts=[
            "Total registered retail and commercial clients.",
            "Accounts currently open and operational.",
            "Highest service-tier customers.",
            "Share of transactions via mobile and online channels.",
        ],
    )
    render_metric_row(
        [
            ("Transaction Volume", f"{kpis['total_transactions']:,}"),
            ("Transaction Value", du.format_tzs(kpis["total_transaction_value"])),
            ("Loan Portfolio", du.format_tzs(kpis["total_loan_portfolio"])),
            ("NPL Rate", f"{kpis['npl_rate']:.2f}%"),
        ],
        help_texts=[
            "All processed transactions in the period.",
            "Total monetary flow through the bank.",
            "Outstanding lending exposure.",
            "Non-performing loans (Late + Default) as % of book.",
        ],
    )

    col_insight, col_watch = st.columns(2)
    with col_insight:
        render_insight_list("Key takeaways", story["bullets"])
    with col_watch:
        render_insight_list("Management watchlist", story["watchouts"], icon="⚠️")

    st.divider()
    render_story_section(
        "Act 2 — What is driving performance?",
        "Trends behind the numbers",
        "Each chart answers one strategic question for leadership.",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(du.create_customer_growth_chart(data["customers"]), use_container_width=True)
        st.caption("**So what?** Sustained customer growth expands the cross-sell funnel.")
        st.plotly_chart(du.create_loan_portfolio_distribution(data["loans"]), use_container_width=True)
        st.caption("**So what?** Product concentration informs capital and risk limits.")
    with col2:
        st.plotly_chart(du.create_transaction_volume_trend(data["transactions"]), use_container_width=True)
        st.caption(
            f"**So what?** Latest monthly volume moved {story.get('tx_growth', 0.0):+.1f}% — monitor momentum."
        )
        st.plotly_chart(du.create_channel_usage_chart(data["transactions"]), use_container_width=True)
        st.caption(
            f"**So what?** {story['top_channel']} leads at {story['channel_share']:.0f}% — "
            "prioritize digital reliability."
        )


def page_customer_analytics(data: dict) -> None:
    """Customer story: who we serve and where value sits."""
    customers = data["customers"]
    accounts = data["accounts"]

    st.sidebar.subheader("Customer Filters")
    selected_regions = st.sidebar.multiselect(
        "Region", sorted(customers["region"].unique()), default=sorted(customers["region"].unique())
    )
    selected_genders = st.sidebar.multiselect(
        "Gender", sorted(customers["gender"].unique()), default=sorted(customers["gender"].unique())
    )
    selected_types = st.sidebar.multiselect(
        "Customer Type",
        sorted(customers["customer_type"].unique()),
        default=sorted(customers["customer_type"].unique()),
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

    st.title("Customer Analytics")
    render_story_headline(story["headline"])

    render_story_section(
        "Context",
        "Who are our customers?",
        "Demographics and segments reveal where to invest in acquisition and retention.",
    )
    render_metric_row(
        [
            ("Customers in View", f"{customer_kpis['total_customers']:,}"),
            ("Average Age", f"{customer_kpis['average_age']:.1f} yrs"),
            ("Premium Share", f"{(filtered_customers['customer_type'] == 'Premium').mean() * 100:.1f}%"),
            ("Regions", f"{customer_kpis['regions_covered']}"),
        ]
    )
    render_insight_list("What this means", story["bullets"])
    st.info(f"**Recommended action:** {story['action']}")

    st.divider()
    charts = du.create_customer_charts(filtered_customers, customer_value)

    render_story_section("Deep dive", "Demographics and value", "Compare geography, age, and wallet share.")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts["region"], use_container_width=True)
        st.plotly_chart(charts["age_group"], use_container_width=True)
    with col2:
        st.plotly_chart(charts["customer_type"], use_container_width=True)
        st.plotly_chart(charts["occupation"], use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(charts["balance_by_type"], use_container_width=True)
        st.caption("**So what?** Widen the gap between Basic and Premium through targeted savings products.")
    with col4:
        st.plotly_chart(charts["segment_distribution"], use_container_width=True)
        st.caption("**So what?** High Activity and Premium segments deserve relationship-manager coverage.")


def page_transaction_analytics(data: dict) -> None:
    """Transaction story: how customers interact with the bank."""
    transactions = data["transactions"]
    min_date = transactions["transaction_date"].min().date()
    max_date = transactions["transaction_date"].max().date()

    st.sidebar.subheader("Transaction Filters")
    date_range = st.sidebar.date_input(
        "Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    selected_regions = st.sidebar.multiselect(
        "Region",
        sorted(transactions["region"].dropna().unique()),
        default=sorted(transactions["region"].dropna().unique()),
    )
    selected_channels = st.sidebar.multiselect(
        "Channel", sorted(transactions["channel"].unique()), default=sorted(transactions["channel"].unique())
    )
    selected_types = st.sidebar.multiselect(
        "Transaction Type",
        sorted(transactions["transaction_type"].unique()),
        default=sorted(transactions["transaction_type"].unique()),
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

    st.title("Transaction Analytics")
    render_story_headline(story["headline"])

    render_story_section(
        "Context",
        "How are customers banking?",
        "Volume, value, and channel mix show digital adoption and operational load.",
    )
    render_metric_row(
        [
            ("Transactions", f"{tx_kpis['transaction_count']:,}"),
            ("Total Value", du.format_tzs(tx_kpis["transaction_value"])),
            ("Average Ticket", du.format_tzs(tx_kpis["average_transaction_amount"])),
            ("MoM Volume Change", f"{story.get('tx_growth', 0.0):+.1f}%"),
        ]
    )
    render_insight_list("What this means", story["bullets"])
    st.info(f"**Recommended action:** {story['action']}")

    st.divider()
    charts = du.create_transaction_charts(filtered_transactions)
    render_story_section("Deep dive", "Trends and channel behavior")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts["volume_trend"], use_container_width=True)
        st.plotly_chart(charts["transaction_type"], use_container_width=True)
    with col2:
        st.plotly_chart(charts["value_trend"], use_container_width=True)
        st.plotly_chart(charts["channel_performance"], use_container_width=True)
        st.caption("**So what?** Invest in the channels that combine high volume with high value.")


def page_loan_analytics(data: dict) -> None:
    """Loan story: credit health and risk exposure."""
    loans = data["loans"]
    customers = data["customers"]

    st.sidebar.subheader("Loan Filters")
    selected_regions = st.sidebar.multiselect(
        "Region", sorted(customers["region"].unique()), default=sorted(customers["region"].unique())
    )
    selected_loan_types = st.sidebar.multiselect(
        "Loan Type", sorted(loans["loan_type"].unique()), default=sorted(loans["loan_type"].unique())
    )
    selected_risk = st.sidebar.multiselect(
        "Risk Category", sorted(loans["risk_category"].unique()), default=sorted(loans["risk_category"].unique())
    )

    filtered_loans, filtered_merged = du.filter_loans(
        loans, customers, regions=selected_regions, loan_types=selected_loan_types, risk_categories=selected_risk
    )
    if filtered_loans.empty:
        st.warning("No loans match the selected filters.")
        return

    story = du.build_loan_story(filtered_loans, filtered_merged)
    loan_kpis = du.calculate_loan_kpis(filtered_loans)

    st.title("Loan Portfolio Analytics")
    render_story_headline(story["headline"])

    render_story_section(
        "Context",
        "How healthy is the loan book?",
        "Repayment performance and regional risk guide provisioning and collections.",
    )
    render_metric_row(
        [
            ("Loans in View", f"{loan_kpis['total_loans']:,}"),
            ("Portfolio Value", du.format_tzs(loan_kpis["total_loan_amount"])),
            ("Average Loan", du.format_tzs(loan_kpis["average_loan_size"])),
            ("NPL Rate", f"{loan_kpis['npl_rate']:.2f}%"),
        ]
    )
    render_insight_list("What this means", story["bullets"])
    st.info(f"**Recommended action:** {story['action']}")

    st.divider()
    charts = du.create_loan_charts(filtered_loans, filtered_merged)
    render_story_section("Deep dive", "Products, repayment, and regional risk")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts["loan_products"], use_container_width=True)
        st.plotly_chart(charts["risk_distribution"], use_container_width=True)
        st.plotly_chart(charts["loan_amount_distribution"], use_container_width=True)
    with col2:
        st.plotly_chart(charts["repayment_status"], use_container_width=True)
        st.plotly_chart(charts["default_by_region"], use_container_width=True)
        st.caption("**So what?** Deploy collections capacity to regions with elevated default rates.")


def main() -> None:
    """Run the banking analytics dashboard."""
    st.sidebar.title("🏦 Banking Analytics")
    st.sidebar.markdown("**Tanzania Banking Intelligence**")
    st.sidebar.caption("A guided data story across customers, transactions, and loans.")

    page = st.sidebar.radio(
        "Navigate the story",
        [
            "📊 Executive Overview",
            "👥 Customer Analytics",
            "💳 Transaction Analytics",
            "🏦 Loan Analytics",
        ],
    )

    st.sidebar.divider()
    st.sidebar.markdown("**How to read this dashboard**")
    st.sidebar.markdown(
        "1. **Headline** — the main insight\n"
        "2. **KPIs** — evidence at a glance\n"
        "3. **Charts** — why it matters\n"
        "4. **Action** — what to do next"
    )
    st.sidebar.divider()
    st.sidebar.caption("Source: cleaned banking datasets")
    try:
        data_dir = du.resolve_data_dir()
        st.sidebar.caption(f"Data folder: `{data_dir.name}`")
    except Exception:
        pass

    try:
        data = get_datasets()
    except du.DataLoadError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:  # pragma: no cover
        st.error(f"Unable to load dashboard data: {exc}")
        st.stop()

    if page == "📊 Executive Overview":
        page_executive_overview(data)
    elif page == "👥 Customer Analytics":
        page_customer_analytics(data)
    elif page == "💳 Transaction Analytics":
        page_transaction_analytics(data)
    else:
        page_loan_analytics(data)


if __name__ == "__main__":
    main()
