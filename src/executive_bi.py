"""
Executive BI decision-support layer for the banking dashboard.

Provides KPI ribbons with MoM change, scorecards, narrative summaries,
chart-level findings, and prioritized management actions.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard_utils import (
    DIGITAL_CHANNELS,
    apply_chart_theme,
    calculate_credit_health,
    enrich_customer_value,
    format_tzs,
    kpi_status,
    _monthly_growth_rate,
    _top_share,
)

# Board targets (illustrative Tanzania retail banking demo thresholds).
TARGET_DIGITAL_ADOPTION = 70.0
TARGET_NPL_RATIO = 10.0
TARGET_ON_TIME = 85.0


def _month_ends(series: pd.Series) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return (current_month_end, prior_month_end) from a date series."""
    end = pd.Timestamp(series.max()).normalize()
    current_end = end + pd.offsets.MonthEnd(0)
    prior_end = current_end - pd.offsets.MonthEnd(1)
    return current_end, prior_end


def _pct_change(current: float, previous: float) -> float:
    """Safe percentage change."""
    if previous == 0:
        return 0.0 if current == 0 else 100.0
    return (current - previous) / abs(previous) * 100


def _status_for_kpi(key: str, value: float) -> str:
    """Map KPI key to a board status badge."""
    mapping = {
        "digital_share": "digital_share",
        "npl_ratio": "at_risk_rate",
        "on_time_rate": "on_time_rate",
        "default_rate": "default_rate",
    }
    metric = mapping.get(key)
    if metric:
        label, _ = kpi_status(metric, value)
        return {
            "On track": "Healthy",
            "Watch": "Watchlist",
            "Needs attention": "Needs Attention",
            "Info": "Review",
        }.get(label, label)
    if key in {"total_customers", "active_customers", "total_deposits", "total_transactions", "loan_portfolio", "avg_balance"}:
        return "Healthy"
    return "Review"


