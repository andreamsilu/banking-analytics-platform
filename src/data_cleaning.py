"""
Banking Analytics Data Cleaning Pipeline.

Loads raw Tanzania banking datasets, performs data quality checks, applies
cleansing rules, engineers analytics features, and exports analysis-ready files.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths and reference values (aligned with data_generator.py)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

VALID_ACCOUNT_TYPES = {"Savings", "Current", "Fixed Deposit"}
VALID_ACCOUNT_STATUSES = {"Active", "Inactive", "Closed"}
VALID_CHANNELS = {"Mobile App", "USSD", "ATM", "Branch", "Internet Banking"}
VALID_TRANSACTION_TYPES = {
    "Deposit",
    "Withdrawal",
    "Transfer",
    "Bill Payment",
    "Merchant Payment",
    "Loan Repayment",
}
VALID_LOAN_TYPES = {
    "Personal Loan",
    "Business Loan",
    "Education Loan",
    "Vehicle Loan",
    "Mortgage",
}
VALID_REPAYMENT_STATUSES = {"On Time", "Late", "Default"}
VALID_LOAN_STATUSES = {"Active", "Closed", "Defaulted"}
VALID_CUSTOMER_TYPES = {"Premium", "Standard", "Basic"}
VALID_GENDERS = {"Male", "Female"}
VALID_INCOME_LEVELS = {"Low", "Medium", "High", "Very High"}

MIN_CUSTOMER_AGE = 18
MAX_CUSTOMER_AGE = 100

DATE_COLUMNS = {
    "customers": ["date_of_birth", "customer_since"],
    "accounts": ["opening_date"],
    "transactions": ["transaction_date"],
    "loans": ["loan_date"],
}

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Configure console logging for the cleaning pipeline."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")


# ---------------------------------------------------------------------------
# TASK 1: Load datasets
# ---------------------------------------------------------------------------


def load_customers(data_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load the raw customer dataset from CSV."""
    return pd.read_csv(data_dir / "customers.csv")


