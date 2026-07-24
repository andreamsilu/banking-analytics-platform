"""
Synthetic Tanzania Banking Data Generator.

Generates realistic customer, account, transaction, and loan datasets
for the Banking Analytics Intelligence Platform portfolio project.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

DEFAULT_CUSTOMER_COUNT = 100_000
DEFAULT_ACCOUNT_COUNT = 150_000
DEFAULT_TRANSACTION_COUNT = 1_000_000
DEFAULT_LOAN_COUNT = 50_000

RANDOM_SEED = 42

TANZANIA_REGIONS = [
    "Dar es Salaam",
    "Arusha",
    "Mwanza",
    "Dodoma",
    "Mbeya",
    "Morogoro",
    "Tanga",
    "Zanzibar",
    "Kilimanjaro",
    "Tabora",
]

CUSTOMER_TYPES = ["Premium", "Standard", "Basic"]
CUSTOMER_TYPE_WEIGHTS = [0.15, 0.55, 0.30]

GENDERS = ["Male", "Female"]

OCCUPATIONS = [
    "Teacher",
    "Farmer",
    "Business Owner",
    "Civil Servant",
    "Student",
    "Engineer",
    "Nurse",
    "Driver",
    "Retail Worker",
    "Accountant",
    "Entrepreneur",
    "Healthcare Worker",
    "Construction Worker",
    "Bank Officer",
    "Self Employed",
]

INCOME_LEVELS = ["Low", "Medium", "High", "Very High"]

ACCOUNT_TYPES = ["Savings", "Current", "Fixed Deposit"]
ACCOUNT_TYPE_WEIGHTS = [0.55, 0.35, 0.10]

ACCOUNT_STATUSES = ["Active", "Inactive", "Closed"]
ACCOUNT_STATUS_WEIGHTS = [0.90, 0.07, 0.03]

CURRENCY = "TZS"

CHANNELS = ["Mobile App", "USSD", "ATM", "Branch", "Internet Banking"]
CHANNEL_WEIGHTS = [0.45, 0.30, 0.15, 0.07, 0.03]

TRANSACTION_TYPES = [
    "Deposit",
    "Withdrawal",
    "Transfer",
    "Bill Payment",
    "Merchant Payment",
    "Loan Repayment",
]

MERCHANT_CATEGORIES = [
    "Shopping",
    "Food",
    "Transport",
    "Utilities",
    "Education",
    "Healthcare",
]

LOAN_TYPES = [
    "Personal Loan",
    "Business Loan",
    "Education Loan",
    "Vehicle Loan",
    "Mortgage",
]

REPAYMENT_STATUSES = ["On Time", "Late", "Default"]
REPAYMENT_STATUS_WEIGHTS = [0.82, 0.13, 0.05]

LOAN_STATUSES = ["Active", "Closed", "Defaulted"]

# Typical TZS transaction amount ranges (min, max) by channel.
CHANNEL_AMOUNT_RANGES: dict[str, tuple[int, int]] = {
    "Mobile App": (1_000, 2_000_000),
    "USSD": (1_000, 1_500_000),
    "ATM": (10_000, 5_000_000),
    "Branch": (100_000, 50_000_000),
    "Internet Banking": (50_000, 20_000_000),
}

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Configure console logging for pipeline progress."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )


def _random_dates(
    start: date,
    end: date,
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate random dates between start and end (inclusive)."""
    start_ord = start.toordinal()
    end_ord = end.toordinal()
    day_offsets = rng.integers(0, end_ord - start_ord + 1, size=size)
    return np.array([date.fromordinal(start_ord + int(offset)) for offset in day_offsets])


