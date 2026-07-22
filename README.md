# Banking Analytics Intelligence Platform Using Python

An end-to-end banking analytics platform for Tanzania financial institutions. It covers data generation, data quality and cleaning, exploratory analysis, and an executive Streamlit BI dashboard for customer, payment, and credit decision support.

## Technology Stack

- Python 3.12+
- Pandas, NumPy
- Faker
- Matplotlib, Seaborn, Plotly
- Jupyter Notebook
- Streamlit

## Project Structure

```
Banking-Analytics-Platform/
├── data/
│   ├── raw/              # Landing-zone source extracts
│   ├── processed/        # Cleaned warehouse tables
│   └── analytics/        # Published analytics mart (cloud / GitHub)
├── notebooks/
├── src/
│   ├── data_generator.py
│   ├── data_cleaning.py
│   ├── dashboard_utils.py
│   └── executive_bi.py
├── dashboards/
│   └── app.py
├── reports/
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

## Data Generation

Generate banking datasets:

```bash
python src/data_generator.py
```

This creates `customers.csv`, `accounts.csv`, `transactions.csv`, and `loans.csv` in `data/raw/`.

## Data Cleaning Pipeline

### Raw data source

The cleaning pipeline reads Tanzania banking datasets from `data/raw/`:

| File | Description |
|------|-------------|
| `customers.csv` | Customer demographics and segmentation |
| `accounts.csv` | Account balances and status |
| `transactions.csv` | Transaction activity across channels |
| `loans.csv` | Loan portfolio and repayment behavior |

### Cleaning process

```bash
python src/data_cleaning.py
```

The script:

1. Loads raw CSV files into Pandas DataFrames
2. Assesses data quality — missing values, duplicates, and data types
3. Cleans records — business-rule validation and type fixes
4. Engineers features for banking analytics
5. Exports cleaned files to `data/processed/`

### Output datasets

| File | New fields |
|------|------------|
| `customers_clean.csv` | `customer_age_group` |
| `accounts_clean.csv` | — |
| `transactions_clean.csv` | `transaction_month`, `transaction_year`, `transaction_hour` |
| `loans_clean.csv` | `risk_category` |

## Banking Analytics Dashboard

### Purpose

The Streamlit dashboard is an internal executive BI platform for portfolio monitoring and management decisions across customers, payments, and credit risk.

### Features

- **Executive Overview** — KPI ribbon, executive summary, action panel, scorecards
- **Customer Analytics** — demographics, value concentration, regional growth
- **Transaction Analytics** — channel adoption, volume/value trends, regional payments
- **Loan Analytics** — repayment health, risk tiers, regional defaults

### Technologies

- Streamlit for the interactive UI
- Pandas for data processing
- Plotly for interactive charts

Reusable logic lives in `src/dashboard_utils.py` and `src/executive_bi.py`; the UI is in `dashboards/app.py`.

### How to run

```bash
source venv/bin/activate
streamlit run dashboards/app.py
```

Open the local URL shown in the terminal (typically `http://localhost:8501`).

### Deploy on Streamlit Community Cloud

1. Push the repository to GitHub
2. Open [https://share.streamlit.io](https://share.streamlit.io)
3. Create an app with:
   - **Branch:** `main`
   - **Main file path:** `dashboards/app.py`
4. Deploy

The cloud app loads the published analytics mart from `data/analytics/`. Local full extracts remain in `data/processed/` (gitignored) and can be regenerated with:

```bash
python src/data_generator.py
python src/data_cleaning.py
```

## License

Proprietary portfolio project — Banking Analytics Intelligence Platform.
