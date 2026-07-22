"""
Reusable utilities for the Banking Analytics Streamlit dashboard.

Loads processed datasets, computes KPIs, and builds Plotly charts used across
executive, customer, transaction, and loan dashboard pages.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ANALYTICS_DIR = PROJECT_ROOT / "data" / "analytics"

REQUIRED_FILES = {
    "customers": "customers_clean.csv",
    "accounts": "accounts_clean.csv",
    "transactions": "transactions_clean.csv",
    "loans": "loans_clean.csv",
}

PREMIUM_BALANCE_THRESHOLD = 5_000_000
LOW_VALUE_BALANCE_THRESHOLD = 500_000
HIGH_ACTIVITY_ACCOUNT_THRESHOLD = 3

AGE_GROUP_ORDER = ["18-30", "31-45", "46-60", "60+"]
RISK_ORDER = ["Low Risk", "Medium Risk", "High Risk"]
REPAYMENT_ORDER = ["On Time", "Late", "Default"]
DIGITAL_CHANNELS = {"Mobile App", "USSD", "Internet Banking"}

# Consistent banking visual identity for Plotly charts.
BANKING_COLORWAY = ["#1f4e79", "#2e75b6", "#5b9bd5", "#70ad47", "#f9a825", "#c62828"]
PLOTLY_LAYOUT = dict(
    font=dict(family="Arial, sans-serif", size=13, color="#1e293b"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    colorway=BANKING_COLORWAY,
    margin=dict(l=24, r=24, t=72, b=24),
    title=dict(x=0, xanchor="left", font=dict(size=16, color="#1f4e79")),
)


class DataLoadError(Exception):
    """Raised when processed banking datasets are missing or empty."""


def format_tzs(value: float, compact: bool = True) -> str:
    """Format Tanzanian shilling values for dashboard display."""
    if pd.isna(value):
        return "TZS 0"
    if compact and value >= 1_000_000_000:
        return f"TZS {value / 1_000_000_000:.2f}B"
    if compact and value >= 1_000_000:
        return f"TZS {value / 1_000_000:.2f}M"
    return f"TZS {value:,.0f}"


def format_pct(value: float, decimals: int = 1) -> str:
    """Format percentage values for narrative text."""
    return f"{value:.{decimals}f}%"


def apply_chart_theme(fig: go.Figure, subtitle: str | None = None) -> go.Figure:
    """Apply consistent banking styling and optional narrative subtitle."""
    fig.update_layout(**PLOTLY_LAYOUT)
    if subtitle:
        current_title = fig.layout.title.text if fig.layout.title else ""
        fig.update_layout(title=dict(text=f"<b>{current_title}</b><br><sup>{subtitle}</sup>"))
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig


def _top_share(series: pd.Series) -> tuple[str, float]:
    """Return the leading category and its percentage share."""
    counts = series.value_counts()
    if counts.empty:
        return "N/A", 0.0
    top_label = str(counts.index[0])
    top_share = counts.iloc[0] / counts.sum() * 100
    return top_label, float(top_share)


def _monthly_growth_rate(transactions: pd.DataFrame, value_col: str = "transaction_id") -> float:
    """Calculate month-on-month growth for the latest complete month."""
    monthly = (
        transactions.assign(period=transactions["transaction_date"].dt.to_period("M"))
        .groupby("period")
        .size()
        .sort_index()
    )
    if len(monthly) < 2:
        return 0.0
    previous, latest = monthly.iloc[-2], monthly.iloc[-1]
    if previous == 0:
        return 0.0
    return (latest - previous) / previous * 100


def build_customer_story(customers: pd.DataFrame, customer_value: pd.DataFrame) -> dict[str, Any]:
    """Build customer-page narrative from filtered data."""
    top_region, region_share = _top_share(customers["region"])
    top_age, age_share = _top_share(customers["customer_age_group"])
    top_segment, segment_share = _top_share(customer_value["customer_segment"])
    premium_share = (customers["customer_type"] == "Premium").mean() * 100

    return {
        "headline": (
            f"Most customers ({age_share:.0f}%) fall in the {top_age} age band, concentrated in {top_region}."
        ),
        "bullets": [
            f"{top_region} leads regional distribution with {region_share:.1f}% of the filtered base.",
            f"Premium customers represent {premium_share:.1f}% of profiles in view.",
            f"Largest value segment: {top_segment} ({segment_share:.1f}% of customers).",
        ],
        "action": "Prioritize retention offers for high-balance Premium and High Activity segments.",
    }


def build_transaction_story(transactions: pd.DataFrame) -> dict[str, Any]:
    """Build transaction-page narrative from filtered data."""
    top_channel, channel_share = _top_share(transactions["channel"])
    top_type, type_share = _top_share(transactions["transaction_type"])
    digital_share = transactions["channel"].isin(DIGITAL_CHANNELS).mean() * 100
    tx_growth = _monthly_growth_rate(transactions)
    peak_month = (
        transactions.assign(period=transactions["transaction_date"].dt.to_period("M").astype(str))
        .groupby("period")
        .size()
        .sort_values(ascending=False)
        .index[0]
    )

    return {
        "headline": (
            f"{top_channel} dominates channel activity ({channel_share:.0f}%) as digital channels reach "
            f"{digital_share:.0f}% of transactions."
        ),
        "bullets": [
            f"Most common transaction type: {top_type} ({type_share:.1f}% of volume).",
            f"Peak activity month in selection: {peak_month}.",
            f"Month-on-month volume change: {tx_growth:+.1f}%.",
        ],
        "action": "Scale digital capacity around peak hours and top-performing channels.",
        "tx_growth": tx_growth,
        "digital_share": digital_share,
        "top_channel": top_channel,
        "channel_share": channel_share,
    }


def build_loan_story(loans: pd.DataFrame, loans_customers: pd.DataFrame) -> dict[str, Any]:
    """Build loan-page narrative from filtered portfolio data."""
    kpis = calculate_loan_kpis(loans)
    top_product = loans.groupby("loan_type")["loan_amount"].sum().idxmax()
    on_time_share = (loans["repayment_status"] == "On Time").mean() * 100
    high_risk_share = (loans["risk_category"] == "High Risk").mean() * 100

    regional = (
        loans_customers.groupby("region")
        .agg(default_rate=("repayment_status", lambda s: (s == "Default").mean() * 100))
        .sort_values("default_rate", ascending=False)
    )
    highest_risk_region = regional.index[0]
    highest_risk_rate = regional.iloc[0]["default_rate"]

    return {
        "headline": (
            f"{top_product} anchors the portfolio at {format_tzs(kpis['total_loan_amount'])} with "
            f"{on_time_share:.1f}% on-time repayment."
        ),
        "bullets": [
            f"On-time repayment: {kpis['on_time_rate']:.1f}%.",
            f"Watchlist (late): {kpis['watchlist_rate']:.1f}% · Defaults: {kpis['default_rate']:.1f}%.",
            f"High Risk exposure: {high_risk_share:.1f}% of loans in the current view.",
            f"{highest_risk_region} shows the highest default rate ({highest_risk_rate:.1f}%).",
        ],
        "action": "Strengthen collections in high-default regions and tighten early-warning for late loans.",
    }


def _read_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    """Read a CSV file with optional date parsing."""
    return pd.read_csv(path, parse_dates=parse_dates or [])


def resolve_data_dir(preferred: Path | None = None) -> Path:
    """
    Choose which data folder to load for local vs Streamlit Cloud.

    Preference order:
    1. Explicit preferred path
    2. Full processed warehouse (local)
    3. Analytics mart published for cloud deployment
    """
    if preferred is not None:
        return preferred

    use_analytics = os.getenv("USE_ANALYTICS_DATA", "").lower() in {"1", "true", "yes"}
    on_streamlit_cloud = Path("/mount/src").exists()

    processed_ready = (PROCESSED_DIR / REQUIRED_FILES["transactions"]).exists()
    analytics_ready = (ANALYTICS_DIR / REQUIRED_FILES["transactions"]).exists()

    if use_analytics or on_streamlit_cloud:
        if analytics_ready:
            return ANALYTICS_DIR
        if processed_ready:
            return PROCESSED_DIR

    if processed_ready:
        return PROCESSED_DIR
    if analytics_ready:
        return ANALYTICS_DIR
    return PROCESSED_DIR


def load_data(data_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    """
    Load all cleaned banking datasets required by the dashboard.

    Raises
    ------
    DataLoadError
        If any required file is missing or empty.
    """
    data_dir = resolve_data_dir(data_dir)
    missing = [name for name, filename in REQUIRED_FILES.items() if not (data_dir / filename).exists()]
    if missing:
        files = ", ".join(REQUIRED_FILES[name] for name in missing)
        raise DataLoadError(
            f"Dataset missing: {files}. Please run the data generation and cleaning pipelines first."
        )

    customers = _read_csv(data_dir / REQUIRED_FILES["customers"], ["date_of_birth", "customer_since"])
    accounts = _read_csv(data_dir / REQUIRED_FILES["accounts"], ["opening_date"])
    transactions = _read_csv(data_dir / REQUIRED_FILES["transactions"], ["transaction_date"])
    loans = _read_csv(data_dir / REQUIRED_FILES["loans"], ["loan_date"])

    datasets = {
        "customers": customers,
        "accounts": accounts,
        "transactions": transactions,
        "loans": loans,
    }

    empty = [name for name, df in datasets.items() if df.empty]
    if empty:
        raise DataLoadError(
            f"Dataset empty: {', '.join(empty)}. Please regenerate processed data before opening the dashboard."
        )

    return datasets


def enrich_customer_value(customers: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    """Attach account balance metrics and rule-based segments to customers."""
    account_metrics = (
        accounts.groupby("customer_id", as_index=False)
        .agg(total_balance=("balance", "sum"), account_count=("account_id", "count"))
    )
    profile = customers.merge(account_metrics, on="customer_id", how="left").fillna(
        {"total_balance": 0, "account_count": 0}
    )

    conditions = [
        profile["total_balance"] > PREMIUM_BALANCE_THRESHOLD,
        profile["account_count"] >= HIGH_ACTIVITY_ACCOUNT_THRESHOLD,
        profile["total_balance"] < LOW_VALUE_BALANCE_THRESHOLD,
    ]
    choices = ["Premium", "High Activity", "Low Value"]
    profile["customer_segment"] = np.select(conditions, choices, default="Standard")
    return profile


def calculate_executive_kpis(data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Compute top-level KPIs for the board overview page."""
    customers = data["customers"]
    accounts = data["accounts"]
    transactions = data["transactions"]
    loans = data["loans"]

    credit = calculate_credit_health(loans)
    digital_share = (
        transactions["channel"].isin(DIGITAL_CHANNELS).mean() * 100 if len(transactions) else 0.0
    )

    return {
        "total_customers": len(customers),
        "active_accounts": int((accounts["status"] == "Active").sum()),
        "premium_customers": int((customers["customer_type"] == "Premium").sum()),
        "premium_share": float((customers["customer_type"] == "Premium").mean() * 100) if len(customers) else 0.0,
        "total_transactions": len(transactions),
        "total_transaction_value": float(transactions["amount"].sum()) if len(transactions) else 0.0,
        "average_transaction_amount": float(transactions["amount"].mean()) if len(transactions) else 0.0,
        "total_loans": len(loans),
        "total_loan_portfolio": float(loans["loan_amount"].sum()) if len(loans) else 0.0,
        "digital_share": float(digital_share),
        **credit,
    }