def build_kpi_ribbon(data: dict[str, pd.DataFrame]) -> list[dict[str, Any]]:
    """
    Build the CEO KPI ribbon with current value, MoM change, and status badge.
    """
    customers = data["customers"]
    accounts = data["accounts"]
    transactions = data["transactions"]
    loans = data["loans"]

    current_end, prior_end = _month_ends(transactions["transaction_date"])

    # Stock snapshots approximated by entities existing as of month-end.
    customers_now = customers[customers["customer_since"] <= current_end]
    customers_prev = customers[customers["customer_since"] <= prior_end]

    accounts_now = accounts[accounts["opening_date"] <= current_end]
    accounts_prev = accounts[accounts["opening_date"] <= prior_end]

    loans_now = loans[loans["loan_date"] <= current_end]
    loans_prev = loans[loans["loan_date"] <= prior_end]

    active_ids_now = set(
        transactions.loc[transactions["transaction_date"] > prior_end, "customer_id"]
    )
    active_ids_prev = set(
        transactions.loc[
            (transactions["transaction_date"] > (prior_end - pd.offsets.MonthEnd(1)))
            & (transactions["transaction_date"] <= prior_end),
            "customer_id",
        ]
    )

    txn_now = transactions[
        (transactions["transaction_date"] > prior_end)
        & (transactions["transaction_date"] <= current_end)
    ]
    txn_prev = transactions[
        (transactions["transaction_date"] > (prior_end - pd.offsets.MonthEnd(1)))
        & (transactions["transaction_date"] <= prior_end)
    ]

    deposits_now = float(accounts_now["balance"].sum())
    deposits_prev = float(accounts_prev["balance"].sum())
    portfolio_now = float(loans_now["loan_amount"].sum())
    portfolio_prev = float(loans_prev["loan_amount"].sum())

    credit_now = calculate_credit_health(loans_now)
    credit_prev = calculate_credit_health(loans_prev)

    digital_now = (
        txn_now["channel"].isin(DIGITAL_CHANNELS).mean() * 100 if len(txn_now) else 0.0
    )
    digital_prev = (
        txn_prev["channel"].isin(DIGITAL_CHANNELS).mean() * 100 if len(txn_prev) else 0.0
    )

    avg_bal_now = deposits_now / len(customers_now) if len(customers_now) else 0.0
    avg_bal_prev = deposits_prev / len(customers_prev) if len(customers_prev) else 0.0

    ribbon = [
        {
            "key": "total_customers",
            "label": "Total Customers",
            "value": float(len(customers_now)),
            "display": f"{len(customers_now):,}",
            "mom_pct": _pct_change(len(customers_now), len(customers_prev)),
            "status": _status_for_kpi("total_customers", len(customers_now)),
            "help": "Customers onboarded on or before the latest month-end.",
        },
        {
            "key": "active_customers",
            "label": "Active Customers",
            "value": float(len(active_ids_now)),
            "display": f"{len(active_ids_now):,}",
            "mom_pct": _pct_change(len(active_ids_now), len(active_ids_prev)),
            "status": _status_for_kpi("active_customers", len(active_ids_now)),
            "help": "Customers with at least one transaction in the latest month.",
        },
        {
            "key": "total_deposits",
            "label": "Total Deposits",
            "value": deposits_now,
            "display": format_tzs(deposits_now),
            "mom_pct": _pct_change(deposits_now, deposits_prev),
            "status": _status_for_kpi("total_deposits", deposits_now),
            "help": "Sum of account balances (deposit book proxy).",
        },
        {
            "key": "total_transactions",
            "label": "Total Transactions",
            "value": float(len(txn_now)),
            "display": f"{len(txn_now):,}",
            "mom_pct": _pct_change(len(txn_now), len(txn_prev)),
            "status": _status_for_kpi("total_transactions", len(txn_now)),
            "help": "Transactions in the latest month.",
        },
        {
            "key": "loan_portfolio",
            "label": "Loan Portfolio",
            "value": portfolio_now,
            "display": format_tzs(portfolio_now),
            "mom_pct": _pct_change(portfolio_now, portfolio_prev),
            "status": _status_for_kpi("loan_portfolio", portfolio_now),
            "help": "Outstanding loan book as of latest month-end.",
        },
        {
            "key": "npl_ratio",
            "label": "NPL Ratio",
            "value": credit_now["at_risk_rate"],
            "display": f"{credit_now['at_risk_rate']:.1f}%",
            "mom_pct": credit_now["at_risk_rate"] - credit_prev["at_risk_rate"],
            "mom_is_pp": True,
            "status": _status_for_kpi("npl_ratio", credit_now["at_risk_rate"]),
            "help": "Late + Default loans as % of loan book (demo NPL proxy).",
        },
        {
            "key": "digital_share",
            "label": "Digital Banking Adoption",
            "value": digital_now,
            "display": f"{digital_now:.1f}%",
            "mom_pct": digital_now - digital_prev,
            "mom_is_pp": True,
            "status": _status_for_kpi("digital_share", digital_now),
            "help": "Share of latest-month transactions via Mobile, USSD, or Internet Banking.",
        },
        {
            "key": "avg_balance",
            "label": "Average Customer Balance",
            "value": avg_bal_now,
            "display": format_tzs(avg_bal_now),
            "mom_pct": _pct_change(avg_bal_now, avg_bal_prev),
            "status": _status_for_kpi("avg_balance", avg_bal_now),
            "help": "Total deposits divided by customers as of latest month-end.",
        },
    ]
    return ribbon


def build_executive_summary_text(data: dict[str, pd.DataFrame], ribbon: list[dict[str, Any]]) -> str:
    """Generate an automatically written executive summary paragraph set."""
    customers = data["customers"]
    transactions = data["transactions"]
    loans = data["loans"]

    digital = next(item for item in ribbon if item["key"] == "digital_share")
    npl = next(item for item in ribbon if item["key"] == "npl_ratio")
    customers_kpi = next(item for item in ribbon if item["key"] == "total_customers")
    credit = calculate_credit_health(loans)

    top_channel, channel_share = _top_share(transactions["channel"])
    loans_customers = loans.merge(customers[["customer_id", "region"]], on="customer_id", how="left")
    regional = (
        loans_customers.groupby("region")
        .agg(default_rate=("repayment_status", lambda s: (s == "Default").mean() * 100))
        .sort_values("default_rate", ascending=False)
    )
    risk_region = regional.index[0]
    risk_rate = float(regional.iloc[0]["default_rate"])

    growth_phrase = (
        "Customer growth remains positive"
        if customers_kpi["mom_pct"] >= 0
        else "Customer growth softened this month"
    )
    repay_phrase = (
        "loan repayments remain above the watch threshold"
        if credit["on_time_rate"] >= TARGET_ON_TIME
        else "loan repayments are below the preferred on-time target"
    )
    risk_phrase = (
        "Credit risk remains acceptable"
        if npl["value"] <= TARGET_NPL_RATIO
        else "Credit risk requires elevated management attention"
    )

    return (
        f"Digital banking continues to perform strongly, representing {digital['value']:.0f}% of "
        f"latest-month transactions, led by {top_channel} ({channel_share:.0f}% of all payments). "
        f"{growth_phrase} while {repay_phrase} ({credit['on_time_rate']:.1f}% on time). "
        f"{risk_phrase}, although {risk_region} requires closer monitoring due to an above-average "
        f"default rate of {risk_rate:.1f}%."
    )