def _random_times(size: int, rng: np.random.Generator) -> list[str]:
    """Generate random transaction times formatted as HH:MM:SS."""
    total_seconds = rng.integers(0, 24 * 60 * 60, size=size)
    return [
        time(hour=seconds // 3600, minute=(seconds % 3600) // 60, second=seconds % 60).isoformat()
        for seconds in total_seconds
    ]


def _lognormal_amounts(
    size: int,
    low: int,
    high: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Generate skewed monetary amounts within a realistic TZS range.

    Uses a log-normal distribution clipped to [low, high].
    """
    mu = np.log((low + high) / 2)
    sigma = 0.65
    amounts = rng.lognormal(mean=mu, sigma=sigma, size=size)
    return np.clip(np.round(amounts, -2), low, high).astype(np.int64)


def generate_customers(
    count: int = DEFAULT_CUSTOMER_COUNT,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate a synthetic Tanzania banking customer dataset.

    Parameters
    ----------
    count : int
        Number of customer records to create.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Customer dataset with demographics and segmentation fields.
    """
    logger.info("Generating customers...")
    rng = np.random.default_rng(seed)
    fake = Faker(["en_US"])
    Faker.seed(seed)

    customer_ids = [f"CUST{i:06d}" for i in range(1, count + 1)]
    genders = rng.choice(GENDERS, size=count)
    regions = rng.choice(TANZANIA_REGIONS, size=count)
    occupations = rng.choice(OCCUPATIONS, size=count)
    customer_types = rng.choice(CUSTOMER_TYPES, size=count, p=CUSTOMER_TYPE_WEIGHTS)

    # Birth dates for adults aged 18-75.
    today = date.today()
    max_birth = today.replace(year=today.year - 18)
    min_birth = today.replace(year=today.year - 75)
    birth_dates = _random_dates(min_birth, max_birth, count, rng)
    ages = np.array([(today - dob).days // 365 for dob in birth_dates])

    # Customer relationship start between 5 and 20 years ago.
    earliest_since = today.replace(year=today.year - 20)
    latest_since = today.replace(year=today.year - 1)
    customer_since_dates = _random_dates(earliest_since, latest_since, count, rng)

    # Income level correlates loosely with customer type for realism.
    income_levels = np.empty(count, dtype=object)
    income_rules = {
        "Premium": (["High", "Very High"], [0.45, 0.55]),
        "Standard": (["Low", "Medium", "High"], [0.20, 0.55, 0.25]),
        "Basic": (["Low", "Medium"], [0.70, 0.30]),
    }
    for customer_type, (choices, weights) in income_rules.items():
        mask = customer_types == customer_type
        income_levels[mask] = rng.choice(choices, size=int(mask.sum()), p=weights)

    # Faker names are generated row-wise for natural full names.
    full_names = [fake.name() for _ in range(count)]

    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "full_name": full_names,
            "gender": genders,
            "date_of_birth": birth_dates,
            "age": ages,
            "region": regions,
            "occupation": occupations,
            "income_level": income_levels,
            "customer_since": customer_since_dates,
            "customer_type": customer_types,
        }
    )

    logger.info("%s customers created", f"{count:,}")
    return customers


def generate_accounts(
    customers: pd.DataFrame,
    count: int = DEFAULT_ACCOUNT_COUNT,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate bank accounts linked to existing customers.

    Parameters
    ----------
    customers : pd.DataFrame
        Customer dataset produced by ``generate_customers``.
    count : int
        Number of account records to create.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Account dataset with balances and status metadata.
    """
    logger.info("Generating accounts...")
    rng = np.random.default_rng(seed)

    if customers.empty:
        raise ValueError("Customer dataset is empty. Generate customers first.")

    customer_ids = customers["customer_id"].to_numpy()
    linked_customers = rng.choice(customer_ids, size=count, replace=True)

    account_types = rng.choice(ACCOUNT_TYPES, size=count, p=ACCOUNT_TYPE_WEIGHTS)
    statuses = rng.choice(ACCOUNT_STATUSES, size=count, p=ACCOUNT_STATUS_WEIGHTS)

    today = date.today()
    earliest_opening = today.replace(year=today.year - 15)
    latest_opening = today
    opening_dates = _random_dates(earliest_opening, latest_opening, count, rng)

    balances = np.zeros(count, dtype=np.int64)
    for account_type in ACCOUNT_TYPES:
        mask = account_types == account_type
        segment_size = int(mask.sum())
        if segment_size == 0:
            continue

        if account_type == "Savings":
            balances[mask] = _lognormal_amounts(segment_size, 50_000, 30_000_000, rng)
        elif account_type == "Current":
            balances[mask] = _lognormal_amounts(segment_size, 100_000, 80_000_000, rng)
        else:
            balances[mask] = _lognormal_amounts(segment_size, 1_000_000, 500_000_000, rng)

    # Closed or inactive accounts tend to hold lower residual balances.
    closed_mask = statuses == "Closed"
    inactive_mask = statuses == "Inactive"
    balances[closed_mask] = rng.integers(0, 50_000, size=int(closed_mask.sum()))
    balances[inactive_mask] = (balances[inactive_mask] * rng.uniform(0.05, 0.4, size=int(inactive_mask.sum()))).astype(np.int64)

    accounts = pd.DataFrame(
        {
            "account_id": [f"ACC{i:07d}" for i in range(1, count + 1)],
            "customer_id": linked_customers,
            "account_type": account_types,
            "opening_date": opening_dates,
            "balance": balances,
            "currency": CURRENCY,
            "status": statuses,
        }
    )

    logger.info("%s accounts created", f"{count:,}")
    return accounts


def generate_transactions(
    accounts: pd.DataFrame,
    customers: pd.DataFrame,
    count: int = DEFAULT_TRANSACTION_COUNT,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate transaction activity for 2025-2026.

    Mobile and USSD channels receive smaller average amounts than branch
    transactions, reflecting typical Tanzanian digital banking behavior.

    Parameters
    ----------
    accounts : pd.DataFrame
        Account dataset produced by ``generate_accounts``.
    customers : pd.DataFrame
        Customer dataset for regional lookup.
    count : int
        Number of transaction records to create.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Transaction dataset with channel, type, and amount details.
    """
    logger.info("Generating transactions...")
    rng = np.random.default_rng(seed)

    if accounts.empty:
        raise ValueError("Account dataset is empty. Generate accounts first.")

    active_accounts = accounts.loc[accounts["status"] == "Active", ["account_id", "customer_id"]]
    if active_accounts.empty:
        raise ValueError("No active accounts available for transaction generation.")

    sampled_accounts = active_accounts.sample(
        n=count,
        replace=True,
        random_state=seed,
    ).reset_index(drop=True)

    channels = rng.choice(CHANNELS, size=count, p=CHANNEL_WEIGHTS)
    transaction_types = rng.choice(TRANSACTION_TYPES, size=count)
    merchant_categories = rng.choice(MERCHANT_CATEGORIES, size=count)

    transaction_dates = _random_dates(date(2025, 1, 1), date(2026, 12, 31), count, rng)
    transaction_times = _random_times(count, rng)

    amounts = np.zeros(count, dtype=np.int64)
    for channel in CHANNELS:
        mask = channels == channel
        segment_size = int(mask.sum())
        if segment_size == 0:
            continue
        low, high = CHANNEL_AMOUNT_RANGES[channel]
        amounts[mask] = _lognormal_amounts(segment_size, low, high, rng)

    customer_regions = customers.set_index("customer_id")["region"]
    regions = sampled_accounts["customer_id"].map(customer_regions).to_numpy()

    transactions = pd.DataFrame(
        {
            "transaction_id": [f"TXN{i:08d}" for i in range(1, count + 1)],
            "customer_id": sampled_accounts["customer_id"].to_numpy(),
            "account_id": sampled_accounts["account_id"].to_numpy(),
            "transaction_date": transaction_dates,
            "transaction_time": transaction_times,
            "channel": channels,
            "transaction_type": transaction_types,
            "amount": amounts,
            "merchant_category": merchant_categories,
            "region": regions,
        }
    )

    logger.info("%s transactions created", f"{count:,}")
    return transactions


def generate_loans(
    customers: pd.DataFrame,
    count: int = DEFAULT_LOAN_COUNT,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate a synthetic loan portfolio linked to customers.

    Parameters
    ----------
    customers : pd.DataFrame
        Customer dataset produced by ``generate_customers``.
    count : int
        Number of loan records to create.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Loan dataset with amount, rate, and repayment metadata.
    """
    logger.info("Generating loans...")
    rng = np.random.default_rng(seed)

    if customers.empty:
        raise ValueError("Customer dataset is empty. Generate customers first.")

    customer_ids = customers["customer_id"].to_numpy()
    linked_customers = rng.choice(customer_ids, size=count, replace=True)
    loan_types = rng.choice(LOAN_TYPES, size=count)
    repayment_statuses = rng.choice(
        REPAYMENT_STATUSES,
        size=count,
        p=REPAYMENT_STATUS_WEIGHTS,
    )

    today = date.today()
    earliest_loan = date(2018, 1, 1)
    latest_loan = date(2026, 12, 31)
    loan_dates = _random_dates(earliest_loan, latest_loan, count, rng)
    duration_months = rng.integers(6, 240, size=count)

    loan_amounts = np.zeros(count, dtype=np.int64)
    interest_rates = np.zeros(count, dtype=float)

    loan_amount_ranges = {
        "Personal Loan": (500_000, 30_000_000),
        "Business Loan": (2_000_000, 200_000_000),
        "Education Loan": (1_000_000, 25_000_000),
        "Vehicle Loan": (5_000_000, 80_000_000),
        "Mortgage": (50_000_000, 1_000_000_000),
    }
    interest_rate_ranges = {
        "Personal Loan": (14.0, 22.0),
        "Business Loan": (15.0, 24.0),
        "Education Loan": (12.0, 18.0),
        "Vehicle Loan": (13.0, 20.0),
        "Mortgage": (11.0, 16.0),
    }

    for loan_type in LOAN_TYPES:
        mask = loan_types == loan_type
        segment_size = int(mask.sum())
        if segment_size == 0:
            continue

        low, high = loan_amount_ranges[loan_type]
        rate_low, rate_high = interest_rate_ranges[loan_type]
        loan_amounts[mask] = _lognormal_amounts(segment_size, low, high, rng)
        interest_rates[mask] = np.round(rng.uniform(rate_low, rate_high, size=segment_size), 2)

    maturity_ordinals = np.array(
        [loan_date.toordinal() + 30 * int(months) for loan_date, months in zip(loan_dates, duration_months)]
    )
    loan_statuses = np.where(
        repayment_statuses == "Default",
        "Defaulted",
        np.where(maturity_ordinals < today.toordinal(), "Closed", "Active"),
    )

    # Contractual interest amounts stored as first-class loan attributes.
    monthly_interest = np.round(loan_amounts * (interest_rates / 100.0) / 12.0, 2)
    total_contractual_interest = np.round(monthly_interest * duration_months, 2)

    loans = pd.DataFrame(
        {
            "loan_id": [f"LOAN{i:06d}" for i in range(1, count + 1)],
            "customer_id": linked_customers,
            "loan_type": loan_types,
            "loan_amount": loan_amounts,
            "interest_rate": interest_rates,
            "loan_date": loan_dates,
            "duration_months": duration_months,
            "repayment_status": repayment_statuses,
            "loan_status": loan_statuses,
            "monthly_interest": monthly_interest,
            "total_contractual_interest": total_contractual_interest,
        }
    )

    logger.info("%s loans created", f"{count:,}")
    return loans


def save_dataset(df: pd.DataFrame, filename: str, output_dir: Path = RAW_DATA_DIR) -> Path:
    """
    Persist a dataset to CSV in the raw data directory.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to export.
    filename : str
        Target CSV filename.
    output_dir : Path
        Destination directory.

    Returns
    -------
    Path
        Full path to the saved CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    df.to_csv(output_path, index=False)
    logger.info("Saved %s", output_path)
    return output_path


def main() -> None:
    """Run the full synthetic data generation pipeline."""
    _configure_logging()
    start_time = datetime.now()

    logger.info("Starting Banking Analytics data generation pipeline...")
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    customers = generate_customers()
    accounts = generate_accounts(customers)
    transactions = generate_transactions(accounts, customers)
    loans = generate_loans(customers)

    save_dataset(customers, "customers.csv")
    save_dataset(accounts, "accounts.csv")
    save_dataset(transactions, "transactions.csv")
    save_dataset(loans, "loans.csv")

    elapsed = datetime.now() - start_time
    logger.info("Pipeline completed in %s", elapsed)


if __name__ == "__main__":
    main()