def calculate_credit_health(loans: pd.DataFrame) -> dict[str, float]:
    """
    Split repayment health into board-friendly credit metrics.

    - On-time repayment: performing loans
    - Watchlist (Late): early warning, not yet default
    - Default rate: loans in Default status
    - At-risk rate: Late + Default (watchlist + default combined)
    """
    total = len(loans)
    if total == 0:
        return {
            "on_time_rate": 0.0,
            "watchlist_rate": 0.0,
            "default_rate": 0.0,
            "at_risk_rate": 0.0,
            "npl_rate": 0.0,
        }

    on_time = (loans["repayment_status"] == "On Time").sum()
    late = (loans["repayment_status"] == "Late").sum()
    defaulted = (loans["repayment_status"] == "Default").sum()
    at_risk = late + defaulted

    return {
        "on_time_rate": float(on_time / total * 100),
        "watchlist_rate": float(late / total * 100),
        "default_rate": float(defaulted / total * 100),
        "at_risk_rate": float(at_risk / total * 100),
        # Keep legacy key for older call sites; maps to at-risk (Late + Default).
        "npl_rate": float(at_risk / total * 100),
    }


def calculate_loan_kpis(loans: pd.DataFrame) -> dict[str, Any]:
    """Compute loan-page KPIs from a filtered loan dataset."""
    credit = calculate_credit_health(loans)
    return {
        "total_loans": len(loans),
        "total_loan_amount": float(loans["loan_amount"].sum()) if len(loans) else 0.0,
        "average_loan_size": float(loans["loan_amount"].mean()) if len(loans) else 0.0,
        **credit,
    }


