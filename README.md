# Banking Analytics Intelligence Platform Using Python

A portfolio-grade analytics project that simulates end-to-end banking data workflows for Tanzania financial institutions. The platform generates synthetic data, prepares it for analysis, and will later support exploratory analytics and dashboards.

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
│   ├── raw/              # Synthetic source datasets
│   └── processed/        # Cleaned, analysis-ready datasets
├── notebooks/
├── src/
│   ├── data_generator.py
│   ├── data_cleaning.py
│   └── dashboard_utils.py
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

Generate raw banking datasets:

```bash
python src/data_generator.py
```

This creates `customers.csv`, `accounts.csv`, `transactions.csv`, and `loans.csv` in `data/raw/`.

## Data Cleaning Pipeline

### Raw data source

The cleaning pipeline reads synthetic Tanzania banking datasets from `data/raw/`:

| File | Description |
|------|-------------|
| `customers.csv` | Customer demographics and segmentation |
| `accounts.csv` | Account balances and status |
| `transactions.csv` | Transaction activity across channels |
| `loans.csv` | Loan portfolio and repayment behavior |

These files are produced by `src/data_generator.py` and represent the raw analytical landing zone before quality controls are applied.

### Cleaning process

Run the pipeline:

```bash
python src/data_cleaning.py
```

The script performs the following steps for each dataset:

1. **Load** raw CSV files into Pandas DataFrames
2. **Assess data quality** — missing values, duplicate rows, and incorrect data types
3. **Clean records** — remove duplicates, validate business rules, and fix data types
4. **Engineer features** for downstream banking analytics
5. **Export** cleaned files to `data/processed/`

Key cleaning rules include:

- **Customers:** duplicate removal, date parsing, age validation (18–100), controlled vocabulary checks, and `customer_age_group` creation
- **Accounts:** non-negative balances, valid account types/statuses, and referential checks against cleaned customers
- **Transactions:** positive amounts only, valid channels/types, datetime conversion, and `transaction_month`, `transaction_year`, `transaction_hour`
- **Loans:** positive loan amounts/rates, valid repayment statuses, and `risk_category` based on repayment behavior

### Output datasets

Cleaned files are saved to `data/processed/`:

| File | New fields |
|------|------------|
| `customers_clean.csv` | `customer_age_group` |
| `accounts_clean.csv` | — |
| `transactions_clean.csv` | `transaction_month`, `transaction_year`, `transaction_hour` |
| `loans_clean.csv` | `risk_category` |

These datasets are the standard input for notebooks, reporting, and the Streamlit dashboard.

## Banking Analytics Dashboard

### Purpose

The Streamlit dashboard provides an interactive executive view of customer, transaction, and loan analytics. It is designed to resemble an internal banking BI tool for portfolio monitoring and management review.

### Features

- **Executive Overview** — portfolio KPIs, customer growth, transaction trends, loan mix, and channel usage
- **Customer Analytics** — demographics, value by segment, and filters by region, gender, and customer type
- **Transaction Analytics** — volume/value trends, channel performance, and filters by date, region, channel, and type
- **Loan Analytics** — portfolio KPIs, repayment and risk views, regional default rates, and loan size distribution

### Technologies

- Streamlit for the interactive UI
- Pandas for data processing
- Plotly for interactive charts

Reusable logic lives in `src/dashboard_utils.py`; the UI is in `dashboards/app.py`.

### How to run

Ensure processed datasets exist (`data/processed/`), then start the dashboard:

```bash
source venv/bin/activate
streamlit run dashboards/app.py
```

Open the local URL shown in the terminal (typically `http://localhost:8501`).

### Deploy on Streamlit Community Cloud

Streamlit Cloud runs apps from a **public GitHub repository**.

This project includes a cloud-safe sample dataset in `data/sample/` (~17 MB) because the full `transactions_clean.csv` exceeds GitHub’s 100 MB file limit. On Streamlit Cloud the dashboard automatically loads the sample data.

#### 1. Push the project to GitHub

```bash
cd Banking-Analytics-Platform
git init
git add .
git commit -m "Prepare Banking Analytics Platform for Streamlit Cloud"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/Banking-Analytics-Platform.git
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud

1. Open [https://share.streamlit.io](https://share.streamlit.io) (or [https://streamlit.io/cloud](https://streamlit.io/cloud))
2. Sign in with GitHub
3. Click **Create app** / **New app**
4. Select your repository: `Banking-Analytics-Platform`
5. Set:
   - **Branch:** `main`
   - **Main file path:** `dashboards/app.py`
   - **Python version:** 3.12 (if available)
6. Click **Deploy**

#### 3. After deploy

- App URL looks like: `https://<app-name>.streamlit.app`
- Rebuilds automatically when you push to `main`
- Local full datasets stay in `data/processed/` (gitignored); regenerate anytime with:

```bash
python src/data_generator.py
python src/data_cleaning.py
```

## License

Portfolio project for educational and demonstration purposes.
# banking-analytics-platform