def load_accounts(data_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load the raw account dataset from CSV."""
    return pd.read_csv(data_dir / "accounts.csv")


def load_transactions(data_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load the raw transaction dataset from CSV."""
    return pd.read_csv(data_dir / "transactions.csv")


def load_loans(data_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load the raw loan dataset from CSV."""
    return pd.read_csv(data_dir / "loans.csv")


# ---------------------------------------------------------------------------
# TASK 2: Data quality checks
# ---------------------------------------------------------------------------


def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify missing values per column.

    Missing demographic or financial fields can bias customer segmentation
    and regulatory reporting, so analysts quantify gaps before imputation.
    """
    missing = df.isna().sum()
    report = (
        pd.DataFrame({"Column": missing.index, "Missing": missing.values})
        .loc[lambda frame: frame["Missing"] > 0]
        .sort_values("Missing", ascending=False)
        .reset_index(drop=True)
    )
    return report


def check_duplicates(df: pd.DataFrame) -> int:
    """
    Count fully duplicated records.

    Duplicate banking records inflate balances and transaction volumes,
    leading to incorrect KPIs if not removed.
    """
    return int(df.duplicated().sum())


def check_data_types(df: pd.DataFrame, dataset_name: str) -> list[str]:
    """
    Flag columns that should use datetime types but are still strings.

    Accurate date typing is required for time-series analysis, cohort studies,
    and month-over-month reporting in banking dashboards.
    """
    issues: list[str] = []
    expected_dates = DATE_COLUMNS.get(dataset_name, [])

    for column in expected_dates:
        if column in df.columns and not pd.api.types.is_datetime64_any_dtype(df[column]):
            issues.append(f"{column} should be datetime")

    numeric_expectations = {
        "customers": ["age"],
        "accounts": ["balance"],
        "transactions": ["amount"],
        "loans": ["loan_amount", "interest_rate", "duration_months"],
    }
    for column in numeric_expectations.get(dataset_name, []):
        if column in df.columns and not pd.api.types.is_numeric_dtype(df[column]):
            issues.append(f"{column} should be numeric")

    return issues


def generate_data_quality_report(df: pd.DataFrame, dataset_name: str) -> None:
    """Display a consolidated data quality summary for one dataset."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("DATA QUALITY REPORT: %s", dataset_name.upper())
    logger.info("=" * 60)
    logger.info("Rows: %s", f"{len(df):,}")
    logger.info("Columns: %s", len(df.columns))

    missing_report = check_missing_values(df)
    if missing_report.empty:
        logger.info("Missing values: none")
    else:
        logger.info("Missing values:")
        for _, row in missing_report.iterrows():
            logger.info("  %-25s %s", row["Column"], f"{int(row['Missing']):,}")

    duplicate_count = check_duplicates(df)
    logger.info("Duplicate rows found: %s", f"{duplicate_count:,}")

    type_issues = check_data_types(df, dataset_name)
    logger.info("Data types:")
    for column in df.columns:
        logger.info("  %-25s %s", column, df[column].dtype)
    if type_issues:
        logger.info("Type issues detected:")
        for issue in type_issues:
            logger.info("  - %s", issue)
    else:
        logger.info("Type issues detected: none")


# ---------------------------------------------------------------------------
# TASK 3 & 4: Cleaning and feature engineering
# ---------------------------------------------------------------------------


def _assign_customer_age_group(age: int) -> str | float:
    """Map customer age to a banking segmentation band."""
    if pd.isna(age):
        return np.nan
    age = int(age)
    if MIN_CUSTOMER_AGE <= age <= 30:
        return "18-30"
    if 31 <= age <= 45:
        return "31-45"
    if 46 <= age <= 60:
        return "46-60"
    if age > 60:
        return "60+"
    return np.nan


def _assign_loan_risk_category(repayment_status: str) -> str | float:
    """Translate repayment behavior into a portfolio risk label."""
    mapping = {
        "Default": "High Risk",
        "Late": "Medium Risk",
        "On Time": "Low Risk",
    }
    return mapping.get(repayment_status, np.nan)


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and enrich the customer dataset.

    Banks require reliable KYC fields for compliance, segmentation, and
    cross-sell models. Invalid ages and duplicate IDs are removed to protect
    downstream analytics accuracy.
    """
    cleaned = df.copy()
    initial_rows = len(cleaned)

    # Remove duplicate customer records to avoid double-counting clients.
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.drop_duplicates(subset=["customer_id"], keep="first")

    # Parse relationship dates for tenure and cohort analysis.
    cleaned["date_of_birth"] = pd.to_datetime(cleaned["date_of_birth"], errors="coerce")
    cleaned["customer_since"] = pd.to_datetime(cleaned["customer_since"], errors="coerce")

    cleaned["age"] = pd.to_numeric(cleaned["age"], errors="coerce")

    # Impute missing categorical values with the mode to retain sample size.
    for column in ["gender", "region", "occupation", "income_level", "customer_type"]:
        if column in cleaned.columns and cleaned[column].isna().any():
            mode_value = cleaned[column].mode(dropna=True)
            if not mode_value.empty:
                cleaned[column] = cleaned[column].fillna(mode_value.iloc[0])

    # Drop rows that cannot be validated for age-based banking rules.
    cleaned = cleaned.dropna(subset=["customer_id", "date_of_birth", "age"])
    cleaned = cleaned[
        (cleaned["age"] >= MIN_CUSTOMER_AGE) & (cleaned["age"] <= MAX_CUSTOMER_AGE)
    ]

    # Standardize controlled vocabularies used in reporting.
    cleaned = cleaned[cleaned["customer_type"].isin(VALID_CUSTOMER_TYPES)]
    cleaned = cleaned[cleaned["gender"].isin(VALID_GENDERS)]
    cleaned = cleaned[cleaned["income_level"].isin(VALID_INCOME_LEVELS)]

    cleaned["customer_age_group"] = cleaned["age"].apply(_assign_customer_age_group)
    cleaned = cleaned.dropna(subset=["customer_age_group"])

    logger.info(
        "Customers cleaned: %s -> %s rows",
        f"{initial_rows:,}",
        f"{len(cleaned):,}",
    )
    return cleaned.reset_index(drop=True)


def clean_accounts(df: pd.DataFrame, customers: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Clean account balances and statuses.

    Negative balances on active accounts usually indicate data errors rather
    than real overdraft policy outcomes in this synthetic portfolio.
    """
    cleaned = df.copy()
    initial_rows = len(cleaned)

    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.drop_duplicates(subset=["account_id"], keep="first")

    cleaned["opening_date"] = pd.to_datetime(cleaned["opening_date"], errors="coerce")
    cleaned["balance"] = pd.to_numeric(cleaned["balance"], errors="coerce")

    cleaned = cleaned.dropna(subset=["account_id", "customer_id", "opening_date", "balance"])
    cleaned = cleaned[cleaned["balance"] >= 0]
    cleaned = cleaned[cleaned["account_type"].isin(VALID_ACCOUNT_TYPES)]
    cleaned = cleaned[cleaned["status"].isin(VALID_ACCOUNT_STATUSES)]

    if customers is not None:
        valid_customer_ids = set(customers["customer_id"])
        cleaned = cleaned[cleaned["customer_id"].isin(valid_customer_ids)]

    logger.info(
        "Accounts cleaned: %s -> %s rows",
        f"{initial_rows:,}",
        f"{len(cleaned):,}",
    )
    return cleaned.reset_index(drop=True)


def clean_transactions(
    df: pd.DataFrame,
    accounts: pd.DataFrame | None = None,
    customers: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Clean transactional activity and derive time-based features.

    Channel validation ensures digital adoption metrics are not distorted by
    miscoded records. Zero-value transactions are removed because they do not
    represent meaningful monetary movement for value-based KPIs.
    """
    cleaned = df.copy()
    initial_rows = len(cleaned)

    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.drop_duplicates(subset=["transaction_id"], keep="first")

    cleaned["transaction_date"] = pd.to_datetime(cleaned["transaction_date"], errors="coerce")
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")

    cleaned = cleaned.dropna(
        subset=["transaction_id", "customer_id", "account_id", "transaction_date", "amount"]
    )
    cleaned = cleaned[cleaned["amount"] > 0]
    cleaned = cleaned[cleaned["channel"].isin(VALID_CHANNELS)]
    cleaned = cleaned[cleaned["transaction_type"].isin(VALID_TRANSACTION_TYPES)]

    if accounts is not None:
        valid_account_ids = set(accounts["account_id"])
        cleaned = cleaned[cleaned["account_id"].isin(valid_account_ids)]

    if customers is not None:
        valid_customer_ids = set(customers["customer_id"])
        cleaned = cleaned[cleaned["customer_id"].isin(valid_customer_ids)]

    # Time features support monthly trend and peak-hour channel analysis.
    cleaned["transaction_month"] = cleaned["transaction_date"].dt.month_name()
    cleaned["transaction_year"] = cleaned["transaction_date"].dt.year
    cleaned["transaction_hour"] = pd.to_datetime(
        cleaned["transaction_time"].astype(str),
        format="%H:%M:%S",
        errors="coerce",
    ).dt.hour

    cleaned = cleaned.dropna(subset=["transaction_hour"])

    logger.info(
        "Transactions cleaned: %s -> %s rows",
        f"{initial_rows:,}",
        f"{len(cleaned):,}",
    )
    return cleaned.reset_index(drop=True)


def clean_loans(df: pd.DataFrame, customers: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Clean loan portfolio records and derive credit risk categories.

    Repayment status is a primary credit risk indicator used by banks for
    provisioning, collections strategy, and portfolio health monitoring.
    """
    cleaned = df.copy()
    initial_rows = len(cleaned)

    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.drop_duplicates(subset=["loan_id"], keep="first")

    cleaned["loan_date"] = pd.to_datetime(cleaned["loan_date"], errors="coerce")
    cleaned["loan_amount"] = pd.to_numeric(cleaned["loan_amount"], errors="coerce")
    cleaned["interest_rate"] = pd.to_numeric(cleaned["interest_rate"], errors="coerce")
    cleaned["duration_months"] = pd.to_numeric(cleaned["duration_months"], errors="coerce")

    cleaned = cleaned.dropna(
        subset=[
            "loan_id",
            "customer_id",
            "loan_date",
            "loan_amount",
            "interest_rate",
            "duration_months",
            "repayment_status",
        ]
    )
    cleaned = cleaned[cleaned["loan_amount"] > 0]
    cleaned = cleaned[cleaned["interest_rate"] > 0]
    cleaned = cleaned[cleaned["duration_months"] > 0]
    cleaned = cleaned[cleaned["loan_type"].isin(VALID_LOAN_TYPES)]
    cleaned = cleaned[cleaned["repayment_status"].isin(VALID_REPAYMENT_STATUSES)]
    cleaned = cleaned[cleaned["loan_status"].isin(VALID_LOAN_STATUSES)]

    if customers is not None:
        valid_customer_ids = set(customers["customer_id"])
        cleaned = cleaned[cleaned["customer_id"].isin(valid_customer_ids)]

    cleaned["risk_category"] = cleaned["repayment_status"].map(_assign_loan_risk_category)

    logger.info(
        "Loans cleaned: %s -> %s rows",
        f"{initial_rows:,}",
        f"{len(cleaned):,}",
    )
    return cleaned.reset_index(drop=True)


# ---------------------------------------------------------------------------
# TASK 5: Save processed datasets
# ---------------------------------------------------------------------------


def save_cleaned_dataset(
    df: pd.DataFrame,
    filename: str,
    output_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Persist a cleaned dataset to the processed data directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    df.to_csv(output_path, index=False)
    logger.info("Saved %s", output_path)
    return output_path


# ---------------------------------------------------------------------------
# TASK 6: Main pipeline
# ---------------------------------------------------------------------------


def main() -> None:
    """Execute the full data quality, cleaning, and export workflow."""
    _configure_logging()
    logger.info("Starting data cleaning pipeline")

    customers_raw = load_customers()
    accounts_raw = load_accounts()
    transactions_raw = load_transactions()
    loans_raw = load_loans()

    for dataset_name, frame in [
        ("customers", customers_raw),
        ("accounts", accounts_raw),
        ("transactions", transactions_raw),
        ("loans", loans_raw),
    ]:
        generate_data_quality_report(frame, dataset_name)

    customers_clean = clean_customers(customers_raw)
    accounts_clean = clean_accounts(accounts_raw, customers_clean)
    transactions_clean = clean_transactions(
        transactions_raw,
        accounts_clean,
        customers_clean,
    )
    loans_clean = clean_loans(loans_raw, customers_clean)

    save_cleaned_dataset(customers_clean, "customers_clean.csv")
    save_cleaned_dataset(accounts_clean, "accounts_clean.csv")
    save_cleaned_dataset(transactions_clean, "transactions_clean.csv")
    save_cleaned_dataset(loans_clean, "loans_clean.csv")

    logger.info("")
    logger.info("Cleaning completed")
    logger.info(
        "Processed files written to %s",
        PROCESSED_DATA_DIR,
    )


if __name__ == "__main__":
    main()