def kpi_status(metric: str, value: float) -> tuple[str, str]:
    """
    Return (status_label, delta_text) traffic-light guidance for board KPIs.

    Thresholds aligned to Tanzania retail banking monitoring bands.
    """
    rules = {
        "digital_share": [(70, "On track"), (50, "Watch"), (0, "Needs attention")],
        "on_time_rate": [(90, "On track"), (80, "Watch"), (0, "Needs attention")],
        "default_rate": [(3, "On track"), (5, "Watch"), (100, "Needs attention")],
        "watchlist_rate": [(8, "On track"), (12, "Watch"), (100, "Needs attention")],
        "at_risk_rate": [(10, "On track"), (15, "Watch"), (100, "Needs attention")],
    }
    # For default/watchlist/at-risk, lower is better.
    lower_is_better = metric in {"default_rate", "watchlist_rate", "at_risk_rate", "npl_rate"}

    if metric not in rules:
        return "Info", "Review"

    bands = rules[metric]
    if lower_is_better:
        if value <= bands[0][0]:
            return "On track", "Within target"
        if value <= bands[1][0]:
            return "Watch", "Above soft target"
        return "Needs attention", "Above risk target"

    # Higher is better
    if value >= bands[0][0]:
        return "On track", "Within target"
    if value >= bands[1][0]:
        return "Watch", "Below soft target"
    return "Needs attention", "Below target"