def build_action_panel(data: dict[str, pd.DataFrame], ribbon: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Build SUCCESS / WATCHLIST / RECOMMENDED ACTIONS lists."""
    customers = data["customers"]
    accounts = data["accounts"]
    transactions = data["transactions"]
    loans = data["loans"]

    digital = next(item for item in ribbon if item["key"] == "digital_share")
    npl = next(item for item in ribbon if item["key"] == "npl_ratio")
    top_channel, channel_share = _top_share(transactions["channel"])
    credit = calculate_credit_health(loans)

    profile = enrich_customer_value(customers, accounts)
    premium_share = (customers["customer_type"] == "Premium").mean() * 100
    premium_bal_share = (
        profile.loc[profile["customer_type"] == "Premium", "total_balance"].sum()
        / profile["total_balance"].sum()
        * 100
        if profile["total_balance"].sum()
        else 0.0
    )

    loans_customers = loans.merge(customers[["customer_id", "region"]], on="customer_id", how="left")
    regional = (
        loans_customers.groupby("region")
        .agg(default_rate=("repayment_status", lambda s: (s == "Default").mean() * 100))
        .sort_values("default_rate", ascending=False)
    )
    risk_region = regional.index[0]
    risk_rate = float(regional.iloc[0]["default_rate"])
    low_region = customers["region"].value_counts().idxmin()

    success = [
        f"Digital banking adoption reached {digital['value']:.0f}% of latest-month transactions.",
        f"{top_channel} leads channel usage at {channel_share:.0f}% of payments.",
        f"On-time repayment stands at {credit['on_time_rate']:.1f}% of the loan book.",
    ]
    watchlist = [
        f"NPL proxy (late + default) is {npl['value']:.1f}% versus a {TARGET_NPL_RATIO:.0f}% board threshold.",
        f"{risk_region} shows the highest default rate at {risk_rate:.1f}%.",
        f"Premium customers are {premium_share:.1f}% of the base but hold {premium_bal_share:.1f}% of balances — concentration risk and opportunity.",
    ]
    actions = [
        f"Increase loan recovery and early-warning outreach in {risk_region}.",
        "Protect mobile/USSD capacity during month-end peaks.",
        f"Run acquisition campaigns in underrepresented regions such as {low_region}.",
        "Launch premium retention and cross-sell programs for high-balance customers.",
    ]
    return {"success": success, "watchlist": watchlist, "actions": actions}


def build_scorecards(data: dict[str, pd.DataFrame], ribbon: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Build executive scorecards for the board overview."""
    digital = next(item for item in ribbon if item["key"] == "digital_share")
    customers_kpi = next(item for item in ribbon if item["key"] == "total_customers")
    npl = next(item for item in ribbon if item["key"] == "npl_ratio")
    credit = calculate_credit_health(data["loans"])
    txn_growth = _monthly_growth_rate(data["transactions"])

    def grade(metric: str, value: float) -> str:
        label, _ = kpi_status(metric, value)
        return {
            "On track": "Excellent" if value >= 75 or metric == "digital_share" and value >= 75 else "Healthy",
            "Watch": "Watchlist",
            "Needs attention": "Needs Attention",
        }.get(label, "Good")

    digital_grade = "Excellent" if digital["value"] >= 75 else grade("digital_share", digital["value"])
    growth_grade = "Healthy" if customers_kpi["mom_pct"] >= 0 else "Watchlist"
    recovery_grade = grade("on_time_rate", credit["on_time_rate"])
    credit_grade = grade("at_risk_rate", npl["value"])
    ops_grade = "Good" if abs(txn_growth) < 15 else ("Watchlist" if txn_growth < 0 else "Healthy")

    return [
        {"area": "Digital Banking", "status": digital_grade},
        {"area": "Customer Growth", "status": growth_grade},
        {"area": "Loan Recovery", "status": recovery_grade},
        {"area": "Credit Risk", "status": credit_grade},
        {"area": "Operational Efficiency", "status": ops_grade},
    ]


def build_management_actions(data: dict[str, pd.DataFrame]) -> list[dict[str, str]]:
    """Top 5 prioritized management recommendations for every page footer."""
    customers = data["customers"]
    transactions = data["transactions"]
    loans = data["loans"]
    accounts = data["accounts"]

    loans_customers = loans.merge(customers[["customer_id", "region"]], on="customer_id", how="left")
    regional = (
        loans_customers.groupby("region")
        .agg(default_rate=("repayment_status", lambda s: (s == "Default").mean() * 100))
        .sort_values("default_rate", ascending=False)
    )
    risk_region = regional.index[0]
    low_region = customers["region"].value_counts().sort_values().index[0]
    top_channel, _ = _top_share(transactions["channel"])
    credit = calculate_credit_health(loans)
    profile = enrich_customer_value(customers, accounts)
    premium_bal_share = (
        profile.loc[profile["customer_type"] == "Premium", "total_balance"].sum()
        / max(profile["total_balance"].sum(), 1)
        * 100
    )

    return [
        {
            "priority": "High",
            "area": "Credit Risk",
            "recommendation": f"Increase collection efforts for overdue loans in {risk_region}.",
            "benefit": "Reduce default rate and stabilize NPL proxy.",
            "timeline": "30 Days",
        },
        {
            "priority": "High",
            "area": "Digital / Operations",
            "recommendation": f"Scale {top_channel} and USSD capacity for month-end peaks.",
            "benefit": "Protect service quality during salary and billing cycles.",
            "timeline": "30 Days",
        },
        {
            "priority": "Medium",
            "area": "Retail Banking",
            "recommendation": f"Launch acquisition campaigns in underrepresented regions such as {low_region}.",
            "benefit": "Diversify customer concentration beyond top markets.",
            "timeline": "60 Days",
        },
        {
            "priority": "Medium",
            "area": "Wealth / Premium",
            "recommendation": "Deploy retention and cross-sell programs for Premium high-balance customers.",
            "benefit": f"Protect the ~{premium_bal_share:.0f}% of balances concentrated in Premium.",
            "timeline": "60 Days",
        },
        {
            "priority": "Medium",
            "area": "Credit Policy",
            "recommendation": "Tighten early-warning follow-up for Late (watchlist) loans before they default.",
            "benefit": f"Defend the {credit['on_time_rate']:.1f}% on-time repayment rate.",
            "timeline": "45 Days",
        },
    ]


def build_customer_insights(customers: pd.DataFrame, accounts: pd.DataFrame) -> dict[str, dict[str, str]]:
    """Finding / recommendation blocks for customer charts."""
    profile = enrich_customer_value(customers, accounts)
    top_region, region_share = _top_share(customers["region"])
    bottom_region = customers["region"].value_counts().sort_values().index[0]
    top_age, age_share = _top_share(customers["customer_age_group"])
    premium_share = (customers["customer_type"] == "Premium").mean() * 100
    premium_bal = (
        profile.loc[profile["customer_type"] == "Premium", "total_balance"].sum()
        / max(profile["total_balance"].sum(), 1)
        * 100
    )
    top_occ = customers["occupation"].value_counts().idxmax()

    return {
        "region": {
            "finding": f"{top_region} contributes {region_share:.1f}% of customers.",
            "impact": "Growth and service capacity are concentrated in a few markets.",
            "recommendation": (
                f"Prioritize acquisition campaigns in underrepresented regions such as {bottom_region}."
            ),
        },
        "segment": {
            "finding": (
                f"Premium customers represent {premium_share:.1f}% of the base but contribute "
                f"{premium_bal:.1f}% of balances."
            ),
            "impact": "A small segment drives a disproportionate share of deposit value.",
            "recommendation": "Develop targeted retention and cross-selling programs for Premium customers.",
        },
        "age": {
            "finding": f"Most customers fall in the {top_age} age band ({age_share:.1f}%).",
            "impact": "Product demand will skew toward working-age digital and credit needs.",
            "recommendation": "Focus digital lending and investment products on this demographic.",
        },
        "occupation": {
            "finding": f"{top_occ} is the largest occupation group in the current view.",
            "impact": "Occupation mix shapes cash-flow patterns and product fit.",
            "recommendation": "Introduce tailored SME and salaried banking bundles for top occupation segments.",
        },
        "value": {
            "finding": "Average balances differ materially by customer type.",
            "impact": "Wallet share is uneven across Basic, Standard, and Premium tiers.",
            "recommendation": "Use tiered relationship management to grow Standard customers into Premium.",
        },
    }


def build_transaction_insights(transactions: pd.DataFrame) -> dict[str, dict[str, str]]:
    """Finding / impact / recommendation blocks for transaction charts."""
    top_channel, channel_share = _top_share(transactions["channel"])
    digital_share = transactions["channel"].isin(DIGITAL_CHANNELS).mean() * 100
    top_type, type_share = _top_share(transactions["transaction_type"])

    value_by_region = transactions.groupby("region")["amount"].sum().sort_values(ascending=False)
    top_value_region = value_by_region.index[0]
    top_value_share = value_by_region.iloc[0] / value_by_region.sum() * 100
    low_value_region = value_by_region.index[-1]

    monthly = (
        transactions.assign(period=transactions["transaction_date"].dt.to_period("M").astype(str))
        .groupby("period")
        .size()
    )
    peak_month = monthly.idxmax()

    # Day-of-month pattern for month-end insight
    transactions = transactions.copy()
    transactions["day"] = transactions["transaction_date"].dt.day
    late_month_share = (transactions["day"] >= 25).mean() * 100

    return {
        "channel": {
            "finding": f"{top_channel} accounts for {channel_share:.1f}% of transactions; digital channels are {digital_share:.0f}%.",
            "impact": "Customers increasingly prefer self-service channels over branch visits.",
            "recommendation": "Increase investment in mobile banking infrastructure and customer support.",
        },
        "trend": {
            "finding": (
                f"Peak activity month is {peak_month}; about {late_month_share:.0f}% of transactions "
                "occur on day 25 or later."
            ),
            "impact": "Systems experience elevated demand during salary and billing windows.",
            "recommendation": "Scale infrastructure during expected peak periods (month-end).",
        },
        "type": {
            "finding": f"{top_type} is the most common transaction type ({type_share:.1f}% of volume).",
            "impact": "Product and fee strategy should align with dominant payment behaviors.",
            "recommendation": "Optimize fees and journey design for the top transaction types.",
        },
        "region": {
            "finding": f"{top_value_region} generates {top_value_share:.1f}% of transaction value.",
            "impact": "Operational and revenue risk is concentrated in one region.",
            "recommendation": (
                f"Expand digital campaigns in lower-performing regions such as {low_value_region} "
                "to diversify volumes."
            ),
        },
        "value_channel": {
            "finding": "Channel value and channel volume are not identical — some channels move larger tickets.",
            "impact": "Cost-to-serve and capacity planning must consider value, not only volume.",
            "recommendation": "Invest first where high volume and high value intersect.",
        },
    }


def build_loan_insights(loans: pd.DataFrame, loans_customers: pd.DataFrame) -> dict[str, dict[str, str]]:
    """Finding / interpretation / decision blocks for loan charts."""
    credit = calculate_credit_health(loans)
    top_product = loans.groupby("loan_type")["loan_amount"].sum().sort_values(ascending=False)
    top_name = top_product.index[0]
    top_share = top_product.iloc[0] / top_product.sum() * 100
    high_risk_share = (loans["risk_category"] == "High Risk").mean() * 100

    regional = (
        loans_customers.groupby("region")
        .agg(default_rate=("repayment_status", lambda s: (s == "Default").mean() * 100))
        .sort_values("default_rate", ascending=False)
    )
    risk_region = regional.index[0]
    risk_rate = float(regional.iloc[0]["default_rate"])

    return {
        "products": {
            "finding": f"{top_name} accounts for {top_share:.1f}% of portfolio value.",
            "impact": "Lending concentration affects capital allocation and sector risk.",
            "recommendation": "Continue supporting core lending products while monitoring concentration limits.",
        },
        "repayment": {
            "finding": f"{credit['on_time_rate']:.1f}% of loans are repaid on time.",
            "impact": "Repayment performance is the primary signal of underwriting quality.",
            "recommendation": "Maintain current underwriting policies while strengthening follow-up for late repayments.",
        },
        "risk": {
            "finding": f"High-risk loans represent {high_risk_share:.1f}% of the book.",
            "impact": "Elevated high-risk share increases provisioning and collections workload.",
            "recommendation": "Review approval criteria for high-risk customer segments.",
        },
        "region": {
            "finding": f"{risk_region} has the highest default rate at {risk_rate:.1f}%.",
            "impact": "Geographic credit risk is uneven and may require localized controls.",
            "recommendation": "Deploy additional credit monitoring and collections resources in this region.",
        },
        "size": {
            "finding": "Loan amounts are skewed — a minority of large facilities drive portfolio value.",
            "impact": "Large-ticket loans dominate credit exposure and loss severity risk.",
            "recommendation": "Apply enhanced monitoring to large loans and SME facilities.",
        },
    }


def annotate_bar_extremes(fig: go.Figure, df: pd.DataFrame, x: str, y: str) -> go.Figure:
    """Highlight highest and lowest bars with annotations."""
    if df.empty:
        return fig
    ordered = df.sort_values(y)
    low = ordered.iloc[0]
    high = ordered.iloc[-1]
    fig.add_annotation(x=high[x], y=high[y], text="Highest", showarrow=True, arrowhead=1, bgcolor="#e8f5e9")
    fig.add_annotation(x=low[x], y=low[y], text="Lowest", showarrow=True, arrowhead=1, bgcolor="#ffebee")
    return fig


def create_channel_chart_with_target(transactions: pd.DataFrame) -> go.Figure:
    """Channel usage chart with digital-adoption context."""
    summary = transactions["channel"].value_counts().reset_index()
    summary.columns = ["channel", "transaction_count"]
    fig = px.bar(
        summary,
        x="channel",
        y="transaction_count",
        color="channel",
        title="Which channels do customers use?",
        labels={"channel": "Channel", "transaction_count": "Transactions"},
    )
    fig = apply_chart_theme(fig, subtitle=f"Board target: digital adoption ≥ {TARGET_DIGITAL_ADOPTION:.0f}%")
    return annotate_bar_extremes(fig, summary, "channel", "transaction_count")


def create_repayment_chart_with_target(loans: pd.DataFrame) -> go.Figure:
    """Repayment status with on-time target reference in subtitle."""
    summary = loans["repayment_status"].value_counts().reindex(["On Time", "Late", "Default"]).reset_index()
    summary.columns = ["repayment_status", "loan_count"]
    credit = calculate_credit_health(loans)
    fig = px.bar(
        summary,
        x="repayment_status",
        y="loan_count",
        color="repayment_status",
        color_discrete_map={"On Time": "#2e7d32", "Late": "#f9a825", "Default": "#c62828"},
        title="How healthy is repayment performance?",
    )
    return apply_chart_theme(
        fig,
        subtitle=f"On-time {credit['on_time_rate']:.1f}% · Board target ≥ {TARGET_ON_TIME:.0f}% · NPL proxy target ≤ {TARGET_NPL_RATIO:.0f}%",
    )


def create_default_by_region_chart(loans_customers: pd.DataFrame) -> go.Figure:
    """Default rate by region with annotations."""
    regional = (
        loans_customers.groupby("region", as_index=False)
        .agg(default_rate=("repayment_status", lambda s: (s == "Default").mean() * 100))
        .sort_values("default_rate", ascending=False)
    )
    fig = px.bar(
        regional,
        x="region",
        y="default_rate",
        color="region",
        title="Which regions have the highest default rates?",
        labels={"default_rate": "Default Rate (%)"},
    )
    fig.add_hline(y=3.0, line_dash="dash", line_color="#c62828", annotation_text="Soft default target 3%")
    fig = apply_chart_theme(fig, subtitle="Higher bars indicate regions needing closer credit monitoring.")
    return annotate_bar_extremes(fig, regional, "region", "default_rate")