def reporting_period(data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Build reporting-period metadata for the executive banner."""
    transactions = data["transactions"]
    loans = data["loans"]
    customers = data["customers"]

    start = transactions["transaction_date"].min()
    end = transactions["transaction_date"].max()
    data_dir = resolve_data_dir()
    layer_labels = {
        "analytics": "Analytics mart",
        "processed": "Processed warehouse",
    }

    return {
        "period_label": f"{start.strftime('%b %Y')} – {end.strftime('%b %Y')}",
        "currency": "TZS",
        "view_label": layer_labels.get(data_dir.name, data_dir.name),
        "customer_count": f"{len(customers):,}",
        "loan_count": f"{len(loans):,}",
        "data_layer": data_dir.name,
    }


def build_board_decisions(data: dict[str, pd.DataFrame]) -> list[dict[str, str]]:
    """
    Build three board-ready decisions: success, risk, and next action.
    """
    story = build_executive_story(data)
    kpis = story["kpis"]
    loans = data["loans"]
    customers = data["customers"]
    loans_customers = loans.merge(customers[["customer_id", "region"]], on="customer_id", how="left")

    regional = (
        loans_customers.groupby("region")
        .agg(default_rate=("repayment_status", lambda s: (s == "Default").mean() * 100))
        .sort_values("default_rate", ascending=False)
    )
    top_risk_region = regional.index[0] if not regional.empty else "N/A"
    top_risk_rate = float(regional.iloc[0]["default_rate"]) if not regional.empty else 0.0

    return [
        {
            "type": "Success",
            "title": "Digital banking is the main channel",
            "detail": (
                f"{story['top_channel']} handles {story['channel_share']:.0f}% of transactions; "
                f"digital channels overall are {kpis['digital_share']:.0f}%."
            ),
            "owner": "Retail / Digital",
        },
        {
            "type": "Risk",
            "title": "Credit watchlist needs management attention",
            "detail": (
                f"On-time repayment is {kpis['on_time_rate']:.1f}%. "
                f"Defaults are {kpis['default_rate']:.1f}% and late (watchlist) loans are "
                f"{kpis['watchlist_rate']:.1f}%. Highest default region: {top_risk_region} "
                f"({top_risk_rate:.1f}%)."
            ),
            "owner": "Credit Risk",
        },
        {
            "type": "Action",
            "title": "Focus collections and digital capacity this month",
            "detail": (
                f"Deploy collections to {top_risk_region} and keep Mobile/USSD capacity strong "
                f"as volume moved {story['tx_growth']:+.1f}% vs last month."
            ),
            "owner": "Credit + Operations",
        },
    ]


def build_executive_story(data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Build headline narrative and talking points for the board overview."""
    customers = data["customers"]
    transactions = data["transactions"]
    loans = data["loans"]
    kpis = calculate_executive_kpis(data)

    top_region, region_share = _top_share(customers["region"])
    top_channel, channel_share = _top_share(transactions["channel"])
    top_loan_product = loans.groupby("loan_type")["loan_amount"].sum().idxmax()
    tx_growth = _monthly_growth_rate(transactions)

    headline = (
        f"Digital channels drive {kpis['digital_share']:.0f}% of payments. "
        f"Loan book is {format_tzs(kpis['total_loan_portfolio'])} with "
        f"{kpis['on_time_rate']:.1f}% on-time repayment and {kpis['default_rate']:.1f}% defaults."
    )

    return {
        "headline": headline,
        "kpis": kpis,
        "bullets": [
            f"Customer base: {kpis['total_customers']:,} clients; Premium share {kpis['premium_share']:.1f}%.",
            f"Largest market: {top_region} ({region_share:.1f}% of customers).",
            f"Payments: {top_channel} leads channels at {channel_share:.1f}% of transactions.",
            f"Credit: on-time {kpis['on_time_rate']:.1f}% · watchlist (late) {kpis['watchlist_rate']:.1f}% · default {kpis['default_rate']:.1f}%.",
            f"Top lending product by value: {top_loan_product}.",
            f"Transaction volume changed {tx_growth:+.1f}% versus the previous month.",
        ],
        "watchouts": [
            f"Default rate at {kpis['default_rate']:.1f}% — prioritize collections and early-warning on late loans.",
            f"Watchlist (late) loans are {kpis['watchlist_rate']:.1f}% — treat as early credit risk, not yet default.",
            "Keep branch capacity for high-value transactions while shifting routine payments to Mobile/USSD.",
        ],
        "top_channel": top_channel,
        "channel_share": channel_share,
        "digital_share": kpis["digital_share"],
        "top_region": top_region,
        "on_time_share": kpis["on_time_rate"],
        "tx_growth": tx_growth,
    }


def calculate_customer_kpis(customers: pd.DataFrame) -> dict[str, Any]:
    """Compute customer-page KPIs from a filtered customer dataset."""
    return {
        "total_customers": len(customers),
        "average_age": float(customers["age"].mean()) if len(customers) else 0.0,
        "premium_customers": int((customers["customer_type"] == "Premium").sum()),
        "regions_covered": int(customers["region"].nunique()),
    }


def calculate_transaction_kpis(transactions: pd.DataFrame) -> dict[str, Any]:
    """Compute transaction-page KPIs from a filtered transaction dataset."""
    return {
        "transaction_count": len(transactions),
        "transaction_value": float(transactions["amount"].sum()) if len(transactions) else 0.0,
        "average_transaction_amount": float(transactions["amount"].mean()) if len(transactions) else 0.0,
    }


def create_customer_growth_chart(customers: pd.DataFrame) -> go.Figure:
    """Plot cumulative customer acquisition trend by relationship start date."""
    trend = (
        customers.assign(acquisition_month=customers["customer_since"].dt.to_period("M").astype(str))
        .groupby("acquisition_month", as_index=False)
        .size()
        .rename(columns={"size": "new_customers"})
        .sort_values("acquisition_month")
    )
    trend["cumulative_customers"] = trend["new_customers"].cumsum()
    fig = px.line(
        trend,
        x="acquisition_month",
        y="cumulative_customers",
        markers=True,
        title="Customer Growth Trend",
        labels={"acquisition_month": "Month", "cumulative_customers": "Cumulative Customers"},
    )
    fig.update_layout(hovermode="x unified")
    return apply_chart_theme(
        fig,
        subtitle="Steady acquisition supports long-term relationship banking growth.",
    )


def create_transaction_volume_trend(transactions: pd.DataFrame) -> go.Figure:
    """Plot monthly transaction volume."""
    trend = (
        transactions.assign(year_month=transactions["transaction_date"].dt.to_period("M").astype(str))
        .groupby("year_month", as_index=False)
        .agg(transaction_volume=("transaction_id", "count"))
        .sort_values("year_month")
    )
    fig = px.line(
        trend,
        x="year_month",
        y="transaction_volume",
        markers=True,
        title="Are transaction volumes growing?",
        labels={"year_month": "Month", "transaction_volume": "Transactions"},
    )
    return apply_chart_theme(fig, subtitle="Monthly volume reveals seasonality and digital adoption momentum.")


def create_transaction_value_trend(transactions: pd.DataFrame) -> go.Figure:
    """Plot monthly transaction value."""
    trend = (
        transactions.assign(year_month=transactions["transaction_date"].dt.to_period("M").astype(str))
        .groupby("year_month", as_index=False)
        .agg(transaction_value=("amount", "sum"))
        .sort_values("year_month")
    )
    fig = px.line(
        trend,
        x="year_month",
        y="transaction_value",
        markers=True,
        title="How much value moves through the bank each month?",
        labels={"year_month": "Month", "transaction_value": "Value (TZS)"},
    )
    return apply_chart_theme(fig, subtitle="Value trends complement volume to show customer spending power.")


def create_loan_portfolio_distribution(loans: pd.DataFrame) -> go.Figure:
    """Plot loan portfolio composition by product type."""
    summary = (
        loans.groupby("loan_type", as_index=False)["loan_amount"]
        .sum()
        .sort_values("loan_amount", ascending=False)
    )
    fig = px.pie(
        summary,
        names="loan_type",
        values="loan_amount",
        title="Where is lending exposure concentrated?",
        hole=0.35,
    )
    return apply_chart_theme(fig, subtitle="Product mix guides capital allocation and risk appetite.")


def create_channel_usage_chart(transactions: pd.DataFrame) -> go.Figure:
    """Plot transaction distribution across banking channels."""
    summary = transactions["channel"].value_counts().reset_index()
    summary.columns = ["channel", "transaction_count"]
    fig = px.bar(
        summary,
        x="channel",
        y="transaction_count",
        title="Which channels do customers prefer?",
        color="channel",
        labels={"channel": "Channel", "transaction_count": "Transactions"},
    )
    return apply_chart_theme(fig, subtitle="Channel mix signals digital maturity and branch dependency.")


def create_customer_charts(customers: pd.DataFrame, customer_value: pd.DataFrame) -> dict[str, go.Figure]:
    """Build customer analytics charts for the dashboard page."""
    region_summary = customers["region"].value_counts().reset_index()
    region_summary.columns = ["region", "customers"]

    age_summary = (
        customers["customer_age_group"]
        .value_counts()
        .reindex(AGE_GROUP_ORDER)
        .reset_index()
    )
    age_summary.columns = ["customer_age_group", "customers"]

    type_summary = customers["customer_type"].value_counts().reset_index()
    type_summary.columns = ["customer_type", "customers"]

    occupation_summary = customers["occupation"].value_counts().head(10).reset_index()
    occupation_summary.columns = ["occupation", "customers"]

    balance_by_type = (
        customer_value.groupby("customer_type", as_index=False)["total_balance"]
        .mean()
        .sort_values("total_balance", ascending=False)
    )

    segment_summary = customer_value["customer_segment"].value_counts().reset_index()
    segment_summary.columns = ["customer_segment", "customers"]

    charts = {
        "region": apply_chart_theme(
            px.bar(region_summary, x="region", y="customers", title="Where are customers located?", color="region"),
            subtitle="Regional concentration informs branch and agent network strategy.",
        ),
        "age_group": apply_chart_theme(
            px.bar(age_summary, x="customer_age_group", y="customers", title="Which age groups dominate?", color="customer_age_group"),
            subtitle="Age mix shapes product design and financial literacy programs.",
        ),
        "customer_type": apply_chart_theme(
            px.bar(type_summary, x="customer_type", y="customers", title="How is the base segmented?", color="customer_type"),
            subtitle="Premium and Standard tiers guide differentiated service models.",
        ),
        "occupation": apply_chart_theme(
            px.bar(occupation_summary, x="customers", y="occupation", orientation="h", title="Who are our customers?", color="occupation"),
            subtitle="Occupation clusters highlight cross-sell and payroll opportunities.",
        ),
        "balance_by_type": apply_chart_theme(
            px.bar(
                balance_by_type,
                x="customer_type",
                y="total_balance",
                title="Who holds the most value?",
                color="customer_type",
                labels={"total_balance": "Average Balance (TZS)"},
            ),
            subtitle="Balance gaps between tiers reveal upsell potential.",
        ),
        "segment_distribution": apply_chart_theme(
            px.pie(
                segment_summary,
                names="customer_segment",
                values="customers",
                title="How are customers distributed by behavior?",
                hole=0.35,
            ),
            subtitle="Behavioral segments support targeted relationship management.",
        ),
    }
    return charts


def create_transaction_charts(transactions: pd.DataFrame) -> dict[str, go.Figure]:
    """Build transaction analytics charts for the dashboard page."""
    type_summary = transactions["transaction_type"].value_counts().reset_index()
    type_summary.columns = ["transaction_type", "transaction_count"]

    channel_summary = (
        transactions.groupby("channel", as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            transaction_value=("amount", "sum"),
        )
        .sort_values("transaction_count", ascending=False)
    )

    return {
        "volume_trend": create_transaction_volume_trend(transactions),
        "value_trend": create_transaction_value_trend(transactions),
        "transaction_type": apply_chart_theme(
            px.bar(
                type_summary,
                x="transaction_type",
                y="transaction_count",
                title="What transactions happen most often?",
                color="transaction_type",
            ),
            subtitle="Deposit vs payment mix indicates liquidity and spending behavior.",
        ),
        "channel_performance": apply_chart_theme(
            px.bar(
                channel_summary,
                x="channel",
                y="transaction_value",
                title="Which channels move the most value?",
                color="channel",
                labels={"transaction_value": "Value (TZS)"},
            ),
            subtitle="Value by channel shows where high-value interactions occur.",
        ),
    }


def create_loan_charts(loans: pd.DataFrame, loans_customers: pd.DataFrame) -> dict[str, go.Figure]:
    """Build loan analytics charts for the dashboard page."""
    product_summary = loans["loan_type"].value_counts().reset_index()
    product_summary.columns = ["loan_type", "loan_count"]

    repayment_summary = loans["repayment_status"].value_counts().reindex(REPAYMENT_ORDER).reset_index()
    repayment_summary.columns = ["repayment_status", "loan_count"]

    risk_summary = loans["risk_category"].value_counts().reindex(RISK_ORDER).reset_index()
    risk_summary.columns = ["risk_category", "loan_count"]

    regional_default = (
        loans_customers.groupby("region", as_index=False)
        .agg(
            loan_count=("loan_id", "count"),
            default_count=("repayment_status", lambda s: (s == "Default").sum()),
        )
    )
    regional_default["default_rate"] = (
        regional_default["default_count"] / regional_default["loan_count"] * 100
    ).round(2)

    return {
        "loan_products": apply_chart_theme(
            px.bar(product_summary, x="loan_type", y="loan_count", title="Which loan products are most popular?", color="loan_type"),
            subtitle="Product popularity informs marketing and underwriting focus.",
        ),
        "repayment_status": apply_chart_theme(
            px.bar(
                repayment_summary,
                x="repayment_status",
                y="loan_count",
                title="How healthy is repayment performance?",
                color="repayment_status",
                color_discrete_map={"On Time": "#2e7d32", "Late": "#f9a825", "Default": "#c62828"},
            ),
            subtitle="Repayment mix is the primary indicator of portfolio quality.",
        ),
        "risk_distribution": apply_chart_theme(
            px.bar(
                risk_summary,
                x="risk_category",
                y="loan_count",
                title="How much exposure sits in each risk tier?",
                color="risk_category",
                color_discrete_map={"Low Risk": "#2e7d32", "Medium Risk": "#f9a825", "High Risk": "#c62828"},
            ),
            subtitle="Risk tiers translate repayment behavior into capital planning.",
        ),
        "default_by_region": apply_chart_theme(
            px.bar(
                regional_default.sort_values("default_rate", ascending=False),
                x="region",
                y="default_rate",
                title="Which regions carry the highest default risk?",
                color="region",
                labels={"default_rate": "Default Rate (%)"},
            ),
            subtitle="Regional default hotspots guide collections deployment.",
        ),
        "loan_amount_distribution": apply_chart_theme(
            px.histogram(
                loans,
                x="loan_amount",
                nbins=40,
                title="How are loan sizes distributed?",
                labels={"loan_amount": "Loan Amount (TZS)"},
            ),
            subtitle="Tail risk in large loans requires enhanced monitoring.",
        ),
    }


def filter_customers(
    customers: pd.DataFrame,
    regions: list[str] | None = None,
    genders: list[str] | None = None,
    customer_types: list[str] | None = None,
) -> pd.DataFrame:
    """Apply sidebar filters to the customer dataset."""
    filtered = customers.copy()
    if regions:
        filtered = filtered[filtered["region"].isin(regions)]
    if genders:
        filtered = filtered[filtered["gender"].isin(genders)]
    if customer_types:
        filtered = filtered[filtered["customer_type"].isin(customer_types)]
    return filtered


def filter_transactions(
    transactions: pd.DataFrame,
    date_range: tuple[pd.Timestamp, pd.Timestamp] | None = None,
    regions: list[str] | None = None,
    channels: list[str] | None = None,
    transaction_types: list[str] | None = None,
) -> pd.DataFrame:
    """Apply sidebar filters to the transaction dataset."""
    filtered = transactions.copy()
    if date_range:
        start, end = date_range
        filtered = filtered[
            (filtered["transaction_date"] >= start) & (filtered["transaction_date"] <= end)
        ]
    if regions:
        filtered = filtered[filtered["region"].isin(regions)]
    if channels:
        filtered = filtered[filtered["channel"].isin(channels)]
    if transaction_types:
        filtered = filtered[filtered["transaction_type"].isin(transaction_types)]
    return filtered


def filter_loans(
    loans: pd.DataFrame,
    customers: pd.DataFrame,
    regions: list[str] | None = None,
    loan_types: list[str] | None = None,
    risk_categories: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply sidebar filters to loan data using customer region."""
    merged = loans.merge(customers[["customer_id", "region"]], on="customer_id", how="left")

    if regions:
        merged = merged[merged["region"].isin(regions)]
    if loan_types:
        merged = merged[merged["loan_type"].isin(loan_types)]
    if risk_categories:
        merged = merged[merged["risk_category"].isin(risk_categories)]

    filtered_loans = loans[loans["loan_id"].isin(merged["loan_id"])].copy()
    return filtered_loans, merged


__all__ = [
    "DataLoadError",
    "apply_chart_theme",
    "build_board_decisions",
    "build_customer_story",
    "build_executive_story",
    "build_loan_story",
    "build_transaction_story",
    "calculate_credit_health",
    "calculate_customer_kpis",
    "calculate_executive_kpis",
    "calculate_loan_kpis",
    "calculate_transaction_kpis",
    "create_channel_usage_chart",
    "create_customer_charts",
    "create_customer_growth_chart",
    "create_loan_charts",
    "create_loan_portfolio_distribution",
    "create_transaction_charts",
    "create_transaction_volume_trend",
    "enrich_customer_value",
    "filter_customers",
    "filter_loans",
    "filter_transactions",
    "format_tzs",
    "kpi_status",
    "load_data",
    "reporting_period",
    "resolve_data_dir",
]
